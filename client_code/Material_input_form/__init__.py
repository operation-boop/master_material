from ._anvil_designer import Material_input_formTemplate
from anvil import *
import anvil.server

class Material_input_form(Material_input_formTemplate):
  def __init__(self, current_document_id=None, item=None, **properties):
    self.init_components(**properties)

    # Initialize dropdown options
    self.material_type_dropdown.items = ["Main Fabric", "Secondary Fabric", "Accessory"]
    self.dropdown_supplier.items = ["Puma", "Nike", "Uniqlo", "Adidas"]
    self.country_of_origin_dropdown.items = ["Vietnam", "China"]
    self.UOM_dropdown.items = ["Meter", "Piece"]
    self.weight_uom_dropdown.items = ["GSM (gram/sq meter)", "GPP (gram/piece)"]
    self.currency_dropdown.items = ["USD", "VND", "RMB"]
    self.vietnam_vat_rate_dropdown.items = ["N/A", "8", "10"]
    self.shipping_term_dropdown.items = ["EXW (Ex Works)", "FOB (Free On Board)", "DDP (Delivered Duty Paid)"]
    self.material_dropdown.items = ["Cotton", "Polyester", "Silk", "Wool", "Elastane"]
    # Initialize fabric composition
    self.composition_list = []
    self.fabric_composition_repeating_panel.items = self.composition_list
    self.fabric_composition_repeating_panel.update_total = self.update_total_percentage

    # Advanced cost section starts hidden
    self.details_section.visible = False
    self.advanced_cost_dropdown.items = ["Advanced Cost Calculation"]

    # Initialize item and document ID
    self.item = {} if item is None else dict(item)
    self.current_document_id = current_document_id or self.item.get("document_id")

    # Normalize and configure
    self._normalize_item()
    self.mode = self._determine_mode()
    self._configure_buttons_for_mode()
    self._load_fabric_composition()
    self._set_dropdown_values()
    self.refresh_data_bindings()

    if not self.current_document_id or not self.item.get("vietnam_vat_rate"):
      self.vietnam_vat_rate_dropdown.selected_value = "N/A"
      
    # Trigger cost calculations if editing existing material
    if self.current_document_id and self.original_cost_per_unit.text:
      self.supplier_tolerance_change()

  # ========================================================================
  # INITIALIZATION HELPERS
  # ========================================================================

  def _normalize_item(self):
    """Normalize item data and set defaults"""
    if not isinstance(self.item, dict):
      self.item = {}

    # Convert VAT to string if it's a number
    vat = self.item.get("vietnam_vat_rate")
    if isinstance(vat, (int, float)):
      self.item["vietnam_vat_rate"] = str(int(vat))
    elif vat is None:
      self.item["vietnam_vat_rate"] = "N/A" 

    # Set refundable checkboxes
    self.refundable_tolerance.checked = bool(self.item.get("refundable_tolerance", False))
    self.refundable_vat.checked = bool(self.item.get("refundable_vat", False))
    self.refundable_import_duty.checked = bool(self.item.get("refundable_import_duty", False))

    # Ensure all expected fields exist with defaults
    defaults = {
      "material_name": self.item.get("name", ""),
      "master_material_id": "",
      "ref_id": "",
      "fabric_composition": [],
      "fabric_roll_width": "",
      "fabric_cut_width": "",
      "fabric_cut_width_no_shrinkage": "",
      "generic_material_size": "",
      "weft_shrinkage": "",
      "werp_shrinkage": "",
      "weight_per_unit": "",
      "original_cost_per_unit": "",
      "supplier_selling_tolerance": "",
      "import_duty": "",
      "logistics_rate": "",
      "description_box": self.item.get("change_description", ""),
      "effective_cost_per_unit": "",
      "logistics_fee_per_unit": "",
      "landed_cost_per_unit": "",
    }

    for key, default_value in defaults.items():
      self.item.setdefault(key, self.item.get(key, default_value))

    self._update_currency_labels(self.item.get("native_cost_currency"))

  def _determine_mode(self):
    """Determine form mode based on current status"""
    if not self.current_document_id:
      return "new"

    current_status = self.item.get("verification_status") or self.item.get("status")

    if current_status == "Submitted - Verified":
      return "edit_verified"
    elif current_status in ["Draft", "Submitted - Unverified"]:
      return "edit_draft"
    else:
      return "new"

  def _configure_buttons_for_mode(self):
    """Configure button visibility based on mode"""
    if self.mode == "edit_verified":
      self.save_as_draft_btn.visible = False
      self.submit_btn.visible = True
      self.submit_btn.text = "Submit New Version"
    elif self.mode == "edit_draft":
      self.save_as_draft_btn.visible = True
      self.submit_btn.visible = True
      self.submit_btn.text = "Submit"
    else:  # new
      self.save_as_draft_btn.visible = True
      self.submit_btn.visible = True
      self.submit_btn.text = "Submit"

  def _set_dropdown_values(self):
    """Set dropdown selected values from item data"""
    def safe_set_selected(dropdown, value):
      if value and value in dropdown.items:
        dropdown.selected_value = value

    safe_set_selected(self.dropdown_supplier, self.item.get("supplier_name"))
    safe_set_selected(self.material_type_dropdown, self.item.get("material_type"))
    safe_set_selected(self.country_of_origin_dropdown, self.item.get("country_of_origin"))
    safe_set_selected(self.UOM_dropdown, self.item.get("unit_of_measurement"))
    safe_set_selected(self.weight_uom_dropdown, self.item.get("weight_uom"))
    safe_set_selected(self.currency_dropdown, self.item.get("native_cost_currency"))
    safe_set_selected(self.shipping_term_dropdown, self.item.get("shipping_term"))

    vat_value = self.item.get("vietnam_vat_rate")
    if vat_value and str(vat_value) in self.vietnam_vat_rate_dropdown.items:
      self.vietnam_vat_rate_dropdown.selected_value = str(vat_value)

  def _load_fabric_composition(self):
    """Parse and load fabric composition data"""
    fabric_comp = self.item.get("fabric_composition", "")

    # Already a list (new material)
    if isinstance(fabric_comp, list):
      self.composition_list = fabric_comp
      self.fabric_composition_repeating_panel.items = self.composition_list
      self.update_total_percentage()
      return

    # Parse string format: "Cotton:50%|Polyester:50%"
    if isinstance(fabric_comp, str) and fabric_comp.strip():
      try:
        parts = fabric_comp.split("|")
        for part in parts:
          if ":" in part:
            material, percent_str = part.split(":", 1)
            percent_str = percent_str.strip().replace("%", "")
            percentage = float(percent_str)

            self.composition_list.append({
              "material": material.strip(),
              "percentage": percentage,
              "form": self
            })

        self.fabric_composition_repeating_panel.items = self.composition_list
        self.update_total_percentage()

      except Exception as e:
        print(f"Error parsing fabric composition: {e}")
        self.composition_list = []
        self.fabric_composition_repeating_panel.items = []

  # ========================================================================
  # FABRIC COMPOSITION MANAGEMENT
  # ========================================================================

  def add_btn_click(self, **event_args):
    """Add material to composition list"""
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

    # Add to list
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
    """Update total percentage display and control input availability"""
    total = sum([float(item['percentage']) for item in self.composition_list if item['percentage']])
    self.total_percentage.text = f"Total: {total} %"

    remaining = 100 - total

    # Disable input when 100% reached
    if remaining <= 0:
      self.material_dropdown.enabled = False
      self.percentage.enabled = False
      self.add_btn.enabled = False
      self.percentage.placeholder = "100% reached"
    else:
      self.material_dropdown.enabled = True
      self.percentage.enabled = True
      self.add_btn.enabled = True
      self.percentage.placeholder = f"Max {remaining}% allowed"

  # ========================================================================
  # COST CALCULATIONS
  # ========================================================================

  def advanced_cost_dropdown_change(self, **event_args):
    """Show/hide advanced cost calculation section"""
    self.details_section.visible = (
      self.advanced_cost_dropdown.selected_value == "Advanced Cost Calculation"
    )

  def currency_dropdown_change(self, **event_args):
    self._update_currency_labels(self.currency_dropdown.selected_value)

  def _update_currency_labels(self, currency):
    """Update all cost-related currency labels"""
    labels = [
      self.original_cost_unit,
      self.supplier_tolerance_cost_unit,
      self.effective_cost_unit,
      self.landed_cost_unit,
      self.logistics_unit_cost
    ]
    for label in labels:
      label.text = currency or ""

  def original_cost_per_unit_change(self, **event_args):
    if(self.original_cost_per_unit.text is not None):
      self.original_cost.text = self.original_cost_per_unit.text

  def supplier_tolerance_change(self, **event_args):
    """Calculate effective cost based on tolerance"""
    original_cost = float(self.original_cost_per_unit.text or 0)
    supplier_tolerance_percentage = float(self.supplier_tolerance.text or 0)

    supplier_tolerance_cost = (supplier_tolerance_percentage / 100) * original_cost
    self.supplier_tolerance_cost.text = str(supplier_tolerance_cost)

    effective_cost = original_cost + supplier_tolerance_cost
    self.effective_cost_per_unit.text = str(effective_cost)

  def logistics_rate_change(self, **event_args):
    """Calculate landed cost based on logistics rate"""
    logistics_rate = float(self.logistics_rate.text or 0)
    effective_cost = float(self.effective_cost_per_unit.text or 0)

    landed_cost = ((logistics_rate / 100) * effective_cost) + effective_cost
    self.landed_cost.text = str(landed_cost)

    weight_per_unit = float(self.weight_per_unit.text or 0)
    logistics_fee_per_unit = weight_per_unit * logistics_rate
    self.logistics_fee_per_unit.text = str(logistics_fee_per_unit)

  # ========================================================================
  # FORM ACTIONS
  # ========================================================================

  def close_btn_click(self, **event_args):
    """Close the form"""
    self.raise_event("x-close-alert")

  def cancel_btn_click(self, **event_args):
    """Cancel and close the form"""
    self.close_btn_click()

  def _current_user_name(self):
    """Get current user's name/email"""
    user = anvil.users.get_user() or anvil.users.login_with_form()
    return user['email'] if user else "Unknown"

  def save_as_draft_btn_click(self, **event_args):
    """Save material as draft"""
    form_data = self.collect_form_data()
    try:
      user_name = self._current_user_name()

      if not self.current_document_id:
        # New material
        resp = anvil.server.call('create_material', user_name, form_data)
      else:
        # Edit existing draft
        resp = anvil.server.call('save_or_edit_draft', self.current_document_id, form_data)

      self.current_document_id = resp.get('document_id') or self.current_document_id
      Notification("Draft saved!", style="success", timeout=3).show()
      self.raise_event("x-refresh-list", document_id=self.current_document_id)
      self.raise_event("x-close-alert", value="saved")
      
    except Exception as e:
      Notification(f"Error: {e}", style="danger", timeout=3).show()

  def submit_btn_click(self, **event_args):
    """Submit material for verification"""
    form_data = self.collect_form_data()

    if not self.validate_form_data(form_data):
      Notification("Please fill in all required fields!", style="warning", timeout=3).show()
      return

    self.submit_btn.enabled = False
    self.submit_btn.text = "Submitting..."

    try:
      user_name = self._current_user_name()

      if self.mode == "edit_verified":
        # Create new version for verified material
        resp = anvil.server.call(
          'edit_verified_and_submit',
          document_id=self.current_document_id,
          edited_by_user=user_name,
          form_data=form_data,
          notes=form_data.get('change_description', 'Edited via UI')
        )
        self.current_document_id = resp.get('document_id') or self.current_document_id
        success_msg = f"New version {resp.get('new_version_number')} created and submitted."


      elif self.mode == "edit_draft":
        # Submit existing draft
        resp = anvil.server.call('submit_version', self.current_document_id, user_name, form_data)
        self.current_document_id = resp.get('document_id') or self.current_document_id
        success_msg = "Submitted successfully!"


      else:  # new
        # Create and submit new material
        resp = anvil.server.call('create_and_submit_material', user_name, form_data)
        self.current_document_id = resp.get('document_id') or self.current_document_id
        success_msg = "Material created and submitted!"

      Notification(success_msg, style="success", timeout=3).show()
      self.raise_event("x-refresh-list", document_id=self.current_document_id)
      self.raise_event("x-close-alert", value="saved")

    except Exception as e:
      Notification(f"Error: {e}", style="danger", timeout=5).show()
    finally:
      self.submit_btn.enabled = True
      self.submit_btn.text = "Submit New Version" if self.mode == "edit_verified" else "Submit"

  # ========================================================================
  # DATA VALIDATION & COLLECTION
  # ========================================================================

  def validate_form_data(self, form_data):
    """Validate required fields"""
    required_fields = [
      'name', 'material_type', 'country_of_origin', 'supplier_name',
      'unit_of_measurement', 'weight_per_unit', 'weight_uom',
      'original_cost_per_unit', 'native_cost_currency'
    ]

    for field in required_fields:
      if not form_data.get(field):
        print(f"Missing required field: {field}")
        return False

    # Validate composition totals 100%
    if self.composition_list:
      total = sum([float(item['percentage']) for item in self.composition_list])
      if total != 100:
        Notification(f"Composition must total 100% (currently {total}%)", style="warning").show()
        return False

    return True

  def collect_form_data(self):
    """Collect all form data into a dictionary"""
    # Handle VAT special case
    vat_value = self.vietnam_vat_rate_dropdown.selected_value
    vat_number = None if vat_value == "N/A" else self.parse_float(vat_value)

    return {
      # Basic Info
      "master_material_id": self.mat_material_id.text,
      "name": self.material_name.text,
      "material_type": self.material_type_dropdown.selected_value,
      "country_of_origin": self.country_of_origin_dropdown.selected_value,
      "supplier_name": self.dropdown_supplier.selected_value,
      "ref_id": self.supplier_reference_id.text,
      "unit_of_measurement": self.UOM_dropdown.selected_value,

      # Technical Specs
      "fabric_roll_width": self.parse_float(self.fabric_roll_width.text),
      "fabric_cut_width": self.parse_float(self.fabric_cut_width.text),
      "fabric_cut_width_no_shrinkage": self.parse_float(self.fabric_cut_width_no_shrinkage.text),
      "weight_per_unit": self.parse_float(self.weight_per_unit.text),
      "weight_uom": self.weight_uom_dropdown.selected_value,
      "weft_shrinkage": self.parse_float(self.weft_shrinkage.text),
      "werp_shrinkage": self.parse_float(self.werp_shrinkage.text),
      "generic_material_size": self.generic_material_size.text,
      "fabric_composition": "|".join([
        f"{item['material']}:{item['percentage']}%" 
        for item in self.composition_list
      ]),

      # Costs
      "original_cost_per_unit": self.parse_float(self.original_cost_per_unit.text),
      "native_cost_currency": self.currency_dropdown.selected_value,
      "supplier_selling_tolerance": self.parse_float(self.supplier_tolerance.text),
      "refundable_tolerance": self.refundable_tolerance.checked,
      "effective_cost_per_unit": self.parse_float(self.effective_cost_per_unit.text),
      "vietnam_vat_rate": vat_number,
      "refundable_vat": self.refundable_vat.checked,
      "import_duty": self.parse_float(self.import_duty.text),
      "refundable_import_duty": self.refundable_import_duty.checked,
      "shipping_term": self.shipping_term_dropdown.selected_value,
      "logistics_rate": self.parse_float(self.logistics_rate.text),
      "logistics_fee_per_unit": self.parse_float(self.logistics_fee_per_unit.text),
      "landed_cost_per_unit": self.parse_float(self.landed_cost.text),
      "change_description": self.description_box.text,
    }

  def parse_float(self, value):
    """Safely parse float values"""
    try:
      return float(value) if value else None
    except (ValueError, TypeError):
      return None