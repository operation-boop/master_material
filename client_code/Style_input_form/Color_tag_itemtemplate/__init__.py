from ._anvil_designer import Color_tag_itemtemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Color_tag_itemtemplate(Color_tag_itemtemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def remove_btn_click(self, **event_args):
    # Call back to parent form to remove the item
    self.parent.raise_event('x-remove-color', value=self.item)
