import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DashboardFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Create chart
        self.create_chart()

        # Create activity details section
        self.create_activity_details()

    def create_chart(self):
        """Function to create bar chart"""
        # Sample data
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        active_hours = [4, 6, 2, 5, 3, 6, 8]

        # Chart Frame
        chart_frame = ttk.LabelFrame(self, text="Statistics", padding=(10, 10))
        chart_frame.place(x=10, y=10, relwidth=0.6, relheight=0.4)  # Using place instead of pack

        # Create chart
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.bar(days, active_hours, color="blue")
        ax.set_xlabel("Week")
        ax.set_ylabel("Active (hours)")
        ax.set_title("Activity Over the Week")

        # Embed chart into Tkinter
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)

    def create_activity_details(self):
        """Function to create activity details section"""
        # Activity Frame
        activity_frame = ttk.LabelFrame(self, text="Activity", padding=(10, 10))
        activity_frame.place(x=10, y=300, relwidth=0.6, relheight=0.3)  # Using place instead of pack

        # Add labels
        labels = ["Date", "User", "Timer", "Calorie", "Stance"]
        details = ["01/01/2024", "NameUser", "1 hour", "324 kcal", "บริหารร่างกาย"]

        for i, (label, detail) in enumerate(zip(labels, details)):
            ttk.Label(activity_frame, text=label, font=("Arial", 12, "bold")).grid(row=0, column=i, padx=5, pady=5)
            ttk.Label(activity_frame, text=detail, font=("Arial", 12)).grid(row=1, column=i, padx=5, pady=5)

