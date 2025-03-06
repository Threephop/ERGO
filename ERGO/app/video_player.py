import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from ffpyplayer.player import MediaPlayer
import time

cv2.setNumThreads(1)  # Limit OpenCV to a single thread

class VideoPlayer:
    def __init__(self, root, video_path):
        self.root = root
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)

        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_time = 1.0 / self.fps
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_duration = self.total_frames / self.fps
        
        # Initialize ffpyplayer for audio with better sync options
        self.player = MediaPlayer(video_path, ff_opts={'sync': 'audio', 'framedrop': True, 'autoexit': True})
        
        self.playing = False  # Video playback state
        self.volume = 1.0     # Volume level (0.0 to 1.0)
        self.current_frame = 0
        self.last_frame_time = 0
        self.update_timer_id = None
        
        # Create UI
        self.canvas = tk.Canvas(root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda event: self.root.after(10, self.update_video))  # อัปเดตวิดีโอเมื่อเปลี่ยนขนาด
        self.canvas.pack(pady=10)
        
        # Control frame
        control_frame = ttk.Frame(root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Control buttons
        self.btn_play = ttk.Button(control_frame, text='▶ Play', command=self.toggle_play)
        self.btn_play.pack(side=tk.LEFT, padx=5)
        
        # Volume control
        vol_frame = ttk.Frame(root)
        vol_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(vol_frame, text="Volume:").pack(side=tk.LEFT, padx=5)
        self.volume_scale = ttk.Scale(vol_frame, from_=0, to=1, orient=tk.HORIZONTAL, 
                                     value=self.volume, command=self.set_volume)
        self.volume_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # ปิดการเล่นเสียงเมื่อเริ่มต้น
        self.player.set_pause(True)

    def toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self.play_video()
            self.btn_play.config(text='⏸ Pause')
        else:
            self.pause_video()
            self.btn_play.config(text='▶ Play')
    
    def play_video(self):
        self.playing = True
        # เริ่มการเล่นเสียงเมื่อกด play
        self.player.set_pause(False)

        # ถ้ามีการหยุดไว้ในเฟรมก่อนหน้า ให้เล่นจากเฟรมเดิม
        if self.current_frame > 0:
            current_time = self.current_frame / self.fps
            self.player.seek(current_time, relative=False)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

        self.last_frame_time = time.time()
        self.update_video()

    def pause_video(self):
        if not self.playing:
            return
            
        self.playing = False
        
        # ตรวจสอบให้แน่ใจว่าเสียงถูกหยุดจริงๆ
        self.player.set_pause(True)
        
        # ในบางกรณี set_pause อาจไม่ทำงานทันที ให้ลองใช้ set_volume เป็น 0 ชั่วคราว
        temp_volume = self.volume
        self.player.set_volume(0)
        
        # อาจจะต้องรอสักครู่ก่อนที่จะคืนค่า volume
        def restore_volume():
            # ตรวจสอบอีกครั้งว่าเรายังคงอยู่ในสถานะ pause
            if not self.playing:
                self.player.set_volume(temp_volume)
        
        # คืนค่า volume หลังจากหยุดเสียงสำเร็จ
        self.root.after(100, restore_volume)
        
        self.btn_play.config(text='▶ Play')

        # Cancel any pending updates
        if self.update_timer_id:
            self.root.after_cancel(self.update_timer_id)
            self.update_timer_id = None

        # เก็บตำแหน่งเฟรมปัจจุบันเมื่อหยุด
        self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def update_video(self):
        if not self.playing or not self.cap.isOpened():
            return

        # Cancel any pending updates
        if self.update_timer_id:
            self.root.after_cancel(self.update_timer_id)
        
        # Get current video time from audio player for sync
        audio_time = self.player.get_pts()
        if audio_time is None:
            audio_time = 0.0
        
        # Set video position based on audio time
        frame_no = int(audio_time * self.fps)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)

        # Read the video frame
        ret, frame = self.cap.read()
        if not ret:
            # End of video
            self.pause_video()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return
        
        # อัปเดตขนาด Canvas
        self.root.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # ขนาดวิดีโอจริง
        video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_aspect = video_width / video_height
        canvas_aspect = canvas_width / canvas_height

        # ปรับขนาดให้คงสัดส่วนของวิดีโอ
        if canvas_aspect > video_aspect:
            new_height = canvas_height
            new_width = int(canvas_height * video_aspect)
        else:
            new_width = canvas_width
            new_height = int(canvas_width / video_aspect)

        # ตรวจสอบค่าขนาด (Debugging)
        print(f"Canvas: {canvas_width}x{canvas_height}, Video: {new_width}x{new_height}")

        # อ่านเฟรมวิดีโอ
        ret, frame = self.cap.read()
        if not ret:
            self.pause_video()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        # แปลงสีจาก BGR → RGB และปรับขนาด
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (new_width, new_height))
        img = ImageTk.PhotoImage(Image.fromarray(frame))

        # ล้างภาพเก่าและแสดงผลตรงกลาง
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=img)
        self.canvas.image = img  # ป้องกัน GC ลบรูป

        # อัปเดตตาม FPS
        wait_time = max(1, int(1000 / self.fps))
        self.update_timer_id = self.root.after(wait_time, self.update_video)
    
    def set_volume(self, value):
        self.volume = float(value)
        self.player.set_volume(self.volume)
    
    def on_closing(self):
        self.playing = False
        # Cancel any pending updates
        if self.update_timer_id:
            self.root.after_cancel(self.update_timer_id)
            self.update_timer_id = None

        # Close video and stop audio immediately
        try:
            self.cap.release()  # Release video capture
            self.player.close_player()  # Close audio player and stop sound
        except:
            pass
        self.player.set_pause(True)  # Pause audio when closing
        self.player.set_volume(0)  # Set volume to 0 (no sound)
        self.root.destroy()