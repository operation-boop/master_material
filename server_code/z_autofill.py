import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
# Paste this into an Anvil Server Module and run/create_sample_boms()
import random
from datetime import datetime, timedelta
from pprint import pprint


def _pick_or_create_first_row(table_name, fallback_values):
  """
    Returns a Row from app_tables.<table_name>.
    If none exists, creates one using fallback_values (a dict).
    """
  table = getattr(app_tables, table_name)
  rows = list(table.search())
  if rows:
    return rows[0]
    # create a fallback row:
  return table.add_row(**fallback_values)

def _ensure_some_rows(table_name, count, fallback_values_template):
  """
    Return list of up to 'count' rows from app_tables.<table_name>.
    If table has fewer than count rows, create additional rows using fallback_values_template(index).
    fallback_values_template: function(i) -> dict
    """
  table = getattr(app_tables, table_name)
  rows = list(table.search())
  while len(rows) < count:
    idx = len(rows) + 1
    rows.append(table.add_row(**fallback_values_template(idx)))
  return rows[:count]

def _make_version_history(prev_rows):
  """
    Version history: depending on your column type, you may want a list of Row objects or a single link.
    This returns a list (which works if your column accepts list of links).
    If your version_history column is a single link, set it to prev_rows[-1] instead.
    """
  return prev_rows[:]  # list of Row references

@anvil.server.callable
def create_sample_boms():
  """
    Create:
      - 2 bill_of_material rows
      - 2 bill_of_material_line_item rows per BOM
    Safely links to staff_users, master_material, material_sku (creates fallback rows if needed).
    """
  # --- Prepare linked-table rows (use existing entries if present; otherwise create fallbacks) ---
  staff_rows = _ensure_some_rows(
    "staff_users",
    2,
    lambda i: {"username": f"dummy_user_{i}", "full_name": f"Dummy User {i}", "email": f"dummy{i}@example.com"}
  )

  master_material_rows = _ensure_some_rows(
    "master_material",
    4,
    lambda i: {"material_name": f"Material {i}", "description": f"Fallback material {i}"}
  )

  material_sku_rows = _ensure_some_rows(
    "material_sku",
    4,
    lambda i: {"sku": f"SKU-{1000 + i}", "description": f"SKU fallback {i}"}
  )

  # --- Create two BOMs ---
  bom_table = app_tables.bill_of_material
  created_boms = []

  base_time = datetime.now() - timedelta(days=10)
  for i in range(2):
    doc_id = f"BOM-{1001 + i}"
    created_at = base_time + timedelta(days=i)
    created_by = staff_rows[i % len(staff_rows)]
    # For this simple example, current_version = 1 and version_history empty
    bom_row = bom_table.add_row(
      document_id=doc_id,
      current_version=1,
      #version_history=[],        # If your column expects a single link, replace [] with None or previous row
      created_at=created_at,
      created_by=created_by,
      submitted_at=created_at + timedelta(days=1),
      submitted_by=created_by
    )
    created_boms.append(bom_row)

    # Optional: If you want version_history to point to another BOM (example),
    # you can update version_history with references. In this example we leave it empty.

    # --- Create 2 line items per BOM ---
  line_table = app_tables.bill_of_material_line_item
  created_line_items = []

  for bom in created_boms:
    # pick two different materials/skus for variety
    mats = random.sample(master_material_rows, 2)
    skus = random.sample(material_sku_rows, 2)

    for idx in range(2):
      assigned_material = mats[idx]
      assigned_sku = skus[idx]

      # generate some numbers
      gross_consumption = round(random.uniform(1.0, 50.0), 3)  # units
      selling_tolerance = round(random.uniform(0.0, 5.0), 2)  # percent
      net_selling_consumption = round(gross_consumption * (1 - selling_tolerance / 100), 3)
      buying_tolerance = round(random.uniform(0.0, 5.0), 2)
      net_buying_consumption = round(gross_consumption * (1 - buying_tolerance / 100), 3)
      material_cost_in_usd = round(random.uniform(0.5, 100.0) * net_buying_consumption, 2)
      native_currency = random.choice(["USD", "SGD", "VND", "MYR"])

      li = line_table.add_row(
        bill_of_material=bom,
        assigned_material=assigned_material,
        assigned_sku=assigned_sku,
        gross_consumption=gross_consumption,
        selling_tolerance=selling_tolerance,
        net_selling_consumption=net_selling_consumption,
        buying_tolerance=buying_tolerance,
        net_buying_consumption=net_buying_consumption,
        material_cost_in_usd=material_cost_in_usd,
        native_currency=native_currency
      )
      created_line_items.append(li)

    # Print summary to Server Logs
  print("Created BOMs:")
  # for b in created_boms:
  #   print({"id": b.get_id(), "document_id": b["document_id"], "created_by": dict(b["created_by"]) if b.get("created_by") else None})

  for b in created_boms:
   b_dict = dict(b)   # now it's a normal dict
   created_by = b_dict.get("created_by")    # this may be a Row or None
   created_by_dict = dict(created_by) if created_by else None

  print({
    "id": b.get_id(),
    "document_id": b_dict.get("document_id"),
    "created_by": created_by_dict
  })

  
  # print("Created Line Items:")
  # for li in created_line_items:
  #   li_copy = dict(li)
  #   # attach link references in human-readable form
  #   li_copy["_id"] = li.get_id()
  #   if li.get("bill_of_material"):
  #     li_copy["bom_id"] = li["bill_of_material"].get_id()
  #   if li.get("assigned_material"):
  #     li_copy["assigned_material_name"] = li["assigned_material"].get("material_name", "")
  #   if li.get("assigned_sku"):
  #     li_copy["assigned_sku_code"] = li["assigned_sku"].get("sku", "")
  #   pprint(li_copy)

  print("Created Line Items:")
  for li in created_line_items:
    li_copy = dict(li)  # copy the main row to a dict
    li_copy["_id"] = li.get_id()

  # bill_of_material is a linked row
    bom_row = li["bill_of_material"]
    li_copy["bom_id"] = bom_row.get_id() if bom_row else None

  # assigned_material is a linked row
    mat_row = li["assigned_material"]
    li_copy["assigned_material_name"] = dict(mat_row).get("material_name", "") if mat_row else ""

  # assigned_sku is a linked row
    sku_row = li["assigned_sku"]
    li_copy["assigned_sku_code"] = dict(sku_row).get("sku", "") if sku_row else ""

    pprint(li_copy)


  
  return {"boms_created": len(created_boms), "line_items_created": len(created_line_items)}

# If you prefer an explicit callable so you can call it from the Anvil UI:

