#!/bin/bash

# Themis Installation Script
# Supports major Linux distributions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VERSION=$(lsb_release -sr)
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
        VERSION=$DISTRIB_RELEASE
    else
        OS=$(uname -s)
        VERSION=$(uname -r)
    fi
    
    print_info "Detected OS: $OS $VERSION"
}

# Install dependencies based on distribution
install_dependencies() {
    print_info "Installing dependencies..."
    
    case "$OS" in
        *"Ubuntu"*|*"Debian"*)
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
            ;;
        *"Fedora"*|*"Red Hat"*|*"CentOS"*)
            sudo dnf install -y \
                python3 \
                python3-pip \
                python3-gobject \
                python3-cairo \
                python3-xlib \
                libwnck3 \
                libappindicator-gtk3
            ;;
        *"Arch"*|*"Manjaro"*)
            sudo pacman -S --noconfirm \
                python \
                python-pip \
                python-gobject \
                python-cairo \
                python-xlib \
                libwnck3 \
                libappindicator-gtk3
            ;;
        *"openSUSE"*)
            sudo zypper install -y \
                python3 \
                python3-pip \
                python3-gobject \
                python3-cairo \
                python3-xlib \
                libwnck-3-0 \
                libappindicator3-1
            ;;
        *)
            print_warning "Unsupported distribution. Please install dependencies manually:"
            echo "  - Python 3.8+"
            echo "  - PyGObject"
            echo "  - python3-cairo"
            echo "  - python3-xlib"
            echo "  - libwnck3"
            echo "  - libappindicator3"
            echo ""
            read -p "Continue with installation? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
            ;;
    esac
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    # Try to use system package manager first
    case "$OS" in
        *"Ubuntu"*|*"Debian"*)
            sudo apt install -y python3-pynput || pip3 install --user pynput
            ;;
        *"Fedora"*|*"Red Hat"*|*"CentOS"*)
            sudo dnf install -y python3-pynput || pip3 install --user pynput
            ;;
        *"Arch"*|*"Manjaro"*)
            sudo pacman -S --noconfirm python-pynput || pip3 install --user pynput
            ;;
        *)
            pip3 install --user pynput
            ;;
    esac
}

# Install Themis
install_themis() {
    print_info "Installing Themis..."
    
    # Create installation directory
    INSTALL_DIR="$HOME/.local/share/themis"
    mkdir -p "$INSTALL_DIR"
    
    # Copy files
    cp -r . "$INSTALL_DIR/"
    
    # Create executable script
    EXEC_SCRIPT="$HOME/.local/bin/themis"
    mkdir -p "$HOME/.local/bin"
    
    cat > "$EXEC_SCRIPT" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 themis.py "\$@"
EOF
    
    chmod +x "$EXEC_SCRIPT"
    
    # Create desktop entry
    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"
    
    cat > "$DESKTOP_DIR/themis.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Themis
GenericName=Window Manager
Comment=Themis - Window management for Linux, based on Rectangle for macOS
Exec=$EXEC_SCRIPT
Icon=preferences-system-windows
Terminal=false
StartupNotify=false
Categories=Utility;System;
Keywords=window;manager;snap;tile;themis;rectangle;
MimeType=
EOF
    
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
}

# Add to PATH
setup_path() {
    SHELL_RC=""
    if [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    else
        SHELL_RC="$HOME/.profile"
    fi
    
    if [ -f "$SHELL_RC" ]; then
        if ! grep -q '$HOME/.local/bin' "$SHELL_RC"; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
            print_info "Added ~/.local/bin to PATH in $SHELL_RC"
        fi
    fi
}

# Main installation
main() {
    print_info "Themis Installation Script"
    echo "===================================="
    echo
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root"
        exit 1
    fi
    
    # Check Python version
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        print_error "Python 3.8+ is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    detect_distro
    install_dependencies
    install_python_deps
    install_themis
    setup_path
    
    print_success "Themis has been installed successfully!"
    echo
    print_info "To run Themis:"
    echo "  1. Open a new terminal (to refresh PATH)"
    echo "  2. Run: themis"
    echo "  3. Or find 'Themis' in your applications menu"
    echo
    print_info "To configure Themis:"
    echo "  themis --config"
    echo
    print_info "To start Themis automatically on login:"
    echo "  1. Run themis --config"
    echo "  2. Go to Behavior tab"
    echo "  3. Check 'Start Themis on login'"
}

# Run main function
main "$@"