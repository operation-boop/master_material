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
#           "override": r.get("override", 0),
#           "attachment_name": getattr(attachment, "name", "") if attachment else "",
#           "override_display": f"{r.get('override', 0):,.2f}"
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
#       override_text = (self.text_box_override.text or "").strip()

#       if not sku_id or not material or not override_text:
#         alert("Fields missing — please fill SKU ID, Material and override before selecting a file.")
#         return

#       try:
#         override = float(override_text)
#       except Exception:
#         alert("Override must be a valid number.")
#         return

#       # Optional confirm
#       proceed = confirm(f"Upload file '{getattr(file, 'name', 'file')}' for SKU '{sku_id}'?")
#       if not proceed:
#         return

#       # Call server and pass the Media object
#       res = anvil.server.call('add_sku', sku_id, material, override, file)

#       if isinstance(res, dict) and res.get("ok"):
#         alert(f"✅ SKU {sku_id} with attachment uploaded.")
#         # refresh and clear inputs
#         self.load_data()
#         self.text_box_sku_id.text = ""
#         self.text_box_material.text = ""
#         self.text_box_override.text = ""
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


# class bingheng_Style_SKU(bingheng_Style_SKUTemplate):
#   def __init__(self, **properties):
#     # Set Form properties and Data Bindings.
#     self.init_components(**properties)

#     # Load rows into the repeating panel
#     self.load_data()

# ---------- corrected syntax only (indentation / try/except / method placement fixes) ----------

############################################
# Load data from the database and map to repeating panel items
############################################

class bingheng_Style_SKU(bingheng_Style_SKUTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    # optional: wire repeating panel item creation hook
    # self.repeating_panel_1.item_template = None  # keep designer-set template
    try:
      self.load_data()
    except Exception:
      # ignore init-time load errors here
      pass

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
          # example numeric/override field (if you have it)
          "override": r.get("override", 0),
          # friendly display strings for template if needed
          "override_display": f"{r.get('override', 0):,.2f}" if r.get("override") is not None else "",
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
  # def btn_refresh(self, **event_args):
  #   """Refresh data from DB into the repeating panel."""
  #   self.load_data()

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
      override_text = (self.text_box_override.text or "").strip()

      if not sku_id or not material or not override_text:
        alert("Fields missing — please fill SKU ID, Material and override before selecting a file.")
        return

      try:
        override = float(override_text)
      except Exception:
        alert("override must be a valid number.")
        return

      proceed = confirm(f"Upload file '{getattr(file, 'name', 'file')}' for SKU '{sku_id}'?")
      if not proceed:
        return

      # Example server function to handle adding row + storing file in Data Tables or Blobstore
      # You must implement this server function named 'add_sku' to accept (sku_id, material, override, file)
      res = anvil.server.call('add_sku', sku_id, material, override, file)

      if isinstance(res, dict) and res.get("ok"):
        alert(f"✅ SKU {sku_id} with attachment uploaded.")
        # refresh and clear inputs
        self.load_data()
        self.text_box_sku_id.text = ""
        self.text_box_material.text = ""
        self.text_box_override.text = ""
      else:
        # If server returns something else, still reload so user sees the latest state
        alert("✅ SKU add request completed (server returned unexpected response).")
        self.load_data()

    except Exception as e:
      alert(f"❌ Error uploading file / adding SKU: {e}")

def get_qr_code(self, **event_args):
  """Generate / fetch a QR code for the SKU using multiple fields."""
  sku_id = (self.text_box_sku_id.text or "").strip()
  if not sku_id:
    alert("Please enter a SKU ID first.")
    return

  # Collect additional fields (use getattr in case some controls are missing)
  ref_id = (getattr(self, "text_box_ref_id", None) and (self.text_box_ref_id.text or "").strip()) or ""
  master_material = (getattr(self, "text_box_master_material", None) and (self.text_box_master_material.text or "").strip()) or ""
  color = (getattr(self, "text_box_color", None) and (self.text_box_color.text or "").strip()) or ""
  size = (getattr(self, "text_box_size", None) and (self.text_box_size.text or "").strip()) or ""
  # For cost/override, accept numeric or text
  sku_cost_override = None
  if getattr(self, "text_box_override", None):
    txt = (self.text_box_override.text or "").strip()
    try:
      sku_cost_override = float(txt) if txt != "" else None
    except Exception:
      # keep as raw text if not parseable
      sku_cost_override = txt

  try:
    # Call the new server function with all fields
    qr_img = anvil.server.call('get_qr_code_payload', sku_id, ref_id, master_material, color, size, sku_cost_override)
    self.image_qr_preview.source = qr_img
    alert("✅ QR code generated.")
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

  # --------------------------END---------------------------------------------
  # --------------------------------------------------------------------------
  #             TEST
  # --------------------------------------------------------------------------

  # The following methods were present in the original; kept but adjusted indentation
  # to be valid inside the same class.

  def load_data_from_server(self):
    """Load SKU list from server and put into repeating panel."""
    try:
      rows = anvil.server.call('get_skus')
      # rows is a list of dicts; each dict includes row_id and fields for display
      self.repeating_panel_1.items = rows
    except Exception as e:
      alert(f"Failed to load SKU data: {e}")
      self.repeating_panel_1.items = []

  def btn_refresh(self, **event_args):
    self.load_data_from_server()

  def btn_add_alt(self, **event_args):
    """Collect inputs and call server add_sku"""
    sku_id = (self.text_box_sku_id.text or "").strip()
    ref_id = (getattr(self, "text_box_ref_id", None) and (self.text_box_ref_id.text or "").strip()) or None
    master_material = (getattr(self, "text_box_material", None) and (self.text_box_material.text or "").strip()) or None
    color = (getattr(self, "text_box_color", None) and (self.text_box_color.text or "").strip()) or None
    size = (getattr(self, "text_box_size", None) and (self.text_box_size.text or "").strip()) or None
    override = None
    try:
      ptxt = getattr(self, "text_box_override", None) and (self.text_box_override.text or "").strip()
      override = float(ptxt) if ptxt else None
    except Exception:
      alert("override must be a number")
      return

    if not sku_id:
      alert("SKU ID is required")
      return

    # optional attachment: if file_loader stores a chosen file on the form (e.g. self._pending_file)
    attachment = getattr(self, "_pending_file", None)

    try:
      res = anvil.server.call('add_sku', sku_id, ref_id, master_material, color, size, None, override, attachment)
      if isinstance(res, dict) and res.get("ok"):
        Notification("Added SKU", style="success").show()
        # clear inputs
        self.text_box_sku_id.text = ""
        if hasattr(self, "text_box_ref_id"):
          self.text_box_ref_id.text = ""
        if hasattr(self, "text_box_master"):
          self.text_box_master.text = ""
        if hasattr(self, "text_box_color"):
          self.text_box_color.text = ""
        if hasattr(self, "text_box_size"):
          self.text_box_size.text = ""
        if hasattr(self, "text_box_override"):
          self.text_box_override.text = ""
        self._pending_file = None
        self.load_data()
      else:
        alert("Server did not confirm add.")
    except Exception as e:
      alert(f"Could not add SKU: {e}")

  def file_loader_1_change(self, file, **event_args):
    """FileLoader change event: store chosen file until Add is clicked"""
    # file is anvil.media.Media (or None)
    self._pending_file = file

  def button_export_pdf_alt(self, **event_args):
    """Send visible items to server to create a PDF"""
    try:
      items = self.repeating_panel_1.items or []
      if not items:
        alert("No items to export")
        return

      # map visible items to simple dicts expected by server PDF generator
      payload = []
      for it in items:
        payload.append({
          "sku_id": it.get("sku_id") or it.get("id"),
          "material": it.get("master_material"),
          "override": it.get("override"),
        })

      pdf = anvil.server.call('generate_sku_pdf', payload)
      if pdf:
        download(pdf)
        Notification("PDF downloaded", style="success").show()
      else:
        alert("Server did not return PDF")
    except Exception as e:
      alert(f"Error exporting PDF: {e}")

  # When an item template is created, we attach handlers so user actions inside the item template
  # (save/delete) can call main form methods. Name must match the designer hook:
  def repeating_panel_1_item_template_create(self, item, **event_args):
    # item is the item-template instance (Form) for a row
    try:
      # listen for custom events raised from the item template
      item.set_event_handler('x-save', lambda **e: self._on_item_save(item))
      item.set_event_handler('x-delete', lambda **e: self._on_item_delete(item))
    except Exception:
      pass

  def _on_item_save(self, item_template):
    """Called when an item-template wants to save. The template should expose its 'item' dict."""
    try:
      item = item_template.item  # this is the dict shown in the repeating panel
      row_id = item.get("row_id")
      updates = {
        "sku_id": item.get("sku_id") or item.get("id"),
        "id": item.get("id"),
        "ref_id": item.get("ref_id"),
        "master_material": item.get("master_material"),
        "color": item.get("color"),
        "size": item.get("size"),
        "qr_data": item.get("qr_data"),
        "override": item.get("override"),
      }
      anvil.server.call('update_sku', row_id, updates)
      Notification("Saved.", style="success").show()
      self.load_data()
    except Exception as e:
      alert(f"Save failed: {e}")

  def _on_item_delete(self, item_template):
    try:
      item = item_template.item
      row_id = item.get("row_id")
      if not confirm("Delete this SKU?"):
        return
      anvil.server.call('delete_sku', row_id)
      Notification("Deleted", style="warning").show()
      self.load_data()
    except Exception as e:
      alert(f"Delete failed: {e}")

