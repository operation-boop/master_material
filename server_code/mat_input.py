# mat_input.py - merged single-file version
import anvil.server
from anvil.tables import app_tables
import uuid
from datetime import datetime

DOC_PREFIX = "vin_mmat_"

VALID_STATUSES = {
  "Creating": ["Draft", "Submitted - Unverified"],
  "Draft": ["Draft", "Submitted - Unverified"],
  "Submitted - Unverified": ["Creating", "Submitted - Verified"],
  "Submitted - Verified": ["Creating"]
}

REQUIRED_FIELDS = ["supplier_name"]


# -----------------------
# Low-level helpers
# -----------------------
def _next_num():
  """Return next numeric suffix for a preview document id."""
  rows = list(app_tables.master_material.search()) if app_tables.master_material else []
  max_n = 0
  for r in rows:
    did = r.get("document_id") or ""
    if isinstance(did, str) and did.startswith(DOC_PREFIX):
      try:
        n = int(did.replace(DOC_PREFIX, ""))
        if n > max_n:
          max_n = n
      except Exception:
        pass
  return max_n + 1

@anvil.server.callable
def preview_next_document_id():
  """Read-only preview id — safe to call, no DB writes."""
  return f"{DOC_PREFIX}{_next_num():04d}"

def _master_exists(document_id):
  """Return True if a master_material row with document_id exists."""
  return bool(list(app_tables.master_material.search(document_id=document_id)))

def _create_master_and_version(document_id, user, data=None, status="Draft"):
  """
  Create master_material + master_material_version.
  If document_id is already taken, allocate next free id and retry.
  Returns dict with document_id, document_uid, ver_num.
  """
  tries = 0
  while True:
    tries += 1
    if _master_exists(document_id):
      # allocate new id and retry
      document_id = f"{DOC_PREFIX}{_next_num():04d}"
      if tries > 10:
        raise Exception("Could not allocate unique document_id after multiple attempts.")
      continue

    uid = str(uuid.uuid4())
    now = datetime.now()

    ver = app_tables.master_material_version.add_row(
      document_uid = uid,
      document_id = document_id,
      ver_num = 1,
      status = status,
      data = data or {},
      created_at = now,
      created_by = user
    )

    app_tables.master_material.add_row(
      version_history_uid = uid,
      document_id = document_id,
      created_at = now,
      created_by = user,
      current_version = ver,
      current_version_uid = uid,
      current_version_number = 1
    )

    return {"document_id": document_id, "document_uid": uid, "ver_num": 1}

# -----------------------
# Read helpers (callable)
# -----------------------
@anvil.server.callable
def get_master_material(document_id):
  """Retrieve a master_material row by document_id or raise."""
  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    raise Exception(f"Document '{document_id}' not found")
  return master


@anvil.server.callable
def get_latest_version(document_id):
  """Return a simple dict representing the current_version for a document_id, or None."""
  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    return None
  ver = master.get("current_version")
  if not ver:
    return None
  return {
    "document_id": master.get("document_id"),
    "document_uid": master.get("version_history_uid") or master.get("document_uid"),
    "ver_num": ver.get("ver_num"),
    "status": ver.get("status"),
    "data": ver.get("data") or {},
    "created_at": ver.get("created_at"),
    "created_by": ver.get("created_by")
  }


# -----------------------
# Validation / status helpers
# -----------------------
def validate_required_fields(document_id):
  """
  Validate required fields are present on the current version.
  Works if version stores fields in 'data' dict or directly as columns on the version row.
  Returns {"is_valid": bool, "missing_fields": [...]}
  """
  master = get_master_material(document_id)
  current_version = master.get("current_version")

  if current_version is None:
    return {"is_valid": False, "missing_fields": ["(no current_version row)"]}

  # Prefer structured 'data' dict
  data_container = current_version.get("data") if isinstance(current_version.get("data"), dict) else None

  missing = []
  for field in REQUIRED_FIELDS:
    if data_container is not None:
      value = data_container.get(field)
    else:
      # fallback to directly stored column (if present)
      value = current_version.get(field) if field in current_version.keys() else None

    if value is None or (isinstance(value, str) and value.strip() == ""):
      missing.append(field)

  return {"is_valid": len(missing) == 0, "missing_fields": missing}


def check_status_transition(current_status, target_status):
  """
  Ensure current_status -> target_status is allowed according to VALID_STATUSES.
  Raises Exception if not allowed.
  """
  allowed = VALID_STATUSES.get(current_status, [])
  if target_status not in allowed:
    raise Exception(
      f"Cannot transition from {current_status!r} to {target_status!r}. Allowed: {', '.join(allowed) or '(none)'}"
    )


def verify_version(document_id, ver_num):
  """
  Return the master_material_version row for (document_id, ver_num) or raise ValueError.
  Use to operate on historical versions safely.
  """
  rows = list(app_tables.master_material_version.search(document_id=document_id, ver_num=ver_num))
  if not rows:
    raise ValueError(f"Version {ver_num} for {document_id} not found.")
  return rows[0]


def is_submitted(version_or_status):
  """Return True if the argument (status string or version row) represents a submitted state."""
  submitted_states = ("Submitted - Unverified", "Submitted - Verified")
  if isinstance(version_or_status, str):
    return version_or_status in submitted_states
  try:
    st = version_or_status.get("status")
    return st in submitted_states
  except Exception:
    return False


# -----------------------
# Save / Submit / Verify flows (callable)
# -----------------------
@anvil.server.callable
def save_draft(document_id, user, data):
  """
  Create or update a Draft.
  - If no master exists -> create master + version with status 'Draft'.
  - If current_version.status is Creating/Draft -> update in-place.
  - Otherwise -> create a new version (ver_num+1) with status 'Draft'.
  Returns a dict describing the action and the document_id / ver_num.
  """
  masters = list(app_tables.master_material.search(document_id=document_id))
  if not masters:
    created = _create_master_and_version(document_id, user, data=data, status="Draft")
    return {"action": "created_and_saved", **created, "status": "Draft"}

  master = masters[0]
  cur = master.get("current_version")
  now = datetime.now()

  if cur and cur.get("status") in ("Creating", "Draft"):
    # update existing draft-like version
    if isinstance(cur.get("data"), dict):
      merged = cur.get("data").copy()
      merged.update(data or {})
      cur['data'] = merged
    else:
      for k, v in (data or {}).items():
        cur[k] = v
    cur['updated_at'] = now
    cur['updated_by'] = user
    master['current_version'] = cur
    return {"action": "updated", "document_id": document_id, "ver_num": cur.get("ver_num"), "status": "Draft"}

  # latest is submitted or otherwise non-editable -> create new draft version
  next_ver = (cur.get("ver_num") if cur else 0) + 1
  ver = app_tables.master_material_version.add_row(
    document_uid = master.get("version_history_uid") or str(uuid.uuid4()),
    document_id = document_id,
    ver_num = next_ver,
    status = "Draft",
    data = data or {},
    created_at = now,
    created_by = user
  )
  master['current_version'] = ver
  master['current_version_number'] = next_ver
  return {"action": "new_draft", "document_id": document_id, "ver_num": next_ver, "status": "Draft"}


@anvil.server.callable
def submit_version(document_id, user, data):
  """
  Persist and mark as 'Submitted - Unverified'.
  If master doesn't exist -> create it first (status Draft) then proceed.
  Performs required-field validation AFTER applying incoming data.
  """
  masters = list(app_tables.master_material.search(document_id=document_id))
  if not masters:
    created = _create_master_and_version(document_id, user, data=data or {}, status="Draft")
    document_id = created["document_id"]
    masters = list(app_tables.master_material.search(document_id=document_id))

  master = masters[0]
  cur = master.get("current_version")
  if cur is None:
    raise Exception("Current version missing; cannot submit.")

  # validate allowed transition
  check_status_transition(cur.get("status"), "Submitted - Unverified")

  # apply incoming data (prefer 'data' dict)
  if data:
    if isinstance(cur.get("data"), dict):
      merged = cur.get("data").copy()
      merged.update(data)
      cur['data'] = merged
    else:
      for k, v in data.items():
        cur[k] = v

  # validate required fields
  validation = validate_required_fields(document_id)
  if not validation['is_valid']:
    missing_str = ', '.join(validation['missing_fields'])
    raise Exception(f"Cannot submit. Missing required fields: {missing_str}")

  # mark submitted
  now = datetime.now()
  cur['status'] = "Submitted - Unverified"
  cur['submitted_at'] = now
  cur['submitted_by'] = user

  master['submitted_at'] = now
  master['submitted_by'] = user
  master['current_version'] = cur

  # ensure verification fields exist (optional initialisation)
  try:
    cur['last_verified_date'] = None
    master['last_verified_date'] = None
  except Exception:
    pass

  return {"action": "submitted_unverified", "document_id": document_id, "ver_num": cur.get("ver_num"), "status": cur.get("status")}


  @anvil.server.callable
  def verify_version(document_id, verified_by_user, notes=None):
    """
    Verify the current version. Only allowed from 'Submitted - Unverified'.
    Sets status to 'Submitted - Verified' and records verifier info.
    """
    master = get_master_material(document_id)
    version = master.get("current_version")
    if version is None:
      raise Exception("Current version missing; cannot verify.")
  
    cur_status = version.get("status")
    if cur_status != "Submitted - Unverified":
      raise Exception("Only a 'Submitted - Unverified' version can be verified.")
  
    now = datetime.now()
    version['status'] = "Submitted - Verified"
    version['last_verified_date'] = now
    version['last_verified_by'] = verified_by_user
    if notes is not None:
      version['verification_notes'] = notes
  
    master['last_verified_date'] = now
    master['last_verified_by'] = verified_by_user
    master['current_version'] = version
  
    return {"action": "verified", "document_id": document_id}
