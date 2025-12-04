import anvil.users
import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
from pydantic import BaseModel, Field
from .api_framework import APIEndpoint
from typing import List, Optional

# --- SKU Models ---

class SkuRequest(BaseModel):
  """Request to fetch SKUs for a specific material"""
  document_id: str = Field(..., description="The Master Material ID (e.g., MAT-001)")

class CreateSkuRequest(BaseModel):
  """Request to create a new SKU"""
  document_id: str = Field(..., description="The Master Material ID to link this SKU to")
  ref_id: str = Field(..., description="External Reference ID")
  qr_data: str = Field(..., description="QR Code content")
  sku_cost_override: float = Field(0.0, description="Cost override for this specific SKU")
  color: Optional[str] = Field(None, description="Color variant")
  size: Optional[str] = Field(None, description="Size variant")

class SkuResponse(BaseModel):
  """Response model for a single SKU"""
  id: str
  ref_id: str
  qr_data: str
  sku_cost_override: float
  color: Optional[str] = None
  size: Optional[str] = None

# --- SKU ENDPOINTS ---

@anvil.server.route("/get_material_sku")
@APIEndpoint(
  name="get_material_sku",
  request_model=SkuRequest,
  response_model=List[SkuResponse],  # Returns a LIST of SKUs
  summary="Get SKUs for Material",
  tags=["SKU Inventory"]
)
def get_material_sku(request: SkuRequest):
  master_row = app_tables.master_material.get(document_id=request.document_id)

  if not master_row:
    # Return empty list if material not found (or raise 404 if you prefer)
    return []

  # Search using the ROW object
  skus = app_tables.material_sku.search(master_material=master_row)

  # Convert Anvil Rows to Dictionaries for Pydantic
  return [
    {
      "id": s['id'],
      "ref_id": s['ref_id'],
      "qr_data": s['qr_data'],
      "sku_cost_override": s['sku_cost_override'] or 0.0,
      "color": s['color'],
      "size": s['size']
    }
    for s in skus
  ]


@anvil.server.route("/create_material_sku")
@APIEndpoint(
  name="create_material_sku",
  request_model=CreateSkuRequest,
  response_model=SkuResponse, # Returns the created SKU
  summary="Create New SKU",
  tags=["SKU Inventory"]
)
def create_material_sku(request: CreateSkuRequest):
  # 1. Fetch Master Material
  master_row = app_tables.master_material.get(document_id=request.document_id)
  if not master_row:
    raise Exception(f"Master material not found for document_id {request.document_id}")

  # 2. Generate ID (Safe Logic)
  # Note: searching all rows to find max ID is slow as database grows. 
  # Ideally, use a dedicated 'counters' table. For now, we keep your logic but make it safer.
  last_sku = app_tables.material_sku.search(tables.order_by("id", ascending=False))

  if len(last_sku) > 0 and last_sku[0]['id'].startswith("SKU"):
    try:
      last_num = int(last_sku[0]['id'][3:])
      new_sku_id = f"SKU{last_num + 1:03d}"
    except ValueError:
      new_sku_id = f"SKU{len(last_sku) + 1:03d}" # Fallback
  else:
    new_sku_id = "SKU001"

  # 3. Create the Row
  new_row = app_tables.material_sku.add_row(
    id=new_sku_id,
    master_material=master_row,
    ref_id=request.ref_id,
    qr_data=request.qr_data,
    sku_cost_override=request.sku_cost_override,
    color=request.color,
    size=request.size
  )

  # 4. Return the new row as a dict
  return {
    "id": new_row['id'],
    "ref_id": new_row['ref_id'],
    "qr_data": new_row['qr_data'],
    "sku_cost_override": new_row['sku_cost_override'] or 0.0,
    "color": new_row['color'],
    "size": new_row['size']
  }
