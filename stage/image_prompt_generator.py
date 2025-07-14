import os
import json
import concurrent.futures
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from models.sd import SDPromptModel
from util import (
    get_background_sd_prompt,
    get_sprite_sd_prompt,
    get_cg_sd_prompt,
)
from config import MAX_CONCURRENT_REQUESTS

# Create console instance
console = Console()


def generate_image_prompts(structured_draft, sd_prompt_model: SDPromptModel):
    """Generate background, character, and CG prompt files for each chapter, using non-streaming output"""
    os.makedirs("./temp/prompts/image", exist_ok=True)

    # Check if all prompt files already exist
    all_prompts_exist = True
    prompts_to_generate = []

    chapters = structured_draft["chapters"]
    for i, chapter in enumerate(chapters):
        bg_file_path = f"./temp/prompts/image/chapter{i + 1}_background_prompt.json"
        sprite_file_path = f"./temp/prompts/image/chapter{i + 1}_sprite_prompt.json"
        cg_file_path = f"./temp/prompts/image/chapter{i + 1}_cg_prompt.json"

        if (
            not os.path.exists(bg_file_path)
            or not os.path.exists(sprite_file_path)
            or not os.path.exists(cg_file_path)
        ):
            all_prompts_exist = False

            status = []
            if not os.path.exists(bg_file_path):
                status.append("background")
            if not os.path.exists(sprite_file_path):
                status.append("sprite")
            if not os.path.exists(cg_file_path):
                status.append("cg")

            script_path = f"./temp/scripts/chapter{i + 1}.rpy"
            if os.path.exists(script_path):
                prompts_to_generate.append((i, chapter, status))
            else:
                console.print(
                    f"[bold red]Warning:[/bold red] Script file {script_path} does not exist, skipping prompt generation..."
                )
        else:
            console.print(
                f"[yellow]Prompt files for chapter {i + 1} already exist, skipping prompt generation for this chapter...[/yellow]"
            )

    if all_prompts_exist:
        console.print(
            "[bold yellow]All prompt files already exist, skipping prompt generation step...[/bold yellow]"
        )
        return

    characters_setting_json = json.dumps(
        structured_draft["characters"], ensure_ascii=False
    )
    world_view_json = json.dumps(structured_draft["world_view"], ensure_ascii=False)

    def generate_prompt_for_chapter(item):
        i, chapter, status_list = item
        script_path = f"./temp/scripts/chapter{i + 1}.rpy"
        bg_file_path = f"./temp/prompts/image/chapter{i + 1}_background_prompt.json"
        sprite_file_path = f"./temp/prompts/image/chapter{i + 1}_sprite_prompt.json"
        cg_file_path = f"./temp/prompts/image/chapter{i + 1}_cg_prompt.json"

        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()

        result = []

        # For thread safety, create a new console in this function
        local_console = Console()

        if "background" in status_list:
            local_console.print(
                f"[bold blue]Generating background prompt for chapter {i + 1}...[/bold blue]"
            )

            # Use non-streaming API directly
            background_prompt = get_background_sd_prompt(
                sd_prompt_model, world_view_json, script_content
            )
            with open(bg_file_path, "w", encoding="utf-8") as f:
                json.dump(background_prompt, f, indent=4, ensure_ascii=False)
            result.append(f"background for chapter {i + 1}")

        if "sprite" in status_list:
            local_console.print(
                f"[bold blue]Generating character prompt for chapter {i + 1}...[/bold blue]"
            )

            # Use non-streaming API directly
            sprite_prompts = get_sprite_sd_prompt(
                sd_prompt_model, characters_setting_json, script_content
            )
            with open(sprite_file_path, "w", encoding="utf-8") as f:
                json.dump(sprite_prompts, f, indent=4, ensure_ascii=False)
            result.append(f"sprite for chapter {i + 1}")

        if "cg" in status_list:
            local_console.print(
                f"[bold blue]Generating CG prompt for chapter {i + 1}...[/bold blue]"
            )

            # Use non-streaming API directly
            cg_prompts = get_cg_sd_prompt(
                sd_prompt_model,
                world_view_json,
                characters_setting_json,
                script_content,
            )
            with open(cg_file_path, "w", encoding="utf-8") as f:
                json.dump(cg_prompts, f, indent=4, ensure_ascii=False)
            result.append(f"cg for chapter {i + 1}")

        return result

    # Use thread pool for concurrent requests
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("[bold]{task.completed}/{task.total}[/bold]"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Generating prompts", total=len(prompts_to_generate))

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_CONCURRENT_REQUESTS
        ) as executor:
            futures = {
                executor.submit(generate_prompt_for_chapter, item): item
                for item in prompts_to_generate
            }
            for future in concurrent.futures.as_completed(futures):
                i, chapter, status = futures[future]
                try:
                    results = future.result()
                    progress.console.print(
                        f"[bold green]✓[/bold green] Finished generating prompts for chapter {i + 1}: [cyan]{', '.join(results)}[/cyan]"
                    )
                    progress.update(task, advance=1)
                except Exception as e:
                    progress.console.print(
                        f"[bold red]✗[/bold red] Error generating prompts for chapter {i + 1}: {str(e)}"
                    )
