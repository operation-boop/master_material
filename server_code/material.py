import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable



  
def get_materials():
  return app_tables.master_material.search() 

@anvil.server.callable
def get_suppliers():
  return app_tables.supplier.search() 
