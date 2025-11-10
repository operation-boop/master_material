import anvil.server
from anvil.tables import app_tables
import uuid
from datetime import datetime
import anvil.tables.query as q


@anvil.server.callable
def list_material_cards(statuses=None):
  statuses = statuses or ["Draft", "Submitted - Unverified", "Submitted - Verified"]

  vers = app_tables.master_material_version.search(
    status=q.any_of(*statuses)
  )

  # Keep latest version per document
  latest = {}
  for v in vers:
    doc_id = _get(v, "document_id") or _get(v, "document_uid")
    if not doc_id:
      continue

    vn = _to_num(_get(v, "ver_num"))
    cur = latest.get(doc_id)

    if (cur is None) or (vn > _to_num(_get(cur, "ver_num"))):
      latest[doc_id] = v

  cards = []
  for v in latest.values():
    wpu  = _get(v, "weight_per_unit")
    wuom = _get(v, "weight_uom")
    weight = f"{wpu} {wuom}" if (wpu is not None and wuom) else ""

    ocpu = _get(v, "original_cost_per_unit")
    nccy = _get(v, "native_cost_currency")
    cost = f"{ocpu} {nccy}" if (ocpu is not None and nccy) else ""

    cards.append({
      "document_id": v["document_id"],
      "material_id": _get(v, "master_material_id") or _get(v, "document_id"),
      "ref_id": _get(v, "ref_id") or "",
      "material_name": _get(v, "name") or "",
      "material_type": _get(v, "material_type") or "",
      "fabric_composition": _get(v, "fabric_composition") or _get(v, "generic_material_composition") or "",
      "weight": weight,
      "supplier": _get(v, "supplier_name") or "",
      "cost_per_unit": cost,
      "verification_status": _get(v, "status") or "Draft",
      "ver_num": _get(v, "ver_num") or 1,
      "updated_at": _get(v, "updated_at"),
      "submitted_at": _get(v, "submitted_at"),
      "last_verified_date": _get(v, "last_verified_date"),
    })

  # Sort newest first (like before)
  cards.sort(key=lambda d: (d.get("updated_at") or 0, _to_num(d.get("ver_num"))), reverse=True)
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


