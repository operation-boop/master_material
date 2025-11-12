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
from io import BytesIO
import base64
import anvil.media
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import anvil.pdf
from PIL import Image
import csv
import zipfile

# --------------------------------------------------
# CLIENT MANAGEMENT
# --------------------------------------------------
@anvil.server.callable
def save_client_info(Enter_Your_Name, Contact_Number, Email, Address):
  """Save client info to Data Table"""
  app_tables.client__masterstyle_.add_row(
    Clients=Enter_Your_Name,
    Clientcontact=Contact_Number,
    Clientemail=Email,
    Clientbilladd=Address,
    created=datetime.now()
  )
  return f"Client {Enter_Your_Name} saved successfully"


@anvil.server.callable
def verify_client_login(client_name, ref_id):
  """Verify client login with name and ref ID"""
  try:
    ref_id = int(ref_id)
  except ValueError:
    return False

  row = app_tables.client__masterstyle_.get(Clients=client_name, id=ref_id)
  return row is not None


@anvil.server.callable
def admin_action(username):
  """Restrict admin-only actions"""
  if username.lower() != "admin":
    raise Exception("You are not authorized to perform this action.")


# --------------------------------------------------
# QR + SKU MANAGEMENT
# --------------------------------------------------
@anvil.server.callable
def get_qr_code(sku_id):
  """Generate a unique QR code for each SKU ID"""
  unique_code = f"{sku_id}-{uuid.uuid4().hex[:8]}"
  qr = pyqrcode.create(unique_code)

  buf = BytesIO()
  qr.png(buf, scale=5)
  buf.seek(0)
  return anvil.BlobMedia("image/png", buf.read(), name=f"{sku_id}_qr.png")


@anvil.server.callable
def generate_sku_pdf(data):
  """Generate PDF containing SKU list with QR codes"""
  buffer = BytesIO()
  c = canvas.Canvas(buffer, pagesize=A4)
  width, height = A4
  y = height - 60

  c.setFont("Helvetica-Bold", 16)
  c.drawString(50, y, "SKU Export Report with QR Codes")
  y -= 40

  for row in data:
    sku_id = row.get("sku_id", "Unknown")
    material = row.get("material", "N/A")
    price = row.get("price", "N/A")

    # Draw SKU details
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"SKU ID: {sku_id}")
    c.drawString(250, y, f"Material: {material}")
    c.drawString(450, y, f"Price: {price}")
    y -= 20

    # Generate QR code
    qr_data = f"{sku_id}-{uuid.uuid4().hex[:8]}"
    qr = pyqrcode.create(qr_data)
    qr_buffer = BytesIO()
    qr.png(qr_buffer, scale=3)
    qr_buffer.seek(0)

    # Draw QR image
    c.drawInlineImage(qr_buffer, 480, y - 50, width=60, height=60)

    y -= 80
    if y < 100:
      c.showPage()
      y = height - 60

  c.save()
  buffer.seek(0)
  return anvil.BlobMedia("application/pdf", buffer.read(), name="SKU_Report.pdf")


@anvil.server.callable
def add_sku(sku_id, material, price):
  """Add a new SKU row"""
  app_tables.sku_table.add_row(
    sku_id=sku_id,
    material=material,
    price=price,
    created=datetime.now()
  )
  return f"✅ SKU {sku_id} added successfully."


# --------------------------------------------------
# FULL STACK BACKUP (ALL TABLES → ZIP)
# --------------------------------------------------
@anvil.server.callable
def backup_fullstack():
  """Create a ZIP backup of all Data Tables"""
  zip_buffer = BytesIO()

  with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
    for table_name in dir(app_tables):
      if not table_name.startswith("_"):
        table = getattr(app_tables, table_name)
        rows = table.search()

        csv_buffer = BytesIO()
        writer = csv.writer(csv_buffer)

        # Write headers
        if len(rows) > 0:
          fieldnames = list(rows[0].keys())
          writer.writerow(fieldnames)

          # Write rows
          for row in rows:
            writer.writerow([row.get(f, "") for f in fieldnames])
        else:
          writer.writerow(["No data in this table"])

        # Add CSV file to zip
        zipf.writestr(f"{table_name}.csv", csv_buffer.getvalue().decode("utf-8"))

  zip_buffer.seek(0)
  filename = f"anvil_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
  return anvil.BlobMedia("application/zip", zip_buffer.read(), name=filename)
