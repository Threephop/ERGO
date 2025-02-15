pip install pillow
pip install matplotlib
pip install opencv-python
pip install opencv-python-headless --upgrade
pip install pygame==2.1.3  
pip3 install ffpyplayer
pip install python-multipart

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

---Manual---
1. pip install ...
2. Run API in terminal
cd ERGO\server
<!-- python -m uvicorn api:app --reload -->
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
3. Run app
cd ERGO\app
python Login.py