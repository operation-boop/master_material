from ._anvil_designer import Material_detailTemplate
import anvil.server
from anvil import alert, Notification, open_form
from ..Material_input_form import Material_input_form

class Material_detail(Material_detailTemplate):
  def __init__(self, doc_id=None, **properties):
    self.init_components(**properties)
    self.item = {} 
    self.refresh_data_bindings()

    # If a doc id was provided, immediately load it
    if doc_id:
      self.load_material(doc_id)


  def form_show(self, **event_args):
    doc_id = self.item.get("document_id")  # if passed from previous form
    if doc_id:
      self.load_material(doc_id)
  
  def load_material(self, document_id):
    detail = anvil.server.call("get_material_detail", document_id)
    self.item = dict(detail)
    self.refresh_data_bindings()

  def technical_specs_tab_btn_click(self, document_id=None, **event_args):
    self.technical_specs_panel.visible = True
    self.cost_details_panel.visible = False
    self.version_history_panel.visible = False
    self.material_sku_panel.visible = False

    doc_id = document_id or (self.item or {}).get("document_id")

    if not doc_id:
      alert("No document ID found!")
      return

    technicaldetail = anvil.server.call("get_technical_detail", doc_id)
    self.item.update(technicaldetail)
    self.item = dict(self.item)
    self.refresh_data_bindings()

  def cost_details_tab_btn_click(self, document_id=None, **event_args):
    self.cost_details_panel.visible = True
    self.technical_specs_panel.visible = False
    self.version_history_panel.visible = False
    self.material_sku_panel.visible = False

    doc_id = document_id or (self.item or {}).get("document_id")

    if not doc_id:
      alert("No document ID found!")
      return

    costdetail = anvil.server.call("get_cost_detail", doc_id)
    self.item.update(costdetail)
    self.item = dict(self.item)
    self.refresh_data_bindings()
    pass
    
  def edit_btn_click(self, **event_args):
    """Simple: fetch the latest version for this document_id and open the edit form."""
    # get document id
    doc_id = (self.item or {}).get("document_id") or getattr(self, "current_document_id", None)
    if not doc_id:
      alert("No document ID available to edit.", title="Error")
      return

    # fetch the latest data from the server (get_material_detail selects latest ver_num)
    try:
      latest = anvil.server.call("get_material_detail", doc_id) or {}
    except Exception as e:
      Notification(f"Failed to load material: {e}", style="danger").show()
      return

    # open input form with the fresh, latest data
    try:
      input_form = Material_input_form(current_document_id=doc_id, item=dict(latest))
    except Exception as e:
      Notification(f"Failed to open edit form: {e}", style="danger").show()
      return

    result = alert(content=input_form, large=True)

    # if saved/submitted, reload and refresh list
    if result in ("saved", "submitted", "edited"):
      try:
        self.load_material(doc_id)
      except Exception:
        pass
      try:
        main = open_form("Material_list")
        if main is not None:
          if hasattr(main, "refresh_materials"):
            main.refresh_materials()
          elif hasattr(main, "load_material_cards"):
            main.load_material_cards()
      except Exception:
        pass
      Notification("Material updated.", style="success").show()



  





 

  


    