from ._anvil_designer import material_list_rowtemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class material_list_rowtemplate(material_list_rowtemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def data_row_panel_item_click(self, **event_args):
    from ..Material_Details import Material_Details
    open_form('Material_Details', material=self.item)

  def select_row_change(self, **event_args):
    # When this row's checkbox is checked, uncheck others
    if self.select_row.checked:
      for row in self.parent.get_components():
        if row is not self:
          row.select_row.checked = False
