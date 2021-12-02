import os
import tkinter as tk
import platform
import ctypes
import threading
import time
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

detail_label = tk.Label(
    inputs_frame,
    text="Status Detail",
    width=50,
    anchor="center",
    font=("*", 8),
)
detail_label.pack(
    padx=2 * scale_factor,
    pady=2 * scale_factor,
)


did_show = False


def watercolorize(filepath):
    original_image = cv2.imread(filepath, cv2.IMREAD_COLOR)

    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    row_count, column_count = gray_image.shape
    random_noise_image = np.random.randn(row_count, column_count) * 32
    noisy_image = gray_image + random_noise_image
    noisy_image = np.clip(noisy_image, 0, 255)
    noisy_image = noisy_image.astype(np.uint8)

    global did_show
    if not did_show:
        did_show = True
        cv2.imshow("Noisy", noisy_image)
        cv2.waitKey(0)  # delay 0
        cv2.destroyAllWindows()


def job():
    while True:
        folderpath = folderpath_input.get()
        try:
            filenames = [
                filename
                for filename in os.listdir(folderpath)
                if os.path.isfile(os.path.join(folderpath, filename))
            ]
            for filename in filenames:
                if not filename.endswith("-watercolorized.jpg"):
                    new_filename = os.path.splitext(filename)[0] + "-watercolorized.jpg"
                    if not os.path.isfile(os.path.join(folderpath, new_filename)):
                        watercolorize(os.path.join(folderpath, filename))
        except FileNotFoundError:
            pass
        time.sleep(1)


threading.Thread(target=job, name="Automation", daemon=True).start()

window.title("Generator")
window.minsize(int(600 * scale_factor), int(600 * scale_factor))
window.geometry("0x0")
window.iconbitmap("./icon.ico")
window.mainloop()
