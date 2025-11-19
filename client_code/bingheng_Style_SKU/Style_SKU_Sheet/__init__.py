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
    self.init_components(**properties)
    self._refresh_ui()

  def _refresh_ui(self):
    item = getattr(self, "item", None)
    if not item:
      return

    try:
      # item is a plain dict provided by server.get_skus()
      self.text_box_sku_id.text = item.get("sku_id") or item.get("id") or ""
      if hasattr(self, "text_box_ref"):
        self.text_box_ref_id.text = item.get("ref_id") or ""
      if hasattr(self, "text_box_master_material"):
        # from server we map master_material to a string already
        self.text_box_master_material.text = str(item.get("master_material") or "")
      if hasattr(self, "text_box_color"):
        self.text_box_color.text = item.get("color") or ""
      if hasattr(self, "text_box_size"):
        self.text_box_size.text = item.get("size") or ""
      if hasattr(self, "text_box_qr"):
        self.text_box_qr.text = item.get("qr_data") or ""
      if hasattr(self, "text_box_override"):
        # server returns sku_cost_override as value; stringify safely
        self.text_box_override.text = str(item.get("sku_cost_override") or "")
    except Exception as e:
      print("Style_SKU_Sheet._refresh_ui error:", e)

  def btn_save(self, **event_args):
    """Gather edited fields into the item dict and notify parent to save."""
    try:
      item = self.item or {}
      item["sku_id"] = (self.text_box_sku_id.text or "").strip()
      if hasattr(self, "text_box_ref"):
        item["ref_id"] = (self.text_box_ref_id.text or "").strip()
      if hasattr(self, "text_box_master_material"):
        item["master_material"] = (self.text_box_master_material.text or "").strip()
      if hasattr(self, "text_box_color"):
        item["color"] = (self.text_box_color.text or "").strip()
      if hasattr(self, "text_box_size"):
        item["size"] = (self.text_box_size.text or "").strip()
      if hasattr(self, "text_box_qr"):
        item["qr_data"] = (self.text_box_qr.text or "").strip()
      if hasattr(self, "text_box_override"):
        try:
          ptxt = (self.text_box_price.text or "").strip()
          item["price"] = float(ptxt) if ptxt else None
        except Exception:
          alert("Price must be a number")
          return
      # Tell parent to persist (parent handles update_sku)
      self.raise_event('x-save')
    except Exception as e:
      alert(f"Could not prepare save: {e}")

  def btn_delete(self, **event_args):
    """Notify parent to delete this item."""
    self.raise_event('x-delete')
