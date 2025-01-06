import tkinter as tk

class DashboardFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        tk.Label(self, text="You clicked Dashboard", font=("Arial", 24), bg="white").pack(expand=True)
