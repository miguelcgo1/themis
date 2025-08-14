#!/usr/bin/env python3

import os
import json
import configparser
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / '.config' / 'rectangle-linux'
        self.config_file = self.config_dir / 'config.json'
        self.autostart_dir = Path.home() / '.config' / 'autostart'
        self.autostart_file = self.autostart_dir / 'rectangle-linux.desktop'
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self._config = self._load_config()

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'hotkeys': {
                'snap_left': 'Super+Left',
                'snap_right': 'Super+Right',
                'maximize': 'Super+Up',
                'center': 'Super+Down',
                'quarter_top_left': 'Super+1',
                'quarter_top_right': 'Super+2',
                'quarter_bottom_left': 'Super+3',
                'quarter_bottom_right': 'Super+4',
                'third_left': 'Ctrl+Alt+Left',
                'third_right': 'Ctrl+Alt+Right',
                'third_top': 'Ctrl+Alt+Up',
                'third_bottom': 'Ctrl+Alt+Down',
            },
            'enable_drag_snap': True,
            'enable_animations': True,
            'animation_speed': 1.0,
            'autostart': False,
            'window_margin': 5,
            'snap_threshold': 20,
            'show_notifications': True,
            'debug_mode': False,
        }

    def _load_config(self) -> Dict[str, Any]:
        default_config = self._get_default_config()
        
        if not self.config_file.exists():
            return default_config
        
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            config = default_config.copy()
            config.update(loaded_config)
            return config
            
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            print(f"Error loading config: {e}. Using defaults.")
            return default_config

    def _save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_config(self) -> Dict[str, Any]:
        return self._config.copy()

    def get_value(self, key: str, default=None):
        return self._config.get(key, default)

    def update_config(self, key: str, value: Any):
        self._config[key] = value
        self._save_config()
        
        # Handle special cases
        if key == 'autostart':
            self._handle_autostart(value)

    def update_multiple(self, updates: Dict[str, Any]):
        self._config.update(updates)
        self._save_config()
        
        # Handle special cases
        if 'autostart' in updates:
            self._handle_autostart(updates['autostart'])

    def reset_to_defaults(self):
        self._config = self._get_default_config()
        self._save_config()

    def _handle_autostart(self, enable: bool):
        try:
            if enable:
                self._create_autostart_entry()
            else:
                self._remove_autostart_entry()
        except Exception as e:
            print(f"Error handling autostart: {e}")

    def _create_autostart_entry(self):
        self.autostart_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the path to the main script
        script_dir = Path(__file__).parent.resolve()
        main_script = script_dir / 'rectangle_linux.py'
        
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=Rectangle Linux
Comment=Window management for Linux
Exec=python3 {main_script}
Icon=preferences-system-windows
StartupNotify=false
NoDisplay=true
Hidden=false
X-GNOME-Autostart-enabled=true
"""
        
        try:
            with open(self.autostart_file, 'w') as f:
                f.write(desktop_content)
            print(f"Created autostart entry: {self.autostart_file}")
        except Exception as e:
            print(f"Failed to create autostart entry: {e}")

    def _remove_autostart_entry(self):
        try:
            if self.autostart_file.exists():
                self.autostart_file.unlink()
                print(f"Removed autostart entry: {self.autostart_file}")
        except Exception as e:
            print(f"Failed to remove autostart entry: {e}")

    def get_hotkey_combo(self, action: str) -> Optional[str]:
        hotkeys = self._config.get('hotkeys', {})
        return hotkeys.get(action)

    def set_hotkey(self, action: str, hotkey_string: str):
        if 'hotkeys' not in self._config:
            self._config['hotkeys'] = {}
        
        self._config['hotkeys'][action] = hotkey_string
        self._save_config()

    def remove_hotkey(self, action: str):
        if 'hotkeys' in self._config and action in self._config['hotkeys']:
            del self._config['hotkeys'][action]
            self._save_config()

    def export_config(self, file_path: str) -> bool:
        try:
            with open(file_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False

    def import_config(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r') as f:
                imported_config = json.load(f)
            
            # Validate and merge
            default_config = self._get_default_config()
            for key, value in imported_config.items():
                if key in default_config:
                    self._config[key] = value
            
            self._save_config()
            return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False

    def get_config_file_path(self) -> str:
        return str(self.config_file)