import anvil.server
from anvil.tables import app_tables
import json

@anvil.server.callable
def _safe_get(row, key, default=None):
  try:
    return row[key]
  except Exception:
    return default
    
@anvil.server.callable
def _format_composition(raw_value):
  """
  Accepts either:
    - JSON string: '[{"fiber":"Cotton","percentage":100}]'
    - Python list: [{"fiber":"Cotton","percentage":100}]
    - Anything else -> returns as-is or empty string
  Returns: '100% Cotton' / '60% Cotton / 40% Polyester'
  """
  if raw_value is None:
    return ""

  data = raw_value
  if isinstance(raw_value, str):
    try:
      data = json.loads(raw_value)
    except Exception:
      # Not JSON; return the string as-is
      return raw_value

  if isinstance(data, list):
    parts = []
    for item in data:
      try:
        pct = float(item.get("percentage", 0))
        fiber = str(item.get("fiber", "")).strip()
        if fiber:
          parts.append(f"{pct:.0f}% {fiber}")
      except Exception:
        continue
    return " / ".join(parts)
  # Fallback: return whatever it is as a string
  return str(raw_value)

@anvil.server.callable
def _format_weight(version_row):
  # Prefer structured weight fields
  w = _safe_get(version_row, "weight_per_unit")
  uom = _safe_get(version_row, "weight_uom")
  if w is not None and uom:
    try:
      # If numeric, avoid too many decimals
      w = float(w)
      if abs(w - round(w)) < 1e-9:
        w = int(w)
      return f"{w}{uom}"
    except Exception:
      pass

  # Fallback to a generic "weight" column if you have one
  w2 = _safe_get(version_row, "weight")
  return w2 or ""
  
@anvil.server.callable
def get_material_cards_for_list():
  """
  Returns a list of dicts for Material_list to render.
  - Always includes: master_material_id, name, ref_id, material_type, fabric_composition, weight, status
  - Includes supplier_name ONLY when status == 'Submitted'
  """
  items = []
  for master in app_tables.master_material.search():
    version = _safe_get(master, "current_version")
    if not version:
      continue

    status = _safe_get(version, "status", "Creating")

    item = {
      "master_material_id": _safe_get(master, "document_id"),
      "name": _safe_get(version, "name", ""),
      "ref_id": _safe_get(version, "ref_id", ""),
      "material_type": _safe_get(version, "material_type", ""),
      "fabric_composition": _format_composition(_safe_get(version, "fabric_composition")),
      "weight": _format_weight(version),
      "status": status,
      "original_cost_per_unit": _safe_get(version,"original_cost_per_unit", "")
    }

    if status == "Submitted":
      item["supplier_name"] = _safe_get(version, "supplier_name", "")

    items.append(item)

  # (Optional) sort: submitted first, then drafts, newest master first if you have timestamps
  # items.sort(key=lambda x: (x["status"] != "Submitted", x["master_material_id"]), reverse=False)

  return items
  
@anvil.server.callable
def get_material_card_by_document_id(document_id):
  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    return None
  version = master['current_version']
  if not version:
    return None

  status = _safe_get(version, "status", "Creating")
  item = {
    "master_material_id": _safe_get(master, "document_id", ""),
    "name": _safe_get(version, "name", ""),
    "ref_id": _safe_get(version, "ref_id", ""),
    "material_type": _safe_get(version, "material_type", ""),
    "fabric_composition": _format_composition(_safe_get(version, "fabric_composition")),
    "weight": _format_weight(version),
    "status": status,
    "original_cost_per_unit": _safe_get(version, "original_cost_per_unit", "")
  }
  if status == "Submitted":
    item["supplier_name"] = _safe_get(version, "supplier_name", "")
  return item



