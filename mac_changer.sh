#!/bin/bash
# MAC Changer Linux/macOS Launcher
# This script runs the MAC changer with proper sudo privileges

echo "MAC Address Changer - Linux/macOS Launcher"
echo "=========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH"
    echo "Please install Python 3.6+ and try again"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if running as root for MAC changing operations
if [[ "$*" == *"--mac"* ]] || [[ "$*" == *"--random"* ]] || [[ "$*" == *"--restore"* ]]; then
    if [ "$EUID" -ne 0 ]; then
        echo "MAC address changes require root privileges."
        echo "Re-running with sudo..."
        echo
        exec sudo "$0" "$@"
    fi
fi

# If no arguments provided, show interface list
if [ $# -eq 0 ]; then
    echo "No arguments provided. Showing available interfaces..."
    echo
    python3 mac_changer.py --list
    echo
    echo "Usage examples:"
    echo "  $0 --interface eth0 --random"
    echo "  $0 --interface wlan0 --mac \"00:11:22:33:44:55\""
    echo "  $0 --help"
    exit 0
fi

# Run the script with provided arguments
python3 mac_changer.py "$@"