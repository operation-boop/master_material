import anvil.server
from anvil.tables import app_tables
from datetime import datetime

def _get_master_material(document_id):
  """Retrieve a master material record by document_id"""
  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    raise Exception(f"Document '{document_id}' not found")
  return master

def _check_admin_permission():
  """Check if current user is admin"""
  user = anvil.users.get_user()
  if not user:
    raise Exception("You must be logged in.")
  if user['role'] != "Admin":
    raise Exception("Permission denied: only admins can perform this action.")
  return user

# ============================================================================
# PUBLIC API - ADMIN OPERATIONS
# ============================================================================

@anvil.server.callable
def verify_material_version(document_id):
  """Admin function: Mark current version as verified"""
  user = _check_admin_permission()

  master = _get_master_material(document_id)
  version = master['current_version']

  if version['status'] != "Submitted - Unverified":
    raise Exception("Only a 'Submitted - Unverified' version can be verified.")

  now = datetime.now()
  verified_by = user['email'] or user['full_name'] or "Unknown"

  # Update to verified status
  version['status'] = "Submitted - Verified"
  version['last_verified_date'] = now
  version['last_verified_by'] = verified_by

  master['last_verified_date'] = now
  master['last_verified_by'] = verified_by

  return {
    "ok": True, 
    "message": f"{document_id} verified by {verified_by}."
  }

@anvil.server.callable
def delete_material(document_id):
  """Admin function: Delete a material and all its versions"""
  _check_admin_permission()

  master = _get_master_material(document_id)

  # Delete all versions first
  versions = list(master['version_history'] or [])
  for version in versions:
    version.delete()

  # Delete the master record
  master.delete()

  return {
    "ok": True,
    "message": f"Material {document_id} deleted successfully."
  }