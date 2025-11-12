import anvil.server
import anvil.users
from datetime import datetime
from anvil.tables import app_tables


@anvil.server.callable
def verify_material(document_id: str):
  user = anvil.users.get_user()
  if not user:
    raise Exception("You must be logged in to verify materials.")
  if user['role'] != "Admin":
    raise Exception("Permission denied: only admins can verify.")
  if not document_id:
    raise Exception("Missing document_id.")
  rows = list(app_tables.master_material_version.search(document_id=document_id))
  if not rows:
    raise Exception(f"No version rows found for {document_id}.")
  try:
    latest = max(rows, key=lambda r: (r['ver_num'] or 0, r['created_at'] or datetime.min))
  except Exception:
    latest = rows[0]
  current_status = latest['status'] or ""
  if current_status == "Submitted - Verified":
    raise Exception("This material is already verified.")
  try:
    latest['status'] = "Submitted - Verified"
    latest['last_verified_by'] = user['email'] or user['full_name'] or "Unknown"
    latest['last_verified_date'] = datetime.now()
    return {"ok": True, "message": f"{document_id} verified by {latest['last_verified_by']}."}
  except Exception as e:
    raise Exception(f"Failed to update version row: {e}")


