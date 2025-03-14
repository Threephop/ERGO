pip install pillow
pip install matplotlib
pip install opencv-python
pip install opencv-python-headless --upgrade
pip install pygame==2.1.3  
pip3 install ffpyplayer
pip install python-multipart
pip install msal
pip install pywin32
pip install customtkinter

---API---
pip install adal
pip install azure-identity pyodbc
pip install uvicorn
pip install fastapi
pip install pandas
pip install openpyxl
pip install azure-storage-blob
pip install sqlalchemy

---RUN API---
python -m uvicorn main:app --reload
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
python -m uvicorn main:app --reload
3. Run app
cd ERGO\app
python Login.py

---Build app .exe---
pip install pyinstaller

pyinstaller --onefile --windowed --name "ERGO" --collect-all numpy --hidden-import=numpy --hidden-import=numpy.core --hidden-import=numpy.core._multiarray_umath --hidden-import=numpy.core._dtype --hidden-import=numpy.core.numeric --hidden-import=numpy.core.shape_base --hidden-import=numpy.linalg --hidden-import=numpy.fft --hidden-import=numpy.random --add-data "video/default_videos/;video/default_videos/" --add-data "icon/;icon/" --add-data "font/;font/" --add-data "sounds/;sounds/" --add-data "text/*;text/" --add-data "Login.py;." --icon="icon/windows_icon.ico" Login.py


---Docker---
<!-- สร้าง container และ รัน-->
docker compose up --build
<!-- สร้าง container -->
docker-compose build --no-cache
<!-- run container -->
docker-compose up
<!-- หยุดทุก Container  -->
docker-compose down
<!-- หยุดแค่ Container เดียว  -->
docker-compose stop

docker login
docker images
docker tag 47f3c8f5ef54 threephop/ergodocker:ergoapipoc
docker push threephop/ergodocker:ergoapipoc

