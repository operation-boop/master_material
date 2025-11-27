import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
@anvil.server.callable
def get_clients():
  return list(app_tables.client.search())

@anvil.server.callable
def add_client(client_name, country, price_category, max_account_value, currency):
  new_id = f"VMC{uuid.uuid4().hex[:8].upper()}"
  app_tables.client.add_row(
    client_id=new_id,
    client_name=client_name,
    country=country,
    price_category=price_category,
    max_account_value=max_account_value,
    currency=currency
  )

@anvil.server.callable
def get_client_by_id(client_id):
  return app_tables.client.get_by_id(client_id)

@anvil.server.callable
def update_client(client_id, client_name, country, price_category, max_value, currency):
  client = app_tables.client.get_by_id(client_id)

  if not client:
    raise Exception(f"Client với ID {client_id} không tồn tại!")

  client.update(
    client_name=client_name,
    country=country,
    price_category=price_category,
    max_account_value=float(max_value or 0),
    currency=currency
  )
  return client

@anvil.server.callable
def get_suppliers():
  return list(app_tables.supplier.search())

@anvil.server.callable
def add_supplier(supplier_name, country, contact_person, email):
  new_id = f"VMC{uuid.uuid4().hex[:8].upper()}"
  return app_tables.supplier.add_row(
    supplier_id = new_id,
    supplier_name=supplier_name,
    country=country,
    contact_person=contact_person,
    email=email,
    status=False
  )

@anvil.server.callable
def get_supplier_by_id(supplier_id):
  return app_tables.supplier.get_by_id(supplier_id)

@anvil.server.callable
def verify_supplier(supplier_id):
  supplier = app_tables.supplier.get(supplier_id=supplier_id)
  if not supplier:
    return {"success": False, "msg": "Supplier not found"}

  if supplier['status']:
    return {"success": False, "msg": "Already verified"}

  supplier['status'] = True
  supplier['approved_date'] = datetime.now()
  # supplier['approved_by'] = current_user
  supplier.update()
  return {"success": True, "approved_date": supplier['approved_date']}

@anvil.server.callable
def update_supplier(supplier_id, supplier_name, country, contact_person, email):
  supplier = app_tables.supplier.get_by_id(supplier_id)
  if not supplier:
    raise ValueError("Supplier not found")

  supplier['supplier_name'] = supplier_name
  supplier['country'] = country
  supplier['contact_person'] = contact_person
  supplier['email'] = email
  supplier.update()
  return True


@anvil.server.callable
def get_contacts():
  return list(app_tables.contact.search())