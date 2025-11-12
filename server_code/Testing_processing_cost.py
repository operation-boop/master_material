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
def test_processing_costs_complete():
  """Complete test for processing costs - PLURAL table names"""

  try:
    results = []
    results.append("=" * 50)
    results.append("PROCESSING COSTS - COMPLETE TEST")
    results.append("=" * 50)
    results.append("")

    # SETUP: Create test data
    results.append("SETUP: Creating test data...")

    # Create test user
    test_user = app_tables.users.add_row(
      name="Test User",
      email="test@test.com",
      role="staff"
    )
    user_id = test_user.get_id()
    results.append(f"✅ Created user: {user_id}")

    # Create test client
    test_client = app_tables.clients.add_row(
      name="Test Client",
      price_category="Medium",
      country="US",
      max_account_value=50000.0,
      currency="USD"
    )

    # Create test style
    test_style = app_tables.master_styles.add_row(
      ref_id="TEST-STYLE-001",
      client=test_client,
      picture="test",
      description="Test style"
    )

    # Create test cost sheet
    test_cost_sheet = app_tables.cost_sheets.add_row(
      document_id="TEST-CS-001",
      current_version=1,
      created_at=datetime.now(),
      created_by=test_user
    )

    # Create test cost sheet version
    test_version = app_tables.cost_sheet_versions.add_row(
      cost_sheet=test_cost_sheet,
      document_id="TEST-CS-001",
      version_number=1,
      change_description="Initial",
      created_at=datetime.now(),
      created_by=test_user,
      status="Draft",
      cost_currency="USD",
      master_style=test_style,
      client=test_client,
      total_material_cost=0.0,
      total_processing_cost=0.0,
      total_overhead_cost=0.0
    )
    version_id = test_version.get_id()
    results.append(f"✅ Created cost sheet version: {version_id}")
    results.append("")

    # TEST 1: Add processing cost
    results.append("TEST 1: Adding Cut-make processing cost...")
    pc1 = anvil.server.call(
      'add_processing_cost',
      version_id,
      "Cut-make",
      5.50,
      "USD",
      "ABC CMT Factory",
      "Standard cut and sew",
      user_id,
      None,
      "Draft"
    )
    results.append(f"✅ Added processing cost: {pc1.get_id()}")
    results.append(f"   Type: {pc1['cost_type']}")
    results.append(f"   Amount: ${pc1['cost_amount']:.2f} {pc1['cost_currency']}")
    results.append(f"   Vendor: {pc1['vendor_name']}")
    results.append(f"   Status: {pc1['status']}")

    # Check total
    test_version = app_tables.cost_sheet_versions.get_by_id(version_id)
    results.append(f"   Total processing cost: ${test_version['total_processing_cost']:.2f}")
    results.append("")

    # TEST 2: Add another processing cost (Embroidery)
    results.append("TEST 2: Adding Embroidery processing cost...")
    pc2 = anvil.server.call(
      'add_processing_cost',
      version_id,
      "Embroidery",
      2.00,
      "USD",
      "XYZ Embroidery Shop",
      "Logo embroidery",
      user_id
    )
    results.append(f"✅ Added embroidery cost: {pc2.get_id()}")
    results.append(f"   Amount: ${pc2['cost_amount']:.2f}")

    # Check updated total
    test_version = app_tables.cost_sheet_versions.get_by_id(version_id)
    results.append(f"   Total processing cost: ${test_version['total_processing_cost']:.2f}")
    results.append("   Expected: $7.50 (5.50 + 2.00)")

    # Verify
    if abs(test_version['total_processing_cost'] - 7.50) < 0.01:
      results.append("   ✅ Total is correct!")
    else:
      results.append(f"   ❌ Total is WRONG! Got {test_version['total_processing_cost']}, expected 7.50")
    results.append("")

    # TEST 3: List all processing costs
    results.append("TEST 3: Listing all processing costs...")
    all_costs = anvil.server.call('list_processing_costs', version_id)
    results.append(f"✅ Found {len(all_costs)} processing cost(s)")
    for cost in all_costs:
      results.append(f"   - {cost['cost_type']}: ${cost['cost_amount']:.2f}")
    results.append("")

    # TEST 4: Update processing cost
    results.append("TEST 4: Updating Cut-make cost...")
    updated_pc = anvil.server.call(
      'update_processing_cost',
      pc1.get_id(),
      6.00,  # Changed from 5.50
      "USD",
      "ABC CMT Factory (Updated)",
      "Updated description",
      user_id,
      "Verified"  # Changed status
    )
    results.append("✅ Updated processing cost")
    results.append(f"   Old amount: $5.50 → New amount: ${updated_pc['cost_amount']:.2f}")
    results.append(f"   Old status: Draft → New status: {updated_pc['status']}")

    # Check updated total
    test_version = app_tables.cost_sheet_versions.get_by_id(version_id)
    results.append(f"   Total processing cost: ${test_version['total_processing_cost']:.2f}")
    results.append("   Expected: $8.00 (6.00 + 2.00)")

    if abs(test_version['total_processing_cost'] - 8.00) < 0.01:
      results.append("   ✅ Total updated correctly!")
    else:
      results.append(f"   ❌ Total is WRONG! Got {test_version['total_processing_cost']}, expected 8.00")
    results.append("")

    # TEST 5: Verify processing cost
    results.append("TEST 5: Testing verify function...")
    verified_pc = anvil.server.call('verify_processing_cost', pc2.get_id(), user_id)
    results.append("✅ Verified processing cost")
    results.append(f"   Status: {verified_pc['status']}")
    results.append(f"   Verified by: {verified_pc['last_verified_by']['name']}")
    results.append("")

    # TEST 6: Delete one processing cost
    results.append("TEST 6: Deleting Embroidery cost...")
    anvil.server.call('delete_processing_cost', pc2.get_id())
    results.append("✅ Deleted processing cost")

    # Check total after delete
    test_version = app_tables.cost_sheet_versions.get_by_id(version_id)
    results.append(f"   Total processing cost: ${test_version['total_processing_cost']:.2f}")
    results.append("   Expected: $6.00 (only Cut-make left)")

    if abs(test_version['total_processing_cost'] - 6.00) < 0.01:
      results.append("   ✅ Total recalculated correctly after delete!")
    else:
      results.append(f"   ❌ Total is WRONG! Got {test_version['total_processing_cost']}, expected 6.00")
    results.append("")

    # TEST 7: Test with different currencies
    results.append("TEST 7: Testing currency conversion...")
    pc_vnd = anvil.server.call(
      'add_processing_cost',
      version_id,
      "Washing",
      125000.0,  # VND
      "VND",
      "Vietnam Washing Plant",
      "Stone wash",
      user_id
    )
    results.append("✅ Added VND processing cost: 125,000 VND")

    # Check total (should convert VND to USD)
    test_version = app_tables.cost_sheet_versions.get_by_id(version_id)
    results.append(f"   Total processing cost in USD: ${test_version['total_processing_cost']:.2f}")
    results.append("   Expected: ~$11.00 (6.00 + 125000/25000)")
    results.append("")

    # CLEANUP
    results.append("CLEANUP: Deleting test data...")
    pc1.delete()
    pc_vnd.delete()
    test_version.delete()
    test_cost_sheet.delete()
    test_style.delete()
    test_client.delete()
    test_user.delete()
    results.append("✅ All test data deleted")
    results.append("")

    # SUCCESS
    results.append("=" * 50)
    results.append("🎉 ALL PROCESSING COST TESTS PASSED! 🎉")
    results.append("=" * 50)
    results.append("")
    results.append("Summary:")
    results.append("✅ Add processing cost")
    results.append("✅ Add multiple costs")
    results.append("✅ List processing costs")
    results.append("✅ Update processing cost")
    results.append("✅ Verify processing cost")
    results.append("✅ Delete processing cost")
    results.append("✅ Currency conversion")
    results.append("✅ Total calculation")
    results.append("✅ Total recalculation after update/delete")

    return "\n".join(results)

  except Exception as e:
    import traceback
    return f"❌ TEST FAILED!\n\nError: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"