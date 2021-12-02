import os
import tkinter as tk
from tkinter import font
import platform
import ctypes
import threading
import time
import subprocess
import tempfile

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
        toggle_button.config(text="Not Running")
    else:
        is_on = True
        toggle_button.config(text="Running")


window = tk.Tk()
scale_factor = round(window.winfo_fpixels("1i") / 96, 2)

default_font = font.nametofont("TkDefaultFont")
default_font.config(size=11)
big_font = default_font.copy()
big_font.config(size=16)
small_font = default_font.copy()
small_font.config(size=8)

inputs_frame = tk.LabelFrame(
    window,
    text="",
    padx=24 * scale_factor,
    pady=24 * scale_factor,
)
inputs_frame.place(
    anchor="c",
    relx=0.5,
    rely=0.5,
    width=1040 * scale_factor,
)

title_label = tk.Label(
    inputs_frame,
    text="Folder to automate conversion",
    anchor="center",
)
title_label.pack(
    padx=2 * scale_factor,
    pady=2 * scale_factor,
)

folderpath_input = tk.Entry(inputs_frame, width=120, textvariable=str, justify="center")
folderpath_input.pack(
    padx=2 * scale_factor,
    pady=2 * scale_factor,
)

guide_label = tk.Label(
    inputs_frame,
    text=(
        "All JPEG images inside this folder will be watercolorized.\nOriginal image is"
        " left untouched, while the new image is placed beside the original."
    ),
    anchor="center",
    font=small_font,
)
guide_label.pack(
    padx=2 * scale_factor,
    pady=2 * scale_factor,
)

toggle_button = tk.Button(
    inputs_frame,
    width=20,
    text="Not Running",
    command=toggle_automation,
)
toggle_button.pack(
    padx=2 * scale_factor,
    pady=2 * scale_factor,
)


def watercolorize(filepath):

    # For Unicode filepaths...
    temporary_array = np.fromfile(filepath, np.uint8)
    original_image = cv2.imdecode(temporary_array, cv2.IMREAD_UNCHANGED)

    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    row_count, column_count = gray_image.shape
    random_noise_image = np.random.randn(row_count, column_count) * 128
    noisy_image = gray_image + random_noise_image
    noisy_image = np.clip(noisy_image, 0, 255)
    noisy_image = noisy_image.astype(np.uint8)

    with tempfile.TemporaryDirectory() as temporary_folderpath:

        # These should be ASCII filepaths
        noisy_filepath = os.path.join(temporary_folderpath, "noisy_image.jpg")
        blurred_filepath = os.path.join(temporary_folderpath, "blurred_image.jpg")

        cv2.imwrite(noisy_filepath, noisy_image)

        subprocess.call(
            [
                "./denoiser/Denoiser.exe",
                "-i",
                noisy_filepath,
                "-o",
                blurred_filepath,
            ]
        )

        while not os.path.isfile(blurred_filepath):
            time.sleep(0.01)

        blurred_image = cv2.imread(blurred_filepath, cv2.IMREAD_GRAYSCALE)

    hsv_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
    hue, saturation, _ = cv2.split(hsv_image)
    hsv_image = cv2.merge([hue, saturation, blurred_image])
    colorized_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

    final_filepath = os.path.splitext(filepath)[0] + "-watercolorized.jpg"

    # For Unicode filepaths...
    _, buffer = cv2.imencode(".jpg", colorized_image, None)
    with open(final_filepath, mode="w+b") as f:
        buffer.tofile(f)


def automate():

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
            and filename.endswith((".jpg", ".jpeg"))
        ]
        for filename in filenames:
            if not filename.endswith("-watercolorized.jpg"):
                filepath = os.path.join(folderpath, filename)
                final_filepath = os.path.splitext(filepath)[0] + "-watercolorized.jpg"
                if not os.path.isfile(final_filepath):
                    watercolorize(filepath)
        time.sleep(1)


threading.Thread(target=automate, name="Automate", daemon=True).start()

window.title("Watercolorizer")
window.minsize(int(1120 * scale_factor), int(200 * scale_factor))
window.geometry("0x0")
window.iconbitmap("./resource/icon.ico")
window.mainloop()
