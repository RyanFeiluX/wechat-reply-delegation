import subprocess
import sys
import os

def run_command(command, cwd=None):
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    print("=== WeChat Reply Delegation Plugin Reinstaller ===")
    print()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Working directory: {current_dir}")
    
    print("\n1. Checking for existing installation...")
    result = run_command("pip list | findstr hermes-wechat-reply-delegation-plugin")
    
    if result:
        print("   Found existing installation. Uninstalling...")
        run_command("pip uninstall -y hermes-wechat-reply-delegation-plugin")
        print("   Uninstallation complete.")
    else:
        print("   No existing installation found.")
    
    print("\n2. Installing latest version...")
    result = run_command(f"pip install \"{current_dir}\"")
    
    if result:
        print("   Installation complete.")
    else:
        print("   Installation failed!")
        sys.exit(1)
    
    print("\n3. Verifying installation...")
    result = run_command("pip list | findstr hermes-wechat-reply-delegation-plugin")
    
    if result:
        print(f"   ✓ Plugin installed: {result}")
        print("\n=== Reinstallation completed successfully! ===")
        print("\nNext steps:")
        print("1. Restart your Flask server")
        print("2. Clear your browser cache (Ctrl+Shift+R)")
        print("3. Reload the web page")
    else:
        print("   ✗ Verification failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()