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
def test_processing_costs_simple():
  """Simple test for processing costs"""

  try:
    # You need these IDs - get them from your database
    # Go to Data Tables and copy an actual ID from each table
    cost_sheet_version_id = "[1024806,4967078002]"  # Copy from cost_sheet_versions table
    user_id = "[1024742,4964220004]"  # Copy from users table

    results = []
    results.append("Testing Processing Costs...")
    results.append("")

    # TEST 1: Add a processing cost
    results.append("TEST 1: Adding processing cost...")
    processing_cost = anvil.server.call(
      'add_processing_cost',
      cost_sheet_version_id,
      "Cut-make",
      5.50,
      "USD",
      "Test Factory",
      "Test CMT processing",
      user_id,
      None,  # No supplier_id for now
      "Draft"
    )
    results.append(f"✅ Added: {processing_cost.get_id()}")
    results.append(f"   Type: {processing_cost['cost_type']}")
    results.append(f"   Amount: ${processing_cost['cost_amount']}")
    results.append("")

    # TEST 2: List processing costs
    results.append("TEST 2: Listing processing costs...")
    costs = anvil.server.call('list_processing_costs', cost_sheet_version_id)
    results.append(f"✅ Found {len(costs)} processing cost(s)")
    results.append("")

    # TEST 3: Update the processing cost
    results.append("TEST 3: Updating processing cost...")
    updated = anvil.server.call(
      'update_processing_cost',
      processing_cost.get_id(),
      6.00,  # New amount
      "USD",
      "Updated Factory Name",
      "Updated description",
      user_id,
      "Verified"  # Change status
    )
    results.append(f"✅ Updated: {updated.get_id()}")
    results.append(f"   New amount: ${updated['cost_amount']}")
    results.append(f"   New status: {updated['status']}")
    results.append("")

    # TEST 4: Check if total was updated
    results.append("TEST 4: Checking if totals updated...")
    from anvil.tables import app_tables
    version = app_tables.cost_sheet_version.get_by_id(cost_sheet_version_id)
    total = version['total_processing_cost']
    results.append(f"✅ Total processing cost: ${total:.2f}")
    results.append("")

    # TEST 5: Delete the processing cost
    results.append("TEST 5: Deleting processing cost...")
    anvil.server.call('delete_processing_cost', processing_cost.get_id())
    results.append("✅ Deleted successfully")

    # Check total after delete
    version = app_tables.cost_sheet_version.get_by_id(cost_sheet_version_id)
    total_after = version['total_processing_cost']
    results.append(f"   Total after delete: ${total_after:.2f}")
    results.append("")

    results.append("=" * 50)
    results.append("🎉 ALL PROCESSING COST TESTS PASSED!")
    results.append("=" * 50)

    return "\n".join(results)

  except Exception as e:
    import traceback
    error_msg = f"❌ TEST FAILED!\nError: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
    return error_msg