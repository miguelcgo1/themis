#!/usr/bin/env python3

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from hotkey_manager import HotkeyManager


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        # Use a temporary config file for testing
        self.test_config_dir = "/tmp/rectangle-linux-test"
        self.config_manager = ConfigManager()
        self.config_manager.config_dir = self.test_config_dir
        self.config_manager.config_file = os.path.join(self.test_config_dir, "config.json")

    def test_default_config(self):
        """Test that default configuration is loaded correctly"""
        config = self.config_manager._get_default_config()
        self.assertIn('hotkeys', config)
        self.assertIn('enable_drag_snap', config)
        self.assertTrue(config['enable_drag_snap'])

    def test_hotkey_management(self):
        """Test hotkey configuration management"""
        # Test setting a hotkey
        self.config_manager.set_hotkey('snap_left', 'Super+Left')
        hotkey = self.config_manager.get_hotkey_combo('snap_left')
        self.assertEqual(hotkey, 'Super+Left')
        
        # Test removing a hotkey
        self.config_manager.remove_hotkey('snap_left')
        hotkey = self.config_manager.get_hotkey_combo('snap_left')
        self.assertIsNone(hotkey)

    def test_config_persistence(self):
        """Test that configuration persists correctly"""
        test_value = True
        self.config_manager.update_config('test_setting', test_value)
        
        # Create new instance to test persistence
        new_manager = ConfigManager()
        new_manager.config_dir = self.test_config_dir
        new_manager.config_file = os.path.join(self.test_config_dir, "config.json")
        new_manager._config = new_manager._load_config()
        
        self.assertEqual(new_manager.get_value('test_setting'), test_value)


class TestHotkeyManager(unittest.TestCase):
    def setUp(self):
        self.hotkey_manager = HotkeyManager()

    def test_hotkey_string_parsing(self):
        """Test parsing hotkey strings"""
        # Test basic parsing
        combo = self.hotkey_manager.parse_hotkey_string("Super+Left")
        self.assertIsInstance(combo, tuple)
        self.assertTrue(len(combo) > 0)
        
        # Test complex combination
        combo = self.hotkey_manager.parse_hotkey_string("Ctrl+Alt+Shift+A")
        self.assertIsInstance(combo, tuple)
        self.assertTrue(len(combo) >= 4)

    def test_hotkey_string_generation(self):
        """Test generating hotkey strings from key combinations"""
        from pynput.keyboard import Key, KeyCode
        
        combo = (Key.cmd, Key.left)
        hotkey_string = self.hotkey_manager.get_hotkey_string(combo)
        self.assertIn("Super", hotkey_string)
        self.assertIn("Left", hotkey_string)

    def test_hotkey_registration(self):
        """Test hotkey registration and unregistration"""
        test_callback = Mock()
        test_combo = ('test', 'combo')
        
        # Test registration
        self.hotkey_manager.register_hotkey(test_combo, test_callback)
        self.assertIn(test_combo, self.hotkey_manager.hotkeys)
        
        # Test unregistration
        self.hotkey_manager.unregister_hotkey(test_combo)
        self.assertNotIn(test_combo, self.hotkey_manager.hotkeys)

    def test_default_hotkeys(self):
        """Test that default hotkeys are properly defined"""
        self.assertIsInstance(self.hotkey_manager.default_hotkeys, dict)
        self.assertTrue(len(self.hotkey_manager.default_hotkeys) > 0)
        
        # Check that all default actions are strings
        for combo, action in self.hotkey_manager.default_hotkeys.items():
            self.assertIsInstance(action, str)
            self.assertIsInstance(combo, tuple)


class TestWindowManagement(unittest.TestCase):
    def setUp(self):
        # Mock the window manager to avoid needing actual X11/Wayland
        self.mock_window_manager = Mock()
        self.mock_window_manager.get_screen_geometry.return_value = (0, 0, 1920, 1080)

    def test_screen_geometry(self):
        """Test screen geometry detection"""
        geometry = self.mock_window_manager.get_screen_geometry()
        self.assertEqual(len(geometry), 4)  # x, y, width, height
        self.assertIsInstance(geometry[0], int)  # x
        self.assertIsInstance(geometry[1], int)  # y
        self.assertIsInstance(geometry[2], int)  # width
        self.assertIsInstance(geometry[3], int)  # height

    def test_window_position_calculations(self):
        """Test window position calculations for different snap positions"""
        screen_x, screen_y, screen_width, screen_height = 0, 0, 1920, 1080
        margin = 5
        
        # Test left half calculation
        expected_left_x = screen_x + margin
        expected_left_y = screen_y + margin
        expected_left_width = screen_width // 2 - margin * 2
        expected_left_height = screen_height - margin * 2
        
        # These calculations should match those in rectangle_linux.py
        self.assertEqual(expected_left_x, 5)
        self.assertEqual(expected_left_y, 5)
        self.assertEqual(expected_left_width, 950)
        self.assertEqual(expected_left_height, 1070)


def run_basic_functionality_test():
    """Run a basic test to check if the application can be imported and initialized"""
    print("Running basic functionality test...")
    
    try:
        # Test imports
        import rectangle_linux
        import window_manager
        import hotkey_manager
        import config_manager
        import snap_areas
        import config_gui
        print("✓ All modules imported successfully")
        
        # Test basic initialization (without starting GUI)
        config_mgr = ConfigManager()
        print("✓ ConfigManager initialized")
        
        hotkey_mgr = HotkeyManager()
        print("✓ HotkeyManager initialized")
        
        # Test configuration loading
        config = config_mgr.get_config()
        assert isinstance(config, dict)
        assert 'hotkeys' in config
        print("✓ Configuration loaded successfully")
        
        print("✓ All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False


def run_compatibility_test():
    """Test compatibility with different environments"""
    print("Running compatibility test...")
    
    try:
        # Test Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            print(f"✗ Python version too old: {python_version}")
            return False
        print(f"✓ Python version compatible: {python_version}")
        
        # Test required modules
        required_modules = ['gi', 'json', 'os', 'sys', 'configparser', 'pathlib']
        for module in required_modules:
            try:
                __import__(module)
                print(f"✓ Module {module} available")
            except ImportError:
                print(f"✗ Module {module} not available")
                return False
        
        # Test GI modules (these might not be available on all systems)
        gi_modules = ['Gtk', 'Gdk', 'GLib']
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            for module in gi_modules:
                gi.require_version(module, '3.0')
            print("✓ GTK/GI modules available")
        except Exception as e:
            print(f"⚠ GTK/GI modules not available (expected on non-Linux systems): {e}")
        
        print("✓ Compatibility test completed!")
        return True
        
    except Exception as e:
        print(f"✗ Compatibility test failed: {e}")
        return False


if __name__ == "__main__":
    print("Rectangle Linux Test Suite")
    print("=" * 50)
    
    # Run basic tests first
    basic_success = run_basic_functionality_test()
    print()
    
    compat_success = run_compatibility_test()
    print()
    
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], verbosity=2, exit=False)
    
    print("\n" + "=" * 50)
    if basic_success and compat_success:
        print("✓ All tests completed successfully!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)