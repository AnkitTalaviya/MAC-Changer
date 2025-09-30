#!/usr/bin/env python3
"""
Cross-Platform MAC Address Changer
Supports Windows, Linux, and macOS with automatic privilege elevation
"""

import subprocess
import platform
import re
import random
import argparse
import sys
import os
import time
import threading
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Union


class MACChanger:
    """Cross-platform MAC address changer with intelligent adapter detection"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_admin = self._check_admin_privileges()
        
    def _check_admin_privileges(self) -> bool:
        """Check if running with administrative privileges"""
        try:
            if self.system == "windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except Exception:
            return False
    
    def validate_mac_address(self, mac: str) -> bool:
        """Validate MAC address format (XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX)"""
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(mac_pattern.match(mac))
    
    def generate_random_mac(self) -> str:
        """Generate random locally administered MAC address"""
        # First byte: locally administered (bit 1 = 1) and unicast (bit 0 = 0)
        first_byte = random.choice(['02', '06', '0A', '0E'])
        mac_parts = [first_byte] + [f"{random.randint(0, 255):02x}" for _ in range(5)]
        return ':'.join(mac_parts)
    
    def _normalize_mac(self, mac: str, separator: str = ':') -> str:
        """Normalize MAC address format"""
        clean_mac = re.sub(r'[:-]', '', mac.upper())
        return separator.join([clean_mac[i:i+2] for i in range(0, 12, 2)])
    
    def get_network_interfaces(self) -> Dict[str, str]:
        """Get available network interfaces with current MAC addresses"""
        try:
            if self.system == "windows":
                return self._get_windows_interfaces()
            elif self.system == "linux":
                return self._get_linux_interfaces()
            elif self.system == "darwin":
                return self._get_macos_interfaces()
        except Exception as e:
            print(f"Error getting interfaces: {e}")
        return {}
    
    def _get_windows_interfaces(self) -> Dict[str, str]:
        """Get Windows network interfaces using PowerShell"""
        interfaces = {}
        try:
            # Primary method: PowerShell Get-NetAdapter
            ps_cmd = 'Get-NetAdapter | Where-Object {$_.MacAddress} | ForEach-Object { "$($_.Name)|$($_.MacAddress)" }'
            result = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if '|' in line and line.strip():
                        name, mac = line.strip().split('|', 1)
                        if mac and len(mac.replace('-', '')) == 12:
                            formatted_mac = self._normalize_mac(mac, ':')
                            interfaces[name] = formatted_mac
            
            # Fallback: ipconfig if PowerShell fails
            if not interfaces:
                result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
                if result.returncode == 0:
                    current_adapter = None
                    for line in result.stdout.split('\n'):
                        line = line.strip()
                        if 'adapter' in line.lower() and ':' in line:
                            current_adapter = line.split(':')[0].replace('adapter', '').strip()
                        elif 'Physical Address' in line and current_adapter:
                            mac_match = re.search(r'([0-9A-Fa-f-]{17})', line)
                            if mac_match:
                                interfaces[current_adapter] = self._normalize_mac(mac_match.group(1), ':')
                                current_adapter = None
        except Exception as e:
            print(f"Error getting Windows interfaces: {e}")
        
        return interfaces
    
    def _get_linux_interfaces(self) -> Dict[str, str]:
        """Get Linux network interfaces using ip or ifconfig"""
        interfaces = {}
        try:
            # Modern method: ip command
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            if result.returncode == 0:
                current_interface = None
                for line in result.stdout.split('\n'):
                    if ': ' in line and not line.startswith(' '):
                        current_interface = line.split(':')[1].strip()
                    elif 'link/ether' in line and current_interface:
                        mac_match = re.search(r'link/ether\s+([a-fA-F0-9:]{17})', line)
                        if mac_match:
                            interfaces[current_interface] = mac_match.group(1).upper()
                            current_interface = None
            
            # Fallback: ifconfig
            if not interfaces:
                result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                if result.returncode == 0:
                    current_interface = None
                    for line in result.stdout.split('\n'):
                        if line and not line.startswith((' ', '\t')):
                            current_interface = line.split(':')[0]
                        elif current_interface and ('ether' in line or 'HWaddr' in line):
                            mac_match = re.search(r'([a-fA-F0-9:]{17})', line)
                            if mac_match:
                                interfaces[current_interface] = mac_match.group(1).upper()
        except Exception as e:
            print(f"Error getting Linux interfaces: {e}")
        
        return interfaces
    
    def _get_macos_interfaces(self) -> Dict[str, str]:
        """Get macOS network interfaces using ifconfig"""
        interfaces = {}
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            if result.returncode == 0:
                current_interface = None
                for line in result.stdout.split('\n'):
                    if line and not line.startswith((' ', '\t')) and ':' in line:
                        current_interface = line.split(':')[0]
                    elif current_interface and 'ether' in line:
                        mac_match = re.search(r'ether\s+([a-fA-F0-9:]{17})', line)
                        if mac_match:
                            interfaces[current_interface] = mac_match.group(1).upper()
        except Exception as e:
            print(f"Error getting macOS interfaces: {e}")
        
        return interfaces
    
    def change_mac_address(self, interface: str, new_mac: str) -> bool:
        """Change MAC address for specified interface"""
        if not self.validate_mac_address(new_mac):
            print(f"❌ Invalid MAC address format: {new_mac}")
            return False
            
        if not self.is_admin:
            print("❌ Administrator/root privileges required!")
            return False
            
        print(f"🔧 Changing MAC address of '{interface}' to '{new_mac}'...")
        
        try:
            if self.system == "windows":
                return self._change_mac_windows(interface, new_mac)
            elif self.system == "linux":
                return self._change_mac_linux(interface, new_mac)
            elif self.system == "darwin":
                return self._change_mac_macos(interface, new_mac)
            else:
                print(f"❌ Unsupported OS: {self.system}")
                return False
        except Exception as e:
            print(f"❌ MAC change error: {e}")
            return False
    
    def _change_mac_windows(self, interface: str, new_mac: str) -> bool:
        """Change MAC address on Windows using PowerShell"""
        try:
            clean_mac = self._normalize_mac(new_mac, '').upper()
            dash_mac = self._normalize_mac(new_mac, '-').upper()
            
            # Method 1: PowerShell Set-NetAdapter
            print("  Trying PowerShell method...")
            try:
                # Find exact adapter name
                ps_find = f'(Get-NetAdapter | Where-Object {{$_.Name -eq "{interface}"}}).Name'
                result = subprocess.run(['powershell', '-Command', ps_find], 
                                      capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0 and result.stdout.strip():
                    adapter_name = result.stdout.strip()
                    
                    # Disable, change MAC, re-enable
                    commands = [
                        f'Disable-NetAdapter -Name "{adapter_name}" -Confirm:$false',
                        f'Set-NetAdapter -Name "{adapter_name}" -MacAddress "{dash_mac}"',
                        f'Enable-NetAdapter -Name "{adapter_name}" -Confirm:$false'
                    ]
                    
                    for i, cmd in enumerate(commands):
                        result = subprocess.run(['powershell', '-Command', cmd], 
                                              capture_output=True, text=True, timeout=15)
                        if result.returncode != 0 and i == 1:  # MAC set failed
                            # Still re-enable the adapter
                            subprocess.run(['powershell', '-Command', commands[2]], 
                                         capture_output=True, text=True, timeout=15)
                            raise subprocess.CalledProcessError(result.returncode, cmd)
                        time.sleep(2 if i < 2 else 3)
                    
                    print("  ✅ PowerShell method completed")
                    return True
                    
            except subprocess.CalledProcessError:
                print("  ❌ PowerShell method failed")
            
            # Method 2: Manual instructions for unsupported adapters
            print(f"\n📋 Manual MAC Change Required:")
            print(f"  1. Open Device Manager (Win + X → Device Manager)")
            print(f"  2. Network adapters → Find your {interface} adapter")
            print(f"  3. Right-click → Properties → Advanced tab")
            print(f"  4. Look for 'Network Address' or 'MAC Address'")
            print(f"  5. Set value to: {clean_mac}")
            print(f"  6. Click OK and restart adapter")
            print(f"\n  ⚠️  If no 'Network Address' property exists,")
            print(f"      your adapter doesn't support MAC changing")
            
            return False
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def _change_mac_linux(self, interface: str, new_mac: str) -> bool:
        """Change MAC address on Linux using ip or ifconfig"""
        commands_sets = [
            # Modern Linux: ip command
            [
                ['ip', 'link', 'set', 'dev', interface, 'down'],
                ['ip', 'link', 'set', 'dev', interface, 'address', new_mac],
                ['ip', 'link', 'set', 'dev', interface, 'up']
            ],
            # Legacy Linux: ifconfig
            [
                ['ifconfig', interface, 'down'],
                ['ifconfig', interface, 'hw', 'ether', new_mac],
                ['ifconfig', interface, 'up']
            ]
        ]
        
        for method, commands in enumerate(commands_sets, 1):
            try:
                print(f"  Trying method {method}...")
                for cmd in commands:
                    subprocess.run(cmd, check=True, capture_output=True)
                    time.sleep(1)
                
                print(f"  ✅ Method {method} successful")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Method {method} failed: {e}")
                continue
        
        return False
    
    def _change_mac_macos(self, interface: str, new_mac: str) -> bool:
        """Change MAC address on macOS using ifconfig"""
        try:
            print(f"  Changing MAC on macOS interface {interface}...")
            
            # For Wi-Fi interfaces, disconnect first
            if 'en' in interface:
                try:
                    subprocess.run(['sudo', '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-z'], 
                                 check=True, capture_output=True)
                    time.sleep(2)
                except subprocess.CalledProcessError:
                    pass
            
            # Change MAC address
            commands = [
                ['sudo', 'ifconfig', interface, 'down'],
                ['sudo', 'ifconfig', interface, 'ether', new_mac],
                ['sudo', 'ifconfig', interface, 'up']
            ]
            
            for cmd in commands:
                subprocess.run(cmd, check=True, capture_output=True)
                time.sleep(1)
            
            print(f"  ✅ macOS MAC change successful")
            if 'en' in interface:
                print(f"  ℹ️  You may need to reconnect to Wi-Fi")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ macOS MAC change failed: {e}")
            print(f"  ℹ️  Some macOS versions restrict MAC changing")
            return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def get_current_mac(self, interface: str) -> Optional[str]:
        """Get current MAC address of specified interface"""
        interfaces = self.get_network_interfaces()
        return interfaces.get(interface)
    
    def list_interfaces(self):
        """Display all available network interfaces"""
        print(f"\n📡 Network Interfaces ({self.system.title()}):")
        print("=" * 50)
        
        interfaces = self.get_network_interfaces()
        if not interfaces:
            print("❌ No network interfaces found")
            return
        
        for interface, mac in interfaces.items():
            print(f"🔌 {interface}")
            print(f"   MAC: {mac}")
            print()
    
    def restore_original_mac(self, interface: str) -> bool:
        """Restore original MAC address by restarting interface"""
        print("🔄 Restoring original MAC address...")
        
        if self.system == "linux":
            try:
                subprocess.run(['ip', 'link', 'set', 'dev', interface, 'down'], check=True, capture_output=True)
                time.sleep(1)
                subprocess.run(['ip', 'link', 'set', 'dev', interface, 'up'], check=True, capture_output=True)
                print("✅ Interface restarted - original MAC restored")
                return True
            except subprocess.CalledProcessError:
                pass
        
        print("ℹ️  Restart your network adapter or reboot to restore original MAC")
        return False


class MACScheduler:
    """Automatic MAC address scheduler with configurable intervals"""
    
    def __init__(self, mac_changer: MACChanger):
        self.mac_changer = mac_changer
        self.is_running = False
        self.scheduler_thread = None
        self.config_file = "mac_scheduler_config.json"
        self.log_file = "mac_scheduler.log"
        self.setup_logging()
        self.config = self.load_config()
    
    def setup_logging(self):
        """Setup logging for scheduled MAC changes"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> dict:
        """Load scheduler configuration from file"""
        default_config = {
            "interface": "Wi-Fi",
            "mode": "random_time",  # "fixed_interval" or "random_time"
            "fixed_interval_minutes": 30,
            "random_min_minutes": 15,
            "random_max_minutes": 60,
            "use_random_mac": True,
            "custom_mac_list": [],
            "enabled": False,
            "start_time": "00:00",
            "end_time": "23:59"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def is_within_schedule(self) -> bool:
        """Check if current time is within scheduled hours"""
        now = datetime.now().time()
        start_time = datetime.strptime(self.config["start_time"], "%H:%M").time()
        end_time = datetime.strptime(self.config["end_time"], "%H:%M").time()
        
        if start_time <= end_time:
            return start_time <= now <= end_time
        else:  # Overnight schedule (e.g., 22:00 to 06:00)
            return now >= start_time or now <= end_time
    
    def get_next_mac(self) -> str:
        """Get next MAC address to use"""
        if self.config["use_random_mac"]:
            return self.mac_changer.generate_random_mac()
        elif self.config["custom_mac_list"]:
            return random.choice(self.config["custom_mac_list"])
        else:
            return self.mac_changer.generate_random_mac()
    
    def calculate_next_interval(self) -> int:
        """Calculate seconds until next MAC change"""
        if self.config["mode"] == "fixed_interval":
            return self.config["fixed_interval_minutes"] * 60
        else:  # random_time
            min_seconds = self.config["random_min_minutes"] * 60
            max_seconds = self.config["random_max_minutes"] * 60
            return random.randint(min_seconds, max_seconds)
    
    def change_mac_scheduled(self):
        """Perform scheduled MAC address change"""
        if not self.is_within_schedule():
            self.logger.info("Outside scheduled hours, skipping MAC change")
            return
        
        interface = self.config["interface"]
        new_mac = self.get_next_mac()
        
        self.logger.info(f"Attempting scheduled MAC change for {interface} to {new_mac}")
        
        current_mac = self.mac_changer.get_current_mac(interface)
        success = self.mac_changer.change_mac_address(interface, new_mac)
        
        if success:
            self.logger.info(f"✅ MAC changed successfully: {current_mac} → {new_mac}")
        else:
            self.logger.warning(f"❌ MAC change failed for interface {interface}")
    
    def scheduler_loop(self):
        """Main scheduler loop"""
        self.logger.info("MAC scheduler started")
        
        while self.is_running:
            try:
                # Perform MAC change
                self.change_mac_scheduled()
                
                # Calculate next interval
                next_interval = self.calculate_next_interval()
                next_change = datetime.now() + timedelta(seconds=next_interval)
                
                self.logger.info(f"Next MAC change scheduled for: {next_change.strftime('%H:%M:%S')} ({next_interval//60} minutes)")
                
                # Wait for next interval (check every 30 seconds for stop signal)
                elapsed = 0
                while elapsed < next_interval and self.is_running:
                    time.sleep(min(30, next_interval - elapsed))
                    elapsed += 30
                    
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
        
        self.logger.info("MAC scheduler stopped")
    
    def start(self) -> bool:
        """Start the MAC scheduler"""
        if self.is_running:
            print("❌ Scheduler is already running")
            return False
        
        if not self.config["enabled"]:
            print("❌ Scheduler is disabled in configuration")
            return False
        
        if not self.mac_changer.is_admin:
            print("❌ Administrator/root privileges required for scheduler")
            return False
        
        # Validate interface exists
        interfaces = self.mac_changer.get_network_interfaces()
        if self.config["interface"] not in interfaces:
            print(f"❌ Interface '{self.config['interface']}' not found")
            print(f"Available interfaces: {list(interfaces.keys())}")
            return False
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self.scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        print(f"✅ MAC scheduler started for interface '{self.config['interface']}'")
        print(f"Mode: {self.config['mode']}")
        print(f"Schedule: {self.config['start_time']} - {self.config['end_time']}")
        return True
    
    def stop(self) -> bool:
        """Stop the MAC scheduler"""
        if not self.is_running:
            print("❌ Scheduler is not running")
            return False
        
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        print("✅ MAC scheduler stopped")
        return True
    
    def status(self):
        """Display scheduler status"""
        print(f"\n📊 MAC Scheduler Status")
        print("=" * 30)
        print(f"Running: {'Yes' if self.is_running else 'No'}")
        print(f"Enabled: {'Yes' if self.config['enabled'] else 'No'}")
        print(f"Interface: {self.config['interface']}")
        print(f"Mode: {self.config['mode']}")
        
        if self.config['mode'] == 'fixed_interval':
            print(f"Interval: {self.config['fixed_interval_minutes']} minutes")
        else:
            print(f"Random interval: {self.config['random_min_minutes']}-{self.config['random_max_minutes']} minutes")
        
        print(f"Schedule: {self.config['start_time']} - {self.config['end_time']}")
        print(f"MAC source: {'Random' if self.config['use_random_mac'] else 'Custom list'}")
        
        if not self.config['use_random_mac'] and self.config['custom_mac_list']:
            print(f"Custom MACs: {len(self.config['custom_mac_list'])} addresses")
        
        print(f"Config file: {self.config_file}")
        print(f"Log file: {self.log_file}")
    
    def configure_interactive(self):
        """Interactive configuration setup"""
        print("\n🔧 MAC Scheduler Configuration")
        print("=" * 35)
        
        # Show available interfaces
        interfaces = self.mac_changer.get_network_interfaces()
        print("\nAvailable interfaces:")
        for i, interface in enumerate(interfaces.keys(), 1):
            current = " (current)" if interface == self.config['interface'] else ""
            print(f"  {i}. {interface}{current}")
        
        # Interface selection
        while True:
            try:
                choice = input(f"\nSelect interface [1-{len(interfaces)}] or press Enter to keep current: ").strip()
                if not choice:
                    break
                idx = int(choice) - 1
                if 0 <= idx < len(interfaces):
                    self.config['interface'] = list(interfaces.keys())[idx]
                    break
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Please enter a number")
        
        # Mode selection
        modes = ["fixed_interval", "random_time"]
        print(f"\nScheduling modes:")
        for i, mode in enumerate(modes, 1):
            current = " (current)" if mode == self.config['mode'] else ""
            print(f"  {i}. {mode.replace('_', ' ').title()}{current}")
        
        while True:
            try:
                choice = input(f"\nSelect mode [1-2] or press Enter to keep current: ").strip()
                if not choice:
                    break
                idx = int(choice) - 1
                if 0 <= idx < len(modes):
                    self.config['mode'] = modes[idx]
                    break
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Please enter a number")
        
        # Interval configuration
        if self.config['mode'] == 'fixed_interval':
            while True:
                try:
                    interval = input(f"\nFixed interval in minutes [{self.config['fixed_interval_minutes']}]: ").strip()
                    if not interval:
                        break
                    interval = int(interval)
                    if interval > 0:
                        self.config['fixed_interval_minutes'] = interval
                        break
                    else:
                        print("❌ Interval must be positive")
                except ValueError:
                    print("❌ Please enter a valid number")
        else:
            while True:
                try:
                    min_interval = input(f"\nMinimum random interval in minutes [{self.config['random_min_minutes']}]: ").strip()
                    if not min_interval:
                        break
                    min_interval = int(min_interval)
                    if min_interval > 0:
                        self.config['random_min_minutes'] = min_interval
                        break
                    else:
                        print("❌ Interval must be positive")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            while True:
                try:
                    max_interval = input(f"\nMaximum random interval in minutes [{self.config['random_max_minutes']}]: ").strip()
                    if not max_interval:
                        break
                    max_interval = int(max_interval)
                    if max_interval >= self.config['random_min_minutes']:
                        self.config['random_max_minutes'] = max_interval
                        break
                    else:
                        print(f"❌ Must be >= {self.config['random_min_minutes']} minutes")
                except ValueError:
                    print("❌ Please enter a valid number")
        
        # Schedule hours
        while True:
            start_time = input(f"\nStart time (HH:MM) [{self.config['start_time']}]: ").strip()
            if not start_time:
                break
            try:
                datetime.strptime(start_time, "%H:%M")
                self.config['start_time'] = start_time
                break
            except ValueError:
                print("❌ Invalid time format (use HH:MM)")
        
        while True:
            end_time = input(f"\nEnd time (HH:MM) [{self.config['end_time']}]: ").strip()
            if not end_time:
                break
            try:
                datetime.strptime(end_time, "%H:%M")
                self.config['end_time'] = end_time
                break
            except ValueError:
                print("❌ Invalid time format (use HH:MM)")
        
        # Enable/disable
        while True:
            enabled = input(f"\nEnable scheduler? (y/n) [{'y' if self.config['enabled'] else 'n'}]: ").strip().lower()
            if not enabled:
                break
            if enabled in ['y', 'yes']:
                self.config['enabled'] = True
                break
            elif enabled in ['n', 'no']:
                self.config['enabled'] = False
                break
            else:
                print("❌ Please enter y or n")
        
        # Save configuration
        self.save_config()
        print("\n✅ Configuration saved successfully")
        self.status()


def restart_with_admin_privileges(system: str) -> int:
    """Restart script with elevated privileges"""
    try:
        if system == "windows":
            import ctypes
            script_path = sys.argv[0]
            args = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in sys.argv[1:])
            elevated_env = f'set ELEVATED_PRIVILEGES=1 && "{sys.executable}" "{script_path}" {args}'
            
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", "cmd.exe", f'/c {elevated_env}', None, 1
            )
            
            if result > 32:
                print("✅ Restarted with administrator privileges")
                return 0
            else:
                print("❌ Failed to get administrator privileges")
                return 1
        else:
            # Linux/macOS: Use sudo
            import os
            sudo_args = ['sudo', sys.executable] + sys.argv
            os.execvp('sudo', sudo_args)
            
    except Exception as e:
        print(f"❌ Privilege elevation failed: {e}")
        return 1


def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(
        description="Cross-platform MAC Address Changer with Automatic Scheduling",
        epilog="Examples:\n"
               "  %(prog)s --list\n"
               "  %(prog)s -i eth0 -m 00:11:22:33:44:55\n"
               "  %(prog)s -i Wi-Fi --random\n"
               "  %(prog)s -i eth0 --restore\n"
               "  %(prog)s --scheduler-start\n"
               "  %(prog)s --scheduler-stop\n"
               "  %(prog)s --scheduler-config",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Basic MAC changing options
    parser.add_argument('-i', '--interface', help='Network interface name')
    parser.add_argument('-m', '--mac', help='New MAC address (XX:XX:XX:XX:XX:XX)')
    parser.add_argument('-r', '--random', action='store_true', help='Generate random MAC')
    parser.add_argument('-l', '--list', action='store_true', help='List interfaces')
    parser.add_argument('-c', '--current', action='store_true', help='Show current MAC')
    parser.add_argument('--restore', action='store_true', help='Restore original MAC')
    
    # Scheduler options
    parser.add_argument('--scheduler-start', action='store_true', help='Start automatic MAC scheduler')
    parser.add_argument('--scheduler-stop', action='store_true', help='Stop automatic MAC scheduler')
    parser.add_argument('--scheduler-status', action='store_true', help='Show scheduler status')
    parser.add_argument('--scheduler-config', action='store_true', help='Configure scheduler settings')
    parser.add_argument('--daemon', action='store_true', help='Run scheduler in daemon mode (background)')
    
    args = parser.parse_args()
    mac_changer = MACChanger()
    scheduler = MACScheduler(mac_changer)
    
    print(f"🔧 MAC Changer - {mac_changer.system.title()}")
    print("=" * 40)
    
    # Handle scheduler commands first
    if args.scheduler_config:
        scheduler.configure_interactive()
        return 0
    elif args.scheduler_status:
        scheduler.status()
        return 0
    elif args.scheduler_start:
        if not mac_changer.is_admin:
            if os.environ.get('SUDO_UID') or os.environ.get('ELEVATED_PRIVILEGES'):
                print("❌ Privilege escalation failed - insufficient permissions")
                return 1
            
            print("⚠️  Administrator/root privileges required for scheduler")
            try:
                response = input("Restart with elevated privileges? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    return restart_with_admin_privileges(mac_changer.system)
                else:
                    print("Operation cancelled")
                    return 1
            except (KeyboardInterrupt, EOFError):
                print("\nCancelled")
                return 1
        
        if scheduler.start():
            if args.daemon:
                print("🔄 Running in daemon mode... Press Ctrl+C to stop")
                try:
                    while scheduler.is_running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    scheduler.stop()
                    print("\n🛑 Daemon stopped by user")
            else:
                print("🔄 Scheduler started. Use --scheduler-stop to stop or --scheduler-status for info")
        return 0
    elif args.scheduler_stop:
        scheduler.stop()
        return 0
    
    # Check for privilege escalation need for regular MAC operations
    if (args.mac or args.random or args.restore) and not mac_changer.is_admin:
        # Prevent infinite loops
        if os.environ.get('SUDO_UID') or os.environ.get('ELEVATED_PRIVILEGES'):
            print("❌ Privilege escalation failed - insufficient permissions")
            return 1
        
        print("⚠️  Administrator/root privileges required")
        try:
            response = input("Restart with elevated privileges? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                return restart_with_admin_privileges(mac_changer.system)
            else:
                print("Operation cancelled")
                return 1
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled")
            return 1
    
    # Handle different operations
    if args.list:
        mac_changer.list_interfaces()
        
    elif args.current:
        if not args.interface:
            print("❌ --interface required")
            return 1
        current_mac = mac_changer.get_current_mac(args.interface)
        print(f"📍 {args.interface}: {current_mac or 'Not found'}")
        
    elif args.restore:
        if not args.interface:
            print("❌ --interface required")
            return 1
        mac_changer.restore_original_mac(args.interface)
        
    elif args.interface:
        # MAC address change operation
        if args.random:
            new_mac = mac_changer.generate_random_mac()
            print(f"🎲 Random MAC: {new_mac}")
        elif args.mac:
            new_mac = args.mac
        else:
            print("❌ Either --mac or --random required")
            return 1
        
        # Show current state
        current_mac = mac_changer.get_current_mac(args.interface)
        print(f"📍 Current: {current_mac or 'Not found'}")
        print(f"🎯 Target:  {new_mac}")
        
        # Attempt MAC change
        success = mac_changer.change_mac_address(args.interface, new_mac)
        
        # Verify result
        time.sleep(3)
        final_mac = mac_changer.get_current_mac(args.interface)
        
        if final_mac and final_mac.lower() == new_mac.lower():
            print(f"✅ SUCCESS: MAC changed to {final_mac}")
        elif final_mac == current_mac:
            print(f"❌ FAILED: MAC unchanged ({final_mac})")
            return 1
        else:
            print(f"⚠️  PARTIAL: Current MAC is {final_mac}")
            
    else:
        # Default: show interfaces and scheduler status
        mac_changer.list_interfaces()
        print("\n" + "="*40)
        scheduler.status()
        print("\nUse --help for all scheduler options")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)