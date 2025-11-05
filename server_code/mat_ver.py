import anvil.server
from anvil.tables import app_tables
import uuid

@anvil.server.callable
def create_new_master_material():
  new_uuid = str(uuid.uuid4())
  next_doc_number = get_next_document_number()
  document_id = f"vin_mmat_{next_doc_number:04d}"
  
  master_material = app_tables.master_material_verison.add_row(
    document_uid=new_uuid,
    document_id=document_id,
    ver_num=1,
    status="Draft"
  )
  return master_material

@anvil.server.callable
def create_new_version(existing_document_id): 
  existing_versions = app_tables.master_material_verison.search(document_id=existing_document_id) ## check for the existing document id for existing version
  if not existing_versions:
    raise Exception("Document not found")

  latest_version = max(existing_versions, key=lambda x: x['ver_num']) 
  new_version_num = latest_version['ver_num'] + 1
  new_uuid = str(uuid.uuid4())
  new_version = app_tables.master_material_verison.add_row(
    document_uid=new_uuid,
    document_id=existing_document_id,
    ver_num=new_version_num,
    status="Draft"
  )

  return new_version

@anvil.server.callable
def get_next_document_number():
  all_documents = app_tables.master_material_verison.search()
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
  versions = app_tables.master_material_verison.search(document_id=document_id)
  return sorted(versions, key=lambda x: x['ver_num'])

@anvil.server.callable
def get_latest_version(document_id):
  versions = get_material_versions(document_id)
  return versions[-1] if versions else None

