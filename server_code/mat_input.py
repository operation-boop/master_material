import anvil.server
from anvil.tables import app_tables
import uuid
from datetime import datetime
import anvil.tables.query as q

DOC_PREFIX = "vin_mmat_"
VALID_STATUSES = {
  "Draft": ["Draft", "Submitted - Unverified"],
  "Submitted - Unverified": ["Draft", "Submitted - Verified"],
  "Submitted - Verified": ["Draft"]  
}
REQUIRED_FIELDS = [
  "master_material_id",
  "name", 
  "material_type",
  "supplier_name",
  "ref_id",
  "country_of_origin",
  "unit_of_measurement",
  "fabric_roll_width",
  "fabric_cut_width",
  "fabric_cut_width_no_shrinkage",
  "weight_per_unit",
  "weight_uom",
  "generic_material_size",
  "original_cost_per_unit",
  "native_cost_currency",
  "supplier_selling_tolerance",
  "refundable_tolerance",
  "vietnam_vat_rate",
  "refundable_vat",
  "import_duty",
  "refundable_import_duty",
  "shipping_term",
  "logistics_rate",
  "change_description",
]  

def _next_ver_num(master_row):
  """Get next version number for a master material"""
  current = master_row['current_version_number'] or 0
  return current + 1

def _clone_version_fields(src_row, dest_row):
  """Clone all fields from source version to destination version, excluding metadata"""
  exclude = {
    "document_uid", "document_id", "ver_num",
    "status", "created_at",
    "submitted_at", "submitted_by",
    "last_verified_date", "last_verified_by"
  }
  cols = [c['name'] for c in app_tables.master_material_version.list_columns()]
  for name in cols:
    if name in exclude:
      continue
    try:
      dest_row[name] = src_row[name]
    except Exception as e:
      print(f"Warning: cannot copy '{name}': {e}")

def _validate_required_fields(version_row):
  """Validate all required fields are filled. Returns (is_valid, missing_fields)"""
  missing = []
  for field in REQUIRED_FIELDS:
    try:
      val = version_row[field]
    except KeyError:
      missing.append(field)
      continue
    if val is None or (isinstance(val, str) and not val.strip()):
      missing.append(field)

  return len(missing) == 0, missing

def _check_status_transition(current_status, target_status):
  """Validate status transition is allowed"""
  if target_status not in VALID_STATUSES.get(current_status, []):
    raise Exception(
      f"Cannot transition from {current_status} to {target_status}. "
      f"Allowed transitions: {', '.join(VALID_STATUSES.get(current_status, []))}"
    )

def _get_master_material(document_id):
  """Retrieve a master material record by document_id"""
  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    raise Exception(f"Document '{document_id}' not found")
  return master

def _update_version_history(master_row, version_row):
  """Add version to master's version history and update UIDs"""
  current_list = list(master_row['version_history'] or [])
  current_list.append(version_row)
  master_row['version_history'] = current_list
  master_row['version_history_uid'] = "|".join([v['document_uid'] for v in current_list])

def _apply_form_data(version_row, form_data):
  """Apply form data to version row"""
  if form_data:
    for k, v in form_data.items():
      if v is not None:
        try:
          version_row[k] = v
        except Exception as e:
          print(f"Warning: cannot set {k}: {e}")

# ============================================================================
# PUBLIC API - CREATE OPERATIONS
# ============================================================================

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

@anvil.server.callable
def create_material(created_by_user, form_data):
  """Create a new material with version 1 as Draft"""
  doc_num = get_next_document_number()
  document_id = f"{DOC_PREFIX}{doc_num:04d}"
  document_uid = str(uuid.uuid4())
  now = datetime.now()

  # Create master material row
  master = app_tables.master_material.add_row(
    document_id=document_id,
    current_version_number=1,
    current_version_uid=document_uid,
    created_at=now,
    created_by=created_by_user
  )

  # Create version 1 as Draft
  version = app_tables.master_material_version.add_row(
    document_id=document_id,
    document_uid=document_uid,
    ver_num=1,
    status="Draft",
    created_at=now,
    created_by=created_by_user,
  )

  _apply_form_data(version, form_data)
  _update_version_history(master, version)

  master['current_version'] = version

  return {"action": "created", "document_id": document_id}

@anvil.server.callable
def create_and_submit_material(created_by_user, form_data):
  """Create a new material and submit it immediately as Submitted - Unverified"""
  # Validate required fields
  missing = []
  for field in REQUIRED_FIELDS:
    if not form_data.get(field):
      missing.append(field)

  if missing:
    raise Exception(f"Cannot submit. Missing required fields: {', '.join(missing)}")

  doc_num = get_next_document_number()
  document_id = f"{DOC_PREFIX}{doc_num:04d}"
  document_uid = str(uuid.uuid4())
  now = datetime.now()

  # Create master material row
  master = app_tables.master_material.add_row(
    document_id=document_id,
    current_version_number=1,
    current_version_uid=document_uid,
    created_at=now,
    created_by=created_by_user,
    submitted_at=now,
    submitted_by=created_by_user
  )

  # Create version 1 as Submitted - Unverified
  version = app_tables.master_material_version.add_row(
    document_id=document_id,
    document_uid=document_uid,
    ver_num=1,
    status="Submitted - Unverified",
    created_at=now,
    created_by=created_by_user,
    submitted_at=now,
    submitted_by=created_by_user
  )

  _apply_form_data(version, form_data)
  _update_version_history(master, version)

  master['current_version'] = version

  return {"action": "created_and_submitted", "document_id": document_id}

# ============================================================================
# PUBLIC API - EDIT OPERATIONS
# ============================================================================

@anvil.server.callable
def save_or_edit_draft(document_id, form_data=None):
  """Update draft material - only works on Draft status"""
  master = _get_master_material(document_id)
  version = master['current_version']

  if version['status'] != "Draft":
    raise Exception(f"Cannot edit. Current status is '{version['status']}', must be 'Draft'")

  _apply_form_data(version, form_data)
  version['status'] = "Draft"

  return {"action": "draft_saved", "version": version, "document_id": document_id}

@anvil.server.callable
def submit_version(document_id, submitted_by_user, form_data=None):
  """Submit draft material as 'Submitted - Unverified'"""
  master = _get_master_material(document_id)
  version = master['current_version']
  now = datetime.now()

  _check_status_transition(version['status'], "Submitted - Unverified")

  # Apply any final updates from form
  _apply_form_data(version, form_data)

  # Validate required fields AFTER updates
  is_valid, missing_fields = _validate_required_fields(version)
  if not is_valid:
    raise Exception(f"Cannot submit. Missing required fields: {', '.join(missing_fields)}")

  # Update to Submitted - Unverified
  version['status'] = "Submitted - Unverified"
  version['submitted_at'] = now
  version['submitted_by'] = submitted_by_user

  master['submitted_at'] = now
  master['submitted_by'] = submitted_by_user

  # Clear verification fields
  try:
    version['last_verified_date'] = None
    version['last_verified_by'] = None
    master['last_verified_date'] = None
    master['last_verified_by'] = None
  except Exception:
    pass

  return {"action": "submitted_unverified", "version": version, "document_id": document_id}

@anvil.server.callable
def edit_verified_and_submit(document_id, edited_by_user, form_data=None, notes=None):
  """Edit a verified material by creating a new version as Submitted - Unverified"""
  master = _get_master_material(document_id)
  old_v = master['current_version']

  if not old_v or old_v['status'] != "Submitted - Verified":
    raise Exception("This action is only for 'Submitted - Verified' documents.")

  new_uid = str(uuid.uuid4())
  new_ver_num = _next_ver_num(master)
  now = datetime.now()

  # Create new version
  new_v = app_tables.master_material_version.add_row(
    document_uid=new_uid,
    document_id=document_id,
    ver_num=new_ver_num,
    status="Draft",
    created_at=now
  )

  # Clone fields from old version
  _clone_version_fields(old_v, new_v)

  # Apply new changes
  _apply_form_data(new_v, form_data)

  # Validate required fields
  is_valid, missing_fields = _validate_required_fields(new_v)
  if not is_valid:
    raise Exception(f"Cannot re-submit. Missing required fields: {', '.join(missing_fields)}")

  # Mark as Submitted - Unverified
  new_v['status'] = "Submitted - Unverified"
  new_v['submitted_at'] = now
  new_v['submitted_by'] = edited_by_user

  try:
    if notes:
      new_v['verification_notes'] = notes
  except Exception:
    pass

  # Update master pointers
  _update_version_history(master, new_v)
  master['current_version'] = new_v
  master['current_version_uid'] = new_uid
  master['current_version_number'] = new_ver_num
  master['submitted_at'] = now
  master['submitted_by'] = edited_by_user

  return {
    "action": "edited_and_resubmitted",
    "document_id": document_id,
    "new_version_number": new_ver_num
  }

# ============================================================================
# PUBLIC API - VALIDATION (Used internally and by forms)
# ============================================================================

@anvil.server.callable
def validate_required_fields(document_id):
  """Validate all required fields are filled on the current version"""
  master = _get_master_material(document_id)
  current_version = master["current_version"]

  if current_version is None:
    return {"is_valid": False, "missing_fields": ["(no current_version row)"]}

  is_valid, missing_fields = _validate_required_fields(current_version)
  return {"is_valid": is_valid, "missing_fields": missing_fields}