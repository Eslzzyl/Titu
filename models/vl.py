from models.openai import ChatOpenAI
from config import (
    VL_MODEL_API_BASE_URL,
    VL_MODEL_API_KEY,
    VL_MODEL_NAME,
    VL_MODEL_TEMPERATURE,
)


class VLModel:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=VL_MODEL_NAME,
            api_key=VL_MODEL_API_KEY,
            base_url=VL_MODEL_API_BASE_URL,
            temperature=VL_MODEL_TEMPERATURE,
        )

    def run(self, input_text: str):
        return self.llm.invoke(input_text)
