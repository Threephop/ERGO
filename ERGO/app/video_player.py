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
        
        # Volume control
        vol_frame = ttk.Frame(root)
        vol_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(vol_frame, text="Volume:").pack(side=tk.LEFT, padx=5)
        self.volume_scale = ttk.Scale(vol_frame, from_=0, to=1, orient=tk.HORIZONTAL, value=self.volume, command=self.set_volume)
        self.volume_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.player.set_pause(True)

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
