from models.openai import ChatOpenAI
from config import (
    SD_PROMPT_MODEL_API_BASE_URL,
    SD_PROMPT_MODEL_API_KEY,
    SD_PROMPT_MODEL_NAME,
    SD_PROMPT_MODEL_TEMPERATURE,
    LANGUAGE_MODE,
)

if LANGUAGE_MODE == "zh":
    from prompt_zh import (
        GENERATE_SPRITE_SD_PROMPT,
        GENERATE_BACKGROUND_SD_PROMPT,
        GENERATE_CG_SD_PROMPT,
    )
else:
    from prompt_en import (
        GENERATE_SPRITE_SD_PROMPT,
        GENERATE_BACKGROUND_SD_PROMPT,
        GENERATE_CG_SD_PROMPT,
    )


class SDPromptModel:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=SD_PROMPT_MODEL_NAME,
            api_key=SD_PROMPT_MODEL_API_KEY,
            base_url=SD_PROMPT_MODEL_API_BASE_URL,
            temperature=SD_PROMPT_MODEL_TEMPERATURE,
        ).bind(response_format={"type": "json_object"})

    def run_sprite(self, character_setting, script, stream=False):
        if LANGUAGE_MODE == "zh":
            human_message = f"角色设定：{character_setting}\n\nRen'Py脚本：{script}"
        else:
            human_message = (
                f"Character Setting: {character_setting}\n\nRen'Py Script: {script}"
            )
        messages = [
            ("system", GENERATE_SPRITE_SD_PROMPT),
            ("user", human_message),
        ]

        if stream:
            return self.stream_invoke(messages)
        return self.llm.invoke(messages)

    def run_background(self, world_view, script, stream=False):
        if LANGUAGE_MODE == "zh":
            human_message = f"世界观设定：{world_view}\n\nRen'Py脚本：{script}"
        else:
            human_message = (
                f"World View Setting: {world_view}\n\nRen'Py Script: {script}"
            )
        messages = [
            ("system", GENERATE_BACKGROUND_SD_PROMPT),
            ("user", human_message),
        ]

        if stream:
            return self.stream_invoke(messages)
        return self.llm.invoke(messages)

    def run_cg(self, world_view, character_setting, script, stream=False):
        if LANGUAGE_MODE == "zh":
            human_message = f"世界观设定：{world_view}\n\n角色设定：{character_setting}\n\nRen'Py脚本：{script}"
        else:
            human_message = f"World View Setting: {world_view}\n\nCharacter Setting: {character_setting}\n\nRen'Py Script: {script}"
        messages = [
            ("system", GENERATE_CG_SD_PROMPT),
            ("user", human_message),
        ]

        if stream:
            return self.stream_invoke(messages)
        return self.llm.invoke(messages)

    def stream_invoke(self, messages):
        for chunk in self.llm.stream_invoke(messages):
            yield chunk
