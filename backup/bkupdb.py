import os
import shutil
import smtplib
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load biến môi trường từ .env
load_dotenv()

SENDER_EMAIL = os.getenv("EMAIL_SENDER")
APP_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("EMAIL_RECEIVER")
DB_FOLDER = r"C:\Users\Thái\OneDrive\Tài liệu\SQL"
BACKUP_FOLDER = r"C:\Users\Thái\OneDrive\Tài liệu\SQL\backup"

def send_email(success=True, message=""):
    subject = "✅ Backup thành công" if success else "❌ Backup thất bại"
    body = message or ("File backup đã được sao lưu thành công." if success else "Không thể sao lưu file.")
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print(f"Đã gửi mail: {subject}")
    except Exception as e:
        print("Lỗi gửi email:", e)

def backup_database():
    try:
        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)

        found = False
        for file in os.listdir(DB_FOLDER):
            if file.endswith(".sql") or file.endswith(".sqlite3"):
                found = True
                src = os.path.join(DB_FOLDER, file)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                name, ext = os.path.splitext(file)  # tách tên và đuôi
                new_filename = f"{name}_{timestamp}{ext}"  # chèn thời gian trước đuôi
                dest = os.path.join(BACKUP_FOLDER, new_filename)

                shutil.copy2(src, dest)
        
        if found:
            send_email(True)
        else:
            send_email(False, "Không tìm thấy file .sql hoặc .sqlite3 để sao lưu.")
    except Exception as e:
        send_email(False, str(e))


# Lên lịch chạy lúc 00:00 mỗi ngày
schedule.every().day.at("00:00").do(backup_database)

print("Đang chạy lịch backup mỗi ngày lúc 00:00...")
while True:
    schedule.run_pending()
    time.sleep(60)
