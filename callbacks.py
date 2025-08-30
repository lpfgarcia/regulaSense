import json
from langchain.callbacks.base import BaseCallbackHandler

class MessagesHandler(BaseCallbackHandler):

    def __init__(self, file="conversa.json"):
        self.file = file
        self.data = []

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.data.append({"role": "user", "content": prompts})

    def on_llm_end(self, response, **kwargs):
        for gen in response.generations:
            self.data.append({"role": "assistant", "content": gen[0].text})
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)