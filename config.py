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
import cv2
import tempfile
import os
from screeninfo import get_monitors

# Defaults
root = tk.Tk()
SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()
root.destroy()

# Creates the 64x64 image for the tray icon
def create_icon_image():
    img = Image.new('RGB', (64, 64), color='#1f538d')
    # Optional: Draw a tiny white dot or design inside it
    d = ImageDraw.Draw(img)
    d.rectangle([(16, 16), (48, 48)], fill='white')
    return img

# Returns a list of all available GPUs on the system
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

# kills all the old ffmpeg instances (this is so the program doesn't hang on launch)
def clear_old_ffmpeg_instances():
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "ffmpeg.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

        # 2. Gives a bit to release the file handles
    time.sleep(0.2)

# Running-------------------------------
with open('defaults.csv','r') as csvfile:
    reader = csv.reader(csvfile)

    for line in reader:
        if line[0] == 'clip_key':
            CLIP_KEY = line[1]

TRAY_ICON = create_icon_image()
clear_old_ffmpeg_instances()
GPU_LIST = get_gpu_name()

