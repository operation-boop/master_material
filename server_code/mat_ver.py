import anvil.server
from anvil.tables import app_tables
import uuid
from datetime import datetime
import anvil.tables.query as q
import json

DOC_PREFIX = "vin_mmat_"
VALID_STATUSES = {
  "Creating": ["Draft", "Submitted"],
  "Draft": ["Creating", "Draft", "Submitted"],
  "Submitted": ["Creating"]
}
REQUIRED_FIELDS = ["supplier"]  

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
@anvil.server.callable
def validate_required_fields(document_id):
  """Validate all required fields are filled"""
  master = get_master_material(document_id)
  current_version = master['current_version']

  missing = []
  for field in REQUIRED_FIELDS:
    value = current_version.get(field)
    # Check if field is None, empty string, or whitespace-only string
    if value is None or (isinstance(value, str) and value.strip() == ""):
      missing.append(field)

  return {"is_valid": len(missing) == 0, "missing_fields": missing}

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
      f"Cannot transition from {current_status} to {target_status}. " +
      f"Allowed transitions: {', '.join(VALID_STATUSES.get(current_status, []))}"
    )

  # ============================================
  # DRAFT WORKFLOW
  # ============================================
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
        if value is not None:  # Only update non-empty fields
          try:
            version[key] = value
            updated_fields.append(key)
          except Exception as e:
            print(f"Warning: Could not update field '{key}': {str(e)}")

      print(f"Updated {len(updated_fields)} fields: {', '.join(updated_fields)}")

    version['status'] = "Draft"
    version['created_at'] = datetime.now()
    version['created_by'] = updated_by_user

    return {"action": "draft_saved", "version": version, "document_id": document_id}

@anvil.server.callable
def save_draft(document_id, submitted_by_user, form_data):
  """Save form data as draft (no validation)."""
  master = get_master_material(document_id)
  version = master['current_version']

  # update all fields directly
  for k, v in (form_data or {}).items():
    try:
      version[k] = v
    except Exception as e:
      print(f"Warning: Could not update {k}: {e}")

  # mark as draft
  version["status"] = "Draft"

  return {"ok": True, "action": "draft_saved", "document_id": document_id}

@anvil.server.callable
def submit_version(document_id, submitted_by_user, form_data):
  """Simple: update fields, validate required ones, mark submitted."""
  master = get_master_material(document_id)
  version = master['current_version']

  required = [
    "name", "material_type", "supplier_name",
    "country_of_origin", "unit_of_measurement",
    "weight_per_unit", "weight_uom",
    "original_cost_per_unit", "native_cost_currency"
  ]
  missing = [f for f in required if not form_data.get(f)]
  if missing:
    raise Exception(f"Missing required fields: {', '.join(missing)}")

  # composition check
  comp = json.loads(form_data.get("fabric_composition") or "[]")
  total = sum(float(i["percentage"]) for i in comp)
  if abs(total - 100) > 0.01:
    raise Exception(f"Composition must total 100% (now {total:.1f}%)")

  # update version fields
  for k, v in form_data.items():
    version[k] = v

  version["status"] = "Submitted"
  version["submitted_at"] = datetime.now()
  version["submitted_by"] = submitted_by_user

  master["submitted_at"] = datetime.now()
  master["submitted_by"] = submitted_by_user

  return {"ok": True, "document_id": document_id}

@anvil.server.callable
def edit_submitted(document_id, updated_by_user):
  """Create new version from submitted document"""
  try:
    master = get_master_material(document_id)
    if not master:
      raise Exception(f"Master document {document_id} not found")

    version = master['current_version']
    if not version:
      raise Exception("No current version found")

    check_status_transition(version['status'], "Creating")

    # Validate current version before editing
    validation = validate_required_fields(document_id)
    if not validation['is_valid']:
      raise Exception(
        f"Cannot edit. Current version missing: {', '.join(validation['missing_fields'])}"
      )

      # Get latest version number efficiently
    versions = app_tables.master_material_version.search(document_id=document_id)
    latest_num = max((v['ver_num'] for v in versions), default=0)

    new_uuid = str(uuid.uuid4())

    # Copy all data from current version to new version
    new_version = app_tables.master_material_version.add_row(
      document_uid=new_uuid,
      document_id=document_id,
      ver_num=latest_num + 1,
      status="Creating",
      created_at=datetime.now(),
      created_by=updated_by_user
    )

    # Copy all fields from previous version
    for col in version.get_column_names():
      if col not in ['document_uid', 'document_id', 'ver_num', 'status', 'created_at', 'created_by', 'row_id']:
        try:
          new_version[col] = version[col]
        except Exception as e:
          print(f"Warning: Could not copy column {col}: {e}")
         

        
    master['current_version'] = new_version
    master['current_version_uid'] = new_uuid
    master['current_version_number'] = latest_num + 1

    return {"action": "new_version_created", "version": new_version}

  except Exception as e:
    print(f"Error in edit_submitted: {e}")
    raise

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






