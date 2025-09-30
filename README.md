# Cross-Platform MAC Address Changer

A simple, lightweight tool to change MAC addresses on Windows, Linux, and macOS systems with automatic privilege elevation.

## 🚀 Quick Start

```bash
# List all network interfaces
python mac_changer.py --list

# Change to a specific MAC address
python mac_changer.py --interface "Wi-Fi" --mac 02:11:22:33:44:55

# Generate and apply a random MAC address
python mac_changer.py --interface "Wi-Fi" --random

# Check current MAC address
python mac_changer.py --interface "Wi-Fi" --current
```

## ⚡ Features

- ✅ **Cross-Platform**: Windows, Linux, macOS
- ✅ **Auto-Privilege Elevation**: Automatically requests admin/sudo
- ✅ **Random MAC Generation**: Generates valid locally administered MACs
- ✅ **Interface Detection**: Lists available network interfaces
- ✅ **MAC Validation**: Ensures proper MAC address format
- ✅ **Clean & Simple**: Lightweight with no external dependencies

---

## 🪟 Windows Usage

### Requirements
- **Windows 10/11** (PowerShell required)
- **Administrator privileges** (automatically requested)

### Find Your Interface
```powershell
python mac_changer.py --list
```
**Output:**
```
📡 Network Interfaces (Windows):
==================================================
🔌 Ethernet
   MAC: E0:D5:5E:93:69:AB

🔌 Wi-Fi
   MAC: 00:E0:4C:B8:38:2F
```

### Change MAC Address
```powershell
# Use specific MAC
python mac_changer.py --interface "Wi-Fi" --mac 02:AA:BB:CC:DD:EE

# Use random MAC
python mac_changer.py --interface "Wi-Fi" --random
```

### Launcher Script (Optional)
Double-click `mac_changer_admin.bat` to run with automatic admin privileges.

### Windows Notes
- Works with built-in network adapters
- Some USB Wi-Fi adapters may not support MAC changing
- Requires PowerShell (included in Windows 10/11)
- Network connection may briefly disconnect during change

---

## 🐧 Linux Usage

### Requirements
- **Linux distribution** with `ip` command (iproute2 package)
- **Root privileges** (sudo access)

### Install Dependencies
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install iproute2

# CentOS/RHEL/Fedora
sudo yum install iproute2    # or dnf install iproute2
```

### Find Your Interface
```bash
python3 mac_changer.py --list
```
**Output:**
```
📡 Network Interfaces (Linux):
==================================================
🔌 eth0
   MAC: 08:00:27:12:34:56

🔌 wlan0
   MAC: 02:42:AC:11:00:02
```

### Change MAC Address
```bash
# Use specific MAC
sudo python3 mac_changer.py --interface eth0 --mac 02:AA:BB:CC:DD:EE

# Use random MAC
sudo python3 mac_changer.py --interface wlan0 --random

# Script will auto-request sudo if needed
python3 mac_changer.py --interface eth0 --random
```

### Launcher Script (Optional)
```bash
chmod +x mac_changer.sh
./mac_changer.sh
```

### Linux Notes
- Works with most Ethernet and Wi-Fi adapters
- May require network manager restart: `sudo systemctl restart NetworkManager`
- Some virtual interfaces (Docker, VPN) may not support MAC changing
- Changes are temporary (reset on reboot)

---

## 🍎 macOS Usage

### Requirements
- **macOS 10.12+**
- **Administrator privileges** (sudo access)

### Find Your Interface
```bash
python3 mac_changer.py --list
```
**Output:**
```
📡 Network Interfaces (Darwin):
==================================================
🔌 en0
   MAC: A4:83:E7:12:34:56

🔌 en1
   MAC: 02:42:AC:11:00:02
```

### Change MAC Address
```bash
# Use specific MAC
sudo python3 mac_changer.py --interface en0 --mac 02:AA:BB:CC:DD:EE

# Use random MAC
sudo python3 mac_changer.py --interface en0 --random

# Script will auto-request sudo if needed
python3 mac_changer.py --interface en0 --random
```

### macOS Notes
- `en0` is typically the main Ethernet/Wi-Fi interface
- May require disconnecting from Wi-Fi networks
- System Integrity Protection (SIP) may restrict some adapters
- Changes are temporary (reset on reboot or network restart)

---

## 📋 Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `--list` or `-l` | List all network interfaces | `python mac_changer.py -l` |
| `--interface` or `-i` | Specify network interface | `python mac_changer.py -i eth0` |
| `--mac` or `-m` | Set specific MAC address | `python mac_changer.py -i eth0 -m 02:11:22:33:44:55` |
| `--random` or `-r` | Generate random MAC | `python mac_changer.py -i eth0 -r` |
| `--current` or `-c` | Show current MAC | `python mac_changer.py -i eth0 -c` |
| `--help` or `-h` | Show help message | `python mac_changer.py -h` |

## 🔧 Installation

### Method 1: Download
1. Download `mac_changer.py`
2. Run with Python 3.6+

### Method 2: Clone Repository
```bash
git clone https://github.com/AnkitTalaviya/MAC-Changer.git
cd MAC-Changer
python mac_changer.py --help
```

### Requirements
- **Python 3.6+** (no additional packages needed)
- **Admin/root privileges** (automatically requested)

## ⚠️ Important Notes

### Legal & Ethical Use
- **Use responsibly** and in compliance with local laws
- **Network policies** may prohibit MAC address changes
- **Educational purposes** - understand your network's terms of service

### Limitations
- **Temporary changes** - MAC resets on reboot/network restart  
- **Hardware dependent** - not all adapters support MAC changing
- **USB adapters** - limited support (especially on Windows)
- **Corporate networks** - may detect and block MAC changes

### Troubleshooting

#### "Administrator privileges required"
- **Windows**: Run as Administrator or use `mac_changer_admin.bat`
- **Linux/macOS**: Use `sudo` or let script auto-elevate

#### "Interface not found"  
- Run `--list` to see available interfaces
- Check interface name spelling and case sensitivity

#### "MAC change failed"
- Adapter may not support MAC changing
- Try with a different network adapter
- On Linux: restart NetworkManager

#### "Permission denied"
- Ensure you have admin/root privileges
- Some corporate systems restrict MAC changes

## 📝 Examples

### Windows Examples
```powershell
# List interfaces
python mac_changer.py --list

# Change Wi-Fi MAC to random
python mac_changer.py --interface "Wi-Fi" --random

# Change Ethernet MAC to specific
python mac_changer.py --interface "Ethernet" --mac 02:11:22:33:44:55
```

### Linux Examples  
```bash
# List interfaces
python3 mac_changer.py --list

# Change eth0 MAC to random
sudo python3 mac_changer.py --interface eth0 --random

# Change wlan0 MAC to specific
sudo python3 mac_changer.py --interface wlan0 --mac 02:11:22:33:44:55
```

### macOS Examples
```bash
# List interfaces  
python3 mac_changer.py --list

# Change en0 MAC to random
sudo python3 mac_changer.py --interface en0 --random

# Change en1 MAC to specific  
sudo python3 mac_changer.py --interface en1 --mac 02:11:22:33:44:55
```

## 🤝 Contributing

Issues and pull requests welcome! Please ensure cross-platform compatibility.

## 📜 License

MIT License - Use freely with attribution.

---

**⚡ Simple, Clean, Cross-Platform MAC Address Changer ⚡**