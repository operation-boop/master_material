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

    # BOM list
    self.bom_list = []
    self.bom_repeating_panel.items = self.bom_list
    self.material_dropdown.items = ["MAT-001 - Cotton Twill", "MAT-002 - Polyester Lining", "MAT-003 - Button 20L"]

    # Processing Costs list
    self.processing_list = []
    self.repeating_panel_processing_costs.items = self.processing_list
    self.type_dropdown.items = ["Cut & Make", "Embroidery", "Washing"]
    
  def close_btn_click(self, **event_args):
    self.raise_event("x-close-alert")

  def cancel_btn_click(self, **event_args):
    self.raise_event("x-close-alert")

  def BOM_add_btn_click(self, **event_args):
    material = self.material_dropdown.selected_value
    consumption = self.consumption.text
    unit_cost = self.unit_cost.text
  
    # Validate
    if not material or not consumption or not unit_cost:
      Notification("Please fill all BOM fields.").show()
      return
  
    try:
      consumption = float(consumption)
      unit_cost = float(unit_cost)
    except ValueError:
      Notification("Consumption and Unit Cost must be numbers.").show()
      return
  
    # Calculate line total
    line_total = consumption * unit_cost
  
    # Append to list
    self.bom_list.append({
      "material": material,
      "consumption": consumption,
      "unit_cost": unit_cost,
      "total": line_total
    })
  
    # Refresh
    self.bom_repeating_panel.items = self.bom_list
  
    # Reset inputs
    self.material_dropdown.selected_value = None
    self.consumption.text = ""
    self.unit_cost.text = ""

  def processing_costs_add_btn_click(self, **event_args):
    type = self.type_dropdown.selected_value
    vendor = self.vendor.text
    cost = self.cost.text
  
    if not type or not vendor or not cost:
      Notification("Please fill all Processing Cost fields.").show()
      return
  
    try:
      cost = float(cost)
    except ValueError:
      Notification("Cost must be a number.").show()
      return
  
    self.processing_list.append({
      "type": type,
      "vendor": vendor,
      "cost": cost
    })
  
    self.repeating_panel_processing_costs.items = self.processing_list
  
    self.type_dropdown.selected_value = None
    self.vendor.text = ""
    self.cost.text = ""

    
