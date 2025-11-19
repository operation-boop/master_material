import anvil.users
import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_material_sku(document_id):
  master_row = app_tables.master_material.get(document_id=document_id)
  if not master_row:
    return []

    # now search using the ROW, not a string
  return app_tables.material_sku.search(master_material=master_row)

@anvil.server.callable
def create_material_sku(document_id, ref_id, qr_data, sku_cost_override, color=None, size=None):
  from anvil.tables import app_tables

  master_row = app_tables.master_material.get(document_id=document_id)
  if not master_row:
    raise Exception(f"Master material not found for document_id {document_id}")

  all_skus = app_tables.material_sku.search()
  sku_numbers = [
    int(sku['id'][3:])
    for sku in all_skus
    if sku['id'] and sku['id'].startswith("SKU")
  ]

  if sku_numbers:
    new_sku_id = f"SKU{max(sku_numbers) + 1:03d}"
  else:
    new_sku_id = "SKU001"

  # 3. Create new SKU record, linked to master_row
  return app_tables.material_sku.add_row(
    id=new_sku_id,
    master_material=master_row,
    ref_id=ref_id,
    qr_data=qr_data,
    sku_cost_override=sku_cost_override,
    color=color,
    size=size
  )

  