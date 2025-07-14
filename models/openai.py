from openai import OpenAI


class ChatOpenAI:
    def __init__(self, model, api_key, base_url, temperature):
        # Initialize openai library configuration
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def bind(self, response_format=None):
        self.response_format = response_format
        return self

    def _prepare_messages(self, input_data):
        # Check input type and convert to Chat API message format
        if isinstance(input_data, str):
            messages = [{"role": "user", "content": input_data}]
        else:
            # Assume input_data is a list of tuples in the format (role, content)
            messages = []
            for role, content in input_data:
                # Convert invalid role to valid 'user'
                if role.lower() == "human":
                    role = "user"
                messages.append({"role": role, "content": content})
        return messages

    def invoke(self, input_data, stream=False):
        messages = self._prepare_messages(input_data)

        if stream:
            return self.stream_invoke(messages)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            response_format=getattr(self, "response_format", None),
        )
        return response.choices[0].message

    def stream_invoke(self, messages):
        messages = self._prepare_messages(messages)

        stream_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            response_format=getattr(self, "response_format", None),
            stream=True,
            max_tokens=8000,
        )

        for chunk in stream_response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
