#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import random
import shutil
import socket
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# ==========================================
# ⚙️ الإعدادات الكبرى (لا تغيير)
# ==========================================
MAX_SESSIONS = 1000000 
TOR_PROXY = "socks5://127.0.0.1:9050"
TOR_CONTROL_PORT = 9051

DEVICES = [
    # --- iOS Devices (iPhones & iPads) ---
    {"name": "iPhone 16 Pro Max", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 430, "h": 932, "gpu": "Apple GPU"},
    {"name": "iPhone 15 Pro", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 393, "h": 852, "gpu": "Apple GPU"},
    {"name": "iPhone 14", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 390, "h": 844, "gpu": "Apple GPU"},
    {"name": "iPhone 13 Mini", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 375, "h": 812, "gpu": "Apple GPU"},
    {"name": "iPad Pro 12.9 M2", "ua": "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1", "plat": "MacIntel", "w": 1024, "h": 1366, "gpu": "Apple M2 GPU"},
    {"name": "iPad Air (Gen 5)", "ua": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "plat": "MacIntel", "w": 820, "h": 1180, "gpu": "Apple M1 GPU"},

    # --- Android High-End ---
    {"name": "Samsung Galaxy S24 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 384, "h": 854, "gpu": "Adreno 750"},
    {"name": "Samsung Galaxy S23 Ultra", "ua": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 360, "h": 800, "gpu": "Adreno 740"},
    {"name": "Google Pixel 9 Pro", "ua": "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro Build/AD1A.240530.019) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.103 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915, "gpu": "Mali-G715"},
    {"name": "Google Pixel 8 Pro", "ua": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 892, "gpu": "Mali-G715"},
    {"name": "Xiaomi 14 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; 24030PN60G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 393, "h": 873, "gpu": "Adreno 750"},
    {"name": "OnePlus 12", "ua": "Mozilla/5.0 (Linux; Android 14; CPH2581) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 384, "h": 854, "gpu": "Adreno 750"},

    # --- Android Mid-Range & Others ---
    {"name": "Samsung Galaxy A54", "ua": "Mozilla/5.0 (Linux; Android 13; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 360, "h": 800, "gpu": "Mali-G68"},
    {"name": "Nothing Phone (2)", "ua": "Mozilla/5.0 (Linux; Android 13; A065) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 412, "h": 915, "gpu": "Adreno 730"},
    {"name": "Samsung Galaxy Tab S9", "ua": "Mozilla/5.0 (Linux; Android 13; SM-X710) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36", "plat": "Linux armv8l", "w": 800, "h": 1280, "gpu": "Adreno 740"},

    # --- Desktop Devices (Windows, Mac, Linux) ---
    {"name": "Windows 11 PC (Chrome)", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", "plat": "Win32", "w": 1920, "h": 1080, "gpu": "NVIDIA GeForce RTX 4090"},
    {"name": "Windows 11 PC (Edge)", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/124.0.0.0 Edg/124.0.0.0", "plat": "Win32", "w": 2560, "h": 1440, "gpu": "NVIDIA GeForce RTX 3080"},
    {"name": "MacBook Pro M3", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36", "plat": "MacIntel", "w": 1728, "h": 1117, "gpu": "Apple M3 Max GPU"},
    {"name": "MacBook Air M2", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", "plat": "MacIntel", "w": 1440, "h": 900, "gpu": "Apple M2 GPU"},
    {"name": "Linux Desktop (Ubuntu/Firefox)", "ua": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0", "plat": "Linux x86_64", "w": 1920, "h": 1080, "gpu": "AMD Radeon RX 7900 XT"}
]


VIDEOS_POOL = [
    {"id": "MrKhyV4Gcog", "keywords": "وش الحلم اللي حققته"},
    {"id": "bmgpC4lGSuQ", "keywords": "أجمل جزيرة في العالم سقطرى"},
    {"id": "6hYLIDz-RRM", "keywords": "هنا اختلفنا وفارقنا علي شان"},
    {"id": "AvH9Ig3A0Qo", "keywords": "Socotra treasure island"}
]

def renew_tor_ip():
    try:
        with socket.create_connection(("127.0.0.1", TOR_CONTROL_PORT)) as sig:
            sig.send(b'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\n')
            time.sleep(5)
    except: pass

def get_geo_full_data():
    try:
        proxies = {'http': TOR_PROXY, 'https': TOR_PROXY}
        r = requests.get('http://ip-api.com/json/?fields=status,country,countryCode,city,lat,lon,timezone,query', proxies=proxies, timeout=15).json()
        if r['status'] == 'success': return r
    except: return None

def apply_advanced_stealth(driver, device, geo):
    cpu = random.choice([4, 6, 8, 12])
    ram = random.choice([8, 12, 16, 32])
    batt_level = round(random.uniform(0.15, 0.98), 2)
    is_charging = "true" if (batt_level < 0.20 or random.random() < 0.3) else "false"
    lang = geo['countryCode'].lower() if geo else "en"
    tz = geo['timezone'] if geo else "UTC"
    lat = geo['lat'] if geo else 0.0
    lon = geo['lon'] if geo else 0.0

    js_code = f"""
    Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {cpu}}});
    Object.defineProperty(navigator, 'deviceMemory', {{get: () => {ram}}});
    const getParam = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(p) {{
        if (p === 37445) return 'Google Inc. (NVIDIA)';
        if (p === 37446) return '{device["gpu"]}';
        return getParam.apply(this, arguments);
    }};
    if (navigator.getBattery) {{
        navigator.getBattery = () => Promise.resolve({{
            charging: {is_charging}, level: {batt_level}, chargingTime: 0, dischargingTime: Infinity
        }});
    }}
    Object.defineProperty(navigator, 'language', {{get: () => '{lang}-{lang.upper()}'}});
    Object.defineProperty(navigator, 'languages', {{get: () => ['{lang}-{lang.upper()}', '{lang}']}});
    Object.defineProperty(navigator, 'platform', {{get: () => '{device["plat"]}'}});
    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_code})
    driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": tz})
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {"latitude": lat, "longitude": lon, "accuracy": 100})

def run_session(session_num):
    # إصلاح: قتل العمليات القديمة بشكل إجباري قبل البدء
    os.system("pkill -9 -f chrome 2>/dev/null || true")
    os.system("pkill -9 -f chromedriver 2>/dev/null || true")
    
    renew_tor_ip()
    geo = get_geo_full_data()
    device = random.choice(DEVICES)
    video = random.choice(VIDEOS_POOL)
    profile_dir = os.path.abspath(f"profile_data_{session_num}")

    print(f"\n{'='*50}")
    print(f"🚀 الجلسة رقم: #{session_num}")
    print(f"🌐 IP تور: {geo['query'] if geo else 'Unknown'}")
    print(f"📍 الموقع: {geo['city'] if geo else '??'}, {geo['country'] if geo else '??'} | GPS: {geo['lat'] if geo else '??'}, {geo['lon'] if geo else '??'}")
    print(f"💻 الجهاز: {device['name']} | 🔋 البطارية: {int(random.random()*80+15)}%")
    print(f"🎬 الفيديو: {video['keywords']}")
    print(f"{'='*50}")

    options = uc.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument(f'--user-agent={device["ua"]}')
    options.add_argument(f'--proxy-server={TOR_PROXY}')
    options.add_argument(f"--window-size={device['w']},{device['h']}")
    
    # إصلاح: إضافة هذه الأسطر يحل مشكلة الربط (Connection Error)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('--remote-debugging-port=0') # السماح للنظام باختيار أي منفذ متاح تلقائياً

    driver = None
    try:
        # إصلاح: سحب المتصفح مع تفعيل subprocess لضمان الاستجابة
        driver = uc.Chrome(options=options, use_subprocess=True)
        apply_advanced_stealth(driver, device, geo)
        wait = WebDriverWait(driver, 45)

        driver.get("https://www.youtube.com")
        time.sleep(random.randint(8, 12))
        
        try:
            btns = driver.find_elements(By.XPATH, "//button[contains(.,'Accept') or contains(.,'Agree') or contains(.,'موافق')]")
            if btns: btns[0].click()
            
            search_box = wait.until(EC.element_to_be_clickable((By.NAME, "search_query")))
            for char in video['keywords']:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.4))
            search_box.send_keys(Keys.ENTER)
            
            target_video = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '{video['id']}')]")))
            target_video.click()
            print("🔗 تم الربط بنجاح والعثور على الفيديو.")
        except:
            print("🔗 تم الربط المباشر بالفيديو.")
            driver.get(f"https://www.youtube.com/watch?v={video['id']}")

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        driver.execute_script("document.querySelector('video').play();")
        
        time.sleep(random.randint(15, 25))
        driver.execute_script(f"window.scrollBy(0, {random.randint(400, 900)});")
        
        # عرض وقت المشاهدة المخطط له
        watch_duration = random.randint(120, 190)
        print(f"⏳ جاري المشاهدة الآن... المدة المخططة: {watch_duration} ثانية")
        time.sleep(watch_duration)
        
        print(f"✅ اكتملت الجلسة بنجاح.")

    except Exception as e:
        print(f"❌ حدث خطأ في الربط: {str(e)[:100]}")
    finally:
        if driver:
            try: driver.quit()
            except: pass
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    print("💎 نظام المشاهدات الاحترافي يعمل الآن...")
    for i in range(1, MAX_SESSIONS + 1):
        run_session(i)
        gap = random.randint(15, 45)
        print(f"💤 انتظار {gap} ثانية...")
        time.sleep(gap)
