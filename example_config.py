REASONING_MODEL_PROVIDER = "OpenAI"     # Options: "OpenAI", "Gemini"
REASONING_MODEL_API_BASE_URL = "https://api.deepseek.com/v1"
REASONING_MODEL_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"
REASONING_MODEL_NAME = "deepseek-reasoner"      # Recommended: DeepSeek-R1-0528、Gemini 2.5 Pro/Flash
REASONING_MODEL_TEMPERATURE = 0.7

GENERAL_MODEL_API_BASE_URL = "https://api.deepseek.com/v1"
GENERAL_MODEL_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"
GENERAL_MODEL_NAME = "deepseek-chat"
GENERAL_MODEL_TEMPERATURE = 0.6

VL_MODEL_API_BASE_URL = "https://api-inference.modelscope.cn/v1/"
VL_MODEL_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"
VL_MODEL_NAME = "Qwen/Qwen2.5-VL-72B-Instruct"
VL_MODEL_TEMPERATURE = 0.1

SD_PROMPT_MODEL_API_BASE_URL = "https://api-inference.modelscope.cn/v1/"
SD_PROMPT_MODEL_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"
SD_PROMPT_MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
SD_PROMPT_MODEL_TEMPERATURE = 0.7

LINT_MODEL_API_BASE_URL = "https://api-inference.modelscope.cn/v1/"
LINT_MODEL_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"
LINT_MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
LINT_MODEL_TEMPERATURE = 0.7

COMFY_UI_SERVER_ADDRESS = "127.0.0.1:8188"

MAX_CONCURRENT_REQUESTS = 1     # No need to change
MAX_RETRY_TIMES = 3     # Max retry times for image self-correction

RENPY_PATH = "D:\\Tools\\renpy-8.3.4-sdk\\lib\\py3-windows-x86_64\\python.exe D:\\Tools\\renpy-8.3.4-sdk\\renpy.py"

LANGUAGE_MODE = "zh"  # "zh" or "en"

# For our paper writing only, won't be used in the actual pipeline
TRANSLATE_MODEL_API_BASE_URL = "http://127.0.0.1:8080/v1/"
TRANSLATE_MODEL_API_KEY = "eslzzyl"
TRANSLATE_MODEL_NAME = "model"
TRANSLATE_MODEL_TEMPERATURE = 0.7

# For our paper writing only, won't be used in the actual pipeline
EVALUATE_MODEL_API_BASE_URL = "https://api.openai.com/v1/"
EVALUATE_MODEL_API_KEY = "sk-abcdefghijklmnopqrstuvwxyz1234567890"
EVALUATE_MODEL_NAME = "gemini-2.5-flash-preview-04-17"
EVALUATE_MODEL_TEMPERATURE = 0
