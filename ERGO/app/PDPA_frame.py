import customtkinter as ctk
from tkinter import messagebox
import webbrowser
import os
import re

class PopupFrame(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("PDPA")
        self.geometry("850x700")
        self.configure(fg_color="white")
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")
        self.wm_iconbitmap(os.path.join(self.icon_dir, "GODJI-Action_200113_0008.ico"))

        # กำหนดตำแหน่งหน้าต่างกลางจอ
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width, window_height = 850, 700
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        ctk.CTkLabel(self, text="ข้อตกลง", font=("PTT 45 Pride", 16), fg_color="transparent").pack(pady=10)

        # สร้าง Canvas และ Scrollbar
        frame_canvas = ctk.CTkFrame(self, fg_color="white")
        frame_canvas.pack(pady=(10, 100), padx=3, fill="both", expand=True)

        canvas = ctk.CTkCanvas(frame_canvas, bg="white", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar_canvas = ctk.CTkScrollbar(frame_canvas, orientation="vertical", command=canvas.yview)
        scrollbar_canvas.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar_canvas.set)

        check_frame = ctk.CTkFrame(canvas, fg_color="white")
        canvas.create_window((0, 0), window=check_frame, anchor="nw", width=800)

        # โหลดข้อความจากไฟล์ pdpa.txt
        pdpa_file_path = os.path.join(os.path.dirname(__file__), "text\pdpa.txt")
        try:
            with open(pdpa_file_path, "r", encoding="utf-8") as file:
                pdpa_content = file.read()
            
            # ใช้ Regular Expression เพื่อแยกแต่ละข้อออกจากกันโดยใช้ตัวเลขลำดับ
            check_texts = re.split(r'(?=\d+\.\s)', pdpa_content.strip())  # แยกตามรูปแบบ "1. " "2. " "3. " เป็นต้น
            check_texts = [text.strip() for text in check_texts if text.strip()]  # ลบช่องว่างหน้า-หลัง
        except FileNotFoundError:
            check_texts = ["ไม่สามารถโหลดเนื้อหา PDPA ได้ กรุณาตรวจสอบไฟล์ pdpa.txt"]

        # เพิ่ม CheckBox และ Label
        self.check_vars = []
        for i, text in enumerate(check_texts):
            var = ctk.BooleanVar()
            self.check_vars.append(var)

            # CheckBox
            check_box = ctk.CTkCheckBox(check_frame, text="", variable=var, fg_color="white",
                                        width=20, height=40, checkbox_width=20, checkbox_height=20)
            check_box.grid(row=i, column=0, sticky="w", padx=(5, 10), pady=5)  # ปรับ padx ให้ Checkbox มีระยะพอดี

            # Label ที่ชิดซ้ายสุด
            label = ctk.CTkLabel(check_frame, text=text, font=("PTT 45 Pride", 16), text_color="black", fg_color="white",
                                wraplength=700, width=600, justify="left", anchor="w")  # ใช้ anchor="w" ให้ชิดซ้าย
            label.grid(row=i, column=1, sticky="w", padx=0, pady=5)  # ปรับให้ Label ตรงกับ CheckBox

        # ตั้งค่า column 1 (Label) ให้เป็นตัวหลักของข้อความ เพื่อให้ข้อความไม่ล้ำไปด้านขวา
        check_frame.grid_columnconfigure(1, weight=1)



        # ปุ่มเลือกทั้งหมด
        select_all_button = ctk.CTkButton(self, text="เลือกทั้งหมด", command=self.select_all,
                                          font=("PTT 45 Pride", 12), fg_color="#2ea6f4", text_color="white")
        select_all_button.place(x=250, y=600)

        # ปุ่มยกเลิกการเลือกทั้งหมด
        deselect_all_button = ctk.CTkButton(self, text="ยกเลิกการเลือกทั้งหมด", command=self.deselect_all,
                                            font=("PTT 45 Pride", 12), fg_color="#FF9800", text_color="white")
        deselect_all_button.place(x=400, y=600)

        # ปรับขนาด Canvas ตามเนื้อหา
        def update_scrollregion(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        check_frame.bind("<Configure>", update_scrollregion)

        # การเลื่อน Scrollbar ด้วยเมาส์
        def on_mouse_wheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        # เปิดลิงก์
        def open_link(event):
            webbrowser.open("https://pttpdpa.pttplc.com/")

        link_label = ctk.CTkLabel(self, text="อ่านเพิ่มเติมเกี่ยวกับนโยบายความเป็นส่วนตัวของเรา",
                                  text_color="blue", cursor="hand2",
                                  font=("PTT 45 Pride", 12), fg_color="white")
        link_label.pack()
        link_label.bind("<Button-1>", open_link)

        accept_button = ctk.CTkButton(self, text="ตกลง", command=self.check_accepted,
                                      font=("PTT 45 Pride", 12), fg_color="#4CAF50", text_color="white")
        accept_button.place(x=100, y=600)

        reject_button = ctk.CTkButton(self, text="ปฏิเสธ", command=self.destroy,
                                      font=("PTT 45 Pride", 12), fg_color="#FF5959", text_color="white")
        reject_button.place(x=550, y=600)

        # Disable parent interaction while popup is open
        self.transient(parent)
        self.grab_set()

    def check_accepted(self):
        if all(var.get() for var in self.check_vars):
            self.destroy()
        else:
            messagebox.showwarning("คำเตือน", "กรุณาอ่านและเลือกให้ครบ")

    # ฟังก์ชันเลือกทั้งหมด
    def select_all(self):
        for var in self.check_vars:
            var.set(True)

    # ฟังก์ชันยกเลิกการเลือกทั้งหมด
    def deselect_all(self):
        for var in self.check_vars:
            var.set(False)
