import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import psutil
import subprocess
import socket

# Initialize both OLED displays
disp1 = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_address=0x3C)
disp1.begin()
disp1.clear()
disp1.display()

disp2 = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_address=0x3D)
disp2.begin()
disp2.clear()
disp2.display()

width = disp1.width
height = disp1.height
font = ImageFont.load_default()

def draw_bar(draw, x, y, width, height, value, max_value):
    """Draws a bar on the provided drawing context."""
    bar_height = int(height * value / max_value)
    draw.rectangle((x, y, x + width, y + height), outline=255, fill=0)
    draw.rectangle((x, y + height - bar_height, x + width, y + height), outline=255, fill=255)

def get_wifi_status():
    try:
        # Using subprocess to get SSID
        cmd = "iwgetid -r"
        ssid = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()

        if ssid:
            return f"Connected to {ssid}"
        else:
            return "Disconnected"
    except subprocess.CalledProcessError:
        return "No WiFi"
    
def get_local_ip():
    """Get the local IP address of the device."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Use Google's public DNS server to find the local endpoint address.
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "No IP"

while True:
    # OLED 1: CPU and Memory
    image1 = Image.new('1', (width, height))
    draw1 = ImageDraw.Draw(image1)

    cpu_percents = psutil.cpu_percent(percpu=True)
    bar_width = width // len(cpu_percents)

    for idx, cpu_percent in enumerate(cpu_percents):
        x = bar_width * idx
        draw1.text((x, 0), f"C{idx}", font=font, fill=255)
        draw_bar(draw1, x, 10, bar_width-2, 20, cpu_percent, 100)
        draw1.text((x, 32), f"{cpu_percent}%", font=font, fill=255)

    # For the memory usage on OLED1:
    mem = psutil.virtual_memory()
    mem_used_gb = mem.used / (1024**3)
    mem_total_gb = mem.total / (1024**3)
    mem_pct = int((mem.used / mem.total) * 100)
    draw1.text((0, 48), f"Mem {mem_used_gb:.1f}G/{mem_total_gb:.1f}G ({mem_pct}%)", font=font, fill=255)

    disp1.image(image1)
    disp1.display()

    # OLED 2: Storage, Swap, and WiFi
    image2 = Image.new('1', (width, height))
    draw2 = ImageDraw.Draw(image2)

    disk_info = psutil.disk_usage('/')
    disk_used_gb = disk_info.used / (1024**3)
    disk_free_gb = disk_info.free / (1024**3)
    draw2.text((0, 0), f"Used:{disk_used_gb:.1f}G/Free:{disk_free_gb:.1f}G", font=font, fill=255)

    swap_pct = int((psutil.swap_memory().used / psutil.swap_memory().total) * 100)
    draw2.text((0, 18), f"Swap: {swap_pct}%", font=font, fill=255)

    wifi_status = get_wifi_status()
    ip_address = get_local_ip()

    draw2.text((0, 36), wifi_status, font=font, fill=255)
    draw2.text((0, 54), f"IP: {ip_address}", font=font, fill=255)

    disp2.image(image2)
    disp2.display()
