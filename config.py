import keyboard
import customtkinter
import numpy
import tkinter as tk
import sounddevice as sd
import ffmpeg
import csv
from PIL import Image, ImageDraw
import pystray
import threading
import mss
import time
import subprocess
from pathlib import Path
import winreg

root = tk.Tk()
SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()
root.destroy()

def create_icon_image():
    """Generates a simple 64x64 blue square icon image for the tray."""
    img = Image.new('RGB', (64, 64), color='#1f538d')
    # Optional: Draw a tiny white dot or design inside it
    d = ImageDraw.Draw(img)
    d.rectangle([(16, 16), (48, 48)], fill='white')
    return img

TRAY_ICON = create_icon_image() # Stores the icon image for if it is minimized to tray

def get_gpu_name():
    gpu_list = []

    # Method 1: PowerShell (Most accurate for active GPUs)
    try:
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name",
        ]
        output = subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL
        )

        for line in output.splitlines():
            line = line.strip()
            if line and line not in gpu_list:
                gpu_list.append(line)
    except Exception:
        pass

    # Method 2: Windows Registry (Backup if PowerShell is restricted)
    if not gpu_list:
        try:
            reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        sub_key_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(
                            key, sub_key_name
                        ) as sub_key:
                            driver_desc, _ = winreg.QueryValueEx(
                                sub_key, "DriverDesc"
                            )
                            if driver_desc and driver_desc not in gpu_list:
                                gpu_list.append(driver_desc)
                    except Exception:
                        continue
        except Exception:
            pass

    # Always add CPU fallback
    gpu_list.append("CPU Only (No GPU)")
    return gpu_list


GPU_LIST = get_gpu_name()
print(GPU_LIST)

with open('defaults.csv','r') as csvfile:
    reader = csv.reader(csvfile)

    for line in reader:
        if line[0] == 'clip_key':
            CLIP_KEY = line[1]
