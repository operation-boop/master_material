from ._anvil_designer import Material_sku_input_formTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Material_sku_input_form(Material_sku_input_formTemplate):
  def __init__(self, master_material=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.master_material.text = master_material
    # Any code you write here will run before the form opens.

  def close_btn_click(self, **event_args):
    self.raise_event("x-close-alert")

  def submit_btn_click(self, **event_args):
    # Get values from form fields
    master_material = self.master_material.text  # could be a label or dropdown value
    ref_id = self.ref_id.text
    qr_data = self.qr_data.text
    sku_cost_override = int(self.sku_cost_override.text)
    color = self.color.text if self.color.text else None
    size = self.size.text if self.size.text else None
  
    # --- Client-side validation ---
    if not master_material:
      alert("Please select a material.")
      return
    if not ref_id:
      alert("Please fill in Ref ID.")
      return
    if not qr_data:
      alert("Please fill in QR Data.")
      return
    if not sku_cost_override:
      alert("Please fill in SKU Cost Override.")
      return
  
    try:
      # Call server to create SKU
      new_row = anvil.server.call('create_material_sku',
                                  master_material,
                                  ref_id,
                                  qr_data,
                                  sku_cost_override,
                                  color,
                                  size)
  
      if hasattr(self.parent, 'refresh_sku_panel'):
        self.parent.refresh_sku_panel(master_material)
  
      
      self.raise_event("x-close-alert")
      alert(f"SKU {new_row['id']} created successfully!")
  
    except Exception as e:
      alert(f"Error creating SKU: {e}")

  