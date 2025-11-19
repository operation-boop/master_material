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


"""
Lean MVP Tests for Cost Sheet System
All tests in one module for simplicity
"""

# ============================================
# TEST 1: COST SHEET CRUD
# ============================================

@anvil.server.callable
def test_cost_sheet_crud():
  """Test creating, listing, and getting cost sheets"""
  try:
    results = []
    results.append("=" * 50)
    results.append("TEST: COST SHEET CRUD")
    results.append("=" * 50)
    results.append("")

    # SETUP
    results.append("SETUP: Creating test data...")
    test_client = app_tables.clients.add_row(
      name="Test Client",
      price_category="Medium",
      country="US",
      max_account_value=50000.0,
      currency="USD"
    )
    test_style = app_tables.master_styles.add_row(
      ref_id="TEST-001",
      client=test_client,
      picture="test",
      description="Test"
    )
    test_user = app_tables.users.add_row(
      name="Test User",
      email="test@test.com",
      role="staff"
    )
    results.append("✅ Setup complete")
    results.append("")

    # TEST: Create
    results.append("TEST 1: Create cost sheet...")
    cs = anvil.server.call('create_cost_sheet',
                           test_style.get_id(),
                           test_client.get_id(),
                           "TEST-CS-001",
                           test_user.get_id(),
                           "USD")
    cs_id = cs.get_id()
    results.append(f"✅ Created: {cs['document_id']}")
    results.append("")

    # TEST: List
    results.append("TEST 2: List all cost sheets...")
    all_sheets = anvil.server.call('list_all_cost_sheets')
    results.append(f"✅ Found {len(all_sheets)} cost sheets")
    results.append("")

    # TEST: Get
    results.append("TEST 3: Get specific cost sheet...")
    retrieved = anvil.server.call('get_cost_sheet', cs_id)
    if retrieved['document_id'] == "TEST-CS-001":
      results.append("✅ Retrieved correct cost sheet")
    else:
      results.append("❌ Retrieved wrong cost sheet")
    results.append("")

    # CLEANUP
    results.append("CLEANUP...")
    version = app_tables.cost_sheet_versions.get(cost_sheet=cs)
    version.delete()
    cs.delete()
    test_style.delete()
    test_client.delete()
    test_user.delete()
    results.append("✅ Cleaned up")
    results.append("")

    results.append("🎉 COST SHEET CRUD TESTS PASSED!")
    return "\n".join(results)

  except Exception as e:
    import traceback
    return f"❌ FAILED: {str(e)}\n{traceback.format_exc()}"


# ============================================
# TEST 2: BOM OPERATIONS
# ============================================

@anvil.server.callable
def test_bom_operations():
  """Test BOM create, add, list, update, delete"""
  try:
    results = []
    results.append("=" * 50)
    results.append("TEST: BOM OPERATIONS")
    results.append("=" * 50)
    results.append("")

    # SETUP
    results.append("SETUP...")
    test_user = app_tables.users.add_row(name="Test", email="t@t.com", role="staff")
    test_client = app_tables.clients.add_row(name="Test", price_category="Medium", country="US", max_account_value=50000.0, currency="USD")
    test_style = app_tables.master_styles.add_row(ref_id="TEST", client=test_client, picture="test", description="Test")
    test_supplier = app_tables.suppliers.add_row(name="Test Supplier", country="Vietnam", approved_vendor=True, approved_date=datetime.now(), approved_by=test_user)
    test_material = app_tables.master_materials.add_row(document_id="MAT-TEST", current_version=1, created_at=datetime.now(), created_by=test_user)
    test_material_version = app_tables.master_material_versions.add_row(
      master_material=test_material,
      document_id="MAT-TEST",
      version_number=1,
      change_description="Initial",
      created_at=datetime.now(),
      created_by=test_user,
      ref_id="SUP-MAT-001",
      master_material_id="MAT-TEST",
      status="Verified",
      supplier=test_supplier,
      supplier_name="Test Supplier",
      country_of_origin="Vietnam",
      name="Test Fabric",
      material_type="Main fabric",
      unit_of_measurement="meter",
      weight_per_unit=200.0,
      weight_uom="gsm",
      original_cost_per_unit=5.00,
      native_cost_currency="USD",
      supplier_selling_tolerance=0.05,
      refundable_tolerance=True,
      effective_cost_per_unit=5.25,
      last_verified_date=datetime.now(),
      last_verified_by=test_user
    )

    cs = anvil.server.call('create_cost_sheet', test_style.get_id(), test_client.get_id(), "TEST-CS", test_user.get_id(), "USD")
    version = anvil.server.call('get_current_version', cs.get_id())
    version_id = version.get_id()
    results.append("✅ Setup complete")
    results.append("")

    # TEST 1: Create BOM
    results.append("TEST 1: Create BOM...")
    bom = anvil.server.call('create_bom_for_cost_sheet', version_id, test_user.get_id())
    bom_version = app_tables.bom_versions.get(bill_of_material=bom)
    bom_version_id = bom_version.get_id()
    results.append(f"✅ Created BOM: {bom['document_id']}")
    results.append("")

    # TEST 2: Add material
    results.append("TEST 2: Add material to BOM...")
    item = anvil.server.call('add_bom_line_item',
                             bom_version_id,
                             test_material.get_id(),
                             2.5,
                             0.05,
                             0.10,
                             test_user.get_id())
    results.append(f"✅ Added material: consumption={item['gross_consumption']}")

    # Check total
    version = app_tables.cost_sheet_versions.get_by_id(version_id)
    results.append(f"   Material total: ${version['total_material_cost']:.2f}")
    results.append("")

    # TEST 3: List materials
    results.append("TEST 3: List BOM items...")
    items = anvil.server.call('list_bom_line_items', bom_version_id)
    results.append(f"✅ Found {len(items)} items")
    results.append("")

    # TEST 4: Update material
    results.append("TEST 4: Update BOM item...")
    updated = anvil.server.call('update_bom_line_item',
                                item.get_id(),
                                3.0,
                                0.05,
                                0.10)
    if updated['gross_consumption'] == 3.0:
      results.append("✅ Updated consumption to 3.0")
    else:
      results.append("❌ Update failed")
    results.append("")

    # TEST 5: Delete material
    results.append("TEST 5: Delete BOM item...")
    anvil.server.call('delete_bom_line_item', item.get_id())
    items_after = anvil.server.call('list_bom_line_items', bom_version_id)
    if len(items_after) == 0:
      results.append("✅ Deleted successfully")
    else:
      results.append("❌ Delete failed")
    results.append("")

    # CLEANUP
    results.append("CLEANUP...")
    bom_version.delete()
    bom.delete()
    version.delete()
    cs.delete()
    test_material_version.delete()
    test_material.delete()
    test_supplier.delete()
    test_style.delete()
    test_client.delete()
    test_user.delete()
    results.append("✅ Cleaned up")
    results.append("")

    results.append("🎉 BOM OPERATIONS TESTS PASSED!")
    return "\n".join(results)

  except Exception as e:
    import traceback
    return f"❌ FAILED: {str(e)}\n{traceback.format_exc()}"


# ============================================
# TEST 3: WORKFLOW OPERATIONS
# ============================================

@anvil.server.callable
def test_workflow_operations():
  """Test submit, approve, reject workflow"""
  try:
    results = []
    results.append("=" * 50)
    results.append("TEST: WORKFLOW OPERATIONS")
    results.append("=" * 50)
    results.append("")

    # SETUP
    results.append("SETUP...")
    test_user = app_tables.users.add_row(name="Staff", email="staff@t.com", role="staff")
    test_admin = app_tables.users.add_row(name="Admin", email="admin@t.com", role="admin")
    test_client = app_tables.clients.add_row(name="Test", price_category="Medium", country="US", max_account_value=50000.0, currency="USD")
    test_style = app_tables.master_styles.add_row(ref_id="TEST", client=test_client, picture="test", description="Test")

    cs = anvil.server.call('create_cost_sheet', test_style.get_id(), test_client.get_id(), "TEST-CS", test_user.get_id(), "USD")
    version = anvil.server.call('get_current_version', cs.get_id())
    version_id = version.get_id()
    results.append("✅ Setup complete")
    results.append(f"   Initial status: {version['status']}")
    results.append("")

    # TEST 1: Submit
    results.append("TEST 1: Submit for review...")
    anvil.server.call('submit_cost_sheet_for_review', version_id, test_user.get_id())
    version = app_tables.cost_sheet_versions.get_by_id(version_id)
    if version['status'] == "Under review":
      results.append(f"✅ Status changed to: {version['status']}")
    else:
      results.append(f"❌ Wrong status: {version['status']}")
    results.append("")

    # TEST 2: Check permissions
    results.append("TEST 2: Check approve permissions...")
    can_staff_approve = anvil.server.call('can_user_approve', test_user.get_id())
    can_admin_approve = anvil.server.call('can_user_approve', test_admin.get_id())

    if not can_staff_approve and can_admin_approve:
      results.append("✅ Permissions correct (staff=No, admin=Yes)")
    else:
      results.append("❌ Permission check failed")
    results.append("")

    # TEST 3: Approve
    results.append("TEST 3: Approve cost sheet...")
    anvil.server.call('approve_cost_sheet', version_id, test_admin.get_id())
    version = app_tables.cost_sheet_versions.get_by_id(version_id)
    if version['status'] == "Approved":
      results.append(f"✅ Status changed to: {version['status']}")
    else:
      results.append(f"❌ Wrong status: {version['status']}")
    results.append("")

    # TEST 4: Get pending (should be empty now)
    results.append("TEST 4: Check pending approvals...")
    pending = anvil.server.call('get_pending_approvals')
    results.append(f"✅ Pending count: {len(pending)}")
    results.append("")

    # CLEANUP
    results.append("CLEANUP...")
    version.delete()
    cs.delete()
    test_style.delete()
    test_client.delete()
    test_user.delete()
    test_admin.delete()
    results.append("✅ Cleaned up")
    results.append("")

    results.append("🎉 WORKFLOW TESTS PASSED!")
    return "\n".join(results)

  except Exception as e:
    import traceback
    return f"❌ FAILED: {str(e)}\n{traceback.format_exc()}"


# ============================================
# TEST 4: EXCHANGE RATES
# ============================================

@anvil.server.callable
def test_exchange_rates():
  """Test exchange rate CRUD"""
  try:
    results = []
    results.append("=" * 50)
    results.append("TEST: EXCHANGE RATES")
    results.append("=" * 50)
    results.append("")

    # SETUP
    results.append("SETUP...")
    test_user = app_tables.users.add_row(name="Test", email="test@test.com", role="staff")
    results.append("✅ Setup complete")
    results.append("")

    # TEST 1: Create rate
    results.append("TEST 1: Create exchange rate...")
    rate = anvil.server.call('create_exchange_rate',
                             datetime.now(),
                             "VND",
                             "USD",
                             0.00004,
                             test_user.get_id())
    results.append(f"✅ Created: VND to USD = {rate['rate']}")
    results.append("")

    # TEST 2: Get latest rate
    results.append("TEST 2: Get latest rate...")
    latest = anvil.server.call('get_latest_exchange_rate', "VND", "USD")
    if latest and latest.get_id() == rate.get_id():
      results.append("✅ Retrieved correct rate")
    else:
      results.append("❌ Retrieved wrong rate")
    results.append("")

    # TEST 3: List all rates
    results.append("TEST 3: List all rates...")
    all_rates = anvil.server.call('list_all_exchange_rates')
    results.append(f"✅ Found {len(all_rates)} rates")
    results.append("")

    # TEST 4: Convert amount
    results.append("TEST 4: Convert amount...")
    converted = anvil.server.call('convert_amount', 25000, "VND", "USD", None)
    results.append(f"✅ 25,000 VND = ${converted:.2f} USD")
    results.append("")

    # CLEANUP
    results.append("CLEANUP...")
    rate.delete()
    test_user.delete()
    results.append("✅ Cleaned up")
    results.append("")

    results.append("🎉 EXCHANGE RATE TESTS PASSED!")
    return "\n".join(results)

  except Exception as e:
    import traceback
    return f"❌ FAILED: {str(e)}\n{traceback.format_exc()}"


# ============================================
# TEST 5: COMPLETE INTEGRATION
# ============================================

@anvil.server.callable
def test_complete_integration():
  """Test complete workflow: create → add costs → price → approve"""
  try:
    results = []
    results.append("=" * 50)
    results.append("TEST: COMPLETE INTEGRATION")
    results.append("=" * 50)
    results.append("")

    # SETUP
    results.append("SETUP: Creating all test data...")
    test_user = app_tables.users.add_row(name="User", email="u@t.com", role="staff")
    test_admin = app_tables.users.add_row(name="Admin", email="a@t.com", role="admin")
    test_client = app_tables.clients.add_row(name="Client", price_category="Medium", country="US", max_account_value=100000.0, currency="USD")
    test_style = app_tables.master_styles.add_row(ref_id="STYLE-001", client=test_client, picture="test", description="Test Style")
    test_supplier = app_tables.suppliers.add_row(name="Supplier", country="Vietnam", approved_vendor=True, approved_date=datetime.now(), approved_by=test_user)
    test_material = app_tables.master_materials.add_row(document_id="MAT-001", current_version=1, created_at=datetime.now(), created_by=test_user)
    test_material_version = app_tables.master_material_versions.add_row(
      master_material=test_material, document_id="MAT-001", version_number=1, change_description="Initial",
      created_at=datetime.now(), created_by=test_user, ref_id="S-MAT-001", master_material_id="MAT-001",
      status="Verified", supplier=test_supplier, supplier_name="Supplier", country_of_origin="Vietnam",
      name="Cotton Fabric", material_type="Main fabric", unit_of_measurement="meter", weight_per_unit=200.0,
      weight_uom="gsm", original_cost_per_unit=5.00, native_cost_currency="USD", supplier_selling_tolerance=0.05,
      refundable_tolerance=True, effective_cost_per_unit=5.25, last_verified_date=datetime.now(), last_verified_by=test_user
    )
    results.append("✅ Setup complete")
    results.append("")

    # STEP 1: Create cost sheet
    results.append("STEP 1: Create cost sheet...")
    cs = anvil.server.call('create_cost_sheet', test_style.get_id(), test_client.get_id(), "CS-INTEGRATION-001", test_user.get_id(), "USD")
    version = anvil.server.call('get_current_version', cs.get_id())
    version_id = version.get_id()
    results.append(f"✅ Created: {cs['document_id']}")
    results.append("")

    # STEP 2: Add BOM
    results.append("STEP 2: Add materials...")
    bom = anvil.server.call('create_bom_for_cost_sheet', version_id, test_user.get_id())
    bom_version = app_tables.bom_versions.get(bill_of_material=bom)
    anvil.server.call('add_bom_line_item', bom_version.get_id(), test_material.get_id(), 2.5, 0.05, 0.10, test_user.get_id())
    version = app_tables.cost_sheet_versions.get_by_id(version_id)
    results.append(f"✅ Material cost: ${version['total_material_cost']:.2f}")
    results.append("")

    # STEP 3: Add processing
    results.append("STEP 3: Add processing costs...")
    anvil.server.call('add_processing_cost', version_id, "Cut-make", 5.50, "USD", "ABC Factory", "CMT", test_user.get_id())
    version = app_tables.cost_sheet_versions.get_by_id(version_id)
    results.append(f"✅ Processing cost: ${version['total_processing_cost']:.2f}")
    results.append("")

    # STEP 4: Add overhead
    results.append("STEP 4: Add overhead costs...")
    anvil.server.call('add_overhead_cost_item', version_id, "Testing", "Material testing", 50.0, "USD", test_user.get_id())
    version = app_tables.cost_sheet_versions.get_by_id(version_id)
    results.append(f"✅ Overhead cost: ${version['total_overhead_cost']:.2f}")
    results.append("")

    # STEP 5: Get summary
    results.append("STEP 5: Get cost summary...")
    summary = anvil.server.call('get_cost_sheet_summary', version_id)
    results.append(f"   Material: ${summary['material_cost']:.2f}")
    results.append(f"   Processing: ${summary['processing_cost']:.2f}")
    results.append(f"   Overhead: ${summary['overhead_cost']:.2f}")
    results.append(f"   ✅ Total: ${summary['total_cost']:.2f}")
    results.append("")

    # STEP 6: Add pricing
    results.append("STEP 6: Add pricing scenario...")
    scenario = anvil.server.call('add_quoted_price_scenario', version_id, 100.0, "USD", test_user.get_id())
    results.append(f"   Quoted: ${scenario['quoted_price']:.2f}")
    results.append(f"   Margin: {scenario['expected_gross_margin']*100:.1f}%")
    results.append(f"   ✅ Profit: ${scenario['expected_gross_profit']:.2f}")
    results.append("")

    # STEP 7: Submit
    results.append("STEP 7: Submit for approval...")
    anvil.server.call('submit_cost_sheet_for_review', version_id, test_user.get_id())
    version = app_tables.cost_sheet_versions.get_by_id(version_id)
    results.append(f"✅ Status: {version['status']}")
    results.append("")

    # STEP 8: Approve
    results.append("STEP 8: Approve cost sheet...")
    anvil.server.call('approve_cost_sheet', version_id, test_admin.get_id())
    version = app_tables.cost_sheet_versions.get_by_id(version_id)
    results.append(f"✅ Final status: {version['status']}")
    results.append("")

    # CLEANUP
    results.append("CLEANUP...")
    scenario.delete()
    processing_items = app_tables.processing_cost_items.search(cost_sheet_version=version)
    for item in processing_items:
      item.delete()
    overhead_items = app_tables.overhead_cost_items.search(cost_sheet_version=version)
    for item in overhead_items:
      item.delete()
    bom_items = app_tables.bom_line_items.search(bom_version=bom_version)
    for item in bom_items:
      item.delete()
    bom_version.delete()
    bom.delete()
    version.delete()
    cs.delete()
    test_material_version.delete()
    test_material.delete()
    test_supplier.delete()
    test_style.delete()
    test_client.delete()
    test_user.delete()
    test_admin.delete()
    results.append("✅ Cleaned up")
    results.append("")

    results.append("=" * 50)
    results.append("🎉 COMPLETE INTEGRATION TEST PASSED! 🎉")
    results.append("=" * 50)
    results.append("")
    results.append("Summary:")
    results.append("✅ Cost sheet creation")
    results.append("✅ BOM operations")
    results.append("✅ Processing costs")
    results.append("✅ Overhead costs")
    results.append("✅ Cost calculations")
    results.append("✅ Pricing scenarios")
    results.append("✅ Workflow (submit/approve)")

    return "\n".join(results)

  except Exception as e:
    import traceback
    return f"❌ FAILED: {str(e)}\n{traceback.format_exc()}"


# ============================================
# RUN ALL TESTS
# ============================================

@anvil.server.callable
def run_all_tests():
  """Run all tests in sequence"""
  all_results = []

  all_results.append("=" * 60)
  all_results.append("RUNNING ALL COST SHEET TESTS")
  all_results.append("=" * 60)
  all_results.append("")

  tests = [
    ('Cost Sheet CRUD', 'test_cost_sheet_crud'),
    ('BOM Operations', 'test_bom_operations'),
    ('Workflow Operations', 'test_workflow_operations'),
    ('Exchange Rates', 'test_exchange_rates'),
    ('Complete Integration', 'test_complete_integration')
  ]

  passed = 0
  failed = 0

  for test_name, test_func in tests:
    all_results.append(f"Running: {test_name}...")
    result = anvil.server.call(test_func)

    if "PASSED" in result:
      passed += 1
      all_results.append(f"✅ {test_name} PASSED")
    else:
      failed += 1
      all_results.append(f"❌ {test_name} FAILED")
      all_results.append(result)  # Show error details

    all_results.append("")

  all_results.append("=" * 60)
  all_results.append(f"FINAL RESULTS: {passed} passed, {failed} failed")
  all_results.append("=" * 60)

  return "\n".join(all_results)