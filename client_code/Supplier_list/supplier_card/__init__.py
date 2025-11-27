from ._anvil_designer import supplier_cardTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Supplier_details import Supplier_details


class supplier_card(supplier_cardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    status = self.item['status']
    if status is True:
      self.status.text = "\u2714  Approved"   # check mark unicode also ok
      self.status.foreground = "#0B7D07"             # green text
      self.status.background = "#DFF8E1"             # soft green bg
    elif status is False:
      self.status.text = "\u2716  Not Approved"
      self.status.foreground = "#9B0A0A"             # red text
      self.status.background = "#F9D6D6"             # soft red bg
    else:   # pending case (None or "Pending")
      self.status.text = "\u26A0  Pending"
      self.status.foreground = "#856404"             # brownish yellow text
      self.status.background = "#FFF3CD"             # soft yellow bg

    self.status.role = "status-label"


  def view_details_btn_click(self, **event_args):
    # Get the Home form
    home_form = get_open_form()

    # Clear the content panel and add Supplier_details
    home_form.content_panel.clear()
    home_form.content_panel.add_component(
      Supplier_details(supplier_data=self.item),
      full_width_row=True
    )