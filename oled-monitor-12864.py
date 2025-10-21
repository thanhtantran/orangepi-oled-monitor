#!/usr/bin/env python3
import time
import psutil
import subprocess
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

# Setup I2C interface for Orange Pi CM5
serial = i2c(port=5, address=0x3C)
device = ssd1306(serial)

# Use a clearer font
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 11)
    small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)
except:
    font = ImageFont.load_default()
    small_font = ImageFont.load_default()

def get_cpu_temperature():
    try:
        # Method 1: Try thermal zone
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read().strip()) / 1000.0
        return f"{temp:.1f}°C"
    except:
        try:
            # Method 2: Try vcgencmd (if available)
            result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
            temp_str = result.stdout.strip()
            return temp_str.replace("temp=", "")
        except:
            return "N/A"

def get_local_ip():
    try:
        # Get all network interfaces
        import netifaces
        # Try common interfaces first
        interfaces = ['eth0', 'wlan0', 'wlan1', 'enx*', 'wlx*']
        
        for interface in interfaces:
            try:
                # Get IPv4 addresses for the interface
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    ip_info = addrs[netifaces.AF_INET][0]
                    ip = ip_info['addr']
                    # Check if it's a private/local IP
                    if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
                        return ip
            except:
                continue
        
        # If specific interfaces fail, try all interfaces
        for interface in netifaces.interfaces():
            try:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    ip_info = addrs[netifaces.AF_INET][0]
                    ip = ip_info['addr']
                    # Check if it's a private/local IP
                    if (ip.startswith('192.168.') or 
                        ip.startswith('10.') or 
                        (ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31)):
                        if ip != '127.0.0.1':
                            return ip
            except:
                continue
                
        return "No Local IP"
    except:
        # Fallback method
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Connect to a local address to determine which interface would be used
            s.connect(("192.168.1.1", 80))  # Connect to a common router IP
            ip = s.getsockname()[0]
            s.close()
            if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
                return ip
            else:
                return "No Local IP"
        except:
            return "No IP"

def main():
    while True:
        # Get system information
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_temp = get_cpu_temperature()
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        ip_address = get_local_ip()
        
        # Display on OLED
        with canvas(device) as draw:
            draw.text((0, 0), f"CPU: {cpu_usage}%", font=font, fill="white")
            draw.text((0, 15), f"RAM: {ram_usage}%", font=font, fill="white")            
            draw.text((0, 30), f"Temp: {cpu_temp}", font=font, fill="white")
            draw.text((0, 45), f"IP: {ip_address}", font=font, fill="white")
        
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
