import os
import tkinter as tk
from tkinter import font
import platform
import ctypes
import threading
import time
import subprocess
import tempfile
import imageio

import cv2
import numpy as np
import blend_modes
from skimage import exposure


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


def remove_isolated_pixels(image):
    # https://stackoverflow.com/questions/46143800/removing-isolated-pixels-using-opencv

    connectivity = 32

    output = cv2.connectedComponentsWithStats(image, connectivity, cv2.CV_32S)

    num_stats = output[0]
    labels = output[1]
    stats = output[2]

    new_image = image.copy()

    for label in range(num_stats):
        if stats[label, cv2.CC_STAT_AREA] == 1:
            new_image[labels == label] = 0

    return new_image


def create_lineart(gray_image):

    row_count, column_count = gray_image.shape
    alpha_image = cv2.adaptiveThreshold(
        gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 2
    )
    alpha_image = 255 - alpha_image
    alpha_image = remove_isolated_pixels(alpha_image)
    lineart_image = np.zeros((row_count, column_count, 4), dtype=np.uint8)
    lineart_image[:, :, 3] = alpha_image
    return lineart_image


def toggle_automation():

    global is_on
    if is_on:
        is_on = False
        toggle_button.config(text="Not Running")
    else:
        is_on = True
        toggle_button.config(text="Running")


def watercolorize(filepath):

    # For Unicode filepaths do not use cv2.imread
    input_image = imageio.imread(filepath)
    original_image = cv2.cvtColor(input_image, cv2.COLOR_RGB2BGR)
    row_count, column_count, _ = original_image.shape

    if not is_unlimited.get():
        if row_count > 1280 and column_count > 1280:
            if row_count > column_count:
                size = (int(column_count * (1280 / row_count)), 1280)
            else:
                size = (1280, int(row_count * (1280 / column_count)))
        elif row_count > 1280:
            size = (int(column_count * (1280 / row_count)), 1280)
        elif column_count > 1280:
            size = (1280, int(row_count * (1280 / column_count)))
        original_image = cv2.resize(original_image, size)
        row_count, column_count, _ = original_image.shape

    normal_noise = np.random.rand(row_count, column_count) * 256
    normal_noise[normal_noise < 192] = 0
    normal_noise[normal_noise >= 192] = 255
    normal_noise = normal_noise.astype(np.uint8)
    normal_noise = cv2.cvtColor(normal_noise, cv2.COLOR_GRAY2RGBA).astype(float)

    hsv_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
    _, _, gray_image = cv2.split(hsv_image)
    noisy_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2RGBA).astype(float)
    noisy_image = blend_modes.hard_light(
        noisy_image, normal_noise, 0.4 + 0.1 * strength.get()
    )
    noisy_image = noisy_image.astype(np.uint8)

    with tempfile.TemporaryDirectory() as temporary_folderpath:

        # OIDN only recognizes PFM image format
        noisy_filepath = os.path.join(temporary_folderpath, "noisy_image.pfm")
        squashed_filepath = os.path.join(temporary_folderpath, "squashed_image.pfm")

        # For Unicode filepaths do not use cv2.imwrite
        imageio.imwrite(
            noisy_filepath,
            cv2.cvtColor(noisy_image, cv2.COLOR_RGBA2RGB).astype(np.float32) / 256,
        )

        subprocess.call(
            [
                "./denoiser/oidnDenoise.exe",
                "--ldr",
                noisy_filepath,
                "--output",
                squashed_filepath,
            ]
        )

        while not os.path.isfile(squashed_filepath):
            time.sleep(0.01)

        # For Unicode filepaths do not use cv2.imread
        squashed_image = imageio.imread(squashed_filepath) * 256
        squashed_image = squashed_image.astype(np.uint8)
        squashed_image = cv2.cvtColor(squashed_image, cv2.COLOR_BGR2HSV)
        _, _, squashed_image = cv2.split(squashed_image)

    matched_image = exposure.match_histograms(squashed_image, gray_image)
    matched_image = matched_image.astype(np.uint8)
    matched_image

    hsv_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
    hue, saturation, _ = cv2.split(hsv_image)
    colorized_image = cv2.merge([hue, saturation, matched_image])
    colorized_image = cv2.cvtColor(colorized_image, cv2.COLOR_HSV2BGR)

    if is_lineart_on:
        lineart_image = create_lineart(squashed_image)
        colorized_image = blend_modes.normal(
            cv2.cvtColor(colorized_image, cv2.COLOR_BGR2RGBA).astype(float),
            lineart_image.astype(float),
            1,
        )
        colorized_image = colorized_image.astype(np.uint8)
        colorized_image = cv2.cvtColor(colorized_image, cv2.COLOR_RGBA2BGR)

    # For Unicode filepaths do not use cv2.imwrite
    output_image = cv2.cvtColor(colorized_image, cv2.COLOR_BGR2RGB)
    output_filepath = os.path.splitext(filepath)[0] + "-watercolorized.jpg"
    imageio.imwrite(output_filepath, output_image)


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


is_on = False

threading.Thread(target=automate, name="Automate", daemon=True).start()

window = tk.Tk()
scale_factor = round(window.winfo_fpixels("1i") / 96, 2)

is_unlimited = tk.IntVar()
is_unlimited.set(0)
is_lineart_on = tk.IntVar()
is_unlimited.set(0)
strength = tk.IntVar()
strength.set(3)

default_font = font.nametofont("TkDefaultFont")
default_font.config(size=10)
big_font = default_font.copy()
big_font.config(size=14)
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
    text="Folder containing images to watercolorize",
    anchor="center",
    font=big_font,
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
        "Any JPEG images inside this folder will be automatically watercolorized if"
        " running.\nOriginal image will be left untouched. New image will be"
        " placed beside the original."
    ),
    anchor="center",
    font=small_font,
)
guide_label.pack(
    padx=2 * scale_factor,
    pady=2 * scale_factor,
)

check_frame = tk.LabelFrame(
    inputs_frame,
    text="",
    borderwidth=0,
)
check_frame.pack()

lineart_check = tk.Checkbutton(
    check_frame,
    text="Add Lineart",
    variable=is_lineart_on,
)
lineart_check.grid(row=0, column=0)

size_unlimit_check = tk.Checkbutton(
    check_frame,
    text="Do not limit output image size to 1280 pixels",
    variable=is_unlimited,
)
size_unlimit_check.grid(row=0, column=1)

small_frame = tk.LabelFrame(
    inputs_frame,
    text="",
    borderwidth=0,
)
small_frame.pack()

strength_button = tk.Radiobutton(
    small_frame,
    text="Weaker",
    value=1,
    variable=strength,
)
strength_button.grid(row=0, column=0)
strength_button = tk.Radiobutton(
    small_frame,
    text="Weak",
    value=2,
    variable=strength,
)
strength_button.grid(row=0, column=1)
strength_button = tk.Radiobutton(
    small_frame,
    text="Moderate",
    value=3,
    variable=strength,
)
strength_button.grid(row=0, column=2)
strength_button = tk.Radiobutton(
    small_frame,
    text="Strong",
    value=4,
    variable=strength,
)
strength_button.grid(row=0, column=3)
strength_button = tk.Radiobutton(
    small_frame,
    text="Stronger",
    value=5,
    variable=strength,
)
strength_button.grid(row=0, column=4)

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


window.title("Watercolorizer")
window.minsize(int(1120 * scale_factor), int(300 * scale_factor))
window.geometry("0x0")
window.iconbitmap("./resource/icon.ico")
window.mainloop()
