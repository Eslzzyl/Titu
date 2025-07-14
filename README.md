This repository provides the source code for the ACM Multimedia 2025 paper "From Outline to Detail: An Hierarchical End-to-end Framework for Coherent and Consistent Visual Novel Generation and Assembly".

## Installation

### Steps

1. Clone this repository: `git clone https://github.com/Eslzzyl/Titu.git`
2. Install uv: https://docs.astral.sh/uv/getting-started/installation/
3. Install Ren'Py SDK: https://www.renpy.org/
4. Deploy ComfyUI on a machine accessible via network: https://www.comfy.org/
5. Install dependencies: Execute `uv sync` in the root directory of the repository
6. Copy `example_config.py` to `config.py`: `cp example_config.py config.py`
7. Obtain the corresponding LLM API according to "About LLMs" below.
8. Complete the deployment according to the "Image/Audio Model Deployment Instructions" below.
9. Install ffmpeg according to "About ffmpeg" below.
10. Modify the values in `config.py` according to the instructions in "Configure `config.py`" below.

### About LLMs

The framework uses the OpenAI Python SDK to call any LLM service compatible with the OpenAI API. Although LLMs can be deployed locally for the framework to use through tools such as llama.cpp/vLLM, the capabilities of most open-source models are very limited, resulting in poor generation results.

#### Reasoning LLMs

> Here, the reasoning ability of the model is not required. However, since reasoning models often have better creative writing abilities, we recommend using such models.

The following models have been tested to have good writing abilities:
- DeepSeek-R1-0528 (DeepSeek-R1-0120 is not recommended)
- Gemini 2.5 Pro/Flash
- Grok 3 (mini)

If you want to use open-source models, please prioritize those optimized models that have been specially fine-tuned for creative writing tasks. You can find these models on Hugging Face, most of which are based on the Qwen series, Gemma series, and Mistral Small series.

#### Non-Reasoning LLMs

> Similarly, here, the model can also be a reasoning model. However, since non-reasoning models tend to have faster response speeds, we recommend using such models.

> Since the framework also uses non-reasoning models to generate prompts for Stable Audio, it is recommended to choose models that are familiar enough with Stable Audio prompts.

Recommended:
- DeepSeek-V3-0324
- Qwen2.5-72B-Instruct
- Gemini 2.0 Flash / Gemini 2.5 Flash(-Lite)
- Any other model with a fast response speed and supports formatted JSON output

#### SD Prompt LLMs

Any model that is familiar enough with Stable Diffusion prompts can handle the task. In our work, we used Qwen2.5-72B-Instruct.

#### Visual LLMs

Any multimodal model with good visual capabilities can handle the task. In our work, we used Qwen2.5-VL-72B-Instruct.

### Image/Audio Model Deployment Instructions

All models described in this section should be served through ComfyUI. To run the recommended models, at least 10 GB of VRAM is required. If the current device (the device running the framework) has a graphics card that meets the requirements, it is recommended to deploy it directly on the current device. Otherwise, you need to access the ComfyUI service through the network.

A large part of the visual novel material generation time is spent on image generation. Therefore, you may want to use a sufficiently powerful graphics card. According to our tests, an RTX 4090 takes about 4.1s to generate an image (excluding self-correction operations). A typical visual novel may contain more than 100 images. Weaker graphics cards can also work, but the speed will be slightly slower.

#### Stable Diffusion Models

It is recommended to choose Stable Diffusion models according to your target style: https://civitai.com/models

For anime styles, the recommended models are Pony or Illustrious (and their further fine-tuned versions) based on Stable Diffusion XL.

Download your favorite model and place it in the `ComfyUI/models/checkpoints` directory. Then, you need to modify `./image/sprite.json` and `./image/background.json`, and change the value of the `ckpt_name` item on line 34 of the two files to the file name of the model you downloaded.

#### Background Removal Model

We used this ComfyUI extension to remove the background of character sprites: https://github.com/ZHO-ZHO-ZHO/ComfyUI-BRIA_AI-RMBG

You need to install the extension according to the instructions in this repository and download the corresponding background removal model.

#### Stable Audio Model

You need to download the Stable Audio model and put it into ComfyUI according to the instructions at https://comfyanonymous.github.io/ComfyUI_examples/audio/#stable-audio-open-10 so that it can be correctly recognized.

### About ffmpeg

This project uses ffmpeg to convert generated audio files into opus format, which is easily recognized by the Ren'Py engine.

Considering that compiling ffmpeg is a complex task, we recommend downloading pre-compiled binaries provided by the community from https://ffmpeg.org/download.html.

After downloading and decompressing, add the `bin` directory to the PATH environment variable so that the project can find ffmpeg.

### Configure `config.py`

Next, make the following modifications to `config.py`:

Modify the values of variables such as `REASONING_MODEL`, `GENERAL_MODEL`, `VL_MODEL`, and `SD_PROMPT_MODEL` to the corresponding API Base URL, API Key, and model name. Among them, `REASONING_MODEL_PROVIDER` can be set to `OpenAI` or `Gemini`. The former can be used for any OpenAI-compatible interface, and the latter can be used for calling the official API of the Gemini series models. Other types of LLMs only support the OpenAI interface.

Modify the value of `COMFY_UI_SERVER_ADDRESS` to the address of the ComfyUI server. If you deploy ComfyUI on your local machine and use the default port, it should be `127.0.0.1:8188`; if you deploy ComfyUI on another server or modify the default port, you need to adjust it according to the specific IP address and port.

Modify the value of `RENPY_PATH` to the path of the Ren'Py SDK executable file installed in the system.

Modify the value of `LANGUAGE_MODE` as needed. Please note that this framework uses Chinese (i.e., `zh` mode) throughout the development and testing stages, and we cannot guarantee that the English mode will achieve exactly the same results. Unexpected bugs may occur.

## Start the project

Before starting the project, make sure you have started the ComfyUI server and that all LLM interfaces can respond normally.

Execute `uv run main.py` in the project root directory to start the project. You will see a prompt asking you to enter the theme of the visual novel. After entering the theme and pressing Enter, the project will automatically execute and generate all the required materials. All materials will be placed in the `./temp` directory.

You can press Ctrl+C at any time to interrupt the program. When you start again later, if the file corresponding to the stage exists in the `./temp` directory, the framework will automatically skip this stage.

> Sometimes the generation task will block the program, and the program will not respond to any input (including Ctrl+C), but it will still run normally. This is a known issue and will be resolved in the future.

## Export

Before exporting, you need to manually generate an empty visual novel project using the Ren'Py SDK, and then copy the project to the root directory of this code repository. Otherwise, the export will report an error.

## Disclaimer

This project is developed for academic research purposes. Under certain specific prompts, LLMs and Stable Diffusion may generate content that is uncomfortable or poses certain legal risks. We do not recommend that you disseminate the content generated by the project. We are not responsible for the legality, originality, or risk of infringement of the generated content.

> Where did the name "Titu" come from?
>
> This name belongs to an NPC character in a certain game. In the game, this character is responsible for recording and spreading stories.
