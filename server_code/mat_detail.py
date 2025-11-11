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

  # build rich detail dict (add/remove fields you need)
  wpu   = _get(v, "weight_per_unit")
  wuom  = _get(v, "weight_uom")
  weight = f"{wpu} {wuom}" if (wpu is not None and wuom) else ""

  ocpu  = _get(v, "original_cost_per_unit")
  nccy  = _get(v, "native_cost_currency")
  cost_display = f"{ocpu} {nccy}" if (ocpu is not None and nccy) else ""

  detail = {
    "document_id": _get(v, "document_id"),
    "ver_num": _get(v, "ver_num"),
    "material_id": _get(v, "master_material_id"),
    "ref_id": _get(v, "ref_id", ""),
    "material_name": _get(v, "name", ""),
    "material_type": _get(v, "material_type", ""),
    "supplier": _get(v, "supplier_name", ""),
    "country_of_origin": _get(v, "country_of_origin", ""),
    "created_by": _get(v, "created_by", ""),
    "created_at": _get(v, "created_at"),
    "fabric_composition": _get(v, "fabric_composition") or _get(v, "generic_material_composition", ""),
    "weight": weight,
    "fabric_roll_width": _get(v, "fabric_roll_width"),
    "fabric_cut_width": _get(v, "fabric_cut_width"),
    "original_cost_per_unit": ocpu,
    "cost_display": cost_display,
    "unit_of_measurement": _get(v, "unit_of_measurement") or wuom,
    "verification_status": _get(v, "status", "Draft"),
    "updated_at": _get(v, "updated_at"),
    "submitted_at": _get(v, "submitted_at"),
    "last_verified_date": _get(v, "last_verified_date"),
  }

  return detail

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

