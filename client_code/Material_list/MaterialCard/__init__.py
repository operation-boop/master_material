from ._anvil_designer import MaterialCardTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Material_detail import Material_detail


class MaterialCard(MaterialCardTemplate):
  def __init__(self, item=None, **properties):
    self.init_components(**properties)
    self.item = item or {}
    self.refresh_card()

    
  def refresh_card(self):
    self.material_id.text = self.item.get("master_material_id", "")
    self.material_name.text = self.item.get("name", "")
    self.ref_id.text = self.item.get("ref_id", "")
    self.material_type.text = self.item.get("material_type", "")
    self.fabric_composition.text = self.item.get("fabric_composition", "")
    self.weight.text = self.item.get("weight", "")
    self.supplier.text = self.item.get("status", "")
    self.cost_per_unit.text = self.item.get("original_cost_per_unit", "")
    
    # supplier_name is optional; show only if present
    supplier = self.item.get("supplier_name")
    if hasattr(self, "supplier") and self.supplier:
      self.supplier.visible = bool(supplier)
      if supplier:
        self.supplier.text = supplier

  def view_details_btn_click(self, **event_args):
    open_form('Material_detail')
    pass
