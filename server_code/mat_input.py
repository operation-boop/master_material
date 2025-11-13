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
REQUIRED_FIELDS = [
  "supplier_name", 
  "name", 
  "material_type", 
  "country_of_origin",
  "unit_of_measurement",
  "weight_per_unit",
  "weight_uom",
  "original_cost_per_unit",
  "native_cost_currency"
]  

def _next_ver_num(master_row):
  current = master_row['current_version_number'] or 1
  return current + 1

def _clone_version_fields(src_row, dest_row):
  exclude = {
    "document_uid","document_id","ver_num",
    "status","created_at","updated_at","updated_by",
    "submitted_at","submitted_by",
    "last_verified_date","last_verified_by"
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
  
@anvil.server.callable
def create_material(created_by_user, form_data):
  """Create a new material with version 1 as Draft"""

  # Generate document_id
  doc_num = get_next_document_number()
  document_id = f"{DOC_PREFIX}{doc_num:04d}"
  document_uid = str(uuid.uuid4())

  # Create master_material row
  master = app_tables.master_material.add_row(
    document_id=document_id,
    current_version_number=1,
    current_version_uid=document_uid,
    created_at=datetime.now(),
    created_by=created_by_user
  )

  # Create version 1 as Draft
  version = app_tables.master_material_version.add_row(
    document_id=document_id,
    document_uid=document_uid,
    ver_num=1,
    status="Draft",
    created_at=datetime.now(),
    created_by=created_by_user,
    updated_at=datetime.now(),
    updated_by=created_by_user
  )

  # Apply form data
  if form_data:
    for k, v in form_data.items():
      if v is not None:
        try:
          version[k] = v
        except Exception as e:
          print(f"Warn: cannot set {k}: {e}")

  # Link version to master
  master['current_version'] = version

  return {"action": "created", "document_id": document_id}

@anvil.server.callable
def create_and_submit_material(created_by_user, form_data):
  """Create a new material and submit it immediately as Submitted - Unverified"""

  # Validate required fields
  missing = []
  for field in REQUIRED_FIELDS:
    if not form_data.get(field):
      missing.append(field)

  if missing:
    raise Exception(f"Cannot submit. Missing required fields: {', '.join(missing)}")

  # Generate document_id
  doc_num = get_next_document_number()
  document_id = f"{DOC_PREFIX}{doc_num:04d}"
  document_uid = str(uuid.uuid4())

  # Create master_material row
  master = app_tables.master_material.add_row(
    document_id=document_id,
    current_version_number=1,
    current_version_uid=document_uid,
    created_at=datetime.now(),
    created_by=created_by_user,
    submitted_at=datetime.now(),
    submitted_by=created_by_user
  )

  # Create version 1 as Submitted - Unverified
  version = app_tables.master_material_version.add_row(
    document_id=document_id,
    document_uid=document_uid,
    ver_num=1,
    status="Submitted - Unverified",
    created_at=datetime.now(),
    created_by=created_by_user,
    updated_at=datetime.now(),
    updated_by=created_by_user,
    submitted_at=datetime.now(),
    submitted_by=created_by_user
  )

  # Apply form data
  if form_data:
    for k, v in form_data.items():
      if v is not None:
        try:
          version[k] = v
        except Exception as e:
          print(f"Warn: cannot set {k}: {e}")

  # Link version to master
  master['current_version'] = version

  return {"action": "created_and_submitted", "document_id": document_id}
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
  version['status'] = "Submitted - Unverified"
  version['submitted_at'] = datetime.now()
  version['submitted_by'] = submitted_by_user
  version['updated_at'] = datetime.now()
  version['updated_by'] = submitted_by_user
  master['submitted_at'] = version['submitted_at']
  master['submitted_by'] = submitted_by_user
  try:
    version['last_verified_date'] = None
    version['last_verified_by'] = None
    master['last_verified_date'] = None
    master['last_verified_by'] = None
  except Exception:
    pass

  return {"action": "submitted_unverified", "version": version, "document_id": document_id}

@anvil.server.callable
def verify_material_version(document_id):
  """
  Admin function: Mark the current version as verified.
  Changes status from 'Submitted - Unverified' to 'Submitted - Verified'.
  """
  user = anvil.users.get_user()
  if not user:
    raise Exception("You must be logged in to verify materials.")
  if user['role'] != "Admin":
    raise Exception("Permission denied: only admins can verify.")

  master = get_master_material(document_id)
  version = master['current_version']

  # Allow verification only if it's in unverified submitted state
  cur_status = version['status']
  if cur_status != "Submitted - Unverified":
    raise Exception("Only a 'Submitted - Unverified' version can be verified.")

  # Update status to verified
  version['status'] = "Submitted - Verified"
  version['last_verified_date'] = datetime.now()
  version['last_verified_by'] = user['email'] or user['full_name'] or "Unknown"

  master['last_verified_date'] = version['last_verified_date']
  master['last_verified_by'] = version['last_verified_by']

  return {
    "ok": True, 
    "message": f"{document_id} verified by {version['last_verified_by']}."
  }

def is_submitted(status):
  """Return True for any submitted flavor."""
  if not status:
    return False
  return status.startswith("Submitted")
