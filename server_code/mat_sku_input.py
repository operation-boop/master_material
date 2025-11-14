import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_material_sku(master_material):
  return app_tables.material_sku.search(master_material=master_material)

@anvil.server.callable
def create_material_sku(master_material, ref_id, qr_data, sku_cost_override, color=None, size=None):

  # Auto-generate sku_id
  all_skus = app_tables.material_sku.search()
  if all_skus:
    last_sku_num = max(int(sku['id'][3:]) for sku in all_skus if sku['id'].startswith("SKU"))
    new_sku_id = f"SKU{last_sku_num+1:03d}"
  else:
    new_sku_id = "SKU001"

  # Create new SKU record
  return app_tables.material_sku.add_row(
    id=new_sku_id,
    master_material=master_material,
    ref_id=ref_id,
    qr_data=qr_data,
    sku_cost_override=sku_cost_override,
    color=color,
    size=size
  )