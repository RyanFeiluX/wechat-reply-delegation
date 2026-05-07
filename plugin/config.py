import os
import yaml
from typing import Optional, Dict, Any
from pathlib import Path


class ConfigManager:
    CONFIG_PATH = "~/.hermes/wechat-reply-delegation/config.yaml"
    
    def __init__(self):
        self.config = {}
        self._load_config()

    def _load_config(self):
        path = Path(self.CONFIG_PATH).expanduser()
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            except Exception:
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
            self._save_config()

    def _get_default_config(self) -> Dict:
        return {
            "enabled": True,
            "timezone": "Asia/Shanghai",
            "online_status": {
                "mode": "hybrid",
                "passive": {
                    "inactivity_timeout_minutes": 30,
                    "source": "last_message"
                },
                "manual": {
                    "webhook": True,
                    "slash_commands": True
                }
            },
            "proxy_marker": {
                "prefix_enabled": True,
                "prefix_text": "🤖 [代班] ",
                "prefix_text_en": "🤖 [Proxy] ",
                "signature_enabled": False,
                "signature_text": "",
                "signature_text_en": ""
            },
            "default_reply": "您好，用户暂时不在，他看到消息后会尽快回复您 🙏",
            "default_reply_en": "Hello, the user is unavailable. They will reply when they see your message.",
            "log_level": "info",
            "groups": {}
        }

    def _save_config(self):
        path = Path(self.CONFIG_PATH).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)

    def get_group_config(self, group_id: str) -> Optional[Dict]:
        groups = self.config.get("groups", {})
        return groups.get(group_id)

    def reload(self) -> bool:
        try:
            self._load_config()
            return True
        except Exception:
            return False

    def validate(self, config: Dict) -> Dict:
        errors = []
        if "enabled" not in config:
            errors.append("Missing 'enabled' field")
        if "timezone" not in config:
            errors.append("Missing 'timezone' field")
        return {"valid": len(errors) == 0, "errors": errors}

    def get_global_config(self) -> Dict:
        return {k: v for k, v in self.config.items() if k != "groups"}