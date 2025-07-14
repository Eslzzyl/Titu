import os
import json
from rich.console import Console
from rich.table import Table
from models.reasoning import ReasoningModel
from models.general import GeneralModel
from config import LANGUAGE_MODE
from util import parse_draft

if LANGUAGE_MODE == "zh":
    from prompt_zh import DRAFT_PROMPT
else:
    from prompt_en import DRAFT_PROMPT

# Create console instance
console = Console()


def generate_draft(game_theme, reasoning_model: ReasoningModel):
    """Generate draft and save to file"""
    draft_file = "./temp/draft.txt"

    if os.path.exists(draft_file):
        console.print(
            "[bold yellow]Draft file already exists, skipping draft generation step...[/bold yellow]"
        )
        with open(draft_file, "r", encoding="utf-8") as f:
            return f.read()

    draft_prompt = DRAFT_PROMPT.format(game_theme=game_theme)

    # Use non-streaming request
    with console.status("[bold green]Generating draft...[/bold green]", spinner="dots"):
        full_content = reasoning_model.run(draft_prompt)

    console.print("[bold green]✓[/bold green] Draft generation completed")
    with open(draft_file, "w", encoding="utf-8") as f:
        f.write(full_content)
    return full_content


def parse_and_save_draft(general_model: GeneralModel):
    """Parse draft and save structured data"""
    structured_draft_file = "./temp/structured_draft.json"

    if os.path.exists(structured_draft_file):
        console.print(
            "[bold yellow]Structured draft file already exists, skipping draft parsing step...[/bold yellow]"
        )
        with open(structured_draft_file, "r", encoding="utf-8") as f:
            return json.load(f)

    with open("./temp/draft.txt", "r", encoding="utf-8") as f:
        draft = f.read()

    draft_response = parse_draft(general_model, draft)

    # Create summary table for structured data
    table = Table(title="Structured Data Summary")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="magenta")
    table.add_column("Details", style="green")

    characters = draft_response.get("characters", [])
    table.add_row(
        "Characters",
        str(len(characters)),
        ", ".join([char["name"] for char in characters]),
    )

    chapters = draft_response.get("chapters", [])
    table.add_row(
        "Chapters", str(len(chapters)), ", ".join([ch["name"] for ch in chapters])
    )

    console.print(table)

    with open(structured_draft_file, "w", encoding="utf-8") as f:
        json.dump(draft_response, f, indent=4, ensure_ascii=False)

    console.print("[bold green]✓[/bold green] Draft structuring completed and saved")
    return draft_response
