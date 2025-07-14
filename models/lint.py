from models.openai import ChatOpenAI
from config import (
    LINT_MODEL_API_BASE_URL,
    LINT_MODEL_API_KEY,
    LINT_MODEL_NAME,
    LINT_MODEL_TEMPERATURE,
)


class LintModel:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=LINT_MODEL_NAME,
            api_key=LINT_MODEL_API_KEY,
            base_url=LINT_MODEL_API_BASE_URL,
            temperature=LINT_MODEL_TEMPERATURE,
        )

    def run(self, input_text: str):
        return self.llm.invoke(input_text)
