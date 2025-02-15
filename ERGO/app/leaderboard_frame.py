import tkinter as tk
import requests
import threading

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

        # ปุ่มแท็บ
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
            btn.pack(side="left", padx=0)
            self.tab_buttons[tab_name] = btn

        # Default Tab Content
        self.tab_frames = {
            "Calorie": self.create_calorie_frame(),
            "Active": self.create_active_frame(),
            "Popular": self.create_popular_frame(),
        }

        self.switch_tab("Calorie")  # เริ่มต้นที่แท็บแรก

    def create_calorie_frame(self):
        frame = tk.Frame(self, bg="white")
        self.calorie_label = tk.Label(frame, text="Loading...", font=("Arial", 18), bg="white", fg="#4B0082")
        self.calorie_label.pack(pady=10)
        self.calorie_list_frame = tk.Frame(frame, bg="white")
        self.calorie_list_frame.pack(pady=5)
        return frame

    def create_active_frame(self):
        frame = tk.Frame(self, bg="white")
        self.active_label = tk.Label(frame, text="Loading...", font=("Arial", 18), bg="white", fg="#4B0082")
        self.active_label.pack(pady=10)
        self.active_list_frame = tk.Frame(frame, bg="white")
        self.active_list_frame.pack(pady=5)
        return frame

    def create_popular_frame(self):
        frame = tk.Frame(self, bg="white")
        self.popular_label = tk.Label(frame, text="Loading...", font=("Arial", 18), bg="white", fg="#4B0082")
        self.popular_label.pack(pady=10)
        self.popular_list_frame = tk.Frame(frame, bg="white")
        self.popular_list_frame.pack(pady=5)
        return frame

    def switch_tab(self, tab_name):
        if self.current_tab_frame:
            self.current_tab_frame.pack_forget()

        for name, button in self.tab_buttons.items():
            button.configure(bg="#4B0082", fg="white" if name == tab_name else "black")

        self.current_tab_frame = self.tab_frames[tab_name]
        self.current_tab_frame.pack(fill="both", expand=True)

        self.fetch_users(tab_name)

    def fetch_users(self, tab_name):
        def fetch():
            try:
                response = requests.get("http://localhost:8000/showstat")
                if response.status_code == 200:
                    data = response.json()
                    self.update_ui(tab_name, data)
                else:
                    self.update_ui(tab_name, {"error": "Failed to fetch data"})
            except Exception as e:
                self.update_ui(tab_name, {"error": str(e)})

        thread = threading.Thread(target=fetch)
        thread.daemon = True
        thread.start()

    def update_ui(self, tab_name, data):
        if "error" in data:
            text = f"Error: {data['error']}"
        else:
            stats = data.get("stats", [])

            if tab_name == "Calorie":
                sorted_stats = sorted(stats, key=lambda x: x["kcal_burned"], reverse=True)  # เรียงจากมากไปน้อย
                top_user = sorted_stats[0]["username"] if sorted_stats else "N/A"
                self.calorie_label.config(text=f"Most Calories Burned: {top_user}")
                self.display_users(self.calorie_list_frame, sorted_stats)

            elif tab_name == "Active":
                sorted_stats = sorted(stats, key=lambda x: x["hours_used"], reverse=True)  # เรียงจากมากไปน้อย
                top_user = sorted_stats[0]["username"] if sorted_stats else "N/A"
                self.active_label.config(text=f"Most Active Hours: {top_user}")
                self.display_users(self.active_list_frame, sorted_stats)

            elif tab_name == "Popular":
                sorted_stats = sorted(stats, key=lambda x: x["like_count_id"], reverse=True)  # เรียงจากมากไปน้อย
                top_user = sorted_stats[0]["username"] if sorted_stats else "N/A"
                self.popular_label.config(text=f"Most Popular User: {top_user}")
                self.display_users(self.popular_list_frame, sorted_stats)


    def display_users(self, frame, stats):
        for widget in frame.winfo_children():
            widget.destroy()

        for idx, user in enumerate(stats):
            name_label = tk.Label(
                frame,
                text=f"{idx+1}. {user['username']} | {user['hours_used']} hrs | {user['kcal_burned']} kcal | {user['like_count_id']} likes",
                font=("Arial", 12),
                bg="white",
                fg="black",
            )
            name_label.pack(anchor="w", padx=20, pady=2)



# เรียกใช้ App
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1024x768")
    root.title("Leaderboard Tabs Example")
    app = LeaderboardFrame(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
