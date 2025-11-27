import json
import random
from pathlib import Path

class GreetingsTools:
    def __init__(self, json_path: str):
        self.path = Path(json_path)
        with open(self.path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def random_greeting(self) -> str:
        return random.choice(self.data.get("greetings", []))

    def random_farewell(self) -> str:
        return random.choice(self.data.get("farewells", []))

    def random_thanks_reply(self) -> str:
        return random.choice(self.data.get("thanks_replies", []))
