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
    if not getattr(self, "doc_id", None):
      alert("No document id provided", title="Error")
      return

    try:
      # Server returns a dict (see get_material_detail)
      data = anvil.server.call("get_material_detail", self.doc_id)
    except Exception as e:
      alert(f"Failed to load material: {e}", title="Load error")
      try:
        self.loading_spinner.visible = False
      except Exception:
        pass
      return
    self.item = data
    
    try:
      self.refresh_data_bindings()
    except Exception:
      pass

    try:
      self.loading_spinner.visible = False
    except Exception:
      pass

  # Optional: if this form allows edits/saves, after saving call:
  # self.raise_event("x-refresh-list", document_id=self.doc_id)
  # self.raise_event("x-close-alert", True)

 

 

  


    