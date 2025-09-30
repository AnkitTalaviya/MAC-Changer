#!/usr/bin/env python3
"""
Demo script showing what the MAC scheduler looks like when running
This simulates the continuous monitoring without actually changing MACs
"""

import time
import random
from datetime import datetime, timedelta

def simulate_mac_scheduler():
    """Simulate the MAC scheduler output"""
    
    # Sample configuration
    interface = "Wi-Fi"
    mode = "random_time" 
    min_interval = 2  # minutes
    max_interval = 4  # minutes
    
    # Sample MAC addresses
    mac_addresses = [
        "00:E0:4C:B8:38:2F",
        "02:A1:B2:C3:D4:E5", 
        "06:F2:E1:D8:C7:B6",
        "0A:B3:C4:D5:E6:F7",
        "0E:D4:C5:B6:A7:98"
    ]
    
    current_mac_index = 0
    
    print(f"\n🚀 MAC Scheduler Started - Press Ctrl+C to stop")
    print(f"📡 Interface: {interface}")
    print(f"⏱️ Mode: {mode}")
    print(f"🎲 Random: {min_interval}-{max_interval} minutes")
    print("=" * 60)
    
    try:
        while True:
            # Simulate MAC change
            old_mac = mac_addresses[current_mac_index]
            current_mac_index = (current_mac_index + 1) % len(mac_addresses)
            new_mac = mac_addresses[current_mac_index]
            
            print(f"\n🔄 [{datetime.now().strftime('%H:%M:%S')}] Current MAC: {old_mac}")
            print(f"🎯 Changing to: {new_mac}")
            
            # Simulate change delay
            time.sleep(2)
            
            # Calculate next interval (2-4 minutes in seconds)
            next_interval = random.randint(min_interval * 60, max_interval * 60)
            next_change = datetime.now() + timedelta(seconds=next_interval)
            
            print(f"⏰ Next change: {next_change.strftime('%H:%M:%S')} ({next_interval//60}m {next_interval%60}s)")
            
            # Simulate countdown with live MAC display
            elapsed = 0
            while elapsed < next_interval:
                remaining = next_interval - elapsed
                mins, secs = divmod(remaining, 60)
                
                # Show current MAC every 5 seconds (faster for demo)
                if elapsed % 5 == 0:
                    print(f"\r📍 [{datetime.now().strftime('%H:%M:%S')}] Current: {new_mac} | Next in: {mins:02d}:{secs:02d}", end='', flush=True)
                
                time.sleep(1)  # Faster for demo
                elapsed += 1
            
            print()  # New line after countdown
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 MAC scheduler stopped by user")
        print(f"📍 Final MAC: {mac_addresses[current_mac_index]}")

if __name__ == "__main__":
    print("🔧 MAC Changer - Demo Mode")
    print("=" * 40)
    print("⚠️  This is a DEMO - no actual MAC changes will occur")
    print("   To run the real scheduler with MAC changes:")
    print("   python mac_changer.py --scheduler-start")
    print()
    
    input("Press Enter to start demo...")
    simulate_mac_scheduler()