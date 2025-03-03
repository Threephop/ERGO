import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import io
import requests
import webbrowser
import subprocess  # เพิ่มการนำเข้า subprocess

class ProfileFrame(tk.Frame):
    def __init__(self, parent, user_email, app_instance):
        super().__init__(parent, bg="white")

        self.app_instance = app_instance
        self.logout_called = False  # ป้องกัน Logout ซ้ำ
        self.timer_stopped = False  # ป้องกัน stop_timer() ทำงานซ้ำ

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
        self.canvas.tag_bind("profile_pic", "<Button-1>", lambda event: self.change_profile_picture(event, self.user_id))

        self.user_email = user_email
        self.api_base_url = "http://127.0.0.1:8000"
        self.user_id = self.fetch_user_id(user_email)  # ดึง user_id จาก API
        
        # 🔹 ดึงรายชื่อ users จาก API
        response = requests.get("http://127.0.0.1:8000/users")
        if response.status_code == 200:
            try:
                data = response.json()

                # พิมพ์ข้อมูลที่ได้รับจาก API
                # print("Users list from API:", data)

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

    def change_profile_picture(self, event=None, user_id=None):
        """ ให้ผู้ใช้เลือกภาพใหม่ และอัปโหลดไปยัง Azure Blob Storage """
        file_path = filedialog.askopenfilename(
            title="เลือกภาพโปรไฟล์",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )

        if file_path:
            try:
                # ✅ 1. เช็คการเชื่อมต่อกับ Azure Blob Storage ก่อน
                container_name = "image-profile"  # 🔹 แก้เป็นชื่อ Container จริง
                check_blob_url = f"http://localhost:8000/check_blob_storage/?container_name={container_name}"
                response = requests.get(check_blob_url)

                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ เชื่อมต่อกับ Blob Storage สำเร็จ: {data['message']}")
                else:
                    print("❌ ไม่สามารถเชื่อมต่อกับ Blob Storage ได้")
                    messagebox.showerror("Error", "ไม่สามารถเชื่อมต่อกับ Blob Storage ได้ กรุณาลองใหม่อีกครั้ง")
                    return

                # ✅ 2. อัปโหลดรูปภาพไปยัง Azure Blob Storage พร้อมส่ง user_id
                upload_url = f"http://localhost:8000/upload_profile/?user_id={user_id}"
                with open(file_path, "rb") as file:
                    files = {"file": file}
                    upload_response = requests.post(upload_url, files=files)

                if upload_response.status_code == 200:
                    profile_url = upload_response.json().get("profile_url", None)
                    if not profile_url:
                        print(f"❌ ไม่พบ URL ของรูปที่อัปโหลด: {upload_response.json()}")
                        messagebox.showerror("Error", "ไม่พบ URL ของรูปที่อัปโหลด กรุณาลองใหม่")
                        return

                    print(f"✅ รูปโปรไฟล์ถูกอัปโหลดไปยัง Azure Blob Storage: {profile_url}")
                else:
                    print(f"❌ อัปโหลดรูปโปรไฟล์ล้มเหลว: {upload_response.json()}")
                    messagebox.showerror("Error", "อัปโหลดรูปโปรไฟล์ไปยัง Blob Storage ล้มเหลว กรุณาลองใหม่อีกครั้ง")
                    return

                # ✅ 3. ดึงรูปภาพจาก URL มาแสดงแทนที่ภาพเดิม
                image_data = requests.get(profile_url).content
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((100, 100), Image.Resampling.LANCZOS)
                self.profile_image = ImageTk.PhotoImage(image)

                # ✅ 4. อัปเดตโปรไฟล์ใน Canvas
                self.canvas.itemconfig(self.profile_pic, image=self.profile_image)
                print("✅ เปลี่ยนรูปโปรไฟล์สำเร็จ!")

            except Exception as e:
                messagebox.showerror("Error", f"ไม่สามารถอัปโหลดรูปโปรไฟล์ได้: {e}")

    
    def fetch_user_id(self, user_email):
        """ดึง user_id จาก API"""
        url = f"{self.api_base_url}/get_user_id/{user_email}"
        try:
            response = requests.get(url, timeout=5)  # ใส่ timeout ป้องกันค้าง
            if response.status_code == 200:
                data = response.json()
                return data.get("user_id")
            else:
                print("Error fetching user_id:", response.json().get("error", "Unknown error"))
        except requests.RequestException as e:
            print("Exception:", e)

        return None  # ถ้าหาไม่เจอให้ return None อย่างชัดเจน

    def change_name(self, event=None):
        """ให้ผู้ใช้เปลี่ยนชื่อ และส่งไปอัปเดตใน API"""
        new_name = simpledialog.askstring("เปลี่ยนชื่อ", "กรุณากรอกชื่อใหม่:", initialvalue=self.username)
        
        if new_name and new_name.strip():
            user_id = self.fetch_user_id(self.user_email)  # ดึง user_id
            if user_id:
                success = self.update_username_in_api(user_id, new_name.strip())  # ส่ง user_id แทน email
                if success:
                    self.username = new_name.strip()
                    if self.name_label:
                        self.name_label.config(text=self.username)
                    messagebox.showinfo("สำเร็จ", f"เปลี่ยนชื่อเป็น '{self.username}' เรียบร้อย!")
                else:
                    messagebox.showerror("ล้มเหลว", "ไม่สามารถเปลี่ยนชื่อได้ กรุณาลองใหม่อีกครั้ง")
            else:
                messagebox.showerror("ล้มเหลว", "ไม่สามารถดึง user_id ได้ กรุณาลองใหม่อีกครั้ง")

    def update_username_in_api(self, user_id, new_username):
        """ส่งคำขอเปลี่ยนชื่อไปยัง API"""
        url = "http://127.0.0.1:8000/update_username"  # ใช้ endpoint POST ที่ถูกต้อง
        payload = {"user_id": user_id, "new_username": new_username}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(url, data=payload, headers=headers, timeout=5)  # เพิ่ม headers
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                messagebox.showerror("ผิดพลาด", "ไม่พบผู้ใช้ในระบบ")
            elif response.status_code == 400:
                messagebox.showerror("ผิดพลาด", response.json().get("detail", "ชื่อใหม่ไม่สามารถเว้นว่างได้"))
            else:
                messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {response.status_code}\n{response.text}")
        except requests.RequestException as e:
            messagebox.showerror("ผิดพลาด", f"ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์: {e}")

        return False  # ถ้าอัปเดตไม่สำเร็จ ให้ return False

    def logout(self):
        """ ฟังก์ชัน Logout ที่ทำให้ stop_timer() ทำงาน """
        print("🔹 logout() ถูกเรียก!")  

        if self.logout_called:
            print("⚠️ logout() ถูกเรียกซ้ำ! ไม่ทำงานอีก")
            return
        self.logout_called = True  # ป้องกันการกด Logout ซ้ำ

        print("📢 แสดง Messagebox ยืนยัน Logout...")
        confirmed = messagebox.askyesno("Logout", "Are you sure you want to log out?")

        if not confirmed:
            print("❌ ผู้ใช้กดยกเลิก Logout")
            self.logout_called = False  # Reset ค่า ถ้าผู้ใช้กดยกเลิก
            return
        print("✅ ผู้ใช้ยืนยัน Logout")

        # ✅ เรียก stop_timer() ก่อน Logout
        if self.app_instance:
            try:
                print("⏳ เรียก stop_timer()...")
                if hasattr(self.app_instance, "stop_timer"):  # เช็คว่า stop_timer() มีอยู่ใน app_instance หรือไม่
                    self.app_instance.stop_timer()
                    print("✅ stop_timer() ทำงานสำเร็จ!")
                else:
                    print("⚠️ stop_timer() ไม่มีอยู่ใน app_instance")
                    messagebox.showerror("Error", "stop_timer() ไม่มีอยู่ใน app_instance")
                    self.logout_called = False
                    return
            except Exception as e:
                print(f"❌ stop_timer() มีปัญหา: {e}")
                messagebox.showerror("Error", f"stop_timer() มีปัญหา: {e}")
                self.logout_called = False
                return

        try:
            # เปิดเบราว์เซอร์ไปที่หน้า Logout ของ Microsoft
            logout_url = "https://login.microsoftonline.com/common/oauth2/v2.0/logout"
            print(f"🌐 เปิด URL: {logout_url}")
            webbrowser.open(logout_url)

            # แสดง Messagebox แจ้งเตือนว่า Logout สำเร็จ
            messagebox.showinfo("Logout", "You have been logged out.")
            print("✅ Messagebox แสดงสำเร็จ!")

            # ปิดแอปทั้งหมดแล้วเปิด Login ใหม่
            self.master.after(500, self.close_app)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during logout: {e}")
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            self.logout_called = False  # Reset ค่าเผื่อมีข้อผิดพลาด


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
        """เปิดหน้าต่าง Login ใหม่โดยไม่ต้องนำเข้า LoginApp"""
        import sys
        import os

        # ตรวจสอบว่าไฟล์ Login.py อยู่ในตำแหน่งที่ถูกต้อง
        login_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "Login.py"))
        if not os.path.exists(login_py_path):
            messagebox.showerror("Error", "Cannot find Login.py")
            return

        try:
            print(f"✅ เปิด Login.py ที่พาธ: {login_py_path}")
            python_executable = sys.executable  # ใช้ Python interpreter เดียวกัน
            subprocess.Popen([python_executable, login_py_path], shell=True)  # ใช้ shell=True ช่วยให้ทำงานได้ดีขึ้น

            print("🛑 บังคับปิดแอปหลักด้วย sys.exit()")
            sys.exit()  # ปิดแอปหลักไปเลย

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Login: {e}")


if __name__ == "__main__":
    root = tk.Tk()  
    root.title("Profile Frame")

    frame = ProfileFrame(root, user_email="test@example.com")
    frame.pack(fill="both", expand=True)

    root.mainloop()
