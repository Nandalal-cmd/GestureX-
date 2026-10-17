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


class Leaderboard:
    """Top-N score table persisted to disk."""

    def __init__(self, path: str = "leaderboard.json", size: int = 5):
        self.path = path
        self.size = max(1, int(size))
        self.entries = self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data = data.get("scores", [])
            scores = sorted((int(x) for x in data), reverse=True)
            return scores[:self.size]
        except (OSError, ValueError, TypeError):
            return []

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({"scores": self.entries}, f)
        except OSError:
            pass

    def add(self, score: int) -> bool:
        """Insert score if it qualifies; returns True if the table changed."""
        score = int(score)
        if score <= 0:
            return False
        combined = sorted(self.entries + [score], reverse=True)[:self.size]
        if combined == self.entries:
            return False
        self.entries = combined
        self._save()
        return True

    def best(self) -> int:
        return self.entries[0] if self.entries else 0

    def rank_of(self, score: int) -> int:
        """1-based rank the given score would take, or 0 if it doesn't make it."""
        score = int(score)
        if score <= 0:
            return 0
        for i, s in enumerate(self.entries):
            if score >= s:
                return i + 1
        if len(self.entries) < self.size:
            return len(self.entries) + 1
        return 0