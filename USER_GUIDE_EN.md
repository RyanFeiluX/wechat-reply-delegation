# Proxy Reply System - User Guide

## Overview

The Proxy Reply System can automatically reply to group messages on WeChat based on configured rules. You can set conditions such as time periods, online status, and keywords to enable the system to reply automatically at the appropriate time.

## Installation Steps

### 1. Install Python Dependencies

Make sure Python 3.8 or higher is installed on your system. Run the following command to install dependencies:

```bash
pip install pyyaml pytz
```

### 2. Install the Plugin

Copy the plugin directory to the Hermes Gateway plugin directory, or install via pip:

```bash
cd d:\src\proxy-reply-system
pip install .
```

### 3. Configure the Plugin

Create the configuration directory and copy the template:

```bash
mkdir -p ~/.hermes/proxy
cp config-template.yaml ~/.hermes/proxy/config.yaml
```

## Configuration Guide

The configuration file is located at `~/.hermes/proxy/config.yaml`. Open it with a text editor to modify.

### Global Configuration

```yaml
# Enable proxy reply feature
enabled: true

# Timezone (recommended: Asia/Shanghai)
timezone: "Asia/Shanghai"

# Default reply message
default_reply_en: "Hello, I'm an AI assistant. I'll relay your message to the user."
```

### Online Status Detection

```yaml
online_status:
  # Detection mode: passive | manual | hybrid
  mode: hybrid
  
  # Passive mode settings
  passive:
    # Minutes of inactivity before considered offline
    inactivity_timeout_minutes: 30
    # Detection source
    source: last_message
  
  # Manual mode settings
  manual:
    # Enable HTTP webhook
    webhook: true
    # Enable slash commands
    slash_commands: true
```

### Proxy Marker Settings

```yaml
proxy_marker:
  # Add prefix to replies
  prefix_enabled: true
  # Prefix text
  prefix_text_en: "🤖 [Proxy] "
  # Add signature
  signature_enabled: false
  # Signature text
  signature_text_en: "\n-- Auto-replied by Hermes"
```

### Group Configuration

Each group can be configured independently. Add group configurations under the `groups` field:

```yaml
groups:
  "Group ID":
    # Enable proxy reply for this group
    enabled: true
    # Display name (for identification only)
    display_name_en: "My Work Group"
    
    # Schedule rules
    schedule:
      enabled: true
      time_ranges:
        # Weekdays 9:00-18:00
        - days: [mon, tue, wed, thu, fri]
          start: "09:00"
          end: "18:00"
        # Weekends 10:00-16:00
        - days: [sat, sun]
          start: "10:00"
          end: "16:00"
    
    # Online status rules
    online_status:
      # Reply when: always | online_only | offline_only
      reply_when: offline_only
    
    # Trigger conditions
    triggers:
      # Require @mention to trigger
      at_mention: true
      # Keyword triggers
      keywords:
        - "meeting"
        - "quote"
        - "question"
      # Respond to @all
      at_all: false
    
    # Reply instructions
    instructions:
      # Default reply
      default_en: "Hello, I'm an AI assistant. I'll relay your message to the user."
      # Topic-specific responses
      topic_responses:
        - keywords: ["meeting"]
          response_en: "Meeting notification received. The user will check and reply soon."
        - keywords: ["quote", "price"]
          response_en: "Regarding pricing questions, the user will provide details soon."
```

## Getting Group ID

You can get the group ID in the following ways:

1. **Auto-detection**: The system automatically records the group ID when you send messages in the group
2. **Command query**: Send `/proxy status` in the group, the system will return the current group ID

## Chat Commands

Send the following commands in group chat to manage proxy replies:

| Command | Function |
|---------|----------|
| `/proxy status` | Check current group proxy status |
| `/proxy on` | Enable proxy reply for current group |
| `/proxy off` | Disable proxy reply for current group |
| `/proxy away` | Set "away" status (enable proxy) |
| `/proxy back` | Set "back" status (disable proxy) |
| `/proxy config` | View current group configuration |
| `/proxy reload` | Hot reload configuration |

## Web Management Panel

Manage configurations through a visual interface for easier operation.

### Start Command

```bash
# Ensure dependencies are installed
pip install .

# Start web service
hermes-proxy-web
```

### Access URL

- Default address: `http://localhost:5100`
- Custom port via environment variable: `PROXY_REPLY_PORT`

### Default Credentials

- Username: `admin`
- Password: `password123`

### Features

- **Global Configuration**: System status, timezone, log level, proxy markers
- **Group Management**: Add, edit, and delete group configurations
- **Online Status Rules**: Set reply timing (always/online_only/offline_only)
- **Trigger Conditions**: @mention, @all, keyword configuration
- **Schedule Rules**: Multiple time periods support
- **Response Management**: Default replies, topic-specific responses
- **Multi-language Support**: Chinese and English configuration

### Security Tips

1. **Change Default Password**: Recommend changing the default password after first login
2. **HTTPS Access**: Configure HTTPS for production environments
3. **Port Security**: Only expose port in trusted network environments
4. **Session Security**: Log out after completing operations

## Usage Examples

### Scenario 1: Work Hours Proxy

```yaml
groups:
  "work_group@chatroom":
    enabled: true
    display_name_en: "Tech Department Group"
    schedule:
      enabled: true
      time_ranges:
        - days: [mon, tue, wed, thu, fri]
          start: "09:00"
          end: "18:00"
    online_status:
      reply_when: offline_only
    triggers:
      at_mention: true
      keywords: ["API", "bug", "emergency"]
    instructions:
      default_en: "Message received, will relay to user soon."
      topic_responses:
        - keywords: ["bug", "emergency"]
          response_en: "Incident reported! User notified immediately!"
```

### Scenario 2: Offline Auto-reply

```yaml
groups:
  "residents@chatroom":
    enabled: true
    display_name_en: "Residents Group"
    schedule:
      enabled: false
    online_status:
      reply_when: offline_only
    triggers:
      at_mention: true
    instructions:
      default_en: "Hello, the user is unavailable. They will reply when they see your message."
```

### Scenario 3: Topic-based Proxy

```yaml
groups:
  "customers@chatroom":
    enabled: true
    display_name_en: "Customer Service Group"
    schedule:
      enabled: true
      time_ranges:
        - days: [mon, tue, wed, thu, fri]
          start: "09:00"
          end: "21:00"
    online_status:
      reply_when: always
    triggers:
      at_mention: true
      keywords: ["product", "service", "support"]
    instructions:
      default_en: "Thank you for your inquiry. I'll record it and reply soon."
      topic_responses:
        - keywords: ["product", "feature"]
          response_en: "For product feature questions, I'll ask a colleague to answer soon."
        - keywords: ["service", "after-sales"]
          response_en: "Customer service hotline: 400-xxx-xxxx, or leave your contact info and we'll reach out."
```

## Hot Reload

After modifying the configuration file, you can apply changes in the following ways:

1. **Chat command**: Send `/proxy reload` in the group
2. **Command line**: Run `hermes proxy reload`

## Notes

1. **Rate limiting**: Maximum 1 proxy reply per minute per group to avoid spamming
2. **Configuration validation**: If configuration is invalid, system uses defaults and logs errors
3. **Online status**: User messages automatically reset the offline timer
4. **Stop words**: Can exclude certain keywords via `stop_words` configuration

## Troubleshooting

### Issue 1: Proxy reply not working

**Check steps:**
1. Ensure `enabled: true` in config
2. Ensure group configuration is added correctly
3. Verify schedule includes current time
4. Check online status conditions

### Issue 2: "Configuration error" message

**Solutions:**
1. Check YAML format with a text editor
2. Ensure spaces after colons
3. Use spaces for indentation, not tabs
4. Refer to `config-template.yaml` for correct format

### Issue 3: Too frequent replies

**Solutions:**
1. Increase `inactivity_timeout_minutes`
2. Set stricter schedule rules
3. Add more keyword filters

## Contact Support

If you encounter issues or have suggestions, please contact us:
- Email: support@example.com
- @mention the bot in the group with your issue description