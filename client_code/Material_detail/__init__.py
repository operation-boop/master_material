from ._anvil_designer import Material_detailTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Material_detail(Material_detailTemplate):
  def __init__(self, item=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.item = item

    # Any code you write here will run before the form opens.

  def back_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Material_list')
