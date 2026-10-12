import json
import os


class BestScore:
    def __init__(self, path: str = "best_score.json"):
        self.path = path
        self.value = self._load()

    def _load(self) -> int:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return int(json.load(f).get("score", 0))
        except (OSError, ValueError, TypeError):
            return 0

    def update(self, score: int) -> bool:
        """Persist if score beats the record; returns True on new best."""
        if int(score) <= self.value:
            return False
        self.value = int(score)
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({"score": self.value}, f)
        except OSError:
            pass
        return True