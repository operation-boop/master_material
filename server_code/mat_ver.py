import anvil.server
from anvil.tables import app_tables
import uuid
from datetime import datetime

# ============================================
#  Create new doc and status "Creating" , add uuid for current version uid and create version 1. 
# ============================================
@anvil.server.callable
def create_new_master_material(created_by_user):
  new_uuid = str(uuid.uuid4())
  next_doc_number = get_next_document_number()
  document_id = f"vin_mmat_{next_doc_number:04d}"

  master_material_version = app_tables.master_material_version.add_row(
    document_uid=new_uuid,
    document_id=document_id,
    ver_num=1,
    status="Creating"
  )

  master_material = app_tables.master_material.add_row(
    version_history_uid=new_uuid,
    created_at=datetime.now(),
    created_by=created_by_user,
    submitted_at=None,
    submitted_by=None,
    current_version=master_material_version,
    current_version_uid=new_uuid,
    current_version_number=1,
    document_id=document_id
  )

  return master_material

# ============================================
# check for the next document number
# ============================================
@anvil.server.callable
def get_next_document_number():

  all_documents = app_tables.master_material_version.search()
  if not all_documents:
    return 1

  max_number = 0
  for doc in all_documents:
    document_id = doc['document_id']
    if document_id and document_id.startswith('vin_mmat_'):
      try:
        number_part = document_id.replace('vin_mmat_', '')
        doc_number = int(number_part)
        max_number = max(max_number, doc_number)
      except ValueError:
        continue
  return max_number + 1

# ============================================
# DRAFT & SUBMIT WORKFLOW
# ============================================

@anvil.server.callable
def save_as_draft(document_id, updated_by_user):
  """Changes status from 'Creating' to 'Draft' (same version)
  Or updates an existing draft (same version) """
  master_material = app_tables.master_material.get(document_id=document_id)

  if not master_material:
    raise Exception("Document not found")

  current_version = master_material['current_version']

  # Only allow if status is "Creating" or "Draft"
  if current_version['status'] not in ["Creating", "Draft"]:
    raise Exception(f"Cannot save as draft. Current status is: {current_version['status']}")

  current_version['status'] = "Draft"
  return {"action": "saved_as_draft", "version": current_version}

@anvil.server.callable
def edit_draft(document_id, updated_by_user):

  ##Edits current draft version (same version, no increment) Only works if status is "Draft" or "Creating" 

  master_material = app_tables.master_material.get(document_id=document_id)

  if not master_material:
    raise Exception("Document not found")

  current_version = master_material['current_version']

  if current_version['status'] not in ["Creating", "Draft"]:
    raise Exception("Can only edit drafts or documents being created")

  # Just update the version (no version increment)
  return {"action": "draft_edited", "version": current_version}

@anvil.server.callable
def submit_version(document_id, submitted_by_user):
  master_material = app_tables.master_material.get(document_id=document_id)
  if not master_material:
    raise Exception("Document not found")

  current_version = master_material['current_version']

  # Can only submit from "Draft" or "Creating" status
  if current_version['status'] not in ["Creating", "Draft"]:
    raise Exception(f"Cannot submit. Current status is: {current_version['status']}")

  # VALIDATION: Check required fields
  validation = validate_required_fields(document_id)
  if not validation['is_valid']:
    missing = ", ".join(validation['missing_fields'])
    raise Exception(f"Cannot submit. Missing required fields: {missing}")

  # Change status to Submitted (same version)
  current_version['status'] = "Submitted"

  # Update master material submission info
  master_material['submitted_at'] = datetime.now()
  master_material['submitted_by'] = submitted_by_user

  return current_version

@anvil.server.callable
def edit_submitted(document_id, updated_by_user):
  """
  Edits a submitted version - creates NEW version with "Creating" status
  This is the ONLY time version number increments!
  """
  master_material = app_tables.master_material.get(document_id=document_id)

  if not master_material:
    raise Exception("Document not found")

  current_version = master_material['current_version']

  # Can only edit if current status is "Submitted"
  if current_version['status'] != "Submitted":
    raise Exception("Can only edit submitted versions")

  validation = validate_required_fields(document_id)
  if not validation['is_valid']:
    missing = ", ".join(validation['missing_fields'])
    raise Exception(f"Cannot edit. Current version missing: {missing}")

  # Create NEW version
  existing_versions = app_tables.master_material_version.search(document_id=document_id)
  latest_version = max(existing_versions, key=lambda x: x['ver_num'])
  new_version_num = latest_version['ver_num'] + 1
  new_uuid = str(uuid.uuid4())

  new_version = app_tables.master_material_version.add_row(
    document_uid=new_uuid,
    document_id=document_id,
    ver_num=new_version_num,
    status="Creating"  # ← New version starts as "Creating"
  )

  # Update master material to point to new version
  master_material['current_version'] = new_version
  master_material['current_version_uid'] = new_uuid
  master_material['current_version_number'] = new_version_num

  return {"action": "new_version_created", "version": new_version}

# ============================================
# QUERY FUNCTIONS
# ============================================

@anvil.server.callable
def get_current_status(document_id):
  """Returns the current version status"""
  master_material = app_tables.master_material.get(document_id=document_id)
  if not master_material:
    return None

  status = master_material['current_version']['status']
  return {
    "document_id": document_id,
    "current_version_number": master_material['current_version_number'],
    "status": status,
    "can_save_draft": status in ["Creating", "Draft"],
    "can_edit_draft": status in ["Creating", "Draft"],
    "can_submit": status in ["Creating", "Draft"],
    "can_edit_submitted": status == "Submitted"
  }

@anvil.server.callable
def get_material_versions(document_id):
  """Returns all versions of a document, sorted by version number"""
  versions = app_tables.master_material_version.search(document_id=document_id)
  return sorted(versions, key=lambda x: x['ver_num'])

@anvil.server.callable
def get_latest_version(document_id):
  versions = get_material_versions(document_id)
  return versions[-1] if versions else None

@anvil.server.callable
def get_master_material_with_latest_version(document_id):
  """Returns the master material record with its current version"""
  master_material = app_tables.master_material.get(document_id=document_id)
  return master_material

@anvil.server.callable
def validate_required_fields(document_id):
  """
    Validates that required fields are filled for submission.
    Returns a dict with validation status and missing fields.
    """
  master_material = app_tables.master_material.get(document_id=document_id)
  if not master_material:
    raise Exception("Document not found")

  current_version = master_material['current_version']
  missing_fields = []

  # Check if supplier field is empty or None
  if not current_version['supplier'] or current_version['supplier'].strip() == "":
    missing_fields.append("supplier")

    # Add other required fields here as needed
    # Example: if not current_version['country_of_origin']:
    #     missing_fields.append("country_of_origin")

  return {
    "is_valid": len(missing_fields) == 0,
    "missing_fields": missing_fields
  }

@anvil.server.callable
def update_supplier_field(document_id, supplier_value):
  """Updates the supplier field in the current version"""
  master_material = app_tables.master_material.get(document_id=document_id)
  if not master_material:
    raise Exception("Document not found")

  current_version = master_material['current_version']
  current_version['supplier'] = supplier_value

  return {"status": "updated"}

@anvil.server.callable
def get_supplier_field(document_id):
  """Gets the current supplier field value"""
  master_material = app_tables.master_material.get(document_id=document_id)
  if not master_material:
    return None

  current_version = master_material['current_version']
  return current_version['supplier']

