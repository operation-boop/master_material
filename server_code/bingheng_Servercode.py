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
@anvil.server.callable
def get_qr_code(sku_id):
  """Return a PNG BlobMedia containing a unique QR code for sku_id."""
  if not sku_id:
    raise ValueError("sku_id required")

  unique_code = f"{sku_id}-{uuid.uuid4().hex[:8]}"
  qr = pyqrcode.create(unique_code)

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
    sku_id = str(row.get("sku_id", "Unknown"))
    material = str(row.get("material", "N/A"))
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

    # drawInlineImage accepts raw image bytes; provide bytes
    c.drawInlineImage(qr_bytes, 480, y - 50, width=60, height=60)

    y -= 80
    if y < 100:
      c.showPage()
      y = height - 60

  c.save()
  out.seek(0)
  return BlobMedia("application/pdf", out.read(), name="SKU_Report.pdf")


@anvil.server.callable
def add_sku(sku_id, material, price):
  """Add a new SKU row"""
  if not sku_id:
    raise ValueError("sku_id required")
  app_tables.sku_table.add_row(
    sku_id=sku_id,
    material=material,
    price=price,
    created=datetime.now()
  )
  return f"✅ SKU {sku_id} added successfully."


# -----------------------
# FULL STACK BACKUP
# -----------------------
# @anvil.server.callable
# def backup_fullstack():
#   """Create and return a zip of all app_tables as CSV files."""
#   zip_buffer = BytesIO()
#   with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
#     for table_name in dir(app_tables):
#       if table_name.startswith("_"):
#         continue
#       table = getattr(app_tables, table_name)
#       rows = list(table.search())

#       # Build CSV text
#       csv_buf = BytesIO()
#       writer = csv.writer(csv_buf)
#       if rows:
#         # header
#         fieldnames = list(rows[0].keys())
#         writer.writerow(fieldnames)
#         for r in rows:
#           writer.writerow([r.get(f, "") for f in fieldnames])
#       else:
#         writer.writerow(["No data in this table"])

#       zipf.writestr(f"{table_name}.csv", csv_buf.getvalue().decode("utf-8"))

#   zip_buffer.seek(0)
#   filename = f"anvil_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
#   return BlobMedia("application/zip", zip_buffer.read(), name=filename)
  
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

#---------------------------------------------------------------------------
#--------------- ADD SKU FUNCTION ------------------------------------------
#---------------------------------------------------------------------------

@anvil.server.callable
def get_skus():
  """Return SKUs as a list of dicts for client-side display."""
  rows = app_tables.material_sku__main_.search()
  result = []
  for r in rows:
    result.append({
      "row_id": r.get_id(),
      "sku_id": r["sku_id"],
      "material": r["material"],
      "price": r["price"],
      "created": r["created"],
    })
  return result
