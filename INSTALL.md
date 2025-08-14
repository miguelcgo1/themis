# Installation Guide

This guide covers installation of Rectangle Linux on various distributions.

## Quick Installation

The easiest way to install Rectangle Linux is using the provided installation script:

```bash
chmod +x install.sh
./install.sh
```

This script will automatically detect your distribution and install all necessary dependencies.

## Manual Installation

### Prerequisites

Rectangle Linux requires Python 3.8+ and several system libraries.

#### Check Dependencies

Before installing, you can check if your system has the required dependencies:

```bash
python3 check_dependencies.py
```

### System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-gi \
    python3-gi-cairo \
    python3-xlib \
    gir1.2-gtk-3.0 \
    gir1.2-wnck-3.0 \
    gir1.2-appindicator3-0.1 \
    libwnck-3-0 \
    libappindicator3-1
```

#### Fedora/RHEL/CentOS
```bash
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-gobject \
    python3-cairo \
    python3-xlib \
    libwnck3 \
    libappindicator-gtk3
```

#### Arch Linux/Manjaro
```bash
sudo pacman -S --noconfirm \
    python \
    python-pip \
    python-gobject \
    python-cairo \
    python-xlib \
    libwnck3 \
    libappindicator-gtk3
```

#### openSUSE
```bash
sudo zypper install -y \
    python3 \
    python3-pip \
    python3-gobject \
    python3-cairo \
    python3-xlib \
    libwnck-3-0 \
    libappindicator3-1
```

### Python Dependencies

Install the required Python packages:

```bash
pip3 install --user pynput
```

Or system-wide (if available in your distribution):
```bash
# Ubuntu/Debian
sudo apt install python3-pynput

# Fedora
sudo dnf install python3-pynput

# Arch
sudo pacman -S python-pynput
```

### Installing Rectangle Linux

1. Clone or download Rectangle Linux:
```bash
git clone https://github.com/your-repo/rectangle-linux.git
cd rectangle-linux
```

2. Install using pip (recommended):
```bash
pip3 install --user .
```

3. Or install manually:
```bash
# Copy files to local directory
mkdir -p ~/.local/share/rectangle-linux
cp -r . ~/.local/share/rectangle-linux/

# Create executable script
mkdir -p ~/.local/bin
cat > ~/.local/bin/rectangle-linux << 'EOF'
#!/bin/bash
cd ~/.local/share/rectangle-linux
python3 rectangle_linux.py "$@"
EOF
chmod +x ~/.local/bin/rectangle-linux

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

4. Create desktop entry:
```bash
mkdir -p ~/.local/share/applications
cp data/rectangle-linux.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
```

## Running Rectangle Linux

After installation:

```bash
# Start Rectangle Linux
rectangle-linux

# Open configuration
rectangle-linux --config

# Enable debug mode
rectangle-linux --debug
```

Or find "Rectangle Linux" in your applications menu.

## Autostart

To start Rectangle Linux automatically when you log in:

1. Run `rectangle-linux --config`
2. Go to the "Behavior" tab
3. Check "Start Rectangle Linux on login"

Alternatively, you can manually create an autostart entry:
```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/rectangle-linux.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Rectangle Linux
Comment=Window management for Linux
Exec=rectangle-linux
Icon=preferences-system-windows
StartupNotify=false
NoDisplay=true
Hidden=false
X-GNOME-Autostart-enabled=true
EOF
```

## Package Installation

### Fedora (RPM)
```bash
# Build RPM package
cd fedora/
rpmbuild -ba rectangle-linux.spec

# Install
sudo dnf install rectangle-linux-*.rpm
```

### Ubuntu/Debian (DEB)
```bash
# Build DEB package
dpkg-buildpackage -us -uc

# Install
sudo dpkg -i ../rectangle-linux_*.deb
sudo apt-get install -f  # Fix any dependency issues
```

### Arch Linux (AUR)
```bash
# Using an AUR helper like yay
yay -S rectangle-linux

# Or manually
cd arch/
makepkg -si
```

## Troubleshooting

### Permission Issues
If you get permission errors:
```bash
# Add yourself to input group (for hotkey detection)
sudo usermod -a -G input $USER
# Log out and log back in
```

### Wayland Issues
On Wayland, some features may require additional setup:
```bash
# For Sway users
echo 'exec rectangle-linux &' >> ~/.config/sway/config

# For GNOME Wayland users
# Use GNOME Shell extensions or configure shortcuts in Settings
```

### X11 Issues
If windows aren't detected properly on X11:
```bash
# Install additional X11 tools
sudo apt install wmctrl xdotool  # Ubuntu/Debian
sudo dnf install wmctrl xdotool  # Fedora
```

### System Tray Issues
If the system tray icon doesn't appear:
```bash
# GNOME users may need an extension
# KDE users: check system tray settings
# XFCE users: add "Notification Area" to panel
```

## Uninstallation

To remove Rectangle Linux:

```bash
# If installed with pip
pip3 uninstall rectangle-linux

# If installed manually
rm -rf ~/.local/share/rectangle-linux
rm ~/.local/bin/rectangle-linux
rm ~/.local/share/applications/rectangle-linux.desktop
rm ~/.config/autostart/rectangle-linux.desktop
rm -rf ~/.config/rectangle-linux

# Remove from package manager
sudo apt remove rectangle-linux     # Ubuntu/Debian
sudo dnf remove rectangle-linux     # Fedora
sudo pacman -R rectangle-linux      # Arch
```

## Getting Help

- Check the dependency checker: `python3 check_dependencies.py`
- Enable debug mode: `rectangle-linux --debug`
- Check logs in `~/.config/rectangle-linux/`
- Report issues on GitHub