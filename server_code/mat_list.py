import anvil.server
from anvil.tables import app_tables
import json
from datetime import datetime

SHORT_UOM = {
  "GSM (gram/sq meter)": "GSM",
  "GPP (gram/piece)": "GPP",
  "Meter": "m",
  "Piece": "pc",
}

def _fmt_composition(json_str):
  """Turn JSON string into '60% Cotton / 40% Polyester'."""
  if not json_str:
    return ""
  try:
    arr = json.loads(json_str) if isinstance(json_str, str) else json_str
  except Exception:
    return ""
  parts = []
  for it in arr or []:
    try:
      pct = float(it.get("percentage", 0))
      name = (it.get("material") or it.get("fiber") or "").strip()
      if name:
        parts.append(f"{pct:.0f}% {name}")
    except Exception:
      continue
  return " / ".join(parts)

def _row_val(row, key, default=None):
  try:
    return row[key]
  except Exception:
    return default

def _fmt_weight(version):
  v = _row_val(version, "weight_per_unit")
  u = _row_val(version, "weight_uom", "")
  if v is None:
    return ""
  short = SHORT_UOM.get(u, u or "")
  return f"{v:g} {short}".strip()

def _version_summary(version):
  """Build a dict the MaterialCard can bind to."""
  return {
    "document_id":     _row_val(version, "document_id", ""),
    "ver_num":         _row_val(version, "ver_num", 0),
    "master_material_id": _row_val(version, "master_material_id", ""),
    "name":            _row_val(version, "name", ""),
    "ref_id":          _row_val(version, "ref_id", ""),
    "material_type":   _row_val(version, "material_type", ""),
    "fabric_composition": _fmt_composition(_row_val(version, "fabric_composition", "")),
    "weight":          _fmt_weight(version),
    "supplier_name":   _row_val(version, "supplier_name", ""),
    "status":          _row_val(version, "status", ""),
    "original_cost_per_unit": _row_val(version, "original_cost_per_unit", None),
  }

@anvil.server.callable
def get_material_summary(document_id):
  """Summary for a single material (current version)."""
  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    raise Exception(f"Material {document_id} not found")
  version = master['current_version']
  if not version:
    raise Exception("No current version found")
  return _version_summary(version)

@anvil.server.callable
def list_material_summaries():
  """All cards (one per master, current version)."""
  items = []
  for m in app_tables.master_material.search():
    v = _row_val(m, "current_version")
    if v:
      items.append(_version_summary(v))
  # newest first (optional)
  items.sort(key=lambda d: (d.get("document_id") or ""), reverse=True)
  return items



