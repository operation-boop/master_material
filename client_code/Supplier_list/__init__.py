from ._anvil_designer import Supplier_listTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Supplier_list(Supplier_listTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.form_show()


    # Any code you write here will run before the form opens.

  def form_show(self, **event_args):

    suppliers = [
      {
        "supplier_id": "SUP001",
        "supplier_name": "ABC Textiles",
        "country": "Vietnam",
        "contact_person": "Nguyen Thanh",
        "email": "nguyen@abctextiles.vn",
        "active_orders": 12,
        "materials_in_catalog": 45,
        "approved_date": "2024-06-15",
        "approved_by": "John",
        "is_approved_vendor": "True"
      },
      {
        "supplier_id": "SUP002",
        "supplier_name": "Shanghai Fabric Co.",
        "country": "China",
        "contact_person": "Li Wei",
        "email": "wei.li@shfabric.cn",
        "active_orders": 4,
        "materials_in_catalog": 18,
        "approved_date": "2024-04-03",
        "approved_by": "Sam",
        "is_approved_vendor": "False"
      },
      {
        "supplier_id": "SUP003",
        "supplier_name": "Hanoi Button Supply",
        "country": "Vietnam",
        "contact_person": "Tran Hoa",
        "email": "hoa@buttons.vn",
        "active_orders": 0,
        "materials_in_catalog": 8,
        "approved_date": "2023-11-22",
        "approved_by": "Minh",
        "is_approved_vendor": "Pending"
      }
    ]

    # CLEAR existing components before adding new ones
    self.flow_panel_suppliers.clear()

    from .supplier_card import supplier_card

    for s in suppliers:
      card = supplier_card(item=s)
      card.width = "100%"   # full width in flow panel (2 per row if role set)
      self.flow_panel_suppliers.add_component(card)

  def add_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    from ..Supplier_input_form import Supplier_input_form

    popup = Supplier_input_form()

    alert(
      content=popup,
      title=None,
      large=True,
      buttons=None 
    )
