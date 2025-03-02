import os
import json
import platform
from pathlib import Path

DEFAULT_CONFIG = {
    "container_manager": "docker",
    "use_x11": True,
    "mount_dev_dir": True
}

def get_config_dir():
    """Get the configuration directory based on the platform."""
    if platform.system() == "Windows":
        config_dir = os.path.join(os.environ.get("APPDATA", ""), "rosbox")
    else:  # Linux, MacOS, etc.
        config_dir = os.path.join(os.path.expanduser("~"), ".config", "rosbox")

    # Ensure the directory exists
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def get_config_file():
    """Get the path to the config file."""
    return os.path.join(get_config_dir(), "config.json")

def load_config():
    """Load the configuration file or create default if not exists."""
    config_file = get_config_file()

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                # Merge with defaults to ensure all needed keys exist
                config = DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config file: {e}")
            print("Using default configuration.")
            return DEFAULT_CONFIG
    else:
        # Create a default config file
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    """Save the configuration to file."""
    config_file = get_config_file()
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except IOError as e:
        print(f"Error saving config file: {e}")
        return False

def update_config(key, value):
    """Update a specific configuration value."""
    config = load_config()
    if key in config:
        config[key] = value
        return save_config(config)
    return False
