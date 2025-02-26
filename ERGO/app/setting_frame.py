import time
import threading
import os
import json
import tkinter as tk
from tkinter import ttk
import pygame  # ใช้สำหรับเล่นเสียง
from popup_video import show_popup  # นำเข้า show_popup สำหรับแสดงวิดีโอ

class SettingFrame(tk.Frame):
    def __init__(self, parent, is_muted_callback, change_language_callback):
        super().__init__(parent, bg="white")
        self.is_muted_callback = is_muted_callback  # ฟังก์ชัน callback สำหรับตรวจสอบ mute
        
        # Callback function to notify parent of language change
        self.change_language_callback = change_language_callback
        
        # แก้ไขเส้นทาง settings.json ให้อยู่ในโฟลเดอร์ผู้ใช้
        self.settings_file = os.path.join(os.path.expanduser("~"), "settings.json")
        
        # Initialize language_var before loading settings
        self.language_var = tk.StringVar(value="English")
        
        # โหลดการตั้งค่าจากไฟล์
        self.settings = self.load_settings()
        
        # ใช้ค่าจาก settings.json ถ้ามี
        self.volume = tk.DoubleVar(value=self.settings.get("volume", 50))
        self.language_var.set(self.settings.get("language", "English"))
        self.default_times = self.settings.get("times", [("10", "30"), ("14", "30")])

        self.time_entries = []  # เก็บรายการของ set time
        self.time_threads = []  # เก็บ thread ของการตั้งเวลา
        self.stop_flags = {}

        self.translations = {
            "English": {"volume": "Volume", "language": "Language", "set": "Set", "skip": "Skip", "add_time": "+ Add Time", "set_time": "Set Time", "delete": "Delete"},
            "ภาษาไทย": {"volume": "ระดับเสียง", "language": "ภาษา", "set": "ตั้ง", "skip": "ข้าม", "add_time": "เพิ่มเวลา", "set_time": "ตั้งเวลา", "delete": "ลบ"}
        }

        # เพิ่มเวลา default จากไฟล์หรือค่าเริ่มต้น
        for hour, minute in self.default_times:
            self.add_time_set(hour, minute)

        # Volume control
        volume_frame = tk.Frame(self, bg="white")
        volume_frame.place(x=50, y=50, width=350, height=50)

        self.volume_label = tk.Label(volume_frame, text="Volume", font=("PTT 45 Pride", 16), bg="white")
        self.volume_label.place(x=0, y=10, width=100, height=30)

        self.volume_scale = tk.Scale(
            volume_frame, from_=0, to=100, orient="horizontal", length=200,
            variable=self.volume, bg="white", highlightthickness=0, troughcolor="lightgray", activebackground="blue"
        )
        self.volume_scale.place(x=100, y=0, width=200, height=50)

        self.volume_value_label = tk.Label(volume_frame, text=f"{int(self.volume.get())}%", font=("PTT 45 Pride", 12), bg="white")
        self.volume_value_label.place(x=300, y=10, width=50, height=30)

        self.volume.trace("w", self.update_volume_label)

    def setup_language_control(self):
        """ตั้งค่าการควบคุมภาษา"""
        language_frame = tk.Frame(self, bg="white")
        language_frame.place(x=50, y=120, width=350, height=50)

        self.language_label = tk.Label(language_frame, text="Language", font=("PTT 45 Pride", 16), bg="white")
        self.language_label.place(x=0, y=10, width=100, height=30)

        self.language_dropdown = ttk.Combobox(language_frame, textvariable=self.language_var, font=("PTT 45 Pride", 12), state="readonly")
        self.language_dropdown["values"] = ("English", "ภาษาไทย")
        self.language_dropdown.place(x=140, y=10, width=150, height=30)
        self.language_dropdown.bind("<<ComboboxSelected>>", self.change_language)

        self.update_language_ui(self.language_var.get())
        
        # ปุ่มเพิ่ม Set Time
        add_time_button = tk.Button(self, text=self.translations[self.language_var.get()]["add_time"], command=self.add_time_set)
        add_time_button.place(x=550, y=230, width=100, height=30)

    def update_volume_label(self, *args):
        self.volume_value_label.config(text=f"{int(self.volume.get())}%")

    def change_language(self, event):
        selected_language = self.language_var.get()
        self.update_language_ui(selected_language)
        self.change_language_callback(selected_language)
        self.save_settings()  # Save settings after language change

    def update_language_ui(self, language):
        translations = self.translations.get(language, {})
        if translations:
            self.volume_label.config(text=translations.get("volume", "Volume"))
            self.language_label.config(text=translations.get("language", "Language"))

            for i, (hour_var, minute_var, time_frame, label, set_button, skip_button, delete_button) in enumerate(self.time_entries):
                label.config(text=f"{translations['set_time']} {i + 1}")
                set_button.config(text=translations["set"])
                skip_button.config(text=translations["skip"])
                delete_button.config(text=translations["delete"])

    def add_time_set(self, default_hour="00", default_minute="00"):
        if len(self.time_entries) >= 12:
            print("Cannot add more than 12 time entries.")
            return

        y_offset = 200 + len(self.time_entries) * 50
        time_frame = tk.Frame(self, bg="white")
        time_frame.place(x=50, y=y_offset, width=500, height=80)

        language = self.language_var.get()
        translations = self.translations[language]

        label = tk.Label(time_frame, text=f"{translations['set_time']} {len(self.time_entries) + 1}", font=("Arial", 16), bg="white")
        label.place(x=0, y=10, width=100, height=30)

        hour_var = tk.StringVar(value=hour)
        minute_var = tk.StringVar(value=minute)

        ttk.Combobox(time_frame, textvariable=hour_var, values=[f"{i:02d}" for i in range(24)], state="readonly").place(x=110, y=10, width=50, height=30)
        ttk.Combobox(time_frame, textvariable=minute_var, values=[f"{i:02d}" for i in range(60)], state="readonly").place(x=170, y=10, width=50, height=30)
        
        # ปุ่ม set เวลา
        set_button = tk.Button(time_frame, text=translations["set"], command=lambda: self.set_time(hour_var, minute_var))
        set_button.place(x=240, y=10, width=50, height=30)

        # ปุ่ม skip เวลา
        skip_button = tk.Button(time_frame, text=translations["skip"], command=lambda: self.skip_time(hour_var, minute_var))
        skip_button.place(x=300, y=10, width=50, height=30)

        # ปุ่มลบเวลา
        delete_button = tk.Button(time_frame, text=translations["delete"], command=lambda: self.delete_time_set(time_frame, hour_var, minute_var))
        delete_button.place(x=360, y=10, width=50, height=30)

        self.time_entries.append((hour_var, minute_var, time_frame, label, set_button, skip_button, delete_button))

        # Save settings after adding a new time entry
        self.save_settings()

    def set_time(self, hour_var, minute_var):
        selected_time = f"{hour_var.get()}:{minute_var.get()}"
        current_volume = int(self.volume.get())
        print(f"Time set to: {selected_time}, Volume: {current_volume}%")

        # เพิ่มการบันทึกเวลาไปที่ JSON ทันที
        self.save_current_times()

        def check_time():
            while True:
                current_time = time.strftime("%H:%M")
                if current_time == selected_time and not self.stop_flags.get(selected_time, False):
                    # เล่นเสียงแจ้งเตือน
                    self.play_notification_sound()
                    show_popup(50)
                    break
                time.sleep(1)

        threading.Thread(target=check_time, daemon=True).start()


    def start_check_time(self, hour_var, minute_var, label_text):
        """เริ่มเฝ้าตรวจสอบเวลา และแจ้งเตือนเมื่อถึงเวลา"""
        print(f"{label_text} started at {hour_var.get()}:{minute_var.get()}")

        # ✅ รีเซ็ตค่าให้ทำงานได้อีกครั้ง
        self.stop_flags[label_text] = False  

        def check_time():
            while True:
                current_time = time.strftime("%H:%M")
                if self.stop_flags.get(label_text, False):  
                    print(f"{label_text} skipped.")
                    break

                if current_time == f"{hour_var.get()}:{minute_var.get()}":
                    print(f"Time reached for {label_text}: {current_time}")
                    self.play_notification_sound()
                    show_popup(50)
                    break
                time.sleep(1)

        threading.Thread(target=check_time, daemon=True).start()

    def skip_time(self, hour_var, minute_var):
        selected_time = f"{hour_var.get()}:{minute_var.get()}"
        self.stop_flags[selected_time] = True
        print(f"Skipped time: {selected_time}")
        
        # บันทึกการตั้งค่าหลังจาก skip
        self.save_current_times()

    def delete_time_set(self, time_frame, hour_var, minute_var):
        """ลบเวลาเฉพาะที่เลือก"""
        selected_time = f"{hour_var.get()}:{minute_var.get()}"
        # ลบเวลาออกจาก list
        self.time_entries = [entry for entry in self.time_entries if entry[2] != time_frame]

        # ทำการลบ UI ของ time_frame
        time_frame.destroy()

        # ลบ stop_flags ของเวลา
        if selected_time in self.stop_flags:
            del self.stop_flags[selected_time]

        # บันทึกการตั้งค่าหลังจากลบข้อมูล
        self.save_current_times()
        print("เวลาถูกลบออกแล้ว")

    def play_notification_sound(self):
        """เล่นเสียงแจ้งเตือน"""
        if self.is_muted_callback():
            print("Muted: เสียงแจ้งเตือนถูกปิดอยู่")
            return  # ไม่เล่นเสียงถ้า mute อยู่

        pygame.init()
        pygame.mixer.init()

        sound_path = os.path.join(os.path.dirname(__file__), "sounds", "notification_sound.mp3")
        if os.path.exists(sound_path):
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.set_volume(self.volume.get() / 100)
            pygame.mixer.music.play()
        else:
            print(f"Error: Sound file not found - {sound_path}")

    def save_current_times(self):
        """บันทึกเวลาล่าสุดลงในไฟล์ JSON"""
        times = [(entry[0].get(), entry[1].get()) for entry in self.time_entries]
        self.settings["times"] = times
        self.save_settings()

    def save_settings(self):
        """บันทึกการตั้งค่าไปยังไฟล์ JSON"""
        settings_data = {
            "volume": self.volume.get(),
            "language": self.language_var.get(),
            "times": [(hour.get(), minute.get()) for hour, minute, _, _, _, _, _ in self.time_entries],
        }
        try:
            # สร้างโฟลเดอร์ถ้ายังไม่มี
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

            # เขียนข้อมูลใหม่ลงไฟล์ในครั้งเดียว
            with open(self.settings_file, "w") as file:
                json.dump(settings_data, file, indent=4)

            print("การตั้งค่าถูกบันทึกเรียบร้อยแล้ว")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการบันทึกไฟล์: {e}")

    def load_settings(self):
        """โหลดการตั้งค่าจากไฟล์ JSON"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print("เกิดข้อผิดพลาดในการอ่านไฟล์ JSON")
        return {}

if __name__ == "__main__":
    def on_language_change(language):
        print(f"Language changed to: {language}")

    def is_muted():
        return False  # ตัวอย่าง callback สำหรับตรวจสอบ mute

    root = tk.Tk()
    root.title("Settings")
    root.geometry("800x400")

    # สร้าง SettingFrame ด้วย callback ทั้งสอง
    setting_frame = SettingFrame(root, is_muted_callback=is_muted, change_language_callback=on_language_change)
    setting_frame.place(x=0, y=0, width=800, height=400)

    root.mainloop()
