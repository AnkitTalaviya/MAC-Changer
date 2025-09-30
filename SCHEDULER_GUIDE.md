# MAC Changer - Automatic Scheduler Guide

## 🕐 Overview

The MAC Changer now includes an automatic scheduler that can change your MAC address at specific intervals or random times. This is useful for enhanced privacy and security.

## ⚡ Quick Start

### 1. Configure the Scheduler
```bash
python mac_changer.py --scheduler-config
```
This opens an interactive configuration where you can set:
- **Interface**: Which network adapter to change
- **Schedule Mode**: Fixed interval or random timing
- **Time Range**: When the scheduler should be active
- **Intervals**: How often to change MAC addresses

### 2. Start the Scheduler (Continuous Mode)
```bash
python mac_changer.py --scheduler-start
```
**Note**: Runs continuously until you press Ctrl+C. Shows live MAC monitoring!

### 3. Check Status (Optional)
```bash
python mac_changer.py --scheduler-status
```

### 4. Stop with Ctrl+C
Simply press `Ctrl+C` while the scheduler is running to stop it gracefully.

## 🔧 Configuration Options

### Scheduling Modes

#### Fixed Interval Mode
- Changes MAC address at regular intervals (e.g., every 30 minutes)
- Predictable timing for consistent privacy rotation
- Good for: Regular work schedules, consistent security needs

#### Random Time Mode
- Changes MAC address at random intervals within a range (e.g., 15-60 minutes)
- Unpredictable timing for enhanced privacy
- Good for: Maximum privacy, avoiding pattern detection

### Continuous Operation
- **Always Active**: Runs 24/7 until manually stopped with Ctrl+C
- **Immediate Start**: No time restrictions, begins changing MAC addresses right away
- **Live Monitoring**: Shows real-time current MAC address and countdown to next change

### MAC Address Sources
- **Random MAC**: Generates new random MAC addresses
- **Custom List**: Use predefined MAC addresses (future feature)

## 🚀 Command Reference

### Basic Commands
```bash
# Configure scheduler settings
python mac_changer.py --scheduler-config

# Start scheduler (requires admin privileges)
python mac_changer.py --scheduler-start

# Run in background daemon mode
python mac_changer.py --scheduler-start --daemon

# Stop running scheduler
python mac_changer.py --scheduler-stop

# Check scheduler status
python mac_changer.py --scheduler-status
```

### Example Scenarios

#### Privacy-Focused Setup (Random)
```
Interface: Wi-Fi
Mode: Random Time
Random Interval: 15-45 minutes
Schedule: 08:00 - 22:00
```

#### Regular Business Setup (Fixed)
```
Interface: Ethernet
Mode: Fixed Interval  
Interval: 60 minutes
Schedule: 09:00 - 17:00
```

#### 24/7 Maximum Privacy
```
Interface: Wi-Fi
Mode: Random Time
Random Interval: 10-30 minutes
Schedule: 00:00 - 23:59
```

## 📁 Files Created

The scheduler creates two files in your project directory:

- **`mac_scheduler_config.json`**: Configuration settings
- **`mac_scheduler.log`**: Change history and logs

## 🔒 Security Features

- **Admin Privilege Check**: Automatically requests elevation
- **Schedule Compliance**: Only changes MAC during configured hours
- **Logging**: All changes are logged with timestamps
- **Safe Shutdown**: Graceful stop with Ctrl+C

## ⚠️ Important Notes

### Privileges
- **Windows**: Requires Administrator privileges
- **Linux/macOS**: Requires root/sudo privileges
- The scheduler will automatically request privilege elevation

### Network Impact
- MAC changes may temporarily disconnect your network
- You may need to reconnect to Wi-Fi after changes
- Some networks track MAC addresses for access control

### Hardware Limitations
- Not all network adapters support MAC address changes
- USB Wi-Fi adapters have limited support (~20% success rate)
- Built-in adapters generally have better support

## 🐛 Troubleshooting

### Scheduler Won't Start
1. Ensure you have administrator/root privileges
2. Check that the interface name is correct
3. Verify the interface supports MAC changing

### MAC Changes Fail
1. Check the log file: `mac_scheduler.log`
2. Verify adapter supports MAC changing manually first
3. Some corporate networks block MAC changes

### Configuration Issues
```bash
# Reset to defaults
rm mac_scheduler_config.json
python mac_changer.py --scheduler-config
```

## 📊 Monitoring

### Real-time Status
```bash
# Watch logs in real-time (Linux/macOS)
tail -f mac_scheduler.log

# Check current status
python mac_changer.py --scheduler-status
```

### Log Analysis
The log file contains:
- Successful MAC changes with timestamps
- Failed attempts and error reasons
- Schedule start/stop events
- Configuration changes

## 🔮 Future Features

- [ ] Custom MAC address lists
- [ ] Multiple interface scheduling
- [ ] Web-based configuration interface
- [ ] System service installation
- [ ] Network-aware scheduling (pause when on trusted networks)

## 💡 Best Practices

1. **Test First**: Verify manual MAC changing works before using scheduler
2. **Conservative Timing**: Start with longer intervals (30+ minutes)
3. **Monitor Logs**: Check logs regularly for any issues
4. **Backup Config**: Save your working configuration
5. **Network Compatibility**: Test with your specific network setup

---

**Need Help?** Check the main README.md or create an issue on GitHub!