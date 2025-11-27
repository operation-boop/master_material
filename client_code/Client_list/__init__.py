from ._anvil_designer import Client_listTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Client_list(Client_listTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.clients = anvil.server.call('get_clients')
    self.show_grid_view()

  def show_grid_view(self):
    self.flow_panel_clients.visible = True
    self.data_grid_clients.visible = False

    self.button_grid.background = "#0d6efd"
    self.button_grid.foreground = "white"
    self.button_table.background = "transparent"
    self.button_table.foreground = "black"

    from .client_card import client_card
    self.flow_panel_clients.clear()      
    for c in self.clients:
      card = client_card(item=c)
      card.width = "100%"   # full width in flow panel (2 per row if role set)
      self.flow_panel_clients.add_component(card)

  def show_table_view(self):
    self.flow_panel_clients.visible = False
    self.data_grid_clients.visible = True

    self.button_grid.background = "transparent"
    self.button_grid.foreground = "black"
    self.button_table.background = "#0d6efd"
    self.button_table.foreground = "white"

    self.repeating_panel_1.items = anvil.server.call('get_clients')

  def button_grid_click(self, **event_args):
    self.show_grid_view()

  def button_table_click(self, **event_args):
    self.show_table_view()

  def add_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    from ..Client_input_form import Client_input_form
    popup = Client_input_form()

    result = alert(
      content=popup,
      large=True,
      buttons=None
    )
    if result == "ok":
      self.refresh_data()

  def refresh_data(self):
    self.clients = anvil.server.call('get_clients')
    self.show_grid_view()


