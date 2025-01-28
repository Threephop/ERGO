import time
import threading
import tkinter as tk
from tkinter import ttk
from popup_video import show_popup  # ฟังก์ชันจาก popup_video.py


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
        time_frame.place(x=50, y=200, width=350, height=120)

        tk.Label(time_frame, text="Set Time 1", font=("Arial", 16), bg="white").place(x=0, y=10, width=100, height=30)

        self.hour_var1 = tk.StringVar(value="10")  # ตั้งค่าเริ่มต้นเป็น 10
        self.minute_var1 = tk.StringVar(value="30")  # ตั้งค่าเริ่มต้นเป็น 30

        ttk.Combobox(time_frame, textvariable=self.hour_var1, width=5, values=[f"{i:02d}" for i in range(24)], state="readonly").place(x=110, y=10, width=50, height=30)
        ttk.Combobox(time_frame, textvariable=self.minute_var1, width=5, values=[f"{i:02d}" for i in range(60)], state="readonly").place(x=170, y=10, width=50, height=30)

        tk.Button(time_frame, text="Set", command=self.set_time1).place(x=240, y=10, width=50, height=30)

        # Set Time 2
        tk.Label(time_frame, text="Set Time 2", font=("Arial", 16), bg="white").place(x=0, y=50, width=100, height=30)

        self.hour_var2 = tk.StringVar(value="15")  # ตั้งค่าเริ่มต้นเป็น 15
        self.minute_var2 = tk.StringVar(value="00")  # ตั้งค่าเริ่มต้นเป็น 30

        ttk.Combobox(time_frame, textvariable=self.hour_var2, width=5, values=[f"{i:02d}" for i in range(24)], state="readonly").place(x=110, y=50, width=50, height=30)
        ttk.Combobox(time_frame, textvariable=self.minute_var2, width=5, values=[f"{i:02d}" for i in range(60)], state="readonly").place(x=170, y=50, width=50, height=30)

        tk.Button(time_frame, text="Set", command=self.set_time2).place(x=240, y=50, width=50, height=30)

        # 🔥 เริ่มทำงานทันทีเมื่อเปิดโปรแกรม
        self.set_time1()
        self.set_time2()

    def update_volume_label(self, *args):
        self.volume_label.config(text=f"{int(self.volume.get())}%")

    def set_time1(self):
        selected_time1 = f"{self.hour_var1.get()}:{self.minute_var1.get()}"
        current_volume = int(self.volume.get())
        print(f"Time 1 set to: {selected_time1}, Volume: {current_volume}%")
        threading.Thread(target=self.check_time, args=(selected_time1, current_volume), daemon=True).start()

    def set_time2(self):
        selected_time2 = f"{self.hour_var2.get()}:{self.minute_var2.get()}"
        current_volume = int(self.volume.get())
        print(f"Time 2 set to: {selected_time2}, Volume: {current_volume}%")
        threading.Thread(target=self.check_time, args=(selected_time2, current_volume), daemon=True).start()

    def check_time(self, target_time, volume):
        while True:
            current_time = time.strftime("%H:%M")
            if current_time == target_time:
                show_popup(volume)
                return  # จบ Thread เมื่อถึงเวลา
            time.sleep(1)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Settings")
    root.geometry("800x400")

    setting_frame = SettingFrame(root)
    setting_frame.place(x=0, y=0, width=800, height=400)

    root.mainloop()
