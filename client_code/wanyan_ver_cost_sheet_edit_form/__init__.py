from ._anvil_designer import wanyan_ver_cost_sheet_edit_formTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class wanyan_ver_cost_sheet_edit_form(wanyan_ver_cost_sheet_edit_formTemplate):
  def __init__(self, cost_sheet=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Store a copy so modifications don't affect original until Save
    self.cost_sheet = dict(cost_sheet)

    self.master_style_dropdown.items = ["MS-001 - White Blazer", "MS-002 - Denim Jeans", "MS-003 - Wool Coat"]
    self.currency_dropdown.items = ["USD", "VND", "RMB"]
    self.material_dropdown.items = ["MAT-001 - Cotton Twill", "MAT-002 - Polyester Lining", "MAT-003 - Button 20L"]
    self.type_dropdown.items = ["Cut & Make", "Embroidery", "Washing"]
    self.overhead_costs_type_dropdown.items = ["MS-001 - White Blazer", "MS-002 - Denim Jeans", "MS-003 - Wool Coat"]
    self.overhead_costs_currency.items = ["USD", "VND", "RMB"]

    # Fill simple fields
    self.master_style_dropdown.selected_value = self.cost_sheet.get("master_style", "")
    self.currency_dropdown.selected_value = self.cost_sheet.get("currency", "")
    self.change_description.text = self.cost_sheet.get("change_description", "")

    # BOM list
    self.bom_list = list(self.cost_sheet.get("bom", []))
    self.bom_repeating_panel.items = self.bom_list

    # Processing Costs list
    self.processing_list = list(self.cost_sheet.get("processing_costs", []))
    self.repeating_panel_processing_costs.items = self.processing_list

    # Overhead Costs list
    self.overhead_list = list(self.cost_sheet.get("overhead_costs", []))
    self.repeating_panel_overhead_costs.items = self.overhead_list
  

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
    total = consumption * unit_cost

    # Append to list
    self.bom_list.append(
      {
        "material": material,
        "consumption": consumption,
        "unit_cost": unit_cost,
        "total": total,
      }
    )

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

    self.processing_list.append(
      {"type": type, "vendor": vendor, "cost": cost}
    )

    self.repeating_panel_processing_costs.items = self.processing_list
    self.type_dropdown.selected_value = None
    self.vendor.text = ""
    self.cost.text = ""

  def overhead_costs_add_btn_click(self, **event_args):
    type = self.overhead_costs_type_dropdown.selected_value
    description = self.description.text
    cost = self.overhead_costs_cost.text
    currency = self.overhead_costs_currency.selected_value

    if not type or not description or not cost or not currency:
      Notification("Please fill all Processing Cost fields.").show()
      return

    try:
      cost = float(cost)
    except ValueError:
      Notification("Cost must be a number.").show()
      return

    self.overhead_list.append(
      {"type": type, "description": description, "cost": cost, "currency": currency}
    )

    self.repeating_panel_overhead_costss.items = self.overhead_list
    self.overhead_costs_type_dropdown.selected_value = None
    self.description.text = ""
    self.overhead_costs_cost.text = ""
    self.overhead_costs_currency.selected_value = None


