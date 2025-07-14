import websocket  # NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
import random
from PIL import Image
import io
from typing import List


class ComfyUI:
    def __init__(self, server_address: str):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.ws = websocket.WebSocket()
        self.ws.connect(
            "ws://{}/ws?clientId={}".format(self.server_address, self.client_id)
        )

    def __del__(self):
        self.ws.close()

    def _queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode("utf-8")
        req = urllib.request.Request(
            "http://{}/prompt".format(self.server_address), data=data
        )
        return json.loads(urllib.request.urlopen(req).read())

    def _get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(
            "http://{}/view?{}".format(self.server_address, url_values)
        ) as response:
            return response.read()

    def _get_audio(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(
            "http://{}/view?{}".format(self.server_address, url_values)
        ) as response:
            return response.read()

    def _get_history(self, prompt_id):
        with urllib.request.urlopen(
            "http://{}/history/{}".format(self.server_address, prompt_id)
        ) as response:
            return json.loads(response.read())

    def _generate_outputs(self, ws, prompt):
        prompt_id = self._queue_prompt(prompt)["prompt_id"]
        output_data = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message["type"] == "executing":
                    data = message["data"]
                    if data["node"] is None and data["prompt_id"] == prompt_id:
                        break  # Execution is done
            else:
                continue  # previews are binary data

        history = self._get_history(prompt_id)[prompt_id]
        for node_id in history["outputs"]:
            node_output = history["outputs"][node_id]
            outputs = []

            # 处理图像输出
            if "images" in node_output:
                for image in node_output["images"]:
                    data = self._get_image(
                        image["filename"], image["subfolder"], image["type"]
                    )
                    outputs.append(("image", data))

            # 处理音频输出
            if "audio" in node_output:
                for audio in node_output["audio"]:
                    data = self._get_audio(
                        audio["filename"], audio["subfolder"], audio["type"]
                    )
                    outputs.append(("audio", data))

            output_data[node_id] = outputs

        return output_data

    def _generate_images(self, ws, prompt):
        outputs = self._generate_outputs(ws, prompt)
        output_images = {}

        for node_id, data_list in outputs.items():
            images_output = []
            for data_type, data in data_list:
                if data_type == "image":
                    images_output.append(data)
            output_images[node_id] = images_output

        return output_images

    def _generate_audio_files(self, ws, prompt):
        outputs = self._generate_outputs(ws, prompt)
        output_audio = {}

        for node_id, data_list in outputs.items():
            audio_output = []
            for data_type, data in data_list:
                if data_type == "audio":
                    audio_output.append(data)
            output_audio[node_id] = audio_output

        return output_audio

    def generate_image(
        self,
        prompt_file: str,
        positive_prompt: str,
        negative_prompt: str | None = None,
        seed: int | None = None,
        batch_size: int = 1,
    ) -> List[Image.Image]:
        with open(prompt_file, "r", encoding="utf-8") as file:
            self.prompt = json.loads(file.read())
        self.prompt["6"]["inputs"]["text"] = positive_prompt
        if negative_prompt is not None:
            self.prompt["7"]["inputs"]["text"] = negative_prompt
        else:
            self.prompt["7"]["inputs"]["text"] = (
                "(nsfw:1.1), text, watermark, nude, lowres, worst quality, bad quality, bad, jpeg artifacts, unfinished, extra digits, scan, [abstract], sketch, bad anatomy, artistic error, duplicate, mutation, deformed, disfigured, artist name, ai-generated, ai-assisted"
            )
        if seed is None:
            self.prompt["3"]["inputs"]["seed"] = random.randint(0, 1000000)
        else:
            self.prompt["3"]["inputs"]["seed"] = seed

        self.prompt["5"]["inputs"]["batch_size"] = batch_size

        images = self._generate_images(self.ws, self.prompt)
        return [Image.open(io.BytesIO(image)) for image in images.get("13", [])]

    def generate_audio(
        self,
        prompt_file: str,
        positive_prompt: str,
        negative_prompt: str | None = None,
        seed: int | None = None,
        duration_seconds: int = 10,
        batch_size: int = 1,
    ) -> List[bytes]:
        with open(prompt_file, "r", encoding="utf-8") as file:
            self.prompt = json.loads(file.read())

        self.prompt["6"]["inputs"]["text"] = positive_prompt
        if negative_prompt is not None:
            self.prompt["7"]["inputs"]["text"] = negative_prompt

        if seed is None:
            self.prompt["3"]["inputs"]["seed"] = random.randint(0, 1000000)
        else:
            self.prompt["3"]["inputs"]["seed"] = seed

        # Set duration and batch size
        self.prompt["11"]["inputs"]["seconds"] = duration_seconds
        self.prompt["11"]["inputs"]["batch_size"] = batch_size

        audio_files = self._generate_audio_files(self.ws, self.prompt)
        return audio_files.get("13", [])
