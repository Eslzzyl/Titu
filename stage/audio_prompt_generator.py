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
from models.general import GeneralModel
from config import LANGUAGE_MODE
from util import remove_json_markers

if LANGUAGE_MODE == "zh":
    from prompt_zh import (
        GENERATE_MUSIC_PROMPT,
        GENERATE_SFX_PROMPT,
    )
else:
    from prompt_en import (
        GENERATE_MUSIC_PROMPT,
        GENERATE_SFX_PROMPT,
    )

# Create console instance
console = Console()


def generate_audio_prompts(structured_draft, general_model: GeneralModel):
    """Generate music and sound effect prompt files for each chapter, using non-streaming output"""
    os.makedirs("./temp/prompts/audio", exist_ok=True)

    # Check if all prompt files already exist
    all_prompts_exist = True
    prompts_to_generate = []

    chapters = structured_draft["chapters"]
    for i, chapter in enumerate(chapters):
        music_file_path = f"./temp/prompts/audio/chapter{i + 1}_music_prompt.json"
        sfx_file_path = f"./temp/prompts/audio/chapter{i + 1}_sfx_prompt.json"

        if not os.path.exists(music_file_path) or not os.path.exists(sfx_file_path):
            all_prompts_exist = False

            if not os.path.exists(music_file_path) and not os.path.exists(
                sfx_file_path
            ):
                status = "both"
            elif not os.path.exists(music_file_path):
                status = "music"
            else:
                status = "sfx"

            script_path = f"./temp/scripts/chapter{i + 1}.rpy"
            if os.path.exists(script_path):
                prompts_to_generate.append((i, chapter, status))
            else:
                console.print(
                    f"[bold red]Warning:[/bold red] Script file {script_path} does not exist, skipping audio prompt generation..."
                )
        else:
            console.print(
                f"[yellow]Audio prompt files for chapter {i + 1} already exist, skipping audio prompt generation for this chapter...[/yellow]"
            )

    if all_prompts_exist:
        console.print(
            "[bold yellow]All audio prompt files already exist, skipping audio prompt generation step...[/bold yellow]"
        )
        return

    def generate_prompt_for_chapter(item):
        i, chapter, status = item
        script_path = f"./temp/scripts/chapter{i + 1}.rpy"
        music_file_path = f"./temp/prompts/audio/chapter{i + 1}_music_prompt.json"
        sfx_file_path = f"./temp/prompts/audio/chapter{i + 1}_sfx_prompt.json"

        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()

        result = []

        # For thread safety, create a new console in this function
        local_console = Console()

        if status in ["both", "music"]:
            local_console.print(
                f"[bold blue]Generating music prompt for chapter {i + 1}...[/bold blue]"
            )

            # Use non-streaming API directly
            music_prompt_response = general_model.run(
                f"{GENERATE_MUSIC_PROMPT}\n\nRen'Py script: {script_content}"
            )
            music_prompt = json.loads(
                remove_json_markers(music_prompt_response.content)
            )
            with open(music_file_path, "w", encoding="utf-8") as f:
                json.dump(music_prompt, f, indent=4, ensure_ascii=False)
            result.append(f"music for chapter {i + 1}")

        if status in ["both", "sfx"]:
            local_console.print(
                f"[bold blue]Generating sound effect prompt for chapter {i + 1}...[/bold blue]"
            )

            # Use non-streaming API directly
            sfx_prompt_response = general_model.run(
                f"{GENERATE_SFX_PROMPT}\n\nRen'Py script: {script_content}"
            )
            sfx_prompt = json.loads(remove_json_markers(sfx_prompt_response.content))
            with open(sfx_file_path, "w", encoding="utf-8") as f:
                json.dump(sfx_prompt, f, indent=4, ensure_ascii=False)
            result.append(f"sfx for chapter {i + 1}")

        return result

    # Sequentially process prompt generation for each chapter
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("[bold]{task.completed}/{task.total}[/bold]"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(
            "Generating audio prompts", total=len(prompts_to_generate)
        )

        for item in prompts_to_generate:
            i, chapter, status = item
            try:
                results = generate_prompt_for_chapter(item)
                progress.console.print(
                    f"[bold green]✓[/bold green] Finished generating audio prompts for chapter {i + 1}: [cyan]{', '.join(results)}[/cyan]"
                )
                progress.update(task, advance=1)
            except Exception as e:
                progress.console.print(
                    f"[bold red]✗[/bold red] Error generating audio prompts for chapter {i + 1}: {str(e)}"
                )
