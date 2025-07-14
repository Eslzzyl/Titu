from models.openai import ChatOpenAI
from models.gemini import ChatGemini
from config import (
    REASONING_MODEL_PROVIDER,
    REASONING_MODEL_API_BASE_URL,
    REASONING_MODEL_API_KEY,
    REASONING_MODEL_NAME,
    REASONING_MODEL_TEMPERATURE,
)


class ReasoningModel:
    def __init__(self):
        if REASONING_MODEL_PROVIDER == "OpenAI":
            self.llm = ChatOpenAI(
                model=REASONING_MODEL_NAME,
                api_key=REASONING_MODEL_API_KEY,
                base_url=REASONING_MODEL_API_BASE_URL,
                temperature=REASONING_MODEL_TEMPERATURE,
            )
        elif REASONING_MODEL_PROVIDER == "Gemini":
            self.llm = ChatGemini(
                model=REASONING_MODEL_NAME,
                api_key=REASONING_MODEL_API_KEY,
                base_url=REASONING_MODEL_API_BASE_URL,
                temperature=REASONING_MODEL_TEMPERATURE,
            )

    def run(self, input_text: str, stream=False):
        if stream:
            return self.stream_run(input_text)
        message = self.llm.invoke(input_text)
        return message.content if hasattr(message, "content") else message

    def stream_run(self, input_text: str):
        for chunk in self.llm.stream_invoke(input_text):
            yield chunk
