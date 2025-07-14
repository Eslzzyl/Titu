import os
import uuid
import json
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
from models.vl import VLModel
from comfy import ComfyUI
from util import evaluate_image

# Create console instance
console = Console()

# Global variable to control whether to perform VL model evaluation and correction
ENABLE_VL_EVALUATION = False


def generate_images(structured_draft, vl_model: VLModel, comfyui: ComfyUI):
    """Generate images based on prompts and evaluate quality with VL model, regenerate if necessary"""
    os.makedirs("./temp/candidates", exist_ok=True)
    os.makedirs("./temp/images", exist_ok=True)
    os.makedirs(
        "./temp/refine", exist_ok=True
    )  # Create directory for saving iterative images
    SPRITE_TEMPLATE = "./image/sprite.json"
    BACKGROUND_TEMPLATE = "./image/background.json"
    # CG uses the same template as background
    CG_TEMPLATE = "./image/background.json"
    chapters = structured_draft["chapters"]

    # Clear candidate directory
    console.print(
        Panel(
            "[bold yellow]Cleaning candidate image directory...[/bold yellow]",
            border_style="yellow",
        )
    )
    with console.status(
        "[bold green]Cleaning candidate image directory...[/bold green]", spinner="dots"
    ):
        for filename in os.listdir("./temp/candidates"):
            os.remove(os.path.join("./temp/candidates", filename))

    # Collect image generation tasks
    image_tasks = []
    # Use a dict to track added image names to avoid duplicates
    added_images = {}

    console.print(
        Panel(
            "[bold blue]Checking images to generate...[/bold blue]", border_style="blue"
        )
    )

    # Create image task table
    table = Table(title="Image Generation Tasks")
    table.add_column("Chapter", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Image Name", style="green")
    table.add_column("Status", style="yellow")

    for i, chapter in enumerate(chapters):
        for prompt_type in ["background", "sprite", "cg"]:
            prompt_file = (
                f"./temp/prompts/image/chapter{i + 1}_{prompt_type}_prompt.json"
            )
            if not os.path.exists(prompt_file):
                table.add_row(
                    f"Chapter {i + 1}", prompt_type, "No prompt file", "⚠️ Skipped"
                )
                continue

            with open(prompt_file, "r", encoding="utf-8") as pf:
                prompts = json.load(pf)

            for prompt_obj in prompts:
                target_name = prompt_obj["image_name"] + ".webp"
                final_path = f"./temp/images/{target_name}"
                # Check if image already exists
                if os.path.exists(final_path):
                    table.add_row(
                        f"Chapter {i + 1}",
                        prompt_type,
                        prompt_obj["image_name"],
                        "✓ Exists",
                    )
                    continue

                # Check for duplicate image tasks
                if prompt_obj["image_name"] in added_images:
                    table.add_row(
                        f"Chapter {i + 1}",
                        prompt_type,
                        prompt_obj["image_name"],
                        "⚠️ Duplicate (already in chapter "
                        + str(added_images[prompt_obj["image_name"]] + 1)
                        + ")",
                    )
                    continue

                # Add to image tasks to be generated
                template = SPRITE_TEMPLATE
                if prompt_type == "background":
                    template = BACKGROUND_TEMPLATE
                elif prompt_type == "cg":
                    template = CG_TEMPLATE

                image_tasks.append((i, prompt_type, prompt_obj, template))
                # Record added image name and its chapter
                added_images[prompt_obj["image_name"]] = i
                table.add_row(
                    f"Chapter {i + 1}",
                    prompt_type,
                    prompt_obj["image_name"],
                    "⏳ To be generated",
                )
            # After the loop, count the total number of images to generate
            total_images_to_generate = len(image_tasks)
            console.print(
                f"[bold blue]Total images to generate: {total_images_to_generate}[/bold blue]"
            )

    console.print(table)

    if not image_tasks:
        console.print(
            "[bold yellow]No images to generate, skipping image generation step...[/bold yellow]"
        )
        return

    def generate_image(task_item, current_prompt=None, attempt=1, max_attempts=3):
        """Generate a single image and evaluate quality, regenerate if necessary"""
        i, prompt_type, prompt_obj, template = task_item
        target_name = prompt_obj["image_name"] + ".webp"
        final_path = f"./temp/images/{target_name}"

        # Record each iteration version of the image
        refine_name = f"{prompt_obj['image_name']}_{attempt}.webp"
        refine_path = f"./temp/refine/{refine_name}"

        # Evaluation info text file
        eval_file_name = f"{prompt_obj['image_name']}_{attempt}.txt"
        eval_file_path = f"./temp/refine/{eval_file_name}"

        # Use the provided prompt or the original prompt
        prompt_to_use = current_prompt if current_prompt else prompt_obj["prompt"]

        # Generate a single image
        image = comfyui.generate_image(
            prompt_file=template,
            positive_prompt=prompt_to_use,
            batch_size=1,  # Only generate one image
        )[0]  # Get the first (and only) generated image

        # Save as a temporary file for evaluation
        temp_filename = f"./temp/candidates/{uuid.uuid4().hex}.webp"
        image.save(temp_filename)

        # Also save the iteration version to the refine directory
        image.save(refine_path)
        console.print(f"[bold cyan]Saved iteration version {refine_name}[/bold cyan]")

        # If VL evaluation is disabled or max attempts reached, use current image and save evaluation info
        if not ENABLE_VL_EVALUATION or attempt >= max_attempts:
            # Save evaluation info
            with open(eval_file_path, "w", encoding="utf-8") as f:
                f.write(f"Image Name: {prompt_obj['image_name']}\n")
                f.write(f"Iteration: {attempt}/{max_attempts}\n")
                f.write(f"Prompt: {prompt_to_use}\n")
                f.write("Evaluation: VL evaluation disabled or max attempts reached\n")

            os.rename(temp_filename, final_path)
            return (
                i,
                prompt_type,
                prompt_obj["image_name"],
                "VL evaluation skipped"
                if not ENABLE_VL_EVALUATION
                else f"Max attempts reached ({max_attempts}), using last generated image",
            )

        # Load script content and outline content as extra reference
        script_content = ""
        outline_content = ""

        # Read script content
        script_path = f"./temp/scripts/chapter{i + 1}.rpy"
        if os.path.exists(script_path):
            try:
                with open(script_path, "r", encoding="utf-8") as f:
                    script_content = f.read()
            except Exception as e:
                console.print(
                    f"[bold yellow]Warning: Failed to read script file {script_path}: {str(e)}[/bold yellow]"
                )

        # Prepare outline content
        try:
            # Get current chapter outline
            chapter_info = chapters[i]
            # For sprite type, add character info
            if prompt_type == "sprite" and "character_renpy_name" in prompt_obj:
                character_name = prompt_obj["character_renpy_name"]
                # Find matching character info
                character_info = None
                for char in structured_draft.get("characters", []):
                    if char.get("renpy_name") == character_name:
                        character_info = char
                        break

                if character_info:
                    outline_content = f"Character Info:\nName: {character_info.get('name', '')}\nBackground: {character_info.get('background', '')}\nPersonality: {character_info.get('personality', '')}\nAppearance: {character_info.get('features', '')}\n\nChapter Content: {chapter_info.get('content', '')}"
                else:
                    outline_content = (
                        f"Chapter Content: {chapter_info.get('content', '')}"
                    )
            else:
                # Background and CG only provide chapter content
                outline_content = f"Chapter Content: {chapter_info.get('content', '')}"
        except Exception as e:
            console.print(
                f"[bold yellow]Warning: Error preparing outline content: {str(e)}[/bold yellow]"
            )

        # Use VL model to evaluate image quality, passing extra script and outline reference
        evaluation = evaluate_image(
            vl_model,
            temp_filename,
            mode=prompt_type,
            sd_prompt=prompt_to_use,
            script_content=script_content,
            outline_content=outline_content,
        )

        # Save evaluation info to text file
        with open(eval_file_path, "w", encoding="utf-8") as f:
            f.write(f"Image Name: {prompt_obj['image_name']}\n")
            f.write(f"Iteration: {attempt}/{max_attempts}\n")
            f.write(f"Prompt: {prompt_to_use}\n")
            f.write(f"Acceptable: {'Yes' if evaluation['acceptable'] else 'No'}\n")
            if evaluation.get("issues"):
                f.write(f"Issues: {', '.join(evaluation['issues'])}\n")
            if evaluation.get("optimized_prompt"):
                f.write(f"Optimized Prompt: {evaluation['optimized_prompt']}\n")
            if evaluation.get("evaluation_details"):
                f.write(f"Evaluation Details:\n{evaluation['evaluation_details']}\n")
            else:
                f.write("Evaluation Details: None\n")

        # If image is acceptable, save and return result
        if evaluation["acceptable"]:
            os.rename(temp_filename, final_path)
            return (i, prompt_type, prompt_obj["image_name"], "Image acceptable")

        # If image is not acceptable but optimized prompt is provided, retry with new prompt
        if (
            evaluation["optimized_prompt"]
            and evaluation["optimized_prompt"] != prompt_to_use
        ):
            # Record optimized prompt info
            console.print(
                f"[bold cyan]Generated optimized prompt for {prompt_obj['image_name']}: {evaluation['optimized_prompt'][:100]}...[/bold cyan]"
            )
            if evaluation.get("issues"):
                console.print(
                    f"[bold yellow]Issues found: {', '.join(evaluation['issues'])}[/bold yellow]"
                )

            # Delete temp file (iteration version already saved to refine directory)
            os.remove(temp_filename)
            # Recursively call itself with optimized prompt
            return generate_image(
                task_item,
                current_prompt=evaluation["optimized_prompt"],
                attempt=attempt + 1,
                max_attempts=max_attempts,
            )

        # If no optimized prompt but image is not acceptable, use current image
        os.rename(temp_filename, final_path)
        if evaluation.get("issues"):
            console.print(
                f"[bold yellow]Image has issues but could not optimize: {', '.join(evaluation['issues'])}[/bold yellow]"
            )
        return (
            i,
            prompt_type,
            prompt_obj["image_name"],
            "Could not optimize prompt, using current image",
        )

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("[bold]{task.completed}/{task.total}[/bold]"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Generating images", total=len(image_tasks))

        for task_item in image_tasks:
            i, prompt_type, prompt_obj, _ = task_item
            try:
                i, type_name, image_name, msg = generate_image(task_item)
                progress.console.print(
                    f"[bold green]✓[/bold green] Finished generating image for Chapter {i + 1} {type_name} [{image_name}]: {msg}"
                )
                progress.update(task, advance=1)
            except Exception as e:
                progress.console.print(
                    f"[bold red]✗[/bold red] Error generating image for Chapter {i + 1} {prompt_type} [{prompt_obj['image_name']}]: {str(e)}"
                )
                progress.update(task, advance=1)
