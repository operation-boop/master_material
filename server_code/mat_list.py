import anvil.server
from anvil.tables import app_tables
import uuid
from datetime import datetime
import anvil.tables.query as q


@anvil.server.callable
def list_material_cards(statuses=None):
  statuses = statuses or ["Draft", "Submitted - Unverified", "Submitted - Verified"]

  # Get all master materials
  masters = app_tables.master_material.search()

  cards = []
  for master in masters:
    version = master['current_version']
    if not version:
      continue

    # Filter by status
    if version['status'] not in statuses:
      continue

    # Build card data
    wpu = version['weight_per_unit']
    wuom = version['weight_uom']
    weight = f"{wpu} {wuom}" if (wpu and wuom) else ""

    ocpu = version['original_cost_per_unit']
    nccy = version['native_cost_currency']
    cost = f"{ocpu} {nccy}" if (ocpu and nccy) else ""

    cards.append({
      "document_id": master['document_id'],
      "material_id": version['master_material_id'],
      "ref_id": version['ref_id'] or "",
      "material_name": version['name'] or "",
      "material_type": version['material_type'] or "",
      "fabric_composition": version['fabric_composition'] ,
      "weight": weight,
      "supplier": version['supplier_name'] or "",
      "cost_per_unit": cost,
      "verification_status": version['status'] or "Draft",
      "ver_num": version['ver_num'],
    })

  return cards

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