import anvil.server
from anvil.tables import app_tables
import uuid
from datetime import datetime
import json
import anvil.tables.query as q


@anvil.server.callable
def create_new_version(document_id, updated_data, user_email):
  
  if not document_id:
    raise ValueError("document_id is required")

  # 1. Get the latest version
  latest = get_latest_version(document_id)
  if not latest:
    raise Exception(f"No existing version found for {document_id}")

  # 2. Check if it's verified
  current_status = latest['status'] or ""

  # 3. Determine new version number
  current_ver = latest['ver_num'] or 0
  new_ver_num = current_ver + 1

  # 4. Create new version row with updated data
  new_version_row = app_tables.master_material_version.add_row(
    # Core identifiers (keep same)
    document_id=document_id,
    document_uid=latest['document_uid'],
    master_material_id=latest['master_material_id'],

    # Version info
    ver_num=new_ver_num,
    status="Draft",  # New versions start as Draft

    # Metadata
    created_by=user_email,
    created_at=datetime.now(),
    updated_at=datetime.now(),
    submitted_at=None,
    last_verified_by=None,
    last_verified_date=None,

    # Copy all existing data fields from latest version
    ref_id=latest['ref_id'],
    name=latest['name'],
    material_type=latest['material_type'],
    supplier_name=latest['supplier_name'],
    country_of_origin=latest['country_of_origin'],

    # Technical specs
    fabric_composition=latest['fabric_composition'],
    generic_material_composition=latest['generic_material_composition'],
    weight_per_unit=latest['weight_per_unit'],
    weight_uom=latest['weight_uom'],
    fabric_roll_width=latest['fabric_roll_width'],
    fabric_cut_width=latest['fabric_cut_width'],
    fabric_cut_width_no_shrinkage=latest['fabric_cut_width_no_shrinkage'],
    weft_shrinkage=latest['weft_shrinkage'],
    werp_shrinkage=latest['werp_shrinkage'],

    # Cost fields
    original_cost_per_unit=latest['original_cost_per_unit'],
    native_cost_currency=latest['native_cost_currency'],
    supplier_selling_tolerance=latest['supplier_selling_tolerance'],
    effective_cost_per_unit=latest['effective_cost_per_unit'],
    vietnam_vat_rate=latest['vietnam_vat_rate'],
    import_duty=latest['import_duty'],
    logistics_rate=latest['logistics_rate'],
    landed_cost_per_unit=latest['landed_cost_per_unit'],

    # Unit of measurement
    unit_of_measurement=latest['unit_of_measurement'],
  )

  # 5. Apply the updated fields
  for key, value in updated_data.items():
    try:
      new_version_row[key] = value
    except Exception as e:
      print(f"Could not update field {key}: {e}")

  # 6. Update master_material table's version_history link
  update_master_material_version_links(document_id, new_version_row)

  return {
    "ok": True,
    "document_id": document_id,
    "new_version": new_ver_num,
    "status": "Draft",
    "message": f"Created version {new_ver_num} for {document_id}"
  }


@anvil.server.callable
def get_latest_version(document_id):
  """Get the latest version row for a document_id"""
  if not document_id:
    return None

  rows = list(app_tables.master_material_version.search(document_id=document_id))
  if not rows:
    return None

  # Find the row with highest ver_num
  latest = None
  for r in rows:
    ver_num = _to_num(r['ver_num'])
    if latest is None or ver_num > _to_num(latest['ver_num']):
      latest = r

  return latest


@anvil.server.callable
def get_version_history(document_id):
  """Get all versions for a document_id, sorted by version number"""
  if not document_id:
    return []

  rows = list(app_tables.master_material_version.search(document_id=document_id))

  # Convert to dictionaries and sort by version
  versions = []
  for r in rows:
    versions.append({
      "ver_num": r['ver_num'],
      "status": r['status'],
      "created_by": r['created_by'],
      "created_at": r['created_at'],
      "updated_at": r['updated_at'],
      "submitted_at": r['submitted_at'],
      "last_verified_by": r['last_verified_by'],
      "last_verified_date": r['last_verified_date'],
    })

  # Sort by version number descending (newest first)
  versions.sort(key=lambda v: v['ver_num'] or 0, reverse=True)

  return versions


def update_master_material_version_links(document_id, new_version_row):
  """
  Updates the master_material table to link all versions.
  Updates both version_history (linked list) and version_history_uid (JSON array).
  """
  # Find or create master_material row
  master_rows = list(app_tables.master_material.search(document_id=document_id))

  if not master_rows:
    # Create new master_material entry
    master_material_id = new_version_row['master_material_id']
    master_row = app_tables.master_material.add_row(
      document_id=document_id,
      master_material_id=master_material_id,
      version_history=[new_version_row],
      version_history_uid=json.dumps([new_version_row.get_id()])
    )
  else:
    # Update existing master_material
    master_row = master_rows[0]

    # Update version_history (linked list)
    current_links = list(master_row['version_history'] or [])
    if new_version_row not in current_links:
      current_links.append(new_version_row)
      master_row['version_history'] = current_links

    # Update version_history_uid (JSON array)
    try:
      uid_list = json.loads(master_row['version_history_uid'] or "[]")
    except:
      uid_list = []

    new_uid = new_version_row.get_id()
    if new_uid not in uid_list:
      uid_list.append(new_uid)
      master_row['version_history_uid'] = json.dumps(uid_list)

  return master_row


@anvil.server.callable
def sync_all_version_links():
  """
  Utility function to sync all existing versions to master_material table.
  Run this once to populate version_history for existing data.
  """
  all_versions = app_tables.master_material_version.search()

  # Group by document_id
  doc_versions = {}
  for v in all_versions:
    doc_id = v['document_id']
    if not doc_id:
      continue
    if doc_id not in doc_versions:
      doc_versions[doc_id] = []
    doc_versions[doc_id].append(v)

  # Update master_material for each document_id
  synced_count = 0
  for doc_id, versions in doc_versions.items():
    # Sort versions by ver_num
    versions.sort(key=lambda v: v['ver_num'] or 0)

    # Find or create master_material row
    master_rows = list(app_tables.master_material.search(document_id=doc_id))

    if not master_rows:
      # Create new
      master_material_id = versions[0]['master_material_id']
      version_uids = [v.get_id() for v in versions]

      app_tables.master_material.add_row(
        document_id=doc_id,
        master_material_id=master_material_id,
        version_history=versions,
        version_history_uid=json.dumps(version_uids)
      )
    else:
      # Update existing
      master_row = master_rows[0]
      version_uids = [v.get_id() for v in versions]

      master_row['version_history'] = versions
      master_row['version_history_uid'] = json.dumps(version_uids)

    synced_count += 1

  return {
    "ok": True,
    "synced_documents": synced_count,
    "total_versions": len(all_versions)
  }


def _to_num(x, default=-1):
  """Convert to number, return default if fails"""
  try:
    return float(x)
  except:
    return default


def _get(row, key, default=None):
  """Safely get value from row"""
  try:
    return row[key]
  except:
    return default