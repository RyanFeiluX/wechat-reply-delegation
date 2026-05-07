from typing import Optional, Any
from .handler import ProxyReplyHandler


class ProxyReplyPlugin:
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