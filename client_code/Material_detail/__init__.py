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

  def edit_btn_click(self, **event_args):
    doc_id = None
    try:
      doc_id = self.item.get("document_id")
    except Exception:
      doc_id = None

    if not doc_id:
      alert("No document ID available to edit.", title="Error")
      return

    initial_item = dict(self.item or {})
    
    input_form = Material_input_form(current_document_id=doc_id, item=initial_item)    
    result = alert(content=input_form, large=True)
    # If the edit form reported a save/submit, reload this detail and trigger list refresh
    if result in ("saved", "submitted", "edited"):
      try:
        self.load_material(doc_id)
      except Exception as e:
        Notification(f"Reload failed: {e}", style="danger").show()


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




 

  


    