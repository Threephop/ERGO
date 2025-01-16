import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk  # นำเข้าโมดูลที่จำเป็นสำหรับการปรับขนาดภาพ
import os

class ProfileFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#2E004F")

        # กำหนดไดเรกทอรีสำหรับไอคอน
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")

        # โหลดภาพโปรไฟล์
        try:
            profile_image_path = os.path.join(self.icon_dir, "profile.png")
            if not os.path.exists(profile_image_path):
                raise FileNotFoundError(f"ไม่พบไฟล์ภาพโปรไฟล์ที่: {profile_image_path}")
            
            # เปิดภาพด้วย PIL
            image = Image.open(profile_image_path)
            
            # ปรับขนาดภาพให้พอดีกับขนาดของ Canvas โดยใช้วิธีการใหม่
            image = image.resize((100, 100), Image.Resampling.LANCZOS)
            self.profile_image = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลด profile.png: {e}")
            raise

        # แสดงภาพโปรไฟล์
        canvas = tk.Canvas(self, width=100, height=100, bg="#2E004F", highlightthickness=0)
        canvas.create_image(50, 50, image=self.profile_image)
        canvas.place(relx=0.4, rely=0.2, anchor="center")  # ปรับตำแหน่งกลางกรอบ

        # ชื่อผู้ใช้
        name_label = tk.Label(self, text="นายธีรพ ธิวะโต", font=("Arial", 16), bg="white")
        name_label.place(relx=0.4, rely=0.35, anchor="center")  # ปรับตำแหน่งใต้ภาพโปรไฟล์

        # จำนวนการใช้งาน
        usage_label = tk.Label(self, text="จำนวนครั้งที่ใช้งาน", font=("Arial", 14), bg="white")
        usage_label.place(relx=0.4, rely=0.45, anchor="center")  # ปรับตำแหน่งใต้ชื่อ

        count_label = tk.Label(self, text="1", font=("Arial", 30), bg="white")
        count_label.place(relx=0.4, rely=0.55, anchor="center")  # ปรับตำแหน่งใต้จำนวนครั้ง

        # ปุ่มออกจากระบบ
        logout_button = tk.Button(self, text="Logout", font=("Arial", 12), bg="#2E004F", fg="red", borderwidth=0, command=self.logout)
        logout_button.place(relx=0.8, rely=0.05, anchor="ne")  # ปรับตำแหน่งมุมขวาบน

    def logout(self):
        print("คลิกออกจากระบบ")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Profile Frame")

    frame = ProfileFrame(root)
    frame.pack(fill="both", expand=True)

    root.mainloop()
