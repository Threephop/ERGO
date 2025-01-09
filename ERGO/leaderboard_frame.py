import tkinter as tk
from tkinter import ttk

class LeaderboardFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.master = master
        self.current_tab_frame = None

        # Header สำหรับ Leaderboard
        title_label = tk.Label(self, text="Leader-board", font=("Arial", 24, "bold"), bg="white", fg="black")
        title_label.pack(pady=10)

        # Tabs Frame
        tabs_frame = tk.Frame(self, bg="white")
        tabs_frame.pack(pady=10)

        # ปุ่มแท็บโค้ง
        self.tab_buttons = {}
        for idx, tab_name in enumerate(["Calorie", "Active", "Popular"]):
            btn = tk.Button(
                tabs_frame,
                text=tab_name,
                font=("Arial", 12),
                bg="#D3D3D3" if idx != 0 else "#4B0082",
                fg="black" if idx != 0 else "white",
                relief="flat",
                width=15,
                height=2,
                command=lambda name=tab_name: self.switch_tab(name),
            )
            btn.pack(side="left", padx=0)  # ปุ่มติดกัน
            self.tab_buttons[tab_name] = btn

        # Default Tab Content
        self.tab_frames = {
            "Calorie": self.create_calorie_frame(),
            "Active": self.create_active_frame(),
            "Popular": self.create_popular_frame(),
        }

        self.switch_tab("Calorie")  # แสดงแท็บแรกโดยเริ่มต้น

    def create_calorie_frame(self):
        frame = tk.Frame(self, bg="white")
        tk.Label(frame, text="Total Calories Burned: xxxx Kcal", font=("Arial", 18), bg="white", fg="#4B0082").pack(pady=20)
        tk.Label(frame, text="This tab shows total calories burned by users.", font=("Arial", 12), bg="white", fg="black").pack(pady=10)
        return frame

    def create_active_frame(self):
        frame = tk.Frame(self, bg="white")
        tk.Label(frame, text="Total Active Hours: xx hours", font=("Arial", 18), bg="white", fg="#4B0082").pack(pady=20)
        tk.Label(frame, text="This tab shows the total active hours logged by users.", font=("Arial", 12), bg="white", fg="black").pack(pady=10)
        return frame

    def create_popular_frame(self):
        frame = tk.Frame(self, bg="white")
        tk.Label(frame, text="Most Popular Activities", font=("Arial", 18), bg="white", fg="#4B0082").pack(pady=20)
        tk.Label(frame, text="This tab shows the most popular activities among users.", font=("Arial", 12), bg="white", fg="black").pack(pady=10)
        return frame

    def switch_tab(self, tab_name):
        # ซ่อน Frame ปัจจุบัน
        if self.current_tab_frame:
            self.current_tab_frame.pack_forget()

        # อัปเดตสีของปุ่ม Tabs
        for name, button in self.tab_buttons.items():
            if name == tab_name:
                button.configure(bg="#4B0082", fg="white")  # ปุ่มถูกเลือก
            else:
                button.configure(bg="#D3D3D3", fg="black")  # ปุ่มไม่ได้ถูกเลือก

        # แสดง Frame ใหม่
        self.current_tab_frame = self.tab_frames[tab_name]
        self.current_tab_frame.pack(fill="both", expand=True)


# เรียกใช้ App
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1024x768")
    root.title("Leaderboard Tabs Example")
    app = LeaderboardFrame(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
