from ._anvil_designer import Material_detailTemplate
from anvil import alert
import anvil.server


class Material_detail(Material_detailTemplate):
  def __init__(self, doc_id=None, **properties):
    self.init_components(**properties)
    self.doc_id = doc_id

    # Optional: show/hide loading UI element if you have one
    try:
      self.loading_spinner.visible = True
    except Exception:
      pass

  def form_show(self, **event_args):
    doc_id = self.item.get("document_id")  # if passed from previous form
    if doc_id:
      self.load_material(doc_id)
  
  def load_material(self, document_id):
    detail = anvil.server.call("get_material_detail", document_id)
  
    self.ver_num.text = detail["ver_num"]
    self.material_id.text = detail["master_material_id"]
    self.txt_country.text = detail["country_of_origin"]
    self.txt_cost.text = detail["original_cost_per_unit"]
    self.txt_weight.text = detail["weight"]
    self.lbl_version.text = f"v{detail['ver_num']}"

"document_id": _get(v, "document_id"),
"ver_num": _get(v, "ver_num"),
"material_id": _get(v, "master_material_id"),
"ref_id": _get(v, "ref_id", ""),
"material_name": _get(v, "name", ""),
"material_type": _get(v, "material_type", ""),
"supplier": _get(v, "supplier_name", ""),
"country_of_origin": _get(v, "country_of_origin", ""),
"created_by": _get(v, "created_by", ""),
"created_at": _get(v, "created_at"),
"fabric_composition": _get(v, "fabric_composition") or _get(v, "generic_material_composition", ""),
"weight": weight,
"fabric_roll_width": _get(v, "fabric_roll_width"),
"fabric_cut_width": _get(v, "fabric_cut_width"),
"original_cost_per_unit": ocpu,
"cost_display": cost_display,
"unit_of_measurement": _get(v, "unit_of_measurement") or wuom,
"verification_status": _get(v, "status", "Draft"),
"updated_at": _get(v, "updated_at"),
"submitted_at": _get(v, "submitted_at"),
"last_verified_date": _get(v, "last_verified_date"),

 

  


    