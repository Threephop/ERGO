import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import requests

class ProfileFrame(tk.Frame):
    def __init__(self, parent,user_email):
        super().__init__(parent, bg="white")

        # กำหนดไดเรกทอรีสำหรับไอคอน
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")
        self.default_profile_path = os.path.join(self.icon_dir, "profile.png")

        # โหลดภาพโปรไฟล์เริ่มต้น
        self.profile_image = None
        self.load_profile_image(self.default_profile_path)

        # Canvas แสดงภาพโปรไฟล์ (คลิกเพื่อเปลี่ยน)
        self.canvas = tk.Canvas(self, width=100, height=100, bg="#ffffff", highlightthickness=0)
        self.profile_pic = self.canvas.create_image(50, 50, image=self.profile_image, tags="profile_pic")
        self.canvas.place(relx=0.4, rely=0.2, anchor="center")
        self.canvas.tag_bind("profile_pic", "<Button-1>", self.change_profile_picture)  # คลิกเปลี่ยนรูป

        self.user_email = user_email
        
        # 🔹 ดึงรายชื่อ users จาก API
        response = requests.get("http://127.0.0.1:8000/users")
        if response.status_code == 200:
            try:
                data = response.json()

                # พิมพ์ข้อมูลที่ได้รับจาก API
                print("Users list from API:", data)

                # ตรวจสอบว่า 'users' มีอยู่ และเป็น list
                users_list = data.get('users', [])
                if isinstance(users_list, list):
                    # 🔹 ค้นหา user ตาม email
                    user_data = next((user for user in users_list if user.get("email") == self.user_email), None)

                    if user_data:
                        self.username = user_data.get("username", "Unknown User")
                    else:
                        self.username = "Unknown User"

                    print(f"🔹 Username: {self.username}")
                else:
                    print("⚠️ Error: 'users' is not a list!")
                    self.username = "Unknown User"
            except ValueError as e:
                print(f"⚠️ Error: Failed to parse response as JSON - {e}")
                self.username = "Unknown User"
        else:
            print(f"⚠️ API Error: {response.status_code}")
            self.username = "Unknown User"

        # ชื่อผู้ใช้
        self.name_label = tk.Label(self, text=self.username, font=("Arial", 16), bg="white", cursor="hand2")
        self.name_label.place(relx=0.4, rely=0.35, anchor="center")
        self.name_label.bind("<Button-1>", self.change_name)  # คลิกที่ชื่อเพื่อเปลี่ยนชื่อ

        # ปุ่มออกจากระบบ
        self.logout_button = tk.Button(self, text="Logout", font=("Arial", 12), bg="#ff0000", fg="white",
                                       borderwidth=0, command=self.logout)
        self.logout_button.place(relx=0.8, rely=0.05, anchor="ne")

    
    def load_profile_image(self, image_path):
        """ โหลดและปรับขนาดภาพโปรไฟล์ """
        try:
            if not os.path.exists(image_path):
                image_path = self.default_profile_path  # ใช้ค่าเริ่มต้นถ้าไม่มีไฟล์

            image = Image.open(image_path)
            image = image.resize((100, 100), Image.Resampling.LANCZOS)
            self.profile_image = ImageTk.PhotoImage(image)

        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลดภาพ: {e}")
            messagebox.showerror("Error", "ไม่สามารถโหลดรูปภาพได้")

    def change_profile_picture(self, event=None):
        """ ให้ผู้ใช้เลือกภาพใหม่ และอัปเดตโปรไฟล์ทันที """
        file_path = filedialog.askopenfilename(
            title="เลือกภาพโปรไฟล์",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )

        if file_path:
            try:
                # บันทึกภาพใหม่แทนที่ profile.png
                image = Image.open(file_path)
                image = image.resize((100, 100), Image.Resampling.LANCZOS)
                image.save(self.default_profile_path)

                # โหลดภาพใหม่ที่บันทึกแล้ว
                self.load_profile_image(self.default_profile_path)

                # อัปเดตภาพใน Canvas
                self.canvas.itemconfig(self.profile_pic, image=self.profile_image)
                
            except Exception as e:
                messagebox.showerror("Error", f"ไม่สามารถบันทึกหรือโหลดรูปภาพได้: {e}")

    def change_name(self, event=None):
        """ ให้ผู้ใช้เปลี่ยนชื่อผ่าน dialog box """
        new_name = simpledialog.askstring("เปลี่ยนชื่อ", "กรุณากรอกชื่อใหม่:", initialvalue=self.username)
        if new_name:
            self.username = new_name
            self.name_label.config(text=self.username)  # อัปเดต Label ทันที
    
    def logout(self):
        print("คลิกออกจากระบบ")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Profile Frame")

    frame = ProfileFrame(root)
    frame.pack(fill="both", expand=True)

    root.mainloop()
