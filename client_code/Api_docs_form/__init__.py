from ._anvil_designer import Api_docs_formTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Api_docs_form(Api_docs_formTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Get the markdown string and assign it directly
    markdown_text = anvil.server.call('get_api_documentation_markdown')
    self.rt_docs.content = markdown_text
