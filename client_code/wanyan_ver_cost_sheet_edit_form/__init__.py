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
    # Handle None or empty cost_sheet FIRST
    if cost_sheet is None:
      cost_sheet = {}

      # Get raw data
    bom_raw = cost_sheet.get('bom') or []
    processing_raw = cost_sheet.get('processing_costs') or []
    overhead_raw = cost_sheet.get('overhead_costs') or []

    # DEBUG
    print("=" * 50)
    print("EDIT FORM DEBUG:")
    print(f"BOM items count: {len(bom_raw)}")
    if bom_raw:
     first_material = bom_raw[0].get('material_name')
     print(f"Material LiveObject type: {type(first_material)}")
     print(f"Material LiveObject: {first_material}")

    # Try to access common column names
    if first_material:
      try:
        print(f"  Trying 'name': {first_material['name']}")
      except (KeyError, TypeError):
        print("  No 'name' column")

      try:
        print(f"  Trying 'material_name': {first_material['material_name']}")
      except (KeyError, TypeError):
        print("  No 'material_name' column")

      try:
        print(f"  Trying 'description': {first_material['description']}")
      except (KeyError, TypeError):
        print("  No 'description' column")

      try:
        print(f"  Trying 'material_id': {first_material['material_id']}")
      except (KeyError, TypeError):
        print("  No 'material_id' column")

    print("=" * 50)


    # Transform BOM data to match Designer bindings
    bom_transformed = []
    for item in bom_raw:
      bom_transformed.append({
        'material': item.get('material_name'),  # Transform key
        'consumption': item.get('consumption'),
        'unit_cost': item.get('unit_cost'),
        'total': item.get('total_cost')  # Transform key
      })
      

      # Transform Processing data to match Designer bindings
    processing_transformed = []
    for item in processing_raw:
      processing_transformed.append({
        'processing_type': item.get('processing_type') or item.get('type'),  # Handle both keys
        'vendor_name': item.get('vendor_name') or item.get('vendor'),
        'cost': item.get('cost')
      })

      # Transform Overhead data to match Designer bindings
    overhead_transformed = []
    for item in overhead_raw:
      overhead_transformed.append({
        'type': item.get('type'),
        'description': item.get('description'),
        'cost': item.get('cost'),
        'currency': item.get('currency')
      })
      
      # Set self.item with transformed data
    self.item = {
      'bom': bom_transformed,
      'processing_costs': processing_transformed,
      'overhead_costs': overhead_transformed,
      'master_style': cost_sheet.get('master_style') or '',
      'currency': cost_sheet.get('currency') or '',
      'change_description': cost_sheet.get('change_description') or ''
    }
    print("TRANSFORMED DATA CHECK:")
    print(f"bom_transformed: {bom_transformed}")
    print(f"self.item['bom']: {self.item['bom']}")
    

    # Store original for reference
    self.cost_sheet = dict(cost_sheet)

    # NOW initialize components - bindings will use self.item
    self.init_components(**properties)

    # Set up dropdown items
    self.master_style_dropdown.items = ["MS-001 - White Blazer", "MS-002 - Denim Jeans", "MS-003 - Wool Coat"]
    self.currency_dropdown.items = ["USD", "VND", "RMB"]
    self.material_dropdown.items = ["MAT-001 - Cotton Twill", "MAT-002 - Polyester Lining", "MAT-003 - Button 20L"]
    self.type_dropdown.items = ["Cut & Make", "Embroidery", "Washing"]
    self.overhead_costs_type_dropdown.items = ["MS-001 - White Blazer", "MS-002 - Denim Jeans", "MS-003 - Wool Coat"]
    self.overhead_costs_currency.items = ["USD", "VND", "RMB"]

    # Set dropdown selected values from data
    self.master_style_dropdown.selected_value = self.item.get("master_style", "")
    self.currency_dropdown.selected_value = self.item.get("currency", "")
    self.change_description.text = self.item.get("change_description", "")

    # Set up working lists for adding new items
    self.bom_list = list(self.item['bom'])
    self.processing_list = list(self.item['processing_costs'])
    self.overhead_list = list(self.item['overhead_costs'])




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

