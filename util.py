from models.general import GeneralModel
from models.sd import SDPromptModel
from models.vl import VLModel
from prompt_zh import (
    PARSE_DRAFT_PROMPT,
    SELECT_BEST_BACKGROUND_PROMPT,
    SELECT_BEST_SPRITE_PROMPT,
    SELECT_BEST_CG_PROMPT,
    EVALUATE_IMAGE_PROMPT,
)
import json
import base64
from typing import Literal
from PIL import Image


def parse_draft(general_model: GeneralModel, draft: str, raw=False):
    """Parse draft text and extract structured information"""
    json_llm = general_model.llm.bind(response_format={"type": "json_object"})
    draft = "Parse the following outline into JSON format:\n\n" + draft
    messages = [("system", PARSE_DRAFT_PROMPT), ("human", draft)]

    response = json_llm.invoke(messages).content

    return json.loads(remove_json_markers(response))


def remove_json_markers(input: str) -> str:
    # Remove ```json and ``` markers if present
    input = input.strip()
    if input.startswith("```json"):
        input = input[7:]
    elif input.startswith("```"):  # Handle case without language identifier
        input = input[3:]
    if input.endswith("```"):
        input = input[:-3]
    input = input.strip()
    return input


def remove_renpy_markers(input: str) -> str:
    # Remove ```renpy and ``` markers if present
    input = input.strip()
    if input.startswith("```renpy"):
        input = input[8:]
    elif input.startswith("```"):  # Handle case without language identifier
        input = input[3:]
    if input.endswith("```"):
        input = input[:-3]
    input = input.strip()
    return input


def get_background_sd_prompt(model: SDPromptModel, world_view: str, script: str):
    """Generate SD background prompt from script"""
    response = model.run_background(world_view, script)
    response = remove_json_markers(response.content)
    return json.loads(response)


def get_sprite_sd_prompt(
    model: SDPromptModel, character_setting_json: str, script: str
):
    """Generate SD character (sprite) prompt from script"""
    response = model.run_sprite(character_setting_json, script)
    response = remove_json_markers(response.content)
    return json.loads(response)


def get_cg_sd_prompt(
    model: SDPromptModel, world_view: str, character_setting: str, script: str
):
    """Generate SD full-screen CG prompt from script"""
    response = model.run_cg(world_view, character_setting, script)
    response = remove_json_markers(response.content)
    return json.loads(response)


def select_best_image(
    vl_model: VLModel,
    image_paths: list[str],
    mode: Literal["sprite", "background", "cg"],
    sd_prompt: str,
) -> str:
    """Select the best image using a visual language model

    Args:
        vl_model (VLModel): visual language model
        image_paths (list[str]): list of image paths
        mode (str): image type, options: sprite, background, cg
        sd_prompt (str): prompt describing the image

    Returns:
        str: path of the best image
    """

    if len(image_paths) == 1:
        return image_paths[0]

    select_prompt = None
    if mode == "sprite":
        select_prompt = SELECT_BEST_SPRITE_PROMPT
    elif mode == "background":
        select_prompt = SELECT_BEST_BACKGROUND_PROMPT
    elif mode == "cg":
        select_prompt = SELECT_BEST_CG_PROMPT
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    # Display each image with index for reference
    prompt_with_sdprompt = select_prompt.format(sd_prompts=sd_prompt)

    # Iterate all image paths, read images and encode as base64
    messages = []
    for image_path in image_paths:
        with open(image_path, "rb") as f:
            image = f.read()
            image_encoded = base64.b64encode(image).decode("utf-8")
            messages.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_encoded}"},
                }
            )
    # Use the model to select the most suitable image
    response = vl_model.run(
        [
            (
                "human",
                [{"type": "text", "text": prompt_with_sdprompt}] + messages,
            )
        ]
    )

    try:
        response_content = remove_json_markers(response.content)
        response_json = json.loads(response_content)
        best_index = int(response_json.get("best", 1)) - 1
        if best_index < 0 or best_index >= len(image_paths):
            print(f"Invalid best index: {best_index}, using default index 0")
            best_index = 0
        return image_paths[best_index]
    except Exception as e:
        print(f"Error parsing response: {e}, response content: {response.content}")
        # Default to first image if parsing fails
        return image_paths[0]


def crop_image(path, target_width=1280, target_height=720):
    # Open image
    image = Image.open(path)

    # Calculate target aspect ratio
    target_ratio = target_width / target_height

    # Calculate original aspect ratio
    original_ratio = image.width / image.height

    # Crop image according to aspect ratio
    if original_ratio > target_ratio:
        # Crop width
        new_width = int(image.height * target_ratio)
        left = (image.width - new_width) / 2
        right = (image.width + new_width) / 2
        top = 0
        bottom = image.height
    else:
        # Crop height
        new_height = int(image.width / target_ratio)
        top = (image.height - new_height) / 2
        bottom = (image.height + new_height) / 2
        left = 0
        right = image.width

    # Crop image
    cropped_image = image.crop((left, top, right, bottom))

    # Resize
    resized_image = cropped_image.resize(
        (target_width, target_height), Image.Resampling.LANCZOS
    )

    # Save image
    resized_image.save(path)


def get_music_prompt(general_model: GeneralModel, script: str):
    """Generate music prompt from script"""
    from prompt_zh import GENERATE_MUSIC_PROMPT

    response = general_model.run(f"{GENERATE_MUSIC_PROMPT}\n\nRen'Py script: {script}")
    response_text = remove_json_markers(response.content)
    return json.loads(response_text)


def get_sfx_prompt(general_model: GeneralModel, script: str):
    """Generate sound effect prompt from script"""
    from prompt_zh import GENERATE_SFX_PROMPT

    response = general_model.run(f"{GENERATE_SFX_PROMPT}\n\nRen'Py script: {script}")
    response_text = remove_json_markers(response.content)
    return json.loads(response_text)


def evaluate_image(
    vl_model: VLModel,
    image_path: str,
    mode: Literal["sprite", "background", "cg"],
    sd_prompt: str,
    script_content: str = "",
    outline_content: str = "",
) -> dict:
    """Evaluate image quality using a visual language model and provide optimized prompts

    Args:
        vl_model (VLModel): visual language model
        image_path (str): image path
        mode (str): image type, options: sprite, background, cg
        sd_prompt (str): prompt describing the image
        script_content (str): script content of the relevant section
        outline_content (str): outline content of the relevant section

    Returns:
        dict: dictionary containing evaluation result, list of issues, and optimized prompt
    """

    evaluate_prompt = EVALUATE_IMAGE_PROMPT.format(
        mode=mode,
        sd_prompts=sd_prompt,
        script_content=script_content,
        outline_content=outline_content,
    )

    # Read image and encode as base64
    with open(image_path, "rb") as f:
        image = f.read()
        image_encoded = base64.b64encode(image).decode("utf-8")

    # Use the model to evaluate the image
    response = vl_model.run(
        [
            (
                "human",
                [
                    {"type": "text", "text": evaluate_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_encoded}"},
                    },
                ],
            )
        ]
    )

    try:
        response_content = remove_json_markers(response.content)
        evaluation_result = json.loads(response_content)
        return evaluation_result
    except Exception as e:
        print(
            f"Error parsing evaluation response: {e}, response content: {response.content}"
        )
        # If parsing fails, return a default value indicating the current image is acceptable
        return {"acceptable": True, "issues": [], "optimized_prompt": sd_prompt}
