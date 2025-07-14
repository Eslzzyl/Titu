from google import genai
from google.genai import types


class ChatGemini:
    def __init__(self, model, api_key, base_url=None, temperature=0.7):
        self.model = model
        self.temperature = temperature
        self.client = genai.Client(
            api_key=api_key, http_options=types.HttpOptions(base_url=base_url)
        )

    def invoke(self, input_data):
        response = self.client.models.generate_content(
            model=self.model, contents=[input_data]
        )

        return response.text
