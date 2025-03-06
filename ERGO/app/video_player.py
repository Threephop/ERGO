import os  
import cv2
from tkinter import messagebox
# ตัวแปรควบคุมสถานะการเล่นวิดีโอ
video_playing = False

def play_video(video_path):
    """เล่นวิดีโอจากไฟล์ที่กำหนด"""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถเปิดวิดีโอได้")
        return

    window_name = "Video Player"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(25)
        if key == ord('q') or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    
    # ตรวจสอบว่าหน้าต่างยังคงเปิดอยู่ก่อนปิด
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
        print(f"Closing window: {window_name}")
        cv2.destroyWindow(window_name)
    else:
        print("No window found, using destroyAllWindows()")
        cv2.destroyAllWindows()

    video_playing = False