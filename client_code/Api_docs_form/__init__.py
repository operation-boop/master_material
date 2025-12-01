from ._anvil_designer import Api_docs_formTemplate
from anvil import *
import anvil.users
import anvil.google.auth, anvil.google.drive
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import HtmlTemplate
import anvil.server
import json
from datetime import (datetime,)  # Needed if you need to pass default values or handle client-side logic


class Api_docs_form(Api_docs_formTemplate):
  def __init__(self, **properties):
    self.html_viewer = HtmlTemplate(html="html_viewer")
    self.init_components(**properties)
    self.column_panel_1.add_component(self.html_viewer)
    docs_data = anvil.server.call("get_api_documentation_openapi")
    json_spec = json.dumps(docs_data)

    self.html_viewer.html = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <title>API Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>body {{ margin: 0; padding: 0; }}</style>
      </head>
      <body>
        <div id="redoc-container"></div>
        
        <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
        
        <script>
          const spec = {json_spec};
          
          Redoc.init(
            spec, 
            {{}}, 
            document.getElementById('redoc-container')
          );
        </script>
      </body>
    </html>
    """
