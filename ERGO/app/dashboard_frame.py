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
from PIL import Image, ImageTk
import cv2

params = {
    "x_api_key": "ergoapipoC18112024",  # ส่ง API Key ใน query parameter
}

class DashboardFrame(ctk.CTkFrame):  # ✅ ใช้ CTkFrame แทน Frame
    def __init__(self, parent, user_email):
        super().__init__(parent, fg_color="white")
        self.api_base_url = "http://127.0.0.1:8000"  
        self.user_id = self.fetch_user_id(user_email)  
        self.user_email = user_email  
        self.user_role = self.fetch_user_role(user_email)  
        self.image_dir = os.path.join(os.path.dirname(__file__), "imageVideo")

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

        # ✅ วาง widget ในแต่ละแท็บ
        self.create_content(self.tab1, "Active", "#000000", self.user_role)
        self.create_content(self.tab2, "Like", "#000000", self.user_role)

    def create_content(self, parent, text, color, role):
        """ สร้าง Label แสดงข้อความในแต่ละแท็บ """
        label = tk.Label(parent, text=text, font=("PTT 45 Pride", 14), fg=color, bg="white")
        label.pack(pady=5)  # ลด pady ที่นี่

        if text == "Active":  # เฉพาะแท็บ "Active" ที่จะสร้างกราฟและปุ่ม Export
            self.create_chart(self.tab1)  # ส่ง self.tab1 ไปเป็น parent
            self.create_activity_details(self.tab1, self.user_email)  # เรียกใช้แค่ใน tab1
        elif text == "Like":
            self.create_video_list(self.tab2)
        else:
            pass

        
    def fetch_user_id(self, user_email):
        """ดึง user_id จาก API"""
        url = f"{self.api_base_url}/get_user_id/{user_email}"
        try:
            response = requests.get(url, params)
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
            response = requests.get(url, params)
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
            response = requests.get(f"{self.api_base_url}/get_user_role/{email}", params)
            if response.status_code == 200:
                return response.json().get("role")
            else:
                return None
        except requests.exceptions.RequestException:
            return None

    def fetch_monthly_usage_data(self):
        """ดึงข้อมูล active_hours รายเดือนจาก API"""
        if self.user_id is None:
            print("No user_id found.")
            return [0] * 12  # ค่าเริ่มต้นเป็นศูนย์

        url = f"{self.api_base_url}/get_monthly_usage_stats/{self.user_id}"
        try:
            response = requests.get(url, params)
            if response.status_code == 200:
                data = response.json()
                return [
                    data.get("January", 0), data.get("February", 0), data.get("March", 0),
                    data.get("April", 0), data.get("May", 0), data.get("June", 0),
                    data.get("July", 0), data.get("August", 0), data.get("September", 0),
                    data.get("October", 0), data.get("November", 0), data.get("December", 0)
                ]
            else:
                print("Error fetching data:", response.status_code)
        except Exception as e:
            print("Exception:", e)
        return [0] * 12  # ค่าเริ่มต้นเป็นศูนย์

    def update_chart(self, filter_option):
        """อัปเดตกราฟตามค่าที่เลือก"""
        if filter_option == "Week":
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            active_hours = self.fetch_usage_data()
            xlabel = "Week"
            title = "Activity Over the Week"
            rotation_angle = 0  # ไม่ต้องหมุนข้อความ
            fontsize = 10  # ปรับขนาดตัวอักษร
        else:
            days = ["January", "February", "March", "April", "May", "June", 
                    "July", "August", "September", "October", "November", "December"]
            active_hours = self.fetch_monthly_usage_data()
            xlabel = "Month"
            title = "Activity Over the Year"
            rotation_angle = 30  # หมุนข้อความเพื่อให้แสดงเต็มที่
            fontsize = 7  # ลดขนาดตัวอักษร

        self.ax.clear()
        bars = self.ax.bar(days, active_hours, color="#1f6eb0", width=0.4)

        self.ax.set_ylabel("Active (hours)", fontsize=12)
        self.ax.set_title(title, fontsize=14)

        self.ax.set_xticks(range(len(days)))
        self.ax.set_xticklabels(days, rotation=rotation_angle, ha="right", fontsize=fontsize)  # ✅ ปรับขนาดตัวหนังสือ

        for bar in bars:
            yval = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), ha="center", va="bottom", fontsize=8)

        self.canvas.draw()
    

    def create_activity_details(self, parent, user_email):
        """สร้าง Activity Table"""

        # ✅ เช็คว่ามี Activity Table แล้วหรือยัง
        if hasattr(self, "activity_frame"):
            return  # ❌ ถ้ามีแล้ว ไม่ต้องสร้างใหม่

        # ✅ สร้าง Frame ของ Activity Table
        self.activity_frame = ttk.LabelFrame(parent, text="Activity", padding=(5, 1))  # ปรับค่า padding เพื่อให้พื้นที่ในแกน Y แคบลง
        self.activity_frame.pack(padx=10, pady=2, fill="both", expand=True)

        # ✅ สร้าง Treeview ครั้งเดียว
        self.tree = ttk.Treeview(self.activity_frame, columns=(), show="headings")
        self.tree.pack(fill="both", expand=True, pady=(0, 10))  # ปรับ pady ที่ Treeview เพื่อจัดการพื้นที่ว่างในแนว Y

        # ✅ อัปเดตตาราง (Week เป็นค่าเริ่มต้น)
        self.update_activity_table("Week", user_email)


 
    def create_chart(self, parent):
        """สร้างกราฟพร้อมตัวเลือก Filter"""
        self.chart_frame = ttk.LabelFrame(parent, text="Statistics", padding=(10, 5))
        self.chart_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # ✅ สร้าง Filter Dropdown
        self.filter_var = tk.StringVar(value="Week")  
        self.filter_dropdown = ttk.Combobox(self.chart_frame, textvariable=self.filter_var, state="readonly", 
                                            values=["Week", "Month"], width=10)
        self.filter_dropdown.pack(pady=5)

        # ✅ อัปเดตทั้งกราฟและตารางเมื่อเลือก Filter ใหม่
        self.filter_dropdown.bind("<<ComboboxSelected>>", lambda e: self.on_filter_change())

        # ✅ สร้างกราฟ
        self.fig, self.ax = plt.subplots(figsize=(12, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        # ✅ สร้าง Activity Table ก่อนเรียก update_activity_table()
        self.create_activity_details(parent, self.user_email)

        # ✅ แสดงข้อมูลเริ่มต้น (Week)
        self.update_chart("Week")

  

    def get_video_thumbnail(self, video_url, post_id):
        """ ดึง Thumbnail จากเฟรมแรกของวิดีโอและบันทึกใน icon/ """
        try:
            cap = cv2.VideoCapture(video_url)
            success, frame = cap.read()
            cap.release()

            if success:
                thumbnail_filename = f"thumbnail_{post_id}.jpg"
                save_path = os.path.join(self.image_dir, thumbnail_filename)  # 🔹 บันทึกที่ icon/

                cv2.imwrite(save_path, frame)  # ✅ บันทึกไฟล์ Thumbnail

                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                img = img.resize((150, 100), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)

        except Exception as e:
            print(f"❌ Error loading thumbnail: {e}")
        
        return None  # ✅ ถ้าล้มเหลวให้คืนค่า None

    def is_valid_url(self, url):
        """ ตรวจสอบว่า URL สามารถเข้าถึงได้หรือไม่ """
        try:
            response = requests.head(url, params={"x_api_key": "ergoapipoC18112024"}, allow_redirects=True, timeout=5)  # ใช้ HEAD request เพื่อเช็คว่า URL ใช้งานได้
            return response.status_code == 200  # ถ้าสถานะ 200 แปลว่า URL ใช้งานได้
        except requests.RequestException:
            return False  # ถ้ามี error แปลว่า URL ใช้ไม่ได้

    def create_video_list(self, parent, videos=None):
        """ สร้าง UI แสดงวิดีโอของผู้ใช้ และ Like Count """

        # ✅ ถ้า videos ไม่มี ให้ดึงข้อมูลจาก API
        if videos is None:
            videos = self.get_user_videos()

        # ✅ สร้าง LabelFrame
        video_frame = ttk.LabelFrame(parent, text="My Videos", padding=(10, 5))
        video_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # ✅ ปุ่ม Refresh เฉพาะ My Videos
        refresh_button = tk.Button(video_frame, text="🔄 Refresh", command=self.refresh_Like, 
                                bg="#d63384", fg="white", font=("Arial", 10, "bold"))
        refresh_button.pack(pady=5, anchor="ne")

        # ✅ ถ้าไม่มีวิดีโอ แสดงข้อความแล้วออกจากฟังก์ชันทันที
        if not videos:
            tk.Label(video_frame, text="No videos uploaded", font=("Arial", 12), bg="white").pack(pady=10)
            return

        # ✅ วนลูปแสดงวิดีโอ
        for video in videos:
            post_id = video.get("post_id", "N/A")
            video_url = video.get("video_url", "")

            # ✅ ตรวจสอบว่า URL ใช้งานได้ไหม
            if not self.is_valid_url(video_url):
                print(f"❌ Video {post_id} is unavailable. Deleting from database...")
                self.delete_video_from_db(post_id)  # ✅ ลบข้อมูลออกจากฐานข้อมูล
                continue  # ข้ามวิดีโอที่เปิดไม่ได้

            # ✅ ตรวจสอบค่า Like Count
            like_count = video.get("like_count", None)

            # ✅ ดึง Thumbnail จากวิดีโอและเก็บไว้ในโฟลเดอร์ icon
            thumbnail = self.get_video_thumbnail(video_url, post_id)

            if thumbnail:
                video_label = tk.Label(video_frame, image=thumbnail, bg="white", cursor="hand2")
                video_label.image = thumbnail
                video_label.pack(pady=5)
                video_label.bind("<Button-1>", lambda e, url=video_url: self.play_video(url))

            # ✅ แสดงจำนวน Like เฉพาะวิดีโอที่เปิดได้
            if like_count is not None:
                like_label = tk.Label(video_frame, text=f"❤ {like_count} Likes", font=("Arial", 12), bg="white")
                like_label.pack(pady=2)


    def delete_video_from_db(self, post_id):
        """ ลบวิดีโอออกจากฐานข้อมูลเมื่อ URL ใช้งานไม่ได้ """
        url = f"{self.api_base_url}/delete-message/{post_id}"
        payload = {"user_id": self.user_id}  # ✅ ส่ง user_id ไปด้วย

        try:
            response = requests.delete(url, params, json=payload, timeout=5)  # ใช้ DELETE request พร้อม JSON payload
            if response.status_code == 200:
                print(f"✅ Successfully deleted video {post_id} from database.")
            else:
                print(f"❌ Failed to delete video {post_id}: {response.json().get('detail', 'Unknown error')}")
        except requests.RequestException as e:
            print(f"❌ API error while deleting video {post_id}: {e}")


    def load_videos(self):
        """ โหลดวิดีโอของผู้ใช้จาก API """
        videos = self.get_user_videos()

        if not videos:
            tk.Label(self.video_frame, text="No videos uploaded", font=("Arial", 12), bg="white").pack(pady=10)
            return

        for video in videos:
            post_id = video.get("post_id", "N/A")
            video_url = video.get("video_url", "")
            like_count = video.get("like_count", 0)

            # ✅ แสดงวิดีโอและจำนวนไลก์
            video_label = tk.Label(self.video_frame, text=f"🎥 Video {post_id}", font=("Arial", 10), bg="white")
            video_label.pack(pady=2)

            like_label = tk.Label(self.video_frame, text=f"❤ {like_count} Likes", font=("Arial", 10), bg="white")
            like_label.pack(pady=2)

    def get_user_videos(self):
        """ ดึงวิดีโอทั้งหมดของผู้ใช้จาก API """
        if self.user_id is None:
            print("❌ No user_id found.")
            return []

        url = f"{self.api_base_url}/get_user_videos/{self.user_id}"
        try:
            response = requests.get(url, params, timeout=10)
            if response.status_code == 200:
                return response.json().get("videos", [])
        except Exception as e:
            print(f"❌ API error: {e}")
        return []
    def refresh_Like(self):
        """ รีโหลดข้อมูล My Videos (Like Tab) ใหม่จาก API refresh_Like """
        if self.user_id is None:
            print("❌ No user_id found.")
            return

        url = f"{self.api_base_url}/refresh_Like/?user_id={self.user_id}"
        
        try:
            response = requests.get(url, params, timeout=10)
            response.raise_for_status()  # ตรวจสอบสถานะ HTTP
            
            data = response.json()
            print(f"✅ Refreshed videos: {data}")  # Debug log
            
            # 🔹 ล้าง UI เก่าทั้งหมด
            for widget in self.tab2.winfo_children():
                widget.destroy()

            # 🔹 โหลดข้อมูลใหม่
            self.create_video_list(self.tab2, videos=data.get("videos", []))

        except requests.exceptions.RequestException as e:
            print(f"❌ API error: {e}")

    def on_filter_change(self):
        """อัปเดตทั้งกราฟและตารางเมื่อเปลี่ยน Filter"""
        filter_option = self.filter_var.get()
        self.update_chart(filter_option)
        self.update_activity_table(filter_option, self.user_email)

    
    def update_activity_table(self, filter_option, user_email):
        """อัปเดต Activity Table ตาม filter (Week/Month)"""
        role = self.user_role

        # ✅ เช็คว่ามีตารางเก่าอยู่หรือไม่ ถ้ามีให้ลบทิ้งก่อน
        if hasattr(self, "tree"):
            self.tree.destroy()  # ลบ Treeview เก่าออก

        # ✅ สร้าง Treeview ใหม่
        self.tree = ttk.Treeview(self.activity_frame, columns=(), show="headings")
        self.tree.pack(fill="both", expand=True)

        # ✅ กำหนดชื่อคอลัมน์ตาม filter
        if filter_option == "Week":
            columns = ["Username", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            api_url = f"{self.api_base_url}/get_activity_details/?email={user_email}"
        else:
            columns = ["Username", "January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"]
            api_url = f"{self.api_base_url}/get_monthly_activity_details/?email={user_email}"

        self.tree["columns"] = columns

        for col in columns:
            self.tree.heading(col, text=col)  # ตั้งชื่อ Header ใหม่
            self.tree.column(col, width=10, anchor="center")  # ปรับขนาดให้พอดี

        # ✅ ดึงข้อมูลจาก API
        response = requests.get(api_url, params)

        if response.status_code == 200:
            activity_data = response.json()

            if filter_option == "Week":
                details = activity_data.get("activity_details", [])
            else:  # 🛠 แก้ให้รองรับ Monthly Activity
                monthly_data = activity_data.get("monthly_activity", {})
                details = [activity_data.get("username", "")] + list(monthly_data.values())
        else:
            details = []

        # ✅ ใส่ข้อมูลใหม่ลงตาราง
        if details:
            self.tree.insert("", "end", values=details)  # ใส่ข้อมูลในแต่ละแถว

        # ✅ ตรวจสอบและลบปุ่ม Export Excel เก่าก่อนสร้างปุ่มใหม่
        if hasattr(self, 'export_button'):
            self.export_button.destroy()  # ลบปุ่มเก่าออก

        # ✅ สร้างปุ่ม Export ใหม่
        if filter_option == "Week":
            if role == 1:
                # 🔹 ปุ่ม Export Excel (อยู่ใน tab1)
                self.export_button = ctk.CTkButton(self.tab1, text="Export Excel", corner_radius=25, command=self.export_excel_active)
                self.export_button.pack(pady=2)  # ลด pady ที่นี่
        else:
            if role == 1:
                # 🔹 ปุ่ม Export Excel (อยู่ใน tab1)
                self.export_button = ctk.CTkButton(self.tab1, text="Export Excel Month", corner_radius=25, command=self.export_excel_active_month)
                self.export_button.pack(pady=2)


    def export_excel_active(self):
        """ 🔹 ตรวจสอบสิทธิ์ก่อนส่งคำขอ Export """
        if self.user_role != 1:
            messagebox.showerror("Permission Denied", "You don't have permission to export data")
            return

        try:
            response = requests.get(f"{self.api_base_url}/export_dashboard_active/?email={self.user_email}", params)

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
    
    def export_excel_active_month(self):
        """ 🔹 ตรวจสอบสิทธิ์ก่อนส่งคำขอ Export """
        if self.user_role != 1:
            messagebox.showerror("Permission Denied", "You don't have permission to export data")
            return

        try:
            response = requests.get(f"{self.api_base_url}/export_dashboard_month/?email={self.user_email}", params)

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
    
    def play_video(self, video_url):
        """เปิดวิดีโอใน Web Browser"""
        import webbrowser
        webbrowser.open(video_url)

            
    def export_excel_month(self):
        """ 🔹 ตรวจสอบสิทธิ์ก่อนส่งคำขอ Export """
        if self.user_role != 1:
            messagebox.showerror("Permission Denied", "You don't have permission to export data")
            return

        try:
            response = requests.get(f"{self.api_base_url}/export_dashboard_month/?email={self.user_email}", params)

            if response.status_code == 200:
                content_disposition = response.headers.get("Content-Disposition", "")
                filename = content_disposition.split("filename=")[-1].strip("\"")

                filename = urllib.parse.unquote(filename)
                filename = re.sub(r'[^a-zA-Z0-9_\-\. ]', '', filename)

                if not filename:
                    filename = "dashboard_month.xlsx"

                downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
                file_path = os.path.join(downloads_folder, filename)

                messagebox.showinfo("Success", f"Excel file ({filename}) has been saved to your Downloads folder!")
            else:
                messagebox.showerror("Error", response.json().get("detail", "Unknown error"))
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Failed to connect to the server")

