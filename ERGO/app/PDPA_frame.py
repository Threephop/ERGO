import customtkinter as ctk
from tkinter import messagebox
import webbrowser
import os
import re
import subprocess
import sys

class PopupFrame(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("PDPA")
        self.geometry("850x700")
        self.configure(fg_color="white")
        
        # ให้ปุ่ม X ทำงานเหมือนปุ่ม "ปฏิเสธ"
        self.protocol("WM_DELETE_WINDOW", self.open_login)
        
        # กำหนดตำแหน่งหน้าต่างกลางจอ
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width, window_height = 850, 700
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        ctk.CTkLabel(self, text="ข้อตกลง", font=("PTT 45 Pride", 22), fg_color="transparent").pack(pady=10)

        # สร้าง Canvas และ Scrollbar
        frame_canvas = ctk.CTkFrame(self, fg_color="white")
        frame_canvas.pack(pady=(10, 100), padx=3, fill="both", expand=True)

        canvas = ctk.CTkCanvas(frame_canvas, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar_canvas = ctk.CTkScrollbar(frame_canvas, orientation="vertical", command=canvas.yview)
        scrollbar_canvas = scrollbar_canvas = ctk.CTkScrollbar(frame_canvas, orientation="vertical", command=canvas.yview)
        scrollbar_canvas.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar_canvas.set)

        self.check_frame = ctk.CTkFrame(canvas, fg_color="white")
        canvas.create_window((0, 0), window=self.check_frame, anchor="nw", width=1000)
        
        # โหลดข้อความจากไฟล์ pdpa.txt
        pdpa_file_path = os.path.join(os.path.dirname(__file__), "text/pdpa.txt")
        try:
            with open(pdpa_file_path, "r", encoding="utf-8") as file:
                pdpa_content = file.read()

            check_texts = re.findall(r'(\d+\.\s.*?)(?=\n\d+\.|\Z)', pdpa_content, re.DOTALL)
        except FileNotFoundError:
            check_texts = ["ไม่สามารถโหลดเนื้อหา PDPA ได้ กรุณาตรวจสอบไฟล์ pdpa.txt"]

        self.check_vars = []
        self.check_boxes = []

        for i, text in enumerate(check_texts):
            var = ctk.BooleanVar()
            self.check_vars.append(var)
            # สร้าง Frame ย่อยสำหรับวาง CheckBox และข้อความให้ชิดกัน
            item_frame = ctk.CTkFrame(self.check_frame, fg_color="white")
            item_frame.grid(row=i, column=0, sticky="w", padx=5, pady=5)

            checkbox = ctk.CTkCheckBox(item_frame, variable=var, text="", fg_color="gray", hover_color="green")
            checkbox.pack(side="left", padx=(0, 5))

            label = ctk.CTkLabel(
                item_frame, 
                text=text, 
                fg_color="white", 
                justify="left", 
                wraplength=700,
                font=("PTT 45 Pride", 16)  # เพิ่ม font และขนาดที่นี่
            )

            label.pack(side="left")

        self.check_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        ctk.CTkButton(self, text="เลือกทั้งหมด", command=self.select_all, fg_color="#2ea6f4").place(x=250, y=600)
        ctk.CTkButton(self, text="ยกเลิกทั้งหมด", command=self.deselect_all, fg_color="#FF9800").place(x=400, y=600)
        ctk.CTkButton(self, text="ตกลง", command=self.check_accepted, fg_color="#4CAF50").place(x=100, y=600)
        ctk.CTkButton(self, text="ปฏิเสธ", command=self.open_login, fg_color="#FF5959").place(x=550, y=600)

        link_label = ctk.CTkLabel(self, text="อ่านเพิ่มเติมเกี่ยวกับนโยบายความเป็นส่วนตัวของเรา",
                                  text_color="blue", cursor="hand2",
                                  fg_color="white")
        link_label.pack()
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://pttpdpa.pttplc.com/"))

        self.transient(parent)
        self.grab_set()

    def check_accepted(self):
        if all(var.get() for var in self.check_vars):
            self.destroy()
        else:
            messagebox.showwarning("คำเตือน", "กรุณายอมรับเงื่อนไขทุกข้อก่อนตกลง")

    def select_all(self):
        for var, item_frame in zip(self.check_vars, self.check_frame.winfo_children()):
            var.set(True)
            checkbox = item_frame.winfo_children()[0]  # checkbox เป็น widget ตัวแรกของ item_frame
            checkbox.configure(fg_color="green")

    def deselect_all(self):
        for var, item_frame in zip(self.check_vars, self.check_frame.winfo_children()):
            var.set(False)
            checkbox = item_frame.winfo_children()[0]
            checkbox.configure(fg_color="gray")

    
    def close_app(self):
        """ ปิดแอปและเปิด Login ใหม่ """
        print("🚪 close_app() ถูกเรียกแล้ว!")
        if self.master.winfo_exists():
            print("🛑 ปิดหน้าต่างหลัก")
            self.master.quit()
            self.master.destroy()

        print("🔄 เรียก open_login()")
        self.open_login()
    
    def open_login(self):
        """ เปิดหน้าต่าง Login ใหม่ """
        try:
            # หาพาธของโฟลเดอร์หลัก (ตำแหน่งของไฟล์ปัจจุบัน)
            base_dir = os.path.dirname(os.path.abspath(__file__))

            # ถ้าพาธของไฟล์ปัจจุบัน **ลงท้ายด้วย** "app" อยู่แล้ว ไม่ต้องเพิ่ม "app" ซ้ำ
            if base_dir.endswith("app"):
                script_path = os.path.join(base_dir, "Login.py")
            else:
                script_path = os.path.join(base_dir, "app", "Login.py")  # ไปที่โฟลเดอร์ "app"

            # ตรวจสอบว่า Login.py มีอยู่จริงหรือไม่
            if not os.path.exists(script_path):
                messagebox.showerror("Error", f"Cannot find Login.py at {script_path}")
                return

            # เปิด Login.py ใหม่
            python_executable = sys.executable  # ใช้ Python ที่กำลังรันอยู่
            subprocess.Popen([python_executable, script_path], shell=True)

            # ปิดโปรแกรมเก่า
            sys.exit()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restart Login: {e}")
