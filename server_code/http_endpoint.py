import anvil.server
import anvil.users
from anvil import BlobMedia
import json
from api_framework import APIRegistry

# 1. Define your API base URL
API_PREFIX = "/api/v1"

# 2. Define the Wrapper
def create_http_handler(endpoint_name, endpoint_obj):
  """
    Dynamically creates an HTTP endpoint for a given API function.
    """
  @anvil.server.http_endpoint(f"{API_PREFIX}/{endpoint_name}", methods=["POST"])
  def http_wrapper(**kwargs):
    try:
      # A. Get the Input
      # Anvil puts JSON body into request.body_json
      req_body = anvil.server.request.body_json

      # If body is empty, fall back to kwargs (query params/form data)
      data = req_body if req_body else kwargs

      # B. Run your existing Logic
      # This calls the @APIEndpoint decorated function in your other files
      # The decorator handles the Pydantic validation automatically.
      result = endpoint_obj(data)

      # C. Return the Result (Status 200 OK)
      # Returning a dict in Anvil automatically becomes a JSON response
      return result

    except Exception as e:
      # D. Handle Errors
      # Return a generic error dict
      return {
        "error": "API Execution Error",
        "message": str(e)
      }

  return http_wrapper

# 3. Define the Registration Logic
def register_http_endpoints():
  """
    Finds all registered API endpoints and creates HTTP routes for them.
    """
  endpoints = APIRegistry.get_all_endpoints()
  print(f"--- Setting up HTTP Interface for {len(endpoints)} endpoints ---")

  for name, endpoint in endpoints.items():
    create_http_handler(name, endpoint)
    print(f"  > Online: {anvil.server.get_app_origin()}{API_PREFIX}/{name}")

# 4. (Optional) Add Documentation UI
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
def get_openapi_spec():
  return APIRegistry.generate_documentation()