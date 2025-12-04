from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import anvil.users
import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .api_framework import APIEndpoint
import API.redoc_export
import uuid
from ..mat_input import create_material, create_and_submit_material, save_or_edit_draft, submit_version, edit_verified_and_submit, validate_required_fields
from API.material_api import MaterialIDRequest
# ============================================================================
# NEW MODELS FOR CREATE/EDIT OPERATIONS
# ============================================================================
class MaterialFormData(BaseModel):
  """
  Flexible model for material fields. 
  All fields are optional because:
  1. Drafts can be partial.
  2. Edits might only update one field.
  """
  name: Optional[str] = None
  material_type: Optional[str] = None
  supplier_name: Optional[str] = None
  ref_id: Optional[str] = None
  country_of_origin: Optional[str] = None
  unit_of_measurement: Optional[str] = None
  fabric_roll_width: Optional[float] = None
  fabric_cut_width: Optional[float] = None
  fabric_cut_width_no_shrinkage: Optional[float] = None
  weight_per_unit: Optional[float] = None
  weight_uom: Optional[str] = None
  generic_material_size: Optional[str] = None
  original_cost_per_unit: Optional[float] = None
  native_cost_currency: Optional[str] = None
  supplier_selling_tolerance: Optional[float] = None
  refundable_tolerance: Optional[float] = None
  vietnam_vat_rate: Optional[float] = None
  refundable_vat: Optional[float] = None
  import_duty: Optional[float] = None
  refundable_import_duty: Optional[float] = None
  shipping_term: Optional[str] = None
  logistics_rate: Optional[float] = None
  change_description: Optional[str] = None

class CreateMaterialRequest(BaseModel):
  """Request to create a new material"""
  form_data: MaterialFormData = Field(..., description="The material details")

class EditMaterialRequest(BaseModel):
  """Request to edit an existing material"""
  document_id: str = Field(..., description="The unique document ID (e.g. vin_mmat_0001)")
  form_data: Optional[MaterialFormData] = Field(None, description="The fields to update")

class EditVerifiedRequest(EditMaterialRequest):
  """Request to edit a verified material (requires notes)"""
  notes: Optional[str] = Field(None, description="Notes explaining why this verified material is being changed")

class ActionResponse(BaseModel):
  """Standard response for create/edit actions"""
  action: str
  document_id: str
  new_version_number: Optional[int] = None
  message: Optional[str] = None

class ValidationResponse(BaseModel):
  is_valid: bool
  missing_fields: List[str]

# ============================================================================
# API ENDPOINTS - CREATE & EDIT
# ============================================================================

@anvil.server.route("/create_material")
@APIEndpoint(
  name="create_material",
  request_model=CreateMaterialRequest,
  response_model=ActionResponse,
  summary="Create Draft Material",
  description="Creates a new material in 'Draft' status.",
  tags=["Workflow"]
)
def api_create_material(request: CreateMaterialRequest):
  # 1. Get current API user
  user = anvil.users.get_user()
  if not user:
    raise Exception("Unauthorized: You must be logged in.")

  user_email = user['email']

  # 2. Call your existing logic
  # Convert Pydantic model back to dict for your helper functions
  data_dict = request.form_data.dict(exclude_unset=True)

  result = create_material(created_by_user=user_email, form_data=data_dict)

  return {
    "action": result['action'],
    "document_id": result['document_id'],
    "message": "Material created successfully as Draft."
  }


@anvil.server.route("/create_and_submit_material")
@APIEndpoint(
  name="create_and_submit_material",
  request_model=CreateMaterialRequest,
  response_model=ActionResponse,
  summary="Create & Submit Material",
  description="Creates a new material and immediately submits it for verification.",
  tags=["Workflow"]
)
def api_create_and_submit(request: CreateMaterialRequest):
  user = anvil.users.get_user()
  if not user:
    raise Exception("Unauthorized.")

  data_dict = request.form_data.dict(exclude_unset=True)

  # This might raise an Exception if fields are missing, which APIEndpoint handles automatically
  result = create_and_submit_material(created_by_user=user['email'], form_data=data_dict)

  return {
    "action": result['action'],
    "document_id": result['document_id'],
    "message": "Material created and submitted for verification."
  }


@anvil.server.route("/save_draft")
@APIEndpoint(
  name="save_draft",
  request_model=EditMaterialRequest,
  response_model=ActionResponse,
  summary="Update Draft",
  description="Updates fields on a material that is still in 'Draft' status.",
  tags=["Workflow"]
)
def api_save_draft(request: EditMaterialRequest):
  data_dict = request.form_data.dict(exclude_unset=True) if request.form_data else {}

  result = save_or_edit_draft(document_id=request.document_id, form_data=data_dict)

  return {
    "action": result['action'],
    "document_id": result['document_id'],
    "message": "Draft updated."
  }


@anvil.server.route("/submit_version")
@APIEndpoint(
  name="submit_version",
  request_model=EditMaterialRequest,
  response_model=ActionResponse,
  summary="Submit Draft",
  description="Promotes a 'Draft' material to 'Submitted - Unverified'. Validates required fields.",
  tags=["Workflow"]
)
def api_submit_version(request: EditMaterialRequest):
  user = anvil.users.get_user()
  if not user:
    raise Exception("Unauthorized.")

  data_dict = request.form_data.dict(exclude_unset=True) if request.form_data else {}

  result = submit_version(
    document_id=request.document_id, 
    submitted_by_user=user['email'], 
    form_data=data_dict
  )

  return {
    "action": result['action'],
    "document_id": result['document_id'],
    "message": "Material submitted successfully."
  }


@anvil.server.route("/edit_verified")
@APIEndpoint(
  name="edit_verified",
  request_model=EditVerifiedRequest,
  response_model=ActionResponse,
  summary="Edit Verified Material",
  description="Creates a NEW version from a Verified material and submits it.",
  tags=["Workflow"]
)
def api_edit_verified(request: EditVerifiedRequest):
  user = anvil.users.get_user()
  if not user:
    raise Exception("Unauthorized.")

  data_dict = request.form_data.dict(exclude_unset=True) if request.form_data else {}

  result = edit_verified_and_submit(
    document_id=request.document_id, 
    edited_by_user=user['email'], 
    form_data=data_dict,
    notes=request.notes
  )

  return {
    "action": result['action'],
    "document_id": result['document_id'],
    "new_version_number": result['new_version_number'],
    "message": f"New version {result['new_version_number']} created and submitted."
  }


@anvil.server.route("/validate_material")
@APIEndpoint(
  name="validate_material",
  request_model=MaterialIDRequest, # reusing your existing ID request model
  response_model=ValidationResponse,
  summary="Validate Material",
  description="Checks if the current version has all required fields filled.",
  tags=["Workflow"]
)
def api_validate_material(request: MaterialIDRequest):
  result = validate_required_fields(request.document_id)
  return result
