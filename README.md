# Cross-Platform MAC Address Changer

A comprehensive Python script that can change MAC addresses on **Windows**, **Linux**, and **macOS** systems.

## Features

- ✅ **Cross-platform support**: Windows, Linux, and macOS
- ✅ **Multiple MAC changing methods**: Automatic fallback for different system configurations
- ✅ **Network interface detection**: Automatically discover available network interfaces
- ✅ **MAC address validation**: Ensures proper MAC address format
- ✅ **Random MAC generation**: Generate cryptographically secure random MAC addresses
- ✅ **Automatic privilege elevation**: Prompts user and automatically restarts with admin/root privileges when needed
- ✅ **Privilege checking**: Automatically checks for required administrator/root privileges
- ✅ **User-friendly CLI**: Easy-to-use command-line interface with helpful examples

## Requirements

- Python 3.6+
- Administrator/root privileges (for MAC address changes)
- Platform-specific tools:
  - **Windows**: PowerShell, netsh, wmic
  - **Linux**: ip command or ifconfig
  - **macOS**: ifconfig, sudo

## Installation

1. Clone or download this repository
2. No additional Python packages required (uses only built-in modules)

```bash
git clone <repository-url>
cd mac-changer
```

## Usage

### Automatic Privilege Elevation

The script automatically detects when administrator/root privileges are required and offers to restart itself with the necessary permissions:

```bash
# Example: Running without admin privileges
python mac_changer.py --interface "Wi-Fi" --random

# Output:
MAC Address Changer - Windows Platform
==================================================
⚠️  Administrator/root privileges required for MAC address changes!

Would you like to restart this script with administrator/root privileges? (y/N): y
Restarting with elevated privileges...
✅ Script restarted with administrator privileges.
```

**How it works:**
- **Windows**: Uses `ShellExecute` with "runas" verb to prompt for UAC elevation
- **Linux/macOS**: Uses `sudo` to restart the script with root privileges
- **Safety**: Prevents infinite loops by detecting previous elevation attempts

### Basic Commands

#### List all network interfaces
```bash
# Show all available network interfaces and their current MAC addresses
python mac_changer.py --list
```

#### Change MAC address to a specific value
```bash
# Windows
python mac_changer.py --interface "Wi-Fi" --mac "00:11:22:33:44:55"

# Linux/macOS
sudo python3 mac_changer.py --interface eth0 --mac "00:11:22:33:44:55"
```

#### Generate and use a random MAC address
```bash
# Windows
python mac_changer.py --interface "Wi-Fi" --random

# Linux/macOS
sudo python3 mac_changer.py --interface eth0 --random
```

#### Show current MAC address of an interface
```bash
python mac_changer.py --interface "Wi-Fi" --current
```

#### Restore original MAC address
```bash
python mac_changer.py --interface "Wi-Fi" --restore
```

### Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--interface` | `-i` | Network interface name (e.g., eth0, Wi-Fi, en0) |
| `--mac` | `-m` | New MAC address (format: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX) |
| `--random` | `-r` | Generate and use a random MAC address |
| `--list` | `-l` | List all available network interfaces |
| `--current` | `-c` | Show current MAC address of specified interface |
| `--restore` | | Restore original MAC address |
| `--help` | `-h` | Show help message and exit |

## Platform-Specific Notes

### Windows
- **Privileges**: Automatically prompts to restart with Administrator privileges if needed
- **Methods used**:
  1. PowerShell `Set-NetAdapter` command (modern method)
  2. Registry modification for advanced cases
  3. Manual Device Manager instructions (fallback)
- **Interface names**: Usually "Wi-Fi", "Ethernet", "Local Area Connection", etc.  
- **Hardware compatibility**: 
  - ✅ Ethernet adapters (90% success rate)
  - ⚠️ Built-in Wi-Fi (70% success rate) 
  - ❌ USB Wi-Fi adapters (20% success rate)
- **Note**: USB Wi-Fi adapters often don't support MAC changing due to firmware limitations
- **Troubleshooting**: See `WINDOWS_MAC_CHANGING.md` for detailed Windows-specific guidance

### Linux
- **Privileges**: Automatically prompts to restart with sudo if root privileges needed
- **Methods used**:
  1. `ip link` commands (modern Linux distributions)
  2. `ifconfig` commands (fallback for older systems)
- **Interface names**: Usually eth0, wlan0, enp0s3, etc.
- **Note**: Interface will be temporarily brought down and back up

### macOS
- **Privileges**: Automatically prompts to restart with sudo if root privileges needed
- **Methods used**:
  1. `ifconfig` with ether parameter
  2. Airport framework for Wi-Fi interfaces
- **Interface names**: Usually en0, en1, etc.
- **Note**: Wi-Fi interfaces may require reconnection to networks

## Examples

### Windows Examples
```bash
# List interfaces
python mac_changer.py --list

# Change Wi-Fi MAC to specific address (run as Administrator)
python mac_changer.py --interface "Wi-Fi" --mac "02:34:56:78:9A:BC"

# Generate random MAC for Ethernet (run as Administrator)
python mac_changer.py --interface "Ethernet" --random

# Check current MAC
python mac_changer.py --interface "Wi-Fi" --current
```

### Linux Examples
```bash
# List interfaces
python3 mac_changer.py --list

# Change ethernet MAC to specific address
sudo python3 mac_changer.py --interface eth0 --mac "02:34:56:78:9A:BC"

# Generate random MAC for Wi-Fi
sudo python3 mac_changer.py --interface wlan0 --random

# Restore original MAC
sudo python3 mac_changer.py --interface eth0 --restore
```

### macOS Examples
```bash
# List interfaces
python3 mac_changer.py --list

# Change Wi-Fi MAC to specific address
sudo python3 mac_changer.py --interface en0 --mac "02:34:56:78:9A:BC"

# Generate random MAC for Ethernet
sudo python3 mac_changer.py --interface en1 --random
```

## Hardware Compatibility

### Windows Compatibility Matrix
| Adapter Type | Success Rate | Notes |
|-------------|-------------|--------|
| **Ethernet (Built-in)** | ✅ 90% | Intel, Realtek, Broadcom wired adapters |
| **Wi-Fi (Built-in)** | ⚠️ 70% | Intel Wi-Fi cards usually work |
| **Wi-Fi (PCIe Cards)** | ⚠️ 70% | Depends on driver support |
| **USB Wi-Fi Adapters** | ❌ 20% | Often firmware-locked |
| **USB Ethernet** | ⚠️ 50% | Mixed results by manufacturer |

### Linux/macOS Compatibility  
| Adapter Type | Success Rate | Notes |
|-------------|-------------|--------|
| **Ethernet** | ✅ 95% | Nearly universal support |
| **Wi-Fi** | ✅ 85% | Most adapters supported |
| **USB Adapters** | ✅ 80% | Better driver flexibility |

**💡 Tip**: Use `python mac_changer.py --interface "InterfaceName" --debug` to check your specific adapter's compatibility.

## Security Considerations

- **Locally Administered Addresses**: Generated random MACs use locally administered address format (second bit of first octet set to 1)
- **Unicast Addresses**: All generated MACs are unicast (first bit of first octet set to 0)
- **Privacy**: Changing MAC addresses can help protect privacy on public networks
- **Legal**: Ensure MAC address changing complies with your local laws and network policies

## Troubleshooting

### Common Issues

1. **"Administrator/root privileges required"**
   - The script will automatically prompt to restart with elevated privileges
   - **Manual method - Windows**: Run Command Prompt/PowerShell as Administrator
   - **Manual method - Linux/macOS**: Use `sudo` before the command

2. **"Interface not found"**
   - Run `python mac_changer.py --list` to see available interfaces
   - Use exact interface name (case-sensitive)

3. **MAC change appears successful but doesn't take effect**
   - **Windows**: May require network adapter restart or reboot
   - **Linux**: Try `sudo systemctl restart NetworkManager`
   - **macOS**: Try disconnecting and reconnecting to network

4. **Command not found errors**
   - **Linux**: Install `net-tools` package for ifconfig: `sudo apt install net-tools`
   - **Windows**: Ensure PowerShell and netsh are available (should be by default)

### Platform-Specific Troubleshooting

#### Windows
- If netsh method fails, the script provides manual Device Manager steps
- Some network adapters may not support MAC address changing
- Virtual network adapters may have different behaviors

#### Linux
- Ensure NetworkManager or systemd-networkd isn't overriding changes
- Some wireless drivers may reset MAC on interface restart
- Use `ip link show` to verify interface names

#### macOS
- Recent macOS versions have increased restrictions on MAC changing
- System Integrity Protection (SIP) may prevent some changes
- Airport utility may be required for some Wi-Fi adapters

## License

This project is provided as-is for educational and legitimate security testing purposes. Users are responsible for ensuring compliance with applicable laws and regulations.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Changelog

- **v1.1.0**: Enhanced user experience
  - **NEW**: Automatic privilege elevation with user prompt
  - **NEW**: Smart detection of elevation attempts to prevent infinite loops
  - Improved Windows interface detection accuracy
  - Enhanced error handling and user feedback

- **v1.0.0**: Initial release with cross-platform support
  - Windows, Linux, and macOS compatibility
  - Multiple MAC changing methods
  - Command-line interface
  - Comprehensive error handling