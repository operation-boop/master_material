from ._anvil_designer import Style_SKU_SheetTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

################## TEST RUN ########################

# class Style_SKU_Sheet(Style_SKU_SheetTemplate):
#   def __init__(self, row=None, **properties):
#     # Set Form properties and Data Bindings.
#     # Accept an optional Data Table row (app_tables.sku_table.get_by_id(...) or similar)
#     self.init_components(**properties)
#     self._row = row   # keep reference to the row (None if creating new)

#     # If you want to do initial UI population immediately:
#     if self._row is not None:
#       self._populate_from_row()
  
  # def form_show(self, **event_args):
  #   """Called when the form is shown. (Also safe place to refresh dynamic UI)"""
  #   # If you didn't populate in __init__, do it here
  #   if self._row is not None:
  #     self._populate_from_row()
  #   else:
  #     # Clear fields for new entry
  #     self.text_box_sku_id.text = ""
  #     self.text_box_material.text = ""
  #     self.text_box_price.text = ""
  #     # If you have an Image control to show attachment preview:
  #     if hasattr(self, "image_attachment_preview"):
  #       self.image_attachment_preview.source = None

  # # -------------------------
  # # Populate UI from row
  # # -------------------------
  # def _populate_from_row(self):
  #   """Copy values from self._row into UI controls"""
  #   try:
  #     r = self._row
  #     # Example control names — change to match your Designer names
  #     self.text_box_sku_id.text = r.get("sku_id", "") if r else ""
  #     self.text_box_material.text = r.get("material", "") if r else ""
  #     # convert number to string for text box
  #     self.text_box_price.text = "" if r is None else str(r.get("price", ""))
  #     # If you store a Media in column 'attachment', show preview link or image
  #     if hasattr(self, "image_attachment_preview"):
  #       media = r.get("attachment") if r else None
  #       self.image_attachment_preview.source = media if media else None

  #   except Exception as e:
  #     alert(f"❌ Could not populate fields: {e}")

  # # -------------------------
  # # Save handler
  # # -------------------------
  # def button_save(self, **event_args):
  #   """Save the values back to the Data Table (update existing row or add new)."""
  #   try:
  #     sku_id = (self.text_box_sku_id.text or "").strip()
  #     material = (self.text_box_material.text or "").strip()
  #     price_text = (self.text_box_price.text or "").strip()

  #     # simple validation
  #     if not sku_id:
  #       alert("SKU ID required.")
  #       return
  #     if not material:
  #       alert("Material required.")
  #       return
  #     try:
  #       price_val = float(price_text) if price_text != "" else None
  #     except Exception:
  #       alert("Price must be a number.")
  #       return

  #     # Prepare row data
  #     row_data = dict(
  #       sku_id = sku_id,
  #       material = material,
  #       price = price_val
  #     )

  #     # If you have a FileLoader on the form (file_loader_attachment) and a selected file,
  #     # you can include it. FileLoader keeps the last selected file as `file_loader_attachment.file`
  #     if hasattr(self, "file_loader_attachment"):
  #       picked = getattr(self.file_loader_attachment, "file", None)
  #       if picked is not None:
  #         row_data["attachment"] = picked

  #     # Update existing row
  #     if self._row is not None:
  #       try:
  #         self._row.update(**row_data)
  #         alert("✅ SKU updated.")
  #       except Exception as e:
  #         # If update permissions fail client-side, call a server function to update instead
  #         # (you can create a server callable like update_sku(row_id, **row_data))
  #         alert(f"❌ Update failed: {e}")
  #         return
  #     else:
  #       # Create new row
  #       try:
  #         new_row = app_tables.sku_table.add_row(**row_data)
  #         self._row = new_row
  #         alert("✅ SKU created.")
  #       except Exception as e:
  #         alert(f"❌ Create failed: {e}")
  #         return

  #     # Optionally close the sheet and tell parent to refresh (if parent passed itself)
  #     # If the sheet was opened with open_form(..., parent=parent_form), you can call parent.refresh_data()
  #     self.raise_event("x-close")   # if you use event-based closing; else call close() or open_form as needed
  #     # Or simply close the form if it's a dialog/sheet:
  #     try:
  #       self.close()   # works for native Anvil forms shown as a dialog
  #     except Exception:
  #       pass

  #   except Exception as e:
  #     alert(f"❌ Save failed: {e}")

  # # -------------------------
  # # Cancel / close handler
  # # -------------------------
  # def button_cancel_click(self, **event_args):
  #   """Close the sheet without saving"""
  #   try:
  #     self.close()
  #   except Exception:
  #     pass

  ###################### TEST RUN 2 #########################
class Style_SKU_Sheet(Style_SKU_SheetTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    # Called when a new item is assigned to the template by the RepeatingPanel.
    self._refresh_ui()


  def _refresh_ui(self):
    item = getattr(self, "item", None)
    if not item:
      return
    # If designer bindings already show the values, you may not need to set them here,
    # but setting them ensures textboxes are in sync for non-binding setups.
    try:
      self.text_box_sku_id.text = item.get("sku_id") or item.get("id") or ""
      if hasattr(self, "text_box_ref_id"):
        self.text_box_ref_id.text = item.get("ref_id") or ""
      if hasattr(self, "text_box_master"):
        # if master_material is a linked row, you might want to display a friendly string
        mm = item.get("master_material")
        self.text_box_master_material.text = getattr(mm, "get", lambda k, d=None: "")("name", str(mm)) if mm else str(mm or "")
      if hasattr(self, "text_box_color"):
        self.text_box_color.text = item.get("color") or ""
      if hasattr(self, "text_box_size"):
        self.text_box_size.text = item.get("size") or ""
      if hasattr(self, "text_box_qr"):
        self.text_box_qr.text = item.get("qr_data") or ""
      if hasattr(self, "text_box_override"):
        self.text_box_override.text = str(item.get("m") or "")
    except Exception:
      pass

  def btn_save_click(self, **event_args):
    """Raise event 'x-save' back to the parent form (main form will handle server update)."""
    # Ensure item contains the latest edited values. If you used data-bind write-back, this is automatic.
    # Otherwise copy values from textboxes into the item dict before raising event:
    try:
      item = self.item or {}
      item["sku_id"] = (self.text_box_sku_id.text or "").strip()
      if hasattr(self, "text_box_ref_id"):
        item["ref_id"] = (self.text_box_ref_id.text or "").strip()
      if hasattr(self, "text_box_master_material"):
        item["master_material"] = (self.text_box_master_material.text or "").strip()
      if hasattr(self, "text_box_color"):
        item["color"] = (self.text_box_color.text or "").strip()
      if hasattr(self, "text_box_size"):
        item["size"] = (self.text_box_size.text or "").strip()
      if hasattr(self, "text_box_qr"):
        item["qr_data"] = (self.text_box_qr.text or "").strip()
      if hasattr(self, "text_box_price"):
        try:
          ptxt = (self.text_box_price.text or "").strip()
          item["price"] = float(ptxt) if ptxt else None
        except:
          alert("Price must be a number"); return
      # push changed item back to repeating panel's list
      # (the repeating panel already contains references to the same item dict)
      self.raise_event('x-save')
    except Exception as e:
      alert(f"Could not prepare save: {e}")

  def btn_delete_click(self, **event_args):
    """Raise event 'x-delete' — parent will handle confirmation/server delete."""
    self.raise_event('x-delete')
