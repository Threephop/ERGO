import cv2
import tkinter as tk
from PIL import Image, ImageTk
import threading
import time


class VideoPlayerApp:
    def __init__(self, root, video_url):
        self.root = root
        self.video_url = video_url
        self.cap = cv2.VideoCapture(self.video_url)
        self.running = True
        self.paused = False

        # ดึงค่า FPS ของวิดีโอ
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30  # ใช้ค่าเริ่มต้น 30 FPS ถ้าหาไม่ได้
        self.delay = 1 / self.fps

        # ส่วนของ GUI
        self.label = tk.Label(root)
        self.label.pack()

        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack()

        self.play_button = tk.Button(self.controls_frame, text="Play", command=self.resume_video)
        self.play_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.controls_frame, text="Pause", command=self.pause_video)
        self.pause_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.controls_frame, text="Stop", command=self.stop_video)
        self.stop_button.pack(side=tk.LEFT)

        self.play_video()

    def play_video(self):
        def stream():
            while self.running:
                if not self.paused and self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if ret:
                        # แปลงสีจาก BGR (OpenCV) เป็น RGB (Pillow)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(frame)
                        imgtk = ImageTk.PhotoImage(image=img)

                        # อัพเดตเฟรมใน GUI
                        self.label.imgtk = imgtk
                        self.label.configure(image=imgtk)

                        # หน่วงเวลาให้สอดคล้องกับ FPS
                        time.sleep(self.delay)
                    else:
                        # ถ้าวิดีโอเล่นจบ ให้หยุดการเล่น
                        break
                else:
                    time.sleep(0.1)

            # ปิด VideoCapture เมื่อหยุด
            self.cap.release()

        # ใช้ Thread เพื่อป้องกัน GUI ค้าง
        threading.Thread(target=stream, daemon=True).start()

    def pause_video(self):
        self.paused = True

    def resume_video(self):
        self.paused = False

    def stop_video(self):
        self.running = False
        self.paused = True
        self.cap.release()
        self.label.config(image="")  # ล้างภาพออกจาก GUI

    def cleanup(self):
        self.running = False
        self.cap.release()


if __name__ == "__main__":
    # URL ของวิดีโอ
    video_url = "https://ergoproject.blob.core.windows.net/ergovideo/test.mp4"

    # สร้างหน้าต่าง Tkinter
    root = tk.Tk()
    root.title("Video Player")

    # สร้าง VideoPlayerApp
    app = VideoPlayerApp(root, video_url)

    # จัดการปิดหน้าต่าง
    def on_close():
        app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
