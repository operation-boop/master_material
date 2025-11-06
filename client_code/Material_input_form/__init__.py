from ._anvil_designer import Material_input_formTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

class Material_input_form(Material_input_formTemplate):
  # ------------------------ INIT ------------------------
  def __init__(self, current_document_id=None, **properties):
    self.init_components(**properties)
    self.current_document_id = current_document_id

    # dropdown options
    self.material_type_dropdown.items = ["Main Fabric", "Secondary Fabric", "Accessory"]
    self.dropdown_supplier.items = ["ABC","CBA","HELLO","BYE"]
    self.country_of_origin_dropdown.items = ["Vietnam", "China"]
    self.UOM_dropdown.items = ["Meter", "Piece"]
    self.weight_uom_dropdown.items = ["GSM (gram/sq meter)", "GPP (gram/piece)"]
    self.currency_dropdown.items = ["USD", "VND", "RMB"]
    self.vietnam_vat_rate_dropdown.items = ["N/A", "8%", "10%"]
    self.shipping_term_dropdown.items = ["EXW (Ex Works)", "FOB (Free On Board)", "DDP (Delivered Duty Paid)"]

    # composition
    self.composition_list = []
    self.material_dropdown.items = ["Cotton", "Polyester", "Silk", "Wool", "Elastane"]
    self.fabric_composition_repeating_panel.items = self.composition_list
    self.fabric_composition_repeating_panel.update_total = self.update_total_percentage

    self.details_section.visible = False
    self.advanced_cost_dropdown.items = ["Advanced Cost Calculation"]

  # ------------------------ UI BASICS ------------------------
  def close_btn_click(self, **event_args):
    self.raise_event("x-close-alert")

  def advanced_cost_dropdown_change(self, **event_args):
    self.details_section.visible = (self.advanced_cost_dropdown.selected_value == "Advanced Cost Calculation")

  def currency_dropdown_change(self, **event_args):
    """Show currency code on unit labels; do NOT overwrite them elsewhere."""
    code = self.currency_dropdown.selected_value or ""
    self.original_cost_unit.text = code
    self.supplier_tolerance_cost_unit.text = code
    self.effective_cost_unit.text = code
    self.landed_cost_unit.text = code

  # ------------------------ COMPOSITION ------------------------
  def add_btn_click(self, **event_args):
    m = self.material_dropdown.selected_value
    if not m:
      Notification("Please choose a material.", style="warning").show()
      return

    if not self.percentage.text:
      Notification("Please enter a percentage.", style="warning").show()
      return

    try:
      pct = float(self.percentage.text)
    except ValueError:
      Notification("Percentage must be a number.", style="warning").show()
      return

    if pct <= 0:
      Notification("Percentage must be greater than 0.", style="warning").show()
      return

    # prevent duplicates
    if any(i["material"] == m for i in self.composition_list):
      Notification(f"{m} is already added.", style="warning").show()
      return

    total = sum(float(item["percentage"]) for item in self.composition_list)
    remaining = max(0.0, 100.0 - total)
    if pct > remaining + 1e-9:
      Notification(f"You can add at most {remaining:.2f}% more.", style="warning").show()
      self.percentage.text = f"{remaining:.2f}" if remaining > 0 else ""
      return

    self.composition_list.append({"material": m, "percentage": pct, "form": self})
    self.fabric_composition_repeating_panel.items = list(self.composition_list)  # refresh
    self.material_dropdown.selected_value = None
    self.percentage.text = ""
    self.update_total_percentage()

  def update_total_percentage(self):
    total = sum(float(item["percentage"]) for item in self.composition_list if item.get("percentage") is not None)
    self.total_percentage.text = f"Total: {total:.2f} %"

    remaining = max(0.0, 100.0 - total)
    block = remaining <= 0.0
    self.material_dropdown.enabled = not block
    self.percentage.enabled = not block
    self.add_btn.enabled = not block
    self.percentage.placeholder = "Total reached" if block else f"Max {remaining:.2f}% allowed"

  # ------------------------ COST LOGIC ------------------------
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

  # ------------------------ DRAFT / SUBMIT ------------------------
  def save_as_draft_btn_click(self, **event_args):
    """Collect all form data and save as draft"""
    if not self.current_document_id:
      Notification("Please create a material first!", style="warning", timeout=3).show()
      return

    form_data = self.collect_form_data()
    try:
      # If your server expects (document_id, 'user', form_data) keep your old call.
      anvil.server.call('save_or_edit_draft', self.current_document_id, form_data)
      Notification("Draft saved!", style="success", timeout=3).show()
    except Exception as e:
      Notification(f"Error: {str(e)}", style="danger", timeout=3).show()

  def submit_button_click(self, **event_args):
    """Collect all form data and submit"""
    if not self.current_document_id:
      Notification("Please create a material first!", style="warning", timeout=3).show()
      return

    form_data = self.collect_form_data()
    if not self.validate_form_data(form_data):
      return

    try:
      if hasattr(self, "submit_btn"):
        self.submit_btn.enabled = False
        self.submit_btn.text = "Submitting..."

      # Server should also validate and set status=Submitted
      result = anvil.server.call('submit_version', self.current_document_id, 'test_user@example.com', form_data)
      if result and result.get("ok"):
        Notification("Submitted successfully!", style="success", timeout=3).show()
        self.raise_event("x-close-alert", value=True)
      else:
        msg = (result and result.get("error")) or "Submit failed."
        Notification(msg, style="danger", timeout=5).show()
    except Exception as e:
      print(f"Full error: {repr(e)}")
      Notification(f"Submission failed: {str(e)}", style="danger", timeout=5).show()
    finally:
      if hasattr(self, "submit_btn"):
        self.submit_btn.enabled = True
        self.submit_btn.text = "Submit"

  # ------------------------ VALIDATION & COLLECTION ------------------------
  def validate_form_data(self, form_data):
    """Basic client-side validation with safer composition check."""
    required_fields = [
      'name', 'material_type', 'country_of_origin', 'supplier_name',
      'unit_of_measurement', 'weight_per_unit', 'weight_uom',
      'original_cost_per_unit', 'native_cost_currency'
    ]
    for field in required_fields:
      if not form_data.get(field):
        Notification(f"Please fill in: {field.replace('_',' ').title()}", style="warning").show()
        return False

    # composition ≈ 100%
    try:
      comp = json.loads(form_data.get("fabric_composition") or "[]")
    except Exception:
      Notification("Fabric composition is invalid.", style="warning").show()
      return False

    total = sum(float(item.get("percentage", 0)) for item in comp)
    if abs(total - 100.0) > 0.01:
      Notification(f"Composition total must be 100% (currently {total:.2f}%)", style="warning").show()
      return False

    # ranges
    for key in ("supplier_selling_tolerance","vietnam_vat_rate","import_duty"):
      v = form_data.get(key)
      if v is not None and not (0 <= v <= 100):
        Notification(f"{key.replace('_',' ').title()} must be between 0 and 100", style="warning").show()
        return False
    for key in ("original_cost_per_unit","effective_cost_per_unit","logistics_rate","logistics_fee_per_unit","landed_cost_per_unit"):
      v = form_data.get(key)
      if v is not None and v < 0:
        Notification(f"{key.replace('_',' ').title()} cannot be negative", style="warning").show()
        return False

    return True

  def collect_form_data(self):
    """Collect all form fields into a dictionary (DB-aligned)."""

    # VAT parse
    vat_value = None
    sv = getattr(self.vietnam_vat_rate_dropdown, "selected_value", None)
    if sv and sv != "N/A":
      try:
        vat_value = float(str(sv).replace('%', ''))
      except (ValueError, AttributeError):
        vat_value = None

    # Composition as JSON string (DB column is string)
    comp_json = json.dumps([
      {"material": item["material"], "percentage": float(item["percentage"])}
      for item in self.composition_list
      if item.get("material") and item.get("percentage") is not None
    ])

    return {
      # Basic Info
      "name": getattr(self, 'material_name', None) and self.material_name.text,
      "material_type": self.material_type_dropdown.selected_value,
      "supplier_name": self.dropdown_supplier.selected_value,
      "ref_id": self._p(self.supplier_reference_id.text),
      "country_of_origin": self.country_of_origin_dropdown.selected_value,
      "unit_of_measurement": self.UOM_dropdown.selected_value,


      # Dimensions & weight
      "fabric_roll_width": self._p(self.fabric_roll_width),
      "fabric_cut_width": self._p(self.fabric_cut_width),
      "fabric_cut_width_no_shrinkage": self._p(self.fabric_cut_width_no_shrinkage),
      "weight_per_unit": self._p(self.weight_per_unit),
      "weight_uom": self.weight_uom_dropdown.selected_value,
      "generic_material_size": getattr(self, "generic_material_size", None) and self.generic_material_size.text,

      # Shrinkage (schema uses 'werp_shrinkage')
      "weft_shrinkage": self._p(self.weft_shrinkage),
      "werp_shrinkage": self._p(getattr(self, "werp_shrinkage", None) or getattr(self, "warp_shrinkage", None)),

      # Composition
      "fabric_composition": comp_json,

      # Costs
      "original_cost_per_unit": self._p(self.original_cost_per_unit),
      "native_cost_currency": self.currency_dropdown.selected_value,
      "supplier_selling_tolerance": self._p(self.supplier_tolerance),
      "refundable_tolerance": hasattr(self, 'refundable_tolerance') and self.refundable_tolerance.checked or False,
      "effective_cost_per_unit": self._p(self.effective_cost_per_unit),
      "vietnam_vat_rate": vat_value,
      "refundable_vat": hasattr(self, 'refundable_vat') and self.refundable_vat.checked or False,
      "import_duty": self._p(self.import_duty),
      "refundable_import_duty": hasattr(self, 'refundable_import_duty') and self.refundable_import_duty.checked or False,
      "shipping_term": self.shipping_term_dropdown.selected_value,
      "logistics_rate": self._p(self.logistics_rate),
      "logistics_fee_per_unit": self._p(self.logistics_fee_per_unit),
      "landed_cost_per_unit": self._p(self.landed_cost),
    }

  # small helper to parse floats from TextBoxes safely
  def _p(self, ctrl):
    try:
      return float(ctrl.text) if (ctrl and ctrl.text not in ("", None)) else None
    except Exception:
      return None



 








