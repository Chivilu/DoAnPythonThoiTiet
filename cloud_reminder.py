import os
import smtplib
import ssl
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.header import Header

# 1. Hàm lấy dữ liệu thời tiết (Giống hệt đồ án chính của bạn)
def lay_du_lieu_thoi_tiet(city):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    url = f"https://www.google.com/search?hl=en&q=weather+{city}"
    try:
        html = requests.get(url, headers=headers, timeout=10).content
        soup = BeautifulSoup(html, 'html.parser')
        temp_div = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'})
        sky_div = soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'})
        if temp_div and sky_div:
            return temp_div.text, sky_div.text.split('\n')[1]
    except Exception:
        pass

    backup_url = f"https://wttr.in/{city.replace(' ', '+')}?format=%t|%C"
    backup_html = requests.get(backup_url, timeout=10).text
    soup_backup = BeautifulSoup(backup_html, 'html.parser')
    data = soup_backup.text.strip().split('|')
    temperature = data[0] if len(data) > 0 else "30°C"
    sky = data[1] if len(data) > 1 else "Cloudy"
    return temperature, sky

# 2. Hàm phân tích thời tiết (Giống hệt đồ án chính của bạn)
def phan_tich_loi_khuyen(temperature_str, sky):
    so_nhiet_do = 28
    digits = ''.join(ch for ch in temperature_str if ch.isdigit() or ch == '-')
    if digits:
        so_nhiet_do = int(digits)

    tu_khoa_mua = ["rain", "rainy", "showers", "drizzle", "thunderstorm", "overcast", "cloudy", "mist", "haze", "patchy"]
    co_mua_hoac_am_u = any(k in sky.lower() for k in tu_khoa_mua)

    if co_mua_hoac_am_u:
        return "CẢNH BÁO MƯA/ÂM U: Hãy nhớ mang theo DÙ (Ô) hoặc ÁO MƯA khi ra ngoài nhé!"
    elif so_nhiet_do >= 33:
        return "CẢNH BÁO NẮNG NÓNG: Nhiệt độ khá cao, hãy mang theo DÙ che nắng, áo khoác và uống nhiều nước!"
    else:
        return "Thời tiết hôm nay rất đẹp và mát mẻ, thuận lợi cho việc di chuyển."

# 3. Hàm chạy tự động trên máy chủ đám mây GitHub (Kể cả khi đã tắt laptop)
def chay_tu_dong_khi_tat_may():
    city = "Long Xuyen"
    sender_email = "chivilu01@gmail.com"
    receiver_email = "vi_dth245951@student.agu.edu.vn"
    
    # Lấy Mật khẩu ứng dụng 16 ký tự từ két bảo mật (Secrets) của GitHub
    app_password = os.environ.get("GMAIL_PASS", "").replace(" ", "").strip()

    temperature, sky = lay_du_lieu_thoi_tiet(city)
    loi_khuyen = phan_tich_loi_khuyen(temperature, sky)

    subject = f"[Thời Tiết {city}] Nhắc nhở tự động mỗi sáng (Cloud)"
    body = (
        f"Xin chào,\n\n"
        f"Hệ thống chạy ngầm trên đám mây (hoạt động cả khi tắt máy tính) xin thông báo:\n"
        f"- Khu vực: {city}\n"
        f"- Nhiệt độ: {temperature}\n"
        f"- Trạng thái bầu trời: {sky}\n"
        f"- Lời khuyên: {loi_khuyen}\n\n"
        f"Gửi tự động từ GitHub Actions."
    )

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = sender_email
    msg['To'] = receiver_email

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=20) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, [receiver_email], msg.as_string())
        
    print(f"Đã gửi mail thời tiết {city} thành công!")

if __name__ == "__main__":
    chay_tu_dong_khi_tat_may()
