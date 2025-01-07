import tkinter as tk

class SettingFrame(tk.Frame):
    def init(self, parent):
        super().init(parent, bg="white")
        tk.Label(self, text="You clicked Setting", font=("Arial", 24), bg="white").pack(expand=True)