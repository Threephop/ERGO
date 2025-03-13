FROM python:3.10

# ติดตั้ง ODBC Driver 17 และ dependencies ที่จำเป็น
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    odbcinst \
    curl \
    gnupg2 \
    software-properties-common && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# ตั้งค่าดirectoryและ copy โค้ดเข้า container
WORKDIR /app
COPY . /app

# ติดตั้ง dependencies ของ Python
RUN pip install --no-cache-dir -r requirements.txt

# รันแอปพลิเคชัน
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
