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
from config import LANGUAGE_MODE

if LANGUAGE_MODE == "zh":
    from prompt_zh import GENERATE_CHAPTER_PROMPT
else:
    from prompt_en import GENERATE_CHAPTER_PROMPT

# Create console instance
console = Console()


def generate_chapters(structured_draft, reasoning_model: ReasoningModel):
    """Generate content for each chapter based on the structured draft and save to corresponding files"""
    os.makedirs("./temp/chapters", exist_ok=True)

    # Check if all chapter files already exist
    all_chapters_exist = True
    chapters_to_generate = []

    chapters = structured_draft["chapters"]
    for i, chapter in enumerate(chapters):
        chapter_file = f"./temp/chapters/{chapter['name']}.txt"
        if not os.path.exists(chapter_file):
            all_chapters_exist = False
            chapters_to_generate.append((i, chapter))
        else:
            console.print(
                f"[yellow]Chapter [bold]{chapter['name']}[/bold] file already exists, skipping generation...[/yellow]"
            )

    if all_chapters_exist:
        console.print(
            "[bold yellow]All chapter files already exist, skipping chapter generation step...[/bold yellow]"
        )
        return

    structured_draft_content = json.dumps(structured_draft, ensure_ascii=False)

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("[bold]{task.completed}/{task.total}[/bold]"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(
            "Generating chapter content", total=len(chapters_to_generate)
        )

        for i, chapter in chapters_to_generate:
            chapter_name = chapter["name"]
            chapter_file = f"./temp/chapters/{chapter_name}.txt"

            progress.update(task, description=f"Generating chapter: {chapter_name}")

            # Get content of previous chapters
            previous_chapter_content = ""
            if i > 0:
                previous_chapters = []
                for j in range(i):
                    prev_chapter_file = f"./temp/chapters/{chapters[j]['name']}.txt"
                    if os.path.exists(prev_chapter_file):
                        with open(prev_chapter_file, "r", encoding="utf-8") as f:
                            previous_chapters.append(
                                f"[{chapters[j]['name']}]:\n{f.read()}\n\n"
                            )
                previous_chapter_content = "".join(previous_chapters)
            else:
                previous_chapter_content = None

            try:
                generate_chapter_prompt = GENERATE_CHAPTER_PROMPT.format(
                    chapter_name=chapter_name, draft_content=structured_draft_content
                )

                if previous_chapter_content:
                    generate_chapter_prompt += f"\n\nReference content from previous chapters:\n{previous_chapter_content}"

                # Use non-streaming request
                with console.status(
                    f"[bold green]Generating chapter: {chapter_name}[/bold green]",
                    spinner="dots",
                ):
                    full_content = reasoning_model.run(generate_chapter_prompt)

                with open(chapter_file, "w", encoding="utf-8") as f:
                    f.write(full_content)
                progress.console.print(
                    f"[bold green]✓[/bold green] Finished generating chapter [cyan]{chapter_name}[/cyan]"
                )
            except Exception as e:
                progress.console.print(
                    f"[bold red]✗[/bold red] Error generating chapter [cyan]{chapter_name}[/cyan]: {str(e)}"
                )

            progress.update(task, advance=1)
