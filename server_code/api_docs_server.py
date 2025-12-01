import anvil.server
import anvil.users
from anvil import BlobMedia
import json
from pydantic import TypeAdapter
from api_framework import APIRegistry

# 1. Import your API definitions so they register themselves
import material_api
import materialcard_api
import admin_api

# Define your API base URL
API_PREFIX = "/api/v1"

# ========================================================
# PART 1: HTTP HANDLER LOGIC
# ========================================================

def create_http_handler(endpoint_name, endpoint_obj):
  """
    Dynamically creates an HTTP endpoint for a given API function.
    """
  @anvil.server.http_endpoint(f"{API_PREFIX}/{endpoint_name}", methods=["POST"])
  def http_wrapper(**kwargs):
    try:
      # A. Get the Input
      req_body = anvil.server.request.body_json
      data = req_body if req_body else kwargs

      # B. Run your existing Logic
      result = endpoint_obj(data)

      # C. Return the Result
      return result

    except Exception as e:
      # D. Handle Errors
      return {
        "error": "API Execution Error",
        "message": str(e)
      }

  return http_wrapper

def register_http_endpoints():
  """
    Finds all registered API endpoints and creates HTTP routes for them.
    """
  endpoints = APIRegistry.get_all_endpoints()
  print(f"--- Setting up HTTP Interface for {len(endpoints)} endpoints ---")

  for name, endpoint in endpoints.items():
    create_http_handler(name, endpoint)
    print(f"  > Online: {anvil.server.get_app_origin()}{API_PREFIX}/{name}")

# ========================================================
# PART 2: DOCUMENTATION ENDPOINTS (Swagger UI)
# ========================================================

@anvil.server.http_endpoint(f"{API_PREFIX}/docs", methods=["GET"])
def get_docs_page():
  spec_url = f"{anvil.server.get_app_origin()}{API_PREFIX}/docs/openapi.json"
  html = f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <title>API Docs</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js" crossorigin></script>
        <script>
          window.onload = () => {{
            window.ui = SwaggerUIBundle({{ url: "{spec_url}", dom_id: '#swagger-ui' }});
          }};
        </script>
      </body>
    </html>
    """
  return BlobMedia("text/html", html.encode(), name="docs.html")

@anvil.server.http_endpoint(f"{API_PREFIX}/docs/openapi.json", methods=["GET"])
def get_openapi_spec_http():
  """Returns the JSON spec for the HTTP Swagger UI"""
  return APIRegistry.generate_documentation()

# ========================================================
# PART 3: INTERNAL ANVIL FUNCTIONS (For your UI)
# ========================================================

@anvil.server.callable
def get_api_documentation():
  """
    Returns API documentation in a format suitable for the front-end viewer
    """
  docs = APIRegistry.get_all_endpoints()

  # (Your existing helper function for schemas)
  def get_properties_from_schema(schema_root):
    if not schema_root: return {}
    if '$ref' in schema_root:
      ref_name = schema_root['$ref'].split('/')[-1]
      if '$defs' in schema_root and ref_name in schema_root['$defs']:
        return schema_root['$defs'][ref_name].get('properties', {})
      return {}
    if schema_root.get('type') == 'array':
      items = schema_root.get('items', {})
      if '$ref' in items and '$defs' in schema_root:
        ref_name = items['$ref'].split('/')[-1]
        return schema_root['$defs'][ref_name].get('properties', {})
      return items.get('properties', {})
    return schema_root.get('properties', {})

  result = {}
  for name, endpoint in docs.items():
    # --- 1. BUILD REQUEST SCHEMA ---
    request_schema = {}
    if endpoint.request_model:
      schema = TypeAdapter(endpoint.request_model).json_schema()
      properties = get_properties_from_schema(schema) 
      required = schema.get('required', [])
      for field_name, field_info in properties.items():
        request_schema[field_name] = {
          'type': field_info.get('type', 'any'),
          'required': field_name in required,
          'description': field_info.get('description', ''),
          'example': field_info.get('example')
        }

        # --- 2. BUILD RESPONSE SCHEMA ---
    response_schema = {}
    if endpoint.response_model:
      schema = TypeAdapter(endpoint.response_model).json_schema()
      properties = get_properties_from_schema(schema)
      required = schema.get('required', [])
      for field_name, field_info in properties.items():
        response_schema[field_name] = {
          'type': field_info.get('type', 'any'),
          'required': field_name in required,
          'description': field_info.get('description', ''),
          'example': field_info.get('example')
        }

    result[name] = {
      'name': endpoint.name,
      'summary': endpoint.summary,
      'description': endpoint.description,
      'tags': endpoint.tags,
      'request': request_schema,
      'response': response_schema,
      'exampleRequest': endpoint.example_request or {},
      'exampleResponse': endpoint.example_response or {}
    }
  return result

# ========================================================
# PART 4: INITIALIZATION
# ========================================================

# Run the registration immediately when this module loads
register_http_endpoints()