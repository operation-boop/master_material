import anvil.server
from anvil.tables import app_tables
import uuid
from datetime import datetime
import anvil.tables.query as q

# ============================================
# CONSTANTS & CONFIG
# ============================================
DOC_PREFIX = "vin_mmat_"
VALID_STATUSES = {
  "Creating": ["Draft"],
  "Draft": ["Creating", "Draft", "Submitted"],
  "Submitted": ["Creating"]
}
REQUIRED_FIELDS = ["supplier"]  

# ============================================
# DOCUMENT CREATION
# ============================================
@anvil.server.callable
def create_new_master_material(created_by_user):
  """Create new master material document"""
  new_uuid = str(uuid.uuid4())
  document_id = f"{DOC_PREFIX}{get_next_document_number():04d}"

  version = app_tables.master_material_version.add_row(
    document_uid=new_uuid,
    document_id=document_id,
    ver_num=1,
    status="Creating"
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

  return master

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

# ============================================
# FIELD VALIDATION
# ============================================
def validate_required_fields(document_id):
  """Validate all required fields are filled"""
  master = get_master_material(document_id)
  current_version = master['current_version']

  missing = [
    field for field in REQUIRED_FIELDS
    if not current_version.get(field) or 
    (isinstance(current_version.get(field), str) and 
     current_version.get(field).strip() == "")
  ]

  return {"is_valid": len(missing) == 0, "missing_fields": missing}

# ============================================
# UTILITY FUNCTIONS (Reduce repetition)
# ============================================
@anvil.server.callable
def get_master_material(document_id):
  """Get master material, raise if not found"""
  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    raise Exception(f"Document {document_id} not found")
  return master

def check_status_transition(current_status, target_status):
  """Validate status transition is allowed"""
  if target_status not in VALID_STATUSES.get(current_status, []):
    raise Exception(
      f"Cannot transition from {current_status} to {target_status}"
    )

# ============================================
# DRAFT WORKFLOW
# ============================================
@anvil.server.callable
def save_or_edit_draft(document_id, updated_by_user, supplier_value=None):
  """Combined save/edit draft function - reduces code duplication"""
  master = get_master_material(document_id)
  version = master['current_version']

  if version['status'] not in ["Creating", "Draft"]:
    raise Exception(f"Cannot edit. Current status: {version['status']}")

  if supplier_value is not None:
    version['supplier'] = supplier_value

  version['status'] = "Draft"
  return {"action": "draft_saved", "version": version}

# ============================================
# SUBMISSION WORKFLOW
# ============================================
@anvil.server.callable
def submit_version(document_id, submitted_by_user, supplier_value=None):
  """Submit document with validation"""
  master = get_master_material(document_id)
  version = master['current_version']

  check_status_transition(version['status'], "Submitted")

  if supplier_value is not None:
    version['supplier'] = supplier_value

    # Validate BEFORE changing status
  validation = validate_required_fields(document_id)
  if not validation['is_valid']:
    raise Exception(f"Missing: {', '.join(validation['missing_fields'])}")

  version['status'] = "Submitted"
  master['submitted_at'] = datetime.now()
  master['submitted_by'] = submitted_by_user

  return version

@anvil.server.callable
def edit_submitted(document_id, updated_by_user):
  """Create new version from submitted document"""
  master = get_master_material(document_id)
  version = master['current_version']

  check_status_transition(version['status'], "Creating")

  # Validate current version before editing
  validation = validate_required_fields(document_id)
  if not validation['is_valid']:
    raise Exception(f"Cannot edit. Current version missing: {', '.join(validation['missing_fields'])}")

    # Get latest version number efficiently
  versions = app_tables.master_material_version.search(document_id=document_id)
  latest_num = max((v['ver_num'] for v in versions), default=0)

  new_uuid = str(uuid.uuid4())
  new_version = app_tables.master_material_version.add_row(
    document_uid=new_uuid,
    document_id=document_id,
    ver_num=latest_num + 1,
    status="Creating"
  )

  master['current_version'] = new_version
  master['current_version_uid'] = new_uuid
  master['current_version_number'] = latest_num + 1

  return {"action": "new_version_created", "version": new_version}

# ============================================
# QUERY FUNCTIONS
# ============================================
@anvil.server.callable
def get_current_status(document_id):
  """Get status and allowed actions"""
  master = get_master_material(document_id)
  status = master['current_version']['status']

  return {
    "document_id": document_id,
    "current_version_number": master['current_version_number'],
    "status": status,
    "can_save_draft": status in ["Creating", "Draft"],
    "can_edit_draft": status in ["Creating", "Draft"],
    "can_submit": status in ["Creating", "Draft"],
    "can_edit_submitted": status == "Submitted"
  }

@anvil.server.callable
def get_material_versions(document_id):
  """Get all versions sorted by version number"""
  versions = app_tables.master_material_version.search(document_id=document_id)
  return sorted(versions, key=lambda x: x['ver_num'])

@anvil.server.callable
def get_supplier_field(document_id):
  """Get current supplier value"""
  master = get_master_material(document_id)
  return master['current_version'].get('supplier')

@anvil.server.callable
def update_supplier_field(document_id, supplier_value):
  """Update supplier field"""
  master = get_master_material(document_id)
  master['current_version']['supplier'] = supplier_value
  return {"status": "updated"}

@anvil.server.callable
def get_all_suppliers():
  """Fetch all suppliers for dropdown"""
  suppliers = app_tables.supplier.search()
  return [
    {
      'supplier_name': s['supplier_name'],
      'ref_id': s['ref_id']
    } for s in suppliers
  ]


