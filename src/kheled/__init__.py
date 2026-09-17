"""
kheled: Local Pydantic Agent Framework
"""

from kheled.agent.core import Agent
from kheled.agent.llm import LMStudioClient
from kheled.tools.base import BaseTool, registry

__version__ = "0.1.0"

__all__ = ["Agent", "LMStudioClient", "BaseTool", "registry"]