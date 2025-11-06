import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q
import uuid, json
from datetime import datetime

DOC_PREFIX = "vin_mmat_"
VALID_STATUSES = {
  "Creating": ["Draft", "Submitted"],
  "Draft": ["Draft", "Submitted"],
  "Submitted": ["Creating"],
}

REQUIRED_FIELDS = [
  "name", "material_type", "supplier_name",
  "country_of_origin", "unit_of_measurement",
  "weight_per_unit", "weight_uom",
  "original_cost_per_unit", "native_cost_currency",
]

# ---------- helpers ----------

def _now():
  return datetime.now()

def _check_status_transition(current_status, target_status):
  allowed = VALID_STATUSES.get(current_status, [])
  if target_status not in allowed:
    raise Exception(
      "Cannot transition from {} to {}. Allowed transitions: {}".format(
        current_status, target_status, ", ".join(allowed) or "(none)"
      )
    )

def _get_next_document_number():
  """Simple sequential allocator by scanning existing versions."""
  all_versions = app_tables.master_material_version.search()
  if not all_versions:
    return 1
  numbers = []
  for v in all_versions:
    try:
      num_str = str(v['document_id'] or "")
      numbers.append(int(num_str.replace(DOC_PREFIX, "")))
    except Exception:
      # Skip rows with malformed or missing document_id
      continue
  return (max(numbers) + 1) if numbers else 1

def _get_version_data(version_row):
  """Always return a dict; never None."""
  if not version_row:
    return {}
  data = version_row['data']
  return data if isinstance(data, dict) else {}

def _set_version_data(version_row, payload):
  """Persist dict back to row with updated_at stamp."""
  version_row['data'] = payload or {}
  version_row['updated_at'] = _now()

def _validate_required_payload(payload):
  missing = []
  for k in REQUIRED_FIELDS:
    val = payload.get(k, None)
    if val is None:
      missing.append(k)
    elif isinstance(val, str) and val.strip() == "":
      missing.append(k)
  return missing

def _validate_composition(payload):
  """
  Validate fabric_composition inside payload.
  Accepts list or JSON string; totals must be ~100%.
  Returns normalized list (or empty list if not present).
  """
  comp_raw = payload.get("fabric_composition")
  if comp_raw in (None, "", []):
    return []

  # Safe parse
  try:
    comp = json.loads(comp_raw) if isinstance(comp_raw, str) else comp_raw
  except Exception as e:
    raise Exception("Invalid fabric_composition JSON: {}".format(e))

  if not isinstance(comp, list):
    raise Exception("fabric_composition must be a list (or JSON list).")

  total = 0.0
  norm = []
  for idx, item in enumerate(comp, start=1):
    if not isinstance(item, dict):
      raise Exception("Composition item {} must be an object.".format(idx))
    fiber = (item.get("fiber") or "").strip()
    try:
      pct = float(item.get("percentage", 0))
    except Exception:
      raise Exception("Composition item {} has non-numeric 'percentage'.".format(idx))
    total += pct
    norm.append({"fiber": fiber, "percentage": pct})

  if abs(total - 100.0) > 0.01:
    raise Exception("Composition must total 100% (now {:.1f}%).".format(total))

  return norm

def _latest_ver_num_for(document_id):
  versions = app_tables.master_material_version.search(document_id=document_id)
  latest = 0
  for v in versions:
    try:
      num = int(v['ver_num'] or 0)
    except Exception:
      num = 0
    if num > latest:
      latest = num
  return latest

# ---------- API ----------

@anvil.server.callable
def create_new_master_material(created_by_user):
  """Create a new material with version 1 in 'Creating' and empty data dict."""
  new_uuid = str(uuid.uuid4())
  document_id = "{}{:04d}".format(DOC_PREFIX, _get_next_document_number())
  now = _now()

  version = app_tables.master_material_version.add_row(
    document_uid=new_uuid,
    document_id=document_id,
    ver_num=1,
    status="Creating",
    data={},               # all fields live here
    created_at=now,
    created_by=created_by_user,
    updated_at=now,
  )

  master = app_tables.master_material.add_row(
    version_history_uid=new_uuid,
    created_at=now,
    created_by=created_by_user,
    updated_at=now,
    current_version=version,
    current_version_uid=new_uuid,
    current_version_number=1,
    document_id=document_id,
  )
  return master

@anvil.server.callable
def get_master_material(document_id):
  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    raise Exception("Document {} not found".format(document_id))
  return master

@anvil.server.callable
def validate_required_fields(document_id):
  """Validate required keys against the CURRENT VERSION's data dict."""
  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    return {"is_valid": False, "missing_fields": ["document_not_found"]}

  version = master['current_version']
  if not version:
    return {"is_valid": False, "missing_fields": ["no_current_version"]}

  payload = _get_version_data(version)
  missing = _validate_required_payload(payload)
  return {"is_valid": len(missing) == 0, "missing_fields": missing}

@anvil.server.callable
def save_or_edit_draft(document_id, updated_by_user, form_data=None):
  """
  Merge form_data into version['data'] and set status to Draft.
  Only allowed when status is Creating or Draft.
  """
  form_data = form_data or {}
  master = get_master_material(document_id)
  version = master['current_version']
  if not version:
    raise Exception("No current version found")

  status = version['status']
  if status not in ("Creating", "Draft"):
    raise Exception("Cannot edit. Current status: {}".format(status))

  current = _get_version_data(version)
  merged = {}
  merged.update(current)
  merged.update(form_data)

  now = _now()
  if status == "Creating":
    if not version['created_at']:
      version['created_at'] = now
    if not version['created_by']:
      version['created_by'] = updated_by_user

  _check_status_transition(status, "Draft")
  version['status'] = "Draft"
  _set_version_data(version, merged)

  master['updated_at'] = now
  return {"ok": True, "document_id": document_id}

@anvil.server.callable
def submit_version(document_id, submitted_by_user, form_data=None):
  """
  Merge existing data with incoming form_data, validate, then mark Submitted.
  """
  form_data = form_data or {}
  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    raise Exception("Document {} not found".format(document_id))

  version = master['current_version']
  if not version:
    raise Exception("No current version found")

  status = version['status']
  if status not in ("Creating", "Draft"):
    raise Exception("Cannot submit. Current status: {}".format(status))

  payload = _get_version_data(version)
  payload.update(form_data)

  missing = _validate_required_payload(payload)
  if missing:
    raise Exception("Missing required fields: {}".format(", ".join(missing)))

  normalized_comp = _validate_composition(payload)
  if normalized_comp:
    payload["fabric_composition"] = normalized_comp

  now = _now()
  _check_status_transition(status, "Submitted")
  version['status'] = "Submitted"
  version['submitted_at'] = now
  version['submitted_by'] = submitted_by_user
  _set_version_data(version, payload)

  master['submitted_at'] = now
  master['submitted_by'] = submitted_by_user
  master['updated_at'] = now

  return {"ok": True, "document_id": document_id}

@anvil.server.callable
def edit_submitted(document_id, updated_by_user):
  """
  Clone the current Submitted version into a new 'Creating' version
  and switch master.current_version to the new row.
  """
  master = get_master_material(document_id)
  version = master['current_version']
  if not version:
    raise Exception("No current version found")

  _check_status_transition(version['status'], "Creating")

  payload = _get_version_data(version)
  missing = _validate_required_payload(payload)
  if missing:
    raise Exception("Cannot edit. Current version missing: {}".format(", ".join(missing)))

  latest_num = _latest_ver_num_for(document_id)
  new_uuid = str(uuid.uuid4())
  now = _now()

  # deep-ish copy via JSON for safety
  try:
    cloned = json.loads(json.dumps(payload))
  except Exception:
    cloned = dict(payload)

  new_version = app_tables.master_material_version.add_row(
    document_uid=new_uuid,
    document_id=document_id,
    ver_num=latest_num + 1,
    status="Creating",
    data=cloned,
    created_at=now,
    created_by=updated_by_user,
    updated_at=now,
  )

  master['current_version'] = new_version
  master['current_version_uid'] = new_uuid
  master['current_version_number'] = latest_num + 1
  master['updated_at'] = now

  return {"action": "new_version_created", "version": new_version}










