from typing import Optional, Any
from .handler import ProxyReplyHandler


class ProxyReplyPlugin:
    name = "wechat-reply-delegation"
    version = "0.1.0"
    description = "Automatically reply to WeChat group messages on behalf of users"
    
    def __init__(self, gateway):
        self.gateway = gateway
        self.handler = ProxyReplyHandler()

    async def on_message(self, event):
        if event.source.chat_type != "group":
            return

        if event.source.platform != "weixin":
            return

        handled = await self.handler.handle_group_message(event, self.gateway.adapters["weixin"])
        if handled:
            event.stop_propagation()

    async def on_start(self):
        pass

    async def on_stop(self):
        pass

    def get_config_schema(self):
        return {}

    def get_metadata(self):
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": "Hermes Agent",
            "platforms": ["weixin"],
            "capabilities": ["group_message_handling", "auto_reply"]
        }