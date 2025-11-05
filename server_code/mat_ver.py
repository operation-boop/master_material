import anvil.server
from anvil.tables import app_tables
import uuid
from datetime import datetime

# ============================================
# CORE FUNCTIONS - Document Creation
# ============================================
@anvil.server.callable
def create_new_master_material(created_by_user):
  """Creates a new master material with version 1 in Draft status"""
  new_uuid = str(uuid.uuid4())
  next_doc_number = get_next_document_number()
  document_id = f"vin_mmat_{next_doc_number:04d}"

  # Create first version
  master_material_version = app_tables.master_material_version.add_row(
    document_uid=new_uuid,
    document_id=document_id,
    ver_num=1,
    status="Draft"
  )

  # Create master material record
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
@anvil.server.callable
def get_next_document_number():
  """Gets the next available document number"""
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
def save_draft(document_id, updated_by_user, draft_data=None):
  """
  Saves changes to the current draft version.
  - If current version is Draft: updates it (no new version created)
  - If current version is Submitted: creates a new Draft version
  """
  master_material = app_tables.master_material.get(document_id=document_id)

  if not master_material:
    raise Exception("Document not found")

  current_version = master_material['current_version']

  # If current version is submitted, create new draft version
  if current_version['status'] == "Submitted":
    existing_versions = app_tables.master_material_version.search(document_id=document_id)
    latest_version = max(existing_versions, key=lambda x: x['ver_num'])
    new_version_num = latest_version['ver_num'] + 1
    new_uuid = str(uuid.uuid4())

    new_draft = app_tables.master_material_version.add_row(
      document_uid=new_uuid,
      document_id=document_id,
      ver_num=new_version_num,
      status="Draft"
    )

    # Update master material to point to new draft
    master_material['current_version'] = new_draft
    master_material['current_version_uid'] = new_uuid
    master_material['current_version_number'] = new_version_num

    return {"action": "new_version_created", "version": new_draft}

  # If current version is Draft, just update it (no new version)
  else:
    # Optionally update timestamp or other fields
    # current_version['last_modified'] = datetime.now()
    # current_version['modified_by'] = updated_by_user

    return {"action": "draft_updated", "version": current_version}
@anvil.server.callable
def submit_version(document_id, submitted_by_user):
  """
  Submits the current draft version.
  Changes status from Draft to Submitted and locks the version.
  """
  master_material = app_tables.master_material.get(document_id=document_id)

  if not master_material:
    raise Exception("Document not found")

  current_version = master_material['current_version']

  if current_version['status'] == "Submitted":
    raise Exception("Current version is already submitted")

  # Change status to Submitted
  current_version['status'] = "Submitted"

  # Update master material submission info
  master_material['submitted_at'] = datetime.now()
  master_material['submitted_by'] = submitted_by_user

  return current_version
@anvil.server.callable
def get_current_status(document_id):
  """Returns the current version status to help UI decide which buttons to show"""
  master_material = app_tables.master_material.get(document_id=document_id)

  if not master_material:
    return None

  return {
    "document_id": document_id,
    "current_version_number": master_material['current_version_number'],
    "status": master_material['current_version']['status'],
    "can_edit": master_material['current_version']['status'] == "Draft",
    "can_submit": master_material['current_version']['status'] == "Draft"
  }
@anvil.server.callable
def get_material_versions(document_id):
  """Returns all versions of a document, sorted by version number"""
  versions = app_tables.master_material_version.search(document_id=document_id)
  return sorted(versions, key=lambda x: x['ver_num'])
@anvil.server.callable
def get_latest_version(document_id):
  """Returns the latest version of a document"""
  versions = get_material_versions(document_id)
  return versions[-1] if versions else None
@anvil.server.callable
def get_master_material_with_latest_version(document_id):
  """Returns the master material record with its current version"""
  master_material = app_tables.master_material.get(document_id=document_id)
  return master_material