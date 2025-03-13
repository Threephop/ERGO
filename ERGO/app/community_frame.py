import tkinter as tk
import customtkinter as ctk
from customtkinter import CTkImage
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import io
import cv2
import requests 
from datetime import datetime 
import threading

params = {
    "x_api_key": "ergoapipoC18112024",  # ส่ง API Key ใน query parameter
}

class CommunityFrame(tk.Frame):
    def __init__(self, parent, user_email):
        super().__init__(parent)
        
        self.api_base_url = "http://127.0.0.1:8000"
        self.user_email = user_email
        self.user_id = self.fetch_user_id(user_email)
        self.like_labels = {}  # เก็บข้อมูลป้าย like สำหรับโพสต์แต่ละโพสต์
        self.like_counts = {}  # เก็บจำนวน like สำหรับโพสต์แต่ละโพสต์
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")
        if not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)
            
        self.profile_icon = self.load_resized_image("profile.png", (50, 50))  # รูปโปรไฟล์เริ่มต้น
        self.profile_images = {}  # เก็บรูปโปรไฟล์ของทุกคน

        # ✅ โหลดรูปโปรไฟล์ของทุกคนตั้งแต่เริ่มต้น
        self.load_all_profiles()

        # สร้าง Canvas และ Scrollbar
        self.canvas = tk.Canvas(self, bg="#ffffff", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        # สร้าง Frame ที่จะใช้เป็นพื้นที่เลื่อน
        self.scrollable_frame = tk.Frame(self.canvas, bg="#ffffff")

        # อัปเดต scrollable_frame ให้มีขนาดเท่ากับ canvas
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.window_id, width=e.width))

        # เพิ่ม scrollable_frame เข้าไปใน canvas
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # ตั้งค่าการเลื่อน scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # ✅ ใช้ `grid()` แทน `pack()`
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # ⭐ สร้าง Bottom Bar ⭐
        self.bottom_bar = tk.Frame(self, bg="#FFFFFF", padx=10, pady=8)  
        self.bottom_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        # ✅ ทำให้ Canvas ปรับขนาดตาม Frame ได้
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # โหลดไอคอน
        self.camera_icon = self.load_resized_image("camera.png", (42, 39))
        self.folder_icon = self.load_resized_image("folder.png", (45, 47))
        self.send_icon = self.load_resized_image("send.png", (30, 30))
        self.profile_icon = self.load_resized_image("profile.png", (50, 50))

        # ไอคอนกล้อง
        self.camera_button = tk.Button(self.bottom_bar, image=self.camera_icon, command=self.open_camera, bd=0, bg="#FFFFFF", activebackground="#D4D4D4")
        self.camera_button.pack(side="left", padx=5, pady=5)

        # ไอคอนโฟลเดอร์
        self.folder_button = tk.Button(self.bottom_bar, image=self.folder_icon, command=self.open_folder, bd=0, bg="#FFFFFF", activebackground="#D4D4D4")
        self.folder_button.pack(side="left", padx=5, pady=5)

        # ⭐ สร้าง Entry แบบสวยงาม ⭐
        self.placeholder_text = "พิมพ์ข้อความ"
        self.entry_frame = tk.Frame(self.bottom_bar, bg="#D9D9D9", bd=0)  # พื้นหลังของช่องพิมพ์
        self.entry_frame.pack(side="left", padx=(10, 10), pady=5, fill="x", expand=True)

        self.entry = tk.Entry(self.entry_frame, font=("PTT 45 Pride", 14), bd=0, fg="gray", bg="#D9D9D9")
        self.entry.pack(ipady=8, fill="x", padx=10, pady=2)  # ขอบมนและพื้นที่ภายใน

        self.add_placeholder()  # แสดง Placeholder เริ่มต้น

        # Bind Event สำหรับ Focus In และ Focus Out
        self.entry.bind("<FocusIn>", self.remove_placeholder)
        self.entry.bind("<FocusOut>", self.add_placeholder)

        # ปุ่มส่ง
        self.send_button = tk.Button(self.bottom_bar, image=self.send_icon, command=self.send_message, bd=0, bg="#FFFFFF", activebackground="#D4D4D4")
        self.send_button.pack(side="right", padx=10, pady=5)
        
        # สร้างปุ่ม refresh
        self.refresh_button = tk.Button(self, text="Refresh", font=("Arial", 12, "bold"), command=self.load_messages, bg="#4CAF50", fg="white")
        self.refresh_button.grid(row=0, column=0, padx=10, pady=10, sticky="ne")

        self.entry.bind("<Return>", lambda event: self.send_message())
        self.is_loading = False # ตั้งค่าเริ่มต้นสำหรับการโหลดข้อความ
        self.load_messages()
        self.update_idletasks() # อัปเดต UI ก่อนเลื่อนลงไปที่ข้อความล่าสุด
        self.canvas.yview_moveto(1.0)  # เลื่อนลงไปที่ข้อความล่าสุด
        
        response = requests.get("http://127.0.0.1:8000/users", params=params)
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

    def add_placeholder(self, event=None):
        """แสดงข้อความ 'พิมพ์ข้อความ' ถ้า input ว่าง"""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder_text)
            self.entry.config(fg="gray")

    def remove_placeholder(self, event=None):
        """ลบข้อความ placeholder ถ้าผู้ใช้เริ่มพิมพ์"""
        if self.entry.get() == self.placeholder_text:
            self.entry.delete(0, "end")
            self.entry.config(fg="black")  # เปลี่ยนเป็นสีดำเมื่อพิมพ์

    def load_resized_image(self, file_name, size):
        try:
            path = os.path.join(self.icon_dir, file_name)
            image = Image.open(path)
            image = image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading {file_name}: {e}")
            return None
        
    def show_confirm_popup(self, title, message, ok_callback, cancel_callback):
        # สร้าง Toplevel window สำหรับ popup
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.geometry("350x150")  # กำหนดขนาด popup
        popup.resizable(False, False)
        popup.configure(bg="white")
        # ทำให้ popup เป็น modal (ไม่ให้คลิกที่ window อื่นได้)
        popup.grab_set()
        
        # สร้าง Label แสดงข้อความใน popup
        label = tk.Label(popup, text=message, font=("PTT 45 Pride", 12), bg="white")
        label.pack(pady=20)
        
        # สร้าง frame สำหรับปุ่ม
        btn_frame = tk.Frame(popup, bg="white")
        btn_frame.pack(pady=10)
        
        # สร้างปุ่ม "ตกลง" และ "ยกเลิก" ด้วยการปรับแต่งตามที่ต้องการ
        ok_button = tk.Button(
            btn_frame, text="ตกลง", font=("PTT 45 Pride", 12, "bold"),
            bg="#4CAF50", fg="white", width=10,
            command=lambda: [ok_callback(), popup.destroy()]
        )
        ok_button.pack(side="left", padx=10)
        
        cancel_button = tk.Button(
            btn_frame, text="ยกเลิก", font=("PTT 45 Pride", 12, "bold"),
            bg="#f44336", fg="white", width=10,
            command=lambda: [cancel_callback(), popup.destroy()]
        )
        cancel_button.pack(side="left", padx=10)
        
        # ตั้งค่าให้ popup อยู่ตรงกลางหน้าจอ parent
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (350 // 2) + 200
        y = self.winfo_y() + (self.winfo_height() // 2) - (150 // 2)
        popup.geometry(f"+{x}+{y}")
        
    def fetch_profile_images(self):
        """ ดึงข้อมูลรูปโปรไฟล์ของทุกคนจาก API """
        url = f"{self.api_base_url}/get_all_profiles/"
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                self.profile_images = data.get("profiles", {})
            else:
                print(f"⚠️ Failed to fetch profile images: {response.status_code}")
                self.profile_images = {}
        except Exception as e:
            print(f"❌ Error fetching profile images: {e}")
            self.profile_images = {}
    
    def load_all_profiles(self):
        """ โหลดรูปโปรไฟล์ของทุก user ตั้งแต่เปิดแอป """
        try:
            response = requests.get(f"{self.api_base_url}/users", params=params)
            if response.status_code == 200:
                users = response.json().get("users", [])
                for user in users:
                    user_id = user.get("user_id")
                    profile_url = user.get("profile_url", None)

                    if user_id:
                        if profile_url and profile_url.strip() and profile_url.lower() != "null":
                            self.profile_images[user_id] = self.load_profile_image(profile_url)  # ✅ โหลดโปรไฟล์จริง
                        else:
                            self.profile_images[user_id] = self.profile_icon  # ✅ ใช้ Default
            else:
                print("⚠️ API Error: ไม่สามารถโหลดข้อมูลผู้ใช้ได้")
        except Exception as e:
            print(f"❌ Error loading user profiles: {e}")

    def load_profile_image(self, image_url):
        """ โหลดรูปโปรไฟล์จาก URL """
        try:
            if not image_url or image_url.strip() == "" or image_url.lower() == "null":
                return self.profile_icon  # ใช้ Default ถ้าไม่มี URL

            response = requests.get(image_url, params=params, timeout=5)
            if response.status_code == 200:
                image_data = io.BytesIO(response.content)
                image = Image.open(image_data)
                image = image.resize((50, 50), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            else:
                print(f"⚠️ โหลดรูปโปรไฟล์ไม่สำเร็จจาก {image_url}")
        except Exception as e:
            print(f"❌ Error loading profile image: {e}")

        return self.profile_icon  # คืนค่าเป็นรูปโปรไฟล์เริ่มต้นถ้าโหลดไม่สำเร็จ
        
    def load_messages(self):
        if self.is_loading:
            return  # ป้องกันการโหลดซ้ำ

        self.is_loading = True  # กำลังโหลด...
        
        def fetch():
            try:
                for widget in self.scrollable_frame.winfo_children():
                    try:
                        widget.unbind("<Button-1>")  # ป้องกันปัญหา event ถูกเรียกหลัง destroy
                    except Exception as e:
                        print(f"⚠️ ไม่สามารถ unbind widget ได้: {e}")  
                    
                    widget.destroy()

                response = requests.get("http://localhost:8000/get-messages", params)
                if response.status_code == 200:
                    messages = response.json().get("messages", [])
                    user_id = self.user_id

                    messages = sorted(messages, key=lambda x: x["post_id"])

                    for msg in messages:
                        username = msg.get("username", "Unknown")
                        post_id = msg.get("post_id")
                        content = msg.get("content")
                        message_owner_id = msg.get("user_id")
                        filepath = msg.get("video_path", None)  
                        like_count = msg.get("like_count", 0)  
                        profile_image = self.profile_images.get(message_owner_id, self.profile_icon)

                        is_liked_response = requests.get(f"http://localhost:8000/check-like", params={"post_id": post_id, "user_id": user_id, "x_api_key": "ergoapipoC18112024"})
                        is_liked = is_liked_response.json().get("is_liked", False) if is_liked_response.status_code == 200 else False

                        if filepath:  
                            if message_owner_id == user_id:
                                self.post_video(filepath, user_id, post_id, username, like_count, is_liked, profile_image)
                            else:
                                self.post_video_another(filepath, user_id, post_id, username, like_count, is_liked, profile_image)
                        else:  
                            if message_owner_id == user_id:
                                self.add_message_bubble(post_id, username, content, profile_image)
                            else:
                                self.add_message_bubble_another(post_id, username, content, profile_image)

                    self.update_idletasks()
                    self.canvas.yview_moveto(1.0)
                else:
                    print("⚠️ เกิดข้อผิดพลาด:", response.json())
            except Exception as e:
                print("⚠️ เกิดข้อผิดพลาดขณะโหลดข้อความ:", e)
            finally:
                self.is_loading = False  # โหลดเสร็จแล้ว
            
        thread = threading.Thread(target=fetch, daemon=True)
        thread.start()

                    
    def fetch_user_id(self, user_email):
        """ดึง user_id จาก API"""
        url = f"{self.api_base_url}/get_user_id/{user_email}"
        try:
            response = requests.get(url, params)
            if response.status_code == 200:
                data = response.json()
                if "user_id" in data:
                    return data["user_id"]
            print("Error fetching user_id:", response.json().get("error", "Unknown error"))
        except Exception as e:
            print("Exception:", e)
        return None  # ถ้าหาไม่เจอให้ return None
            
    def cancel_single_message(self, bubble_frame, post_id):
        """ ฟังก์ชันยกเลิก (ลบ) ข้อความและลบวิดีโอจาก Storage ถ้ามี """

        def on_ok():
            try:
                # ✅ 1. เรียก API เพื่อตรวจสอบว่ามีวิดีโอในโพสต์นี้หรือไม่
                video_response = requests.get(
                    f"http://localhost:8000/get_video_path",
                    params={"post_id": post_id, "x_api_key": "ergoapipoC18112024"}        
                )

                if video_response.status_code == 200:
                    video_path = video_response.json().get("video_path")
                    if video_path:
                        # ✅ 2. ลบวิดีโอออกจาก Storage
                        delete_video_response = requests.delete(
                            f"http://localhost:8000/delete_video",
                            params={"post_id": post_id, "video_url": video_path, "x_api_key": "ergoapipoC18112024"}  # ส่ง post_id และ video_url ใน query string
                        )

                        if delete_video_response.status_code == 200:
                            print(f"✅ วิดีโอถูกลบออกจาก Storage: {video_path}")
                        else:
                            print(f"⚠️ ไม่สามารถลบวิดีโอได้: {delete_video_response.json()}")

                # ✅ 3. ลบโพสต์ออกจากฐานข้อมูล
                response = requests.delete(
                    f"http://localhost:8000/delete-message/{post_id}",
                    params=params,
                    json={"user_id": self.user_id},
                )

                if response.status_code == 200:
                    print("✅ ลบข้อความสำเร็จ!")
                    bubble_frame.destroy()  # ✅ อัปเดต UI
                else:
                    print("⚠️ เกิดข้อผิดพลาดในการลบโพสต์:", response.json())

            except Exception as e:
                print("❌ เชื่อมต่อ API ไม่สำเร็จ:", e)

        def on_cancel():
            print("⛔ ยกเลิกการลบข้อความ")

        # ✅ แสดง popup ยืนยันก่อนลบ
        self.show_confirm_popup("ยืนยันการลบ", "คุณต้องการลบข้อความนี้หรือไม่?", on_ok, on_cancel)
        
    def send_message(self):
        message = self.entry.get().strip()
        if message and message != self.placeholder_text:
            # ลบข้อความในช่องพิมพ์และอัปเดต UI
            self.entry.delete(0, "end")
            self.add_placeholder()
            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1)

            # ตรวจสอบค่าที่ส่งไป API
            print(f"Sending user_id: {self.user_id}, content: {message}")

            try:
                create_at = datetime.now().isoformat()
                response = requests.post(
                    "http://localhost:8000/post-message",
                    params={
                        "user_id": self.user_id,
                        "content": message,
                        "create_at": create_at,
                        "x_api_key": "ergoapipoC18112024"
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    post_id = data.get("post_id")
                    if post_id:
                        print("ส่งข้อความสำเร็จ! post_id:", post_id)
                        # คุณสามารถเรียก add_message_bubble โดยส่ง post_id ที่ถูกต้องได้
                        self.add_message_bubble(post_id, self.username, message, self.profile_icon)
                        self.update_idletasks() # อัปเดต UI ก่อนเลื่อนลงไปที่ข้อความล่าสุด
                        self.canvas.yview_moveto(1.0)  # เลื่อนลงไปที่ข้อความล่าสุด
                    else:
                        print("ไม่สามารถดึง post_id ได้จากการตอบกลับ")
                else:
                    print("เกิดข้อผิดพลาด:", response.json())
                        
            except Exception as e:
                print("เชื่อมต่อ API ไม่สำเร็จ:", e)


    def add_message_bubble(self, post_id, username, message, profile_image):
        bubble_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white", corner_radius=20)
        bubble_frame.pack(anchor="e", fill="x", padx=5, pady=5)

        # แสดงรูปโปรไฟล์
        profile_label = tk.Label(bubble_frame, image=profile_image, bg="white")
        profile_image.image = profile_image  # ป้องกัน GC
        profile_label.pack(side="right", padx=5)

        # แสดงข้อความ
        text_bubble = ctk.CTkLabel(
            bubble_frame,
            text=message,
            font=("PTT 45 Pride", 18),
            fg_color="#a3d977",  # สีพื้นหลังของข้อความ
            text_color="black",  # สีตัวอักษร
            corner_radius=20,
            wraplength=600,
            padx=10,
            pady=5,
        )
        text_bubble.pack(side="right", padx=5)

        # แสดงชื่อผู้ใช้
        username_label = ctk.CTkLabel(
            bubble_frame,
            text=username,
            font=("PTT 45 Pride", 14, "italic"),
            text_color="gray",
            fg_color="white",
        )
        username_label.pack(anchor="e", padx=5)

        # ปุ่มยกเลิกการส่ง
        cancel_button = ctk.CTkButton(
            bubble_frame, 
            text="ยกเลิกการส่ง", 
            fg_color="white", 
            text_color="red",
            hover_color="#f5c6cb",  # เปลี่ยนสีเมื่อชี้เมาส์
            font=("PTT 45 Pride", 14), 
            command=lambda: self.cancel_single_message(bubble_frame, post_id)
        )
        cancel_button.pack(side="bottom", pady=5, anchor="e")


    def add_message_bubble_another(self, post_id, username, message, profile_image):
        bubble_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white", corner_radius=15)
        bubble_frame.pack(anchor="w", fill="x", padx=5, pady=5)

        # แสดงรูปโปรไฟล์
        profile_label = tk.Label(bubble_frame, image=profile_image, bg="white")
        profile_image.image = profile_image  # ป้องกัน GC
        profile_label.pack(side="left", padx=5)

        # แสดงข้อความ
        text_bubble = ctk.CTkLabel(
            bubble_frame,
            text=message,
            font=("PTT 45 Pride", 18),
            fg_color="#d0f0ff",  # สีฟ้าอ่อน
            text_color="black",
            corner_radius=20,
            wraplength=600,
            padx=10,
            pady=5,
        )
        text_bubble.pack(side="left", padx=5)

        # แสดงชื่อผู้ใช้
        username_label = ctk.CTkLabel(
            bubble_frame,
            text=username,
            font=("PTT 45 Pride", 14, "italic"),
            text_color="gray",
            fg_color="white",
        )
        username_label.pack(anchor="w", padx=5)


        
    def post_video(self, filepath, user_id, post_id, username, like_count, is_liked, profile_image):
        try:
            print(f"ใช้ post_id: {post_id} สำหรับการแสดงผลวิดีโอ")

            bubble_frame = tk.Frame(self.scrollable_frame, bg="white", pady=5, padx=10)
            profile_label = tk.Label(bubble_frame, image=profile_image, bg="white")
            profile_label.image = profile_image  # ป้องกัน GC
            profile_label.pack(side="right", padx=5)

            thumbnail = self.get_video_thumbnail(filepath)
            if thumbnail:
                video_label = tk.Label(bubble_frame, image=thumbnail, bg="white", cursor="hand2")
                video_label.image = thumbnail
                video_label.pack(side="right", padx=5)
                video_label.bind("<Button-1>", lambda e: self.play_video(filepath))
            else:
                tk.Label(bubble_frame, text="ไม่สามารถโหลดวิดีโอได้", font=("PTT 45 Pride", 12), bg="white").pack(side="left", padx=5)

            username_label = tk.Label(bubble_frame, text=username, font=("PTT 45 Pride", 10, "italic"), fg="gray", bg="white")
            username_label.pack(anchor="e", padx=5)

            # สร้าง Like Frame
            like_frame = tk.Frame(bubble_frame, bg="white")
            like_frame.pack(side="right", anchor="e", pady=5)

            like_icon = self.load_resized_image("Like.png", (20, 20))
            heart_icon = self.load_resized_image("heart.png", (20, 20))

            initial_icon = heart_icon if is_liked else like_icon

            like_button = tk.Button(like_frame, image=initial_icon, bd=0, bg="white")
            like_button.image = initial_icon  # ป้องกัน GC
            like_button.heart_icon = heart_icon
            like_button.like_icon = like_icon
            like_button.is_liked = is_liked  
            like_button.like_count = like_count

            like_label = tk.Label(like_frame, text=f"{like_count} Likes", font=("PTT 45 Pride", 12), bg="white")

            # ใช้ try-except ป้องกัน error ที่เกิดจาก widget ที่อาจถูกลบ
            try:
                like_button.config(command=lambda: self.toggle_like(like_button, like_label, post_id, user_id, like_button.is_liked))
                like_button.pack(side="top", pady=2)
                like_label.pack(side="top")
            except tk.TclError:
                print(f"⚠️ ไม่สามารถสร้าง Like button สำหรับ post_id {post_id}")

            self.like_labels[post_id] = like_label

            self.add_like_count(post_id, like_count)

            cancel_button = tk.Button(
                bubble_frame, 
                text="ยกเลิกการส่ง", 
                fg="red", 
                font=("PTT 45 Pride", 12), 
                bd=0, 
                bg="white", 
                command=lambda: self.cancel_single_message(bubble_frame, post_id)
            )
            cancel_button.pack(side="bottom", pady=5, anchor="e")

            bubble_frame.pack(anchor="w", fill="x", padx=5, pady=5)
            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1)

        except Exception as e:
            messagebox.showerror("Error", f"Error posting video: {e}")


    def post_video_another(self, filepath, user_id, post_id, username, like_count, is_liked ,profile_image):
        try:
            print(f"📌 ใช้ post_id: {post_id} สำหรับการแสดงผลวิดีโอที่โพสต์โดยผู้ใช้อื่น")

            bubble_frame = tk.Frame(self.scrollable_frame, bg="#ffffff", pady=5, padx=10)
            
            profile_label = tk.Label(bubble_frame, image=profile_image, bg="#ffffff")
            profile_label.image = profile_image  # ป้องกัน GC
            profile_label.pack(side="left", padx=5)

            thumbnail = self.get_video_thumbnail(filepath)
            if thumbnail:
                video_label = tk.Label(bubble_frame, image=thumbnail, bg="#ffffff", cursor="hand2")
                video_label.image = thumbnail
                video_label.pack(side="left", padx=5)
                video_label.bind("<Button-1>", lambda e: self.play_video(filepath))
            else:
                tk.Label(bubble_frame, text="ไม่สามารถโหลดวิดีโอได้", font=("PTT 45 Pride", 12), bg="lightgray").pack(side="left", padx=5)

            username_label = tk.Label(bubble_frame, text=username, font=("PTT 45 Pride", 10, "italic"), fg="gray", bg="#ffffff")
            username_label.pack(anchor="w", padx=5)

            # ✅ สร้าง Like Frame และ Like Button
            like_frame = tk.Frame(bubble_frame, bg="#ffffff")
            like_frame.pack(expand=True, anchor="w", pady=5)

            like_icon = self.load_resized_image("Like.png", (20, 20))
            heart_icon = self.load_resized_image("heart.png", (20, 20))
            
            initial_icon = heart_icon if is_liked else like_icon

            like_button = tk.Button(like_frame, image=initial_icon, bd=0, bg="white")
            like_button.image = initial_icon  # ป้องกัน GC
            like_button.heart_icon = heart_icon
            like_button.like_icon = like_icon
            like_button.is_liked = is_liked  
            like_button.like_count = like_count

            like_label = tk.Label(like_frame, text=f"{like_count} Likes", font=("PTT 45 Pride", 12), bg="white")

            # ใช้ try-except ป้องกัน error ที่เกิดจาก widget ที่อาจถูกลบ
            try:
                like_button.config(command=lambda: self.toggle_like(like_button, like_label, post_id, user_id, like_button.is_liked))
                like_button.pack(side="top", pady=2)
                like_label.pack(side="top")
            except tk.TclError:
                print(f"⚠️ ไม่สามารถสร้าง Like button สำหรับ post_id {post_id}")

            # ✅ บันทึก like_label ลง self.like_labels
            self.like_labels[post_id] = like_label

            # ✅ อัปเดตจำนวนไลก์
            self.add_like_count(post_id, like_count)

            bubble_frame.pack(anchor="w", fill="x", padx=5, pady=5)
            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1)

        except Exception as e:
            messagebox.showerror("Error", f"❌ Error posting video by another user: {e}")


    def toggle_like(self, like_button, like_label, post_id, user_id, is_liked):
        """ เปลี่ยนสถานะของปุ่ม Like และอัปเดตจำนวน Like พร้อมกับส่งข้อมูลไปยัง FastAPI """

        # ตรวจสอบว่าปุ่มยังคงอยู่ก่อนอัปเดต
        if not like_button.winfo_exists() or not like_label.winfo_exists():
            print(f"⚠️ ปุ่มหรือ Label ของ post_id {post_id} ถูกลบไปแล้ว")
            return

        if is_liked:
            # ถ้ายกเลิก Like
            like_button.config(image=like_button.like_icon, bg="white")
            like_button.like_count -= 1
            like_button.is_liked = False
            action = "unlike"
        else:
            # ถ้ายังไม่ Like
            like_button.config(image=like_button.heart_icon, bg="white")
            like_button.like_count += 1
            like_button.is_liked = True
            action = "like"

        # ส่งคำขอไปยัง API
        self.send_like(post_id, user_id, action)

        # ตรวจสอบว่า label ยังมีอยู่ก่อนอัปเดตข้อความ
        if like_label.winfo_exists():
            like_label.config(text=f"{like_button.like_count} Likes")

    def send_like(self, post_id, user_id, action):
        """ ส่งคำขอ Like หรือ Unlike ไปยัง API """
        url = "http://127.0.0.1:8000/like"
        
        # สร้าง dictionary สำหรับการส่งข้อมูล
        params = {
            "post_id": post_id,
            "user_id": user_id,
            "action": action,  # ใช้ action เพื่อบอกว่าเป็นการ Like หรือ 
            "x_api_key": "ergoapipoC18112024"
        }

        try:
            response = requests.post(url, params=params)

            if response.status_code == 200:
                print(f"{action.capitalize()} added successfully")
            else:
                print(f"Error: {response.status_code}, {response.json()['detail']}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending request: {e}")
            
    def add_like_count(self, post_id, like_count):
        """ แสดงจำนวน Like ของโพสต์ """
        try:
            if post_id in self.like_labels:
                like_count_label = self.like_labels[post_id]
                like_count_label.config(text=f"{like_count} Likes")
            else:
                print(f"⚠️ ไม่พบ like_label สำหรับ post_id: {post_id}")
        except Exception as e:
            print(f"❌ Error in add_like_count: {e}")


    def get_video_thumbnail(self, filepath):
        try:
            cap = cv2.VideoCapture(filepath)
            if not cap.isOpened():
                print(f"ไม่สามารถเปิดไฟล์วิดีโอ: {filepath}")
                return None

            ret, frame = cap.read()
            cap.release()

            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                image = image.resize((150, 150), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            else:
                print(f"ไม่สามารถอ่านเฟรมจากไฟล์วิดีโอ: {filepath}")
                return None
        except Exception as e:
            print(f"Error generating video thumbnail: {e}")
            return None

    def play_video(self, filepath):
        try:
            os.startfile(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Error playing video: {e}")
            
    def open_camera(self):
        try:
            video_path = os.path.join(self.icon_dir, "recorded_video.avi")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "ไม่สามารถเปิดกล้องได้")
                return

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))

            cv2.namedWindow("Camera")
            print("กด 'r' เพื่อเริ่ม/หยุดการอัดวิดีโอ, 's' เพื่อบันทึก, 'q' เพื่อออก")
            is_recording = False

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("ไม่สามารถอ่านข้อมูลจากกล้องได้")
                    break

                cv2.imshow("Camera", frame)

                if is_recording:
                    print("กำลังบันทึกเฟรม...")
                    out.write(frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('r'):
                    is_recording = not is_recording
                    print("เริ่มการอัดวิดีโอ" if is_recording else "หยุดการอัดวิดีโอ")
                elif key == ord('s'):
                    if not is_recording:
                        print("บันทึกวิดีโอ")
                        messagebox.showinfo("บันทึกสำเร็จ", f"วิดีโอถูกบันทึกที่ {video_path}")
                    else:
                        print("กรุณาหยุดการอัดวิดีโอก่อนบันทึก")
                elif key == ord('q'):
                    break

            cap.release()
            out.release()
            cv2.destroyAllWindows()
            cv2.waitKey(1)  # เพิ่มเวลาหน่วงเล็กน้อยเพื่อให้หน้าต่างปิดอย่างสมบูรณ์

        except Exception as e:
            messagebox.showerror("Error", f"Error opening camera: {e}")

    def open_folder(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png"), ("Video files", "*.mp4 *.avi *.mkv")])
        if filepath:
            # ✅ อัปโหลดไฟล์ครั้งเดียว และรับ `post_id`
            upload_url = "http://localhost:8000/upload_file/"
            with open(filepath, "rb") as file:
                files = {"file": file}
                params = {"user_id": self.user_id, "x_api_key": "ergoapipoC18112024"}
                upload_response = requests.post(upload_url, files=files, params=params)

            if upload_response.status_code == 200:
                response_data = upload_response.json()
                post_id = response_data.get("post_id")
                if post_id is not None:
                    print(f"✅ ได้รับ post_id: {post_id}")
                    self.post_media(filepath, post_id)  # ✅ ส่ง post_id ต่อให้ post_media
                else:
                    messagebox.showerror("Error", "ไม่สามารถดึง post_id ได้")
            else:
                messagebox.showerror("Error", "อัปโหลดไฟล์ไม่สำเร็จ กรุณาลองใหม่อีกครั้ง")


    def post_media(self, filepath, post_id):
        username = self.username  # ดึงค่า username จาก instance variable
        if filepath.lower().endswith(('mp4', 'avi', 'mkv')):
            like_count = 0  # หรือดึงค่า like_count จากฐานข้อมูลถ้ามี
            self.post_video(filepath, self.user_id, post_id, username, like_count, is_liked=False, profile_image=self.profile_icon)
        else:
            self.post_image(filepath)


    def post_image(self, filepath):
        try:
            # ✅ 1. เช็คการเชื่อมต่อกับ Blob Storage ก่อน
            container_name = "ergo"  # แก้ไขเป็นชื่อ Container จริง
            check_blob_url = f"http://localhost:8000/check_blob_storage/?container_name={container_name}"
            response = requests.get(check_blob_url, params)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ เชื่อมต่อกับ Blob Storage สำเร็จ: {data['message']}")
            else:
                print("❌ ไม่สามารถเชื่อมต่อกับ Blob Storage ได้")
                messagebox.showerror("Error", "ไม่สามารถเชื่อมต่อกับ Blob Storage ได้ กรุณาลองใหม่อีกครั้ง")
                return

            # ✅ 2. อัปโหลดรูปภาพไปยัง Azure Blob Storage
            upload_url = "http://localhost:8000/upload_video/"
            with open(filepath, "rb") as file:
                files = {"file": file}
                upload_response = requests.post(upload_url, params, files=files)

            if upload_response.status_code == 200:
                image_url = upload_response.json().get("image_url")
                print(f"✅ รูปภาพถูกอัปโหลดไปยัง Azure Blob Storage: {image_url}")
            else:
                print(f"❌ อัปโหลดรูปภาพล้มเหลว: {upload_response.json()}")
                messagebox.showerror("Error", "อัปโหลดรูปภาพไปยัง Blob Storage ล้มเหลว กรุณาลองใหม่อีกครั้ง")
                return

            # ✅ 3. ดึงรูปภาพจาก URL แทนการใช้ Local Path
            image_data = requests.get(image_url, params).content
            image = Image.open(io.BytesIO(image_data))
            image = image.resize((150, 150))
            image_tk = ImageTk.PhotoImage(image)

            # ✅ 4. อัปเดต UI และแสดงผลรูปภาพที่อัปโหลด
            bubble_frame = tk.Frame(self.scrollable_frame, bg="white", pady=5, padx=10)
            profile_label = tk.Label(bubble_frame, image=self.profile_icon, bg="white")
            profile_label.pack(side="left", padx=5)

            image_label = tk.Label(bubble_frame, image=image_tk, bg="white")
            image_label.image = image_tk
            image_label.pack(side="left", padx=5)

            username_label = tk.Label(bubble_frame, text=self.username, font=("PTT 45 Pride", 10, "italic"), fg="gray", bg="white")
            username_label.pack(anchor="w", padx=5)

            # ปุ่มยกเลิกการส่ง
            cancel_button = tk.Button(bubble_frame, text="ยกเลิกการส่ง", fg="red", font=("PTT 45 Pride", 12), bd=0, bg="white", command=lambda: self.cancel_single_message(bubble_frame))
            cancel_button.pack(side="bottom", pady=5, anchor="center")

            bubble_frame.pack(anchor="w", fill="x", padx=5, pady=5)

            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1)

        except Exception as e:
            messagebox.showerror("Error", f"Error posting image: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Community Chat")
    root.geometry("824x768")
    frame = CommunityFrame(root)
    frame.grid(row=0, column=0, sticky="nsew")

    root.mainloop()