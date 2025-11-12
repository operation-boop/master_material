import anvil.server
from anvil.tables import app_tables
import uuid
from datetime import datetime
import anvil.tables.query as q

DOC_PREFIX = "vin_mmat_"
VALID_STATUSES = {
  "Creating": ["Draft", "Submitted - Unverified"],
  "Draft": ["Draft", "Submitted - Unverified"],  
  "Submitted - Unverified": ["Creating", "Submitted - Verified"],  
  "Submitted - Verified": ["Creating"]  
}
REQUIRED_FIELDS = ["supplier_name"]  

@anvil.server.callable
def create_new_master_material(created_by_user):
  """Create new master material document"""
  new_uuid = str(uuid.uuid4())
  document_id = f"{DOC_PREFIX}{get_next_document_number():04d}"

  version = app_tables.master_material_version.add_row(
    document_uid=new_uuid,
    document_id=document_id,
    ver_num=1,
    status="Creating",
    created_at=datetime.now()
  )

  master = app_tables.master_material.add_row(
    version_history_uid=new_uuid,
    created_at=datetime.now(),
    created_by=created_by_user,
    current_version=version,
    current_version_uid=new_uuid,
    current_version_number=1,
    document_id=document_id
  )

  # Return a dictionary with document_id so the client can use it easily
  return {"document_id": document_id, "master": master}

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




















