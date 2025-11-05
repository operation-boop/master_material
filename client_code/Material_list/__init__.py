from ._anvil_designer import Material_listTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Material_list(Material_listTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.load_materials()
    self.form_show()
    # Any code you write here will run before the form opens.

  def load_materials(self):
    try:
      materials = anvil.server.call('get_materials')
      self.repeating_panel_1.items = materials
    except Exception as e:
      alert(f"Error loading materials: {e}")

  def view_details_btn_click(self, **event_args):
    selected = None

    for row_form in self.repeating_panel_1.get_components():
      if getattr(row_form, 'select_row', None) and row_form.select_row.checked:
        selected = row_form.item
        break

    if selected:
      open_form('Material_detail', item=selected)
    else:
      alert("Please select a material first.")

  def add_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    from ..Material_input_form import Material_input_form

    popup = Material_input_form()
  
    alert(
      content=popup,
      title=None,
      large=True,
      buttons=None 
    )

  def form_show(self, **event_args):
  
    materials = [
      {
        "material_id": "M001",
        "ref_id": "R1001",
        "material_name": "Cotton White",
        "material_type": "Fabric",
        "fabric_composition": "100% Cotton",
        "weight": "250gsm",
        "supplier": "ABC Textiles",
        "cost_per_unit": "$4.50",
        "verification_status": "Verified"
      },
      {
        "material_id": "M002",
        "ref_id": "R1002",
        "material_name": "Polyester Black",
        "material_type": "Fabric",
        "fabric_composition": "Polyester Blend",
        "weight": "180gsm",
        "supplier": "XYZ Fabrics",
        "cost_per_unit": "$3.20",
        "verification_status": "Pending"
      },
      {
      "material_id": "M002",
      "ref_id": "R1002",
      "material_name": "Polyester Black",
      "material_type": "Fabric",
      "fabric_composition": "Polyester Blend",
      "weight": "180gsm",
      "supplier": "XYZ Fabrics",
      "cost_per_unit": "$3.20",
      "verification_status": "Pending"
      }
    ]
  
    self.repeating_panel_materials.items = materials
