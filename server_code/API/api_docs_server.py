"""
Server-side API Documentation Provider
Add this to your Anvil server modules
"""
import anvil.server
from .api_framework import APIRegistry
import json
from pydantic import TypeAdapter # <--- ADD THIS IMPORT

@anvil.server.callable
def get_api_documentation():
  docs = APIRegistry.get_all_endpoints()
  result = {}

  for name, endpoint in docs.items():
    # 1. Safe Request Schema
    request_schema = {}
    if endpoint.request_model:
      # Use TypeAdapter to safely handle Lists or Models
      schema = TypeAdapter(endpoint.request_model).json_schema()

      # Extract properties if it's a standard object
      properties = schema.get('properties', {})
      required = schema.get('required', [])

      for field_name, field_info in properties.items():
        request_schema[field_name] = {
          'type': field_info.get('type', 'any'),
          'description': field_info.get('description', ''),
          'required': field_name in required
        }

    # 2. Safe Response Schema
    response_schema = {}
    if endpoint.response_model:
      # Use TypeAdapter here too!
      schema = TypeAdapter(endpoint.response_model).json_schema()

      properties = schema.get('properties', {})
      required = schema.get('required', [])

      for field_name, field_info in properties.items():
        response_schema[field_name] = {
          'type': field_info.get('type', 'any'),
          'description': field_info.get('description', ''),
          'required': field_name in required
        }

    result[name] = {
      'name': endpoint.name,
      'summary': endpoint.summary,
      'description': endpoint.description,
      'tags': endpoint.tags,
      'request': request_schema,
      'response': response_schema
    }

  return result


@anvil.server.callable
def get_api_documentation_markdown():
  """
    Returns API documentation in markdown format
    
    Returns:
        str: Markdown documentation
    """
  from .api_framework import export_api_docs
  return export_api_docs(format='markdown')


@anvil.server.callable
def get_api_documentation_openapi():
  """
    Returns API documentation in OpenAPI 3.0 format
    
    Returns:
        dict: OpenAPI specification
    """
  return APIRegistry.generate_documentation()


