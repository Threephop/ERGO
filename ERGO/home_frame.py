import tkinter as tk
from tkinter import PhotoImage
import webbrowser  # สำหรับเปิดวิดีโอในเว็บเบราว์เซอร์

class HomeFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ffffff")

        # Title
        tk.Label(self, text="Title", bg="#ffffff", fg="#000000", font=("Arial", 24)).pack(pady=10)

        # Video Section with YouTube link
        video_data = [
            {"title": "Sample Video", 
             "image": "path_to_thumbnail.png", 
             "path": "https://www.youtube.com/watch?v=P5sHZRicEXg",  # YouTube link
             "description": "ตัวอย่างวิดีโอ"}
        ]

        # Grid layout for video
        video_frame = tk.Frame(self, bg="#ffffff")
        video_frame.pack(pady=10)

        for i, video in enumerate(video_data):
            # Placeholder image for video thumbnail
            thumbnail = PhotoImage(file="")  # เปลี่ยน path ให้เป็นภาพจริง
            video_btn = tk.Button(video_frame, image=thumbnail, text=video["description"],
                                   compound="top", bg="#ffffff", fg="#000000",
                                   command=lambda v=video: self.play_video(v))
            video_btn.image = thumbnail  # เก็บ reference เพื่อป้องกัน garbage collection
            video_btn.grid(row=i // 2, column=i % 2, padx=10, pady=10)

    def play_video(self, video):
        # เปิดวิดีโอจาก YouTube โดยใช้ webbrowser
        video_url = video['path']
        print(f"Opening video: {video['title']} at {video_url}")
        webbrowser.open(video_url)  # ใช้ webbrowser เปิด YouTube link

# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("ERGO PROJECT")
#     root.geometry("800x600")
#     HomeFrame(root).pack(expand=True, fill="both")
#     root.mainloop()
