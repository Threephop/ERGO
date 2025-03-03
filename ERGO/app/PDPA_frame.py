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
        pdpa_file_path = os.path.join(os.path.dirname(__file__), "text/pdpa.txt")
        try:
            with open(pdpa_file_path, "r", encoding="utf-8") as file:
                pdpa_content = file.read()
            
            # ใช้ Regular Expression เพื่อจับตัวเลขข้อ + เนื้อหาไว้ด้วยกัน
            check_texts = re.findall(r'(\d+\.\s.*?)(?=\n\d+\.|\Z)', pdpa_content, re.DOTALL)
        except FileNotFoundError:
            check_texts = ["ไม่สามารถโหลดเนื้อหา PDPA ได้ กรุณาตรวจสอบไฟล์ pdpa.txt"]

        # เพิ่ม CheckBox และ Label
        self.check_vars = []
        self.check_boxes = []

        for i, text in enumerate(check_texts):
            var = ctk.BooleanVar()
            self.check_vars.append(var)

            # สร้าง Frame ย่อยสำหรับวาง CheckBox และข้อความให้ชิดกัน
            item_frame = ctk.CTkFrame(check_frame, fg_color="white")
            item_frame.grid(row=i, column=0, sticky="w", padx=5, pady=5)

            # สร้าง CheckBox
            check_box = ctk.CTkCheckBox(item_frame, text="", variable=var, 
                                        width=20, height=40, checkbox_width=20, checkbox_height=20,
                                        fg_color="gray")  # ตั้งค่าเริ่มต้นเป็นสีเทา
            check_box.pack(side="left", padx=(0, 5))

            # บันทึก CheckBox ไว้ในรายการ
            self.check_boxes.append(check_box)

            # ฟังก์ชันเปลี่ยนสี Checkbox เป็นสีเขียวเมื่อเลือก
            def update_checkbox_color(var=var, checkbox=check_box):
                if var.get():
                    checkbox.configure(fg_color="green")  # เปลี่ยนเป็นสีเขียวเมื่อถูกติ๊ก
                else:
                    checkbox.configure(fg_color="gray")  # สีเริ่มต้น

            # กำหนดให้ CheckBox เรียกฟังก์ชัน update_checkbox_color ทุกครั้งที่มีการกด
            check_box.configure(command=lambda v=var, c=check_box: update_checkbox_color(v, c))

            # สร้าง Label อยู่ใน item_frame เดียวกับ CheckBox
            label = ctk.CTkLabel(item_frame, text=text, font=("PTT 45 Pride", 16), text_color="black", fg_color="white",
                                 wraplength=700, width=700, justify="left", anchor="w")
            label.pack(side="left")

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

        self.transient(parent)
        self.grab_set()

    def check_accepted(self):
        if all(var.get() for var in self.check_vars):
            self.destroy()
        else:
            messagebox.showwarning("คำเตือน", "กรุณาอ่านและเลือกให้ครบ")

    # ฟังก์ชันเลือกทั้งหมด
    def select_all(self):
        for var, checkbox in zip(self.check_vars, self.check_boxes):
            var.set(True)
            checkbox.configure(fg_color="green")  # เปลี่ยนเป็นสีเขียว

    # ฟังก์ชันยกเลิกการเลือกทั้งหมด
    def deselect_all(self):
        for var, checkbox in zip(self.check_vars, self.check_boxes):
            var.set(False)
            checkbox.configure(fg_color="gray")  # กลับเป็นสีเทา
