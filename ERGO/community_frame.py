import tkinter as tk
from tkinter import filedialog
import os
from PIL import Image, ImageTk

class CommunityFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Define the directory for icons
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")

        # Main area for displaying messages
        self.text_area = tk.Text(self, wrap="word", font=("Arial", 14), state="disabled", bg="white", height=20)
        self.text_area.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Create a container frame for the bottom bar
        self.bottom_bar = tk.Frame(self)
        self.bottom_bar.pack(side="bottom", fill="x", padx=10, pady=10)

        # Helper function to load and resize images
        def load_resized_image(file_name, size):
            try:
                path = os.path.join(self.icon_dir, file_name)
                image = Image.open(path)
                image = image.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error loading {file_name}: {e}")
                return None

        # Load images for buttons and profile
        self.camera_icon = load_resized_image("camera.png", (45, 40))
        self.folder_icon = load_resized_image("folder.png", (50, 47))
        self.send_icon = load_resized_image("send.png", (30, 30))
        self.profile_icon = load_resized_image("profile.png", (50, 50))  # Example profile icon

        # Icon buttons
        self.camera_button = tk.Button(self.bottom_bar, image=self.camera_icon, command=self.open_camera, bd=0)
        self.camera_button.grid(row=0, column=0, padx=(10, 5), pady=10)

        self.folder_button = tk.Button(self.bottom_bar, image=self.folder_icon, command=self.open_folder, bd=0)
        self.folder_button.grid(row=0, column=1, padx=5, pady=10)

        # Frame for Entry and Send button
        self.entry_frame = tk.Frame(self.bottom_bar, bd=1, relief="sunken")
        self.entry_frame.grid(row=0, column=2, padx=5, pady=10, sticky="ew")

        # Entry field
        self.entry = tk.Entry(self.entry_frame, font=("Arial", 14), bd=0, width=55)
        self.default_text = "\u0e02\u0e49\u0e2d\u0e04\u0e27\u0e32\u0e21"  # Default text in Thai
        self.entry.insert(0, self.default_text)
        self.entry.pack(side="left", fill="x", expand=True, padx=(10, 5))

        # Bind focus-in event to clear default text
        self.entry.bind("<FocusIn>", self.clear_default_text)

        # Bind Enter key to send_message function
        self.entry.bind("<Return>", lambda event: self.send_message())

        # Send button inside Entry frame
        self.send_button = tk.Button(self.entry_frame, image=self.send_icon, command=self.send_message, bd=0)
        self.send_button.pack(side="right", padx=5)

        # Adjust column weights for flexible resizing
        self.bottom_bar.columnconfigure(3, weight=1, minsize=300)

    def open_camera(self):
        print("Camera button clicked")

    def open_folder(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png"), ("All files", "*.*")])
        if filepath:
            print(f"Selected file: {filepath}")

    def send_message(self):
        # Get the message from the entry field
        message = self.entry.get()
        if message.strip():  # Check if the message is not empty
            # Enable text area to insert the message
            self.text_area.config(state="normal")

            # Add profile image
            self.text_area.image_create("end", image=self.profile_icon)

            # Add message
            self.text_area.insert("end", f" {message}\n", "message")

            # Add username below the message
            self.text_area.insert("end", "  Username\n", "username")

            # Scroll to the bottom and disable text editing
            self.text_area.see("end")
            self.text_area.config(state="disabled")

            # Clear the entry field
            self.entry.delete(0, "end")
            print(f"Message sent: {message}")

    def clear_default_text(self, event):
        if self.entry.get() == self.default_text:
            self.entry.delete(0, "end")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Community Frame")

    frame = CommunityFrame(root)
    frame.pack(fill="both", expand=True)

    root.mainloop()
