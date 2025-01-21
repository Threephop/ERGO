import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import cv2

class CommunityFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")
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

        self.bottom_bar = tk.Frame(self, bg="white", padx=100, pady=5)
        self.bottom_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        def load_resized_image(file_name, size):
            try:
                path = os.path.join(self.icon_dir, file_name)
                image = Image.open(path)
                image = image.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error loading {file_name}: {e}")
                return None

        self.camera_icon = load_resized_image("camera.png", (45, 40))
        self.folder_icon = load_resized_image("folder.png", (50, 47))
        self.send_icon = load_resized_image("send.png", (30, 30))
        self.profile_icon = load_resized_image("profile.png", (50, 50))

        self.camera_button = tk.Button(self.bottom_bar, image=self.camera_icon, command=self.open_camera, bd=0, bg="white")
        self.camera_button.pack(side="left", padx=5, pady=5)

        self.folder_button = tk.Button(self.bottom_bar, image=self.folder_icon, command=self.open_folder, bd=0, bg="white")
        self.folder_button.pack(side="left", padx=5, pady=5)

        self.entry = tk.Entry(self.bottom_bar, font=("Arial", 14), bd=1)
        self.entry.pack(side="left", padx=(100, 80), pady=5, fill="x", expand=True)

        self.send_button = tk.Button(self.bottom_bar, image=self.send_icon, command=self.send_message, bd=0, bg="white")
        self.send_button.pack(side="left", padx=1, pady=5)

        self.entry.bind("<Return>", lambda event: self.send_message())

    def send_message(self):
        message = self.entry.get().strip()
        if message:
            self.add_message_bubble("Username", message)
            self.entry.delete(0, "end")
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

        bubble_frame.pack(anchor="w", fill="x", padx=5, pady=5)

    def open_camera(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("ไม่สามารถเปิดกล้องได้")
                return

            cv2.namedWindow("Camera")

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("ไม่สามารถอ่านข้อมูลจากกล้องได้")
                    break

                cv2.imshow("Camera", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('s'):
                    image_path = os.path.join(self.icon_dir, "captured_image.jpg")
                    cv2.imwrite(image_path, frame)
                    print(f"ภาพถูกบันทึกที่ {image_path}")
                    break
                elif key == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

        except Exception as e:
            print(f"Error opening camera: {e}")

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

            bubble_frame.pack(anchor="w", fill="x", padx=5, pady=5)

            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1)

        except Exception as e:
            print(f"Error posting image: {e}")

    def post_video(self, filepath):
        try:
            bubble_frame = tk.Frame(self.scrollable_frame, bg="white", pady=5, padx=10)
            profile_label = tk.Label(bubble_frame, image=self.profile_icon, bg="white")
            profile_label.pack(side="left", padx=5)

            # ดึงเฟรมแรกของวิดีโอเพื่อใช้เป็นรูปตัวอย่าง
            thumbnail = self.get_video_thumbnail(filepath)
            if thumbnail:
                video_label = tk.Label(bubble_frame, image=thumbnail, bg="white", cursor="hand2")
                video_label.image = thumbnail  # เก็บ reference เพื่อป้องกันการเก็บขยะ
                video_label.pack(side="left", padx=5)
                video_label.bind("<Button-1>", lambda e: self.play_video(filepath))
            else:
                video_label = tk.Label(
                    bubble_frame,
                    text="Unable to load video preview",
                    font=("Arial", 14),
                    bg="#e0e0e0",
                    wraplength=400,
                    justify="left",
                    anchor="w",
                    padx=10,
                    pady=5,
                    relief="ridge",
                )
                video_label.pack(side="left", padx=5)

            username_label = tk.Label(
                bubble_frame,
                text="Username",
                font=("Arial", 10, "italic"),
                fg="gray",
                bg="white",
            )
            username_label.pack(anchor="w", padx=5)

            bubble_frame.pack(anchor="w", fill="x", padx=5, pady=5)

            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1)

        except Exception as e:
            print(f"Error posting video: {e}")

    def get_video_thumbnail(self, filepath):
        try:
            cap = cv2.VideoCapture(filepath)
            if not cap.isOpened():
                print(f"Cannot open video file: {filepath}")
                return None

            ret, frame = cap.read()  # อ่านเฟรมแรกของวิดีโอ
            cap.release()

            if ret:
                # แปลงเฟรมเป็นรูปภาพเพื่อแสดงใน Tkinter
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                image = image.resize((150, 150), Image.Resampling.LANCZOS)  # ปรับขนาดให้เหมาะสม
                return ImageTk.PhotoImage(image)
            else:
                print("Cannot read the first frame of the video.")
                return None
        except Exception as e:
            print(f"Error generating video thumbnail: {e}")
            return None

    def play_video(self, filepath):
        try:
            os.startfile(filepath)  # ใช้ Media Player เริ่มต้นของ Windows
            print(f"Playing video: {filepath}")
        except Exception as e:
            print(f"Error playing video: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Community Chat")
    root.geometry("824x768")

    frame = CommunityFrame(root)
    frame.grid(row=0, column=0, sticky="nsew")

    root.mainloop()
