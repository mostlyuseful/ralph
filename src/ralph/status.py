import json
from pathlib import Path

import pydantic
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class StatusModel(pydantic.BaseModel):
    task: str
    tests_passed: bool
    notes: str
    success: bool
    next_task: str | None
    user_input_required: bool | None

STATUS_PATH = Path("status.json")


def load_status(status_path: Path | None = None) -> StatusModel:
    path = status_path or STATUS_PATH
    if not path.exists():
        raise FileNotFoundError(f"Status file not found at {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return StatusModel.model_validate(data)

def print_status(status_path: Path | None = None) -> StatusModel:
    status = load_status(status_path)

    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    success_style = "green" if status.success else "red"
    tests_style = "green" if status.tests_passed else "red"
    user_input_style = "yellow" if status.user_input_required else "green"

    table.add_row("Task", status.task or "-")
    table.add_row("Success", f"[{success_style}]{status.success}[/]")
    table.add_row("Tests Passed", f"[{tests_style}]{status.tests_passed}[/]")
    table.add_row("Next Task", status.next_task or "-")
    table.add_row("Notes", status.notes or "-")
    table.add_row("User Input Required", f"[{user_input_style}]{status.user_input_required}[/]")

    Console().print(Panel(table, title="Status", expand=False))
    return status