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

### From PyPI (Recommended)

**Single command installation:**

```bash
pip install hermes-wechat-reply-delegation-plugin && hermes-wechat-reply-delegation-install
```

Or install and configure separately:

```bash
# Install the package
pip install hermes-wechat-reply-delegation-plugin

# Run the installer to set up configuration
hermes-wechat-reply-delegation-install
```

### Directly from GitHub

**Single command installation from GitHub:**

```bash
pip install git+https://github.com/RyanFeiluX/wechat-reply-delegation.git && hermes-wechat-reply-delegation-install
```

**Install from a specific branch:**

```bash
pip install git+https://github.com/RyanFeiluX/wechat-reply-delegation.git@main && hermes-wechat-reply-delegation-install
```

## Usage

### Quick Start

After installation, the plugin is automatically registered with Hermes. Just:

1. Enable the plugin in your Hermes Gateway config by adding `wechat-reply-delegation` to the plugins list
2. Start Hermes Gateway

### Web Dashboard

Start the web dashboard for visual configuration management:

```bash
hermes-wechat-reply-delegation-web
```

The dashboard will be available at `http://localhost:5100`

**Default Credentials:**
- Username: `admin`
- Password: `password123`

### Configuration

The installer automatically creates the config file at `~/.hermes/wechat-reply-delegation/config.yaml`.

Edit the configuration file:
```bash
nano ~/.hermes/wechat-reply-delegation/config.yaml
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