from ._anvil_designer import bingheng_Style_SKUTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class bingheng_Style_SKU(bingheng_Style_SKUTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.load_data()

  ############################################
  # Load data from the database
  ############################################
  def load_data(self):
    """Load SKU data from your database table"""
    if hasattr(app_tables, "sku_table"):
      rows = app_tables.sku_table.search()
      self.repeating_panel_1.items = rows
    else:
      self.repeating_panel_1.items = []
      alert("⚠️ Table 'sku_table' not found — please create it in Data Tables.")

  ############################################
  # Add SKU Entry
  ############################################
  def button_add_sku_click(self, **event_args):
    """Add a new SKU to the database"""
    try:
      sku_id = self.text_box_sku_id.text.strip()
      material = self.text_box_material.text.strip()
      price_text = self.text_box_price.text.strip()

      if not sku_id or not material or not price_text:
        alert("Please fill in all fields.")
        return

      price = float(price_text)

      anvil.server.call('add_sku', sku_id, material, price)
      alert(f"✅ SKU {sku_id} added successfully!")

      # Reload table after adding
      self.load_data()

    except ValueError:
      alert("❌ Price must be a valid number.")
    except Exception as e:
      alert(f"❌ Error adding SKU: {e}")

  def edit_button(self, **event_args):
    """This method is called when the button is clicked"""
  open_form('bingheng_Style_SKU.Style_SKU_sheet')
  pass
def button_generate_qr_click(self, **event_args):
  sku_id = self.text_box_sku_id.text.strip()
  if not sku_id:
    alert("Please enter a SKU ID first.")
    return

  try:
    qr_img = anvil.server.call('get_qr_code', sku_id)
    self.image_qr_preview.source = qr_img
    alert("✅ Unique QR code generated!")
  except Exception as e:
    alert(f"⚠️ QR generation failed: {e}")


def button_export_pdf_click(self, **event_args):
  """Manual export to PDF with QR codes"""
  try:
    data = self.repeating_panel_1.items or []
    if not data:
      alert("No SKU data available to export.")
      return

    pdf_file = anvil.server.call('generate_sku_pdf', data)
    download(pdf_file)
    alert("✅ PDF exported successfully!")

  except Exception as e:
    alert(f"❌ Error exporting PDF: {e}")
