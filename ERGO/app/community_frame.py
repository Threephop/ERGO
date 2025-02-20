import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import cv2
import requests 
from datetime import datetime 

class CommunityFrame(tk.Frame):
    def __init__(self, parent, user_email):
        super().__init__(parent)
        
        self.api_base_url = "http://127.0.0.1:8000"
        self.user_email = user_email
        self.user_id = self.fetch_user_id(user_email)
        
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")
        if not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)

        # สร้าง Canvas และ Scrollbar
        self.canvas = tk.Canvas(self, bg="#364DB6", highlightthickness=0)
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
        self.load_messages()
        self.update_idletasks() # อัปเดต UI ก่อนเลื่อนลงไปที่ข้อความล่าสุด
        self.canvas.yview_moveto(1.0)  # เลื่อนลงไปที่ข้อความล่าสุด
        
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
        
    def load_messages(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        try:
            response = requests.get("http://localhost:8000/get-messages")
            if response.status_code == 200:
                messages = response.json().get("messages", [])
                user_id = self.user_id  # user_id ของผู้ใช้ที่ล็อกอินอยู่
                
                print(f"✅ Logged-in user_id: {user_id}")  # เช็ค user_id

                for msg in messages:
                    username = msg.get("username", "Unknown")
                    post_id = msg.get("post_id")
                    content = msg.get("content")
                    message_owner_id = msg.get("user_id")  # user_id ของเจ้าของโพสต์
                    
                    # print(f"📝 Post {post_id} by user_id: {message_owner_id}")  # ดูค่าของ user_id ในโพสต์

                    if message_owner_id == user_id:
                        self.add_message_bubble(post_id, username, content)
                    else:
                        self.add_message_bubble_another(post_id, username, content)
                # ✅ เลื่อน scroll ลงไปที่ข้อความล่าสุด
                self.update_idletasks() # อัปเดต UI ก่อนเลื่อนลงไปที่ข้อความล่าสุด
                self.canvas.yview_moveto(1.0)  # เลื่อนลงไปที่ข้อความล่าสุด
            else:
                print("⚠️ เกิดข้อผิดพลาด:", response.json())
        except Exception as e:
            print("⚠️ เกิดข้อผิดพลาดขณะโหลดข้อความ:", e)
            
    def fetch_user_id(self, user_email):
        """ดึง user_id จาก API"""
        url = f"{self.api_base_url}/get_user_id/{user_email}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if "user_id" in data:
                    return data["user_id"]
            print("Error fetching user_id:", response.json().get("error", "Unknown error"))
        except Exception as e:
            print("Exception:", e)
        return None  # ถ้าหาไม่เจอให้ return None
            
    def cancel_single_message(self, bubble_frame, post_id):
        # ฟังก์ชัน callback เมื่อผู้ใช้กดยืนยันการลบ
        def on_ok():
            try:
                response = requests.delete(
                    f"http://localhost:8000/delete-message/{post_id}",
                    json={"user_id": self.user_id}  # ส่ง user_id ไปด้วยเพื่อยืนยันสิทธิ์ในการลบ
                )
                if response.status_code == 200:
                    print("ลบข้อความสำเร็จ!")
                    bubble_frame.destroy()  # ลบ UI หลังจากลบข้อมูลในฐานข้อมูลสำเร็จ
                else:
                    print("เกิดข้อผิดพลาด:", response.json())
            except Exception as e:
                print("เชื่อมต่อ API ไม่สำเร็จ:", e)
        
        # ฟังก์ชัน callback เมื่อผู้ใช้กดยกเลิกการลบ
        def on_cancel():
            print("ยกเลิกการลบข้อความ")
        
        # แสดง popup ยืนยันการลบ
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
                        "create_at": create_at
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    post_id = data.get("post_id")
                    if post_id:
                        print("ส่งข้อความสำเร็จ! post_id:", post_id)
                        # คุณสามารถเรียก add_message_bubble โดยส่ง post_id ที่ถูกต้องได้
                        self.add_message_bubble(post_id, self.username, message)
                        self.update_idletasks() # อัปเดต UI ก่อนเลื่อนลงไปที่ข้อความล่าสุด
                        self.canvas.yview_moveto(1.0)  # เลื่อนลงไปที่ข้อความล่าสุด
                    else:
                        print("ไม่สามารถดึง post_id ได้จากการตอบกลับ")
                else:
                    print("เกิดข้อผิดพลาด:", response.json())
                        
            except Exception as e:
                print("เชื่อมต่อ API ไม่สำเร็จ:", e)



    def add_message_bubble(self, post_id, username, message):
        bubble_frame = tk.Frame(self.scrollable_frame, bg="white", pady=5, padx=10)
        bubble_frame.pack(anchor="e", fill="x", padx=5, pady=5)  # จัดให้อยู่ทางขวา

        # แสดงรูปโปรไฟล์
        profile_label = tk.Label(bubble_frame, image=self.profile_icon, bg="white")
        profile_label.pack(side="right", padx=5)  # จัดรูปโปรไฟล์ไปทางขวา

        # แสดงข้อความ
        text_bubble = tk.Label(
            bubble_frame,
            text=message,
            font=("PTT 45 Pride", 14),
            bg="#a3d977",  # เปลี่ยนสีพื้นหลังเป็นสีเขียว
            wraplength=400,
            justify="left",
            anchor="w",
            padx=10,
            pady=5,
            relief="ridge",
        )
        text_bubble.pack(side="right", padx=5)  # จัดข้อความไปด้านขวา

        # แสดงชื่อผู้ใช้
        username_label = tk.Label(
            bubble_frame,
            text=username,
            font=("PTT 45 Pride", 10, "italic"),
            fg="gray",
            bg="white",
        )
        username_label.pack(anchor="e", padx=5)  # จัดชื่อผู้ใช้ไปทางขวา

        # ปุ่มยกเลิกการส่ง โดยส่ง bubble_frame และ post_id ไปยังฟังก์ชัน cancel_single_message
        cancel_button = tk.Button(
            bubble_frame, 
            text="ยกเลิกการส่ง", 
            fg="red", 
            font=("PTT 45 Pride", 12), 
            bd=0, 
            bg="white", 
            command=lambda: self.cancel_single_message(bubble_frame, post_id)
    )
        cancel_button.pack(side="bottom", pady=5, anchor="e")  # จัดปุ่มไปด้านขวา

        
    def add_message_bubble_another(self, post_id, username, message):
        bubble_frame = tk.Frame(self.scrollable_frame, bg="#ffffff", pady=5, padx=10)
        
        # แสดงรูปโปรไฟล์
        profile_label = tk.Label(bubble_frame, image=self.profile_icon, bg="#ffffff")
        profile_label.pack(side="left", padx=5)
        
        # แสดงข้อความ
        text_bubble = tk.Label(
            bubble_frame,
            text=message,
            font=("PTT 45 Pride", 14),
            bg="#d0f0ff",  # สีฟ้าอ่อน
            wraplength=400,
            justify="left",
            anchor="w",
            padx=10,
            pady=5,
            relief="ridge",
        )
        text_bubble.pack(side="left", padx=5)
        
        # แสดงชื่อผู้ใช้
        username_label = tk.Label(
            bubble_frame,
            text=username,
            font=("PTT 45 Pride", 10, "italic"),
            fg="gray",
            bg="#ffffff",
        )
        username_label.pack(anchor="w", padx=5)
        
        bubble_frame.pack(anchor="w", fill="x", padx=5, pady=5)


    def post_video(self, filepath):
        try:
            bubble_frame = tk.Frame(self.scrollable_frame, bg="white", pady=5, padx=10)
            profile_label = tk.Label(bubble_frame, image=self.profile_icon, bg="white")
            profile_label.pack(side="left", padx=5)

            thumbnail = self.get_video_thumbnail(filepath)
            if thumbnail:
                video_label = tk.Label(bubble_frame, image=thumbnail, bg="white", cursor="hand2")
                video_label.image = thumbnail
                video_label.pack(side="left", padx=5)
                video_label.bind("<Button-1>", lambda e: self.play_video(filepath))
            else:
                tk.Label(bubble_frame, text="ไม่สามารถโหลดวิดีโอได้", font=("PTT 45 Pride", 12), bg="white").pack(side="left", padx=5)

            username_label = tk.Label(bubble_frame, text="Username", font=("PTT 45 Pride", 10, "italic"), fg="gray", bg="white")
            username_label.pack(anchor="w", padx=5)

            # Like Section
            like_frame = tk.Frame(bubble_frame, bg="white")
            like_frame.pack(expand=True, anchor="center", pady=5)

            like_icon = self.load_resized_image("Like.png", (20, 20))
            heart_icon = self.load_resized_image("heart.png", (20, 20))

            like_button = tk.Button(like_frame, image=like_icon, bd=0, bg="white")
            like_button.image = like_icon
            like_button.heart_icon = heart_icon
            like_button.like_icon = like_icon
            like_button.is_liked = False  # เริ่มต้นยังไม่กด Like

            self.like_count = 0
            like_label = tk.Label(like_frame, text=f"{self.like_count} Likes", font=("PTT 45 Pride", 12), bg="white")

            like_button.config(command=lambda: self.toggle_like(like_button, like_label))
            like_button.pack(side="top", pady=2)
            like_label.pack(side="top")


            # ปุ่มยกเลิกการส่ง
            cancel_button = tk.Button(bubble_frame, text="ยกเลิกการส่ง", fg="red", font=("PTT 45 Pride", 12), bd=0, bg="white", command=lambda: self.cancel_single_message(bubble_frame))
            cancel_button.pack(side="bottom", pady=5, anchor="center")

            bubble_frame.pack(anchor="w", fill="x", padx=5, pady=5)
            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1)

        except Exception as e:
            messagebox.showerror("Error", f"Error posting video: {e}")

    def toggle_like(self, like_button, like_label):
        """ เปลี่ยนสถานะของปุ่ม Like และอัปเดตจำนวน Like """
        if like_button.is_liked:  # ถ้ากดแล้ว (Unlike)
            like_button.config(image=like_button.like_icon, bg="white")
            self.like_count -= 1
        else:  # ถ้ายังกด Like ไม่ได้
            like_button.config(image=like_button.heart_icon, bg="white")
            self.like_count += 1

        like_button.is_liked = not like_button.is_liked  # สลับสถานะ
        like_label.config(text=f"{self.like_count} Likes")  # อัปเดตจำนวน Like


    def get_video_thumbnail(self, filepath):
        try:
            cap = cv2.VideoCapture(filepath)
            if not cap.isOpened():
                return None

            ret, frame = cap.read()
            cap.release()

            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                image = image.resize((150, 150), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            else:
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
            self.post_media(filepath)

    def post_media(self, filepath):
        if filepath.lower().endswith(('mp4', 'avi', 'mkv')):
            self.post_video(filepath)
        else:
            self.post_image(filepath)

    def post_image(self, filepath):
        try:
            image = Image.open(filepath)
            image = image.resize((150, 150))
            image_tk = ImageTk.PhotoImage(image)

            bubble_frame = tk.Frame(self.scrollable_frame, bg="white", pady=5, padx=10)
            profile_label = tk.Label(bubble_frame, image=self.profile_icon, bg="white")
            profile_label.pack(side="left", padx=5)

            image_label = tk.Label(bubble_frame, image=image_tk, bg="white")
            image_label.image = image_tk
            image_label.pack(side="left", padx=5)

            username_label = tk.Label(bubble_frame, text="Username", font=("PTT 45 Pride", 10, "italic"), fg="gray", bg="white")
            username_label.pack(anchor="w", padx=5)

            # ปุ่มยกเลิกการส่ง จะไปอยู่ด้านล่างตรงกลาง
            cancel_button = tk.Button(bubble_frame, text="ยกเลิกการส่ง", fg="red", font=("PTT 45 Pride", 12), bd=0, bg="white", command=lambda: self.cancel_single_message(bubble_frame))
            cancel_button.pack(side="bottom", pady=5, anchor="center")  # เปลี่ยนจาก "right" เป็น "bottom" และใช้ anchor="center"

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