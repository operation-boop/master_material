from ._anvil_designer import Material_detailTemplate
import anvil.server
from anvil import alert, Notification, open_form
from ..Material_input_form import Material_input_form
from ..Material_sku_input_form import Material_sku_input_form


# class Material_detail(Material_detailTemplate):
#   def __init__(self, doc_id=None, **properties):
#     self.init_components(**properties)
#     self.item = {} 
#     self.refresh_data_bindings()
#     if doc_id:
#       self.load_material(doc_id)
#       self.refresh_data()
#     self.set_verification_status(self.item['verification_status'].lower())

#   def form_show(self, **event_args):
#     doc_id = self.item.get("document_id")  # if passed from previous form
#     if doc_id:
#       self.load_material(doc_id)
  
#   def load_material(self, document_id):
#     detail = anvil.server.call("get_material_detail", document_id)
  
#     self.ver_num.text = detail["ver_num"]
#     self.material_id.text = detail["master_material_id"]
#     self.txt_country.text = detail["country_of_origin"]
#     self.txt_cost.text = detail["original_cost_per_unit"]
#     self.txt_weight.text = detail["weight"]
#     self.lbl_version.text = f"v{detail['ver_num']}"
#     """Load material when form is shown"""
#     doc_id = self.item.get("document_id")
#     if doc_id:
#       self.load_material(doc_id)

#   def load_material(self, document_id):
#     """Load material basic details"""
#     detail = anvil.server.call("get_material_detail", document_id)
#     self.item = dict(detail)
#     self.refresh_data_bindings()

#   # ========================================================================
#   # TAB NAVIGATION
#   # ========================================================================

#   def technical_specs_tab_btn_click(self, **event_args):
#     """Show technical specifications panel"""
#     self.technical_specs_panel.visible = True
#     self.cost_details_panel.visible = False
#     self.version_history_panel.visible = False
#     self.material_sku_panel.visible = False

#     doc_id = self.item.get("document_id")
#     if not doc_id:
#       alert("No document ID found!")
#       return

# "document_id": _get(v, "document_id"),
# "ver_num": _get(v, "ver_num"),
# "material_id": _get(v, "master_material_id"),
# "ref_id": _get(v, "ref_id", ""),
# "material_name": _get(v, "name", ""),
# "material_type": _get(v, "material_type", ""),
# "supplier": _get(v, "supplier_name", ""),
# "country_of_origin": _get(v, "country_of_origin", ""),
# "created_by": _get(v, "created_by", ""),
# "created_at": _get(v, "created_at"),
# "fabric_composition": _get(v, "fabric_composition") or _get(v, "generic_material_composition", ""),
# "weight": weight,
# "fabric_roll_width": _get(v, "fabric_roll_width"),
# "fabric_cut_width": _get(v, "fabric_cut_width"),
# "original_cost_per_unit": ocpu,
# "cost_display": cost_display,
# "unit_of_measurement": _get(v, "unit_of_measurement") or wuom,
# "verification_status": _get(v, "status", "Draft"),
# "updated_at": _get(v, "updated_at"),
# "submitted_at": _get(v, "submitted_at"),
# "last_verified_date": _get(v, "last_verified_date"),

 

  


    
#     technical_detail = anvil.server.call("get_technical_detail", doc_id)
#     self.item.update(technical_detail)
#     self.item = dict(self.item)
#     self.refresh_data_bindings()

#   def cost_details_tab_btn_click(self, **event_args):
#     """Show cost details panel"""
#     self.cost_details_panel.visible = True
#     self.technical_specs_panel.visible = False
#     self.version_history_panel.visible = False
#     self.material_sku_panel.visible = False

#     doc_id = self.item.get("document_id")
#     if not doc_id:
#       alert("No document ID found!")
#       return

#     cost_detail = anvil.server.call("get_cost_detail", doc_id)
#     self.item.update(cost_detail)
#     self.item = dict(self.item)
#     self.refresh_data_bindings()

#   def version_history_tab_btn_click(self, **event_args):
#     """Show version history panel"""
#     self.version_history_panel.visible = True
#     self.technical_specs_panel.visible = False
#     self.cost_details_panel.visible = False
#     self.material_sku_panel.visible = False

#     doc_id = self.item.get("document_id")
#     if not doc_id:
#       alert("No document ID found!")
#       return

#     history = anvil.server.call("get_version_history", doc_id)
#     self.repeating_panel_version_history.items = history

#   def material_sku_tab_btn_click(self, **event_args):
#     """Show material SKU panel"""
#     self.material_sku_panel.visible = True
#     self.version_history_panel.visible = False
#     self.cost_details_panel.visible = False
#     self.technical_specs_panel.visible = False
#     self.refresh_data()

#   # ========================================================================
#   # ACTIONS
#   # ========================================================================

#   def edit_btn_click(self, **event_args):
#     """Open edit form for current material"""
#     doc_id = self.item.get("document_id")
#     if not doc_id:
#       alert("No document ID available to edit.", title="Error")
#       return

#     # Get the full row data for editing
#     latest = anvil.server.call("get_material_full_row", doc_id) or {}

#     try:
#       input_form = Material_input_form(current_document_id=doc_id, item=dict(latest))

#       # Set event handler to refresh this form when changes are saved
#       input_form.set_event_handler("x-refresh-list", lambda **args: self.load_material(doc_id))

#       result = alert(content=input_form, title="Edit Material", large=True, buttons=None)

#       # Refresh if saved/submitted
#       if result in ("saved", "submitted", "edited_and_resubmitted"):
#         try:
#           self.load_material(doc_id)
#         except Exception:
#           pass
#         Notification("Material updated.", style="success").show()

#     except Exception as e:
#       Notification(f"Failed to open edit form: {e}", style="danger").show()

#   def back_btn_click(self, **event_args):
#     """Return to material list"""
#     open_form("Material_list")

#   def add_sku_btn_click(self, **event_args):
#     """Open form to add new SKU variant"""
#     doc_id = self.item.get("document_id")
#     if not doc_id:
#       alert("No document ID found!")
#       return

#     form = Material_sku_input_form(document_id=doc_id)
#     alert(form, large=True)

#     if getattr(form, "saved", False):
#       self.refresh_data()

#   def set_verification_status(self, status_value):
#     """
#     Sets the background color and text of the verification_status component
#     based on the status_value.
#     """
#     status = (status_value or "").lower()

#     if status == "submitted - verified":
#       self.verification_status.background = "lightgreen"
#       self.verification_status.text = "✓ Verified"
#     elif status == "submitted - unverified":
#       self.verification_status.background = "orange"
#       self.verification_status.text = "\u2717 Unverified"
#     elif status == "draft":
#       self.verification_status.background = "#c7c7c7"
#       self.verification_status.text = "📝 Draft"
#     else:
#       self.verification_status.background = "#ffffff"
#       self.verification_status.text = status.capitalize() if status else "Unknown"

      
#   def refresh_data(self):
#     """Reload SKU data from server"""
#     doc_id = self.item.get("document_id")
#     if not doc_id:
#       return

#     try:
#       self.material_sku_repeating_panel.items = anvil.server.call(
#         "get_material_sku",
#         doc_id
#       )
#     except Exception as e:
#       Notification(f"Error loading data: {e}").show():