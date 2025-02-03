import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk  # นำเข้าโมดูลที่จำเป็นสำหรับการปรับขนาดภาพ
import os
from tkinter import messagebox

class ProfileFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        # self.root = root  # เก็บตัวแปร root ไว้ใน self

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
        canvas = tk.Canvas(self, width=100, height=100, bg="#ffffff", highlightthickness=0)
        canvas.create_image(50, 50, image=self.profile_image)
        canvas.place(relx=0.4, rely=0.2, anchor="center")  # ปรับตำแหน่งกลางกรอบ

        # ชื่อผู้ใช้
        name_label = tk.Label(self, text="นายธีภพ ธิวะโต", font=("Arial", 16), bg="white")
        name_label.place(relx=0.4, rely=0.35, anchor="center")  # ปรับตำแหน่งใต้ภาพโปรไฟล์

        # จำนวนการใช้งาน
        usage_label = tk.Label(self, text="จำนวนครั้งที่ใช้งาน", font=("Arial", 14), bg="white")
        usage_label.place(relx=0.4, rely=0.45, anchor="center")  # ปรับตำแหน่งใต้ชื่อ

        count_label = tk.Label(self, text="1", font=("Arial", 30), bg="white")
        count_label.place(relx=0.4, rely=0.55, anchor="center")  # ปรับตำแหน่งใต้จำนวนครั้ง

        # ปุ่มออกจากระบบ
        logout_button = tk.Button(self, text="Logout", font=("Arial", 12), bg="#ffffff", fg="red", borderwidth=0, command=self.logout)
        logout_button.place(relx=0.8, rely=0.05, anchor="ne")  # ปรับตำแหน่งมุมขวาบน

    def logout(self):
            # ปิดการเชื่อมต่อ หรือทำการล็อกเอาท์จากระบบ (ตามที่ต้องการ)
            print("คลิกออกจากระบบ")
    # def logout(self):
    #     try:
    #         # ปิดการเชื่อมต่อ หรือทำการล็อกเอาท์จากระบบ (ตามที่ต้องการ)
    #         print("คลิกออกจากระบบ")

    #         # ทำการซ่อนหน้าต่าง (ล็อกเอาท์)
    #         self.root.withdraw()

    #         # เรียกหน้าต่าง login ขึ้นมาใหม่
    #         self.root.after(100, lambda: self.show_login_window())  # ใช้ after เพื่อเรียกการแสดงหน้าต่าง login ใหม่

    #     except Exception as e:
    #         messagebox.showerror("Error", f"An error occurred during logout: {e}")
            
    # # ฟังก์ชันในการแสดงหน้าต่าง login
    # def show_login_window(self):
    #     # คืนค่าให้ root (login window) กลับมาปรากฏ
    #     self.root.deiconify()

    #     # รีเซ็ตหรือทำให้พร้อมใช้งานตามที่ต้องการ (เช่น เคลียร์ข้อมูลในฟอร์ม login)
    #     self.clear_login_form()

    # def clear_login_form(self):
    #     # ตัวอย่างการเคลียร์ฟอร์ม login
    #     # ลบข้อความจากช่องกรอกข้อมูล
    #     self.username_entry.delete(0, 'end')
    #     self.password_entry.delete(0, 'end')


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Profile Frame")

    frame = ProfileFrame(root, root)  # ส่ง root ไปให้ ProfileFrame
    frame.pack(fill="both", expand=True)

    root.mainloop()
