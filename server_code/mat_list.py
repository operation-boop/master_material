import anvil.server
from anvil.tables import app_tables
import json
from datetime import datetime

@anvil.server.callable
def list_material_cards():
  """
  Return a list of dicts for the Material_list UI.
  Pulls from master_material.current_version so we show the latest values.
  """
  rows = app_tables.master_material.search()
  cards = []
  for r in rows:
    v = r.get('current_version')
    if not v:
      continue

    cards.append({
      "document_id": r.get('document_id'),
      "ref_id": v.get('ref_id'),
      "material_name": v.get('name'),
      "material_type": v.get('material_type'),
      "fabric_composition": v.get('fabric_composition'),
      "weight": (
        f"{v.get('weight_per_unit')} {v.get('weight_uom')}"
        if v.get('weight_per_unit') and v.get('weight_uom') else None
      ),
      "supplier": v.get('supplier_name'),
      "cost_per_unit": (
        f"{v.get('original_cost_per_unit')} {v.get('native_cost_currency')}"
        if v.get('original_cost_per_unit') and v.get('native_cost_currency') else None
      ),
      "verification_status": v.get('status') or "Draft"
    })
  return cards



