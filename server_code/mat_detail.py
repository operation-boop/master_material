import anvil.server
from anvil.tables import app_tables

@anvil.server.callable
def get_material_detail(document_id):
  v = app_tables.master_material_version.get(document_id=document_id)

  if not v:
    raise Exception(f"No document found for ID: {document_id}")


  def _get(key, default=None):
    try:
      return v.get(key, default)
    except Exception:
      return default
      
  wpu  = _get(v, "weight_per_unit")
  wuom = _get(v, "weight_uom")
  weight = f"{wpu} {wuom}" if (wpu is not None and wuom) else ""

  ocpu = _get(v, "original_cost_per_unit")
  nccy = _get(v, "native_cost_currency")
  cost_display = f"{ocpu} {nccy}" if (ocpu is not None and nccy) else ""

  return {
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



