import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q

@anvil.server.callable
def get_material_detail(document_id):
  if not document_id:
    raise ValueError("document_id is required")

  # search both columns, then pick latest by ver_num
  rows = list(app_tables.master_material_version.search(document_id=document_id)) + \
  list(app_tables.master_material_version.search(document_uid=document_id))

  if not rows:
    raise Exception(f"No material version found for ID: {document_id}")

  latest = None
  for r in rows:
    if latest is None or _to_num(_get(r, "ver_num")) > _to_num(_get(latest, "ver_num")):
      latest = r
  v = latest


  ocpu  = _get(v, "original_cost_per_unit")
  nccy  = _get(v, "native_cost_currency")
  cost_display = f"{ocpu} {nccy}" if (ocpu is not None and nccy) else ""

  detail = {
    "document_id": _get(v, "document_id"),
    "ver_num": _get(v, "ver_num"),
    "master_material_id": _get(v, "master_material_id", ""),
    "name": _get(v, "name", ""),
    "ref_id": _get(v, "ref_id", ""),
    "material_type": _get(v, "material_type", ""),
    "supplier": _get(v, "supplier_name", ""),
    "country_of_origin": _get(v, "country_of_origin", ""),
    "created_by": _get(v, "created_by", ""),
    "created_at": _get(v, "created_at"),
    "fabric_composition": _get(v, "fabric_composition"),
    "weight_per_unit": _get(v,"weight_per_unit"),
    "fabric_roll_width": _get(v, "fabric_roll_width"),
    "fabric_cut_width": _get(v, "fabric_cut_width"),
    "original_cost_per_unit": ocpu,
    "cost_display": cost_display,
    "unit_of_measurement": _get(v, "unit_of_measurement"),
    "verification_status": _get(v, "status", "Draft"),
    "updated_at": _get(v, "updated_at"),
    "submitted_at": _get(v, "submitted_at"),
    "last_verified_date": _get(v, "last_verified_date"),
  }

  return detail

@anvil.server.callable
def get_technical_detail(document_id):
  rows = list(app_tables.master_material_version.search(document_id=document_id)) + \
  list(app_tables.master_material_version.search(document_uid=document_id))

  latest = None
  for r in rows:
    if latest is None or _to_num(_get(r, "ver_num")) > _to_num(_get(latest, "ver_num")):
      latest = r
    v = latest

    techdetails = {
      "fabric_composition": _get(v, "fabric_composition"),
      "fabric_roll_width": _get(v,"fabric_roll_width"),
      "fabric_cut_width": _get(v,"fabric_cut_width"),
      "fabric_cut_width_no_shrinkage": _get(v,"fabric_cut_width_no_shrinkage"),
      "weight_per_unit":_get(v,"weight_per_unit"),
      "weft_shrinkage":_get(v,"weft_shrinkage"),
      "werp_shrinkage":_get(v,"werp_shrinkage"),
    }
    return techdetails

@anvil.server.callable
def get_cost_detail(document_id):
  rows = list(app_tables.master_material_version.search(document_id=document_id)) + \
  list(app_tables.master_material_version.search(document_uid=document_id))

  latest = None
  for r in rows:
    if latest is None or _to_num(_get(r, "ver_num")) > _to_num(_get(latest, "ver_num")):
      latest = r
    v = latest

    costdetails = {
      "original_cost_per_unit": _get(v,"original_cost_per_unit"),
      "currency": _get(v,"native_cost_currency"),
      "supplier_tolerance": _get(v,"supplier_selling_tolerance"),
      "effective_cost": _get(v,"effective_cost_per_unit"),
      "vat": _get(v,"vietnam_vat_rate"),
      "import_duty": _get(v,"import_duty"),
      "logistics_rate": _get(v,"logistics_rate"),
      "landed_cost": _get(v,"landed_cost_per_unit"),
    }
    return costdetails
    
def _get(row, key, default=None):
  try:
    return row[key]
  except Exception:
    return default

def _to_num(x, default=-1):
  try:
    return float(x)
  except Exception:
    return default

@anvil.server.callable
def get_material_full_row(document_id):
  """Return the entire row (all columns) of the LATEST version for the given document_id"""
  if not document_id:
    return None

  rows = app_tables.master_material_version.search(document_id=document_id)
  
  latest = None
  for r in rows:
    if latest is None or (r['ver_num'] > latest['ver_num']):
      latest = r

    # if found, return the whole row as a dict
  if latest:
    return dict(latest)
  return None