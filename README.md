pip install pillow
pip install matplotlib
pip install opencv-python
pip install opencv-python-headless --upgrade
pip install pygame==2.1.3  
pip3 install ffpyplayer
pip install python-multipart
pip install msal
pip install pywin32

---API---
pip install adal
pip install azure-identity pyodbc
pip install uvicorn
pip install fastapi
pip install fastapi[all] python-socketio
pip install fastapi fastapi-socketio python-socketio uvicorn
pip install Flask-SocketIO==4.3.1
pip install python-engineio==3.13.2
pip install python-socketio==4.6.0

---RUN API---
python -m uvicorn api:app --reload
---STOP API---
Ctrl + C in terminal
---Venv---
<!-- เข้าสู่โหมด venv เพื่อคำสั่ง pip install จะติดตั้ง package ลงใน venv แทนที่จะลงใน Python หลักของเครื่อง -->
<!-- สร้าง -->
python -m venv venv
<!-- เข้า -->
venv\Scripts\activate
<!-- ตรวจสอบแพ็กเกจที่ติดติ้ง -->
pip list
<!-- ออก -->
deactivate
---requirements---
<!-- อัพเดตว่า pip อะไรไปบ้างใน venv -->
pip freeze > requirements.txt
<!-- ติดตั้งทุก pip install -->
pip install -r requirements.txt

---Manual---
1. pip install ...
2. Run API in terminal
cd ERGO\server
<!-- python -m uvicorn api:app --reload -->
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
3. Run app
cd ERGO\app
python Login.py

---Build app .exe---
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "video/*;video/" --add-data "icon/*;icon/" --add-data "font/*;font/" --add-data "sounds/*;sounds/" Login.py
