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

skutable = app_tables.material_sku__main_

def form_show(self, **event_args):
  self.Style_SKU_Sheet.id.item = self.item["id"]
  self.Style_SKU_Sheet.ref_id.item = self.item["ref_id"]
  self.Style_SKU_Sheet.master_material.item = self.item["master_material"]
  self.Style_SKU_Sheet.color.item = self.item["color"]
  self.Style_SKU_Sheet.size.item = self.item["size"]
  self.Style_SKU_Sheet.qr_data.item = self.item["qr_data"]
  self.Style_SKU_Sheet.sku_override.item = self.item["sku_cost_override"]
  
class Style_SKU_Sheet(Style_SKU_SheetTemplate):
  def __init__(self, row=None, **properties):
    # Set Form properties and Data Bindings.
    # Accept an optional Data Table row (app_tables.sku_table.get_by_id(...) or similar)
    self.init_components(**properties)
    self._row = row   # keep reference to the row (None if creating new)

    # If you want to do initial UI population immediately:
    if self._row is not None:
      self._populate_from_row()

  def form_show(self, **event_args):
    """Called when the form is shown. (Also safe place to refresh dynamic UI)"""
    # If you didn't populate in __init__, do it here
    if self._row is not None:
      self._populate_from_row()
    else:
      # Clear fields for new entry
      self.text_box_sku_id.text = ""
      self.text_box_material.text = ""
      self.text_box_price.text = ""
      # If you have an Image control to show attachment preview:
      if hasattr(self, "image_attachment_preview"):
        self.image_attachment_preview.source = None

  # -------------------------
  # Populate UI from row
  # -------------------------
  def _populate_from_row(self):
    """Copy values from self._row into UI controls"""
    try:
      r = self._row
      # Example control names — change to match your Designer names
      self.text_box_sku_id.text = r.get("sku_id", "") if r else ""
      self.text_box_material.text = r.get("material", "") if r else ""
      # convert number to string for text box
      self.text_box_price.text = "" if r is None else str(r.get("price", ""))
      # If you store a Media in column 'attachment', show preview link or image
      if hasattr(self, "image_attachment_preview"):
        media = r.get("attachment") if r else None
        self.image_attachment_preview.source = media if media else None

    except Exception as e:
      alert(f"❌ Could not populate fields: {e}")

  # -------------------------
  # Save handler
  # -------------------------
  def button_save(self, **event_args):
    """Save the values back to the Data Table (update existing row or add new)."""
    try:
      sku_id = (self.text_box_sku_id.text or "").strip()
      material = (self.text_box_material.text or "").strip()
      price_text = (self.text_box_price.text or "").strip()

      # simple validation
      if not sku_id:
        alert("SKU ID required.")
        return
      if not material:
        alert("Material required.")
        return
      try:
        price_val = float(price_text) if price_text != "" else None
      except Exception:
        alert("Price must be a number.")
        return

      # Prepare row data
      row_data = dict(
        sku_id = sku_id,
        material = material,
        price = price_val
      )

      # If you have a FileLoader on the form (file_loader_attachment) and a selected file,
      # you can include it. FileLoader keeps the last selected file as `file_loader_attachment.file`
      if hasattr(self, "file_loader_attachment"):
        picked = getattr(self.file_loader_attachment, "file", None)
        if picked is not None:
          row_data["attachment"] = picked

      # Update existing row
      if self._row is not None:
        try:
          self._row.update(**row_data)
          alert("✅ SKU updated.")
        except Exception as e:
          # If update permissions fail client-side, call a server function to update instead
          # (you can create a server callable like update_sku(row_id, **row_data))
          alert(f"❌ Update failed: {e}")
          return
      else:
        # Create new row
        try:
          new_row = app_tables.sku_table.add_row(**row_data)
          self._row = new_row
          alert("✅ SKU created.")
        except Exception as e:
          alert(f"❌ Create failed: {e}")
          return

      # Optionally close the sheet and tell parent to refresh (if parent passed itself)
      # If the sheet was opened with open_form(..., parent=parent_form), you can call parent.refresh_data()
      self.raise_event("x-close")   # if you use event-based closing; else call close() or open_form as needed
      # Or simply close the form if it's a dialog/sheet:
      try:
        self.close()   # works for native Anvil forms shown as a dialog
      except Exception:
        pass

    except Exception as e:
      alert(f"❌ Save failed: {e}")

  # -------------------------
  # Cancel / close handler
  # -------------------------
  def button_cancel_click(self, **event_args):
    """Close the sheet without saving"""
    try:
      self.close()
    except Exception:
      pass

  
