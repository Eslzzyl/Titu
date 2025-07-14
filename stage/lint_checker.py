import os
import shutil
import json
import re
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from config import RENPY_PATH, LANGUAGE_MODE

if LANGUAGE_MODE == "zh":
    from prompt_zh import SCRIPT_VALIDATION_PROMPT, SCRIPT_FIX_PROMPT
else:
    from prompt_en import SCRIPT_VALIDATION_PROMPT, SCRIPT_FIX_PROMPT

# Create console instance
console = Console()


def run_lint_check(lint_model):
    """Run Ren'Py lint check and fix discovered issues"""
    # Check if there is an export directory record
    export_dir_file = "./temp/export_dir.txt"
    if os.path.exists(export_dir_file):
        with open(export_dir_file, "r") as f:
            game_dir = f.read().strip()
    else:
        # If there is no export directory record, ask the user
        game_dir = Prompt.ask(
            "[bold blue]Please enter the game project directory to check[/bold blue]",
            default="./CVV25",
        )

    console.print(
        Panel(
            f"[bold blue]Start Ren'Py Lint check and fix process for {game_dir}[/bold blue]",
            border_style="blue",
        )
    )

    # Create temp directory
    os.makedirs("./temp", exist_ok=True)
    lint_output_path = "./temp/lint.txt"

    # Run lint command
    if os.path.exists(lint_output_path):
        console.print(
            "[bold blue]Found existing Lint output file, skipping Lint check step[/bold blue]"
        )
    else:
        with console.status(
            "[bold yellow]Running Ren'Py Lint check...[/bold yellow]", spinner="dots"
        ):
            try:
                # Build lint command
                lint_cmd = f"{RENPY_PATH} {game_dir} lint --all-problems"

                # Execute command and capture output
                process = subprocess.Popen(
                    lint_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                )

                # Write output to file
                with open(lint_output_path, "w", encoding="utf-8") as f:
                    for line in process.stdout:
                        f.write(line)

                # Wait for process to complete
                return_code = process.wait()

                # if return_code != 0:
                #     console.print("[bold yellow]Lint check completed, potential issues found[/bold yellow]")
                # else:
                #     console.print("[bold green]Lint check completed, no issues found[/bold green]")
                #     return

            except Exception as e:
                console.print(f"[bold red]Error during Lint check: {str(e)}[/bold red]")
                return

    # Parse lint results
    errors_json_path = "./temp/lint_errors.json"
    if os.path.exists(errors_json_path):
        console.print(
            "[bold blue]Found existing error info file, skipping parsing step[/bold blue]"
        )
        with open(errors_json_path, "r", encoding="utf-8") as f:
            parsed_errors = json.load(f)
        console.print(f"[bold blue]Parsed {len(parsed_errors)} errors[/bold blue]")
    else:
        with console.status(
            "[bold yellow]Parsing Lint results...[/bold yellow]", spinner="dots"
        ):
            try:
                # Read lint output
                with open(lint_output_path, "r", encoding="utf-8") as f:
                    lint_content = f.read()

                parse_prompt = SCRIPT_VALIDATION_PROMPT.format(lint_content)

                response = lint_model.run(parse_prompt)
                parsed_errors = json.loads(response.content)

                # Save parsed results
                with open(errors_json_path, "w", encoding="utf-8") as f:
                    json.dump(parsed_errors, f, ensure_ascii=False, indent=2)

                console.print(
                    f"[bold blue]Parsed {len(parsed_errors)} errors[/bold blue]"
                )
                console.print(
                    f"[bold blue]Detailed error info saved to {errors_json_path}[/bold blue]"
                )

            except Exception as e:
                console.print(
                    f"[bold red]Error parsing Lint results: {str(e)}[/bold red]"
                )
                return

    # Fix detected issues
    if parsed_errors:
        # Get script files to fix
        files_to_fix = set(error["file"] for error in parsed_errors if "file" in error)

        console.print(
            f"[bold blue]Detected {len(files_to_fix)} script files to fix[/bold blue]"
        )

        for file_path in files_to_fix:
            relative_path = file_path

            # If file path starts with "game/", find actual file path
            if relative_path.startswith("game/"):
                relative_path = relative_path[5:]  # Remove "game/" prefix

            # Build full file path
            full_path = os.path.join(game_dir, "game", relative_path)
            if not os.path.exists(full_path):
                console.print(f"[bold red]Cannot find file: {full_path}[/bold red]")
                continue

            # Read file content
            with open(full_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Collect all errors related to this file
            file_errors = [e for e in parsed_errors if e.get("file") == file_path]

            # Output file info
            console.print(
                f"[bold blue]Fixing file: {relative_path}, detected {len(file_errors)} issues[/bold blue]"
            )

            # Build fix prompt
            error_descriptions = "\n".join(
                [f"- {e.get('description', 'Unknown error')}" for e in file_errors]
            )

            fix_prompt = SCRIPT_FIX_PROMPT.format(
                file_name=relative_path,
                file_content=file_content,
                error_descriptions=error_descriptions,
            )

            with console.status(
                f"[bold yellow]Fixing issues in {relative_path}...[/bold yellow]",
                spinner="dots",
            ):
                try:
                    # Use model to fix issues
                    response = lint_model.run(fix_prompt)
                    fixed_content = response.content.strip()

                    # If returned content contains code block markers, extract content
                    if fixed_content.startswith("```") and fixed_content.endswith(
                        "```"
                    ):
                        fixed_content = re.search(
                            r"```(?:rpy|python)?\n(.*?)```", fixed_content, re.DOTALL
                        )
                        if fixed_content:
                            fixed_content = fixed_content.group(1).strip()

                    # Save backup
                    backup_path = f"{full_path}.bak"
                    shutil.copy2(full_path, backup_path)

                    # Write fixed content
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(fixed_content)

                    # Also update file in temp/scripts directory for possible future export
                    script_name = os.path.basename(full_path)
                    temp_script_path = os.path.join("./temp/scripts", script_name)
                    if os.path.exists(temp_script_path):
                        with open(temp_script_path, "w", encoding="utf-8") as f:
                            f.write(fixed_content)
                        console.print(
                            f"  - [cyan]↺[/cyan] Synchronized temporary script file {script_name}"
                        )

                    console.print(
                        f"[bold green]✓[/bold green] Fixed issues in {relative_path}, original file backed up as {os.path.basename(backup_path)}"
                    )

                except Exception as e:
                    console.print(
                        f"[bold red]Error fixing {relative_path}: {str(e)}[/bold red]"
                    )

        # Validate fixed results
        console.print("[bold blue]Validating fix results...[/bold blue]")
        validation_output_path = "./temp/lint_validation.txt"

        try:
            # Run lint command again
            lint_cmd = f"{RENPY_PATH} {game_dir} lint --all-problems"
            process = subprocess.Popen(
                lint_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

            # Save validation output
            with open(validation_output_path, "w", encoding="utf-8") as f:
                for line in process.stdout:
                    f.write(line)

            return_code = process.wait()

            if return_code != 0:
                console.print(
                    Panel(
                        "[bold yellow]Fix may be incomplete, issues still exist. Please check validation results.[/bold yellow]",
                        title="[bold yellow]Fix Results[/bold yellow]",
                        border_style="yellow",
                    )
                )
            else:
                console.print(
                    Panel(
                        "[bold green]All issues successfully fixed![/bold green]",
                        title="[bold green]Fix Results[/bold green]",
                        border_style="green",
                    )
                )

        except Exception as e:
            console.print(
                f"[bold red]Error validating fix results: {str(e)}[/bold red]"
            )
