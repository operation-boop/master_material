import anvil.server
import anvil.users
from anvil import BlobMedia
# --- FIXED IMPORT BELOW ---
from anvil.server import HttpResponse
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
# PART 1: THE DISPATCHER (The Fix)
# ========================================================

# We define ONE static endpoint that captures the function name from the URL.
# The ":endpoint_name" part acts as a variable.
@anvil.server.http_endpoint(f"{API_PREFIX}/:endpoint_name", methods=["POST", "OPTIONS"])
def api_dispatcher(endpoint_name, **kwargs):

  # 1. Handle CORS (Optional, but good for web apps)
  if anvil.server.request.method == 'OPTIONS':
    r = HttpResponse()
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    r.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return r

    # 2. Look up the endpoint in our Registry
  endpoints = APIRegistry.get_all_endpoints()
  endpoint_obj = endpoints.get(endpoint_name)

  # 3. If not found, return 404
  if not endpoint_obj:
    return HttpResponse(status=404, body=json.dumps({"error": f"Endpoint '{endpoint_name}' not found"}))

    # 4. Execute the Logic
  try:
    # Get JSON body or Fallback to kwargs
    req_body = anvil.server.request.body_json
    data = req_body if req_body else kwargs

    # Run the internal function (validation happens inside here)
    result = endpoint_obj(data)

    # Return success
    return HttpResponse(
      status=200,
      body=json.dumps(result, default=str),
      headers={"Content-Type": "application/json"}
    )

  except Exception as e:
    # Handle internal errors
    print(f"Error in {endpoint_name}: {e}")
    return HttpResponse(
      status=400, # or 500 depending on error type
      body=json.dumps({"error": "API Execution Error", "message": str(e)}),
      headers={"Content-Type": "application/json"}
    )

# ========================================================
# PART 2: DOCUMENTATION ENDPOINTS
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
  return HttpResponse(
    status=200,
    body=json.dumps(APIRegistry.generate_documentation(), default=str),
    headers={"Content-Type": "application/json"}
  )

# ========================================================
# PART 3: INTERNAL ANVIL FUNCTIONS
# ========================================================

@anvil.server.callable("get_api_documentation")
def internal_get_api_docs():
  """
    Returns API documentation in a format suitable for the front-end viewer
    """
  docs = APIRegistry.get_all_endpoints()

  # (Helper function for schemas)
  def get_properties_from_schema(schema_root):
    if not schema_root: 
      return {}
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