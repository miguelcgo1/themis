# Themis

Themis is a window management application for Linux, inspired by and based on Rectangle for macOS. This is a specialized Linux version of Rectangle that works across all distributions including Fedora, providing powerful window management functionality.

**Attribution**: This code is a copy of Rectangle made specifically for Linux.

## Features

- Window snapping with keyboard shortcuts
- Drag-to-snap functionality
- Support for X11 and Wayland
- Cross-distribution compatibility
- Customizable keyboard shortcuts
- Quarter, half, and third window positioning

## Requirements

- Python 3.8+
- GTK 3.0+
- PyGObject
- python3-xlib (for X11 support)

## Installation

### From Source
```bash
git clone <repository>
cd themis
pip install -r requirements.txt
python themis.py
```

### Distribution Packages
Coming soon for major distributions.

## Usage

Run the application:
```bash
python themis.py
```

Default keyboard shortcuts:
- `Super+Left`: Snap to left half
- `Super+Right`: Snap to right half
- `Super+Up`: Maximize
- `Super+Down`: Center window
- `Super+1`: First quarter
- `Super+2`: Second quarter
- `Super+3`: Third quarter
- `Super+4`: Fourth quarter

## Configuration

The configuration GUI can be accessed through the system tray icon or by running with `--config` flag.