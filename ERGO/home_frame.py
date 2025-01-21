import tkinter as tk
from tkinter import PhotoImage
import webbrowser  # For opening video in a web browser

class HomeFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ffffff")

        # Main content
        main_content = tk.Frame(self, bg="#ffffff")
        main_content.pack(side="right", expand=True, fill="both")

        # Title
        tk.Label(main_content, text="Title", bg="#ffffff", fg="#000000", font=("Arial", 24, "bold")).pack(pady=10)
        tk.Label(main_content, text="Description Lorem da ma fa de do re me fa son la tee", 
                 bg="#ffffff", fg="#888888", font=("Arial", 12, "italic")).pack(pady=5)

        # Video Section
        video_data = [
            {"title": "Video Name + นอก K.cal", "path": "https://www.youtube.com/watch?v=P5sHZRicEXg", "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19\u0e44\u0e2b\u0e19 EP1", "image": "C:\\Users\\User\\Downloads\\image111111.png"},
            {"title": "Video Name", "path": "https://www.youtube.com/watch?v=P5sHZRicEXg", "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19\u0e44\u0e2b\u0e19 EP2", "image": "C:\\Users\\User\\Downloads\\image111111.png"},
            {"title": "Video Name", "path": "https://www.youtube.com/watch?v=P5sHZRicEXg", "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19\u0e44\u0e2b\u0e19 EP3", "image": "C:\\Users\\User\\Downloads\\image111111.png"},
            {"title": "Video Name", "path": "https://www.youtube.com/watch?v=P5sHZRicEXg", "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19\u0e44\u0e2b\u0e19 EP4", "image": "C:\\Users\\User\\Downloads\\image111111.png"},
            {"title": "Video Name", "path": "https://www.youtube.com/watch?v=P5sHZRicEXg", "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19\u0e44\u0e2b\u0e19 EP5", "image": "C:\\Users\\User\\Downloads\\image111111.png"}
        ]

        video_frame = tk.Frame(main_content, bg="#ffffff")
        video_frame.pack(pady=10)

        for i, video in enumerate(video_data):
            try:
                thumbnail = PhotoImage(file=video["image"]).subsample(2, 2)  # Load image and resize
            except Exception as e:
                print(f"Error loading image for {video['title']}: {e}")
                thumbnail = PhotoImage(width=150, height=100)  # Placeholder image

            video_btn = tk.Button(video_frame, image=thumbnail, text=video["description"],
                                   compound="top", bg="#ffffff", fg="#000000",
                                   font=("Arial", 10),
                                   command=lambda v=video: self.play_video(v))
            video_btn.image = thumbnail  # Keep a reference to prevent garbage collection
            video_btn.grid(row=i // 2, column=i % 2, padx=10, pady=10)

        # Test Button
        test_button = tk.Button(main_content, text="Test", bg="#007bff", fg="#ffffff",
                                 font=("Arial", 14), bd=0, padx=20, pady=10)
        test_button.pack(pady=20)

    def play_video(self, video):
        # Open video URL in web browser
        video_url = video['path']
        print(f"Opening video: {video['title']} at {video_url}")
        webbrowser.open(video_url)

# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("ERGO PROJECT")
#     root.geometry("1024x768")
#     root.resizable(False, False)
#     HomeFrame(root).pack(expand=True, fill="both")
#     root.mainloop()
