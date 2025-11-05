import anvil.server
from anvil.tables import app_tables
import uuid
from datetime import datetime

@anvil.server.callable
def create_new_master_material(created_by_user):
  new_uuid = str(uuid.uuid4())
  next_doc_number = get_next_document_number()
  document_id = f"vin_mmat_{next_doc_number:04d}"

  master_material_version = app_tables.master_material_version.add_row(
    document_uid=new_uuid,
    document_id=document_id,
    ver_num=1,
    status="Draft"
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
@anvil.server.callable
def create_new_version(existing_document_id, created_by_user): 
  existing_versions = app_tables.master_material_version.search(document_id=existing_document_id)
  if not existing_versions:
    raise Exception("Document not found")
  latest_version = max(existing_versions, key=lambda x: x['ver_num'])
  new_version_num = latest_version['ver_num'] + 1
  new_uuid = str(uuid.uuid4())

  new_version = app_tables.master_material_version.add_row(
    document_uid=new_uuid,
    document_id=existing_document_id,
    ver_num=new_version_num,
    status="Draft"
  )
  master_material_record = app_tables.master_material.get(document_id=existing_document_id)
  if master_material_record:
    master_material_record['current_version'] = new_version  
    master_material_record['current_version_uid'] = new_uuid
    master_material_record['current_version_number'] = new_version_num
  master_material_record.update()
  
  return new_version
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
@anvil.server.callable
def get_material_versions(document_id):
  versions = app_tables.master_material_version.search(document_id=document_id)
  return sorted(versions, key=lambda x: x['ver_num'])
@anvil.server.callable
def get_latest_version(document_id):
  versions = get_material_versions(document_id)
  return versions[-1] if versions else None
@anvil.server.callable
def get_master_material_with_latest_version(document_id):
  master_materials = app_tables.master_material.search(document_id=document_id)
  if not master_materials:
    return None
    
  master_material = master_materials[0]
  return master_material
@anvil.server.callable
def submit_master_material_version(document_id, submitted_by_user):
  master_materials = app_tables.master_material.search(document_id=document_id)
  if not master_materials:
    raise Exception("Master material not found")

    master_material = master_materials[0]
    current_version = master_material['current_version']
    if current_version:
      # Update the version status
      current_version['status'] = "Submitted"

      # Update the master material submission info
      master_material['submitted_at'] = datetime.now()
      master_material['submitted_by'] = submitted_by_user

      return current_version

    raise Exception("No current version found")
    

