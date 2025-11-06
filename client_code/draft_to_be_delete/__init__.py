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
    # all_cost_sheets = anvil.server.call('list_all_cost_sheets')
    # all_cost_sheet_versions = anvil.server.call('list_all_cost_sheet_versions')

    # print(len(all_cost_sheets))
    
    # print(all_cost_sheets[0])

    # for cost_sheet in all_cost_sheets:
    #   print(cost_sheet.get_id())
    #   cost_sheet_copy = dict(cost_sheet)
    #   print(cost_sheet_copy)
    #   print(cost_sheet_copy == cost_sheet)

    # for cost_sheet_version in all_cost_sheet_versions:
    #   print(dict(cost_sheet_version))

    # # show simple list + get each detail on-demand
    # list_of_cost_sheets_simple = anvil.server.call('list_all_cost_sheets_simple')
    # print(list_of_cost_sheets_simple)

    # list_of_cost_sheet_versions_simple = anvil.server.call('list_all_cost_sheet_versions_simple')
    # print(list_of_cost_sheet_versions_simple)
    
    # id_of_clicked_cost_sheet = list_of_cost_sheets_simple[0]['id']
    # cost_sheet_detail = anvil.server.call('get_cost_sheet_with_id', id_of_clicked_cost_sheet)
    # print(dict(cost_sheet_detail))

    # get versions pertaining only the the cost sheet
    # method 1: whole row sent over to UI
    all_cost_sheets = anvil.server.call('list_all_cost_sheets')
    clicked_cost_sheet = all_cost_sheets[0]
    print(clicked_cost_sheet['version_history'])
    most_recent_version = anvil.server.call('get_cost_sheet_version_with_id', clicked_cost_sheet['current_version_id'])

    clicked_id = clicked_cost_sheet['current_version_id']
    print(most_recent_version)
    print(clicked_id)

    list_of_cost_sheet_versions_simple = anvil.server.call('list_all_cost_sheet_versions_simple')
    print(list_of_cost_sheet_versions_simple)

    target_id = list_of_cost_sheet_versions_simple[0]['id']
    print(target_id)
    print(clicked_id == target_id)

    print(dict(most_recent_version))