from ._anvil_designer import Material_input_formTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Material_input_form(Material_input_formTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    self.material_type_dropdown.items = ["Main Fabric", "Secondary Fabric", "Accessory"]
    suppliers = anvil.server.call("get_suppliers")
    self.supplier_dropdown.items = [(s['supplier_name'], s) for s in suppliers]
    self.country_of_origin_dropdown.items = ["Vietnam", "China"]
    self.UOM_dropdown.items = ["Meter", "Piece"]
    self.weight_uom_dropdown.items = ["GSM (gram/sq meter)", "GPP (gram/piece)"]
    self.currency_dropdown.items = ["USD", "VND", "RMB"]
    self.vietnam_vat_rate_dropdown.items = ["N/A", "8%", "10%"]
    self.shipping_term_dropdown.items = ["EXW (Ex Works)", "FOB (Free On Board)", "DDP (Delivered Duty Paid)"]

    # all_materials = anvil.server.call('get_all_materials') 
    #self.material_dropdown.items = [(m['material_name'], m) for m in all_materials]
    #self.fabric_composition_repeating_panel.item_template = Material_composition_row

    self.composition_list = []   # this will store all composition entries
    self.material_dropdown.items = ["Cotton", "Polyester", "Silk", "Wool", "Elastane"]
    self.fabric_composition_repeating_panel.items = self.composition_list
    self.fabric_composition_repeating_panel.update_total = self.update_total_percentage

    self.details_section.visible = False
    self.advanced_cost_dropdown.items = ["Advanced Cost Calculation"]
    # Any code you write here will run before the form opens.

  def close_btn_click(self, **event_args):
    self.raise_event("x-close-alert")

  def advanced_cost_dropdown_change(self, **event_args):
      # Show the section only if a value is selected (not None or blank)
    if self.advanced_cost_dropdown.selected_value == "Advanced Cost Calculation":
      self.details_section.visible = True
    else:
      self.details_section.visible = False

  def currency_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.original_cost_unit.text = self.currency_dropdown.selected_value
    self.supplier_tolerance_cost_unit.text = self.currency_dropdown.selected_value
    self.effective_cost_unit.text = self.currency_dropdown.selected_value
    self.landed_cost_unit.text = self.currency_dropdown.selected_value
    self.logistics_unit_cost.text = self.currency_dropdown.selected_value

  def add_btn_click(self, **event_args):
    selected_material = self.material_dropdown.selected_value

    if not self.percentage.text:
      Notification("Please enter a percentage.").show()
      return

    try:
      percentage = float(self.percentage.text)
    except ValueError:
      Notification("Percentage must be a number.").show()
      return
    
    total = sum([float(item['percentage']) for item in self.composition_list])
    remaining = 100 - total

    # Reject invalid input
    if percentage <= 0:
      Notification("Percentage must be greater than 0.").show()
      return

    if percentage > remaining:
      Notification(f"You can only add up to {remaining}% more.").show()
      self.percentage.text = str(remaining) if remaining > 0 else ""
      return
    
    # Add item to list
    self.composition_list.append({
      "material": selected_material,
      "percentage": percentage,
      "form": self
    })
    
    # Refresh repeating panel
    self.fabric_composition_repeating_panel.items = self.composition_list
    self.material_dropdown.selected_value = None
    self.percentage.text = ""  # Clear input
    self.update_total_percentage()  

  def update_total_percentage(self):
    total = sum([float(item['percentage']) for item in self.composition_list if item['percentage']])
    self.total_percentage.text = f"Total: {total} %"

    # Remaining percentage allowed
    remaining = 100 - total

    # Disable input if total full
    if remaining <= 0:
      self.material_dropdown.enabled = False
      self.percentage.enabled = False
      self.add_btn.enabled = False
      self.percentage.placeholder = f"Max {remaining}% allowed"
    else:
      self.material_dropdown.enabled = True
      self.percentage.enabled = True
      self.add_btn.enabled = True

      # Also restrict textbox max manually
      self.percentage.placeholder = f"Max {remaining}% allowed"

  def original_cost_per_unit_change(self, **event_args):
    if(self.original_cost_per_unit.text is not None):
      self.original_cost.text = self.original_cost_per_unit.text

  def supplier_tolerance_change(self, **event_args):
    if(self.supplier_tolerance.text is not None):
      original_cost = int(self.original_cost_per_unit.text)
      supplier_tolerance_percentage = int(self.supplier_tolerance.text)
      supplier_tolerance_cost = (supplier_tolerance_percentage / 100) * original_cost
      self.supplier_tolerance_cost.text = str(supplier_tolerance_cost)
  
      effective_cost = original_cost + supplier_tolerance_cost
      self.effective_cost_per_unit.text = str(effective_cost)

  def logistics_rate_change(self, **event_args):
    if(self.logistics_rate.text is not None):
      logistics_rate = int(self.logistics_rate.text)
      effective_cost = int(float(self.effective_cost_per_unit.text))
      landed_cost = ((logistics_rate/100) * effective_cost ) + effective_cost
      self.landed_cost.text = str(landed_cost)
      weight_per_unit = int(self.weight_per_unit.text)
      logistics_fee_per_unit = weight_per_unit * logistics_rate
      self.logistics_fee_per_unit.text = str(logistics_fee_per_unit)

  def cancel_btn_click(self, **event_args):
    self.raise_event("x-close-alert")
