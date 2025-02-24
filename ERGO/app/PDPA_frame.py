import customtkinter as ctk
from tkinter import messagebox
import webbrowser
import os

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
        canvas.create_window((0, 0), window=check_frame, anchor="nw", width=1100)

        # ข้อความข้อตกลง
        check_texts = [
            "1. จุดประสงค์ของการจัดเก็บข้อมูล (Purpose of Data Collection)\n\n"
            "แอปพลิเคชันจะจัดเก็บและบันทึกวิดีโอที่ผู้ใช้ถ่ายทำผ่านแอป เพื่อให้สามารถแชร์และดูซ้ำได้ในกลุ่มแชทภายในแอป\n"
            "การจัดเก็บข้อมูลนี้มีวัตถุประสงค์เพื่อสนับสนุนประสบการณ์การใช้งาน และเพิ่มประสิทธิภาพในการสื่อสารระหว่างผู้ใช้\n",
            "2. การจัดเก็บและใช้ข้อมูล (Data Storage and Usage)\n\n"
            "ข้อมูลที่จัดเก็บประกอบด้วย วิดีโอที่ผู้ใช้บันทึกผ่านแอป รวมถึงข้อมูลวันที่และเวลาที่บันทึก\n"
            "การเก็บข้อมูลตำแหน่ง (Location) จะทำก็ต่อเมื่อได้รับความยินยอมจากผู้ใช้เท่านั้น\n",
            "3. สิทธิ์ของผู้ใช้ (User Rights)\n\n"
            "ผู้ใช้มีสิทธิ์ในการเข้าถึง แก้ไข หรือขอลบวิดีโอที่บันทึกไว้ในระบบของแอปได้ตลอดเวลา นอกจากนี้\n"
            "ผู้ใช้สามารถเพิกถอนความยินยอมในการเก็บข้อมูลส่วนบุคคลได้ทุกเมื่อผ่านการติดต่อ\n",
            "4. วิธีการจัดเก็บและระยะเวลาการเก็บข้อมูล (Data Storage and Retention Period)\n\n"
            "วิดีโอทั้งหมดที่บันทึกผ่านแอปจะถูกจัดเก็บในเซิร์ฟเวอร์ของแอปเป็นระยะเวลา 5 วัน\n"
            "หลังจากนั้นวิดีโอจะถูกลบโดยอัตโนมัติ\n",
            "5. การแชร์ข้อมูลกับบุคคลที่สาม (Data Sharing with Third Parties)\n\n"
            "แอปนี้จะไม่เผยแพร่หรือแบ่งปันวิดีโอที่บันทึกโดยผู้ใช้กับบุคคลภายนอกโดยไม่ได้รับความยินยอมล่วงหน้า\n"
            "ข้อมูลจะถูกจัดเก็บไว้ในระบบเซิร์ฟเวอร์ที่ปลอดภัยและมีการเข้ารหัสเพื่อป้องกันการเข้าถึงโดยไม่ได้รับอนุญาต\n",
            "6. การป้องกันความปลอดภัยของข้อมูล (Data Security)\n\n"
            "วิดีโอและข้อมูลเมตาที่จัดเก็บไว้ในระบบเซิร์ฟเวอร์ของแอปจะได้รับการเข้ารหัสเพื่อป้องกันการเข้าถึงโดยไม่ได้รับอนุญาต\n"
            "แอปนี้ใช้เทคโนโลยีป้องกันการโจมตีทางไซเบอร์และมาตรการความปลอดภัยที่ได้มาตรฐานสากล\n",
            "7. วิธีการขอความยินยอม (Consent Request Mechanism)\n\n"
            "แอปนี้มีการจัดเก็บวิดีโอที่บันทึกโดยผู้ใช้ เพื่อการจัดเก็บและการแชร์ในกลุ่มแชทภายในแอปเท่านั้น\n"
            "วิดีโอจะถูกจัดเก็บเป็นระยะเวลา 5 วัน และจะถูกลบโดยอัตโนมัติหากเกินระยะเวลาดังกล่าว \n"
            "คุณมีสิทธิ์ในการลบวิดีโอหรือเพิกถอนความยินยอมได้ตลอดเวลา\n"
            "อ่านเพิ่มเติมเกี่ยวกับนโยบายความเป็นส่วนตัวของเรา [ลิงก์นโยบายความเป็นส่วนตัว]\n"
            "กด (ยอมรับ) เพื่อยอมรับเงื่อนไขการเก็บข้อมูลส่วนบุคคล\n",
            "8. การติดต่อสอบถาม (Contact Information)\n\n"
            "หากต้องการสอบถามเพิ่มเติมเกี่ยวกับนโยบายความเป็นส่วนตัว หรือขอใช้สิทธิ์ตาม PDPA โปรดติดต่อ\n"
            "0-3849-3720 ทีมงานของเราพร้อมให้บริการและดูแลข้อมูลส่วนบุคคลของคุณอย่างเต็มความสามารถ\n"
        ]

        # เพิ่ม CheckBox และ Label แยกกันเพื่อให้ข้อความขึ้นบรรทัดใหม่ได้
        self.check_vars = []
        for i, text in enumerate(check_texts):
            var = ctk.BooleanVar()
            self.check_vars.append(var)

            check_box = ctk.CTkCheckBox(check_frame, text="", variable=var, fg_color="white",
                width=20, height=40, checkbox_width=20, checkbox_height=20)

            check_box.grid(row=i, column=0, sticky="nw", padx=10, pady=5)

            label = ctk.CTkLabel(check_frame, text=text, font=("PTT 45 Pride", 16), fg_color="white",
                wraplength=800,  width=600, justify="left")  # ปรับ wraplength และ width
            label.grid(row=i, column=1, sticky="w", padx=5, pady=5)

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

