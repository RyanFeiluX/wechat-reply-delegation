from typing import Optional, Any
import threading
import os
from .handler import ProxyReplyHandler


class ProxyReplyPlugin:
    name = "wechat-reply-delegation"
    version = "0.1.0"
    description = "Automatically reply to WeChat group messages on behalf of users"
    
    def __init__(self, gateway):
        self.gateway = gateway
        self.handler = ProxyReplyHandler()
        self.web_server_thread = None
        self.web_server_running = False
        self.web_server_port = int(os.environ.get('WECHAT_REPLY_DELEGATION_PORT', 5100))

    async def on_message(self, event):
        if event.source.chat_type != "group":
            return

        if event.source.platform != "weixin":
            return

        handled = await self.handler.handle_group_message(event, self.gateway.adapters["weixin"])
        if handled:
            event.stop_propagation()

    async def on_start(self):
        self._start_web_server()

    async def on_stop(self):
        self._stop_web_server()

    def _start_web_server(self):
        if self.web_server_running:
            return
        
        def run_web_server():
            from web.app import app
            app.run(host='0.0.0.0', port=self.web_server_port, debug=False, use_reloader=False)
        
        self.web_server_thread = threading.Thread(target=run_web_server, daemon=True)
        self.web_server_thread.start()
        self.web_server_running = True

    def _stop_web_server(self):
        self.web_server_running = False

    def get_config_schema(self):
        return {}

    def get_metadata(self):
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": "Hermes Agent",
            "platforms": ["weixin"],
            "capabilities": ["group_message_handling", "auto_reply"],
            "web_ui": {
                "enabled": True,
                "port": self.web_server_port,
                "path": "/",
                "url": f"http://localhost:{self.web_server_port}",
                "title": "WeChat Reply Delegation Config",
                "icon": "settings"
            },
            "actions": [
                {
                    "id": "open_config",
                    "label": "Open Configuration",
                    "description": "Open the web configuration interface",
                    "type": "web_ui",
                    "url": f"http://localhost:{self.web_server_port}"
                }
            ]
        }

    def get_actions(self):
        return [
            {
                "id": "open_config",
                "label": "Open Configuration",
                "description": "Open the web configuration interface for managing WeChat reply delegation settings",
                "type": "external_url",
                "url": f"http://localhost:{self.web_server_port}",
                "icon": "🔧"
            }
        ]