import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
from ffpyplayer.player import MediaPlayer
import time
import os

cv2.setNumThreads(1)  # Limit OpenCV to a single thread

class VideoPlayer:
    def __init__(self, root, video_path):
        self.root = root
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")

        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30  # Default to 30 FPS if not detected
        self.frame_time = 1.0 / self.fps
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Initialize audio player
        self.player = MediaPlayer(video_path, ff_opts={'sync': 'audio', 'framedrop': True, 'autoexit': True})
        
        self.playing = False
        self.volume = 1.0
        self.last_frame_time = time.time()
        self.update_timer_id = None

        # Create UI
        self.canvas = tk.Canvas(root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Control frame
        control_frame = ttk.Frame(root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_play = ttk.Button(control_frame, text='▶ Play', command=self.toggle_play)
        self.btn_play.pack(side=tk.LEFT, padx=5)
        
        # ไอคอนกล้อง
        self.camera_icon = self.load_resized_image("camera.png", (42, 39))
        self.camera_button = tk.Button(control_frame, image=self.camera_icon, command=self.open_camera, bd=0, bg="#FFFFFF", activebackground="#D4D4D4")
        self.camera_button.pack(side="left", padx=5, pady=5)

        
        # Volume control
        vol_frame = ttk.Frame(root)
        vol_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(vol_frame, text="Volume:").pack(side=tk.LEFT, padx=5)
        self.volume_scale = ttk.Scale(vol_frame, from_=0, to=1, orient=tk.HORIZONTAL, value=self.volume, command=self.set_volume)
        self.volume_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.player.set_pause(True)
        
    def load_resized_image(self, file_name, size):
        try:
            path = os.path.join(self.icon_dir, file_name)
            image = Image.open(path)
            image = image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading {file_name}: {e}")
            return None
        
    def open_camera(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "ไม่สามารถเปิดกล้องได้")
                return

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = None
            
            cv2.namedWindow("Camera")
            print("กด 'r' เพื่อเริ่ม/หยุดการอัดวิดีโอ, 's' เพื่อบันทึก, 'q' เพื่อออก")
            is_recording = False
            video_path = None

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("ไม่สามารถอ่านข้อมูลจากกล้องได้")
                    break

                cv2.imshow("Camera", frame)

                if is_recording and out is not None:
                    print("กำลังบันทึกเฟรม...")
                    out.write(frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('r'):
                    is_recording = not is_recording
                    if is_recording:
                        print("เริ่มการอัดวิดีโอ")
                    else:
                        print("หยุดการอัดวิดีโอ")
                        if out is not None:
                            out.release()
                            out = None
                elif key == ord('s'):
                    if not is_recording:
                        root = tk.Tk()
                        root.withdraw()
                        video_path = filedialog.asksaveasfilename(defaultextension=".avi", filetypes=[("AVI files", "*.avi")])
                        if not video_path:
                            print("ยกเลิกการบันทึกวิดีโอ")
                            continue
                        out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))
                        print(f"บันทึกวิดีโอที่ {video_path}")
                        messagebox.showinfo("บันทึกสำเร็จ", f"วิดีโอถูกบันทึกที่ {video_path}")
                        out.release()
                        out = None
                    else:
                        print("กรุณาหยุดการอัดวิดีโอก่อนบันทึก")
                elif key == ord('q'):
                    break

            cap.release()
            if out is not None:
                out.release()
            cv2.destroyAllWindows()
            cv2.waitKey(1)  # ป้องกันหน้าต่างปิดไม่สมบูรณ์
        except Exception as e:
            messagebox.showerror("Error", f"Error opening camera: {e}")

    def toggle_play(self):
        if self.playing:
            self.pause_video()
        else:
            self.play_video()

    def play_video(self):
        self.playing = True
        self.player.set_pause(False)
        self.player.set_volume(self.volume)
        self.last_frame_time = time.time()
        self.update_video()
        self.btn_play.config(text='⏸ Pause')

    def pause_video(self):
        if not self.playing:
            return
        self.playing = False
        self.player.set_pause(True)
        self.btn_play.config(text='▶ Play')

        if self.update_timer_id:
            self.root.after_cancel(self.update_timer_id)
            self.update_timer_id = None

    def update_video(self):
        if not self.playing or not self.cap.isOpened():
            return

        audio_time = self.player.get_pts() or 0.0
        frame_no = int(audio_time * self.fps)

        if frame_no >= self.total_frames:
            self.pause_video()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ret, frame = self.cap.read()
        if not ret:
            return

        # Resize frame to fit canvas
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_aspect = video_width / video_height
        canvas_aspect = canvas_width / canvas_height

        if canvas_aspect > video_aspect:
            new_height = canvas_height
            new_width = int(canvas_height * video_aspect)
        else:
            new_width = canvas_width
            new_height = int(canvas_width / video_aspect)

        frame = cv2.resize(frame, (new_width, new_height))
        img = ImageTk.PhotoImage(Image.fromarray(frame))

        self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=img)
        self.canvas.image = img  # ป้องกัน GC ลบรูป

        self.update_timer_id = self.root.after(int(1000 / self.fps), self.update_video)

    def set_volume(self, value):
        self.volume = float(value)
        self.player.set_volume(self.volume)

    def on_closing(self):
        self.playing = False
        if self.update_timer_id:
            self.root.after_cancel(self.update_timer_id)

        if self.cap.isOpened():
            self.cap.release()
        
        try:
            self.player.close_player()
        except:
            pass
        
        self.root.destroy()
