import tkinter as tk
import webbrowser
from tkinter import messagebox
from tkinter import *

class PopupFrame(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("PDPA")
        self.geometry("850x700")
        self.configure(bg="white")

        # คำนวณตำแหน่งตรงกลางจอ
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 850
        window_height = 700
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        # เนื้อหาใน Popup
        tk.Label(
            self,
            text="ข้อตกลง",
            font=("PTT 45 Pride", 16),
            bg="white"
        ).pack(pady=10)

                # สร้าง Frame สำหรับ Canvas และ Scrollbar
        frame_canvas = tk.Frame(self, bg="white")
        frame_canvas.pack(pady=(10, 100), padx=10, fill="both", expand=True)

        # สร้าง Canvas สำหรับ Checkboxes
        canvas = tk.Canvas(frame_canvas, bg="white")
        canvas.pack(side="left", fill="both", expand=True)

        # สร้าง Scrollbar สำหรับ Canvas
        scrollbar_canvas = tk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
        scrollbar_canvas.pack(side="right", fill="y")  # เลื่อนมาทางด้านขวา
        canvas.config(yscrollcommand=scrollbar_canvas.set)

        # สร้าง Frame ภายใน Canvas
        check_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=check_frame, anchor="nw")

        # เพิ่ม Checkboxes ลงใน Frame ภายใน Canvas
        self.chk8 = BooleanVar()
        self.chk7 = BooleanVar()
        self.chk6 = BooleanVar()
        self.chk5 = BooleanVar()
        self.chk4 = BooleanVar()
        self.chk3 = BooleanVar()
        self.chk2 = BooleanVar()
        self.chk1 = BooleanVar()

        Checkbutton(check_frame, text="1. จุดประสงค์ของการจัดเก็บข้อมูล (Purpose of Data Collection)\n\n"
            "แอปพลิเคชันจะจัดเก็บและบันทึกวิดีโอที่ผู้ใช้ถ่ายทำผ่านแอป เพื่อให้สามารถแชร์และดูซ้ำได้ในกลุ่มแชทภายในแอป\n"
            "การจัดเก็บข้อมูลนี้มีวัตถุประสงค์เพื่อสนับสนุนประสบการณ์การใช้งาน และเพิ่มประสิทธิภาพในการสื่อสารระหว่างผู้ใช้\n", 
            variable=self.chk1, anchor="w", justify="left", font=("PTT 45 Pride", 12), bg="white").grid(row=0, sticky="w", padx=10, pady=5)

        Checkbutton(check_frame, text="2. การจัดเก็บและใช้ข้อมูล (Data Storage and Usage)\n"
            "ข้อมูลที่จัดเก็บประกอบด้วย วิดีโอที่ผู้ใช้บันทึกผ่านแอป รวมถึงข้อมูลวันที่และเวลาที่บันทึก\n"
            "การเก็บข้อมูลตำแหน่ง (Location) จะทำก็ต่อเมื่อได้รับความยินยอมจากผู้ใช้เท่านั้น\n", 
            variable=self.chk2, anchor="w", justify="left", font=("PTT 45 Pride", 12), bg="white").grid(row=1, sticky="w", padx=10, pady=5)

        Checkbutton(check_frame, text="3. สิทธิ์ของผู้ใช้ (User Rights)\n"
            "ผู้ใช้มีสิทธิ์ในการเข้าถึง แก้ไข หรือขอลบวิดีโอที่บันทึกไว้ในระบบของแอปได้ตลอดเวลา นอกจากนี้\n"
            "ผู้ใช้สามารถเพิกถอนความยินยอมในการเก็บข้อมูลส่วนบุคคลได้ทุกเมื่อผ่านการติดต่อ\n", 
            variable=self.chk3, anchor="w", justify="left", font=("PTT 45 Pride", 12), bg="white").grid(row=2, sticky="w", padx=10, pady=5)

        Checkbutton(check_frame, text="4. วิธีการจัดเก็บและระยะเวลาการเก็บข้อมูล (Data Storage and Retention Period)\n\n"
            "วิดีโอทั้งหมดที่บันทึกผ่านแอปจะถูกจัดเก็บในเซิร์ฟเวอร์ของแอปเป็นระยะเวลา 5 วัน\n"
            "หลังจากนั้นวิดีโอจะถูกลบโดยอัตโนมัติ\n", 
            variable=self.chk4, anchor="w", justify="left", font=("PTT 45 Pride", 12), bg="white").grid(row=3, sticky="w", padx=10, pady=5)

        Checkbutton(check_frame, text="5. การแชร์ข้อมูลกับบุคคลที่สาม (Data Sharing with Third Parties)\n\n"
            "แอปนี้จะไม่เผยแพร่หรือแบ่งปันวิดีโอที่บันทึกโดยผู้ใช้กับบุคคลภายนอกโดยไม่ได้รับความยินยอมล่วงหน้า\n"
            "ข้อมูลจะถูกจัดเก็บไว้ในระบบเซิร์ฟเวอร์ที่ปลอดภัยและมีการเข้ารหัสเพื่อป้องกันการเข้าถึงโดยไม่ได้รับอนุญาต\n", 
            variable=self.chk5, anchor="w", justify="left", font=("PTT 45 Pride", 12), bg="white").grid(row=4, sticky="w", padx=10, pady=5)

        Checkbutton(check_frame, text="6. การป้องกันความปลอดภัยของข้อมูล (Data Security)\n\n"
            "วิดีโอและข้อมูลเมตาที่จัดเก็บไว้ในระบบเซิร์ฟเวอร์ของแอปจะได้รับการเข้ารหัสเพื่อป้องกันการเข้าถึงโดยไม่ได้รับอนุญาต\n"
            "แอปนี้ใช้เทคโนโลยีป้องกันการโจมตีทางไซเบอร์และมาตรการความปลอดภัยที่ได้มาตรฐานสากล\n",
            variable=self.chk6, anchor="w", justify="left", font=("PTT 45 Pride", 12), bg="white").grid(row=5, sticky="w", padx=10, pady=5)

        Checkbutton(check_frame, text="7. วิธีการขอความยินยอม (Consent Request Mechanism)\n\n"
            "แอปนี้มีการจัดเก็บวิดีโอที่บันทึกโดยผู้ใช้ เพื่อการจัดเก็บและการแชร์ในกลุ่มแชทภายในแอปเท่านั้น\n"
            "วิดีโอจะถูกจัดเก็บเป็นระยะเวลา 5 วัน และจะถูกลบโดยอัตโนมัติหากเกินระยะเวลาดังกล่าว \n"
            "คุณมีสิทธิ์ในการลบวิดีโอหรือเพิกถอนความยินยอมได้ตลอดเวลา\n"
            "อ่านเพิ่มเติมเกี่ยวกับนโยบายความเป็นส่วนตัวของเรา [ลิงก์นโยบายความเป็นส่วนตัว]\n"
            "กด (ยอมรับ) เพื่อยอมรับเงื่อนไขการเก็บข้อมูลส่วนบุคคล\n",
            variable=self.chk7, anchor="w", justify="left", font=("PTT 45 Pride", 12), bg="white").grid(row=6, sticky="w", padx=10, pady=5)

        Checkbutton(check_frame, text="8. การติดต่อสอบถาม (Contact Information)\n\n"
            "หากต้องการสอบถามเพิ่มเติมเกี่ยวกับนโยบายความเป็นส่วนตัว หรือขอใช้สิทธิ์ตาม PDPA โปรดติดต่อ\n"
            "0-3849-3720 ทีมงานของเราพร้อมให้บริการและดูแลข้อมูลส่วนบุคคลของคุณอย่างเต็มความสามารถ\n", 
            variable=self.chk8, anchor="w", justify="left", font=("PTT 45 Pride", 12), bg="white").grid(row=7, sticky="w", padx=10, pady=5)


        # ปรับขนาดของ Canvas ให้พอดีกับจำนวน Checkboxes
        def update_scrollregion(event=None):
            canvas.config(scrollregion=canvas.bbox("all"))
            
        check_frame.bind("<Configure>", update_scrollregion)
        
        def on_mouse_wheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")
            
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)


        # เปิดลิงก์
        def open_link(event):
            webbrowser.open("https://pttpdpa.pttplc.com/")

        link_label = tk.Label(self, text="อ่านเพิ่มเติมเกี่ยวกับนโยบายความเป็นส่วนตัวของเรา", fg="blue", cursor="hand2", font=("PTT 45 Pride", 12), bg="white")
        link_label.pack()
        link_label.bind("<Button-1>", open_link)

        # ปุ่มตกลงและปฏิเสธ
        accept_button = tk.Button(
            self,
            text="ตกลง",
            command=self.check_accepted,
            font=("PTT 45 Pride", 12),
            bg="#787878",
            fg="white",
            relief="flat",
        )
        accept_button.place(x=350, y=600)

        reject_button = tk.Button(
            self,
            text="ปฏิเสธ",
            command=self.destroy,
            font=("PTT 45 Pride", 12),
            bg="#FF5959",
            fg="white",
            relief="flat",
        )
        reject_button.place(x=450, y=600)

        # Disable parent interaction while popup is open
        self.transient(parent)
        self.grab_set()

    def check_accepted(self):
        if self.chk1.get() and self.chk2.get() and self.chk3.get() and self.chk4.get() and self.chk5.get() and self.chk6.get() and self.chk7.get() and self.chk8.get():
            self.destroy()
        else:
            messagebox.showwarning("คำเตือน", "กรุณาอ่านและเลือกให้ครบ")

# ทดสอบ PopupFrame
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # ซ่อนหน้าต่างหลัก
    popup = PopupFrame(root)
    root.mainloop()
