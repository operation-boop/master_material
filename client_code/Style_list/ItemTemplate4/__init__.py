from ._anvil_designer import ItemTemplate4Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Style_details import Style_details


class ItemTemplate4(ItemTemplate4Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def view_details_btn_click(self, **event_args):
    # Get the Home form
    home_form = get_open_form()

    # Clear the content panel and add Material_details
    home_form.content_panel.clear()
    home_form.content_panel.add_component(
      Style_details(style_data=self.item),
      full_width_row=True
    )

