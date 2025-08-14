#!/usr/bin/env python3

import sys
import os
import signal
import argparse
from typing import Dict, Callable

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, GLib, AppIndicator3

from window_manager import WindowManager
from hotkey_manager import HotkeyManager
from snap_areas import DragSnapManager
from config_manager import ConfigManager
from config_gui import ConfigWindow


class Themis:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.window_manager = WindowManager()
        self.hotkey_manager = HotkeyManager()
        self.drag_snap_manager = None
        self.config_window = None
        
        # Set up actions
        self.actions: Dict[str, Callable] = {
            'snap_left': self.snap_left,
            'snap_right': self.snap_right,
            'maximize': self.maximize,
            'center': self.center,
            'quarter_top_left': self.quarter_top_left,
            'quarter_top_right': self.quarter_top_right,
            'quarter_bottom_left': self.quarter_bottom_left,
            'quarter_bottom_right': self.quarter_bottom_right,
            'third_left': self.third_left,
            'third_right': self.third_right,
            'third_top': self.third_top,
            'third_bottom': self.third_bottom,
        }
        
        # Set up system tray
        self._setup_system_tray()
        
        # Register hotkeys
        self._register_hotkeys()
        
        # Set up drag-to-snap if enabled
        if self.config_manager.get_value('enable_drag_snap', True):
            self.drag_snap_manager = DragSnapManager(self.window_manager, self.actions)

    def _setup_system_tray(self):
        self.indicator = AppIndicator3.Indicator.new(
            "themis",
            "preferences-system-windows",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self._create_menu())

    def _create_menu(self):
        menu = Gtk.Menu()
        
        # Configuration item
        config_item = Gtk.MenuItem.new_with_label("Configure...")
        config_item.connect("activate", self._on_configure)
        menu.append(config_item)
        
        # Separator
        separator = Gtk.SeparatorMenuItem()
        menu.append(separator)
        
        # Test actions submenu
        test_menu = Gtk.Menu()
        test_item = Gtk.MenuItem.new_with_label("Test Actions")
        test_item.set_submenu(test_menu)
        
        for action_name in self.actions.keys():
            action_item = Gtk.MenuItem.new_with_label(action_name.replace('_', ' ').title())
            action_item.connect("activate", lambda item, action=action_name: self.actions[action]())
            test_menu.append(action_item)
        
        menu.append(test_item)
        
        # Separator
        separator2 = Gtk.SeparatorMenuItem()
        menu.append(separator2)
        
        # About item
        about_item = Gtk.MenuItem.new_with_label("About")
        about_item.connect("activate", self._on_about)
        menu.append(about_item)
        
        # Quit item
        quit_item = Gtk.MenuItem.new_with_label("Quit")
        quit_item.connect("activate", self._on_quit)
        menu.append(quit_item)
        
        menu.show_all()
        return menu

    def _register_hotkeys(self):
        hotkeys_config = self.config_manager.get_value('hotkeys', {})
        
        for action, hotkey_string in hotkeys_config.items():
            if action in self.actions:
                try:
                    key_combo = self.hotkey_manager.parse_hotkey_string(hotkey_string)
                    if key_combo:
                        self.hotkey_manager.register_hotkey(key_combo, self.actions[action])
                except Exception as e:
                    print(f"Failed to register hotkey {hotkey_string} for {action}: {e}")

    def _on_configure(self, item):
        if self.config_window is None:
            self.config_window = ConfigWindow(
                self.config_manager, 
                self.hotkey_manager,
                self._on_config_changed
            )
            self.config_window.connect("delete-event", self._on_config_window_closed)
        else:
            self.config_window.present()

    def _on_config_window_closed(self, window, event):
        self.config_window = None
        return False

    def _on_config_changed(self, section):
        if section == 'hotkeys':
            # Re-register hotkeys
            self.hotkey_manager.clear_all_hotkeys()
            self._register_hotkeys()
        elif section == 'behavior':
            # Handle behavior changes
            if self.config_manager.get_value('enable_drag_snap', True):
                if self.drag_snap_manager is None:
                    self.drag_snap_manager = DragSnapManager(self.window_manager, self.actions)
            else:
                if self.drag_snap_manager:
                    self.drag_snap_manager.cleanup()
                    self.drag_snap_manager = None

    def _on_about(self, item):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_program_name("Themis")
        about_dialog.set_version("1.0.0")
        about_dialog.set_comments("Themis - Window management for Linux\nBased on Rectangle for macOS")
        about_dialog.set_copyright("© 2025")
        about_dialog.set_website("https://github.com/miguel/themis")
        about_dialog.set_logo_icon_name("preferences-system-windows")
        about_dialog.run()
        about_dialog.destroy()

    def _on_quit(self, item):
        self.cleanup()
        Gtk.main_quit()

    def cleanup(self):
        if self.hotkey_manager:
            self.hotkey_manager.stop_listening()
        if self.drag_snap_manager:
            self.drag_snap_manager.cleanup()

    # Window action methods
    def snap_left(self):
        self._snap_to_position('left')

    def snap_right(self):
        self._snap_to_position('right')

    def maximize(self):
        window = self.window_manager.get_active_window()
        if window:
            self.window_manager.maximize_window(window)

    def center(self):
        self._snap_to_position('center')

    def quarter_top_left(self):
        self._snap_to_position('quarter_top_left')

    def quarter_top_right(self):
        self._snap_to_position('quarter_top_right')

    def quarter_bottom_left(self):
        self._snap_to_position('quarter_bottom_left')

    def quarter_bottom_right(self):
        self._snap_to_position('quarter_bottom_right')

    def third_left(self):
        self._snap_to_position('third_left')

    def third_right(self):
        self._snap_to_position('third_right')

    def third_top(self):
        self._snap_to_position('third_top')

    def third_bottom(self):
        self._snap_to_position('third_bottom')

    def _snap_to_position(self, position: str):
        window = self.window_manager.get_active_window()
        if not window:
            return

        screen_x, screen_y, screen_width, screen_height = self.window_manager.get_screen_geometry()
        margin = self.config_manager.get_value('window_margin', 5)
        
        # Calculate target geometry based on position
        if position == 'left':
            x, y = screen_x + margin, screen_y + margin
            width, height = screen_width // 2 - margin * 2, screen_height - margin * 2
        
        elif position == 'right':
            x = screen_x + screen_width // 2 + margin
            y = screen_y + margin
            width, height = screen_width // 2 - margin * 2, screen_height - margin * 2
        
        elif position == 'center':
            width, height = screen_width * 2 // 3, screen_height * 2 // 3
            x = screen_x + (screen_width - width) // 2
            y = screen_y + (screen_height - height) // 2
        
        elif position == 'quarter_top_left':
            x, y = screen_x + margin, screen_y + margin
            width = screen_width // 2 - margin * 2
            height = screen_height // 2 - margin * 2
        
        elif position == 'quarter_top_right':
            x = screen_x + screen_width // 2 + margin
            y = screen_y + margin
            width = screen_width // 2 - margin * 2
            height = screen_height // 2 - margin * 2
        
        elif position == 'quarter_bottom_left':
            x = screen_x + margin
            y = screen_y + screen_height // 2 + margin
            width = screen_width // 2 - margin * 2
            height = screen_height // 2 - margin * 2
        
        elif position == 'quarter_bottom_right':
            x = screen_x + screen_width // 2 + margin
            y = screen_y + screen_height // 2 + margin
            width = screen_width // 2 - margin * 2
            height = screen_height // 2 - margin * 2
        
        elif position == 'third_left':
            x, y = screen_x + margin, screen_y + margin
            width = screen_width // 3 - margin * 2
            height = screen_height - margin * 2
        
        elif position == 'third_right':
            x = screen_x + screen_width * 2 // 3 + margin
            y = screen_y + margin
            width = screen_width // 3 - margin * 2
            height = screen_height - margin * 2
        
        elif position == 'third_top':
            x, y = screen_x + margin, screen_y + margin
            width = screen_width - margin * 2
            height = screen_height // 3 - margin * 2
        
        elif position == 'third_bottom':
            x = screen_x + margin
            y = screen_y + screen_height * 2 // 3 + margin
            width = screen_width - margin * 2
            height = screen_height // 3 - margin * 2
        
        else:
            return

        # Apply the new geometry
        self.window_manager.move_resize_window(window, x, y, width, height)

    def run(self):
        # Start hotkey listening
        self.hotkey_manager.start_listening()
        
        # Run the main loop
        try:
            Gtk.main()
        except KeyboardInterrupt:
            print("\nShutting down Themis...")
        finally:
            self.cleanup()


def main():
    parser = argparse.ArgumentParser(description='Themis - Window Management')
    parser.add_argument('--config', action='store_true', 
                       help='Open configuration window')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Handle SIGINT gracefully
    def signal_handler(sig, frame):
        print("\nShutting down Rectangle Linux...")
        Gtk.main_quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and run the application
    app = Themis()
    
    if args.config:
        app._on_configure(None)
    
    if args.debug:
        app.config_manager.update_config('debug_mode', True)
    
    print("Themis started. Use system tray to configure or quit.")
    app.run()


if __name__ == "__main__":
    main()