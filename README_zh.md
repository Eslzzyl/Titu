# Titu

本仓库提供了 ACM Multimedia 2025 论文《From Outline to Detail: An Hierarchical End-to-end Framework for Coherent and Consistent Visual Novel Generation and Assembly》的源代码。

## 安装

### 步骤

1. 克隆仓库：`git clone https://github.com/Eslzzyl/Titu.git`
2. 安装 uv：https://docs.astral.sh/uv/getting-started/installation/
3. 安装 Ren'Py SDK：https://www.renpy.org/
4. 在一台可通过网络访问的机器上部署 ComfyUI：https://www.comfy.org/
5. 安装依赖：在仓库根目录执行 `uv sync`
6. 将 `example_config.py` 复制一份到 `config.py`：`cp example_config.py config.py`
7. 根据后文“关于 LLM 的说明”获取对应的 LLM API。
8. 根据后文“关于图片/音频模型的部署说明”完成部署。
9. 根据后文“关于 ffmpeg 的说明”安装 ffmpeg。
10. 根据后文“配置 `config.py`”的说明修改 `config.py` 中的值。

### 关于 LLM 的说明

框架通过 OpenAI Python SDK 调用任何兼容 OpenAI API 的 LLM 服务。尽管可以通过 llama.cpp/vLLM 等工具本地部署 LLM 供框架使用，但大部分开源模型的能力都十分有限，生成效果不佳。

#### 推理模型 Reasoning LLMs

> 在这里，模型的推理能力不是必需的。但由于推理模型往往具备更佳的创意写作能力，我们推荐使用这类模型。

以下模型经过测试具有良好的写作能力：
- DeepSeek-R1-0528（不推荐使用 DeepSeek-R1-0120）
- Gemini 2.5 Pro/Flash
- Grok 3 (mini)

如果希望使用开源模型，请优先选取那些针对创意写作任务进行特别微调的优化模型。您可以在 Hugging Face 上找到这些模型，它们大多基于 Qwen 系列、Gemma 系列和 Mistral Small 系列。

#### 非推理模型 Non-Reasoning LLMs

> 同样，在这里，模型也可以是推理模型。但由于非推理模型往往具备更快的响应速度，我们推荐使用这类模型。

> 由于框架同时使用非推理模型生成 Stable Audio 的提示词，建议选取那些对 Stable Audio 提示词足够熟悉的模型。

推荐使用：
- DeepSeek-V3-0324
- Qwen2.5-72B-Instruct
- Gemini 2.0 Flash / Gemini 2.5 Flash(-Lite)
- 任何其他具有较快的响应速度且支持格式化 JSON 输出的模型

#### SD 提示词模型 SD Prompt LLMs

任何对 Stable Diffusion 提示词足够熟悉的模型都能够胜任。在我们的工作中，使用了 Qwen2.5-72B-Instruct。

#### 视觉 LLMs

任何具有良好视觉能力的多模态模型都能够胜任。在我们的工作中，使用了 Qwen2.5-VL-72B-Instruct。

### 关于图片/音频模型的部署说明

本节所述的所有模型都应当通过 ComfyUI 提供服务。为了运行推荐的模型，需要至少 10 GB 的 VRAM。如果当前设备（运行框架的设备）有一张满足条件的显卡，那么推荐直接部署在当前设备上。否则，需要通过网络访问 ComfyUI 服务。

视觉小说素材生成中很大一部分时间用于图片生成。因此，您可能希望使用一张性能足够强劲的显卡。根据我们的测试，RTX 4090 生成一张图片（不含自我矫正操作）需要约 4.1s。典型长度的视觉小说可能包含超过 100 张图片。较弱的显卡也可以工作，但速度将会稍慢。

#### Stable Diffusion 模型

建议根据自己的目标风格挑选 Stable Diffusion 模型：https://civitai.com/models

对于动漫风格，推荐的模型是基于 Stable Diffusion XL 微调的 Pony 或 Illustrious（以及它们的进一步微调版本）。

下载您喜爱的模型，并将其放置在 `ComfyUI/models/checkpoints` 目录中。然后，您需要修改 `./image/sprite.json` 和 `./image/background.json`，将两个文件第 34 行的 `ckpt_name` 项的值改为您下载的模型文件名。

#### 背景去除模型

我们使用了这个 ComfyUI 扩展来移除角色立绘的背景：https://github.com/ZHO-ZHO-ZHO/ComfyUI-BRIA_AI-RMBG

您需要根据此仓库中的说明安装扩展并下载相应的背景去除模型。

#### Stable Audio 模型

您需要根据 https://comfyanonymous.github.io/ComfyUI_examples/audio/#stable-audio-open-10 的指示下载 Stable Audio 模型并放入 ComfyUI，使其可以被正确识别。

### 关于 ffmpeg 的说明

本项目使用 ffmpeg 将生成的音频文件转换成 opus 格式，从而便于 Ren'Py 引擎识别。

考虑到 ffmpeg 的编译是一项复杂的任务，我们推荐到 https://ffmpeg.org/download.html 下载由社区提供的、编译好的二进制文件。

下载并解压缩后，将 `bin` 目录加入到 PATH 环境变量，以便项目可以找到 ffmpeg。

### 配置 `config.py`

接下来，对 `config.py` 进行以下修改：

修改 `REASONING_MODEL`、`GENERAL_MODEL`、`VL_MODEL`、`SD_PROMPT_MODEL` 等系列变量的值，改为对应的 API Base URL、API Key 和模型名称。其中 `REASONING_MODEL_PROVIDER` 可设置为 `OpenAI` 或 `Gemini`，前者可用于任何 OpenAI 兼容接口，后者可用于 Gemini 系列模型官方 API 的调用。其他类别的 LLM 仅支持 OpenAI 接口。

修改 `COMFY_UI_SERVER_ADDRESS` 的值，改为 ComfyUI 服务端的地址。如果您在本机部署 ComfyUI 且使用默认端口，那么应当是 `127.0.0.1:8188`；如果您在其他服务器部署 ComfyUI 或修改了默认端口，那么需要根据具体的 IP 地址和端口进行调整。

修改 `RENPY_PATH` 的值，改为系统中安装的 Ren'Py SDK 可执行文件的路径。

根据需要修改 `LANGUAGE_MODE` 的值。请注意，本框架在开发和测试阶段全程使用中文（即 `zh` 模式），我们不能保证英文模式获得完全一致的效果。可能会出现预期之外的 bug。

## 启动项目

在启动项目之前，确保您已经启动了 ComfyUI 服务器，且所有 LLM 的接口都可以正常响应。

在项目根目录执行 `uv run main.py` 来启动项目。您将看到一个提示，要求您输入视觉小说的主题。输入主题并回车后，项目将自动执行，生成所有需要的素材。所有素材将被放置于 `./temp` 目录。

您可以随时按下 Ctrl+C 来中断程序。之后再次启动时，如果 `./temp` 目录中对应阶段的文件存在，则框架会自动跳过这一阶段。

> 有时生成任务会阻塞程序，此时程序将不响应任何输入（包括 Ctrl+C），但仍然正常运行。这是一个已知的问题，将在未来寻求解决。

## 导出

在执行导出之前，您需要使用 Ren'Py SDK 手动生成一个空的视觉小说项目，然后将该项目拷贝到此代码库的根目录。否则，导出将会报错。

## 声明

此项目为学术研究目的开发。在某些特定的提示词下，LLM 和 Stable Diffusion 可能生成令人感到不适的内容，或者引发某些法律风险。我们不建议您对项目生成的内容进行传播。我们对生成内容的合法性、原创性或侵权风险不承担任何责任。

> “Titu” 这个名字是怎么来的？
>
> 这个名字属于某个游戏中的一个 NPC 角色。在该游戏中，这名角色负责记录并传播故事。
