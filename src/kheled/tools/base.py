import json
from typing import Any, Dict, List, Type
from pydantic import BaseModel

class BaseTool(BaseModel):
    """Base class for all tools in the kheled ecosystem."""

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        schema = cls.model_json_schema()
        description = cls.__doc__.strip() if cls.__doc__ else cls.__name__

        return {
            "type": "function",
            "function": {
                "name": cls.__name__,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                },
            },
        }

    def run(self) -> str:
        raise NotImplementedError


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Type[BaseTool]] = {}

    def register(self, tool_cls: Type[BaseTool]):
        self._tools[tool_cls.__name__] = tool_cls
        return tool_cls

    def get_schemas(self) -> List[Dict[str, Any]]:
        return [tool.get_schema() for tool in self._tools.values()]

    def execute(self, name: str, arguments: Any) -> str:
        if name not in self._tools:
            return f"Error: Tool '{name}' not found."

        tool_cls = self._tools[name]
        try:
            if isinstance(arguments, str):
                tool_instance = tool_cls.model_validate_json(arguments)
            elif isinstance(arguments, dict):
                tool_instance = tool_cls.model_validate(arguments)
            else:
                return f"Error: Invalid arguments type for tool '{name}'."

            return tool_instance.run()
        except Exception as e:
            return f"Error executing tool '{name}': {e}"


registry = ToolRegistry()