import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import uuid
import pyqrcode
from io import BytesIO, StringIO
import base64
import anvil.media
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import anvil.pdf
from PIL import Image
import csv
import zipfile
from anvil import BlobMedia
import json


# Keep your existing table name
TABLE = app_tables.material_sku__main_
#
# --- SAMPLE uploaded file path (from your workspace) ---
SAMPLE_ATTACHMENT_URL = "/mnt/data/7795bc78-226b-4877-87f7-8d6982339a86.png"

# -----------------------
# CLIENT MANAGEMENT
# -----------------------
@anvil.server.callable
def save_client_info(Enter_Your_Name, Contact_Number, Email, Address):
  """Save client info to Data Table"""
  ref_id = uuid.uuid4().hex[:8].upper()
  app_tables.client__masterstyle_.add_row(
    Clients=Enter_Your_Name,
    Clientcontact=Contact_Number,
    Clientemail=Email,
    Clientbilladd=Address,
    ref_id=ref_id,
    created=datetime.now()
  )
  return {
    "message": f"Client {Enter_Your_Name} saved successfully.",
    "ref_id": ref_id
  }

@anvil.server.callable
def verify_client_login(client_name, ref_id):
  """Verify client login with name and ref ID (returns True/False)."""
  if not client_name or not ref_id:
    return False
  client_name = str(client_name).strip()
  ref_id = str(ref_id).strip().upper()
  row = app_tables.client__masterstyle_.get(Clients=client_name, ref_id=ref_id)
  return row is not None

# -----------------------
# ADMIN ACTION
# -----------------------
@anvil.server.callable
def admin_action(username):
  """Restrict admin-only actions. Single canonical implementation."""
  if not username:
    raise Exception("Missing username")
  if username.lower() != "admin":
    raise Exception("You are not authorized to perform this action.")
  return "Admin action executed."

# -----------------------
# TEST helpers (non-database demo data)
# -----------------------
@anvil.server.callable
def get_test_skus():
  """Return a small list of demo SKUs (plain dicts) for client testing (no DB)."""
  return [
    {
      "row_id": "TEST-001",
      "sku_id": "TSHIRT001",
      "id": "TSHIRT001",
      "ref_id": "A93F2D19",
      "master_material": "Cotton",
      "color": "Blue",
      "size": "L",
      "qr_data": "",
      "sku_cost_override": 12.5,
      "price": 12.5,
      "attachment_url": SAMPLE_ATTACHMENT_URL,
      "created": datetime.now().isoformat()
    },
    {
      "row_id": "TEST-002",
      "sku_id": "TSHIRT002",
      "id": "TSHIRT002",
      "ref_id": "B21K7Z33",
      "master_material": "Polyester",
      "color": "Black",
      "size": "M",
      "qr_data": "",
      "sku_cost_override": 9.99,
      "price": 9.99,
      "attachment_url": SAMPLE_ATTACHMENT_URL,
      "created": datetime.now().isoformat()
    },
    {
      "row_id": "TEST-003",
      "sku_id": "HAT001",
      "id": "HAT001",
      "ref_id": "HAT-555",
      "master_material": "Wool",
      "color": "Gray",
      "size": "OneSize",
      "qr_data": "",
      "sku_cost_override": 7.0,
      "price": 7.0,
      "attachment_url": SAMPLE_ATTACHMENT_URL,
      "created": datetime.now().isoformat()
    },
  ]

@anvil.server.callable
def test_qr():
  """Return a QR BlobMedia for a sample payload so you can check QR generation quickly."""
  return get_qr_code("DEMO_SKU", "DEMOREF", "Cotton", "Red", "XL", 15.0)

# -----------------------
# SKU LIST / CRUD (server-side)
# -----------------------
@anvil.server.callable
def get_skus():
  """
  Return a list of plain dicts for the client repeating panel.
  Defensive: converts rows to dicts, strips out non-serializable fields,
  and protects against unexpected exceptions per-row so one bad row won't break everything.
  """
  try:
    rows = list(TABLE.search())
  except Exception as e:
    raise RuntimeError(f"get_skus: could not query table: {e}")

  out = []
  for r in rows:
    try:
      try:
        row_dict = dict(r)
      except Exception:
        row_dict = {}
        try:
          keys = list(r.keys())
        except Exception:
          keys = []
        for k in keys:
          try:
            row_dict[k] = r[k]
          except Exception:
            row_dict[k] = None

      item = {
        "row_id": (r.get_id() if hasattr(r, "get_id") else None),
        "sku_id": (row_dict.get("sku_id") or row_dict.get("id") or ""),
        "id": row_dict.get("id", ""),
        "ref_id": row_dict.get("ref_id", ""),
        "master_material": (
          (row_dict.get("master_material").get("name") if isinstance(row_dict.get("master_material"), dict) and "name" in row_dict.get("master_material") else None)
          if row_dict.get("master_material") is not None else ""
        ) or (str(row_dict.get("master_material") or "")),
        "color": str(row_dict.get("color") or ""),
        "size": str(row_dict.get("size") or ""),
        "qr_data": str(row_dict.get("qr_data") or ""),
        "sku_cost_override": row_dict.get("sku_cost_override"),
        "price": row_dict.get("price"),
        "attachment_name": (getattr(row_dict.get("attachment"), "name", None) or "") if row_dict.get("attachment") else "",
        "created": (row_dict.get("created").isoformat() if hasattr(row_dict.get("created"), "isoformat") else row_dict.get("created"))
      }
      out.append(item)

    except Exception as row_e:
      out.append({
        "row_id": (r.get_id() if hasattr(r, "get_id") else None),
        "sku_id": getattr(r, "sku_id", "") or "",
        "id": getattr(r, "id", "") or "",
        "ref_id": getattr(r, "ref_id", "") or "",
        "master_material": "",
        "color": "",
        "size": "",
        "qr_data": "",
        "sku_cost_override": None,
        "price": None,
        "attachment_name": "",
        "created": None,
        "_error": f"row conversion error: {row_e}"
      })
  return out

@anvil.server.callable
def add_sku(sku_id, ref_id=None, master_material=None, color=None, size=None, qr_data=None, price=None, attachment=None):
  """Create a new SKU row. attachment may be an anvil.media.Media (optional)."""
  if not sku_id:
    raise ValueError("sku_id required")
  kwargs = dict(
    sku_id=sku_id,
    id=sku_id,
    ref_id=ref_id,
    master_material=master_material,
    color=color,
    size=size,
    qr_data=qr_data,
    price=price,
    created=datetime.now()
  )
  row = TABLE.add_row(**kwargs)
  if attachment is not None:
    row['attachment'] = attachment
  return {"ok": True, "row_id": row.get_id()}

@anvil.server.callable
def update_sku(row_id, updates: dict):
  """Update the DB row identified by row_id with the values in updates."""
  r = TABLE.get_by_id(row_id)
  if r is None:
    raise Exception("Row not found")
  allowed = {"sku_id", "id", "ref_id", "master_material", "color", "size", "qr_data", "price", "attachment"}
  safe_updates = {k: v for k, v in updates.items() if k in allowed}
  if safe_updates:
    r.update(**safe_updates)
  return {"ok": True}

@anvil.server.callable
def delete_sku(row_id):
  """Delete the DB row identified by row_id."""
  r = TABLE.get_by_id(row_id)
  if r is None:
    raise Exception("Row not found")
  r.delete()
  return {"ok": True}

# -----------------------
# QR / PDF helpers (updated)
# -----------------------
@anvil.server.callable
def get_qr_code(sku_id, ref_id="", master_material="", color="", size="", sku_cost_override=None):
  """
  Return a PNG BlobMedia containing a unique QR code based on:
  sku_id, ref_id, master_material, color, size, sku_cost_override.
  """
  if not sku_id:
    raise ValueError("sku_id required")
  sku_id = (sku_id or "").strip()
  ref_id = (ref_id or "").strip()
  master_material = (master_material or "").strip()
  color = (color or "").strip()
  size = (size or "").strip()
  sku_cost_override = "" if sku_cost_override is None else str(sku_cost_override)
  payload = (
    f"SKU:{sku_id}|"
    f"REF:{ref_id}|"
    f"MAT:{master_material}|"
    f"COL:{color}|"
    f"SIZE:{size}|"
    f"COST:{sku_cost_override}|"
    f"UNIQ:{uuid.uuid4().hex[:8]}"
  )
  qr = pyqrcode.create(payload)
  buf = BytesIO()
  qr.png(buf, scale=5)
  buf.seek(0)
  return BlobMedia("image/png", buf.read(), name=f"{sku_id}_qr.png")

@anvil.server.callable
def generate_sku_pdf(data):
  """
  Generate a PDF containing SKU rows (list of dicts with keys sku_id, material, price)
  and embedded QR codes. Returns a BlobMedia('application/pdf', ...).
  """
  if not isinstance(data, (list, tuple)):
    raise ValueError("data must be a list of dicts")
  out = BytesIO()
  c = canvas.Canvas(out, pagesize=A4)
  width, height = A4
  y = height - 60
  c.setFont("Helvetica-Bold", 16)
  c.drawString(50, y, "SKU Export Report with QR Codes")
  y -= 40
  for row in data:
    sku_id = str(row.get("sku_id", row.get("id", "Unknown")))
    material = str(row.get("material", row.get("master_material", "N/A")))
    price = str(row.get("price", "N/A"))
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"SKU ID: {sku_id}")
    c.drawString(250, y, f"Material: {material}")
    c.drawString(450, y, f"Price: {price}")
    y -= 20
    qr_payload = f"{sku_id}-{uuid.uuid4().hex[:8]}"
    qr = pyqrcode.create(qr_payload)
    qr_buf = BytesIO()
    qr.png(qr_buf, scale=3)
    qr_bytes = qr_buf.getvalue()
    try:
      c.drawInlineImage(qr_bytes, 480, y - 50, width=60, height=60)
    except Exception:
      pass
    y -= 80
    if y < 100:
      c.showPage()
      y = height - 60
  c.save()
  out.seek(0)
  return BlobMedia("application/pdf", out.read(), name="SKU_Report.pdf")

# -----------------------
# Backup (keeps original behavior)
# -----------------------
@anvil.server.callable
def backup_fullstack():
  """Create a ZIP containing CSV exports of all app_tables and app_files if possible."""
  def serialize(value):
    if value is None:
      return ""
    if hasattr(value, "get_bytes"):
      return getattr(value, "name", "<media>")
    if hasattr(value, "isoformat"):
      try:
        return value.isoformat()
      except Exception:
        pass
    return str(value)
  zip_buffer = BytesIO()
  with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
    for table_name in dir(app_tables):
      if table_name.startswith("_"):
        continue
      table_obj = getattr(app_tables, table_name)
      try:
        rows = list(table_obj.search())
      except Exception:
        continue
      csv_buf = StringIO()
      writer = csv.writer(csv_buf)
      if rows:
        try:
          first_row = dict(rows[0])
          fieldnames = sorted(first_row.keys())
        except Exception:
          fieldnames = []
        writer.writerow(fieldnames)
        for r in rows:
          try:
            rd = dict(r)
          except Exception:
            rd = {}
          writer.writerow([serialize(rd.get(f)) for f in fieldnames])
      else:
        writer.writerow(["(no rows)"])
      zipf.writestr(f"tables/{table_name}.csv", csv_buf.getvalue().encode("utf-8"))
    # add app_files if possible
    try:
      from anvil.google.drive import app_files
      for f in dir(app_files):
        if f.startswith("_"):
          continue
        file_obj = getattr(app_files, f)
        try:
          data = file_obj.get_bytes()
          name = getattr(file_obj, "name", f)
          zipf.writestr(f"app_files/{name}", data)
        except Exception:
          pass
    except Exception:
      pass
  zip_buffer.seek(0)
  zip_bytes = zip_buffer.read()
  filename = f"anvil_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
  return BlobMedia("application/zip", zip_bytes, name=filename)

# -------------------- END SERVER MODULE --------------------
