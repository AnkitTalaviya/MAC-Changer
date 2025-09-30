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
from typing import Optional, Dict


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
            print(f"Γ¥î Invalid MAC address format: {new_mac}")
            return False
            
        if not self.is_admin:
            print("Γ¥î Administrator/root privileges required!")
            return False
            
        print(f"≡ƒöº Changing MAC address of '{interface}' to '{new_mac}'...")
        
        try:
            if self.system == "windows":
                return self._change_mac_windows(interface, new_mac)
            elif self.system == "linux":
                return self._change_mac_linux(interface, new_mac)
            elif self.system == "darwin":
                return self._change_mac_macos(interface, new_mac)
            else:
                print(f"Γ¥î Unsupported OS: {self.system}")
                return False
        except Exception as e:
            print(f"Γ¥î MAC change error: {e}")
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
                    
                    print("  Γ£à PowerShell method completed")
                    return True
                    
            except subprocess.CalledProcessError:
                print("  Γ¥î PowerShell method failed")
            
            # Method 2: Manual instructions for unsupported adapters
            print(f"\n≡ƒôï Manual MAC Change Required:")
            print(f"  1. Open Device Manager (Win + X ΓåÆ Device Manager)")
            print(f"  2. Network adapters ΓåÆ Find your {interface} adapter")
            print(f"  3. Right-click ΓåÆ Properties ΓåÆ Advanced tab")
            print(f"  4. Look for 'Network Address' or 'MAC Address'")
            print(f"  5. Set value to: {clean_mac}")
            print(f"  6. Click OK and restart adapter")
            print(f"\n  ΓÜá∩╕Å  If no 'Network Address' property exists,")
            print(f"      your adapter doesn't support MAC changing")
            
            return False
            
        except Exception as e:
            print(f"  Γ¥î Error: {e}")
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
                
                print(f"  Γ£à Method {method} successful")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"  Γ¥î Method {method} failed: {e}")
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
            
            print(f"  Γ£à macOS MAC change successful")
            if 'en' in interface:
                print(f"  Γä╣∩╕Å  You may need to reconnect to Wi-Fi")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  Γ¥î macOS MAC change failed: {e}")
            print(f"  Γä╣∩╕Å  Some macOS versions restrict MAC changing")
            return False
        except Exception as e:
            print(f"  Γ¥î Error: {e}")
            return False
    
    def get_current_mac(self, interface: str) -> Optional[str]:
        """Get current MAC address of specified interface"""
        interfaces = self.get_network_interfaces()
        return interfaces.get(interface)
    
    def list_interfaces(self):
        """Display all available network interfaces"""
        print(f"\n≡ƒôí Network Interfaces ({self.system.title()}):")
        print("=" * 50)
        
        interfaces = self.get_network_interfaces()
        if not interfaces:
            print("Γ¥î No network interfaces found")
            return
        
        for interface, mac in interfaces.items():
            print(f"≡ƒöî {interface}")
            print(f"   MAC: {mac}")
            print()
    
    def restore_original_mac(self, interface: str) -> bool:
        """Restore original MAC address by restarting interface"""
        print("≡ƒöä Restoring original MAC address...")
        
        if self.system == "linux":
            try:
                subprocess.run(['ip', 'link', 'set', 'dev', interface, 'down'], check=True, capture_output=True)
                time.sleep(1)
                subprocess.run(['ip', 'link', 'set', 'dev', interface, 'up'], check=True, capture_output=True)
                print("Γ£à Interface restarted - original MAC restored")
                return True
            except subprocess.CalledProcessError:
                pass
        
        print("Γä╣∩╕Å  Restart your network adapter or reboot to restore original MAC")
        return False


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
                print("Γ£à Restarted with administrator privileges")
                return 0
            else:
                print("Γ¥î Failed to get administrator privileges")
                return 1
        else:
            # Linux/macOS: Use sudo
            import os
            sudo_args = ['sudo', sys.executable] + sys.argv
            os.execvp('sudo', sudo_args)
            
    except Exception as e:
        print(f"Γ¥î Privilege elevation failed: {e}")
        return 1


def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(
        description="Cross-platform MAC Address Changer",
        epilog="Examples:\n"
               "  %(prog)s --list\n"
               "  %(prog)s -i eth0 -m 00:11:22:33:44:55\n"
               "  %(prog)s -i Wi-Fi --random\n"
               "  %(prog)s -i eth0 --restore",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-i', '--interface', help='Network interface name')
    parser.add_argument('-m', '--mac', help='New MAC address (XX:XX:XX:XX:XX:XX)')
    parser.add_argument('-r', '--random', action='store_true', help='Generate random MAC')
    parser.add_argument('-l', '--list', action='store_true', help='List interfaces')
    parser.add_argument('-c', '--current', action='store_true', help='Show current MAC')
    parser.add_argument('--restore', action='store_true', help='Restore original MAC')
    
    args = parser.parse_args()
    mac_changer = MACChanger()
    
    print(f"≡ƒöº MAC Changer - {mac_changer.system.title()}")
    print("=" * 40)
    
    # Check for privilege escalation need
    if (args.mac or args.random or args.restore) and not mac_changer.is_admin:
        # Prevent infinite loops
        if os.environ.get('SUDO_UID') or os.environ.get('ELEVATED_PRIVILEGES'):
            print("Γ¥î Privilege escalation failed - insufficient permissions")
            return 1
        
        print("ΓÜá∩╕Å  Administrator/root privileges required")
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
            print("Γ¥î --interface required")
            return 1
        current_mac = mac_changer.get_current_mac(args.interface)
        print(f"≡ƒôì {args.interface}: {current_mac or 'Not found'}")
        
    elif args.restore:
        if not args.interface:
            print("Γ¥î --interface required")
            return 1
        mac_changer.restore_original_mac(args.interface)
        
    elif args.interface:
        # MAC address change operation
        if args.random:
            new_mac = mac_changer.generate_random_mac()
            print(f"≡ƒÄ▓ Random MAC: {new_mac}")
        elif args.mac:
            new_mac = args.mac
        else:
            print("Γ¥î Either --mac or --random required")
            return 1
        
        # Show current state
        current_mac = mac_changer.get_current_mac(args.interface)
        print(f"≡ƒôì Current: {current_mac or 'Not found'}")
        print(f"≡ƒÄ» Target:  {new_mac}")
        
        # Attempt MAC change
        success = mac_changer.change_mac_address(args.interface, new_mac)
        
        # Verify result
        time.sleep(3)
        final_mac = mac_changer.get_current_mac(args.interface)
        
        if final_mac and final_mac.lower() == new_mac.lower():
            print(f"Γ£à SUCCESS: MAC changed to {final_mac}")
        elif final_mac == current_mac:
            print(f"Γ¥î FAILED: MAC unchanged ({final_mac})")
            return 1
        else:
            print(f"ΓÜá∩╕Å  PARTIAL: Current MAC is {final_mac}")
            
    else:
        # Default: show interfaces
        mac_changer.list_interfaces()
        print("Use --help for options")
    
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
