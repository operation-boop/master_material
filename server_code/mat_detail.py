import anvil.server
from anvil.tables import app_tables

@anvil.server.callable
def get_material_detail(document_id):
  v = app_tables.master_material_version.get(document_id=document_id)

  if not v:
    raise Exception(f"No document found for ID: {document_id}")

  # Format combined fields
  wpu  = v["weight_per_unit"]
  wuom = v["weight_uom"]
  weight = f"{wpu} {wuom}" if wpu and wuom else ""

  ocpu = v["original_cost_per_unit"]
  nccy = v["native_cost_currency"]
  cost = f"{ocpu} {nccy}" if ocpu and nccy else ""

  return {
    "document_id": v["document_id"],
    "ver_num": v["ver_num"],
    "material_id": v["master_material_id"],
    "ref_id": v["ref_id"] or "",
    "material_name": v["name"] or "",
    "material_type": v["material_type"] or "",
    "supplier": v["supplier_name"] or "",
    "country_of_origin": v["country_of_origin"] or"",
    "created_by": v["created_by"],
    "created_at":["created_at"],
    "fabric_composition": v["fabric_composition"] or v["generic_material_composition"] or "",
    "weight": weight,
    "fabric_roll_width": v["fabric_roll_width"],
    "fabric_cut_width": v["fabric_cut_width"],
    "original_cost_per_unit": cost,
    "unit_of_measurement": v["weight_uom"],
    "verification_status": v["status"] or "Draft",
    "updated_at": v["updated_at"],
    "submitted_at": v["submitted_at"],
    "last_verified_date": v["last_verified_date"],
  }