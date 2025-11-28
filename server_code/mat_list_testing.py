import anvil.users
import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from typing import List, Optional
from pydantic import BaseModel, Field
from api_framework import APIEndpoint


class MaterialCard(BaseModel):
  """Represents a single material card for UI display"""
  document_id: str
  master_material_id: str
  ref_id: str
  material_name: str
  material_type: str
  fabric_composition: str
  weight: str
  supplier: str
  cost_per_unit: str
  verification_status: str
  ver_num: str

# --- STEP 2: Define the Search Filters (Input) ---
class ListMaterialCardsRequest(BaseModel):
  """Filters for listing material cards"""
  statuses: Optional[List[str]] = Field(
    None, 
    description="List of statuses to include. Defaults to active statuses if empty.",
    example=["Draft", "Submitted - Verified"]
  )

# --- STEP 3: The Integration ---
@APIEndpoint(
  name="list_material_cards",
  request_model=ListMaterialCardsRequest,
  response_model=List[MaterialCard],  # Returns a LIST of cards
  summary="List Material Cards",
  description="Get a list of material cards formatted for UI display, filtered by status.",
  tags=["Materials", "UI"]
)
def list_material_cards(request: ListMaterialCardsRequest):
  statuses = request.statuses or ["Draft", "Submitted - Unverified", "Submitted - Verified"]
  masters = app_tables.master_material.search()
  cards = []
  for master in masters:
    version = master['current_version']
    if not version:
      continue

      # Filter by status
    if version['status'] not in statuses:
      continue

      # Build display strings (Original Logic)
    wpu = version['weight_per_unit']
    wuom = version['weight_uom']
    weight = f"{wpu} {wuom}" if (wpu and wuom) else ""

    ocpu = version['original_cost_per_unit']
    nccy = version['native_cost_currency']
    cost = f"{ocpu} {nccy}" if (ocpu and nccy) else ""

    # Append to list (Original Logic)
    # Pydantic will validate this dict against the MaterialCard model automatically
    cards.append({
      "document_id": master['document_id'] or " ",
      "master_material_id": version['master_material_id'] or " ",
      "ref_id": version['ref_id'] or " ",
      "material_name": version['name'] or " ",
      "material_type": version['material_type'] or " ",
      "fabric_composition": version['fabric_composition'] or " ",
      "weight": weight or " ",
      "supplier": version['supplier_name'] or " ",
      "cost_per_unit": cost or " ",
      "verification_status": version['status'] or "Draft",
      # Ensure ver_num is string to match the " " fallback
      "ver_num": str(version['ver_num']) if version['ver_num'] else " ",
    })

  return cards