from ._anvil_designer import MaterialCardTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Material_detail import Material_detail


class MaterialCard(MaterialCardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def form_show(self, **event_args):
    self._render(self.item)

  def update_from(self, summary):
    self.item = summary
    self._render(summary)

  def _render(self, it):
    self.lbl_material_id.text   = it.get("material_id")
    self.lbl_name.text          = it.get("material_name")
    self.lbl_type.text          = it.get("material_type")
    self.lbl_supplier.text      = it.get("supplier")
    self.lbl_weight.text        = it.get("weight")
    self.lbl_cost.text          = it.get("cost_per_unit")
    self.lbl_status.text        = it.get("verification_status")

  def view_details_btn_click(self, **event_args):
    open_form(Material_detail(material_data=self.item))
