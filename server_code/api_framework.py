from typing import Dict, Any, Callable, Optional, Type
from pydantic import BaseModel, Field, ValidationError, TypeAdapter
import functools
import anvil.server
import inspect
import json
from datetime import datetime

class APIRegistry:
  """Central registry for all API endpoints"""
  _endpoints = {}

  @classmethod
  def register(cls, endpoint):
    cls._endpoints[endpoint.name] = endpoint
    return endpoint

  @classmethod
  def get_all_endpoints(cls):
    return cls._endpoints

  @classmethod
  def generate_documentation(cls):
    """Generate OpenAPI-style documentation for all endpoints"""
    docs = {
      "openapi": "3.0.0",
      "info": {
        "title": "Anvil API Documentation",
        "version": "1.0.0",
        "description": "Auto-generated API documentation with request/response schemas"
      },
      "paths": {}
    }

    for name, endpoint in cls._endpoints.items():
      docs["paths"][f"/{name}"] = {
        "post": {
          "summary": endpoint.summary,
          "description": endpoint.description,
          "tags": endpoint.tags,
          "requestBody": {
            "required": True,
            "content": {
              "application/json": {
                "schema": endpoint.request_model.model_json_schema() if endpoint.request_model else {}
              }
            }
          },
          "responses": {
            "200": {
              "description": "Successful response",
              "content": {
                "application/json": {
                  "schema": endpoint.response_model.model_json_schema()
                }
              }
            },
            "400": {
              "description": "Validation error",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "error": {"type": "string"},
                      "details": {"type": "object"}
                    }
                  }
                }
              }
            },
            "500": {
              "description": "Server error",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "error": {"type": "string"}
                    }
                  }
                }
              }
            }
          }
        }
      }

    return docs

  @classmethod
  def generate_markdown_docs(cls):
    """Generate markdown documentation"""
    md = "# API Documentation\n\n"
    md += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    md += "---\n\n"

    for name, endpoint in cls._endpoints.items():
      md += f"## {name}\n\n"
      md += f"**Summary:** {endpoint.summary}\n\n"
      md += f"{endpoint.description}\n\n"

      if endpoint.tags:
        md += f"**Tags:** {', '.join(endpoint.tags)}\n\n"

      if endpoint.request_model:
        md += "### Request Body\n\n"
        schema = endpoint.request_model.model_json_schema()
        md += "```json\n"
        md += json.dumps(schema, indent=2)
        md += "\n```\n\n"

        # Add field descriptions
        if 'properties' in schema:
          md += "#### Parameters\n\n"
          for field_name, field_info in schema['properties'].items():
            required = field_name in schema.get('required', [])
            req_badge = "**required**" if required else "*optional*"
            md += f"- **`{field_name}`** ({field_info.get('type', 'any')}) {req_badge}\n"
            if 'description' in field_info:
              md += f"  - {field_info['description']}\n"
            if 'example' in field_info:
              md += f"  - Example: `{field_info['example']}`\n"
          md += "\n"

      md += "### Response\n\n"
      response_schema = endpoint.response_model.model_json_schema()
      md += "```json\n"
      md += json.dumps(response_schema, indent=2)
      md += "\n```\n\n"

      # Add example
      if endpoint.example_request:
        md += "### Example Request\n\n"
        md += "```python\n"
        md += f"result = anvil.server.call('{name}', {json.dumps(endpoint.example_request, indent=2)})\n"
        md += "```\n\n"

      if endpoint.example_response:
        md += "### Example Response\n\n"
        md += "```json\n"
        md += json.dumps(endpoint.example_response, indent=2)
        md += "\n```\n\n"

      md += "---\n\n"

    return md


class APIEndpoint:
  """Decorator for creating documented and validated API endpoints"""

  def __init__(
    self,
    name: str,
    request_model: Optional[Type[BaseModel]] = None,
    response_model: Type[BaseModel] = None,
    summary: str = "",
    description: str = "",
    tags: list = None,
    example_request: dict = None,
    example_response: dict = None
  ):
    self.name = name
    self.request_model = request_model
    self.response_model = response_model
    self.summary = summary or name
    self.description = description
    self.tags = tags or []
    self.example_request = example_request
    self.example_response = example_response

    # Register this endpoint
    APIRegistry.register(self)

  def __call__(self, func: Callable):
    """Wrap the function with validation and error handling"""
    @functools.wraps(func)
    @anvil.server.callable(self.name)
    def wrapper(*args, **kwargs):
      try:
        # Handle both positional and keyword arguments
        if args:
          # If called with positional args, convert to dict if we have a request model
          if self.request_model:
            # Assume single dict argument
            data = args[0] if args else {}
          else:
            # No request model, pass through
            return func(*args, **kwargs)
        else:
          data = kwargs

          # Validate request if model is provided
        if self.request_model:
          validated_request = self.request_model(**data)
          # Call function with validated model
          result = func(validated_request)
        else:
          # No request validation
          result = func(*args, **kwargs)

        if self.response_model:
          # Use TypeAdapter to automatically handle List[Model], Dict, or single Model
          adapter = TypeAdapter(self.response_model)
          # validate_python converts dicts/lists into Pydantic models
          validated_obj = adapter.validate_python(result)
          # dump_python converts them back to JSON-safe dicts/lists
          return adapter.dump_python(validated_obj)
        else:
          return result

      except ValidationError as e:
        # Return structured validation errors
        error_details = {
          "error": "Validation Error",
          "details": e.errors()
        }
        raise Exception(json.dumps(error_details))


    wrapper._api_endpoint = self

    return wrapper


# Helper function to export documentation
def export_api_docs(format='markdown', output_file=None):
  """
    Export API documentation
    
    Args:
        format: 'markdown' or 'openapi' or 'json'
        output_file: Optional file path to write to
    
    Returns:
        Documentation string
    """
  if format == 'markdown':
    docs = APIRegistry.generate_markdown_docs()
  elif format in ['openapi', 'json']:
    docs = json.dumps(APIRegistry.generate_documentation(), indent=2)
  else:
    raise ValueError(f"Unsupported format: {format}")

  if output_file:
    with open(output_file, 'w') as f:
      f.write(docs)

  return docs
