import anvil.server
from anvil.tables import app_tables
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

# ---------------- Helpers ----------------

def _now():
  return datetime.now()

def _check_status_transition(current_status, target_status):
  allowed = VALID_STATUSES.get(current_status, [])
  if target_status not in allowed:
    raise Exception(
      "Cannot transition from {} to {}. Allowed: {}".format(
        current_status, target_status, ", ".join(allowed) or "(none)"
      )
    )

def _get_next_document_number():
  rows = app_tables.master_material_version.search()
  nums = []
  for r in rows:
    try:
      did = r['document_id'] or ""
      nums.append(int(str(did).replace(DOC_PREFIX, "")))
    except Exception:
      continue
  return (max(nums) + 1) if nums else 1

def _is_filled(v):
  if v is None: 
    return False
  if isinstance(v, str) and v.strip() == "": 
    return False
  return True

def _merged_value(version_row, incoming, key):
  if key in incoming and _is_filled(incoming.get(key)):
    return incoming.get(key)
  try:
    return version_row[key]
  except Exception:
    return None

def _validate_required_merged(version_row, incoming_dict):
  missing = []
  for k in REQUIRED_FIELDS:
    val = _merged_value(version_row, incoming_dict, k)
    if not _is_filled(val):
      missing.append(k)
  return missing

def _validate_composition_sum(version_row, incoming_dict):
  """
  Validate fabric_composition (column is a JSON string).
  Accepts either incoming string or uses current row value.
  If empty, do nothing. If present, must sum ~100.
  """
  raw = None
  if _is_filled(incoming_dict.get("fabric_composition")):
    raw = incoming_dict.get("fabric_composition")
  else:
    try:
      raw = version_row["fabric_composition"]
    except Exception:
      raw = None

  if not _is_filled(raw):
    return  # nothing entered; skip

  try:
    comp = json.loads(raw) if isinstance(raw, str) else raw
  except Exception as e:
    raise Exception("Invalid fabric_composition JSON: {}".format(e))

  if not isinstance(comp, list):
    raise Exception("fabric_composition must be a JSON array of items.")

  total = 0.0
  for i, item in enumerate(comp, start=1):
    if not isinstance(item, dict):
      raise Exception("Composition item {} must be an object.".format(i))
    try:
      total += float(item.get("percentage", 0))
    except Exception:
      raise Exception("Composition item {} has non-numeric 'percentage'.".format(i))

  if abs(total - 100.0) > 0.01:
    raise Exception("Composition must total 100% (now {:.1f}%).".format(total))

def _latest_ver_num_for(document_id):
  versions = app_tables.master_material_version.search(document_id=document_id)
  latest = 0
  for v in versions:
    try:
      n = int(v['ver_num'] or 0)
    except Exception:
      n = 0
    latest = max(latest, n)
  return latest

# ---------------- API ----------------

@anvil.server.callable
def create_new_master_material(created_by_user):
  """Create master + initial version (ver 1, Creating)."""
  now = _now()
  uid = str(uuid.uuid4())
  document_id = "{}{:04d}".format(DOC_PREFIX, _get_next_document_number())

  # initial version row
  v = app_tables.master_material_version.add_row(
    document_uid=uid,
    document_id=document_id,
    ver_num=1,
    status="Creating",
    created_at=now,
    created_by=created_by_user,
    updated_at=now,
  )

  # master row linking to current version
  m = app_tables.master_material.add_row(
    version_history_uid=uid,
    document_id=document_id,
    current_version=v,
    current_version_uid=uid,
    current_version_number=1,
  created_at=now,
    created_by=created_by_user,
    updated_at=now,
  )

  # (Optional: if your versions table has a 'document' Link column back to master)
  try:
    v['document'] = m
  except Exception:
    pass

  return m

@anvil.server.callable
def save_or_edit_draft(document_id, updated_by_user, form_data=None):
  form_data = form_data or {}
  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    raise Exception("Document {} not found".format(document_id))
  version = master['current_version']
  if not version:
    raise Exception("No current version found")

  status = version['status']
  if status not in ("Creating", "Draft"):
    raise Exception("Cannot edit. Current status: {}".format(status))

  _check_status_transition(status, "Draft")
  version['status'] = "Draft"

  now = _now()

  # Row-safe presence checks (no .get on rows)
  try:
    created_at_present = bool(version['created_at'])
  except Exception:
    created_at_present = False
  if not created_at_present:
    version['created_at'] = now

  try:
    created_by_present = bool(version['created_by'])
  except Exception:
    created_by_present = False
  if not created_by_present:
    version['created_by'] = updated_by_user

  version['updated_at'] = now
  master['updated_at'] = now

  return {"ok": True, "document_id": document_id}

@anvil.server.callable
def submit_version(document_id, submitted_by_user, form_data=None):
  """
  Submit: validate required fields using merged (incoming-over-current) values,
  validate composition, then write provided fields and mark Submitted.
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

  # Validate requireds on merged view
  missing = _validate_required_merged(version, form_data)
  if missing:
    raise Exception("Missing required fields: {}".format(", ".join(missing)))

  # Validate composition (from incoming or current)
  _validate_composition_sum(version, form_data)

  # Status + stamps
  now = _now()
  _check_status_transition(status, "Submitted")
  version['status'] = "Submitted"
  version['submitted_at'] = now
  version['submitted_by'] = submitted_by_user
  version['updated_at'] = now

  master['submitted_at'] = now
  master['submitted_by'] = submitted_by_user
  master['updated_at'] = now

  return {"ok": True, "document_id": document_id}














