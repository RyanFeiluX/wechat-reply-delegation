from typing import Optional, Any, Dict
from .config import ConfigManager
from .engine import ConditionEngine


class ProxyReplyHandler:
    def __init__(self):
        self.engine = ConditionEngine()
        self.config_manager = ConfigManager()

    async def handle_group_message(self, message, adapter) -> bool:
        group_id = message.source.room_id
        
        group_config = self.config_manager.get_group_config(group_id)
        if not group_config:
            return False

        if not group_config.get("enabled", False):
            return False

        message_text = getattr(message, "text", "")
        language = self._detect_language(message_text)

        result = self.engine.evaluate(group_config, message, language)
        
        if result["passed"]:
            reply_text = self._build_reply(result["response_text"], group_config, language)
            await adapter.send_message(group_id, reply_text)
            return True
        
        return False

    def _detect_language(self, text: str) -> str:
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_chars = sum(1 for c in text if 'a' <= c.lower() <= 'z')
        
        if chinese_chars > english_chars:
            return "zh"
        return "en"

    def _build_reply(self, instruction: str, config: Dict, language: str) -> str:
        proxy_marker = config.get("proxy_marker", {})
        
        if language == "en":
            prefix = proxy_marker.get("prefix_text_en", "") if proxy_marker.get("prefix_enabled", True) else ""
            signature = proxy_marker.get("signature_text_en", "") if proxy_marker.get("signature_enabled", False) else ""
        else:
            prefix = proxy_marker.get("prefix_text", "") if proxy_marker.get("prefix_enabled", True) else ""
            signature = proxy_marker.get("signature_text", "") if proxy_marker.get("signature_enabled", False) else ""
        
        return f"{prefix}{instruction}{signature}"