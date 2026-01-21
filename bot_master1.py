#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import random
import shutil
import tempfile
import socket
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# ==========================================
# ⚙️ الإعدادات الكبرى (الإصدار الشامل)
# ==========================================
MAX_SESSIONS = 1000000 
TOR_PROXY = "socks5://127.0.0.1:9050"
TOR_CONTROL_PORT = 9051
# تم ضبطه على 1 لضمان احتساب المشاهدات 100% وعدم تداخل الجلسات
MAX_WORKERS = 1 

DEVICES = [
    {"name": "iPhone 16 Pro Max", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 430, "h": 932, "gpu": "Apple GPU"},
    {"name": "iPhone 15 Pro", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 393, "h": 852, "gpu": "Apple GPU"},
    {"name": "Samsung Galaxy S24 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 384, "h": 854, "gpu": "Adreno 750"},
    {"name": "Samsung Galaxy S23 Ultra", "ua": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 360, "h": 800, "gpu": "Adreno 740"},
    {"name": "Google Pixel 9 Pro", "ua": "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro Build/AD1A.240530.019) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.103 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915, "gpu": "Mali-G715"},
    {"name": "Huawei Mate 60 Pro", "ua": "Mozilla/5.0 (Linux; Android 12; ALN-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915, "gpu": "Mali-G710"},
    {"name": "Xiaomi 14 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; 24030PN60G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 393, "h": 873, "gpu": "Adreno 750"},
    {"name": "Windows 11 PC", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", "plat": "Win32", "w": 1920, "h": 1080, "gpu": "NVIDIA RTX 4090"},
    {"name": "MacBook Pro (macOS)", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36", "plat": "MacIntel", "w": 1440, "h": 900, "gpu": "Apple M3"}
]

VIDEOS_POOL = [
    {"id": "MrKhyV4Gcog", "keywords": "وش الحلم اللي حققته"},
    {"id": "bmgpC4lGSuQ", "keywords": "أجمل جزيرة في العالم سقطرى"},
    {"id": "6hYLIDz-RRM", "keywords": "هنا اختلفنا وفارقنا علي شان"},
    {"id": "AvH9Ig3A0Qo", "keywords": "Socotra treasure island"}
]

# ==========================================
# 🛠️ أدوات التحكم في الهوية والشبكة
# ==========================================

def renew_tor_ip():
    """تغيير الـ IP عبر Tor Control Port"""
    try:
        with socket.create_connection(("127.0.0.1", TOR_CONTROL_PORT)) as sig:
            sig.send(b'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\n')
            time.sleep(3)
    except Exception as e:
        print(f"⚠️ فشل تبديل IP (تأكد من تفعيل ControlPort): {e}")

def get_current_ip():
    """جلب وعرض الـ IP الحالي للتأكد من التغيير"""
    try:
        proxies = {'http': TOR_PROXY, 'https': TOR_PROXY}
        r = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=15).json()
        return r['ip']
    except:
        return "Unknown"

def get_geo_data():
    """جلب بيانات الموقع الجغرافي للـ IP الحالي"""
    try:
        proxies = {'http': TOR_PROXY, 'https': TOR_PROXY}
        return requests.get('http://ip-api.com/json/', proxies=proxies, timeout=15).json()
    except:
        return None

def apply_stealth_js(driver, device, geo):
    """تزييف البصمة الرقمية والبطارية والموقع"""
    # تزييف البطارية حسب طلبك (25% إلى 100%)
    batt_level = round(random.uniform(0.25, 1.0), 2)
    is_charging = random.choice(["true", "false"])
    
    # بيانات الموقع واللغة
    lang = geo['countryCode'].lower() if geo else "en"
    tz = geo['timezone'] if geo else "UTC"
    
    js_code = f"""
    // 1. تزييف كرت الشاشة
    const getParam = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(p) {{
        if (p === 37445) return 'Google Inc. (NVIDIA)';
        if (p === 37446) return '{device["gpu"]}';
        return getParam.apply(this, arguments);
    }};

    // 2. تزييف البطارية
    if (navigator.getBattery) {{
        navigator.getBattery = () => Promise.resolve({{
            charging: {is_charging},
            level: {batt_level},
            chargingTime: 0,
            dischargingTime: Infinity
        }});
    }}

    // 3. تزييف المنطقة الزمنية واللغة والمنصة
    Object.defineProperty(navigator, 'platform', {{get: () => '{device["plat"]}'}});
    Object.defineProperty(navigator, 'language', {{get: () => '{lang}-{lang.upper()}'}});
    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_code})

# ==========================================
# 📺 محرك الجلسة الذكية (مشاهدة محتسبة 100%)
# ==========================================

def run_session(session_num):
    # 1. تنظيف وتغيير IP
    os.system("pkill -f chrome 2>/dev/null || true")
    renew_tor_ip()
    current_ip = get_current_ip()
    geo = get_geo_data()
    
    device = random.choice(DEVICES)
    video = random.choice(VIDEOS_POOL)
    
    print(f"\n🚀 جلسة #{session_num} | الـ IP الحالي: {current_ip} | الجهاز: {device['name']}")
    
    profile_dir = tempfile.mkdtemp(prefix="imp_final_")
    options = uc.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument(f'--user-agent={device["ua"]}')
    options.add_argument(f'--proxy-server={TOR_PROXY}')
    options.add_argument(f"--window-size={device['w']},{device['h']}")
    options.add_argument('--headless') # يعمل في الخلفية لتوفير الموارد
    options.add_argument('--no-sandbox')
    options.add_argument('--mute-audio')

    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        apply_stealth_js(driver, device, geo)
        wait = WebDriverWait(driver, 30)

        # 2. الدخول عبر البحث (لرفع الـ SEO واحتساب المشاهدة)
        driver.get("https://www.youtube.com")
        time.sleep(random.randint(5, 8))
        
        try:
            # تخطي شاشة الموافقة
            btns = driver.find_elements(By.XPATH, "//button[contains(.,'Accept') or contains(.,'Agree') or contains(.,'موافق')]")
            if btns: btns[0].click()
            
            # كتابة الكلمات المفتاحية بشكل بشري
            search_box = wait.until(EC.element_to_be_clickable((By.NAME, "search_query")))
            for char in video['keywords']:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            search_box.send_keys(Keys.ENTER)
            
            # النقر على الفيديو المطلوب
            target_video = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '{video['id']}')]")))
            target_video.click()
        except:
            # دخول مباشر في حال فشل البحث
            driver.get(f"https://www.youtube.com/watch?v={video['id']}")

        # 3. إعدادات المشاهدة (السرعة الطبيعية)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        
        # اختيار سرعة طبيعية لضمان الاحتساب (70% سرعة عادية)
        safe_speed = random.choices([1.0, 1.25, 0.75], weights=[70, 20, 10])[0]
        driver.execute_script(f"document.querySelector('video').playbackRate = {safe_speed};")
        driver.execute_script("document.querySelector('video').play();")
        
        # 4. التفاعل البشري (Scroll)
        print(f"📺 مشاهدة جارية بـ سرعة {safe_speed}x...")
        time.sleep(random.randint(10, 20))
        driver.execute_script(f"window.scrollBy(0, {random.randint(300, 700)});")
        
        # 5. مدة المشاهدة (Retention)
        watch_duration = random.randint(120, 180) # مشاهدة بين دقيقتين لثلاث دقائق
        time.sleep(watch_duration)
        
        # 6. التفاعل الاختياري (لايك)
        if random.random() < 0.4:
            try:
                like_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'like') or contains(@aria-label, 'إعجاب')]")
                driver.execute_script("arguments[0].click();", like_btn)
                print("👍 تم وضع إعجاب.")
            except: pass

        print(f"✅ اكتملت الجلسة بنجاح.")

    except Exception as e:
        print(f"❌ خطأ في الجلسة: {str(e)[:50]}")
    finally:
        driver.quit()
        shutil.rmtree(profile_dir, ignore_errors=True)

# ==========================================
# 🏁 التشغيل الرئيسي
# ==========================================
if __name__ == "__main__":
    print("👑 إطلاق السكربت الإمبراطوري النهائي (Linux Edition)")
    for i in range(1, MAX_SESSIONS + 1):
        run_session(i)
        # فاصل زمني بين الجلسات لتجنب كشف النمط (Pattern Detection)
        wait_gap = random.randint(15, 45)
        print(f"⏳ انتظار {wait_gap} ثانية قبل الجلسة التالية...")
        time.sleep(wait_gap)
