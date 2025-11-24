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
    item = self.item or {}
    try:
      self.text_box_id.text = item.get("sku_id") or ""
      self.text_box_ref.text = item.get("ref_id") or ""
      self.text_box_master.text = item.get("master_material") or ""
      self.text_box_color.text = item.get("color") or ""
      self.text_box_size.text = item.get("size") or ""
      self.text_box_qr.text = item.get("qr_data") or ""
      self.text_box_override.text = str(item.get("price") or "")
    except Exception as e:
      print("refresh_ui error:", e)

  # SAVE BUTTON
  def btn_save(self, **event_args):
    item = self.item or {}

    item["sku_id"] = (self.text_box_id.text or "").strip()
    item["ref_id"] = (self.text_box_ref.text or "").strip()
    item["master_material"] = (self.text_box_master.text or "").strip()
    item["color"] = (self.text_box_color.text or "").strip()
    item["size"] = (self.text_box_size.text or "").strip()
    item["qr_data"] = (self.text_box_qr.text or "").strip()

    ptxt = (self.text_box_override.text or "").strip()
    item["price"] = float(ptxt) if ptxt else None

    self.raise_event('x-save')

  # DELETE BUTTON
  def btn_delete(self, **event_args):
    self.raise_event('x-delete')