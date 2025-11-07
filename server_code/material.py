import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server






@anvil.server.callable
def get_suppliers():
  return app_tables.supplier.search() 

@anvil.server.callable
def get_material_sku():
  return app_tables.material_sku.search()
