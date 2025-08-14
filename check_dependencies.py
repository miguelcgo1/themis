#!/usr/bin/env python3

import sys
import subprocess
import importlib.util


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version < (3, 8):
        print(f"✗ Python {version.major}.{version.minor} is too old. Minimum required: 3.8")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_module(module_name, package_name=None, install_hint=None):
    """Check if a Python module is available"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            print(f"✓ {module_name} is available")
            return True
        else:
            print(f"✗ {module_name} is not available")
            if install_hint:
                print(f"  Install with: {install_hint}")
            return False
    except Exception as e:
        print(f"✗ Error checking {module_name}: {e}")
        if install_hint:
            print(f"  Install with: {install_hint}")
        return False


def check_system_dependencies():
    """Check system-level dependencies"""
    print("\nChecking system dependencies...")
    
    system_deps = {
        'gtk': 'GTK 3.0 development files',
        'cairo': 'Cairo development files',
        'gobject-introspection': 'GObject Introspection',
    }
    
    # This is a basic check - on actual Linux systems, you'd check for pkg-config
    try:
        result = subprocess.run(['pkg-config', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ pkg-config is available")
            
            # Check for GTK
            result = subprocess.run(['pkg-config', '--exists', 'gtk+-3.0'], 
                                  capture_output=True)
            if result.returncode == 0:
                print("✓ GTK 3.0 development files found")
            else:
                print("✗ GTK 3.0 development files not found")
                
        else:
            print("⚠ pkg-config not available (this is expected on non-Linux systems)")
    except FileNotFoundError:
        print("⚠ pkg-config not found (this is expected on non-Linux systems)")


def main():
    print("Rectangle Linux Dependency Checker")
    print("=" * 50)
    
    all_good = True
    
    # Check Python version
    if not check_python_version():
        all_good = False
    
    print("\nChecking Python modules...")
    
    # Core modules that should be available
    core_modules = [
        ('os', None, None),
        ('sys', None, None),
        ('json', None, None),
        ('configparser', None, None),
        ('pathlib', None, None),
        ('threading', None, None),
        ('time', None, None),
        ('typing', None, None),
    ]
    
    for module, package, hint in core_modules:
        if not check_module(module, package, hint):
            all_good = False
    
    # Optional but recommended modules
    print("\nChecking GUI modules (required for full functionality)...")
    gui_modules = [
        ('gi', 'PyGObject', 'pip install PyGObject or use system package manager'),
        ('cairo', 'pycairo', 'pip install pycairo or use system package manager'),
    ]
    
    gui_available = True
    for module, package, hint in gui_modules:
        if not check_module(module, package, hint):
            gui_available = False
            all_good = False
    
    # Check GI modules if gi is available
    if gui_available:
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            gi.require_version('Gdk', '3.0')
            
            from gi.repository import Gtk, Gdk, GLib
            print("✓ GTK 3.0 bindings are working")
            
            # Try to check for Wnck
            try:
                gi.require_version('Wnck', '3.0')
                from gi.repository import Wnck
                print("✓ Wnck (window management) bindings available")
            except:
                print("⚠ Wnck bindings not available (may affect X11 functionality)")
                
            # Try to check for AppIndicator
            try:
                gi.require_version('AppIndicator3', '0.1')
                from gi.repository import AppIndicator3
                print("✓ AppIndicator3 (system tray) bindings available")
            except:
                print("⚠ AppIndicator3 bindings not available (may affect system tray)")
                
        except Exception as e:
            print(f"✗ GTK bindings not working: {e}")
            all_good = False
    
    # Check additional dependencies
    print("\nChecking additional dependencies...")
    additional_modules = [
        ('pynput', 'pynput', 'pip install pynput'),
    ]
    
    for module, package, hint in additional_modules:
        if not check_module(module, package, hint):
            print(f"  Note: {module} is required for hotkey functionality")
    
    # Optional X11 support
    try:
        import Xlib
        print("✓ python-xlib is available (X11 support)")
    except ImportError:
        print("⚠ python-xlib not available (X11 support disabled)")
        print("  Install with: pip install python-xlib")
    
    # Check system dependencies
    check_system_dependencies()
    
    print("\n" + "=" * 50)
    if all_good:
        print("✓ All core dependencies are satisfied!")
        print("Rectangle Linux should work correctly on this system.")
    else:
        print("✗ Some dependencies are missing.")
        print("Please install the missing dependencies before running Rectangle Linux.")
        
        print("\nQuick installation guide:")
        print("1. Install system dependencies:")
        print("   Ubuntu/Debian: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0")
        print("   Fedora: sudo dnf install python3-gobject python3-cairo gtk3")
        print("   Arch: sudo pacman -S python-gobject python-cairo gtk3")
        print("")
        print("2. Install Python dependencies:")
        print("   pip install pynput python-xlib")
        print("")
        print("3. Or use the provided install.sh script:")
        print("   ./install.sh")
    
    return all_good


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)