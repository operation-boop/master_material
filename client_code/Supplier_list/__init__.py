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
    self.suppliers = anvil.server.call('get_suppliers')
    self.show_grid_view()

  def show_grid_view(self):
    self.flow_panel_suppliers.visible = True
    self.data_grid_suppliers.visible = False

    self.button_grid.background = "#0d6efd"
    self.button_grid.foreground = "white"
    self.button_table.background = "transparent"
    self.button_table.foreground = "black"

    from .supplier_card import supplier_card
    self.flow_panel_suppliers.clear()    
    for s in self.suppliers:
      card = supplier_card(item=s)
      card.width = "100%"   # full width in flow panel (2 per row if role set)
      self.flow_panel_suppliers.add_component(card)

  def show_table_view(self):
    self.flow_panel_suppliers.visible = False
    self.data_grid_suppliers.visible = True
    self.repeating_panel_1.items = anvil.server.call('get_suppliers')

    self.button_grid.background = "transparent"
    self.button_grid.foreground = "black"
    self.button_table.background = "#0d6efd"
    self.button_table.foreground = "white"

    self.data_grid_suppliers.role = "outlined-card"
    self.data_grid_suppliers.background = "#F8F9FA"
    self.data_grid_suppliers.border = "1px solid #E0E0E0"
    self.data_grid_suppliers.foreground = "#333"
    self.data_grid_suppliers.row_spacing = 4

  def refresh_data(self):
    self.suppliers = anvil.server.call('get_suppliers')
    self.show_grid_view()

  def add_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    from ..Supplier_input_form import Supplier_input_form
    popup = Supplier_input_form()

    result = alert(
      content=popup,
      title=None,
      large=True,
      buttons=None 
    )
    if result == "ok":
      self.refresh_data()

  def button_grid_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.show_grid_view()

  def button_table_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.show_table_view()
