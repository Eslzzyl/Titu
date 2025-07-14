import os
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Create console instance
console = Console()


def get_game_theme():
    theme_file = "./temp/game_theme.txt"

    if os.path.exists(theme_file):
        with open(theme_file, "r", encoding="utf-8") as f:
            previous_theme = f.read().strip()

        console.print(
            Panel(
                f"[yellow]Found previous game theme:[/yellow] [bold cyan]{previous_theme}[/bold cyan]",
                border_style="green",
            )
        )
        console.print(
            "[yellow]If you choose 'Yes', missing files will be checked and generated; if you choose 'No', the ./temp directory will be cleared and all content will be regenerated.[/yellow]"
        )
        use_previous = Confirm.ask("Use the previous theme?", default=True)

        if use_previous:
            console.print(
                "[bold green]Using the previous theme, checking and generating missing files...[/bold green]"
            )
            return previous_theme
        else:
            console.print(
                "[bold red]Clearing ./temp directory and starting over...[/bold red]"
            )
            # Clear the temp directory
            with console.status(
                "[bold yellow]Clearing temporary directory...[/bold yellow]"
            ):
                for item in os.listdir("./temp"):
                    item_path = os.path.join("./temp", item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)

    # Ensure temp directory exists (in case it was deleted or doesn't exist yet)
    os.makedirs("./temp", exist_ok=True)

    # Ask for new theme input
    new_theme = Prompt.ask(
        "[bold blue]Enter the game theme and other necessary information[/bold blue]"
    )

    # Save the new theme
    with open(theme_file, "w", encoding="utf-8") as f:
        f.write(new_theme)

    console.print(f"[bold green]✓[/bold green] Theme saved: [cyan]{new_theme}[/cyan]")
    return new_theme
