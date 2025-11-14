from ._anvil_designer import Material_detailTemplate
import anvil.server
from anvil import alert, Notification, open_form
from ..Material_input_form import Material_input_form

class Material_detail(Material_detailTemplate):
  def __init__(self, doc_id=None, **properties):
    self.init_components(**properties)
    self.item = {} 
    self.refresh_data_bindings()
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
    doc_id = (self.item or {}).get("document_id") or getattr(self, "current_document_id", None)
    if not doc_id:
      alert("No document ID available to edit.", title="Error")
      return

    # Get the full row data
    latest = anvil.server.call("get_material_full_row", doc_id) or {}
  
    try:
      input_form = Material_input_form(current_document_id=doc_id, item=dict(latest))
    
      # Set event handler for refresh
      input_form.set_event_handler("x-refresh-list", lambda **args: self.load_material(doc_id))
    
      result = alert(content=input_form, title="Edit Material", large=True, buttons=None)
    
      # Refresh if saved/submitted
      if result in ("saved", "submitted", "edited_and_resubmitted"):
        try:
          self.load_material(doc_id)
        except Exception:
          pass
        Notification("Material updated.", style="success").show()
    
    except Exception as e:
      Notification(f"Failed to open edit form: {e}", style="danger").show()

  def version_history_tab_btn_click(self, **event_args):
    self.version_history_panel.visible = True
    self.technical_specs_panel.visible = False
    self.cost_details_panel.visible = False
    doc_id = (self.item or {}).get("document_id")
    if not doc_id:
      alert("No document ID found!")
      return
    history = anvil.server.call("get_version_history", doc_id)


    self.repeating_panel_version_history.items = history

  def back_btn_click(self, **event_args):
    open_form("Material_list")
    pass

  def material_sku_tab_btn_click(self, **event_args):
    self.material_sku_panel.visible = True
    self.version_history_panel.visible = False
    self.cost_details_panel.visible = False
    self.technical_specs_panel.visible = False
    pass

  def add_sku_btn_click(self, **event_args):
    form = Material_sku_input_form(master_material=self.item['material_id'])
    alert(content=form, title=None, large=True, buttons=None)
  
    # When the form closes successfully, refresh the data 
    if form.saved: 
      self.refresh_data()

  def refresh_data(self): 
    try: 
      self.material_sku_repeating_panel.items = anvil.server.call('get_material_sku', self.item['material_id']) 
    except Exception as e: 
      Notification(f"Error loading data: {e}").show()



  





 

  


    