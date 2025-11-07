from ._anvil_designer import Material_listTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..Material_input_form import Material_input_form


class Material_list(Material_listTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def add_btn_click(self, **event_args):
    """Creates new material with 'Creating' status"""
    try:
      result = anvil.server.call('create_new_master_material', 'test_user@example.com')
      document_id = result['document_id']
      Notification(f"Created new material: {document_id}", style="success", timeout=2).show()
      # Import and create popup WITH document_id
      from ..Material_input_form import Material_input_form
      popup = Material_input_form(current_document_id=document_id)  
      alert(
        content=popup,
        title=None,
        large=True,
        buttons=None 
      )
    except Exception as e:
      alert(f"Error creating material: {str(e)}")
      
 



  


