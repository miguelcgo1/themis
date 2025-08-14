#!/usr/bin/env python3

import os
import sys
import subprocess
from typing import Tuple, Optional, List
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Wnck', '3.0')

from gi.repository import Gtk, Gdk, Wnck, GObject

try:
    from Xlib import display as x_display
    from Xlib.ext import randr
    XLIB_AVAILABLE = True
except ImportError:
    XLIB_AVAILABLE = False


class WindowManager:
    def __init__(self):
        self.is_wayland = os.environ.get('XDG_SESSION_TYPE') == 'wayland'
        self.display = None
        
        if not self.is_wayland and XLIB_AVAILABLE:
            try:
                self.display = x_display.Display()
            except:
                self.display = None
        
        self.screen = None
        if not self.is_wayland:
            Wnck.Screen.get_default().force_update()
            self.screen = Wnck.Screen.get_default()

    def get_screen_geometry(self) -> Tuple[int, int, int, int]:
        if self.is_wayland:
            return self._get_wayland_screen_geometry()
        else:
            return self._get_x11_screen_geometry()

    def _get_wayland_screen_geometry(self) -> Tuple[int, int, int, int]:
        try:
            gdk_display = Gdk.Display.get_default()
            monitor = gdk_display.get_primary_monitor()
            if monitor:
                geometry = monitor.get_geometry()
                return geometry.x, geometry.y, geometry.width, geometry.height
        except:
            pass
        
        return 0, 0, 1920, 1080

    def _get_x11_screen_geometry(self) -> Tuple[int, int, int, int]:
        if self.display:
            try:
                screen = self.display.screen()
                return 0, 0, screen.width_in_pixels, screen.height_in_pixels
            except:
                pass
        
        gdk_screen = Gdk.Screen.get_default()
        return 0, 0, gdk_screen.get_width(), gdk_screen.get_height()

    def get_active_window(self):
        if self.is_wayland:
            return self._get_wayland_active_window()
        else:
            return self._get_x11_active_window()

    def _get_wayland_active_window(self):
        try:
            result = subprocess.run(['swaymsg', '-t', 'get_tree'], 
                                  capture_output=True, text=True, timeout=1)
            if result.returncode == 0:
                import json
                tree = json.loads(result.stdout)
                return self._find_focused_window(tree)
        except:
            pass
        return None

    def _find_focused_window(self, node):
        if node.get('focused', False):
            return node
        for child in node.get('nodes', []) + node.get('floating_nodes', []):
            result = self._find_focused_window(child)
            if result:
                return result
        return None

    def _get_x11_active_window(self):
        if self.screen:
            return self.screen.get_active_window()
        return None

    def move_resize_window(self, window, x: int, y: int, width: int, height: int):
        if self.is_wayland:
            self._wayland_move_resize(window, x, y, width, height)
        else:
            self._x11_move_resize(window, x, y, width, height)

    def _wayland_move_resize(self, window, x: int, y: int, width: int, height: int):
        try:
            if window and 'id' in window:
                commands = [
                    f'[con_id="{window["id"]}"] floating enable',
                    f'[con_id="{window["id"]}"] resize set {width} {height}',
                    f'[con_id="{window["id"]}"] move position {x} {y}'
                ]
                for cmd in commands:
                    subprocess.run(['swaymsg', cmd], timeout=1)
        except Exception as e:
            print(f"Wayland resize error: {e}")

    def _x11_move_resize(self, window, x: int, y: int, width: int, height: int):
        if window and hasattr(window, 'set_geometry'):
            try:
                gravity = Wnck.WindowGravity.NORTHWEST
                geometry_mask = (Wnck.WindowMoveResizeMask.X | 
                               Wnck.WindowMoveResizeMask.Y |
                               Wnck.WindowMoveResizeMask.WIDTH |
                               Wnck.WindowMoveResizeMask.HEIGHT)
                
                window.set_geometry(gravity, geometry_mask, x, y, width, height)
            except Exception as e:
                print(f"X11 resize error: {e}")

    def maximize_window(self, window):
        if self.is_wayland:
            try:
                if window and 'id' in window:
                    subprocess.run(['swaymsg', f'[con_id="{window["id"]}"] fullscreen'], timeout=1)
            except:
                pass
        else:
            if window and hasattr(window, 'maximize'):
                window.maximize()

    def get_window_list(self) -> List:
        if self.is_wayland:
            return self._get_wayland_windows()
        else:
            return self._get_x11_windows()

    def _get_wayland_windows(self) -> List:
        try:
            result = subprocess.run(['swaymsg', '-t', 'get_tree'], 
                                  capture_output=True, text=True, timeout=1)
            if result.returncode == 0:
                import json
                tree = json.loads(result.stdout)
                windows = []
                self._collect_windows(tree, windows)
                return windows
        except:
            pass
        return []

    def _collect_windows(self, node, windows):
        if node.get('type') == 'con' and node.get('name'):
            windows.append(node)
        for child in node.get('nodes', []) + node.get('floating_nodes', []):
            self._collect_windows(child, windows)

    def _get_x11_windows(self) -> List:
        windows = []
        if self.screen:
            for window in self.screen.get_windows():
                if window.get_window_type() == Wnck.WindowType.NORMAL:
                    windows.append(window)
        return windows