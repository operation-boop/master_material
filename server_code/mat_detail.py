import anvil.server
from anvil.tables import app_tables

@anvil.server.callable
def get_version_by_doc_and_ver(document_id, ver_num):
  """Return a single master_material_version Row matching document_id and ver_num.

  - document_id: string like "vin_mmat_0001"
  - ver_num: int or string representing the version number
  Raises ValueError if not found.
  """
  if not document_id:
    raise ValueError("document_id is required")

  # Try exact get() first (works when types stored consistently)
  try:
    row = app_tables.master_material_version.get(document_id=document_id, ver_num=ver_num)
    if row is not None:
      return row
  except Exception:
    # ignore and fall back to search (handles type mismatches)
    pass

  # Fallback: search and compare ver_num as int (safer against string/number mismatch)
  rows = list(app_tables.master_material_version.search(document_id=document_id))
  for r in rows:
    try:
      if int(r.get('ver_num') or 0) == int(ver_num):
        return r
    except Exception:
      # if conversion fails for a row, skip it
      continue

  # If we reach here, not found
  raise ValueError(f"Version not found: {document_id} v{ver_num}")
