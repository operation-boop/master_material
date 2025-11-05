import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def draft_version(status):
  return app_tables.master_material_version.get(status=status)


  