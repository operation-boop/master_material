from ._anvil_designer import Material_input_formTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Material_input_form(Material_input_formTemplate):
  def __init__(self, current_document_id=None, item=None, **properties):
    self.init_components(**properties)

    self.material_type_dropdown.items = ["Main Fabric", "Secondary Fabric", "Accessory"]
    self.dropdown_supplier.items = ["ABC", "CBA", "HELLO", "BYE"]
    self.country_of_origin_dropdown.items = ["Vietnam", "China"]
    self.UOM_dropdown.items = ["Meter", "Piece"]
    self.weight_uom_dropdown.items = ["GSM (gram/sq meter)", "GPP (gram/piece)"]
    self.currency_dropdown.items = ["USD", "VND", "RMB"]
    self.vietnam_vat_rate_dropdown.items = ["N/A", "8", "10"]
    self.shipping_term_dropdown.items = ["EXW (Ex Works)", "FOB (Free On Board)", "DDP (Delivered Duty Paid)"]
    self.vietnam_vat_rate_dropdown.selected_value = "N/A"

    self.composition_list = []
    self.material_dropdown.items = ["Cotton", "Polyester", "Silk", "Wool", "Elastane"]
    self.fabric_composition_repeating_panel.items = self.composition_list
    self.fabric_composition_repeating_panel.update_total = self.update_total_percentage

    self.details_section.visible = False
    self.advanced_cost_dropdown.items = ["Advanced Cost Calculation"]

    self.refundable_tolerance.checked = bool(self.item.get("refundable_tolerance",False))
    self.refundable_vat.checked = bool(self.item.get("refundable_vat",False))
    self.refundable_import_duty.checked = bool(self.item.get("refundable_import_duty",False))

    self.item = {} if item is None else dict(item)
    self.current_document_id = current_document_id or (item or {}).get("document_id")
    self._normalize_item()

    self.mode = self._determine_mode()
    self._configure_buttons_for_mode()
    self._load_fabric_composition()
    def safe_set_selected(dropdown, value):
      try:
        if value is not None and value != "" and value in getattr(dropdown, "items", []):
          dropdown.selected_value = value
      except Exception:
        pass

    safe_set_selected(self.dropdown_supplier, self.item.get("supplier_name"))
    safe_set_selected(self.material_type_dropdown, self.item.get("material_type"))
    safe_set_selected(self.country_of_origin_dropdown, self.item.get("country_of_origin"))
    safe_set_selected(self.UOM_dropdown, self.item.get("unit_of_measurement"))
    safe_set_selected(self.weight_uom_dropdown, self.item.get("weight_uom"))
    safe_set_selected(self.currency_dropdown, self.item.get("native_cost_currency"))
    safe_set_selected(self.vietnam_vat_rate_dropdown, self.item.get("vietnam_vat_rate"))
    safe_set_selected(self.shipping_term_dropdown, self.item.get("shipping_term"))

    self.refresh_data_bindings()
    if self.current_document_id and self.original_cost_per_unit.text:
      self.supplier_tolerance_change()
  def _normalize_item(self):
    if not isinstance(self.item, dict):
      self.item = {}

    vat = self.item.get("vietnam_vat_rate")
    if isinstance(vat, (int, float)):
      self.item["vietnam_vat_rate"] = str(int(vat))

    self.item.setdefault("material_name", self.item.get("name", ""))
    self.item.setdefault("master_material_id", self.item.get("master_material_id", ""))
    self.item.setdefault("ref_id", self.item.get("ref_id", ""))
    self.item.setdefault("fabric_composition", self.item.get("fabric_composition", []))
    self.item.setdefault("fabric_roll_width", self.item.get("fabric_roll_width", ""))
    self.item.setdefault("fabric_cut_width", self.item.get("fabric_cut_width", ""))
    self.item.setdefault("fabric_cut_width_no_shrinkage", self.item.get("fabric_cut_width_no_shrinkage", ""))
    self.item.setdefault("generic_material_size", self.item.get("generic_material_size", ""))
    self.item.setdefault("weft_shrinkage", self.item.get("weft_shrinkage", ""))
    self.item.setdefault("werp_shrinkage", self.item.get("werp_shrinkage", ""))
    self.item.setdefault("weight_per_unit", self.item.get("weight_per_unit", ""))
    self.item.setdefault("original_cost_per_unit", self.item.get("original_cost_per_unit"))
    self.item.setdefault("supplier_selling_tolerance", self.item.get("supplier_selling_tolerance", ""))
    self.item.setdefault("import_duty", self.item.get("import_duty", ""))
    self.item.setdefault("logistics_rate",self.item.get("logistics_rate", ""))
    self.item.setdefault("description_box",self.item.get("change_description",""))
    self.item.setdefault("effective_cost_per_unit",self.item.get("effective_cost_per_unit", ""))
    self.item.setdefault("logistics_fee_per_unit",self.item.get("logistics_fee_per_unit",""))
    self.item.setdefault("landed_cost_per_unit",self.item.get("landed_cost_per_unit",""))
    self._update_currency_labels(self.item.get("native_cost_currency"))
  def _determine_mode(self):
    """Determine what mode the form is in based on current status"""
    if not self.current_document_id:
      return "new"  # Creating new material

    # Get current status
    current_status = self.item.get("verification_status") or self.item.get("status")

    if current_status == "Submitted - Verified":
      return "edit_verified"  # Editing verified material
    elif current_status in ["Draft", "Creating", "Submitted - Unverified"]:
      return "edit_draft"  # Editing draft or unverified
    else:
      return "new"
  def _configure_buttons_for_mode(self):
    """Show/hide buttons based on mode"""
    if self.mode == "edit_verified":
      # Editing verified material - only show Submit button
      self.save_as_draft_btn.visible = False
      self.submit_btn.visible = True
      self.submit_btn.text = "Submit New Version"
    elif self.mode == "edit_draft":
      # Editing draft - show both buttons
      self.save_as_draft_btn.visible = True
      self.submit_btn.visible = True
      self.submit_btn.text = "Submit"
    else:
      # New material - show both buttons
      self.save_as_draft_btn.visible = True
      self.submit_btn.visible = True
      self.submit_btn.text = "Submit"
  def _load_fabric_composition(self):
    """Parse fabric composition string and populate the repeating panel"""
    fabric_comp = self.item.get("fabric_composition", "")

    # If it's already a list (new material), use it as-is
    if isinstance(fabric_comp, list):
      self.composition_list = fabric_comp
      self.fabric_composition_repeating_panel.items = self.composition_list
      self.update_total_percentage()
      return

      # If it's a string, parse it
    if isinstance(fabric_comp, str) and fabric_comp.strip():
      try:
        # Parse "Cotton:50%|Polyester:50%" format
        parts = fabric_comp.split("|")
        for part in parts:
          if ":" in part:
            material, percent_str = part.split(":", 1)
            # Remove the % sign and convert to float
            percent_str = percent_str.strip().replace("%", "")
            percentage = float(percent_str)

            self.composition_list.append({
              "material": material.strip(),
              "percentage": percentage,
              "form": self
            })

            # Update the repeating panel
        self.fabric_composition_repeating_panel.items = self.composition_list
        self.update_total_percentage()

      except Exception as e:
        print(f"Error parsing fabric composition: {e}")
        self.composition_list = []
        self.fabric_composition_repeating_panel.items = []

  ##------------Calculate cost prices & UI for costing----------------------------
  def advanced_cost_dropdown_change(self, **event_args):
    # Show the section only if a value is selected (not None or blank)
    if self.advanced_cost_dropdown.selected_value == "Advanced Cost Calculation":
      self.details_section.visible = True
    else:
      self.details_section.visible = False

  def currency_dropdown_change(self, **event_args):
    self._update_currency_labels(self.currency_dropdown.selected_value)

  def _update_currency_labels(self, currency):
    for label in [
      self.original_cost_unit,
      self.supplier_tolerance_cost_unit,
      self.effective_cost_unit,
      self.landed_cost_unit,
      self.logistics_unit_cost
    ]:
      label.text = currency or ""

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

  def supplier_tolerance_change(self, **event_args):
    original_cost = float(self.original_cost_per_unit.text or 0)
    supplier_tolerance_percentage = float(self.supplier_tolerance.text or 0)

    supplier_tolerance_cost = (supplier_tolerance_percentage / 100) * original_cost
    self.supplier_tolerance_cost.text = str(supplier_tolerance_cost)

    effective_cost = original_cost + supplier_tolerance_cost
    self.effective_cost_per_unit.text = str(effective_cost)

  def original_cost_per_unit_change(self, **event_args):
    if(self.original_cost_per_unit.text is not None):
      self.original_cost.text = self.original_cost_per_unit.text

  def logistics_rate_change(self, **event_args):
    logistics_rate = float(self.logistics_rate.text or 0)
    effective_cost = float(self.effective_cost_per_unit.text or 0)   # ✅ FIXED HERE
    landed_cost = ((logistics_rate / 100) * effective_cost) + effective_cost
    self.landed_cost.text = str(landed_cost)
    weight_per_unit = float(self.weight_per_unit.text or 0)
    logistics_fee_per_unit = weight_per_unit * logistics_rate
    self.logistics_fee_per_unit.text = str(logistics_fee_per_unit)

  ##------------------------buttons---------------------------------------
  def close_btn_click(self, **event_args):
    self.raise_event("x-close-alert")
  def cancel_btn_click(self, **event_args):
    self.close_btn_click()
    
  def _current_user_name(self):
    user = anvil.users.get_user() or anvil.users.login_with_form()
    return user['email'] if user else "Unknown"

  def save_as_draft_btn_click(self, **event_args):
    """Save as draft - only for new materials or editing drafts"""
    form_data = self.collect_form_data()
    try:
      user_name = self._current_user_name()

      if not self.current_document_id:
        # New material - create it
        resp = anvil.server.call('create_material', user_name, form_data)
      else:
        # Editing draft
        resp = anvil.server.call('save_or_edit_draft', self.current_document_id, user_name, form_data)

      self.current_document_id = resp.get('document_id') or self.current_document_id
      Notification("Draft saved!", style="success", timeout=3).show()
      self.raise_event("x-refresh-list", document_id=self.current_document_id)
      self.raise_event("x-close-alert", value="saved")
    except Exception as e:
      Notification(f"Error: {e}", style="danger", timeout=3).show()

  def submit_btn_click(self, **event_args):
    """Submit material - handles all cases: new, edit draft, edit verified"""
    form_data = self.collect_form_data()
  
    if not self.validate_form_data(form_data):
      Notification("Please fill in all required fields!", style="warning", timeout=3).show()
      return
  
    self.submit_btn.enabled = False
    self.submit_btn.text = "Submitting..."
  
    try:
      user_name = self._current_user_name()
  
      mode = getattr(self, 'mode', 'new')  # Get mode safely
  
      if mode == "edit_verified":
        # Editing verified material - create new version as Submitted - Unverified
        resp = anvil.server.call(
          'edit_verified_and_submit',
          document_id=self.current_document_id,
          edited_by_user=user_name,
          form_data=form_data,
          notes=form_data.get('change_description', 'Edited via UI')
        )
        self.current_document_id = resp.get('document_id') or self.current_document_id
        success_msg = f"New version {resp.get('new_version_number')} created and submitted for verification."
        result_token = "edited_and_resubmitted"
  
      elif mode == "edit_draft":
        # Editing draft or unverified - submit it
        resp = anvil.server.call('submit_version', self.current_document_id, user_name, form_data)
        self.current_document_id = resp.get('document_id') or self.current_document_id
        success_msg = "Submitted successfully!"
        result_token = "submitted"
  
      else:
        # New material - create and submit
        resp = anvil.server.call('create_and_submit_material', user_name, form_data)
        self.current_document_id = resp.get('document_id') or self.current_document_id
        success_msg = "Material created and submitted!"
        result_token = "submitted"
  
      Notification(success_msg, style="success", timeout=3).show()
      self.raise_event("x-refresh-list", document_id=self.current_document_id)
      self.raise_event("x-close-alert", value=result_token)
  
    except Exception as e:
      Notification(f"Error: {e}", style="danger", timeout=5).show()
    finally:
      self.submit_btn.enabled = True
      # Use getattr to safely get mode
      mode = getattr(self, 'mode', 'new')
      self.submit_btn.text = "Submit New Version" if mode == "edit_verified" else "Submit"

  ##-----------------validations + data collections------------------------
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
    vat_value = self.vietnam_vat_rate_dropdown.selected_value
    if vat_value == "N/A":
      vat_number = None
    else:
      vat_number = self.parse_float(vat_value)


    return {
      # Basic Info
      "master_material_id": self.mat_material_id.text,
      "name": self.material_name.text if hasattr(self, 'material_name') else None,
      "material_type": self.material_type_dropdown.selected_value,
      "country_of_origin": self.country_of_origin_dropdown.selected_value,
      "supplier_name" : self.dropdown_supplier.selected_value,
      "ref_id" : self.supplier_reference_id.text,
      "unit_of_measurement": self.UOM_dropdown.selected_value,
      "fabric_roll_width": self.parse_float(self.fabric_roll_width.text) if hasattr(self, 'fabric_roll_width') else None,
      "fabric_cut_width": self.parse_float(self.fabric_cut_width.text) if hasattr(self, 'fabric_cut_width') else None,
      "fabric_cut_width_no_shrinkage": self.parse_float(self.fabric_cut_width_no_shrinkage.text) if hasattr(self, 'fabric_cut_width_no_shrinkage') else None,
      "weight_per_unit": self.parse_float(self.weight_per_unit.text) if hasattr(self, 'weight_per_unit') else None,
      "weight_uom": self.weight_uom_dropdown.selected_value,
      "weft_shrinkage": self.parse_float(self.weft_shrinkage.text) if hasattr(self, 'weft_shrinkage') else None,
      "werp_shrinkage": self.parse_float(self.werp_shrinkage.text) if hasattr(self, 'werp_shrinkage') else None,
      "generic_material_size": self.generic_material_size.text,
      "fabric_composition": "|".join([f"{item['material']}:{item['percentage']}%" for item in self.composition_list]),

      # Costs
      "original_cost_per_unit": self.parse_float(self.original_cost_per_unit.text) if hasattr(self, 'original_cost_per_unit') else None,
      "native_cost_currency": self.currency_dropdown.selected_value,
      "supplier_selling_tolerance": self.parse_float(self.supplier_tolerance.text) if hasattr(self, 'supplier_tolerance') else None,
      "refundable_tolerance": self.refundable_tolerance.checked if hasattr(self, 'refundable_tolerance') else False,
      "effective_cost_per_unit": self.parse_float(self.effective_cost_per_unit.text) if hasattr(self, 'effective_cost_per_unit') else None,
      "vietnam_vat_rate": vat_number,
      "refundable_vat": self.refundable_vat.checked if hasattr(self, 'refundable_vat') else False,
      "import_duty": self.parse_float(self.import_duty.text) if hasattr(self, 'import_duty') else None,
      "refundable_import_duty": self.refundable_import_duty.checked if hasattr(self,'refundable_import_duty') else False,
      "shipping_term": self.shipping_term_dropdown.selected_value,
      "logistics_rate": self.parse_float(self.logistics_rate.text) if hasattr(self, 'logistics_rate') else None,
      "logistics_fee_per_unit": self.parse_float(self.logistics_fee_per_unit.text) if hasattr(self, 'logistics_fee_per_unit') else None,
      "landed_cost_per_unit": self.parse_float(self.landed_cost.text) if hasattr(self, 'landed_cost') else None,
      "change_description":self.description_box.text,
    }

  def parse_float(self, value):
    """Helper to safely parse float values"""
    try:
      return float(value) if value else None
    except (ValueError, TypeError):
      return None