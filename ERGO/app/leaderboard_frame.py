import tkinter as tk
import customtkinter as ctk
import requests
import urllib.parse
import re
import os
from tkinter import messagebox
import threading

class LeaderboardFrame(tk.Frame):
    def __init__(self, master, user_email):
        super().__init__(master, bg="white")
        self.master = master
        self.current_tab_frame = None
        self.api_base_url = "http://127.0.0.1:8000"  
        self.user_email = user_email
        self.user_role = self.fetch_user_role(user_email) 

        # Header สำหรับ Leaderboard
        title_label = tk.Label(self, text="Leader-board", font=("PTT 45 Pride", 24, "bold"), bg="white", fg="black")
        title_label.pack(pady=10)

        # Tabs Frame
        tabs_frame = tk.Frame(self, bg="white")
        tabs_frame.pack(pady=10)

        # ปุ่มแท็บ
        self.tab_buttons = {}
        for idx, tab_name in enumerate(["Active", "Popular"]):
            btn = tk.Button(
                tabs_frame,
                text=tab_name,
                font=("PTT 45 Pride", 12),
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
            "Active": self.create_active_frame(),
            "Popular": self.create_popular_frame(),
        }

        self.switch_tab("Active")  # เริ่มต้นที่แท็บแรก
        
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

    def create_active_frame(self):
        frame = tk.Frame(self, bg="white")
        self.active_label = tk.Label(frame, text="Loading...", font=("PTT 45 Pride", 18), bg="white", fg="#4B0082")
        self.active_label.pack(pady=10)
        self.active_list_frame = tk.Frame(frame, bg="white")
        self.active_list_frame.pack(pady=5)
        
        return frame

    def create_popular_frame(self):
        frame = tk.Frame(self, bg="white")
        self.popular_label = tk.Label(frame, text="Loading...", font=("PTT 45 Pride", 18), bg="white", fg="#4B0082")
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
            role = self.user_role

            if tab_name == "Active":
                sorted_stats = sorted(stats, key=lambda x: x["hours_used"], reverse=True)  # เรียงจากมากไปน้อย
                top_user = sorted_stats[0]["username"] if sorted_stats else "N/A"
                self.active_label.config(text=f"Most Active Hours: {top_user}")
                self.display_users(self.active_list_frame, sorted_stats)

            elif tab_name == "Popular":
                sorted_stats = sorted(stats, key=lambda x: x["like_count"], reverse=True)  # เปลี่ยนเป็น like_count
                top_user = sorted_stats[0]["username"] if sorted_stats else "N/A"
                self.popular_label.config(text=f"Most Popular User: {top_user}")
                self.display_users(self.popular_list_frame, sorted_stats)
                
            if role == 1 and tab_name == "Active":
                # ถ้ามีปุ่ม export_button อยู่แล้ว ให้ลบก่อน
                if hasattr(self, "export_button") and self.export_button is not None:
                    self.export_button.destroy()

                # สร้างปุ่มใหม่
                self.export_button_active = ctk.CTkButton(
                    self.active_list_frame, text="Export Excel Active", font = ("PTT 45 Pride", 16),
                    corner_radius=25,
                    fg_color = "#176E1B", command=self.export_active_excel)
                self.export_button_active.pack(pady=10)
                
            if role == 1 and tab_name == "Popular":
                # ถ้ามีปุ่ม export_button อยู่แล้ว ให้ลบก่อน
                if hasattr(self, "export_button") and self.export_button is not None:
                    self.export_button.destroy()

                # สร้างปุ่มใหม่
                self.export_button_popular = ctk.CTkButton(
                    self.popular_list_frame, text="Export Excel Popular", font = ("PTT 45 Pride", 16),
                    corner_radius=25,
                    fg_color = "#176E1B", command=self.export_popular_excel)
                self.export_button_popular.pack(pady=10)

    def export_active_excel(self):
        """ 🔹 ตรวจสอบสิทธิ์ก่อนส่งคำขอ Export """
        if self.user_role != 1:
            messagebox.showerror("Permission Denied", "You don't have permission to export data")
            return

        try:
            response = requests.get(f"{self.api_base_url}/export_leaderboard_active/?email={self.user_email}")

            if response.status_code == 200:
                content_disposition = response.headers.get("Content-Disposition", "")
                filename = content_disposition.split("filename=")[-1].strip("\"")

                filename = urllib.parse.unquote(filename)
                filename = re.sub(r'[^a-zA-Z0-9_\-\. ]', '', filename)

                if not filename:
                    filename = "leaderboard_active.xlsx"

                downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
                file_path = os.path.join(downloads_folder, filename)

                messagebox.showinfo("Success", f"Excel file ({filename}) has been saved to your Downloads folder!")
            else:
                messagebox.showerror("Error", response.json().get("detail", "Unknown error"))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Failed to connect to the server")
        
    def export_popular_excel(self):
        """ 🔹 ตรวจสอบสิทธิ์ก่อนส่งคำขอ Export """
        if self.user_role != 1:
            messagebox.showerror("Permission Denied", "You don't have permission to export data")
            return

        try:
            response = requests.get(f"{self.api_base_url}/export_leaderboard_popular/?email={self.user_email}")

            if response.status_code == 200:
                content_disposition = response.headers.get("Content-Disposition", "")
                filename = content_disposition.split("filename=")[-1].strip("\"")

                filename = urllib.parse.unquote(filename)
                filename = re.sub(r'[^a-zA-Z0-9_\-\. ]', '', filename)

                if not filename:
                    filename = "leaderboard_popular.xlsx"

                downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
                file_path = os.path.join(downloads_folder, filename)

                messagebox.showinfo("Success", f"Excel file ({filename}) has been saved to your Downloads folder!")
            else:
                messagebox.showerror("Error", response.json().get("detail", "Unknown error"))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Failed to connect to the server")

    def display_users(self, frame, stats):
        for widget in frame.winfo_children():
            widget.destroy()

        for idx, user in enumerate(stats):
            name_label = tk.Label(
                frame,
                text=f"{idx+1}. {user['username']} | {user['hours_used']} hrs | {user['like_count']} likes",  # เปลี่ยนเป็น like_count
                font=("PTT 45 Pride", 12),
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
