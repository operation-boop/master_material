# material_detail.py
from ._anvil_designer import Material_detailTemplate
from anvil import *
import anvil.server
from datetime import datetime

class Material_detail(Material_detailTemplate):
  def __init__(self, doc_id=None, **properties):
    self.init_components(**properties)
    self.doc_id = doc_id

  def form_show(self, **event_args):
    if not self.doc_id:
      alert("No document ID provided!")
      return
  
    try:
      # Call server to get material data
      data = anvil.server.call("get_material_detail", self.doc_id)
      self.item = data
      self.refresh_data_bindings()
      
    except Exception as e:
      alert(f"Failed to load details: {e}")

  def back_btn_click(self, **event_args):
    open_form('Material_list')
    pass
  


    