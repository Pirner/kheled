from pathlib import Path
from typing import Optional
from pydantic import Field
from kheled.tools.base import BaseTool, registry

LOGS_DIR = Path("./logs").resolve()


@registry.register
class ListLogFilesTool(BaseTool):
    """Lists files available in the active working directory or target path."""

    target_dir: Optional[str] = Field(None, description="Optional relative directory path.")

    def run(self) -> str:
        path = (LOGS_DIR / self.target_dir).resolve() if self.target_dir else LOGS_DIR

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            return f"Created missing directory at {path}. No files present."

        files = [f.name for f in path.glob("*") if f.is_file()]
        if not files:
            return f"No files found in '{path.name}'."

        return f"Found {len(files)} file(s):\n" + "\n".join(f"- {f}" for f in sorted(files))


@registry.register
class ReadLogFileTool(BaseTool):
    """Reads lines from a designated log file."""

    filename: str = Field(..., description="Filename to read.")
    lines_count: int = Field(50, ge=1, le=500, description="Number of lines to tail.")

    def run(self) -> str:
        target_path = (LOGS_DIR / self.filename).resolve()

        if not target_path.exists():
            return f"Error: Log file '{self.filename}' does not exist."

        try:
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            selected = lines[-self.lines_count:]
            return f"--- [Last {len(selected)} lines of {self.filename}] ---\n" + "".join(selected)
        except Exception as e:
            return f"Error reading log file: {e}"