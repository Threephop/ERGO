import time
import threading
import tkinter as tk
from tkinter import ttk
from popup_video import show_popup  # ฟังก์ชันจาก popup_video.py
import pygame  # ใช้สำหรับเล่นเสียง

class SettingFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        # Volume control
        volume_frame = tk.Frame(self, bg="white")
        volume_frame.place(x=50, y=50, width=350, height=50)

        tk.Label(volume_frame, text="Volume", font=("Arial", 16), bg="white").place(x=0, y=10, width=80, height=30)

        self.volume = tk.DoubleVar(value=50)
        self.volume_scale = tk.Scale(
            volume_frame, from_=0, to=100, orient="horizontal",
            length=200, variable=self.volume, bg="white",
            highlightthickness=0, troughcolor="lightgray", activebackground="blue"
        )
        self.volume_scale.place(x=90, y=0, width=200, height=50)

        self.volume_label = tk.Label(volume_frame, text=f"{int(self.volume.get())}%", font=("Arial", 12), bg="white")
        self.volume_label.place(x=300, y=10, width=50, height=30)

        self.volume.trace("w", self.update_volume_label)

        # Language control
        language_frame = tk.Frame(self, bg="white")
        language_frame.place(x=50, y=120, width=350, height=50)

        tk.Label(language_frame, text="Language", font=("Arial", 16), bg="white").place(x=0, y=10, width=100, height=30)

        self.language_var = tk.StringVar(value="Select")
        self.language_dropdown = ttk.Combobox(language_frame, textvariable=self.language_var, font=("Arial", 12), state="readonly")
        self.language_dropdown["values"] = ("English", "ภาษาไทย")
        self.language_dropdown.place(x=110, y=10, width=150, height=30)

        # Time control
        time_frame = tk.Frame(self, bg="white")
        time_frame.place(x=50, y=200, width=350, height=100)

        tk.Label(time_frame, text="Set Time 1", font=("Arial", 16), bg="white").place(x=0, y=10, width=100, height=30)

        self.hour_var1 = tk.StringVar(value="10")
        self.minute_var1 = tk.StringVar(value="30")

        ttk.Combobox(time_frame, textvariable=self.hour_var1, width=5, values=[f"{i:02d}" for i in range(24)], state="readonly").place(x=110, y=10, width=50, height=30)
        ttk.Combobox(time_frame, textvariable=self.minute_var1, width=5, values=[f"{i:02d}" for i in range(60)], state="readonly").place(x=170, y=10, width=50, height=30)

        tk.Button(time_frame, text="Set", command=lambda: self.set_time(self.hour_var1, self.minute_var1)).place(x=240, y=10, width=50, height=30)

        # Set Time 2
        tk.Label(time_frame, text="Set Time 2", font=("Arial", 16), bg="white").place(x=0, y=50, width=100, height=30)

        self.hour_var2 = tk.StringVar(value="15")
        self.minute_var2 = tk.StringVar(value="00")

        ttk.Combobox(time_frame, textvariable=self.hour_var2, width=5, values=[f"{i:02d}" for i in range(24)], state="readonly").place(x=110, y=50, width=50, height=30)
        ttk.Combobox(time_frame, textvariable=self.minute_var2, width=5, values=[f"{i:02d}" for i in range(60)], state="readonly").place(x=170, y=50, width=50, height=30)

        tk.Button(time_frame, text="Set", command=lambda: self.set_time(self.hour_var2, self.minute_var2)).place(x=240, y=50, width=50, height=30)

    def update_volume_label(self, *args):
        self.volume_label.config(text=f"{int(self.volume.get())}%")

    def set_time(self, hour_var, minute_var):
        selected_time = f"{hour_var.get()}:{minute_var.get()}"
        current_volume = int(self.volume.get())
        print(f"Time set to: {selected_time}, Volume: {current_volume}%")

        def check_time():
            while True:
                current_time = time.strftime("%H:%M")
                if current_time == selected_time:
                    # เล่นเสียงแจ้งเตือน
                    self.play_notification_sound()
                    show_popup(current_volume)
                    break
                time.sleep(60)

        threading.Thread(target=check_time, daemon=True).start()

    def play_notification_sound(self):
        """เล่นเสียงแจ้งเตือน"""
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("D:/project/GitHub/ERGO/ERGO/sounds/notification_sound.mp3")
        pygame.mixer.music.set_volume(self.volume.get() / 100)  # ตั้งค่า Volume ตามที่ผู้ใช้ตั้ง
        pygame.mixer.music.play()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Settings")
    root.geometry("800x400")

    setting_frame = SettingFrame(root)
    setting_frame.place(x=0, y=0, width=800, height=400)

    root.mainloop()
