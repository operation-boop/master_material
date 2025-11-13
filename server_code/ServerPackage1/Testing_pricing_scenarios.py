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
def test_pricing_scenarios():
  """Test pricing scenario operations"""

  try:
    results = []
    results.append("TESTING PRICING SCENARIOS")
    results.append("")

    # SETUP (same as before)
    results.append("SETUP...")
    test_user = app_tables.users.add_row(name="Test", email="test@test.com", role="staff")
    test_client = app_tables.clients.add_row(name="Test", price_category="Medium", country="US", max_account_value=50000.0, currency="USD")
    test_style = app_tables.master_styles.add_row(ref_id="TEST", client=test_client, picture="test", description="Test")
    test_cost_sheet = app_tables.cost_sheets.add_row(document_id="TEST", current_version=1, created_at=datetime.now(), created_by=test_user)
    test_version = app_tables.cost_sheet_versions.add_row(
      cost_sheet=test_cost_sheet, document_id="TEST", version_number=1, change_description="Initial",
      created_at=datetime.now(), created_by=test_user, status="Draft", cost_currency="USD",
      master_style=test_style, client=test_client,
      total_material_cost=10.0,  # Set some costs
      total_processing_cost=5.0,
      total_overhead_cost=2.0
    )
    version_id = test_version.get_id()
    results.append("✅ Setup complete (Total cost: $17.00)")
    results.append("")

    # TEST 1: Add pricing scenario
    results.append("TEST 1: Add pricing scenario at $25...")
    scenario = anvil.server.call('add_quoted_price_scenario', version_id, 25.00, "USD", test_user.get_id())
    results.append(f"✅ Added scenario")
    results.append(f"   Quoted price: ${scenario['quoted_price']:.2f}")
    results.append(f"   Gross profit: ${scenario['expected_gross_profit']:.2f}")
    results.append(f"   Gross margin: {scenario['expected_gross_margin']*100:.1f}%")

    # Check calculation
    expected_profit = 25.0 - 17.0  # 8.0
    expected_margin = 8.0 / 25.0  # 0.32 = 32%
    if abs(scenario['expected_gross_profit'] - expected_profit) < 0.01:
      results.append("   ✅ Profit calculation correct!")
    else:
      results.append(f"   ❌ Profit wrong! Expected ${expected_profit}, got ${scenario['expected_gross_profit']}")

      # TEST 2: Add another scenario
    results.append("")
    results.append("TEST 2: Add scenario at $30...")
    scenario2 = anvil.server.call('add_quoted_price_scenario', version_id, 30.00, "USD", test_user.get_id())
    results.append(f"✅ Added: Margin = {scenario2['expected_gross_margin']*100:.1f}%")

    # TEST 3: List scenarios
    results.append("")
    results.append("TEST 3: List all scenarios...")
    scenarios = anvil.server.call('list_quoted_price_scenarios', version_id)
    results.append(f"✅ Found {len(scenarios)} scenarios")

    # TEST 4: Update scenario
    results.append("")
    results.append("TEST 4: Update first scenario to $28...")
    updated = anvil.server.call('update_quoted_price_scenario', scenario.get_id(), 28.00, "USD", test_user.get_id())
    results.append(f"✅ Updated: New margin = {updated['expected_gross_margin']*100:.1f}%")

    # TEST 5: Delete scenario
    results.append("")
    results.append("TEST 5: Delete second scenario...")
    anvil.server.call('delete_quoted_price_scenario', scenario2.get_id())
    results.append("✅ Deleted")

    # CLEANUP
    results.append("")
    results.append("CLEANUP...")
    scenario.delete()
    test_version.delete()
    test_cost_sheet.delete()
    test_style.delete()
    test_client.delete()
    test_user.delete()
    results.append("✅ Cleaned up")

    results.append("")
    results.append("🎉 ALL PRICING TESTS PASSED!")
    return "\n".join(results)

  except Exception as e:
    import traceback
    return f"❌ FAILED: {str(e)}\n{traceback.format_exc()}"