import os
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Create console instance
console = Console()


def export_game_assets():
    """Copy generated game assets to the specified game project directory"""
    # Ask user to specify the target game directory
    target_dir = Prompt.ask(
        "[bold blue]Please enter the root directory of the target game project[/bold blue]",
        default="./CVV25",
    )

    # Ensure the target directory exists
    os.makedirs(target_dir, exist_ok=True)

    # Ensure the 'game' directory in the target game exists
    game_dir = os.path.join(target_dir, "game")
    os.makedirs(game_dir, exist_ok=True)

    with console.status(
        "[bold green]Exporting game assets...[/bold green]", spinner="dots"
    ):
        # Copy script files
        scripts_dir = "./temp/scripts"
        if os.path.exists(scripts_dir):
            console.print("[yellow]Copying script files...[/yellow]")

            # First delete all existing chapter*.rpy files
            console.print("[yellow]Deleting old chapter script files...[/yellow]")
            for file in os.listdir(game_dir):
                if file.startswith("chapter") and file.endswith(".rpy"):
                    file_path = os.path.join(game_dir, file)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        console.print(f"  - [red]×[/red] Deleted {file}")

            # Delete all *.rpyc files
            console.print("[yellow]Deleting old compiled script files...[/yellow]")
            for file in os.listdir(game_dir):
                if file.endswith(".rpyc"):
                    file_path = os.path.join(game_dir, file)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        console.print(f"  - [red]×[/red] Deleted {file}")

            # Copy new script files
            script_files = [f for f in os.listdir(scripts_dir) if f.endswith(".rpy")]
            for script_file in script_files:
                src_path = os.path.join(scripts_dir, script_file)
                dst_path = os.path.join(game_dir, script_file)

                # If the target file exists, delete it first
                if os.path.exists(dst_path):
                    os.remove(dst_path)

                # Copy file
                shutil.copy2(src_path, dst_path)
                console.print(f"  - [green]✓[/green] {script_file}")

        # Handle image files
        target_images_dir = os.path.join(game_dir, "images")
        source_images_dir = "./temp/images"

        # If the target image directory exists, delete it first
        if os.path.exists(target_images_dir):
            console.print("[yellow]Deleting old image directory...[/yellow]")
            shutil.rmtree(target_images_dir)

        os.makedirs(
            target_images_dir, exist_ok=True
        )  # Ensure the target image directory exists

        # If the source image directory exists, copy files
        if os.path.exists(source_images_dir):
            console.print("[yellow]Copying image files...[/yellow]")
            # Create new target image directory
            os.makedirs(target_images_dir, exist_ok=True)

            # Copy the entire image directory
            for item in os.listdir(source_images_dir):
                src_item = os.path.join(source_images_dir, item)
                dst_item = os.path.join(target_images_dir, item)
                if os.path.isfile(src_item):
                    shutil.copy2(src_item, dst_item)
                    console.print(f"  - [green]✓[/green] images/{item}")

        # Handle audio files
        target_audio_dir = os.path.join(game_dir, "audio")
        source_audio_dir = "./temp/audio"

        # If the target audio directory exists, delete it first
        if os.path.exists(target_audio_dir):
            console.print("[yellow]Deleting old audio directory...[/yellow]")
            shutil.rmtree(target_audio_dir)

        os.makedirs(
            target_audio_dir, exist_ok=True
        )  # Ensure the target audio directory exists

        # If the source audio directory exists, copy files
        if os.path.exists(source_audio_dir):
            console.print("[yellow]Copying audio files...[/yellow]")

            if os.path.exists(source_audio_dir):
                for item in os.listdir(source_audio_dir):
                    src_item = os.path.join(source_audio_dir, item)
                    dst_item = os.path.join(target_audio_dir, item)
                    if os.path.isfile(src_item):
                        shutil.copy2(src_item, dst_item)
                        console.print(f"  - [green]✓[/green] audio/{item}")

    # Show export completion message
    console.print(
        Panel(
            f"[bold green]Game assets have been successfully exported to the {target_dir} directory![/bold green]\n\n"
            "You can now use the Ren'Py SDK to open this directory to run or build the game.",
            title="[bold green]Export Complete[/bold green]",
            border_style="green",
        )
    )

    # Save export directory to a temporary file for subsequent steps
    with open("./temp/export_dir.txt", "w") as f:
        f.write(target_dir)
