from ._anvil_designer import bingheng_Style_SKUTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# Warning code does not function according to how its supposed to work

TABLE = app_tables.material_sku__main_

class bingheng_Style_SKU(bingheng_Style_SKUTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self._pending_file = None
    try:
      self.load_data()
    except Exception:
      pass

  # -----------------------
  # Helpers to safely access Designer controls by name
  # -----------------------
  def _get_text(self, ctrl_name):
    """Return trimmed .text of control if it exists, else empty string."""
    ctrl = getattr(self, ctrl_name, None)
    if ctrl is None:
      return ""
    try:
      return (ctrl.text or "").strip()
    except Exception:
      return ""

  def _set_text(self, ctrl_name, value):
    """Set .text on a control if present; no-op if missing."""
    ctrl = getattr(self, ctrl_name, None)
    if ctrl is None:
      return
    try:
      ctrl.text = value
    except Exception:
      pass

  # -----------------------
  # Data loading
  # -----------------------
  def load_data(self):
    """Load SKU list from server and put into repeating panel as plain dicts."""
    try:
      rows = anvil.server.call('get_skus')   # returns list of dicts (no LiveObjectProxy)
      # Quick sanity check: ensure rows is a list of dict-like objects
      if not isinstance(rows, (list, tuple)):
        alert(f"Failed to load SKU data: unexpected response type: {type(rows)}")
        try:
          self.repeating_panel_1.items = []
        except Exception:
          pass
        return

      # Optionally log rows that contain conversion errors
      problems = [r for r in rows if isinstance(r, dict) and r.get("_error")]
      if problems:
        print("get_skus returned rows with conversion issues:", problems)

      # assign to repeating panel
      try:
        self.repeating_panel_1.items = rows
      except Exception:
        # if repeating_panel missing, just print
        print("No repeating_panel_1 found or could not assign items.")

    except Exception as e:
      # show full exception (repr) so we can see the real cause instead of the one-word 'get'
      alert(f"Failed to load SKU data: {repr(e)}")
      try:
        self.repeating_panel_1.items = []
      except Exception:
        pass

  def refresh_data(self):
    self.load_data()

  # -----------------------
  # Add/create
  # -----------------------
  def btn_add(self, **event_args):
    """Create a new blank row in the DB (quick create)"""
    try:
      # call server to add an intentionally blank row — server may validate and reject empty sku_id
      anvil.server.call('add_sku', "", None, None, None, None, None, None, None)
      self.load_data()
      Notification("Create attempted.", style="info").show()
    except Exception as e:
      alert(f"❌ Could not add new SKU: {e}")

  def btn_add_alt(self, **event_args):
    """Collect inputs and call server add_sku (the form 'Add' functionality)."""
    # changed to use the actual textbox names you provided
    sku_id = self._get_text("text_box_id")
    if not sku_id:
      alert("SKU ID is required")
      return

    # Specifying where each textbox is supposed to get their reference from
    ref_id = self._get_text("text_box_ref") or None
    master_material = self._get_text("text_box_master") or None
    color = self._get_text("text_box_color") or None
    size = self._get_text("text_box_size") or None

    price = None
    ptxt = self._get_text("text_box_override")
    if ptxt:
      try:
        price = float(ptxt)
      except Exception:
        alert("Price must be a number")
        return

    attachment = getattr(self, "_pending_file", None)

    try:
      res = anvil.server.call('add_sku', sku_id, ref_id, master_material, color, size, None, price, attachment)
      if isinstance(res, dict) and res.get("ok"):
        Notification("Added SKU", style="success").show()
        # clear inputs safely (use your actual control names)
        self._set_text("text_box_id", "")
        self._set_text("text_box_ref", "")
        self._set_text("text_box_master", "")
        self._set_text("text_box_color", "")
        self._set_text("text_box_size", "")
        self._set_text("text_box_override", "")
        self._pending_file = None
        self.load_data()
      else:
        alert("Server did not confirm add.")
    except Exception as e:
      alert(f"Could not add SKU: {e}")

  # -----------------------
  # File loader
  # -----------------------
  def file_loader_1_change(self, file, **event_args):
    """Store the selected file to send with add_sku."""
    self._pending_file = file

  # keep compatibility with older handler name (if designer wires file_loader_1)
  def file_loader_1(self, file, **event_args):
    self.file_loader_1_change(file, **event_args)

  # -----------------------
  # QR generation (client) -> calls server get_qr_code
  # -----------------------
  def get_qr_code(self, **event_args):
    """Generate / fetch a QR code for the SKU using multiple fields."""
    sku_id = self._get_text("text_box_id")
    if not sku_id:
      alert("Please enter a SKU ID first.")
      return

    # collect optional fields (use actual textbox names)
    ref_id = self._get_text("text_box_ref")
    master_material = self._get_text("text_box_master")
    color = self._get_text("text_box_color")
    size = self._get_text("text_box_size")

    sku_cost_override = None
    txt = self._get_text("text_box_override")
    if txt != "":
      try:
        sku_cost_override = float(txt)
      except Exception:
        sku_cost_override = txt  # keep raw text if not parseable as float

    try:
      qr_img = anvil.server.call('get_qr_code', sku_id, ref_id, master_material, color, size, sku_cost_override)
      # set image preview only if control exists
      img_ctrl = getattr(self, "image_qr_preview", None)
      if img_ctrl is not None:
        try:
          img_ctrl.source = qr_img
        except Exception:
          pass
      Notification("QR code generated.", style="success").show()
    except Exception as e:
      alert(f"QR generation failed: {e}")

  # -----------------------
  # Export to PDF
  # -----------------------
  def button_export_pdf(self, **event_args):
    """Manual export to PDF with QR codes using visible items."""
    try:
      items = getattr(self, "repeating_panel_1", None)
      if items is None:
        alert("No repeating panel found to export.")
        return
      items = self.repeating_panel_1.items or []
      if not items:
        alert("No SKU data available to export.")
        return

      payload = []
      for it in items:
        payload.append({
          "sku_id": it.get("sku_id") or it.get("id"),
          "material": it.get("master_material"),
          "price": it.get("price"),
        })

      pdf = anvil.server.call('generate_sku_pdf', payload)
      if pdf:
        download(pdf)
        Notification("PDF downloaded", style="success").show()
      else:
        alert("Server did not return PDF")
    except Exception as e:
      alert(f"Error exporting PDF: {e}")

  # -----------------------
  # Repeating panel / item events
  # -----------------------
  def repeating_panel_1_item_template_create(self, item, **event_args):
    # item is the item-template instance (Form)
    try:
      item.set_event_handler('x-save', lambda **e: self._on_item_save(item))
      item.set_event_handler('x-delete', lambda **e: self._on_item_delete(item))
    except Exception:
      pass

  def _on_item_save(self, item_template):
    """Persist an item-template's edited dict back to the DB via server update_sku."""
    try:
      item = item_template.item  # plain dict from server.get_skus
      if not item:
        alert("No item data to save.")
        return
      row_id = item.get("row_id")
      updates = {
        "sku_id": item.get("sku_id") or item.get("id"),
        "id": item.get("id"),
        "ref_id": item.get("ref_id"),
        "master_material": item.get("master_material"),
        "color": item.get("color"),
        "size": item.get("size"),
        "qr_data": item.get("qr_data"),
        "price": item.get("price"),
      }
      anvil.server.call('update_sku', row_id, updates)
      Notification("Saved.", style="success").show()
      self.load_data()
    except Exception as e:
      alert(f"Save failed: {e}")

  def _on_item_delete(self, item_template):
    try:
      item = item_template.item
      if not item:
        return
      row_id = item.get("row_id")
      if not confirm("Delete this SKU?"):
        return
      anvil.server.call('delete_sku', row_id)
      Notification("Deleted", style="warning").show()
      self.load_data()
    except Exception as e:
      alert(f"Delete failed: {e}")


