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
  #     self.text_box_override.text = ""
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
  #     self.text_box_override.text = "" if r is None else str(r.get("override", ""))
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
  #     override_text = (self.text_box_override.text or "").strip()

  #     # simple validation
  #     if not sku_id:
  #       alert("SKU ID required.")
  #       return
  #     if not material:
  #       alert("Material required.")
  #       return
  #     try:
  #       override_val = float(override_text) if override_text != "" else None
  #     except Exception:
  #       alert("override must be a number.")
  #       return

  #     # Prepare row data
  #     row_data = dict(
  #       sku_id = sku_id,
  #       material = material,
  #       override = override_val
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
    self._refresh_ui()

  def _get_val(self, item, key):
    """Safely get a value from either a dict or a LiveObjectProxy / row."""
    if item is None:
      return None
    try:
      if isinstance(item, dict):
        return item.get(key)
    except Exception:
      pass
    try:
      return item[key]
    except Exception:
      pass
    try:
      return getattr(item, key)
    except Exception:
      pass
    return None

  def _set_val(self, item, key, value):
    """Safely set a value into either a dict or a LiveObjectProxy / row-like object."""
    if item is None:
      return
    try:
      if isinstance(item, dict):
        item[key] = value
        return
    except Exception:
      pass
    try:
      item[key] = value
      return
    except Exception:
      pass
    try:
      setattr(item, key, value)
    except Exception:
      pass

  def _refresh_ui(self):
    item = getattr(self, "item", None)
    if not item:
      return

    try:
      # SKU id (try sku_id first, then fallback to id)
      self.text_box_sku_id.text = (self._get_val(item, "sku_id")
                                   or self._get_val(item, "id") or "")

      # ref id
      if hasattr(self, "text_box_ref"):
        self.text_box_ref_id.text = self._get_val(item, "ref_id") or ""

      # master material (linked row or simple value)
      if hasattr(self, "text_box_master"):
        mm = self._get_val(item, "master_material")
        if mm:
          name_val = None
          try:
            name_val = mm["name"]
          except Exception:
            try:
              name_val = getattr(mm, "name")
            except Exception:
              try:
                name_val = str(mm)
              except Exception:
                name_val = ""
          self.text_box_master_material.text = name_val or ""
        else:
          self.text_box_master_material.text = ""

      # color
      if hasattr(self, "text_box_color"):
        self.text_box_color.text = self._get_val(item, "color") or ""

      # size
      if hasattr(self, "text_box_size"):
        self.text_box_size.text = self._get_val(item, "size") or ""

      # qr_data
      if hasattr(self, "text_box_qr"):
        self.text_box_qr.text = self._get_val(item, "qr_data") or ""

      # sku_cost_override / override display
      if hasattr(self, "text_box_override"):
        ov = self._get_val(item, "sku_cost_override")
        try:
          self.text_box_override.text = str(ov) if ov is not None else ""
        except Exception:
          self.text_box_override.text = ""

    except Exception as e:
      # Keep UI safe: print for debugging but don't crash
      print("Style_SKU_Sheet._refresh_ui error:", e)

  def btn_save(self, **event_args):
    """Raise event 'x-save' back to the parent form (main form will handle server update)."""
    try:
      item = self.item or {}

      def set_field(k, v):
        try:
          self._set_val(item, k, v)
        except Exception:
          pass

      set_field("sku_id", (self.text_box_sku_id.text or "").strip())

      if hasattr(self, "text_box_ref"):
        set_field("ref_id", (self.text_box_ref_id.text or "").strip())

      if hasattr(self, "text_box_master"):
        set_field("master_material", (self.text_box_master_material.text or "").strip())

      if hasattr(self, "text_box_color"):
        set_field("color", (self.text_box_color.text or "").strip())

      if hasattr(self, "text_box_size"):
        set_field("size", (self.text_box_size.text or "").strip())

      if hasattr(self, "text_box_qr"):
        set_field("qr_data", (self.text_box_qr.text or "").strip())

      if hasattr(self, "text_box_override"):
        try:
          ptxt = (self.text_box_price.text or "").strip()
          if ptxt:
            set_field("price", float(ptxt))
          else:
            set_field("price", None)
        except Exception:
          alert("Price must be a number")
          return

      # push changed item back to repeating panel's list / notify parent
      self.raise_event('x-save')

    except Exception as e:
      alert(f"Could not prepare save: {e}")

  def btn_delete(self, **event_args):
    """Raise event 'x-delete' — parent will handle confirmation/server delete."""
    self.raise_event('x-delete')
