from rich.console import Console
from rich.panel import Panel
import time
from contextlib import contextmanager
from models.reasoning import ReasoningModel
from models.general import GeneralModel
from models.sd import SDPromptModel
from models.vl import VLModel
from models.lint import LintModel
from config import COMFY_UI_SERVER_ADDRESS
from comfy import ComfyUI

from .theme_manager import get_game_theme
from .draft_generator import generate_draft, parse_and_save_draft
from .chapter_generator import generate_chapters
from .script_generator import generate_scripts
from .image_prompt_generator import generate_image_prompts
from .audio_prompt_generator import generate_audio_prompts
from .image_generator import generate_images
from .audio_generator import generate_audio
from .export_game import export_game_assets
from .lint_checker import run_lint_check

# Create a console instance for global style control
console = Console()


@contextmanager
def timer(step_name):
    """Timer context manager for calculating and displaying the time taken for each step"""
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        console.print(f"[bold yellow]Step time: {elapsed_time:.2f} seconds[/bold yellow]")


def run_workflow():
    """Call each workflow function in order"""
    console.print(
        Panel.fit(
            "[bold cyan]Titu[/bold cyan]\n\n"
            "This tool will automatically generate all necessary files for a visual novel, including:\n"
            "- Story draft and structure\n"
            "- Chapter content\n"
            "- Ren'Py scripts\n"
            "- Background and character CG prompts\n"
            "- Music and sound effect prompts\n"
            "- Image and audio assets",
            title="[bold green]CVV2025[/bold green]",
            border_style="blue",
        )
    )

    console.rule("[bold green]Step 1: Get Game Theme[/bold green]")
    with timer("Get Game Theme"):
        game_theme = get_game_theme()

    # Initialize models
    console.print("[yellow]Initializing models...[/yellow]")
    start_time = time.time()
    reasoning_model = ReasoningModel()
    general_model = GeneralModel()
    sd_prompt_model = SDPromptModel()
    vl_model = VLModel()
    lint_model = LintModel()
    comfyui = ComfyUI(COMFY_UI_SERVER_ADDRESS)
    console.print(
        f"[bold yellow]Model initialization time: {time.time() - start_time:.2f} seconds[/bold yellow]"
    )

    # Get draft content
    console.rule("[bold green]Step 2: Generate Game Draft[/bold green]")
    with timer("Generate Game Draft"):
        generate_draft(game_theme, reasoning_model)

    # Parse draft to get structured data
    console.rule("[bold green]Step 3: Parse Draft Structure[/bold green]")
    with timer("Parse Draft Structure"):
        structured_draft = parse_and_save_draft(general_model)

    # Generate plot
    console.rule("[bold green]Step 4: Generate Chapter Plot[/bold green]")
    with timer("Generate Chapter Content"):
        generate_chapters(structured_draft, reasoning_model)

    # Generate script files
    console.rule("[bold green]Step 5: Generate Ren'Py Scripts[/bold green]")
    with timer("Generate Ren'Py Scripts"):
        generate_scripts(structured_draft, reasoning_model)

    # Generate image prompts
    console.rule("[bold green]Step 6: Generate Image Prompts[/bold green]")
    with timer("Generate Image Prompts"):
        generate_image_prompts(structured_draft, sd_prompt_model)

    # Generate audio prompts
    console.rule("[bold green]Step 7: Generate Audio Prompts[/bold green]")
    with timer("Generate Audio Prompts"):
        generate_audio_prompts(structured_draft, general_model)

    # Generate images
    console.rule("[bold green]Step 8: Generate Game Images[/bold green]")
    with timer("Generate Game Images"):
        generate_images(structured_draft, vl_model, comfyui)

    # Generate audio
    console.rule("[bold green]Step 9: Generate Game Audio[/bold green]")
    with timer("Generate Game Audio"):
        generate_audio(structured_draft, comfyui)

    # Export game assets
    console.rule("[bold green]Step 10: Export Game Assets[/bold green]")
    with timer("Export Game Assets"):
        export_game_assets()

    # Lint check and fix
    console.rule("[bold green]Step 11: Ren'Py Script Syntax Check and Fix[/bold green]")
    with timer("Ren'Py Script Syntax Check"):
        run_lint_check(lint_model)

    console.print(
        Panel(
            "[bold green]Game generation completed![/bold green]\n\n"
            "All assets have been saved to the following directories:\n"
            "- Draft and structure: [cyan]./temp/[/cyan]\n"
            "- Chapter content: [cyan]./temp/chapters/[/cyan]\n"
            "- Ren'Py scripts: [cyan]./temp/scripts/[/cyan]\n"
            "- Image assets: [cyan]./temp/images/[/cyan]\n"
            "- Audio assets: [cyan]./temp/audio/[/cyan]",
            title="[bold green]Completed[/bold green]",
            border_style="green",
        )
    )
