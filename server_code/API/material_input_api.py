import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .api_framework import APIEndpoint

# ============================================================================
# 1. CONSTANTS & HELPERS
# ============================================================================

DOC_PREFIX = "vin_mmat_"
REQUIRED_FIELDS = [
  "material_name", "material_type", "supplier_name",
  # ... add the rest of your required fields here
]

def _get_next_document_id():
  """Helper to generate next ID like vin_mmat_0004"""
  # Note: For production with high concurrency, use a dedicated counter table
  all_rows = app_tables.master_material_version.search()
  numbers = []
  for r in all_rows:
    try:
      num = int(r['document_id'].replace(DOC_PREFIX, ''))
      numbers.append(num)
    except ValueError:
      continue

  next_num = (max(numbers) + 1) if numbers else 1
  return f"{DOC_PREFIX}{next_num:04d}"

# ============================================================================
# 2. MODELS
# ============================================================================

class MaterialBase(BaseModel):
  """Common fields for creating/updating materials"""
  material_name: Optional[str] = None
  material_type: Optional[str] = None
  supplier_name: Optional[str] = None
  ref_id: Optional[str] = None
  unit_of_measurement: Optional[str] = None
  # Add other fields as optional to allow partial updates...

class CreateMaterialRequest(MaterialBase):
  """Request to create a new material"""
  pass

class UpdateDraftRequest(MaterialBase):
  """Request to update a draft"""
  document_id: str = Field(..., description="The ID of the document to update")

class SubmitVersionRequest(BaseModel):
  """Request to submit a version"""
  document_id: str = Field(..., description="The ID of the document to submit")
  form_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Final updates before submit")

class EditVerifiedRequest(BaseModel):
  """Request to edit a verified document (creates v+1)"""
  document_id: str = Field(..., description="The Verified Document ID")
  form_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Changes for the new version")
  notes: Optional[str] = Field(None, description="Notes for this revision")

class MaterialResponse(BaseModel):
  """Standard response for material operations"""
  document_id: str
  version_num: int
  status: str
  message: str

# ============================================================================
# 3. ENDPOINTS
# ============================================================================
@anvil.server.route("/create_and_submit", methods=["POST"])
@APIEndpoint(
  name="create_and_submit_material", # Matches your old function name?
  request_model=CreateMaterialRequest,
  response_model=MaterialResponse,
  summary="Create & Submit Immediately",
  tags=["Material_Input"]
)
def create_and_submit_material(request: CreateMaterialRequest):
  user = anvil.users.get_user()
  user_email = user['email'] if user else "system"

  # 1. Validation (Check required fields before creating anything)
  # Convert request to dict to check values
  data = request.model_dump(exclude_none=True)

  missing = []
  for field in REQUIRED_FIELDS:
    # Check if field is missing or empty string
    if not data.get(field): 
      missing.append(field)

  if missing:
    raise Exception(f"Cannot submit. Missing required fields: {', '.join(missing)}")

    # 2. Generate IDs
  doc_id = _get_next_document_id()
  doc_uid = str(uuid.uuid4())
  now = datetime.now()

  # 3. Create Master (Verified = False)
  master = app_tables.master_material.add_row(
    document_id=doc_id,
    current_version_number=1,
    current_version_uid=doc_uid,
    created_at=now,
    created_by=user_email,
    submitted_at=now,
    submitted_by=user_email
  )

  # 4. Create Version (Status = Submitted - Unverified)
  version = app_tables.master_material_version.add_row(
    document_id=doc_id,
    document_uid=doc_uid,
    ver_num=1,
    status="Submitted - Unverified",
    created_at=now,
    created_by=user_email,
    submitted_at=now,
    submitted_by=user_email,
    **data 
  )

  # 5. Link
  master['version_history'] = [version]
  master['current_version'] = version

  return {
    "document_id": doc_id,
    "version_num": 1,
    "status": "Submitted - Unverified",
    "message": "Material created and submitted for verification"
  }
  
@anvil.server.route("/create_material_draft", methods=["POST"])
@APIEndpoint(
  name="create_material_draft",
  request_model=CreateMaterialRequest,
  response_model=MaterialResponse,
  summary="Create New Draft",
  tags=["Material_Input"]
)
def create_material_draft(request: CreateMaterialRequest):
  user = anvil.users.get_user()
  user_name = user['full_name']

  doc_id = _get_next_document_id()
  doc_uid = str(uuid.uuid4())
  now = datetime.now()

  # 1. Create Master
  master = app_tables.master_material.add_row(
    document_id=doc_id,
    current_version_number=1,
    current_version_uid=doc_uid,
    created_at=now,
    created_by=user_name
  )

  # 2. Create Version
  version = app_tables.master_material_version.add_row(
    document_id=doc_id,
    document_uid=doc_uid,
    ver_num=1,
    status="Draft",
    created_at=now,
    created_by=user_name,
    **request.model_dump(exclude_none=True) # Apply form data directly
  )

  # 3. Link
  master['version_history'] = [version]
  master['current_version'] = version

  return {
    "document_id": doc_id,
    "version_num": 1,
    "status": "Draft",
    "message": "Draft created successfully"
  }


@anvil.server.route("/update_draft", methods=["POST"])
@APIEndpoint(
  name="update_draft",
  request_model=UpdateDraftRequest,
  response_model=MaterialResponse,
  summary="Update Existing Draft",
  tags=["Material_Input"]
)
def update_draft(request: UpdateDraftRequest):
  # 1. Fetch Master & Version
  master = app_tables.master_material.get(document_id=request.document_id)
  if not master:
    raise Exception(f"Document {request.document_id} not found")

  version = master['current_version']
  if version['status'] != "Draft":
    raise Exception(f"Cannot edit {request.document_id}. Status is '{version['status']}', must be 'Draft'.")

    # 2. Update Fields
  updates = request.model_dump(exclude={'document_id'}, exclude_none=True)
  for k, v in updates.items():
    version[k] = v

  return {
    "document_id": request.document_id,
    "version_num": version['ver_num'],
    "status": "Draft",
    "message": "Draft updated successfully"
  }


@anvil.server.route("/submit_version", methods=["POST"])
@APIEndpoint(
  name="submit_version",
  request_model=SubmitVersionRequest,
  response_model=MaterialResponse,
  summary="Submit Draft to Unverified",
  tags=["Material_Input"]
)
def submit_version(request: SubmitVersionRequest):
  user = anvil.users.get_user()
  user_name = user['full_name']
  
  # 1. Fetch
  master = app_tables.master_material.get(document_id=request.document_id)
  if not master:
    raise Exception("Document not found")
  version = master['current_version']

  # 2. Validate Status
  if version['status'] != "Draft":
    raise Exception("Only Drafts can be submitted")

    # 3. Apply final updates if any
  if request.form_data:
    for k, v in request.form_data.items():
      version[k] = v

    # 4. Check Required Fields
    # (Simplified check for brevity, logic remains same as before)
  missing = []
  for field in REQUIRED_FIELDS:
    if not version[field]: 
      missing.append(field)

  if missing:
    raise Exception(f"Missing required fields: {', '.join(missing)}")

    # 5. Transition
  now = datetime.now()
  version['status'] = "Submitted - Unverified"
  version['submitted_at'] = now
  version['submitted_by'] = user_name

  master['submitted_at'] = now
  master['submitted_by'] = user_name

  return {
    "document_id": request.document_id,
    "version_num": version['ver_num'],
    "status": "Submitted - Unverified",
    "message": "Version submitted for verification"
  }


@anvil.server.route("/edit_verified", methods=["POST"])
@APIEndpoint(
  name="edit_verified",
  request_model=EditVerifiedRequest,
  response_model=MaterialResponse,
  summary="Revise Verified Document",
  tags=["Material_Input"]
)
def edit_verified(request: EditVerifiedRequest):
  user = anvil.users.get_user()
  user_name = user['full_name']
  master = app_tables.master_material.get(document_id=request.document_id)
  if not master: 
    raise Exception("Document not found")

  old_v = master['current_version']
  if old_v['status'] != "Submitted - Verified":
    raise Exception("Can only revise Verified documents")

    # 1. Prepare New Version
  new_ver_num = (master['current_version_number'] or 0) + 1
  new_uid = str(uuid.uuid4())
  now = datetime.now()

  # 2. Create New Version Row
  # (We clone manually to avoid copying system fields)
  exclude = {"document_uid", "ver_num", "status", "created_at", "submitted_at", "submitted_by"}
  prev_data = dict(old_v)
  cloned_data = {k: v for k, v in prev_data.items() if k not in exclude and not k.startswith("_")}

  # Apply new updates over cloned data
  if request.form_data:
    cloned_data.update(request.form_data)

  new_v = app_tables.master_material_version.add_row(
    document_id=request.document_id,
    document_uid=new_uid,
    ver_num=new_ver_num,
    status="Submitted - Unverified", # Jumping straight to unverified as per logic
    created_at=now,
    submitted_at=now,
    submitted_by=user_name,
    verification_notes=request.notes,
    **cloned_data
  )

  # 3. Update Master Pointers
  # Need to manually rebuild history list
  current_history = list(master['version_history'] or [])
  current_history.append(new_v)

  master['version_history'] = current_history
  master['current_version'] = new_v
  master['current_version_number'] = new_ver_num
  master['current_version_uid'] = new_uid

  return {
    "document_id": request.document_id,
    "version_num": new_ver_num,
    "status": "Submitted - Unverified",
    "message": "New version created and submitted"
  }
