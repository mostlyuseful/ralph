import logging
from pathlib import Path
import subprocess

import typer

from ralph.instructions import get_instructions
from ralph.opencode import run_opencode
from ralph.prd import count_checked, extract_next_task
from ralph.status import load_status, print_status

app = typer.Typer()


@app.command()
def main(
    max_iterations: int = typer.Option(
        1, help="Maximum number of ralph iterations to run"
    ),
    user_input: str = typer.Option(
        "",
        help="Optional user input to inject into the instructions template",
    ),
    instructions_path: Path = typer.Option(
        "instructions.j2",
        help="Path to the Jinja2 file containing the instructions. If missing, falls back to embedded instructions.",
    ),
    model: str = typer.Option(
        "",
        help="The model to use for opencode. This will be passed directly to the --model flag of the opencode CLI. If omitted, the flag will not be included and opencode will use its default model.",
    ),
):
    logging.basicConfig(level=logging.INFO, force=True)

    for iteration in range(max_iterations):
        logging.info(f"Ralph iteration {iteration + 1}/{max_iterations}")

        next_task = extract_next_task("prd.md")
        if next_task is None:
            print("All tasks complete.")
            break

        checked_before = count_checked("prd.md")

        # Print next task in green for visibility:
        print(f"\nNext task:\n\033[92m{next_task}\033[0m\n")

        try:
            status_before = load_status()
            if status_before.user_input_required and not user_input:
                # Get input interactively from the user if required and not provided via CLI:
                user_input = typer.prompt(
                    "Ralph is requesting user input to proceed. Please provide the required input"
                )
                if not user_input:
                    raise ValueError(
                        "Ralph is waiting for user input to proceed. Please provide input using the --user-input option."
                    )
        except FileNotFoundError:
            logging.info("No existing status found, starting fresh.")

        instructions = get_instructions(
            instructions_path,
            iteration_number=iteration + 1,
            max_iterations=max_iterations,
            scoped_task=next_task,
            user_input=user_input or None,
        )

        expected_checkboxes = next_task.count("- [ ]")
        run_opencode(instructions, model=model)
        checked_after = count_checked("prd.md")
        delta = checked_after - checked_before

        if delta > expected_checkboxes:
            print(
                f"⚠️  Agent ticked {delta} boxes but was scoped to {expected_checkboxes}."
            )
            subprocess.run(["git", "diff", "HEAD~1", "--", "prd.md"])
            if typer.confirm("Revert prd.md to last commit?"):
                subprocess.run(["git", "checkout", "HEAD~1", "--", "prd.md"])

        status = print_status()
        if status.next_task is None:
            logging.info("All tasks completed. Exiting.")
            raise typer.Exit()


if __name__ == "__main__":
    app()
