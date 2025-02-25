import time
import threading
import os
import tkinter as tk
from tkinter import ttk
import pygame  # ใช้สำหรับเล่นเสียง
from popup_video import show_popup  # นำเข้า show_popup สำหรับแสดงวิดีโอ

class SettingFrame(tk.Frame):
    def __init__(self, parent, is_muted_callback, change_language_callback):
        super().__init__(parent, bg="white")
        self.is_muted_callback = is_muted_callback  
        self.change_language_callback = change_language_callback  

        self.stop_flags = {}
        self.time_entries = []  
        self.max_time_entries = 12

        self.language_var = tk.StringVar(value="English")

        # ปุ่มเพิ่มเวลา
        self.add_time_button = tk.Button(
            self, text="+ Add Time", font=("Arial", 12), bg="#f0f0f0", 
            relief="raised", command=self.add_time_set
        )
        self.add_time_button.place(x=595, y=240, width=110, height=40)

        # เรียกใช้ฟังก์ชันเพิ่มเวลาตั้งต้น
        self.initialize_time_entries()

        # ควบคุมภาษาและเสียง
        self.setup_volume_control()
        self.setup_language_control()
        
        self.update_language_ui("English")  # ตั้งค่า UI เริ่มต้น
    
    def initialize_time_entries(self):
        """สร้างเวลาตั้งต้น"""
        default_times = [("10", "30"), ("15", "00")]  # เวลาตั้งต้น
        for i, (hour, minute) in enumerate(default_times):
            self.set_time(hour, minute, f"Set Time {i + 1}")

    def setup_volume_control(self):
        """ตั้งค่าการควบคุมระดับเสียง"""
        volume_frame = tk.Frame(self, bg="white")
        volume_frame.place(x=50, y=50, width=350, height=50)

        self.volume_label = tk.Label(volume_frame, text="Volume", font=("PTT 45 Pride", 16), bg="white")
        self.volume_label.place(x=0, y=10, width=100, height=30)

        self.volume = tk.DoubleVar(value=50)
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

        self.language_var = tk.StringVar(value="Select")
        self.language_dropdown = ttk.Combobox(language_frame, textvariable=self.language_var, font=("PTT 45 Pride", 12), state="readonly")
        self.language_dropdown["values"] = ("English", "ภาษาไทย")
        self.language_dropdown.place(x=140, y=10, width=150, height=30)
        self.language_dropdown.bind("<<ComboboxSelected>>", self.change_language)

        self.translations = {
            "English": {"volume": "Volume", "language": "Language"},
            "ภาษาไทย": {"volume": "ระดับเสียง", "language": "ภาษา"},
        }

        self.update_language_ui("English")
    
    def update_volume_label(self, *args):
        self.volume_value_label.config(text=f"{int(self.volume.get())}%")
    
    def change_language(self, event):
        """เปลี่ยนภาษา UI"""
        selected_language = self.language_var.get()
        self.update_language_ui(selected_language)
        self.change_language_callback(selected_language)
        
    def update_language_ui(self, language):
        """อัปเดต UI ตามภาษา"""
        translations = self.translations.get(language, {})
        if translations:
            self.volume_label.config(text=translations.get("volume", "Volume"))
            self.language_label.config(text=translations.get("language", "Language"))

        # เปลี่ยนข้อความของ Set Time, Set, Skip
        for i, (hour_var, minute_var, label, set_button, skip_button) in enumerate(self.time_entries):
            new_label_text = f"ตั้งเวลา {i + 1}" if language == "ภาษาไทย" else f"Set Time {i + 1}"
            set_text = "ตั้ง" if language == "ภาษาไทย" else "Set"
            skip_text = "ข้าม" if language == "ภาษาไทย" else "Skip"

            label.config(text=new_label_text)
            set_button.config(text=set_text)
            skip_button.config(text=skip_text)

            self.time_entries[i] = (hour_var, minute_var, label, set_button, skip_button)

        # เปลี่ยนปุ่ม Add Time
        self.add_time_button.config(text="เพิ่มเวลา" if language == "ภาษาไทย" else "+ Add Time")
        
            
    def set_time(self, hour, minute, label_text, set_text=None, skip_text=None):
        """สร้างอินพุตเวลา และเพิ่มเข้าไปใน UI"""
        y_offset = 200 + len(self.time_entries) * 60
        time_frame = tk.Frame(self, bg="white")
        time_frame.place(x=50, y=y_offset, width=550, height=60)

        label = tk.Label(time_frame, text=label_text, font=("Arial", 14), bg="white")
        label.place(x=0, y=10, width=100, height=30)

        hour_var = tk.StringVar(value=hour)
        minute_var = tk.StringVar(value=minute)

        ttk.Combobox(time_frame, textvariable=hour_var, values=[f"{i:02d}" for i in range(24)], state="readonly").place(x=120, y=10, width=60, height=30)
        ttk.Combobox(time_frame, textvariable=minute_var, values=[f"{i:02d}" for i in range(60)], state="readonly").place(x=190, y=10, width=60, height=30)

        # 🔹 ตรวจสอบให้แน่ใจว่า language_var ถูกสร้างแล้ว
        if hasattr(self, "language_var"):
            current_language = self.language_var.get()
        else:
            current_language = "English"  # ค่าเริ่มต้นถ้าไม่มี language_var

        # ตั้งค่าปุ่ม Set และ Skip ตามภาษา
        if set_text is None:
            set_text = "ตั้ง" if current_language == "ภาษาไทย" else "Set"
        if skip_text is None:
            skip_text = "ข้าม" if current_language == "ภาษาไทย" else "Skip"

        set_button = tk.Button(time_frame, text=set_text, font=("Arial", 10), command=lambda: self.start_check_time(hour_var, minute_var, label_text))
        set_button.place(x=270, y=10, width=70, height=30)

        skip_button = tk.Button(time_frame, text=skip_text, font=("Arial", 10), command=lambda: self.skip_time(label_text))
        skip_button.place(x=350, y=10, width=70, height=30)

        self.time_entries.append((hour_var, minute_var, label, set_button, skip_button))
        self.stop_flags[label_text] = False
        self.start_check_time(hour_var, minute_var, label_text)  # เริ่มตรวจสอบเวลาทันทีที่สร้าง



    def start_check_time(self, hour_var, minute_var, label_text):
        """เริ่มเฝ้าตรวจสอบเวลา และแจ้งเตือนเมื่อถึงเวลา"""
        print(f"{label_text} updated to: {hour_var.get()}:{minute_var.get()}")
        
        def check_time():
            while not self.stop_flags.get(label_text, False):  # หยุดเมื่อกด Skip
                current_time = time.strftime("%H:%M")
                if current_time == f"{hour_var.get()}:{minute_var.get()}" and not self.stop_flags.get(label_text, False):
                    self.play_notification_sound()  # เล่นเสียงแจ้งเตือน
                    show_popup(50)  # แสดง popup
                    break
                time.sleep(1)

        threading.Thread(target=check_time, daemon=True).start()

    def skip_time(self, label_text):
        """ข้ามเวลา (Skip) ที่เลือก และหยุดการแจ้งเตือน"""
        self.stop_flags[label_text] = True
        print(f"{label_text} skipped. No popup will appear.")

    def add_time_set(self):
        """เพิ่มเวลาตั้งใหม่ (สูงสุด 12 ครั้ง)"""
        if len(self.time_entries) >= self.max_time_entries:
            print("Cannot add more than 12 time entries.")
            return
        
        # ตรวจสอบภาษาปัจจุบัน
        current_language = self.language_var.get()
        new_time_label = f"ตั้งเวลา {len(self.time_entries) + 1}" if current_language == "ภาษาไทย" else f"Set Time {len(self.time_entries) + 1}"

        # เพิ่มเวลาตั้งใหม่
        self.set_time("00", "00", new_time_label)


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