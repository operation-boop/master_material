from ._anvil_designer import wanyan_ver_cost_sheet_input_formTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class wanyan_ver_cost_sheet_input_form(wanyan_ver_cost_sheet_input_formTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.master_style_dropdown.items = ["MS-001 - White Blazer", "MS-002 - Denim Jeans", "MS-003 - Wool Coat"]
    self.currency_dropdown.items = ["USD", "VND", "RMB"]
    self.material_dropdown.items = ["MAT-001 - Cotton Twill", "MAT-002 - Polyester Lining", "MAT-003 - Button 20L"]
    self.type_dropdown.items = ["Cut & Make", "Embroidery", "Washing"]
    
  def close_btn_click(self, **event_args):
    self.raise_event("x-close-alert")

  def cancel_btn_click(self, **event_args):
    self.raise_event("x-close-alert")
