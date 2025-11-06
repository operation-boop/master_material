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
    self.init_components(**properties)
    self.form_show()

  def add_btn_click(self, **event_args):
    """Creates new material with 'Creating' status"""
    try:
      # Create new material document on server
      result = anvil.server.call('create_new_master_material', 'test_user@example.com')
      document_id = result['document_id']
      # Show notification
      Notification(f"Created new material: {document_id}", style="success", timeout=2).show()
      # Import and create popup WITH document_id
      from ..Material_input_form import Material_input_form
      popup = Material_input_form(current_document_id=document_id)  
      alert(
        content=popup,
        title=f"New Material - {document_id}",
        large=True,
        buttons=None 
      )
      self.load_materials()

    except Exception as e:
      alert(f"Error creating material: {str(e)}")

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

    self.flow_panel_materials.clear()

    for m in materials:
      from .MaterialCard import MaterialCard
      card = MaterialCard(item=m)
      card.width = "100%" 
      self.flow_panel_materials.add_component(card)