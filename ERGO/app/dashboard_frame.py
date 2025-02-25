import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from customtkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
import urllib.parse
import re
import os
import requests

class DashboardFrame(ctk.CTkFrame):  # ✅ ใช้ CTkFrame แทน Frame
    def __init__(self, parent, user_email):
        super().__init__(parent, fg_color="white")
        self.api_base_url = "http://127.0.0.1:8000"  
        self.user_id = self.fetch_user_id(user_email)  
        self.user_email = user_email  
        self.user_role = self.fetch_user_role(user_email)  

        # ✅ สร้าง Notebook (ใช้แท็บของ Tkinter)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # ✅ สร้าง Style สำหรับแต่งแท็บ
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("PTT 45 Pride", 12, "bold"), padding=[10, 5])
        style.configure("TNotebook", background="white")  # สีพื้นหลังของ Notebook

        # ✅ สร้าง Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ สร้างแท็บ
        self.tab1 = tk.Frame(self.notebook, bg="#ffffff", bd=3, relief="solid")
        self.tab2 = tk.Frame(self.notebook, bg="#ffffff", bd=3, relief="solid")
        self.tab3 = tk.Frame(self.notebook, bg="#ffffff", bd=3, relief="solid")

        self.notebook.add(self.tab1, text="Active")  
        self.notebook.add(self.tab2, text="Like")  
        self.notebook.add(self.tab3, text="Calories")  # เพิ่ม Tab 3

        # ✅ วาง widget ในแต่ละแท็บ
        self.create_content(self.tab1, "Active", "#000000")
        self.create_content(self.tab2, "Like", "#000000")
        self.create_content(self.tab3, "Calories", "#000000")

    def create_content(self, parent, text, color):
        """ สร้าง Label แสดงข้อความในแต่ละแท็บ """
        label = tk.Label(parent, text=text, font=("PTT 45 Pride", 14), fg=color, bg="white")
        label.pack(pady=10) 

        # ✅ วาง widget ต่างๆ ใน tab1
        self.create_chart(self.tab1)  # ส่ง self.tab1 ไปเป็น parent
        self.create_activity_details(self.tab1)

        # 🔹 ปุ่ม Export Excel (อยู่ใน tab1)
        self.export_button = ctk.CTkButton(self.tab1, text="Export Excel", corner_radius=25, command=self.export_excel_active)
        self.export_button.pack(pady=10)
        
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
        return None
        
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

    def fetch_user_role(self, email):
        """ 🔹 ดึง role ของผู้ใช้จาก API """
        try:
            response = requests.get(f"{self.api_base_url}/get_user_role/{email}")
            if response.status_code == 200:
                return response.json().get("role")
            else:
                return None
        except requests.exceptions.RequestException:
            return None

    def create_chart(self, parent):
        """Function to create bar chart"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        active_hours = self.fetch_usage_data()  

        # Chart Frame
        chart_frame = ttk.LabelFrame(parent, text="Statistics", padding=(10, 10))
        chart_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Create chart
        fig, ax = plt.subplots(figsize=(12, 4))
        bars = ax.bar(days, active_hours, color="#1f6eb0", width=0.4)

        ax.set_xlabel("Week", fontsize=12)
        ax.set_ylabel("Active (hours)", fontsize=12)
        ax.set_title("Activity Over the Week", fontsize=14)

        ax.set_xticks(range(len(days)))
        ax.set_xticklabels(days, rotation=0, ha="center", fontsize=9)

        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), ha="center", va="bottom", fontsize=10)

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)

    def create_activity_details(self, parent):
        """Function to create activity details section"""
        activity_frame = ttk.LabelFrame(parent, text="Activity", padding=(10, 10))
        activity_frame.pack(padx=10, pady=10, fill="both", expand=True)

        labels = ["Date", "User", "Timer", "Calorie", "Stance"]
        details = ["01/01/2024", "NameUser", "1 hour", "324 kcal", "บริหารร่างกาย"]

        for i, (label, detail) in enumerate(zip(labels, details)):
            ttk.Label(activity_frame, text=label, font=("PTT 45 Pride", 12, "bold")).grid(row=0, column=i, padx=5, pady=5)
            ttk.Label(activity_frame, text=detail, font=("PTT 45 Pride", 12)).grid(row=1, column=i, padx=5, pady=5)

    def export_excel_active(self):
        """ 🔹 ตรวจสอบสิทธิ์ก่อนส่งคำขอ Export """
        if self.user_role != 1:
            messagebox.showerror("Permission Denied", "You don't have permission to export data")
            return

        try:
            response = requests.get(f"{self.api_base_url}/export_dashboard_active/?email={self.user_email}")

            if response.status_code == 200:
                content_disposition = response.headers.get("Content-Disposition", "")
                filename = content_disposition.split("filename=")[-1].strip("\"")

                filename = urllib.parse.unquote(filename)
                filename = re.sub(r'[^a-zA-Z0-9_\-\. ]', '', filename)

                if not filename:
                    filename = "dashboard_active.xlsx"

                downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
                file_path = os.path.join(downloads_folder, filename)

                messagebox.showinfo("Success", f"Excel file ({filename}) has been saved to your Downloads folder!")
            else:
                messagebox.showerror("Error", response.json().get("detail", "Unknown error"))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Failed to connect to the server")
