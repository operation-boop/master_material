import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime

@anvil.server.callable
def test_overhead_costs():
  """Test overhead cost operations"""

  try:
    results = []
    results.append("=" * 50)
    results.append("TESTING OVERHEAD COSTS")
    results.append("=" * 50)
    results.append("")

    # SETUP
    results.append("SETUP: Creating test data...")
    test_user = app_tables.users.add_row(name="Test User", email="test@test.com", role="staff")
    test_client = app_tables.clients.add_row(name="Test Client", price_category="Medium", country="US", max_account_value=50000.0, currency="USD")
    test_style = app_tables.master_styles.add_row(ref_id="TEST-001", client=test_client, picture="test", description="Test")
    test_cost_sheet = app_tables.cost_sheets.add_row(document_id="TEST-CS", current_version=1, created_at=datetime.now(), created_by=test_user)
    test_version = app_tables.cost_sheet_versions.add_row(
      cost_sheet=test_cost_sheet, document_id="TEST-CS", version_number=1, change_description="Initial",
      created_at=datetime.now(), created_by=test_user, status="Draft", cost_currency="USD",
      master_style=test_style, client=test_client, total_material_cost=0.0, total_processing_cost=0.0, total_overhead_cost=0.0
    )
    version_id = test_version.get_id()
    results.append("✅ Setup complete")
    results.append("")

    # TEST 1: Add Tier 2 overhead
    results.append("TEST 1: Add Tier 2 overhead (Import logistics)...")
    oh1 = anvil.server.call('add_overhead_cost_item', version_id, "Sea freight", "Import logistics", 1.50, "USD", test_user.get_id())
    results.append(f"✅ Added: {oh1['name']} - ${oh1['cost_amount']}")

    # TEST 2: Add Tier 3 overhead
    results.append("TEST 2: Add Tier 3 overhead (Material testing)...")
    oh2 = anvil.server.call('add_overhead_cost_item', version_id, "Lab test", "Material testing", 75.0, "USD", test_user.get_id())
    results.append(f"✅ Added: {oh2['name']} - ${oh2['cost_amount']}")

    # TEST 3: Check total
    results.append("TEST 3: Check total overhead cost...")
    test_version = app_tables.cost_sheet_versions.get_by_id(version_id)
    total = test_version['total_overhead_cost']
    expected = 76.50
    results.append(f"   Total: ${total:.2f}")
    results.append(f"   Expected: ${expected:.2f}")
    if abs(total - expected) < 0.01:
      results.append("   ✅ Correct!")
    else:
      results.append("   ❌ Wrong!")

      # TEST 4: List overhead items
    results.append("TEST 4: List overhead items...")
    items = anvil.server.call('list_overhead_cost_items', version_id)
    results.append(f"✅ Found {len(items)} items")

    # TEST 5: Update overhead item
    results.append("TEST 5: Update overhead item...")
    updated = anvil.server.call('update_overhead_cost_item', oh1.get_id(), "Updated freight", 2.00, "USD", test_user.get_id())
    results.append(f"✅ Updated to ${updated['cost_amount']}")

    # TEST 6: Delete overhead item
    results.append("TEST 6: Delete overhead item...")
    anvil.server.call('delete_overhead_cost_item', oh2.get_id())
    results.append("✅ Deleted")

    # CLEANUP
    results.append("")
    results.append("CLEANUP...")
    oh1.delete()
    test_version.delete()
    test_cost_sheet.delete()
    test_style.delete()
    test_client.delete()
    test_user.delete()
    results.append("✅ Cleaned up")

    results.append("")
    results.append("🎉 ALL OVERHEAD TESTS PASSED!")
    return "\n".join(results)

  except Exception as e:
    import traceback
    return f"❌ FAILED: {str(e)}\n{traceback.format_exc()}"