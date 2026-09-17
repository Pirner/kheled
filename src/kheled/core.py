import json
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel

from kheled.agent.llm import LMStudioClient
from kheled.tools.base import ToolRegistry

console = Console()

class Agent(BaseModel):
    llm: LMStudioClient
    registry: ToolRegistry
    max_steps: int = 6
    messages: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def run(self, prompt: str) -> str:
        if not self.messages:
            self.messages.append({
                "role": "system",
                "content": (
                    "You are kheled, an intelligent AI agent equipped with file and system tools. "
                    "Use available tools to inspect logs, gather evidence, and solve user queries."
                )
            })

        self.messages.append({"role": "user", "content": prompt})

        for step in range(self.max_steps):
            response = self.llm.chat(
                messages=self.messages,
                tools=self.registry.get_schemas()
            )

            choice = response["choices"][0]["message"]
            self.messages.append(choice)

            tool_calls = choice.get("tool_calls")
            if not tool_calls:
                return choice.get("content", "")

            # Handle execution and render styled terminal panels for each tool call
            for call in tool_calls:
                func_name = call["function"]["name"]
                raw_args = call["function"]["arguments"]

                # Display active tool call panel in CLI
                args_str = json.dumps(raw_args) if isinstance(raw_args, dict) else str(raw_args)
                console.print(
                    Panel(
                        f"[bold yellow]Tool:[/bold yellow] {func_name}\n[bold yellow]Arguments:[/bold yellow] {args_str}",
                        title="🔧 Tool Execution",
                        border_style="yellow",
                        expand=False
                    )
                )

                result = self.registry.execute(func_name, raw_args)

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": result
                })

        return "Agent reached maximum execution steps without completing the task."