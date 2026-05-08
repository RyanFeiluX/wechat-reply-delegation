# Hermes WeChat Reply Delegation Plugin

Automatically reply to WeChat group messages on behalf of users when they are unavailable.

## Features

- **Smart Reply**: Automatically replies to WeChat group messages when the user is offline or busy
- **Schedule-based Replies**: Configure specific time ranges for automatic replies
- **Keyword Triggers**: Trigger replies based on keywords or @mentions
- **Topic Matching**: Customize responses for different topics
- **Web Dashboard**: Manage configurations through a web interface
- **Multi-language Support**: Supports both Chinese and English

## Installation

```bash
pip install hermes-wechat-reply-delegation-plugin
```

## Usage

### As a Hermes Plugin

The plugin is automatically registered with Hermes through entry points. Simply install the package and configure your Hermes agent.

### Web Dashboard

Start the web dashboard using the provided CLI command:

```bash
hermes-wechat-reply-delegation-web
```

The dashboard will be available at `http://localhost:5100`

**Default Credentials:**
- Username: `admin`
- Password: `password123`

### Configuration

Copy and modify the configuration template:

```bash
cp config-template.yaml config.yaml
```

## Requirements

- Python 3.8+
- Hermes Agent
- WeChat Gateway

## Dependencies

- pyyaml
- pytz
- flask
- flask-login
- flask-cors

## License

MIT License