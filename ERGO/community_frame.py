import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import cv2

class CommunityFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")
        if not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0, width=800, height=700)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # ⭐ สร้าง Bottom Bar ⭐
        self.bottom_bar = tk.Frame(self, bg="#FFFFFF", padx=10, pady=8)  # พื้นหลังสีเทาอ่อน
        self.bottom_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

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

        self.entry = tk.Entry(self.entry_frame, font=("Arial", 14), bd=0, fg="gray", bg="#D9D9D9")
        self.entry.pack(ipady=8, fill="x", padx=10, pady=2)  # ขอบมนและพื้นที่ภายใน

        self.add_placeholder()  # แสดง Placeholder เริ่มต้น

        # Bind Event สำหรับ Focus In และ Focus Out
        self.entry.bind("<FocusIn>", self.remove_placeholder)
        self.entry.bind("<FocusOut>", self.add_placeholder)

        # ปุ่มส่ง
        self.send_button = tk.Button(self.bottom_bar, image=self.send_icon, command=self.send_message, bd=0, bg="#FFFFFF", activebackground="#D4D4D4")
        self.send_button.pack(side="right", padx=10, pady=5)

        self.entry.bind("<Return>", lambda event: self.send_message())

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

    def cancel_single_message(self, bubble_frame):
        """ ลบเฉพาะข้อความหรือสื่อใน bubble_frame นั้นๆ """
        bubble_frame.destroy()

    def send_message(self):
        message = self.entry.get().strip()
        if message and message != self.placeholder_text:
            self.add_message_bubble("Username", message)
            self.entry.delete(0, "end")
            self.add_placeholder()  # แสดง Placeholder ใหม่หากไม่มีข้อความ
            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1)

    def add_message_bubble(self, username, message):
        bubble_frame = tk.Frame(self.scrollable_frame, bg="white", pady=5, padx=10)
        profile_label = tk.Label(bubble_frame, image=self.profile_icon, bg="white")
        profile_label.pack(side="left", padx=5)

        text_bubble = tk.Label(
            bubble_frame,
            text=message,
            font=("Arial", 14),
            bg="#e0e0e0",
            wraplength=400,
            justify="left",
            anchor="w",
            padx=10,
            pady=5,
            relief="ridge",
        )
        text_bubble.pack(side="left", padx=5)

        username_label = tk.Label(
            bubble_frame,
            text=username,
            font=("Arial", 10, "italic"),
            fg="gray",
            bg="white",
        )
        username_label.pack(anchor="w", padx=5)

        # ปุ่มยกเลิกการส่ง จะไปอยู่ด้านล่างตรงกลาง
        cancel_button = tk.Button(bubble_frame, text="ยกเลิกการส่ง", fg="red", font=("Arial", 12), bd=0, bg="white", command=lambda: self.cancel_single_message(bubble_frame))
        cancel_button.pack(side="bottom", pady=5, anchor="center")  # เปลี่ยนจาก "right" เป็น "bottom" และใช้ anchor="center"

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
                tk.Label(bubble_frame, text="ไม่สามารถโหลดวิดีโอได้", font=("Arial", 12), bg="white").pack(side="left", padx=5)

            username_label = tk.Label(bubble_frame, text="Username", font=("Arial", 10, "italic"), fg="gray", bg="white")
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
            like_label = tk.Label(like_frame, text=f"{self.like_count} Likes", font=("Arial", 12), bg="white")

            like_button.config(command=lambda: self.toggle_like(like_button, like_label))
            like_button.pack(side="top", pady=2)
            like_label.pack(side="top")


            # ปุ่มยกเลิกการส่ง
            cancel_button = tk.Button(bubble_frame, text="ยกเลิกการส่ง", fg="red", font=("Arial", 12), bd=0, bg="white", command=lambda: self.cancel_single_message(bubble_frame))
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

            username_label = tk.Label(bubble_frame, text="Username", font=("Arial", 10, "italic"), fg="gray", bg="white")
            username_label.pack(anchor="w", padx=5)

            # ปุ่มยกเลิกการส่ง จะไปอยู่ด้านล่างตรงกลาง
            cancel_button = tk.Button(bubble_frame, text="ยกเลิกการส่ง", fg="red", font=("Arial", 12), bd=0, bg="white", command=lambda: self.cancel_single_message(bubble_frame))
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