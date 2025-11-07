from ._anvil_designer import Material_input_formTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Material_input_form(Material_input_formTemplate):
  def __init__(self, current_document_id=None, **properties):
    self.init_components(**properties)
    self.current_document_id = current_document_id
    self.material_type_dropdown.items = ["Main Fabric", "Secondary Fabric", "Accessory"]
    self.dropdown_supplier.items = ["ABC","CBA","HELLO","BYE"]
    self.country_of_origin_dropdown.items = ["Vietnam", "China"]
    self.UOM_dropdown.items = ["Meter", "Piece"]
    self.weight_uom_dropdown.items = ["GSM (gram/sq meter)", "GPP (gram/piece)"]
    self.currency_dropdown.items = ["USD", "VND", "RMB"]
    self.vietnam_vat_rate_dropdown.items = ["N/A", "8%", "10%"]
    self.shipping_term_dropdown.items = ["EXW (Ex Works)", "FOB (Free On Board)", "DDP (Delivered Duty Paid)"]


    self.composition_list = []
    self.material_dropdown.items = ["Cotton", "Polyester", "Silk", "Wool", "Elastane"]
    self.fabric_composition_repeating_panel.items = self.composition_list
    self.fabric_composition_repeating_panel.update_total = self.update_total_percentage

    self.details_section.visible = False
    self.advanced_cost_dropdown.items = ["Advanced Cost Calculation"]

  def close_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.raise_event("x-close-alert")

  def advanced_cost_dropdown_change(self, **event_args):
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

    if percentage <= 0:
      Notification("Percentage must be greater than 0.").show()
      return

    if percentage > remaining:
      Notification(f"You can only add up to {remaining}% more.").show()
      self.percentage.text = str(remaining) if remaining > 0 else ""
      return

    self.composition_list.append({
      "material": selected_material,
      "percentage": percentage,
      "form": self
    })

    self.fabric_composition_repeating_panel.items = self.composition_list
    self.material_dropdown.selected_value = None
    self.percentage.text = ""
    self.update_total_percentage()  

  def update_total_percentage(self):
    total = sum([float(item['percentage']) for item in self.composition_list if item['percentage']])
    self.total_percentage.text = f"Total: {total} %"

    remaining = 100 - total

    if remaining <= 0:
      self.material_dropdown.enabled = False
      self.percentage.enabled = False
      self.add_btn.enabled = False
      self.percentage.placeholder = f"Max {remaining}% allowed"
    else:
      self.material_dropdown.enabled = True
      self.percentage.enabled = True
      self.add_btn.enabled = True
      self.percentage.placeholder = f"Max {remaining}% allowed"

  def original_cost_per_unit_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    self.original_cost_unit.text = self.original_cost_per_unit.text

  def supplier_tolerance_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    try:
      original_cost = float(self.original_cost_per_unit.text or 0)
      supplier_tolerance_percentage = float(self.supplier_tolerance.text or 0)
      supplier_tolerance_cost = (supplier_tolerance_percentage / 100) * original_cost
      self.supplier_tolerance_cost_unit.text = str(supplier_tolerance_cost)

      effective_cost = original_cost + supplier_tolerance_cost
      self.effective_cost_per_unit.text = str(effective_cost)
    except (ValueError, TypeError):
      Notification("Please enter valid numbers").show()

  def logistics_rate_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    try:
      logistics_rate = float(self.logistics_rate.text or 0)
      effective_cost = float(self.effective_cost_per_unit.text or 0)
      landed_cost = ((logistics_rate/100) * effective_cost) + effective_cost
      self.landed_cost.text = str(landed_cost)
    except (ValueError, TypeError):
      Notification("Please enter valid numbers").show()
##---------------------------------------------------------------
  def save_as_draft_btn_click(self, **event_args):
    """Collect all form data and save as draft"""
    if not self.current_document_id:
      Notification("Please create a material first!", style="warning", timeout=3).show()
      return

    form_data = self.collect_form_data()

    try:
      anvil.server.call('save_or_edit_draft', self.current_document_id, 'test_user@example.com', form_data)
      Notification("Draft saved!", style="success", timeout=3).show()
      self.raise_event("x-refresh-list", document_id=self.current_document_id)
    except Exception as e:
      Notification(f"Error: {str(e)}", style="danger", timeout=3).show()

  def submit_btn_click(self, **event_args):
    """Collect all form data and submit"""
    if not self.current_document_id:
      Notification("Please create a material first!", style="warning", timeout=3).show()
      return
      
    form_data = self.collect_form_data()
    if not self.validate_form_data(form_data):
      Notification("Please fill in all required fields!", style="warning", timeout=3).show()
      return
      
    try:
      self.submit_btn.enabled = False
      self.submit_btn.text = "Submitting..."
      anvil.server.call('submit_version', self.current_document_id, 'test_user@example.com', form_data)
      Notification("Submitted successfully!", style="success", timeout=3).show()
      self.raise_event("x-refresh-list", document_id=self.current_document_id)
      self.raise_event("x-close-alert", value=True)

    except Exception as e:
      error_msg = f"Submission failed: {str(e)}"
      print(f"Full error: {repr(e)}")  # Check console for full error
      Notification(error_msg, style="danger", timeout=5).show()
    finally:
      self.submit_btn.enabled = True
      self.submit_btn.text = "Submit"

  def validate_form_data(self, form_data):
    """Basic client-side validation"""
    required_fields = [
      'name', 'material_type', 'country_of_origin', 'supplier_name',
      'unit_of_measurement', 'weight_per_unit', 'weight_uom',
      'original_cost_per_unit', 'native_cost_currency'
    ]

    for field in required_fields:
      if not form_data.get(field):
        print(f"Missing required field: {field}")
        return False

      # Validate composition total is 100%
    if hasattr(self, 'composition_list') and self.composition_list:
      total = sum([float(item['percentage']) for item in self.composition_list])
      if total != 100:
        Notification(f"Composition total must be 100% (currently {total}%)", style="warning").show()
        return False

    return True

  def collect_form_data(self):
    """Collect all form fields into a dictionary"""

    # Parse VAT rate safely
    vat_value = None
    if self.vietnam_vat_rate_dropdown.selected_value:
      if self.vietnam_vat_rate_dropdown.selected_value != "N/A":
        try:
          vat_value = float(self.vietnam_vat_rate_dropdown.selected_value.replace('%', ''))
        except (ValueError, AttributeError):
          vat_value = None

    return {
      # Basic Info
      "name": self.material_name.text if hasattr(self, 'material_name') else None,
      "material_type": self.material_type_dropdown.selected_value,
      "country_of_origin": self.country_of_origin_dropdown.selected_value,
      "supplier_name" : self.dropdown_supplier.selected_value,
      "unit_of_measurement": self.UOM_dropdown.selected_value,
      "fabric_roll_width": self.parse_float(self.fabric_roll_width.text) if hasattr(self, 'fabric_roll_width') else None,
      "fabric_cut_width": self.parse_float(self.fabric_cut_width.text) if hasattr(self, 'fabric_cut_width') else None,
      "fabric_cut_width_no_shrinkage": self.parse_float(self.fabric_cut_width_no_shrinkage.text) if hasattr(self, 'fabric_cut_width_no_shrinkage') else None,
      "weight_per_unit": self.parse_float(self.weight_per_unit.text) if hasattr(self, 'weight_per_unit') else None,
      "weight_uom": self.weight_uom_dropdown.selected_value,
      "weft_shrinkage": self.parse_float(self.weft_shrinkage.text) if hasattr(self, 'weft_shrinkage') else None,
      "werp_shrinkage": self.parse_float(self.werp_shrinkage.text) if hasattr(self, 'werp_shrinkage') else None,
      "generic_material_size": self.parse_float(self.generic_material_size.text) if hasattr(self,'generic_material_size') else None,
      "fabric_composition": "|".join([f"{item['material']}:{item['percentage']}%" for item in self.composition_list]),

      # Costs
      "original_cost_per_unit": self.parse_float(self.original_cost_per_unit.text) if hasattr(self, 'original_cost_per_unit') else None,
      "native_cost_currency": self.currency_dropdown.selected_value,
      "supplier_selling_tolerance": self.parse_float(self.supplier_tolerance.text) if hasattr(self, 'supplier_tolerance') else None,
      "refundable_tolerance": self.refundable_tolerance.checked if hasattr(self, 'refundable_tolerance') else False,
      "effective_cost_per_unit": self.parse_float(self.effective_cost_per_unit.text) if hasattr(self, 'effective_cost_per_unit') else None,
      "vietnam_vat_rate": vat_value,  # FIXED: Safe VAT parsing
      "refundable_vat": self.refundable_vat.checked if hasattr(self, 'refundable_vat') else False,
      "import_duty": self.parse_float(self.import_duty.text) if hasattr(self, 'import_duty') else None,
      "refundable_import_duty": self.refundable_import_duty.checked if hasattr(self,'refundable_import_duty') else False,
      "shipping_term": self.shipping_term_dropdown.selected_value,
      "logistics_rate": self.parse_float(self.logistics_rate.text) if hasattr(self, 'logistics_rate') else None,
      "logistics_fee_per_unit": self.parse_float(self.logistics_fee_per_unit.text) if hasattr(self, 'logistics_fee_per_unit') else None,
      "landed_cost_per_unit": self.parse_float(self.landed_cost.text) if hasattr(self, 'landed_cost') else None,
    }

  def parse_float(self, value):
    """Helper to safely parse float values"""
    try:
      return float(value) if value else None
    except (ValueError, TypeError):
      return None
