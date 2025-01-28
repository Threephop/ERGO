import tkinter as tk
from tkinter import ttk

class SettingFrame(tk.Frame):
    def __init__(self, parent, change_language_callback):
        super().__init__(parent, bg="white")
        
        # Callback function to notify parent of language change
        self.change_language_callback = change_language_callback

        # Volume control
        volume_frame = tk.Frame(self, bg="white")
        volume_frame.place(x=50, y=50, width=350, height=50)

        self.volume_label = tk.Label(volume_frame, text="Volume", font=("PTT 45 Pride", 16), bg="white")
        self.volume_label.place(x=0, y=10, width=100, height=30)

        self.volume = tk.DoubleVar(value=50)  # Default value is 50
        self.volume_scale = tk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient="horizontal",
            length=200,
            variable=self.volume,
            bg="white",
            highlightthickness=0,
            troughcolor="lightgray",
            activebackground="blue"
        )
        self.volume_scale.place(x=100, y=0, width=200, height=50)

        self.volume_value_label = tk.Label(volume_frame, text=f"{int(self.volume.get())}%", font=("PTT 45 Pride", 12), bg="white")
        self.volume_value_label.place(x=300, y=10, width=50, height=30)

        self.volume.trace("w", self.update_volume_label)

        # Language control using a dropdown
        language_frame = tk.Frame(self, bg="white")
        language_frame.place(x=50, y=120, width=350, height=50)

        self.language_label = tk.Label(language_frame, text="Language", font=("PTT 45 Pride", 16), bg="white")
        self.language_label.place(x=0, y=10, width=100, height=30)

        self.language_var = tk.StringVar(value="Select")
        self.language_dropdown = ttk.Combobox(language_frame, textvariable=self.language_var, font=("PTT 45 Pride", 12), state="readonly")
        self.language_dropdown["values"] = ("English", "ภาษาไทย")
        self.language_dropdown.place(x=140, y=10, width=150, height=30)

        self.language_dropdown.bind("<<ComboboxSelected>>", self.change_language)

        self.translations = {
            "English": {
                "volume": "Volume",
                "language": "Language",
            },
            "ภาษาไทย": {
                "volume": "ระดับเสียง",
                "language": "ภาษา",
            },
        }

        self.update_language_ui("English")

    def update_volume_label(self, *args):
        self.volume_value_label.config(text=f"{int(self.volume.get())}%")

    def change_language(self, event):
        selected_language = self.language_var.get()
        self.update_language_ui(selected_language)

        # Notify parent (main.py) about language change
        self.change_language_callback(selected_language)

    def update_language_ui(self, language):
        translations = self.translations.get(language, {})
        if translations:
            self.volume_label.config(text=translations.get("volume", "Volume"))
            self.language_label.config(text=translations.get("language", "Language"))
            

# Example usage in main.py
if __name__ == "__main__":
    def on_language_change(language):
        print(f"Language changed to: {language}")

    root = tk.Tk()
    root.title("Settings")
    root.geometry("800x400")

    setting_frame = SettingFrame(root, change_language_callback=on_language_change)
    setting_frame.place(x=0, y=0, width=800, height=400)

    root.mainloop()
