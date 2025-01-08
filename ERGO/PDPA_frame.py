import tkinter as tk

class PopupFrame(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("PDPA")
        self.geometry("400x300")
        self.configure(bg="white")

        # เนื้อหาใน Popup
        tk.Label(
            self,
            text="ข้อตกลง",
            font=("Arial", 16),
            bg="white"
        ).pack(pady=10)

        # สร้าง Frame สำหรับ Text และ Scrollbar
        text_frame = tk.Frame(self, bg="white")
        text_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # เพิ่ม Text Widget สำหรับแสดงข้อความ
        text_widget = tk.Text(
            text_frame,
            wrap="word",   # ตัดคำเมื่อข้อความยาวเกินขอบ
            font=("Arial", 12),
            bg="white",
            relief="flat",
        )
        text_widget.pack(side="left", fill="both", expand=True)

        # เพิ่ม Scrollbar
        scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")

        # เชื่อม Scrollbar กับ Text Widget
        text_widget.config(yscrollcommand=scrollbar.set)

        # ข้อความยาว ๆ
        long_text = (
            "1. จุดประสงค์ของการจัดเก็บข้อมูล (Purpose of Data Collection)\n\n"
            "The main purpose of collecting and storing data is to enhance user well-being "
            "by providing reminders to take breaks, adjust posture, and engage in physical activities. "
            "Please follow the instructions displayed on your screen to maintain a healthy work routine.\n\n"
            "2. การจัดเก็บและใช้ข้อมูล (Data Storage and Usage)\n\n"
            "Your data will be securely stored and used exclusively for the purpose of improving your health "
            "and productivity at the workplace."
        )
        text_widget.insert("1.0", long_text)
        text_widget.config(state="disabled")  # ปิดการแก้ไขข้อความ

        # ปุ่มปิด Popup
        tk.Button(
            self,
            text="Close",
            command=self.destroy,
            font=("Arial", 12),
            bg="#221551",
            fg="white",
            relief="flat"
        ).pack(pady=10)

        # Disable parent interaction while popup is open
        self.transient(parent)
        self.grab_set()

# ทดสอบ PopupFrame
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # ซ่อนหน้าต่างหลัก
    popup = PopupFrame(root)
