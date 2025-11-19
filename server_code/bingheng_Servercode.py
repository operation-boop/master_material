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
  "message":f"Client {Enter_Your_Name} saved successfully.",
  "ref_id": ref_id
  }

@anvil.server.callable
def verify_client_login(client_name, ref_id):
  """Verify client login with name and ref ID (returns True/False)."""
  if not client_name or not ref_id:
    return False

  # normalize inputs (trim whitespace)
  client_name = str(client_name).strip()
  ref_id = str(ref_id).strip().upper()

  # look up by Clients and the custom ref_id column
  row = app_tables.client__masterstyle_.get(Clients=client_name, ref_id=ref_id)
  return row is not None



# -----------------------
# ADMIN ACTION (single definition)
# -----------------------
@anvil.server.callable
def admin_action(username):
  """Restrict admin-only actions. Single canonical implementation."""
  if not username:
    raise Exception("Missing username")
  if username.lower() != "admin":
    raise Exception("You are not authorized to perform this action.")
  # add admin-only logic here
  return "Admin action executed."


# -----------------------
# QR / SKU
# -----------------------
# @anvil.server.callable
# def get_qr_code(sku_id):
#   """Return a PNG BlobMedia containing a unique QR code for sku_id."""
#   if not sku_id:
#     raise ValueError("sku_id required")

#   unique_code = f"{sku_id}-{uuid.uuid4().hex[:8]}"
#   qr = pyqrcode.create(unique_code)

#   buf = BytesIO()
#   qr.png(buf, scale=5)
#   buf.seek(0)
#   return BlobMedia("image/png", buf.read(), name=f"{sku_id}_qr.png")


# @anvil.server.callable
# def generate_sku_pdf(data):
#   """
#   Generate a PDF containing SKU rows (list of dicts with keys sku_id, material, price)
#   and embedded QR codes. Returns a BlobMedia('application/pdf', ...).
#   """
#   if not isinstance(data, (list, tuple)):
#     raise ValueError("data must be a list of dicts")

#   out = BytesIO()
#   c = canvas.Canvas(out, pagesize=A4)
#   width, height = A4
#   y = height - 60

#   c.setFont("Helvetica-Bold", 16)
#   c.drawString(50, y, "SKU Export Report with QR Codes")
#   y -= 40

#   for row in data:
#     sku_id = str(row.get("sku_id", "Unknown"))
#     material = str(row.get("material", "N/A"))
#     price = str(row.get("price", "N/A"))

#     # Draw SKU text
#     c.setFont("Helvetica", 12)
#     c.drawString(50, y, f"SKU ID: {sku_id}")
#     c.drawString(250, y, f"Material: {material}")
#     c.drawString(450, y, f"Price: {price}")
#     y -= 20

#     # create QR bytes (unique per PDF generation)
#     qr_payload = f"{sku_id}-{uuid.uuid4().hex[:8]}"
#     qr = pyqrcode.create(qr_payload)
#     qr_buf = BytesIO()
#     qr.png(qr_buf, scale=3)
#     qr_bytes = qr_buf.getvalue()

#     # drawInlineImage accepts raw image bytes; provide bytes
#     c.drawInlineImage(qr_bytes, 480, y - 50, width=60, height=60)

#     y -= 80
#     if y < 100:
#       c.showPage()
#       y = height - 60

#   c.save()
#   out.seek(0)
#   return BlobMedia("application/pdf", out.read(), name="SKU_Report.pdf")


# @anvil.server.callable
# def add_sku(sku_id, material, price):
#   """Add a new SKU row"""
#   if not sku_id:
#     raise ValueError("sku_id required")
#   app_tables.sku_table.add_row(
#     sku_id=sku_id,
#     material=material,
#     price=price,
#     created=datetime.now()
#   )
#   return f"✅ SKU {sku_id} added successfully."


# -----------------------
# TEST 2
# -----------------------
# Table reference (your confirmed table name)
TABLE = app_tables.material_sku__main_

# -----------------------
# SKU LIST / CRUD (server-side)
# -----------------------
@anvil.server.callable
def get_skus():
  """Return a list of plain dicts for the client repeating panel."""
  rows = list(app_tables.material_sku__main_.search())
  out = []
  for r in rows:
    out.append({
      "row_id": r.get_id(),
      "sku_id": r.get("sku_id") or r.get("id") or "",
      "id": r.get("id", ""),
      "ref_id": r.get("ref_id", ""),
      "master_material": (r.get("master_material") or ""),
      "color": r.get("color", ""),
      "size": r.get("size", ""),
      "qr_data": r.get("qr_data", ""),
      "sku_cost_override": r.get("sku_cost_override"),
      "price": r.get("price"),
      "attachment_name": getattr(r.get("attachment"), "name", "") if r.get("attachment") else "",
      "created": r.get("created")
    })
  return out



@anvil.server.callable
def add_sku(sku_id, ref_id=None, master_material=None, color=None, size=None, qr_data=None, price=None, attachment=None):
  """Create a new SKU row. attachment may be an anvil.media.Media (optional)."""
  if not sku_id:
    raise ValueError("sku_id required")

  kwargs = dict(
    sku_id=sku_id,
    id=sku_id,               # keep id in sync if you use both
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
    # Ensure your table has an 'attachment' column (Media)
    row['attachment'] = attachment

  return {"ok": True, "row_id": row.get_id()}


@anvil.server.callable
def update_sku(row_id, updates: dict):
  """Update the DB row identified by row_id with the values in updates."""
  r = TABLE.get_by_id(row_id)
  if r is None:
    raise Exception("Row not found")

  # whitelist allowed columns to avoid accidental mass update
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
def get_qr_code(sku_id, ref_id, master_material, color, size, sku_cost_override):
  """
  Return a PNG BlobMedia containing a unique QR code based on:
  sku_id, ref_id, master_material, color, size, sku_cost_override.
  """
  if not sku_id:
    raise ValueError("sku_id required")

  # Normalize values
  sku_id = (sku_id or "").strip()
  ref_id = (ref_id or "").strip()
  master_material = (master_material or "").strip()
  color = (color or "").strip()
  size = (size or "").strip()

  # Convert override to string (may be number or blank)
  sku_cost_override = "" if sku_cost_override is None else str(sku_cost_override)

  # Create payload
  # Format is human-readable and easy to parse later.
  # You can change this to JSON if you prefer — just tell me.
  payload = (
    f"SKU:{sku_id}|"
    f"REF:{ref_id}|"
    f"MAT:{master_material}|"
    f"COL:{color}|"
    f"SIZE:{size}|"
    f"COST:{sku_cost_override}|"
    f"UNIQ:{uuid.uuid4().hex[:8]}"
  )

  # Generate QR code
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
  # Keep your existing implementation or use this one
 

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

    # Draw SKU text
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"SKU ID: {sku_id}")
    c.drawString(250, y, f"Material: {material}")
    c.drawString(450, y, f"Price: {price}")
    y -= 20

    # create QR bytes (unique per PDF generation)
    qr_payload = f"{sku_id}-{uuid.uuid4().hex[:8]}"
    qr = pyqrcode.create(qr_payload)
    qr_buf = BytesIO()
    qr.png(qr_buf, scale=3)
    qr_bytes = qr_buf.getvalue()

    # drawInlineImage accepts raw image bytes
    try:
      c.drawInlineImage(qr_bytes, 480, y - 50, width=60, height=60)
    except Exception:
      # If drawInlineImage doesn't accept raw bytes in your environment,
      # create a temporary BlobMedia and use anvil.pdf.render or similar alternative.
      pass

    y -= 80
    if y < 100:
      c.showPage()
      y = height - 60

  c.save()
  out.seek(0)
  return BlobMedia("application/pdf", out.read(), name="SKU_Report.pdf")
  
# #########################TEST#######################

@anvil.server.callable
def backup_fullstack():
  """Create a ZIP containing:
     - CSV export of each app_table
     - All app_files (if any)
     Works on Standard Python Server (BlobMedia only).
  """

  # --- Helper serializer for complex values ---
  def serialize(value):
    if value is None:
      return ""
    # Handle Media objects
    if hasattr(value, "get_bytes"):
      return getattr(value, "name", "<media>")
    # Handle datetime
    if hasattr(value, "isoformat"):
      try:
        return value.isoformat()
      except:
        pass
    # Fallback
    return str(value)

  zip_buffer = BytesIO()

  with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:

    # === Export all app_tables as CSV ===
    for table_name in dir(app_tables):
      if table_name.startswith("_"):
        continue

      table_obj = getattr(app_tables, table_name)

      # Skip non-table attributes
      try:
        rows = list(table_obj.search())
      except:
        continue

      csv_buf = StringIO()
      writer = csv.writer(csv_buf)

      if rows:
        first_row = dict(rows[0])
        fieldnames = sorted(first_row.keys())
        writer.writerow(fieldnames)

        for r in rows:
          rd = dict(r)
          writer.writerow([serialize(rd.get(f)) for f in fieldnames])
      else:
        writer.writerow(["(no rows)"])

      # Add CSV to ZIP
      zipf.writestr(
        f"tables/{table_name}.csv",
        csv_buf.getvalue().encode("utf-8")
      )

    # === Add app_files ===
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
        except:
          pass
    except:
      pass

  # Finalize ZIP
  zip_buffer.seek(0)
  zip_bytes = zip_buffer.read()

  filename = f"anvil_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

  # RETURN AS BLOBMEDIA (Standard Server uses this)
  return BlobMedia("application/zip", zip_bytes, name=filename)


