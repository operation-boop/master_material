from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Individual test buttons
  def button_test_crud_click(self, **event_args):
    result = anvil.server.call('test_cost_sheet_crud')
    print(result)
    alert(result, large=True)

  def button_test_bom_click(self, **event_args):
    result = anvil.server.call('test_bom_operations')
    print(result)
    alert(result, large=True)

  def button_test_workflow_click(self, **event_args):
    result = anvil.server.call('test_workflow_operations')
    print(result)
    alert(result, large=True)

  def button_test_exchange_click(self, **event_args):
    result = anvil.server.call('test_exchange_rates')
    print(result)
    alert(result, large=True)

  def button_test_integration_click(self, **event_args):
    result = anvil.server.call('test_complete_integration')
    print(result)
    alert(result, large=True)

    # Run all tests
  def button_run_all_tests_click(self, **event_args):
    self.label_status.text = "Running all tests..."
    result = anvil.server.call('run_all_tests')
    print(result)
    alert(result, large=True)

    if "failed: 0" in result:
      self.label_status.text = "✅ All tests passed!"
    else:
      self.label_status.text = "❌ Some tests failed"