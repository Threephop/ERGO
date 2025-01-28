import cv2
from tkinter import messagebox

# รายการวิดีโอที่กำหนดไว้
video_list = {
    "วิดีโอ 1": "C:\\Users\\User\\Downloads\\VideoTest\\sample-mp4-files-sample_640x360.mp4",
    "วิดีโอ 2": "C:\\Users\\User\\Downloads\\VideoTest\\SampleVideo_1280x720_1mb.mp4",
}

# ตัวแปรควบคุมสถานะการเล่นวิดีโอ
video_playing = False


def play_video(video_path, volume=50):
    global video_playing
    video_playing = True

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot open video file!")
        return

    print(f"Playing video at {volume}% volume")

    window_name = "Video Player"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while video_playing and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(25)
        if key == ord('q') or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyWindow(window_name)
    video_playing = False


def show_popup(volume):
    from tkinter import Toplevel, StringVar, ttk, Button

    popup = Toplevel()
    popup.title("เลือกวิดีโอ")
    popup.geometry("300x200")

    def select_video():
        selected = video_var.get()
        if selected and selected in video_list:
            play_video(video_list[selected], volume)
        else:
            messagebox.showerror("Error", "กรุณาเลือกวิดีโอ")
        popup.destroy()

    # Dropdown ให้เลือกวิดีโอ
    video_var = StringVar(value=list(video_list.keys())[0])
    ttk.Label(popup, text="เลือกวิดีโอ").pack(pady=10)
    video_dropdown = ttk.Combobox(popup, textvariable=video_var, values=list(video_list.keys()), state="readonly")
    video_dropdown.pack(pady=10)

    Button(popup, text="เล่นวิดีโอ", command=select_video).pack(pady=10)
