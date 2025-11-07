# material_detail.py
from ._anvil_designer import Material_detailTemplate
from anvil import *
import anvil.server
from datetime import datetime

class Material_detail(Material_detailTemplate):
  def __init__(self, document_id=None, ver_num=None, **properties):
    # Standard Anvil init
    self.init_components(**properties)

    # Initialize version holder
    self.item = None

    # Try to load the freshest row from server
    if document_id and ver_num is not None:
      try:
        self.item = anvil.server.call('get_version_by_doc_and_ver',
        document_id,
        ver_num,
        )
      except Exception as e:
        alert(f"Could not load version: {e}", title="Load error")
        # keep self.version as None so bindings won't break (we'll guard bindings)
        self.version = None



    