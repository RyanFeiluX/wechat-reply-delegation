import time
from typing import Dict, Optional


class OnlineStatusDetector:
    def __init__(self):
        self.user_status: Dict[str, str] = {}
        self.last_active: Dict[str, float] = {}
        self.manual_status: Dict[str, Optional[str]] = {}
        self.config = {
            "mode": "hybrid",
            "passive": {
                "inactivity_timeout_minutes": 30,
                "source": "last_message"
            },
            "manual": {
                "webhook": True,
                "slash_commands": True
            }
        }

    def get_status(self, user_id: str = "default") -> str:
        if self.config["mode"] == "manual":
            return self._get_manual_status(user_id)
        elif self.config["mode"] == "passive":
            return self._get_passive_status(user_id)
        else:
            return self._get_hybrid_status(user_id)

    def _get_manual_status(self, user_id: str) -> str:
        return self.manual_status.get(user_id, "online")

    def _get_passive_status(self, user_id: str) -> str:
        last_active = self.last_active.get(user_id, 0)
        timeout = self.config["passive"]["inactivity_timeout_minutes"] * 60
        if time.time() - last_active > timeout:
            return "offline"
        return "online"

    def _get_hybrid_status(self, user_id: str) -> str:
        manual = self.manual_status.get(user_id)
        if manual:
            return manual
        return self._get_passive_status(user_id)

    def update_last_active(self, user_id: str = "default"):
        self.last_active[user_id] = time.time()
        if self.config["mode"] == "hybrid":
            self.manual_status.pop(user_id, None)

    def set_manual_status(self, status: str, user_id: str = "default"):
        if status in ["online", "away", "offline"]:
            self.manual_status[user_id] = status