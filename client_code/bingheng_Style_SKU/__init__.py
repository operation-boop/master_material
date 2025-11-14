from ._anvil_designer import bingheng_Style_SKUTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


# class bingheng_Style_SKU(bingheng_Style_SKUTemplate):
#   def __init__(self, **properties):
#     # Set Form properties and Data Bindings.
#     self.init_components(**properties)
#     self.load_data()

#     ############################################
#     # Load data from the database
#     ############################################
#   def load_data(self):
#     """Load SKU data from your database table"""
#     if hasattr(app_tables, "sku_table"):
#       rows = app_tables.sku_table.search()
#       self.repeating_panel_1.items = rows
#     else:
#       self.repeating_panel_1.items = []
#       alert("⚠️ Table 'sku_table' not found — please create it in Data Tables.")

#     ############################################
#     # Add SKU Entry
#     ############################################
  

#   def edit_button(self, **event_args):
#     """Called when edit button is clicked — open the sheet"""
#     # This call will only run when the button is clicked (not at import)
#     open_form('bingheng_Style_SKU.Style_SKU_sheet')

#   def button_generate_qr(self, **event_args):
#     sku_id = self.text_box_sku_id.text.strip()
#     if not sku_id:
#       alert("Please enter a SKU ID first.")
#       return

#     try:
#       # server call from event handler — allowed
#       qr_img = anvil.server.call('get_qr_code', sku_id)
#       self.image_qr_preview.source = qr_img
#       alert("✅ Unique QR code generated!")
#     except Exception as e:
#       alert(f"⚠️ QR generation failed: {e}")

#   def button_export_pdf(self, **event_args):
#     """Manual export to PDF with QR codes"""
#     try:
#       data = self.repeating_panel_1.items or []
#       if not data:
#         alert("No SKU data available to export.")
#         return

#       pdf_file = anvil.server.call('generate_sku_pdf', data)
#       download(pdf_file)
#       alert("✅ PDF exported successfully!")

#     except Exception as e:
#       alert(f"❌ Error exporting PDF: {e}")

class bingheng_Style_SKU(bingheng_Style_SKUTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Load rows into the repeating panel
    self.load_data()

  ############################################
  # Load data from the database
  ############################################
  def load_data(self):
    """Load SKU data from your database table and bind to repeating_panel_1.

    Each item is a dict and contains the original Row under key '_row' so
    the item-template can perform row-level operations if needed.
    """
    try:
      if not hasattr(app_tables, "sku_table"):
        self.repeating_panel_1.items = []
        alert("⚠️ Table 'sku_table' not found — please create it in Data Tables.")
        return

      rows = list(app_tables.sku_table.search())  # fetch rows
      items = []
      for r in rows:
        attachment = r.get("attachment")
        items.append({
          "_row": r,
          "sku_id": r.get("sku_id", ""),
          "material": r.get("material", ""),
          "price": r.get("price", 0),
          "attachment_name": getattr(attachment, "name", "") if attachment else "",
          "price_display": f"{r.get('price', 0):,.2f}"
        })

      self.repeating_panel_1.items = items

    except Exception as e:
      alert(f"❌ Failed to load SKU data: {e}")
      self.repeating_panel_1.items = []

  def refresh_data(self):
    """Helper to reload the repeating panel after add/edit/delete."""
    self.load_data()

  ############################################
  # Add SKU Entry (opens file picker)
  ############################################
  # def button_add_sku(self, **event_args):
  #   """Validate fields and open FileLoader for user to pick an attachment."""
  #   try:
  #     sku_id = (self.text_box_sku_id.text or "").strip()
  #     material = (self.text_box_material.text or "").strip()
  #     price_text = (self.text_box_price.text or "").strip()

  #     if not sku_id or not material or not price_text:
  #       alert("Please fill SKU ID, Material and Price before choosing a file.")
  #       return

  #     # Quick client-side numeric validation
  #     try:
  #       float(price_text)
  #     except Exception:
  #       alert("Please enter a valid numeric price before selecting a file.")
  #       return

  #     # Open the file dialog; user will trigger file_loader_sku_change
  #     # Make sure a FileLoader component named `file_loader_sku` exists on the form
  #     try:
  #       self.file_loader_sku.open_file_dialog()
  #     except Exception as fe:
  #       # If FileLoader is missing or opening fails, fallback to direct add without file
  #       if not confirm("File picker is unavailable. Add SKU without attachment?"):
  #         return
  #       # call server with no file
  #       price = float(price_text)
  #       res = anvil.server.call('add_sku', sku_id, material, price, None)
  #       if isinstance(res, dict) and res.get("ok"):
  #         alert(f"✅ SKU {sku_id} added (no file).")
  #         self.load_data()
  #       else:
  #         alert("✅ SKU added (server response unexpected).")
  #         self.load_data()

  #   except Exception as e:
  #     alert(f"❌ Error while starting add flow: {e}")

  ############################################
  # FileLoader change handler — triggered when user picks file
  # Ensure you have a FileLoader component named `file_loader_sku` in Designer.
  ############################################
  def file_loader_1(self, file, **event_args):
    """Called after user selects a file. `file` is an anvil.media.Media or None."""
    try:
      # If user cancelled the picker, file will be None
      if file is None:
        return

      sku_id = (self.text_box_sku_id.text or "").strip()
      material = (self.text_box_material.text or "").strip()
      price_text = (self.text_box_price.text or "").strip()

      if not sku_id or not material or not price_text:
        alert("Fields missing — please fill SKU ID, Material and Price before selecting a file.")
        return

      try:
        price = float(price_text)
      except Exception:
        alert("Price must be a valid number.")
        return

      # Optional confirm
      proceed = confirm(f"Upload file '{getattr(file, 'name', 'file')}' for SKU '{sku_id}'?")
      if not proceed:
        return

      # Call server and pass the Media object
      res = anvil.server.call('add_sku', sku_id, material, price, file)

      if isinstance(res, dict) and res.get("ok"):
        alert(f"✅ SKU {sku_id} with attachment uploaded.")
        # refresh and clear inputs
        self.load_data()
        self.text_box_sku_id.text = ""
        self.text_box_material.text = ""
        self.text_box_price.text = ""
      else:
        alert("✅ SKU added (server response unexpected).")
        self.load_data()

    except Exception as e:
      alert(f"❌ Error uploading file / adding SKU: {e}")

  ############################################
  # Edit / QR / Export handlers (kept from your original code)
  ############################################
  def edit_button(self, **event_args):
    """Called when edit button is clicked — open the sheet"""
    try:
      open_form('bingheng_Style_SKU.Style_SKU_sheet')
    except Exception as e:
      alert(f"❌ Could not open edit sheet: {e}")

  def get_qr_code(self, **event_args):
    sku_id = (self.text_box_sku_id.text or "").strip()
    if not sku_id:
      alert("Please enter a SKU ID first.")
      return

    try:
      qr_img = anvil.server.call('get_qr_code', sku_id)
      self.image_qr_preview.source = qr_img
      alert("✅ Unique QR code generated!")
    except Exception as e:
      alert(f"⚠️ QR generation failed: {e}")

  def button_export_pdf(self, **event_args):
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
