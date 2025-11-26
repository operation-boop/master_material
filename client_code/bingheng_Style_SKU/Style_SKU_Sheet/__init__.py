from ._anvil_designer import Style_SKU_SheetTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Style_SKU_Sheet(Style_SKU_SheetTemplate):
  def __init__(self, **properties):
    # initialize designer components
    self.init_components(**properties)
    # refresh UI from current `self.item` (set by parent repeating panel)
    self._refresh_ui()

  def _coerce_item(self, item_raw):
    """Return a plain dict `item` regardless of how the repeating panel supplied it.
       Accepts:
         - dict
         - (key, dict) tuple or list (e.g. (index, row))
         - LiveObjectProxy-like objects where dict() works
    """
    if item_raw is None:
      return {}
    # tuple/list shape: (key, value)
    if isinstance(item_raw, (list, tuple)) and len(item_raw) >= 2:
      candidate = item_raw[1]
      if isinstance(candidate, dict):
        return candidate
      try:
        return dict(candidate)
      except Exception:
        return {}
    # dict-ish
    if isinstance(item_raw, dict):
      return item_raw
    # try coercing
    try:
      return dict(item_raw)
    except Exception:
      return {}

  def _refresh_ui(self):
    """Populate text boxes from self.item (robust to many item shapes)."""
    item = self._coerce_item(getattr(self, "item", None))
    if not item:
      # clear fields if no item
      if hasattr(self, "text_box_id"): self.text_box_id.text = ""
      if hasattr(self, "text_box_ref"): self.text_box_ref.text = ""
      if hasattr(self, "text_box_master"): self.text_box_master.text = ""
      if hasattr(self, "text_box_color"): self.text_box_color.text = ""
      if hasattr(self, "text_box_size"): self.text_box_size.text = ""
      if hasattr(self, "text_box_qr"): self.text_box_qr.text = ""
      if hasattr(self, "text_box_override"): self.text_box_override.text = ""
      return

    try:
      if hasattr(self, "text_box_id"):
        self.text_box_id.text = item.get("sku_id") or item.get("id") or ""
      if hasattr(self, "text_box_ref"):
        self.text_box_ref.text = item.get("ref_id") or ""
      if hasattr(self, "text_box_master"):
        self.text_box_master.text = str(item.get("master_material") or "")
      if hasattr(self, "text_box_color"):
        self.text_box_color.text = item.get("color") or ""
      if hasattr(self, "text_box_size"):
        self.text_box_size.text = item.get("size") or ""
      if hasattr(self, "text_box_qr"):
        self.text_box_qr.text = item.get("qr_data") or ""
      if hasattr(self, "text_box_override"):
        ov = item.get("sku_cost_override") if "sku_cost_override" in item else item.get("price")
        self.text_box_override.text = "" if ov is None else str(ov)
    except Exception as e:
      # keep safe — show a console message for debugging
      print("Style_SKU_Sheet._refresh_ui error:", e)

  # If the item-template is reused / its item changes, Anvil will call this hook:
  def form_show(self, **event_args):
    # called when the form is shown; refresh UI to reflect latest `self.item`
    self._refresh_ui()

  # --------------- Save / Delete (raise events so parent main form persists) ---------------
  # Note: we use *_click names (you must wire buttons to these)
  def btn_save_click(self, **event_args):
    """Gather edited values into self.item (a dict) and raise x-save to parent."""
    try:
      item = self.item or {}
      item_dict = self._coerce_item(item)  # get underlying dict (if tuple supplied)
      # copy back values from textboxes to the item dict
      if hasattr(self, "text_box_id"):
        item_dict["sku_id"] = (self.text_box_id.text or "").strip()
      if hasattr(self, "text_box_ref"):
        item_dict["ref_id"] = (self.text_box_ref.text or "").strip()
      if hasattr(self, "text_box_master"):
        item_dict["master_material"] = (self.text_box_master.text or "").strip()
      if hasattr(self, "text_box_color"):
        item_dict["color"] = (self.text_box_color.text or "").strip()
      if hasattr(self, "text_box_size"):
        item_dict["size"] = (self.text_box_size.text or "").strip()
      if hasattr(self, "text_box_qr"):
        item_dict["qr_data"] = (self.text_box_qr.text or "").strip()
      if hasattr(self, "text_box_override"):
        # keep numeric handling flexible
        txt = (self.text_box_override.text or "").strip()
        try:
          item_dict["sku_cost_override"] = float(txt) if txt != "" else None
        except Exception:
          item_dict["sku_cost_override"] = txt

      # Ensure the repeating panel sees the updated dict:
      # if the parent set the repeating panel items as list-of-dicts, changing item_dict updates it.
      # If parent set items as (key, dict) pairs, parent handles saving using row_id etc.
      # Raise event and let parent handle persistence.
      self.raise_event("x-save")
    except Exception as e:
      alert(f"Could not prepare save: {e}")

  def btn_delete_click(self, **event_args):
    """Raise an x-delete event so parent can confirm and delete the row."""
    try:
      self.raise_event("x-delete")
    except Exception as e:
      alert(f"Could not raise delete event: {e}")

  # --------------- File loader (store file locally on sheet) ---------------
  # keep the Anvil naming convention `file_loader_1_change`
  def file_loader_1_change(self, file, **event_args):
    """Called when user chooses a file in this item-template's FileLoader."""
    # store locally so the parent can use when saving, or you can upload immediately
    self._picked_file = file
    # optional: show preview if image control exists:
    try:
      if file and hasattr(self, "image_attachment_preview"):
        self.image_attachment_preview.source = file
    except Exception:
      pass

  # --------------- QR preview (calls server get_qr_code) ---------------
  def get_qr_code_click(self, **event_args):
    """Generate/fetch QR for the values shown in this item-template."""
    try:
      sku_id = (self.text_box_id.text or "").strip() if hasattr(self, "text_box_id") else ""
      if not sku_id:
        alert("Please enter a SKU ID first.")
        return

      ref_id = (self.text_box_ref.text or "").strip() if hasattr(self, "text_box_ref") else ""
      master_material = (self.text_box_master.text or "").strip() if hasattr(self, "text_box_master") else ""
      color = (self.text_box_color.text or "").strip() if hasattr(self, "text_box_color") else ""
      size = (self.text_box_size.text or "").strip() if hasattr(self, "text_box_size") else ""
      sku_cost_override = None
      if hasattr(self, "text_box_override"):
        txt = (self.text_box_override.text or "").strip()
        try:
          sku_cost_override = float(txt) if txt != "" else None
        except Exception:
          sku_cost_override = txt

      qr_img = anvil.server.call('get_qr_code', sku_id, ref_id, master_material, color, size, sku_cost_override)
      # if there's an image control for preview in the item template:
      if hasattr(self, "image_qr_preview"):
        try:
          self.image_qr_preview.source = qr_img
        except Exception:
          pass
      Notification("QR generated", style="success").show()
    except Exception as e:
      alert(f"QR generation failed: {e}")

  # --------------- Export PDF for single item (optional) ---------------
  def button_export_pdf_click(self, **event_args):
    """Ask the server to generate a PDF for this single item (calls same server helper)."""
    try:
      item = self._coerce_item(getattr(self, "item", None))
      payload = [{
        "sku_id": item.get("sku_id") or item.get("id"),
        "material": item.get("master_material"),
        "price": item.get("sku_cost_override") or item.get("price")
      }]
      pdf = anvil.server.call('generate_sku_pdf', payload)
      if pdf:
        download(pdf)
        Notification("PDF downloaded", style="success").show()
      else:
        alert("Server did not return PDF.")
    except Exception as e:
      alert(f"Error exporting PDF: {e}")