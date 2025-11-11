from ._anvil_designer import Material_detailTemplate
from anvil import alert
import anvil.server


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


 

  


    