import anvil.users
import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .api_framework import export_api_docs
from . import materialcard_api
from . import material_api


def generate_all_docs_for_anvil():
  """
    Generates documentation and prints it to the Anvil Server Log.
    NOTE: File saving is commented out for cloud compatibility.
    """

  # Generate Markdown documentation
  print("Generating Markdown documentation...")
  md_docs = export_api_docs(format='markdown')
  print(f"--- MARKDOWN DOCS START ({len(md_docs)} chars) ---")
  print(md_docs)
  print("--- MARKDOWN DOCS END ---\n")

  # Generate OpenAPI/Swagger JSON
  print("Generating OpenAPI specification...")
  openapi_docs = export_api_docs(format='openapi')
  print(f"--- OPENAPI SPEC START ({len(openapi_docs)} chars) ---")
  print(openapi_docs)
  print("--- OPENAPI SPEC END ---\n")

  # File saving is disabled unless you are running Anvil Uplink locally:
  # export_api_docs(format='markdown', output_file='API_DOCUMENTATION.md')
  # export_api_docs(format='openapi', output_file='openapi.json')

  print("="*60)
  print("Documentation generation complete.")
  print("="*60)

@anvil.server.callable
def trigger_doc_generation():
  generate_all_docs_for_anvil()
  return "Documentation updated in server logs."