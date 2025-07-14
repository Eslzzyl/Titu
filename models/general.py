from models.openai import ChatOpenAI
from config import (
    GENERAL_MODEL_API_BASE_URL,
    GENERAL_MODEL_API_KEY,
    GENERAL_MODEL_NAME,
    GENERAL_MODEL_TEMPERATURE,
)


class GeneralModel:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=GENERAL_MODEL_NAME,
            api_key=GENERAL_MODEL_API_KEY,
            base_url=GENERAL_MODEL_API_BASE_URL,
            temperature=GENERAL_MODEL_TEMPERATURE,
        )

    def run(self, input_text: str, stream=False):
        if stream:
            return self.stream_run(input_text)
        return self.llm.invoke(input_text)
        
    def stream_run(self, input_text: str):
        for chunk in self.llm.stream_invoke(input_text):
            yield chunk
