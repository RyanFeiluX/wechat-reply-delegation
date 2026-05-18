import os
import shutil
import sys
from pathlib import Path

CONFIG_DIR = "~/.hermes/wechat-reply-delegation"
CONFIG_FILE = "config.yaml"
TEMPLATE_FILE = "config-template.yaml"

def get_config_dir():
    return Path(os.path.expanduser(CONFIG_DIR))

def get_config_path():
    return get_config_dir() / CONFIG_FILE

def install():
    config_dir = get_config_dir()
    config_path = get_config_path()
    
    print("🔧 Setting up WeChat Reply Delegation plugin...")
    
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created config directory: {config_dir}")
    except Exception as e:
        print(f"❌ Failed to create config directory: {e}")
        return False
    
    template_path = Path(__file__).parent.parent / TEMPLATE_FILE
    if template_path.exists():
        try:
            shutil.copy(template_path, config_path)
            print(f"✅ Copied config template to: {config_path}")
        except Exception as e:
            print(f"❌ Failed to copy config template: {e}")
            return False
    else:
        print(f"⚠️ Config template not found at {template_path}, creating default config")
        create_default_config(config_path)
    
    print("\n🎉 Installation complete!")
    print("\n📋 Next steps:")
    print("1. Edit the config file:")
    print(f"   nano {config_path}")
    print("\n2. Enable the plugin in your Hermes Gateway config:")
    print("   Add 'wechat-reply-delegation' to the plugins list")
    print("\n3. Start Hermes Gateway")
    print("\n4. Optional: Start the web dashboard:")
    print("   hermes-wechat-reply-delegation-web")
    
    return True

def create_default_config(config_path):
    default_config = """# WeChat Reply Delegation Configuration
enabled: true
timezone: "Asia/Shanghai"

online_status:
  mode: hybrid
  passive:
    inactivity_timeout_minutes: 30
    source: last_message
  manual:
    webhook: true
    slash_commands: true

proxy_marker:
  prefix_enabled: true
  prefix_text: "🤖 [代班] "
  prefix_text_en: "🤖 [Proxy] "
  signature_enabled: false
  signature_text: "\\n—— 由 Hermes 代班回复"
  signature_text_en: "\\n-- Auto-replied by Hermes"

groups: {}
"""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(default_config)
        return True
    except Exception as e:
        print(f"❌ Failed to create default config: {e}")
        return False

def main():
    success = install()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()