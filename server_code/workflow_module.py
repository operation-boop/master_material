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

# Import helper functions
from . import cost_sheet_helpers as helpers

"""
Workflow Operations Module
Handles cost sheet approval workflow (Submit, Approve, Reject).
"""

@anvil.server.callable
def submit_cost_sheet_for_review(cost_sheet_version_id, user_id):
  """
    Submit a cost sheet version for supervisor review.
    Changes status from Draft to Under review.
    
    Args:
        cost_sheet_version_id: Which cost sheet version to submit
        user_id: Who is submitting this
    
    Returns:
        The updated cost sheet version
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)
  user = app_tables.users.get_by_id(user_id)

  cost_sheet_version['status'] = "Under review"
  cost_sheet_version['submitted_at'] = datetime.now()
  cost_sheet_version['submitted_by'] = user

  print(f"[Workflow] Submitted cost sheet version {cost_sheet_version['version_number']} for review")
  return cost_sheet_version


@anvil.server.callable
def approve_cost_sheet(cost_sheet_version_id, user_id):
  """
    Approve a cost sheet version (supervisor action).
    Changes status from Under review to Approved.
    
    Args:
        cost_sheet_version_id: Which cost sheet version to approve
        user_id: Who is approving (should be supervisor)
    
    Returns:
        The updated cost sheet version
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)
  user = app_tables.users.get_by_id(user_id)

  cost_sheet_version['status'] = "Approved"
  cost_sheet_version['approved_at'] = datetime.now()
  cost_sheet_version['approved_by'] = user

  print(f"[Workflow] Approved cost sheet version {cost_sheet_version['version_number']}")
  return cost_sheet_version


@anvil.server.callable
def reject_cost_sheet(cost_sheet_version_id, user_id, rejection_reason=None):
  """
    Reject a cost sheet version (supervisor action).
    Changes status from Under review to Rejected.
    
    Args:
        cost_sheet_version_id: Which cost sheet version to reject
        user_id: Who is rejecting (should be supervisor)
        rejection_reason: Optional - reason for rejection
    
    Returns:
        The updated cost sheet version
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)
  user = app_tables.users.get_by_id(user_id)

  cost_sheet_version['status'] = "Rejected"
  cost_sheet_version['approved_at'] = datetime.now()
  cost_sheet_version['approved_by'] = user

  # Store rejection reason if provided (you may need to add this column)
  if rejection_reason:
    cost_sheet_version['rejection_reason'] = rejection_reason

  print(f"[Workflow] Rejected cost sheet version {cost_sheet_version['version_number']}")
  return cost_sheet_version


@anvil.server.callable
def get_pending_approvals():
  """
    Get all cost sheet versions waiting for approval.
    Useful for supervisor dashboard.
    
    Returns:
        List of cost sheet versions with status "Under review"
    """

  pending = app_tables.cost_sheet_versions.search(
    status="Under review"
  )

  # Sort by submission date (oldest first for fairness)
  sorted_pending = sorted(pending, key=lambda x: x['submitted_at'])

  return sorted_pending


@anvil.server.callable
def get_my_submitted_cost_sheets(user_id):
  """
    Get all cost sheets submitted by a specific user.
    Useful for user dashboard to track their submissions.
    
    Args:
        user_id: Which user's submissions to get
    
    Returns:
        List of cost sheet versions submitted by this user
    """

  user = app_tables.users.get_by_id(user_id)

  submissions = app_tables.cost_sheet_versions.search(
    submitted_by=user
  )

  # Sort by submission date (newest first)
  sorted_submissions = sorted(submissions, key=lambda x: x['submitted_at'], reverse=True)

  return sorted_submissions


@anvil.server.callable
def get_workflow_history(cost_sheet_id):
  """
    Get the complete workflow history of a cost sheet.
    Shows all versions and their approval status.
    
    Args:
        cost_sheet_id: Which cost sheet to get history for
    
    Returns:
        List of all versions with workflow info
    """

  cost_sheet = app_tables.cost_sheets.get_by_id(cost_sheet_id)

  versions = app_tables.cost_sheet_versions.search(
    cost_sheet=cost_sheet
  )

  # Sort by version number
  sorted_versions = sorted(versions, key=lambda x: x['version_number'])

  history = []
  for version in sorted_versions:
    history.append({
      'version_number': version['version_number'],
      'status': version['status'],
      'created_at': version['created_at'],
      'created_by': version['created_by']['name'] if version['created_by'] else None,
      'submitted_at': version['submitted_at'],
      'submitted_by': version['submitted_by']['name'] if version['submitted_by'] else None,
      'approved_at': version['approved_at'],
      'approved_by': version['approved_by']['name'] if version['approved_by'] else None,
      'change_description': version['change_description']
    })

  return history


@anvil.server.callable
def can_user_approve(user_id):
  """
    Check if a user has permission to approve cost sheets.
    For MVP, checks if user role is "admin".
    
    Args:
        user_id: Which user to check
    
    Returns:
        True if user can approve, False otherwise
    """

  user = app_tables.users.get_by_id(user_id)

  # For MVP, only admins can approve
  can_approve = (user['role'] == "admin")

  return can_approve


@anvil.server.callable
def reopen_cost_sheet(cost_sheet_version_id, user_id):
  """
    Reopen a rejected cost sheet back to Draft status.
    Allows user to make changes and resubmit.
    
    Args:
        cost_sheet_version_id: Which cost sheet version to reopen
        user_id: Who is reopening this
    
    Returns:
        The updated cost sheet version
    """

  cost_sheet_version = app_tables.cost_sheet_versions.get_by_id(cost_sheet_version_id)
  user = app_tables.users.get_by_id(user_id)

  # Only allow reopening if current status is Rejected
  if cost_sheet_version['status'] != "Rejected":
    print(f"[Workflow] Cannot reopen - current status is {cost_sheet_version['status']}")
    return None

  cost_sheet_version['status'] = "Draft"

  print(f"[Workflow] Reopened cost sheet version {cost_sheet_version['version_number']} to Draft")
  return cost_sheet_version
