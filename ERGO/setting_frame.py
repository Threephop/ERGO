import tkinter as tk
from tkinter import ttk

class SettingFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        # Volume control
        volume_frame = tk.Frame(self, bg="white")
        volume_frame.place(x=50, y=50, width=350, height=50)  # Increased width of the frame

        tk.Label(volume_frame, text="Volume", font=("Arial", 16), bg="white").place(x=0, y=10, width=80, height=30)

        # Scale widget for volume
        self.volume = tk.DoubleVar(value=50)  # Default value is 50
        self.volume_scale = tk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient="horizontal",
            length=200,  # Increased length of the scale
            variable=self.volume,
            bg="white",
            highlightthickness=0,
            troughcolor="lightgray",
            activebackground="blue"
        )
        self.volume_scale.place(x=90, y=0, width=200, height=50)

        # Label to display current volume
        self.volume_label = tk.Label(volume_frame, text=f"{int(self.volume.get())}%", font=("Arial", 12), bg="white")
        self.volume_label.place(x=300, y=10, width=50, height=30)  # Adjusted position to fit in the expanded frame

        # Update volume label whenever scale is moved
        self.volume.trace("w", self.update_volume_label)

        # Language control using a dropdown
        language_frame = tk.Frame(self, bg="white")
        language_frame.place(x=50, y=120, width=350, height=50)

        tk.Label(language_frame, text="Language", font=("Arial", 16), bg="white").place(x=0, y=10, width=100, height=30)

        self.language_var = tk.StringVar(value="Select")
        self.language_dropdown = ttk.Combobox(language_frame, textvariable=self.language_var, font=("Arial", 12), state="readonly")
        self.language_dropdown["values"] = ("English", "ภาษาไทย")
        self.language_dropdown.place(x=110, y=10, width=150, height=30)

    def update_volume_label(self, *args):
        self.volume_label.config(text=f"{int(self.volume.get())}%")

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Settings")
    root.geometry("800x400")

    setting_frame = SettingFrame(root)
    setting_frame.place(x=0, y=0, width=800, height=400)

    root.mainloop()
