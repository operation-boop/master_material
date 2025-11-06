from ._anvil_designer import draft_to_be_deleteTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class draft_to_be_delete(draft_to_be_deleteTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    all_cost_sheets = anvil.server.call('list_all_cost_sheets')
    all_cost_sheet_versions = anvil.server.call('list_all_cost_sheet_versions')

    print(len(all_cost_sheets))
    
    print(all_cost_sheets[0])

    for cost_sheet in all_cost_sheets:
      print(cost_sheet)
      cost_sheet_copy = dict(cost_sheet)
      print(cost_sheet_copy)
      print(cost_sheet_copy == cost_sheet)

    for cost_sheet_version in all_cost_sheet_versions:
      print(dict(cost_sheet_version))
