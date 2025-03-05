FROM python:3.10

# ติดตั้ง ODBC driver
RUN apt-get update && apt-get install -y unixodbc unixodbc-dev

# ตั้งค่าดirectoryและcopyโค้ดเข้า container
WORKDIR /app
COPY . /app

# ติดตั้ง dependencies ของ Python
RUN pip install --no-cache-dir -r requirements.txt

# รันแอปพลิเคชัน
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


