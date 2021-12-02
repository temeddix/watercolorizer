import os
import tkinter as tk
import platform
import ctypes
import threading
import time
import subprocess

import cv2
import numpy as np


# Set DPI
if platform.system() == "Windows":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

# Hide Terminal
if platform.system() == "Windows":
    kernel32 = ctypes.WinDLL("kernel32")
    user32 = ctypes.WinDLL("user32")
    console_window = kernel32.GetConsoleWindow()
    user32.ShowWindow(console_window, 0)
elif platform.system() == "Linux":
    pass
elif platform.system() == "Darwin":  # macOS
    pass

is_on = False


def toggle_automation():
    global is_on
    if is_on:
        is_on = False
        status_label.config(text="Not Running")
    else:
        is_on = True
        status_label.config(text="Running")


window = tk.Tk()
scale_factor = round(window.winfo_fpixels("1i") / 96, 2)

inputs_frame = tk.LabelFrame(
    window,
    text="",
    padx=6 * scale_factor,
    pady=6 * scale_factor,
    height=1000,
)
inputs_frame.pack(
    side="top",
    fill="y",
    padx=10 * scale_factor,
    pady=10 * scale_factor,
)

title_label = tk.Label(
    inputs_frame,
    text="Folder to Automate",
    width=50,
    anchor="center",
    font=("*", 10),
)
title_label.pack(
    padx=2 * scale_factor,
    pady=2 * scale_factor,
)

folderpath_input = tk.Entry(
    inputs_frame,
    width=62,
    textvariable=str,
    font=("*", 10),
)
folderpath_input.pack(
    padx=2 * scale_factor,
    pady=2 * scale_factor,
)

toggle_button = tk.Button(
    inputs_frame,
    width=30,
    text="Toggle",
    font=("*", 10),
    command=toggle_automation,
)
toggle_button.pack(
    padx=2 * scale_factor,
    pady=2 * scale_factor,
)

status_label = tk.Label(
    inputs_frame,
    text="Not Running",
    width=50,
    anchor="center",
    font=("*", 14),
)
status_label.pack(
    padx=2 * scale_factor,
    pady=2 * scale_factor,
)


def watercolorize(filepath):
    original_image = cv2.imread(filepath, cv2.IMREAD_COLOR)

    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    row_count, column_count = gray_image.shape
    random_noise_image = np.random.randn(row_count, column_count) * 128
    noisy_image = gray_image + random_noise_image
    noisy_image = np.clip(noisy_image, 0, 255)
    noisy_image = noisy_image.astype(np.uint8)

    temporary_filepath = os.path.splitext(filepath)[0] + "-temporary.jpg"
    cv2.imwrite(temporary_filepath, noisy_image)

    subprocess.call(
        [
            "./denoiser/Denoiser.exe",
            "-i",
            temporary_filepath,
            "-o",
            temporary_filepath,
        ]
    )

    while not os.path.isfile(temporary_filepath):
        time.sleep(0.01)

    blurred_image = cv2.imread(temporary_filepath, cv2.IMREAD_GRAYSCALE)
    os.remove(temporary_filepath)
    hsv_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
    hue, saturation, _ = cv2.split(hsv_image)
    hsv_image = cv2.merge([hue, saturation, blurred_image])
    colorized_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

    final_filepath = os.path.splitext(filepath)[0] + "-watercolorized.jpg"
    cv2.imwrite(final_filepath, colorized_image)


def job():
    while True:
        global is_on
        if not is_on:
            time.sleep(1)
            continue
        folderpath = folderpath_input.get()
        if not os.path.isdir(folderpath):
            time.sleep(1)
            continue
        filenames = [
            filename
            for filename in os.listdir(folderpath)
            if os.path.isfile(os.path.join(folderpath, filename))
        ]
        for filename in filenames:
            if not filename.endswith("-watercolorized.jpg"):
                filepath = os.path.join(folderpath, filename)
                final_filepath = os.path.splitext(filepath)[0] + "-watercolorized.jpg"
                if not os.path.isfile(final_filepath) and not filepath.endswith(
                    "-temporary.jpg"
                ):
                    watercolorize(filepath)
        time.sleep(1)


threading.Thread(target=job, name="Automation", daemon=True).start()

window.title("Watercolorizer")
window.minsize(int(600 * scale_factor), int(600 * scale_factor))
window.geometry("0x0")
window.iconbitmap("./icon.ico")
window.mainloop()
