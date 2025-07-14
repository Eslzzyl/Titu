import os
import json
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from comfy import ComfyUI

# Create console instance
console = Console()


def convert_flac_to_opus(input_file, output_file):
    """Use ffmpeg to convert FLAC format to Opus format"""
    # Check if ffmpeg is installed
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        console.print(
            "[bold red]Error: ffmpeg is not installed or not accessible. Please install ffmpeg first.[/bold red]"
        )
        raise RuntimeError("ffmpeg is not installed or accessible")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Perform conversion
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_file,
                "-c:a",
                "libopus",
                "-b:a",
                "128k",
                "-vbr",
                "on",  # Enable variable bitrate
                "-compression_level",
                "10",  # Maximum compression
                "-y",  # Overwrite output file if exists
                output_file,  # Output file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        console.print(
            f"[bold red]Error occurred while converting audio file: {e}[/bold red]"
        )
        console.print(
            f"[red]Error output: {e.stderr.decode('utf-8', errors='ignore')}[/red]"
        )
        raise


def generate_audio(structured_draft, comfyui: ComfyUI):
    """Generate audio based on prompts and save to the specified directory"""
    os.makedirs("./temp/audio", exist_ok=True)
    MUSIC_TEMPLATE = "./audio/music.json"
    MUSIC_DURATION = 30
    SFX_TEMPLATE = "./audio/sfx_audio.json"
    SFX_DURATION = 5
    chapters = structured_draft["chapters"]

    # Collect audio generation tasks
    audio_tasks = []

    console.print(
        Panel(
            "[bold blue]Checking audio to be generated...[/bold blue]",
            border_style="blue",
        )
    )

    # Create audio task table
    table = Table(title="Audio Generation Tasks")
    table.add_column("Chapter", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Audio Name", style="green")
    table.add_column("Status", style="yellow")

    for i, chapter in enumerate(chapters):
        for prompt_type in ["music", "sfx"]:
            prompt_file = (
                f"./temp/prompts/audio/chapter{i + 1}_{prompt_type}_prompt.json"
            )
            if not os.path.exists(prompt_file):
                table.add_row(
                    f"Chapter {i + 1}", prompt_type, "No prompt file", "⚠️ Skipped"
                )
                continue

            with open(prompt_file, "r", encoding="utf-8") as pf:
                prompts = json.load(pf)

            for prompt_obj in prompts:
                target_name = prompt_obj["audio_name"] + ".opus"
                final_path = f"./temp/audio/{target_name}"

                if os.path.exists(final_path):
                    table.add_row(
                        f"Chapter {i + 1}",
                        prompt_type,
                        prompt_obj["audio_name"],
                        "✓ Exists",
                    )
                    continue

                # Add to pending audio generation tasks
                template = MUSIC_TEMPLATE if prompt_type == "music" else SFX_TEMPLATE
                duration = MUSIC_DURATION if prompt_type == "music" else SFX_DURATION
                audio_tasks.append((i, prompt_type, prompt_obj, template, duration))
                table.add_row(
                    f"Chapter {i + 1}",
                    prompt_type,
                    prompt_obj["audio_name"],
                    "⏳ To be generated",
                )
            # After the loop, count the total number of audio to be generated
            total_audio_to_generate = len(audio_tasks)
            console.print(
                f"[bold blue]Total audio to be generated: {total_audio_to_generate}[/bold blue]"
            )
            # Calculate total audio duration
            total_duration = 0
            for _, prompt_type, _, _, duration in audio_tasks:
                total_duration += duration

            # Convert total seconds to a more readable format (min:sec)
            minutes = total_duration // 60
            seconds = total_duration % 60
            duration_str = f"{minutes}min{seconds}s" if minutes > 0 else f"{seconds}s"

            console.print(
                f"[bold blue]Estimated total audio duration: {duration_str} ({total_duration}s)[/bold blue]"
            )

    console.print(table)

    if not audio_tasks:
        console.print(
            "[bold yellow]No audio to generate, skipping audio generation step...[/bold yellow]"
        )
        return

    def generate_audio_file(task_item):
        i, prompt_type, prompt_obj, template, duration = task_item
        target_name = prompt_obj["audio_name"] + ".opus"
        final_path = f"./temp/audio/{target_name}"

        audio_data_list = comfyui.generate_audio(
            prompt_file=template,
            positive_prompt=prompt_obj["prompt"],
            duration_seconds=duration,
            batch_size=1,
        )

        if not audio_data_list:
            raise RuntimeError(f"Audio generation failed: {prompt_obj['audio_name']}")

        # Get the first (and only) audio data
        audio_data = audio_data_list[0]

        # Save as temporary FLAC file
        temp_flac = f"./temp/audio/{target_name}.temp.flac"
        with open(temp_flac, "wb") as f:
            f.write(audio_data)

        # Convert to opus format and save to final directory
        convert_flac_to_opus(temp_flac, final_path)

        # Delete temporary flac file
        os.remove(temp_flac)

        return (i, prompt_type, prompt_obj["audio_name"])

    # Sequentially execute audio generation tasks
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("[bold]{task.completed}/{task.total}[/bold]"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Generating audio", total=len(audio_tasks))

        for task_item in audio_tasks:
            i, prompt_type, prompt_obj, template, duration = task_item
            try:
                result = generate_audio_file(task_item)
                i, type_name, audio_name = result
                progress.console.print(
                    f"[bold green]✓[/bold green] Finished generating Chapter {i + 1} {type_name} audio [{audio_name}]"
                )
            except Exception as e:
                progress.console.print(
                    f"[bold red]✗[/bold red] Error generating Chapter {i + 1} {prompt_type} audio [{prompt_obj['audio_name']}]: {str(e)}"
                )
            finally:
                progress.update(task, advance=1)
