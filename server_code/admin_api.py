import anvil.users
import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
from pydantic import BaseModel, Field
from api_framework import APIEndpoint
from typing import List, Optional

# ============================================================================
# MODELS
# ============================================================================

class AdminRequest(BaseModel):
  """Standard request for admin actions on a specific document"""
  document_id: Optional[List[str]] = Field(..., description="The unique document ID to act upon")

class VerificationResponse(BaseModel):
  ok: bool
  message: str

class DeleteResponse(BaseModel):
  success: bool
  message: str

# ============================================================================
# HELPERS
# ============================================================================

def _fetch_material_for_admin(document_id):
  """Helper to get master and current version safely"""
  if not document_id:
    raise ValueError("document_id is required")

  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    raise Exception(f"No material found for ID: {document_id}")

  v = master['current_version']
  if not v:
    raise Exception(f"No current version found for ID: {document_id}")

  return master, v

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@APIEndpoint(
  name="verify_material_version",
  request_model=AdminRequest,
  response_model=VerificationResponse,
  summary="Admin: Verify Material",
  description="Marks the current version as verified. Requires Admin role.",
  tags=["Admin", "Workflow"]
)

def verify_material_version(request: AdminRequest):
  # 1. Auth Check
  user = anvil.users.get_user()
  if not user:
    raise Exception("You must be logged in.")
  if user['role'] != "Admin":
    raise Exception("Permission denied: Admin only.")

    # 2. Get Data
  master, version = _fetch_material_for_admin(request.document_id)

  # 3. Logic
  if version['status'] != "Submitted - Unverified":
    raise Exception("Only a 'Submitted - Unverified' version can be verified.")

  now = datetime.now()
  verified_by = user['email'] or user['full_name'] or "Unknown"

  # Update status
  version['status'] = "Submitted - Verified"
  version['last_verified_date'] = now
  version['last_verified_by'] = verified_by

  master['last_verified_date'] = now
  master['last_verified_by'] = verified_by

  return {
    "ok": True, 
    "message": f"{request.document_id} verified by {verified_by}."
  }

@APIEndpoint(
  name="delete_material",
  request_model=AdminRequest,
  response_model=DeleteResponse,
  summary="Admin: Delete Material",
  description="Permanently deletes material, history, and SKUs. Cannot be undone.",
  tags=["Admin", "Danger Zone"]
)
def delete_material(request: AdminRequest):
  # 1. Auth Check
  user = anvil.users.get_user()
  if not user or user['role'] != 'Admin':
    raise Exception("Permission Denied: Admin only.")

  document_id = request.document_id
  
  # 2. Get Data
  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    return {"success": False, "message": "Material not found (already deleted?)"}

  # 3. Logic (Delete everything)
    # Delete versions
  versions = app_tables.master_material_version.search(document_id=document_id)
  for v in versions:
    v.delete()

    # Delete SKUs
  skus = list(app_tables.material_sku.search(master_material=master))
  for s in skus:
    s.delete()

  # Delete Master
  master.delete()

  return {
    "success": True, 
    "message": f"Material {document_id} and all related data deleted."
  }