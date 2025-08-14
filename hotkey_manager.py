#!/usr/bin/env python3

import os
import threading
import time
from typing import Dict, Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode, Listener
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib


class HotkeyManager:
    def __init__(self):
        self.hotkeys: Dict[tuple, Callable] = {}
        self.pressed_keys = set()
        self.listener = None
        self.running = False
        
        # Default hotkey mappings (Rectangle-like)
        self.default_hotkeys = {
            (Key.cmd, Key.left): 'snap_left',
            (Key.cmd, Key.right): 'snap_right', 
            (Key.cmd, Key.up): 'maximize',
            (Key.cmd, Key.down): 'center',
            (Key.cmd, KeyCode.from_char('1')): 'quarter_top_left',
            (Key.cmd, KeyCode.from_char('2')): 'quarter_top_right',
            (Key.cmd, KeyCode.from_char('3')): 'quarter_bottom_left',
            (Key.cmd, KeyCode.from_char('4')): 'quarter_bottom_right',
            (Key.ctrl, Key.alt, Key.left): 'third_left',
            (Key.ctrl, Key.alt, Key.right): 'third_right',
            (Key.ctrl, Key.alt, Key.up): 'third_top',
            (Key.ctrl, Key.alt, Key.down): 'third_bottom',
        }

    def register_hotkey(self, key_combo: tuple, callback: Callable):
        self.hotkeys[key_combo] = callback

    def unregister_hotkey(self, key_combo: tuple):
        if key_combo in self.hotkeys:
            del self.hotkeys[key_combo]

    def _normalize_key(self, key):
        if hasattr(key, 'char') and key.char:
            return KeyCode.from_char(key.char.lower())
        elif key == Key.cmd_l or key == Key.cmd_r:
            return Key.cmd
        elif key == Key.ctrl_l or key == Key.ctrl_r:
            return Key.ctrl
        elif key == Key.alt_l or key == Key.alt_r:
            return Key.alt
        elif key == Key.shift_l or key == Key.shift_r:
            return Key.shift
        return key

    def _on_press(self, key):
        normalized_key = self._normalize_key(key)
        self.pressed_keys.add(normalized_key)
        
        # Check for hotkey matches
        for hotkey_combo, callback in self.hotkeys.items():
            if self._matches_combo(hotkey_combo):
                GLib.idle_add(callback)
                return

    def _on_release(self, key):
        normalized_key = self._normalize_key(key)
        self.pressed_keys.discard(normalized_key)

    def _matches_combo(self, combo: tuple) -> bool:
        return set(combo).issubset(self.pressed_keys)

    def start_listening(self):
        if self.running:
            return
            
        self.running = True
        try:
            self.listener = Listener(
                on_press=self._on_press,
                on_release=self._on_release,
                suppress=False
            )
            self.listener.start()
        except Exception as e:
            print(f"Failed to start hotkey listener: {e}")
            self.running = False

    def stop_listening(self):
        self.running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.pressed_keys.clear()

    def get_hotkey_string(self, combo: tuple) -> str:
        key_names = []
        for key in combo:
            if key == Key.cmd:
                key_names.append("Super")
            elif key == Key.ctrl:
                key_names.append("Ctrl")
            elif key == Key.alt:
                key_names.append("Alt")
            elif key == Key.shift:
                key_names.append("Shift")
            elif hasattr(key, 'char') and key.char:
                key_names.append(key.char.upper())
            elif hasattr(key, 'name'):
                key_names.append(key.name.title())
            else:
                key_names.append(str(key))
        
        return "+".join(key_names)

    def parse_hotkey_string(self, hotkey_str: str) -> tuple:
        parts = [part.strip().lower() for part in hotkey_str.split('+')]
        keys = []
        
        for part in parts:
            if part in ['super', 'cmd', 'meta']:
                keys.append(Key.cmd)
            elif part == 'ctrl':
                keys.append(Key.ctrl)
            elif part == 'alt':
                keys.append(Key.alt)
            elif part == 'shift':
                keys.append(Key.shift)
            elif part == 'left':
                keys.append(Key.left)
            elif part == 'right':
                keys.append(Key.right)
            elif part == 'up':
                keys.append(Key.up)
            elif part == 'down':
                keys.append(Key.down)
            elif len(part) == 1 and part.isalnum():
                keys.append(KeyCode.from_char(part))
            
        return tuple(keys) if keys else tuple()

    def register_defaults(self, action_callbacks: Dict[str, Callable]):
        for combo, action in self.default_hotkeys.items():
            if action in action_callbacks:
                self.register_hotkey(combo, action_callbacks[action])

    def clear_all_hotkeys(self):
        self.hotkeys.clear()