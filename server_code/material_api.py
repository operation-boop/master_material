from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import anvil.users
import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from api_framework import APIEndpoint

# ============================================================================
# 1. MODELS (The Inputs and Outputs)
# ============================================================================

# --- Shared Request Model ---
class MaterialIDRequest(BaseModel):
  """Standard request for any endpoint requiring a document_id"""
  document_id: str = Field(..., description="The unique document ID of the material")

# --- Response Models ---
class MaterialDetailResponse(BaseModel):
  document_id: str
  ver_num: str
  master_material_id: str
  name: str
  ref_id: str
  material_type: str
  supplier: str
  country_of_origin: str
  created_by: str
  created_at: Optional[Any] # Accepts datetime or string
  fabric_composition: str
  weight_per_unit: Optional[Any] # Accepts float or string " "
  fabric_roll_width: Optional[Any]
  fabric_cut_width: Optional[Any]
  original_cost_per_unit: Optional[float]
  cost_display: str
  unit_of_measurement: str
  verification_status: str
  updated_at: Optional[Any] = None
  submitted_at: Optional[Any] = None
  last_verified_date: Optional[Any] = None
  
class TechnicalDetailResponse(BaseModel):
  fabric_composition: Optional[str] = None
  fabric_roll_width: Optional[float] = None
  fabric_cut_width: Optional[float] = None
  fabric_cut_width_no_shrinkage: Optional[float] = None
  weight_per_unit: Optional[float] = None
  weft_shrinkage: Optional[float] = None
  werp_shrinkage: Optional[float] = None

class CostDetailResponse(BaseModel):
  original_cost_per_unit: Optional[float] = None
  currency: Optional[str] = None
  supplier_tolerance: Optional[float] = None
  effective_cost: Optional[float] = None
  vat: Optional[float] = None
  import_duty: Optional[float] = None
  logistics_rate: Optional[float] = None
  landed_cost: Optional[float] = None

class VersionHistoryItem(BaseModel):
  """A single item in the version history list"""
  ver_num: int
  submitted_by: str
  submitted_at: Optional[Any] = None
  change_description: str

# ============================================================================
# 2. HELPERS
# ============================================================================

def _get(row, key, default=None):
  """Safely get a value from a row"""
  try:
    val = row[key]
    return val if val is not None else default
  except Exception:
    return default

def _fetch_material_version(document_id):
  """Common logic to get the master and version row"""
  if not document_id:
    raise ValueError("document_id is required")

  master = app_tables.master_material.get(document_id=document_id)
  if not master:
    raise Exception(f"No material found for ID: {document_id}")

  v = master['current_version']
  if not v:
    raise Exception(f"No current version found for ID: {document_id}")

  return master, v

# ============================================================================
# 3. API ENDPOINTS
# ============================================================================
@APIEndpoint(
  name="get_material_detail",
  request_model=MaterialIDRequest,
  response_model=MaterialDetailResponse,
  summary="Get Material Dashboard Details",
  tags=["Materials", "Dashboard"]
)
def get_material_detail(request: MaterialIDRequest):
  _, v = _fetch_material_version(request.document_id)

  # Cost logic
  ocpu = _get(v, "original_cost_per_unit")
  nccy = _get(v, "native_cost_currency")
  cost_display = f"{ocpu} {nccy}" if (ocpu is not None and nccy) else ""

  return {
    "document_id": _get(v, "document_id", " "),
    "ver_num": str(_get(v, "ver_num", " ")), # Cast to str to be safe
    "master_material_id": _get(v, "master_material_id", " "),
    "name": _get(v, "name", " "),
    "ref_id": _get(v, "ref_id", " "),
    "material_type": _get(v, "material_type", " "),
    "supplier": _get(v, "supplier_name", " "),
    "country_of_origin": _get(v, "country_of_origin", " "),
    "created_by": _get(v, "created_by", " "),
    "created_at": _get(v, "created_at", " "),
    "fabric_composition": _get(v, "fabric_composition", " "),
    "weight_per_unit": _get(v, "weight_per_unit", " "),
    "fabric_roll_width": _get(v, "fabric_roll_width", " "),
    "fabric_cut_width": _get(v, "fabric_cut_width", " "),
    "original_cost_per_unit": ocpu,
    "cost_display": cost_display,
    "unit_of_measurement": _get(v, "unit_of_measurement", " "),
    "verification_status": _get(v, "status", "Draft"),
    "updated_at": _get(v, "updated_at"),
    "submitted_at": _get(v, "submitted_at"),
    "last_verified_date": _get(v, "last_verified_date"),
  }
  ##-------------------------------------------------------------------------------------------------------------------------
  
@APIEndpoint(
  name="get_technical_detail",
  request_model=MaterialIDRequest,
  response_model=TechnicalDetailResponse,
  summary="Get Technical Specifications",
  tags=["Materials", "Technical"]
)
def get_technical_detail(request: MaterialIDRequest):
  _, v = _fetch_material_version(request.document_id)

  return {
    "fabric_composition": _get(v, "fabric_composition"),
    "fabric_roll_width": _get(v, "fabric_roll_width"),
    "fabric_cut_width": _get(v, "fabric_cut_width"),
    "fabric_cut_width_no_shrinkage": _get(v, "fabric_cut_width_no_shrinkage"),
    "weight_per_unit": _get(v, "weight_per_unit"),
    "weft_shrinkage": _get(v, "weft_shrinkage"),
    "werp_shrinkage": _get(v, "werp_shrinkage"),
  }
  ##-------------------------------------------------------------------------------------------------------------------------
  
@APIEndpoint(
  name="get_cost_detail",
  request_model=MaterialIDRequest,
  response_model=CostDetailResponse,
  summary="Get Cost Breakdown",
  tags=["Materials", "Financial"]
)
def get_cost_detail(request: MaterialIDRequest):
  _, v = _fetch_material_version(request.document_id)

  return {
    "original_cost_per_unit": _get(v, "original_cost_per_unit"),
    "currency": _get(v, "native_cost_currency"),
    "supplier_tolerance": _get(v, "supplier_selling_tolerance"),
    "effective_cost": _get(v, "effective_cost_per_unit"),
    "vat": _get(v, "vietnam_vat_rate"),
    "import_duty": _get(v, "import_duty"),
    "logistics_rate": _get(v, "logistics_rate"),
    "landed_cost": _get(v, "landed_cost_per_unit"),
  }
  ##------------------------------------------------------------------------------------------------------------------------- 
@APIEndpoint(
  name="get_version_history",
  request_model=MaterialIDRequest,
  response_model=List[VersionHistoryItem], # Returns a LIST
  summary="Get Version History",
  tags=["Materials", "History"]
)
def get_version_history(request: MaterialIDRequest):
  master = app_tables.master_material.get(document_id=request.document_id)
  if not master:
    return []

  versions = list(master['version_history'] or [])
  versions.sort(key=lambda v: v['ver_num'])

  return [
    {
      "ver_num": int(v['ver_num']),
      "submitted_by": v.get('submitted_by', '') or '',
      "submitted_at": v.get('submitted_at', None),
      "change_description": v.get('change_description', '') or ''
    }
    for v in versions
  ]
  ##-------------------------------------------------------------------------------------------------------------------------

@APIEndpoint(
  name="get_material_full_row",
  request_model=MaterialIDRequest,
  response_model=Dict[str, Any], # Returns a generic Dictionary
  summary="Get Full Material Row",
  description="Returns the raw database row for editing purposes",
  tags=["Materials", "Internal"]
)
def get_material_full_row(request: MaterialIDRequest):
  master = app_tables.master_material.get(document_id=request.document_id)
  if not master:
    return {} # Return empty dict instead of None for easier UI handling

  version = master['current_version']
  if not version:
    return {}

    # Convert to dict
  result = dict(version)
  # Add status field manually for form compatibility
  result['verification_status'] = version['status']

  return result
  ##-------------------------------------------------------------------------------------------------------------------------