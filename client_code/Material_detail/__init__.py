# material_detail.py
from ._anvil_designer import Material_detailTemplate
from anvil import *
import anvil.server
from datetime import datetime

class Material_detail(Material_detailTemplate):
  def __init__(self, document_id=None, **properties):
    self.init_components(**properties)