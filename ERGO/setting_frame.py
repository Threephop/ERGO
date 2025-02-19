import time
import threading
import tkinter as tk
from tkinter import ttk
from popup_video import show_popup  # ฟังก์ชันจาก popup_video.py


class SettingFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        
        self.time_entries = []  # เก็บรายการของ set time
        self.time_threads = []  # เก็บ thread ของการตั้งเวลา
        self.skipped_times = set() # เก็บเวลาที่ skip ไปแล้ว

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

        # ปุ่มเพิ่ม Set Time
        add_time_button = tk.Button(self, text="+ เพิ่มเวลา", command=self.add_time_set)
        add_time_button.place(x=400, y=230, width=100, height=30)

        self.add_time_set("10", "30")
        self.add_time_set("14", "30")

    def update_volume_label(self, *args):
        self.volume_label.config(text=f"{int(self.volume.get())}%")
    
    def add_time_set(self, default_hour="00", default_minute="00"):
        if len(self.time_entries) >= 12:
            print("Cannot add more than 12 set times.")
            return # ไม่สร้างเวลาเพิ่มเมื่อเต็ม 12 ช่อง
    
        y_offset = 200 + len(self.time_entries) * 50
        time_frame = tk.Frame(self, bg="white")
        time_frame.place(x=50, y=y_offset, width=350, height=80)

        tk.Label(time_frame, text=f"Set Time {len(self.time_entries) + 1}", font=("Arial", 16), bg="white").place(x=0, y=10, width=100, height=30)

        hour_var = tk.StringVar(value=default_hour)
        minute_var = tk.StringVar(value=default_minute)

        ttk.Combobox(time_frame, textvariable=hour_var, values=[f"{i:02d}" for i in range(24)], state="readonly").place(x=110, y=10, width=50, height=30)
        ttk.Combobox(time_frame, textvariable=minute_var, values=[f"{i:02d}" for i in range(60)], state="readonly").place(x=170, y=10, width=50, height=30)

        set_button = tk.Button(time_frame, text="Set", command=lambda: self.set_time(hour_var, minute_var))
        set_button.place(x=240, y=10, width=50, height=30)
        
        set_button = tk.Button(time_frame, text="skip", command=lambda: self.stop_time(hour_var, minute_var))
        set_button.place(x=290, y=10, width=50, height=30)

        self.time_entries.append((hour_var, minute_var, time_frame))
        self.set_time(hour_var, minute_var)
    
    def set_time(self, hour_var, minute_var):
        selected_time = f"{hour_var.get()}:{minute_var.get()}"
        current_volume = int(self.volume.get())
        print(f"Time set to: {selected_time}, Volume: {current_volume}%")

        # ลบจาก skipped_times ถ้ามี
        if selected_time in self.skipped_times:
            self.skipped_times.remove(selected_time)

        thread = threading.Thread(target=self.check_time, args=(selected_time,), daemon=True)
        self.time_threads.append(thread)
        thread.start()

    def stop_time(self, hour_var, minute_var):
        selected_time = f"{hour_var.get()}:{minute_var.get()}"
        print(f"Skipping time: {selected_time}")
        self.skipped_times.add(selected_time)  # เพิ่มเวลาที่ skip ไปแล้ว 

    def check_time(self, target_time):
        while True:
            current_time = time.strftime("%H:%M")

            if target_time in self.skipped_times:  # เช็คว่าอยู่ใน skipped_times ไหม
                print(f"Skipped: {target_time}")
                return  # จบ Thread เมื่อถูก skip
            
            if current_time == target_time:
                show_popup(int(self.volume.get()))
                return  # จบ Thread เมื่อถึงเวลา
            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Settings")
    root.geometry("800x400")

    setting_frame = SettingFrame(root)
    setting_frame.place(x=0, y=0, width=800, height=400)

    root.mainloop()
