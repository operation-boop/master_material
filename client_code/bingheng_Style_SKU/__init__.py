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

#     # Load rows into the repeating panel
#     self.load_data()

#   ############################################
#   # Load data from the database
#   ############################################
#   def load_items(self):
#     rows = list(app_tables.material_sku__main_
#       .search())
#     self.repeating_panel_1.items = rows

#   def btn_refresh(self, **event_args):
#     app_tables.material_sku__main_ = bingheng_Style_SKUTemplate.add_row(
#       id="", ref_id="", master_material="", color="", size="",qr_data="", sku_override=""
#     )
#   self.load_items()
  
#   def load_data(self):
#     """Load SKU data from your database table and bind to repeating_panel_1.

#     Each item is a dict and contains the original Row under key '_row' so
#     the item-template can perform row-level operations if needed.
#     """
#     try:
#       if not hasattr(app_tables, "sku_table"):
#         self.repeating_panel_1.items = []
#         alert("⚠️ Table 'sku_table' not found — please create it in Data Tables.")
#         return

#       rows = list(app_tables.sku_table.search())  # fetch rows
#       items = []
#       for r in rows:
#         attachment = r.get("attachment")
#         items.append({
#           "_row": r,
#           "sku_id": r.get("sku_id", ""),
#           "material": r.get("material", ""),
#           "price": r.get("price", 0),
#           "attachment_name": getattr(attachment, "name", "") if attachment else "",
#           "price_display": f"{r.get('price', 0):,.2f}"
#         })

#       self.repeating_panel_1.items = items

#     except Exception as e:
#       alert(f"❌ Failed to load SKU data: {e}")
#       self.repeating_panel_1.items = []

#   def refresh_data(self):
#     """Helper to reload the repeating panel after add/edit/delete."""
#     self.load_data()

#   def file_loader_1(self, file, **event_args):
#     """Called after user selects a file. `file` is an anvil.media.Media or None."""
#     try:
#       # If user cancelled the picker, file will be None
#       if file is None:
#         return

#       sku_id = (self.text_box_sku_id.text or "").strip()
#       material = (self.text_box_material.text or "").strip()
#       price_text = (self.text_box_price.text or "").strip()

#       if not sku_id or not material or not price_text:
#         alert("Fields missing — please fill SKU ID, Material and Price before selecting a file.")
#         return

#       try:
#         price = float(price_text)
#       except Exception:
#         alert("Price must be a valid number.")
#         return

#       # Optional confirm
#       proceed = confirm(f"Upload file '{getattr(file, 'name', 'file')}' for SKU '{sku_id}'?")
#       if not proceed:
#         return

#       # Call server and pass the Media object
#       res = anvil.server.call('add_sku', sku_id, material, price, file)

#       if isinstance(res, dict) and res.get("ok"):
#         alert(f"✅ SKU {sku_id} with attachment uploaded.")
#         # refresh and clear inputs
#         self.load_data()
#         self.text_box_sku_id.text = ""
#         self.text_box_material.text = ""
#         self.text_box_price.text = ""
#       else:
#         alert("✅ SKU added (server response unexpected).")
#         self.load_data()

#     except Exception as e:
#       alert(f"❌ Error uploading file / adding SKU: {e}")

#       ############################################
#       # Edit / QR / Export handlers (kept from your original code)
#       ############################################
#       def edit_button(self, **event_args):
#         """Called when edit button is clicked — open the sheet"""
#         try:
#           open_form('bingheng_Style_SKU.Style_SKU_sheet')
#         except Exception as e:
#           alert(f"❌ Could not open edit sheet: {e}")

#       def get_qr_code(self, **event_args):
#         sku_id = (self.text_box_sku_id.text or "").strip()
#         if not sku_id:
#           alert("Please enter a SKU ID first.")
#           return

#         try:
#           qr_img = anvil.server.call('get_qr_code', sku_id)
#           self.image_qr_preview.source = qr_img
#           alert("✅ Unique QR code generated!")
#         except Exception as e:
#           alert(f"⚠️ QR generation failed: {e}")

#       def button_export_pdf(self, **event_args):
#         """Manual export to PDF with QR codes"""
#         try:
#           data = self.repeating_panel_1.items or []
#           if not data:
#             alert("No SKU data available to export.")
#             return

#           pdf_file = anvil.server.call('generate_sku_pdf', data)
#           download(pdf_file)
#           alert("✅ PDF exported successfully!")

#         except Exception as e:
#           alert(f"❌ Error exporting PDF: {e}")


#-----------------------------------------------------
#                 MOCK GENERATED QR TEST
#------------------------------------------------------
TABLE = app_tables.material_sku__main_


class bingheng_Style_SKU(bingheng_Style_SKUTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Load rows into the repeating panel
    self.load_data()

  ############################################
  # Load data from the database and map to repeating panel items
  ############################################
  def load_data(self):
    """Load SKU data from your database table and bind to repeating_panel_1.

    Each item is a dict containing the original Row under key '_row' so
    the item-template can perform row-level operations if needed.
    """
    try:
      rows = list(TABLE.search())  # fetch rows from the DB table
      items = []
      for r in rows:
        # Map the columns you care about into an item dict
        # Adjust field names if your table uses different column names
        items.append({
          "_row": r,
          "id": r.get("id", ""),                # SKU id
          "ref_id": r.get("ref_id", ""),
          "master_material": r.get("master_material"),
          "color": r.get("color"),
          "size": r.get("size"),
          "qr_data": r.get("qr_data", ""),
          # example numeric/price field (if you have it)
          "price": r.get("price", 0),
          # friendly display strings for template if needed
          "price_display": f"{r.get('price', 0):,.2f}" if r.get("price") is not None else "",
        })

      # assign to repeating panel. The item template will receive `self.item`
      self.repeating_panel_1.items = items

    except Exception as e:
      alert(f"❌ Failed to load SKU data: {e}")
      self.repeating_panel_1.items = []

  def refresh_data(self):
    """Convenience wrapper to reload the repeating panel."""
    self.load_data()

  ############################################
  # UI event handlers
  ############################################
  def btn_refresh(self, **event_args):
    """Refresh data from DB into the repeating panel."""
    self.load_data()

  def btn_add(self, **event_args):
    """Create a new blank row in the DB and reload to show it in the list."""
    try:
      # create a new (blank) row in the DB table
      TABLE.add_row(
        id="",
        ref_id="",
        master_material="",
        color="",
        size="",
        qr_data="",
        sku_override=""
      )
      # reload the UI
      self.load_data()
      Notification("New SKU created.", style="success").show()
    except Exception as e:
      alert(f"❌ Could not add new SKU: {e}")

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

      proceed = confirm(f"Upload file '{getattr(file, 'name', 'file')}' for SKU '{sku_id}'?")
      if not proceed:
        return

      # Example server function to handle adding row + storing file in Data Tables or Blobstore
      # You must implement this server function named 'add_sku' to accept (sku_id, material, price, file)
      res = anvil.server.call('add_sku', sku_id, material, price, file)

      if isinstance(res, dict) and res.get("ok"):
        alert(f"✅ SKU {sku_id} with attachment uploaded.")
        # refresh and clear inputs
        self.load_data()
        self.text_box_sku_id.text = ""
        self.text_box_material.text = ""
        self.text_box_price.text = ""
      else:
        # If server returns something else, still reload so user sees the latest state
        alert("✅ SKU add request completed (server returned unexpected response).")
        self.load_data()

    except Exception as e:
      alert(f"❌ Error uploading file / adding SKU: {e}")

  def edit_button(self, **event_args):
    """Called when edit button is clicked — open the edit sheet/form."""
    try:
      # This assumes you created a Form named "Style_SKU_sheet" under a package bingheng_Style_SKU
      open_form('bingheng_Style_SKU.Style_SKU_sheet')
    except Exception as e:
      alert(f"❌ Could not open edit sheet: {e}")

  def get_qr_code(self, **event_args):
    """Generate / fetch a QR code for the SKU currently in the SKU input box."""
    sku_id = (self.text_box_sku_id.text or "").strip()
    if not sku_id:
      alert("Please enter a SKU ID first.")
      return

    try:
      # server must implement 'get_qr_code' that returns anvil.media.Media (image)
      qr_img = anvil.server.call('get_qr_code', sku_id)
      self.image_qr_preview.source = qr_img
      alert("✅ Unique QR code generated!")
    except Exception as e:
      alert(f"⚠️ QR generation failed: {e}")

  def button_export_pdf(self, **event_args):
    """Manual export to PDF with QR codes."""
    try:
      # Pass the data from the repeating panel to the server to render as PDF.
      # We pass the underlying DB rows for precise data—map items -> rows
      data_items = self.repeating_panel_1.items or []
      if not data_items:
        alert("No SKU data available to export.")
        return

      # send only necessary data (or the rows' IDs) to server
      # e.g. send list of row.get_id() or the small dict of values
      export_payload = []
      for it in data_items:
        r = it.get("_row")
        if r:
          export_payload.append({
            "id": r.get("id"),
            "ref_id": r.get("ref_id"),
            "qr_data": r.get("qr_data"),
            # add other fields as needed
          })

      pdf_file = anvil.server.call('generate_sku_pdf', export_payload)
      if pdf_file:
        download(pdf_file)
        alert("✅ PDF exported successfully!")
      else:
        alert("❌ Server did not return a PDF file.")

    except Exception as e:
      alert(f"❌ Error exporting PDF: {e}")
#--------------------------END---------------------------------------------