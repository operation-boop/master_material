import anvil.server
from anvil.tables import app_tables
import uuid
from datetime import datetime
import anvil.tables.query as q

DOC_PREFIX = "vin_mmat_"
VALID_STATUSES = {
  "Draft": ["Draft", "Submitted - Unverified"],
  "Submitted - Unverified": ["Draft", "Submitted - Verified"],
  "Submitted - Verified": ["Draft"]  
}
REQUIRED_FIELDS = ["supplier_name"]  

def _next_ver_num(master_row):
  """Compute next version number from master.current_version_number or fallback to 1."""
  current = master_row.get('current_version_number') or 1
  return current + 1

def _clone_version_fields(src_row, dest_row):
  exclude = {
    "document_uid","document_id","ver_num",
    "status","created_at","updated_at","updated_by",
    "submitted_at","submitted_by",
    "last_verified_date","last_verified_by","verification_notes"
  }
  cols = [c['name'] for c in app_tables.master_material_version.list_columns()]
  for name in cols:
    if name in exclude:
      continue
    try:
      dest_row[name] = src_row[name]
    except Exception as e:
      print(f"Warn: cannot copy '{name}': {e}")

@anvil.server.callable
def edit_verified_and_submit(document_id, edited_by_user, form_data=None, notes=None):

  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    raise Exception(f"Document '{document_id}' not found")

  old_v = master['current_version']
  if not old_v or old_v['status'] != "Submitted - Verified":
    raise Exception("This action is only for 'Submitted - Verified' documents.")


  new_uid = str(uuid.uuid4())
  new_ver_num = _next_ver_num(master)

  new_v = app_tables.master_material_version.add_row(
    document_uid = new_uid,
    document_id  = document_id,
    ver_num      = new_ver_num,
    status       = "Draft", 
    created_at   = datetime.now()
  )
  _clone_version_fields(old_v, new_v)

  if form_data:
    for k, v in form_data.items():
      if v is not None:
        try:
          new_v[k] = v
        except Exception as e:
          print(f"Warn: cannot set {k}: {e}")

  new_v['updated_at'] = datetime.now()
  new_v['updated_by'] = edited_by_user

  # 3) Validate required fields on the NEW version
  missing = []
  for field in REQUIRED_FIELDS:
    try:
      val = new_v[field]
    except KeyError:
      missing.append(field)
      continue
    if val is None or (isinstance(val, str) and not val.strip()):
      missing.append(field)

  if missing:
    raise Exception(f"Cannot re-submit. Missing required fields: {', '.join(missing)}")

  # 4) Mark new version as Submitted - Unverified
  new_v['status'] = "Submitted - Unverified"
  new_v['submitted_at'] = datetime.now()
  new_v['submitted_by'] = edited_by_user
  try:
    if notes is not None:
      new_v['verification_notes'] = notes
  except Exception:
    pass

  # 5) Advance master pointers to the NEW version
  master['current_version'] = new_v
  master['current_version_uid'] = new_uid
  master['current_version_number'] = new_ver_num
  master['submitted_at'] = new_v['submitted_at']
  master['submitted_by'] = edited_by_user

  return {
    "action": "edited_and_resubmitted",
    "document_id": document_id,
    "new_version_number": new_ver_num
  }
 
@anvil.server.callable
def get_next_document_number():
  """Get next available document number"""
  all_versions = app_tables.master_material_version.search()

  if not all_versions:
    return 1

  numbers = []
  for doc in all_versions:
    try:
      num = int(doc['document_id'].replace(DOC_PREFIX, ''))
      numbers.append(num)
    except ValueError:
      continue

  return max(numbers) + 1 if numbers else 1

#-----------------------------------------------------------------------
@anvil.server.callable
def get_master_material(document_id):
  """Retrieve a master material record by document_id."""
  master = app_tables.master_material.get(document_id=document_id)

  if not master:
    raise Exception(f"Document '{document_id}' not found")

  return master
    
@anvil.server.callable
def validate_required_fields(document_id):
  """Validate all required fields are filled on the current version"""
  master = get_master_material(document_id)
  current_version = master["current_version"]

  if current_version is None:
    return {"is_valid": False, "missing_fields": ["(no current_version row)"]}

  missing = []
  for field in REQUIRED_FIELDS:
    try:
      value = current_version[field] 
    except KeyError:
      missing.append(field)
      continue

    if value is None or (isinstance(value, str) and value.strip() == ""):
      missing.append(field)

  return {"is_valid": len(missing) == 0, "missing_fields": missing}

def check_status_transition(current_status, target_status):
  """Validate status transition is allowed"""
  if target_status not in VALID_STATUSES.get(current_status, []):
    raise Exception(
      f"Cannot transition from {current_status} to {target_status}. " +
      f"Allowed transitions: {', '.join(VALID_STATUSES.get(current_status, []))}"
    )

#-----------------------------------------------------------------------
@anvil.server.callable
def save_or_edit_draft(document_id, updated_by_user, form_data=None):
  """Combined save/edit draft function - updates all fields from form"""
  master = get_master_material(document_id)
  version = master['current_version']

  if version['status'] not in ["Creating", "Draft"]:
    raise Exception(f"Cannot edit. Current status: {version['status']}")

  # Update all fields from form data
  if form_data:
    updated_fields = []
    for key, value in form_data.items():
      if value is not None:  
        try:
          version[key] = value
          updated_fields.append(key)
        except Exception as e:
          print(f"Warning: Could not update field '{key}': {str(e)}")

    print(f"Updated {len(updated_fields)} fields: {', '.join(updated_fields)}")

  version['status'] = "Draft"
  version['updated_at'] = datetime.now()
  version['updated_by'] = updated_by_user

  return {"action": "draft_saved", "version": version, "document_id": document_id}

@anvil.server.callable
def submit_version(document_id, submitted_by_user, form_data=None):
  """
  Submit document but mark status as 'Submitted - Unverified'.
  This stores the "yet to verify" state inside the existing 'status' column.
  """
  master = get_master_material(document_id)
  version = master['current_version']

  check_status_transition(version['status'], "Submitted - Unverified")

  if form_data:
    updated_fields = []
    for key, value in form_data.items():
      if value is not None:
        try:
          version[key] = value
          updated_fields.append(key)
        except Exception as e:
          print(f"Warning: Could not update field '{key}': {str(e)}")
    print(f"Updated {len(updated_fields)} fields before validation")

  # Validate required fields AFTER updates
  validation = validate_required_fields(document_id)
  if not validation['is_valid']:
    missing_str = ', '.join(validation['missing_fields'])
    raise Exception(f"Cannot submit. Missing required fields: {missing_str}")

  # Mark as submitted-but-unverified by storing combined text
  combined_status = "Submitted - Unverified"
  version['status'] = combined_status
  version['submitted_at'] = datetime.now()
  version['submitted_by'] = submitted_by_user

  master['submitted_at'] = version['submitted_at']
  master['submitted_by'] = submitted_by_user

  try:
    version['last_verified_date'] = None
    master['last_verified_date'] = None
  except Exception:
    # If those fields don't exist, ignore (no schema change required)
    pass

  return {"action": "submitted_unverified", "version": version, "document_id": document_id}

@anvil.server.callable
def verify_version(document_id, verified_by_user, notes=None):
  """
  Mark the current version as verified by changing status text to
  'Submitted - Verified' (still stored in the same 'status' column).
  """
  master = get_master_material(document_id)
  version = master['current_version']

  # allow verification only if it's in an unverified submitted state
  cur_status = version['status']
  if cur_status != "Submitted - Unverified":
    raise Exception("Only a 'Submitted - Unverified' version can be verified.")

  # Update status to verified
  version['status'] = "Submitted - Verified"
  version['last_verified_date'] = datetime.now()
  version['last_verified_by'] = verified_by_user
  if notes is not None:
    try:
      version['verification_notes'] = notes
    except Exception:
      # ignore if column not present
      pass


  master['last_verified_date'] = version['last_verified_date']
  master['last_verified_by'] = version['last_verified_by']

  return {"action": "verified", "document_id": document_id}

def is_submitted(status):
  """Return True for any submitted flavor."""
  if not status:
    return False
  return status.startswith("Submitted")