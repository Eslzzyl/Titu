import os
import json
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from models.reasoning import ReasoningModel
from util import remove_renpy_markers
from config import LANGUAGE_MODE

if LANGUAGE_MODE == "zh":
    from prompt_zh import GENERATE_CHAPTER_SCRIPT_PROMPT
else:
    from prompt_en import GENERATE_CHAPTER_SCRIPT_PROMPT

# Create console instance
console = Console()


def generate_scripts(structured_draft, reasoning_model: ReasoningModel):
    """Generate Ren'Py script files"""
    os.makedirs("./temp/scripts", exist_ok=True)

    # Check if all script files already exist
    script_path = "./temp/scripts/script.rpy"
    all_scripts_exist = os.path.exists(script_path)
    chapters_to_generate = []

    if all_scripts_exist:
        for i, chapter in enumerate(structured_draft["chapters"]):
            chapter_script_path = f"./temp/scripts/chapter{i + 1}.rpy"
            if not os.path.exists(chapter_script_path):
                all_scripts_exist = False
                chapters_to_generate.append((i, chapter))
            else:
                console.print(
                    f"[yellow]Chapter [bold]{chapter['name']}[/bold] script file already exists, skipping script generation...[/yellow]"
                )

    if all_scripts_exist:
        console.print(
            "[bold yellow]All script files already exist, skipping script generation step...[/bold yellow]"
        )
        return

    # Generate character definitions and entry label
    if not os.path.exists(script_path):
        with console.status(
            "[bold green]Generating character definition file...[/bold green]",
            spinner="dots",
        ):
            characters = structured_draft["characters"]
            characters_definition = ""
            for character in characters:
                renpy_name = character["renpy_name"]
                name = character["name"]
                characters_definition += f"define {renpy_name} = Character('{name}')\n"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(characters_definition)
                f.write("\nlabel start:\n    jump chapter1\n")
        console.print(
            f"[bold green]✓[/bold green] Character definition file generated: [cyan]{script_path}[/cyan]"
        )

    # Prepare all chapters' content
    chapters = []
    for chapter in structured_draft["chapters"]:
        chapter_file = f"./temp/chapters/{chapter['name']}.txt"
        if os.path.exists(chapter_file):
            with open(chapter_file, "r", encoding="utf-8") as f:
                chapter_content = f.read()
            chapters.append({"name": chapter["name"], "content": chapter_content})
        else:
            console.print(
                f"[bold red]Warning:[/bold red] Chapter file {chapter_file} does not exist"
            )

    if len(chapters) == 0:
        console.print(
            "[bold red]Error:[/bold red] No chapter content files found, unable to generate scripts"
        )
        return

    structured_draft_content = json.dumps(structured_draft, ensure_ascii=False)

    # Generate each chapter's script in order
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("[bold]{task.completed}/{task.total}[/bold]"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(
            "Generating Ren'Py scripts", total=len(chapters_to_generate)
        )

        # Read character definition file content as reference
        characters_definition = ""
        if os.path.exists(script_path):
            with open(script_path, "r", encoding="utf-8") as f:
                characters_definition = f.read()

        for i, chapter in chapters_to_generate:
            chapter_name = chapter["name"]
            chapter_file = f"./temp/chapters/{chapter_name}.txt"
            script_chapter_path = f"./temp/scripts/chapter{i + 1}.rpy"

            progress.update(
                task, description=f"Generating chapter script: {chapter_name}"
            )

            # Get previous chapters' script content
            previous_scripts_content = ""
            if i > 0:
                previous_scripts = []
                for j in range(i):
                    prev_script_file = f"./temp/scripts/chapter{j + 1}.rpy"
                    if os.path.exists(prev_script_file):
                        with open(prev_script_file, "r", encoding="utf-8") as f:
                            previous_scripts.append(
                                f"[{structured_draft['chapters'][j]['name']} Script]:\n{f.read()}\n\n"
                            )
                previous_scripts_content = "".join(previous_scripts)
            else:
                previous_scripts_content = None

            # Get current chapter content
            with open(chapter_file, "r", encoding="utf-8") as f:
                chapter_content = f.read()

            try:
                generate_script_prompt = GENERATE_CHAPTER_SCRIPT_PROMPT.format(
                    draft_content=structured_draft_content,
                    chapter_name=chapter_name,
                    chapter_content=chapter_content,
                )

                # Add character definition file reference in the prompt
                if LANGUAGE_MODE == "zh":
                    definition_prompt = (
                        "请参考大纲中的角色定义（不要重新定义这些角色）:\n"
                    )
                else:
                    definition_prompt = "Reference character definitions in the outline (do not redefine these characters):\n"
                generate_script_prompt += (
                    f"\n\n{definition_prompt}\n{characters_definition}\n\n"
                )

                # Add previous chapters' script reference in the prompt
                if previous_scripts_content is not None:
                    if LANGUAGE_MODE == "zh":
                        reference_script_prompt = "请参考前面章节的脚本格式和风格:\n"
                    else:
                        reference_script_prompt = "Refer to the script format and style of previous chapters:\n"
                    generate_script_prompt += (
                        f"{reference_script_prompt}\n{previous_scripts_content}"
                    )

                # Use non-streaming request
                with console.status(
                    f"[bold green]Generating script: {chapter_name}[/bold green]",
                    spinner="dots",
                ):
                    full_content = reasoning_model.run(generate_script_prompt)

                with open(script_chapter_path, "w", encoding="utf-8") as f:
                    cleaned_content = remove_renpy_markers(full_content)
                    f.write(cleaned_content)

                progress.console.print(
                    f"[bold green]✓[/bold green] Finished generating script for chapter [cyan]{chapter_name}[/cyan]"
                )
            except Exception as e:
                progress.console.print(
                    f"[bold red]✗[/bold red] Error generating script for chapter [cyan]{chapter_name}[/cyan]: {str(e)}"
                )

            progress.update(task, advance=1)
