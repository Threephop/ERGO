import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests

class DashboardFrame(tk.Frame):
    def __init__(self, parent,user_email):
        super().__init__(parent)
        self.api_base_url = "http://127.0.0.1:8000"  # ✅ กำหนดค่าก่อน
        self.user_id = self.fetch_user_id(user_email)  # ✅ เรียกใช้หลังจากกำหนดค่า api_base_url
        

        # Create chart
        self.create_chart()

        # Create activity details section
        self.create_activity_details()
        
    def fetch_user_id(self, user_email):
        """ดึง user_id จาก API"""
        url = f"{self.api_base_url}/get_user_id/{user_email}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if "user_id" in data:
                    return data["user_id"]
            print("Error fetching user_id:", response.json().get("error", "Unknown error"))
        except Exception as e:
            print("Exception:", e)
        return None  # ถ้าหาไม่เจอให้ return None
        
    def fetch_usage_data(self):
        """ดึงข้อมูล active_hours จาก API"""
        if self.user_id is None:
            print("No user_id found.")
            return [0, 0, 0, 0, 0, 0, 0]

        url = f"{self.api_base_url}/get_usage_stats/{self.user_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return [
                    data.get("Monday", 0), data.get("Tuesday", 0), data.get("Wednesday", 0),
                    data.get("Thursday", 0), data.get("Friday", 0), data.get("Saturday", 0), data.get("Sunday", 0)
                ]
            else:
                print("Error fetching data:", response.status_code)
        except Exception as e:
            print("Exception:", e)
        return [0, 0, 0, 0, 0, 0, 0]


    def create_chart(self):
        """Function to create bar chart"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        active_hours = self.fetch_usage_data()  # ดึงข้อมูลจาก API

        # Chart Frame
        chart_frame = ttk.LabelFrame(self, text="Statistics", padding=(10, 10))
        chart_frame.place(x=5, y=10, relwidth=0.8, relheight=0.6)

        # Create chart
        fig, ax = plt.subplots(figsize=(12, 4))
        bars = ax.bar(days, active_hours, color="#1f6eb0", width=0.4)

        # Apply font, labels without italic
        ax.set_xlabel("Week", fontsize=12)
        ax.set_ylabel("Active (hours)", fontsize=12)
        ax.set_title("Activity Over the Week", fontsize=14)

        # Set ticks for x-axis
        ax.set_xticks(range(len(days)))
        ax.set_xticklabels(days, rotation=0, ha="center", fontsize=9)

        # แสดงตัวเลขบนแท่งกราฟ
        for bar in bars:
            yval = bar.get_height()  # ความสูงของแท่ง (จำนวนชั่วโมง)
            ax.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), ha="center", va="bottom", fontsize=10)

        # Embed chart into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)




    def create_activity_details(self):
        """Function to create activity details section"""
        # Activity Frame
        activity_frame = ttk.LabelFrame(self, text="Activity", padding=(10, 10))
        activity_frame.place(x=10, y=520, relwidth=0.6, relheight=0.3)

        # Add labels
        labels = ["Date", "User", "Timer", "Calorie", "Stance"]
        details = ["01/01/2024", "NameUser", "1 hour", "324 kcal", "บริหารร่างกาย"]

        for i, (label, detail) in enumerate(zip(labels, details)):
            ttk.Label(activity_frame, text=label, font=("Arial", 12, "bold")).grid(row=0, column=i, padx=5, pady=5)
            ttk.Label(activity_frame, text=detail, font=("Arial", 12)).grid(row=1, column=i, padx=5, pady=5)
