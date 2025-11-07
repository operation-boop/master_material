from ._anvil_designer import CostSheetCardTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...wanyan_ver_cost_sheet_details import wanyan_ver_cost_sheet_details

class CostSheetCard(CostSheetCardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def view_details_btn_click(self, **event_args):
    # Get the Home form
    home_form = get_open_form()

    # Clear the content panel and add Material_details
    home_form.content_panel.clear()
    home_form.content_panel.add_component(
      wanyan_ver_cost_sheet_details(cost_sheet_data=self.item),
      full_width_row=True
    )
