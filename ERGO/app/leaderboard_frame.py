import tkinter as tk
import customtkinter as ctk
from customtkinter import *
import requests
import urllib.parse
import re
import os
from tkinter import messagebox
import threading

params = {
    "x_api_key": "ergoapipoC18112024",  # ส่ง API Key ใน query parameter
}

class LeaderboardFrame(tk.Frame):
    def __init__(self, master, user_email):
        super().__init__(master, bg="white")
        self.master = master
        self.current_tab_frame = None
        self.api_base_url = "https://ergoapicontainer.kindfield-b150dbf6.southeastasia.azurecontainerapps.io"  
        self.user_email = user_email
        self.user_role = self.fetch_user_role(user_email) 

        # Header สำหรับ Leaderboard
        title_label = tk.Label(self, text="Leader-board", font=("PTT 45 Pride", 24, "bold"), bg="white", fg="black")
        title_label.pack(pady=10)

        # Tabs Frame
        tabs_frame = tk.Frame(self, bg="white")
        tabs_frame.pack(pady=10)

        # ในส่วน __init__ ของคลาส LeaderboardFrame เพิ่มปุ่ม Refresh
        refresh_button = ctk.CTkButton(
            self,
            text="Refresh",
            font=("PTT 45 Pride", 14),
            corner_radius=25,
            fg_color="#0078D4",
            command=self.refresh_data
        )
        refresh_button.place(relx=0.95, rely=0.02, anchor="ne")

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
            response = requests.get(f"{self.api_base_url}/get_user_role/{email}", params=params)
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
                response = requests.get("https://ergoapicontainer.kindfield-b150dbf6.southeastasia.azurecontainerapps.io/showstat", params=params)
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
                sorted_stats = sorted(stats, key=lambda x: x["hours_used"], reverse=True)  
                top_user = sorted_stats[0]["username"] if sorted_stats else "N/A"
                self.active_label.config(text=f"Most Active User: {top_user}")
                self.display_users(self.active_list_frame, sorted_stats, "hours_used")

            elif tab_name == "Popular":
                sorted_stats = sorted(stats, key=lambda x: x["like_count"], reverse=True)  
                top_user = sorted_stats[0]["username"] if sorted_stats else "N/A"
                self.popular_label.config(text=f"Most Popular User: {top_user}")
                self.display_users(self.popular_list_frame, sorted_stats, "like_count")

            # ปุ่ม Export สำหรับ Admin เท่านั้น
            if role == 1:
                if tab_name == "Active":
                    if hasattr(self, "export_button") and self.export_button is not None:
                        self.export_button.destroy()
                    self.export_button_active = ctk.CTkButton(
                        self.active_list_frame, text="Export Excel Active",
                        font=("PTT 45 Pride", 16), corner_radius=25, fg_color="#176E1B",
                        command=self.export_active_excel
                    )
                    self.export_button_active.pack(pady=10)

                elif tab_name == "Popular":
                    if hasattr(self, "export_button") and self.export_button is not None:
                        self.export_button.destroy()
                    self.export_button_popular = ctk.CTkButton(
                        self.popular_list_frame, text="Export Excel Popular",
                        font=("PTT 45 Pride", 16), corner_radius=25, fg_color="#176E1B",
                        command=self.export_popular_excel
                    )
                    self.export_button_popular.pack(pady=10)


    def export_active_excel(self):
        """ 🔹 ตรวจสอบสิทธิ์ก่อนส่งคำขอ Export """
        if self.user_role != 1:
            messagebox.showerror("Permission Denied", "You don't have permission to export data")
            return

        try:
            response = requests.get(f"{self.api_base_url}/export_leaderboard_active/?email={self.user_email}",params=params , stream=True)

            if response.status_code == 200:
                # ให้ user เลือกที่บันทึกไฟล์เอง
                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

                if file_path:
                    with open(file_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    messagebox.showinfo("Success", f"Excel file has been saved to {file_path}!")
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
            response = requests.get(f"{self.api_base_url}/export_leaderboard_popular/?email={self.user_email}",params=params , stream=True)

            if response.status_code == 200:
                # ให้ user เลือกที่บันทึกไฟล์เอง
                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

                if file_path:
                    with open(file_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    messagebox.showinfo("Success", f"Excel file has been saved to {file_path}!")
            else:
                messagebox.showerror("Error", response.json().get("detail", "Unknown error"))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Failed to connect to the server")

    def display_users(self, frame, stats, key):
        for widget in frame.winfo_children():
            widget.destroy()

        for idx, user in enumerate(stats):
            value = user[key]  # ใช้ key ที่ส่งมา
            text = f"{idx+1}. {user['username']} | {value} {'hrs' if key == 'hours_used' else 'likes'}"
            
            name_label = tk.Label(
                frame, text=text, font=("PTT 45 Pride", 12),
                bg="white", fg="black"
            )
            name_label.pack(anchor="w", padx=20, pady=2)

    def refresh_data(self):
        self.fetch_users("Active")
        self.fetch_users("Popular")


    # เรียกใช้ App
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1024x768")
    root.title("Leaderboard Tabs Example")
    app = LeaderboardFrame(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
