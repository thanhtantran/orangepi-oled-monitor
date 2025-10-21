#!/usr/bin/env python3
# Run with: sudo python3 oled-monitor.py
import time
import socket
import psutil
import subprocess
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

# Setup I2C interface for Orange Pi CM5 - 128x32 display
serial = i2c(port=5, address=0x3C)
device = ssd1306(serial, width=128, height=32)

# Use a smaller font for 32px height display
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)
    small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 8)
except:
    font = ImageFont.load_default()
    small_font = ImageFont.load_default()

def get_cpu_temperature():
    try:
        # Method 1: Try thermal zone
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read().strip()) / 1000.0
        return f"{temp:.0f}C"
    except:
        try:
            # Method 2: Try vcgencmd (if available)
            result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
            temp_str = result.stdout.strip()
            return temp_str.replace("temp=", "").replace("°", "")
        except:
            return "N/A"

def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d{hours}h"
        elif hours > 0:
            return f"{hours}h{minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "N/A"

def get_local_ip():
    try:
        # Get all network interfaces
        import netifaces
        
        for interface in netifaces.interfaces():
            try:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    ip_info = addrs[netifaces.AF_INET][0]
                    ip = ip_info['addr']
                    # Check if it's a private/local IP (not loopback)
                    if ip != '127.0.0.1' and (
                        ip.startswith('192.168.') or 
                        ip.startswith('10.') or 
                        (ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31)):
                        return ip
            except:
                continue
                
        return "No IP"
    except ImportError:
        # Fallback method if netifaces is not available
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip if ip != '127.0.0.1' else "No IP"
        except:
            return "No IP"

def main():
    print("Starting OLED monitor (128x32)...")
    while True:
        try:
            # Get system information
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_temp = get_cpu_temperature()
            ram = psutil.virtual_memory()
            ram_usage = ram.percent
            uptime = get_uptime()
            ip_address = get_local_ip()
            
            # Display on OLED (128x32 layout)
            with canvas(device) as draw:
                # Line 1: CPU and RAM (top)
                draw.text((0, 0), f"CPU:{cpu_usage:.0f}%", font=font, fill="white")
                draw.text((65, 0), f"RAM:{ram_usage:.0f}%", font=font, fill="white")
                
                # Line 2: Temperature and Uptime (middle)
                draw.text((0, 11), f"Temp:{cpu_temp}", font=font, fill="white")
                draw.text((65, 11), f"Up:{uptime}", font=font, fill="white")
                
                # Line 3: IP Address (bottom)
                draw.text((0, 22), f"IP:{ip_address}", font=small_font, fill="white")
            
            time.sleep(1)
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        pass
    except Exception as e:
        print(f"Fatal error: {e}")