import anvil.users
import anvil.server
from anvil.tables import app_tables

@anvil.server.callable
def list_material_cards(statuses=None):
  """Get list of material cards filtered by status"""
  statuses = statuses or ["Draft", "Submitted - Unverified", "Submitted - Verified"]

  masters = app_tables.master_material.search()

  cards = []
  for master in masters:
    version = master['current_version']
    if not version:
      continue

    # Filter by status
    if version['status'] not in statuses:
      continue

    # Build display strings
    wpu = version['weight_per_unit']
    wuom = version['weight_uom']
    weight = f"{wpu} {wuom}" if (wpu and wuom) else ""

    ocpu = version['original_cost_per_unit']
    nccy = version['native_cost_currency']
    cost = f"{ocpu} {nccy}" if (ocpu and nccy) else ""

    cards.append({
      "document_id": master['document_id'] or " ",
      "master_material_id": version['master_material_id'] or " ",
      "ref_id": version['ref_id'] or " ",
      "material_name": version['name'] or " ",
      "material_type": version['material_type'] or " ",
      "fabric_composition": version['fabric_composition'] or " ",
      "weight": weight or " ",
      "supplier": version['supplier_name'] or " ",
      "cost_per_unit": cost or " ",
      "verification_status": version['status'] or "Draft",
      "ver_num": version['ver_num'] or " ",
    })

  return cards