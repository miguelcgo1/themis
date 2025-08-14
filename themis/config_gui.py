#!/usr/bin/env python3

import gi
import json
import os
from typing import Dict, Any

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject


class ConfigWindow(Gtk.Window):
    def __init__(self, config_manager, hotkey_manager, on_config_changed=None):
        super().__init__()
        
        self.config_manager = config_manager
        self.hotkey_manager = hotkey_manager
        self.on_config_changed = on_config_changed
        
        self.set_title("Rectangle Linux - Configuration")
        self.set_default_size(600, 500)
        self.set_resizable(True)
        
        # Create main container
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)
        
        # Add tabs
        self._create_hotkeys_tab()
        self._create_behavior_tab()
        self._create_about_tab()
        
        # Load current configuration
        self._load_current_config()
        
        self.show_all()

    def _create_hotkeys_tab(self):
        # Hotkeys configuration tab
        hotkeys_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hotkeys_box.set_border_width(10)
        
        # Title
        title = Gtk.Label()
        title.set_markup("<b>Keyboard Shortcuts</b>")
        title.set_halign(Gtk.Align.START)
        hotkeys_box.pack_start(title, False, False, 0)
        
        # Create scrollable area for hotkeys
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_size_request(-1, 350)
        
        self.hotkeys_grid = Gtk.Grid()
        self.hotkeys_grid.set_column_spacing(15)
        self.hotkeys_grid.set_row_spacing(8)
        self.hotkeys_grid.set_border_width(5)
        
        scrolled.add(self.hotkeys_grid)
        hotkeys_box.pack_start(scrolled, True, True, 0)
        
        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.END)
        
        reset_button = Gtk.Button.new_with_label("Reset to Defaults")
        reset_button.connect("clicked", self._on_reset_hotkeys)
        button_box.pack_start(reset_button, False, False, 0)
        
        apply_button = Gtk.Button.new_with_label("Apply")
        apply_button.connect("clicked", self._on_apply_hotkeys)
        apply_button.get_style_context().add_class("suggested-action")
        button_box.pack_start(apply_button, False, False, 0)
        
        hotkeys_box.pack_start(button_box, False, False, 0)
        
        self.notebook.append_page(hotkeys_box, Gtk.Label("Hotkeys"))

    def _create_behavior_tab(self):
        # Behavior configuration tab
        behavior_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        behavior_box.set_border_width(10)
        
        # Title
        title = Gtk.Label()
        title.set_markup("<b>Behavior Settings</b>")
        title.set_halign(Gtk.Align.START)
        behavior_box.pack_start(title, False, False, 0)
        
        # Enable/Disable drag to snap
        self.drag_snap_check = Gtk.CheckButton.new_with_label("Enable drag-to-snap areas")
        self.drag_snap_check.set_tooltip_text("Show snap areas when dragging windows")
        behavior_box.pack_start(self.drag_snap_check, False, False, 0)
        
        # Animation settings
        animation_frame = Gtk.Frame()
        animation_frame.set_label("Animation")
        animation_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        animation_box.set_border_width(10)
        
        self.animation_check = Gtk.CheckButton.new_with_label("Enable window animations")
        animation_box.pack_start(self.animation_check, False, False, 0)
        
        # Animation speed
        speed_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        speed_label = Gtk.Label("Animation speed:")
        speed_box.pack_start(speed_label, False, False, 0)
        
        self.speed_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.1, 2.0, 0.1)
        self.speed_scale.set_value(1.0)
        self.speed_scale.set_hexpand(True)
        speed_box.pack_start(self.speed_scale, True, True, 0)
        
        animation_box.pack_start(speed_box, False, False, 0)
        animation_frame.add(animation_box)
        behavior_box.pack_start(animation_frame, False, False, 0)
        
        # Startup settings
        startup_frame = Gtk.Frame()
        startup_frame.set_label("Startup")
        startup_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        startup_box.set_border_width(10)
        
        self.autostart_check = Gtk.CheckButton.new_with_label("Start Rectangle Linux on login")
        startup_box.pack_start(self.autostart_check, False, False, 0)
        
        startup_frame.add(startup_box)
        behavior_box.pack_start(startup_frame, False, False, 0)
        
        # Apply button
        apply_button = Gtk.Button.new_with_label("Apply")
        apply_button.connect("clicked", self._on_apply_behavior)
        apply_button.set_halign(Gtk.Align.END)
        apply_button.get_style_context().add_class("suggested-action")
        behavior_box.pack_start(apply_button, False, False, 0)
        
        self.notebook.append_page(behavior_box, Gtk.Label("Behavior"))

    def _create_about_tab(self):
        # About tab
        about_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        about_box.set_border_width(20)
        about_box.set_halign(Gtk.Align.CENTER)
        about_box.set_valign(Gtk.Align.CENTER)
        
        # App name and version
        name_label = Gtk.Label()
        name_label.set_markup("<span size='xx-large'><b>Rectangle Linux</b></span>")
        about_box.pack_start(name_label, False, False, 0)
        
        version_label = Gtk.Label("Version 1.0.0")
        about_box.pack_start(version_label, False, False, 0)
        
        # Description
        desc_label = Gtk.Label()
        desc_label.set_markup("<i>A Rectangle clone for Linux\nWindow management made easy</i>")
        desc_label.set_justify(Gtk.Justification.CENTER)
        about_box.pack_start(desc_label, False, False, 0)
        
        # Compatibility info
        compat_label = Gtk.Label()
        compat_label.set_markup("Compatible with:\n• X11 and Wayland\n• All major Linux distributions\n• GNOME, KDE, XFCE, and more")
        compat_label.set_justify(Gtk.Justification.CENTER)
        about_box.pack_start(compat_label, False, False, 0)
        
        self.notebook.append_page(about_box, Gtk.Label("About"))

    def _load_current_config(self):
        config = self.config_manager.get_config()
        
        # Load hotkeys
        self._populate_hotkeys_grid()
        
        # Load behavior settings
        self.drag_snap_check.set_active(config.get('enable_drag_snap', True))
        self.animation_check.set_active(config.get('enable_animations', True))
        self.speed_scale.set_value(config.get('animation_speed', 1.0))
        self.autostart_check.set_active(config.get('autostart', False))

    def _populate_hotkeys_grid(self):
        # Clear existing widgets
        for child in self.hotkeys_grid.get_children():
            self.hotkeys_grid.remove(child)
        
        # Action descriptions
        action_descriptions = {
            'snap_left': 'Snap to Left Half',
            'snap_right': 'Snap to Right Half',
            'maximize': 'Maximize Window',
            'center': 'Center Window',
            'quarter_top_left': 'Top Left Quarter',
            'quarter_top_right': 'Top Right Quarter',
            'quarter_bottom_left': 'Bottom Left Quarter',
            'quarter_bottom_right': 'Bottom Right Quarter',
            'third_left': 'Left Third',
            'third_right': 'Right Third',
            'third_top': 'Top Third',
            'third_bottom': 'Bottom Third',
        }
        
        # Headers
        action_header = Gtk.Label()
        action_header.set_markup("<b>Action</b>")
        action_header.set_halign(Gtk.Align.START)
        self.hotkeys_grid.attach(action_header, 0, 0, 1, 1)
        
        hotkey_header = Gtk.Label()
        hotkey_header.set_markup("<b>Hotkey</b>")
        hotkey_header.set_halign(Gtk.Align.START)
        self.hotkeys_grid.attach(hotkey_header, 1, 0, 1, 1)
        
        # Get current hotkey mappings
        config = self.config_manager.get_config()
        hotkeys = config.get('hotkeys', {})
        
        self.hotkey_entries = {}
        row = 1
        
        for action, description in action_descriptions.items():
            # Action label
            action_label = Gtk.Label(description)
            action_label.set_halign(Gtk.Align.START)
            self.hotkeys_grid.attach(action_label, 0, row, 1, 1)
            
            # Hotkey entry
            entry = Gtk.Entry()
            entry.set_placeholder_text("Click to set hotkey...")
            entry.set_editable(False)
            entry.connect("button-press-event", self._on_hotkey_entry_clicked, action)
            
            # Set current hotkey if exists
            if action in hotkeys:
                entry.set_text(hotkeys[action])
            
            self.hotkey_entries[action] = entry
            self.hotkeys_grid.attach(entry, 1, row, 1, 1)
            
            row += 1
        
        self.hotkeys_grid.show_all()

    def _on_hotkey_entry_clicked(self, entry, event, action):
        dialog = HotkeyCaptureDialog(self, action)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            hotkey_string = dialog.get_hotkey_string()
            if hotkey_string:
                entry.set_text(hotkey_string)
        
        dialog.destroy()

    def _on_reset_hotkeys(self, button):
        # Reset to default hotkeys
        for action, entry in self.hotkey_entries.items():
            # Find default hotkey for this action
            for combo, default_action in self.hotkey_manager.default_hotkeys.items():
                if default_action == action:
                    hotkey_string = self.hotkey_manager.get_hotkey_string(combo)
                    entry.set_text(hotkey_string)
                    break
            else:
                entry.set_text("")

    def _on_apply_hotkeys(self, button):
        # Collect hotkey settings
        hotkeys = {}
        for action, entry in self.hotkey_entries.items():
            text = entry.get_text().strip()
            if text:
                hotkeys[action] = text
        
        # Update configuration
        self.config_manager.update_config('hotkeys', hotkeys)
        
        if self.on_config_changed:
            self.on_config_changed('hotkeys')

    def _on_apply_behavior(self, button):
        # Collect behavior settings
        config_updates = {
            'enable_drag_snap': self.drag_snap_check.get_active(),
            'enable_animations': self.animation_check.get_active(),
            'animation_speed': self.speed_scale.get_value(),
            'autostart': self.autostart_check.get_active(),
        }
        
        for key, value in config_updates.items():
            self.config_manager.update_config(key, value)
        
        if self.on_config_changed:
            self.on_config_changed('behavior')


class HotkeyCaptureDialog(Gtk.Dialog):
    def __init__(self, parent, action):
        super().__init__(title=f"Set Hotkey for {action}", 
                         transient_for=parent, 
                         flags=Gtk.DialogFlags.MODAL)
        
        self.action = action
        self.captured_keys = []
        self.listening = False
        
        # Add buttons
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("OK", Gtk.ResponseType.OK)
        
        # Create content
        content = self.get_content_area()
        content.set_spacing(10)
        content.set_border_width(20)
        
        label = Gtk.Label(f"Press the key combination for '{action}':")
        content.pack_start(label, False, False, 0)
        
        self.display_label = Gtk.Label()
        self.display_label.set_markup("<i>Waiting for keys...</i>")
        content.pack_start(self.display_label, False, False, 0)
        
        # Start listening for keys
        self.connect("key-press-event", self._on_key_press)
        self.connect("key-release-event", self._on_key_release)
        
        content.show_all()
        
        self.listening = True

    def _on_key_press(self, widget, event):
        if not self.listening:
            return False
        
        key_name = Gdk.keyval_name(event.keyval)
        
        # Convert some key names
        if key_name in ['Super_L', 'Super_R']:
            key_name = 'Super'
        elif key_name in ['Control_L', 'Control_R']:
            key_name = 'Ctrl'
        elif key_name in ['Alt_L', 'Alt_R']:
            key_name = 'Alt'
        elif key_name in ['Shift_L', 'Shift_R']:
            key_name = 'Shift'
        
        if key_name not in self.captured_keys and key_name not in ['Super', 'Ctrl', 'Alt', 'Shift']:
            self.captured_keys.append(key_name)
        
        # Update display
        self._update_display()
        
        return True  # Prevent default handling

    def _on_key_release(self, widget, event):
        # Don't do anything on key release for now
        return True

    def _update_display(self):
        modifiers = []
        keys = []
        
        for key in self.captured_keys:
            if key in ['Super', 'Ctrl', 'Alt', 'Shift']:
                modifiers.append(key)
            else:
                keys.append(key)
        
        all_keys = modifiers + keys
        display_text = " + ".join(all_keys) if all_keys else "Waiting for keys..."
        
        self.display_label.set_text(display_text)

    def get_hotkey_string(self):
        if self.captured_keys:
            return " + ".join(self.captured_keys)
        return ""