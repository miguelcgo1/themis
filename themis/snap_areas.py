#!/usr/bin/env python3

import gi
import time
from typing import Tuple, Optional, Dict

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gtk, Gdk, GLib, cairo


class SnapArea:
    def __init__(self, x: int, y: int, width: int, height: int, action: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.action = action
        self.active = False


class SnapOverlay(Gtk.Window):
    def __init__(self, screen_width: int, screen_height: int):
        super().__init__()
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Configure window properties
        self.set_app_paintable(True)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_accept_focus(False)
        self.set_can_focus(False)
        
        # Make window transparent
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        
        # Set window size to cover entire screen
        self.set_size_request(screen_width, screen_height)
        self.move(0, 0)
        
        self.connect('draw', self.on_draw)
        
        self.snap_areas = self._create_snap_areas()
        self.current_area = None
        
    def _create_snap_areas(self) -> Dict[str, SnapArea]:
        edge_width = 20  # Width of edge snap areas
        corner_size = 100  # Size of corner areas
        
        return {
            # Edge areas
            'left_edge': SnapArea(0, 0, edge_width, self.screen_height, 'snap_left'),
            'right_edge': SnapArea(self.screen_width - edge_width, 0, edge_width, self.screen_height, 'snap_right'),
            'top_edge': SnapArea(0, 0, self.screen_width, edge_width, 'maximize'),
            'bottom_edge': SnapArea(0, self.screen_height - edge_width, self.screen_width, edge_width, 'center'),
            
            # Corner areas
            'top_left': SnapArea(0, 0, corner_size, corner_size, 'quarter_top_left'),
            'top_right': SnapArea(self.screen_width - corner_size, 0, corner_size, corner_size, 'quarter_top_right'),
            'bottom_left': SnapArea(0, self.screen_height - corner_size, corner_size, corner_size, 'quarter_bottom_left'),
            'bottom_right': SnapArea(self.screen_width - corner_size, self.screen_height - corner_size, corner_size, corner_size, 'quarter_bottom_right'),
            
            # Third areas (when dragging to edges)
            'left_third': SnapArea(0, edge_width, edge_width, self.screen_height - 2*edge_width, 'third_left'),
            'right_third': SnapArea(self.screen_width - edge_width, edge_width, edge_width, self.screen_height - 2*edge_width, 'third_right'),
        }

    def on_draw(self, widget, cr):
        # Clear the surface
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        
        # Draw active snap areas
        if self.current_area:
            area = self.snap_areas[self.current_area]
            
            # Set color based on action type
            if 'quarter' in area.action:
                cr.set_source_rgba(0.2, 0.6, 1.0, 0.3)  # Blue for quarters
            elif 'third' in area.action:
                cr.set_source_rgba(0.8, 0.4, 0.2, 0.3)  # Orange for thirds
            elif area.action == 'maximize':
                cr.set_source_rgba(0.2, 0.8, 0.2, 0.3)  # Green for maximize
            else:
                cr.set_source_rgba(0.6, 0.2, 0.8, 0.3)  # Purple for halves
            
            # Draw filled rectangle for snap area preview
            cr.rectangle(area.x, area.y, area.width, area.height)
            cr.fill()
            
            # Draw border
            cr.set_source_rgba(1.0, 1.0, 1.0, 0.8)
            cr.set_line_width(2)
            cr.rectangle(area.x, area.y, area.width, area.height)
            cr.stroke()
        
        return False

    def update_mouse_position(self, x: int, y: int) -> Optional[str]:
        new_area = None
        
        # Check which area the mouse is in (prioritize corners over edges)
        for area_name, area in self.snap_areas.items():
            if (area.x <= x <= area.x + area.width and 
                area.y <= y <= area.y + area.height):
                if 'quarter' in area.action or 'third' in area.action:
                    new_area = area_name
                    break
                elif new_area is None:
                    new_area = area_name
        
        if new_area != self.current_area:
            self.current_area = new_area
            self.queue_draw()
            
        return new_area

    def get_current_action(self) -> Optional[str]:
        if self.current_area:
            return self.snap_areas[self.current_area].action
        return None

    def hide_overlay(self):
        self.current_area = None
        self.hide()

    def show_overlay(self):
        self.show_all()


class DragSnapManager:
    def __init__(self, window_manager, action_callbacks):
        self.window_manager = window_manager
        self.action_callbacks = action_callbacks
        self.overlay = None
        self.is_dragging = False
        self.drag_window = None
        self.drag_start_time = 0
        
        # Get screen dimensions
        screen_x, screen_y, screen_width, screen_height = window_manager.get_screen_geometry()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Set up mouse tracking
        self._setup_mouse_tracking()

    def _setup_mouse_tracking(self):
        try:
            from pynput.mouse import Listener as MouseListener
            
            self.mouse_listener = MouseListener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click
            )
            self.mouse_listener.start()
        except Exception as e:
            print(f"Failed to set up mouse tracking: {e}")

    def _on_mouse_move(self, x, y):
        if self.is_dragging and self.overlay:
            area = self.overlay.update_mouse_position(x, y)

    def _on_mouse_click(self, x, y, button, pressed):
        from pynput.mouse import Button
        
        if button == Button.left:
            if pressed:
                self._start_drag(x, y)
            else:
                self._end_drag(x, y)

    def _start_drag(self, x, y):
        # Check if we're dragging a window
        active_window = self.window_manager.get_active_window()
        if active_window:
            self.is_dragging = True
            self.drag_window = active_window
            self.drag_start_time = time.time()
            
            # Create and show overlay after a brief delay to avoid accidental triggers
            GLib.timeout_add(200, self._show_overlay_delayed)

    def _show_overlay_delayed(self):
        if self.is_dragging:
            if not self.overlay:
                self.overlay = SnapOverlay(self.screen_width, self.screen_height)
            self.overlay.show_overlay()
        return False  # Don't repeat

    def _end_drag(self, x, y):
        if not self.is_dragging:
            return
            
        self.is_dragging = False
        
        # Check if we dragged long enough and have an overlay
        drag_duration = time.time() - self.drag_start_time
        if drag_duration > 0.2 and self.overlay:
            action = self.overlay.get_current_action()
            
            if action and action in self.action_callbacks and self.drag_window:
                # Execute the snap action
                self.action_callbacks[action]()
        
        # Hide overlay
        if self.overlay:
            self.overlay.hide_overlay()
        
        self.drag_window = None

    def cleanup(self):
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
        if self.overlay:
            self.overlay.destroy()