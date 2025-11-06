from ._anvil_designer import MaterialCardTemplate
from anvil import *
from ...Material_detail import Material_detail

class MaterialCard(MaterialCardTemplate):
  def __init__(self, item=None, **properties):
    self.init_components(**properties)
    self.item = item or {}
    self.refresh_card()

  def set_item(self, item):
    self.item = item or {}
    self.refresh_card()

  def refresh_card(self):
    it = self.item or {}
    self.material_id.text        = it.get("master_material_id","")
    self.material_name.text      = it.get("name","")
    self.ref_id.text             = it.get("ref_id","")
    self.material_type.text      = it.get("material_type","")
    self.fabric_composition.text = it.get("fabric_composition","")
    self.weight.text             = it.get("weight","")
    self.supplier.text           = it.get("status","")
    self.cost_per_unit.text      = str(it.get("original_cost_per_unit","") or "")
    supplier = it.get("supplier_name")
    if hasattr(self, "supplier") and self.supplier:
      self.supplier.visible = bool(supplier) or bool(self.supplier.text)
      if supplier:
        self.supplier.text = supplier

  def view_details_btn_click(self, **event_args):
    doc_id = (self.item or {}).get("document_id")
    open_form('Material_detail', document_id=doc_id)
