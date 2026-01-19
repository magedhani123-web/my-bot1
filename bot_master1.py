import time
import random
import os
import shutil
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# --- [ الإعدادات الأساسية ] ---
TOR_PROXY = "socks5://127.0.0.1:9050"

# --- [ قائمة الفيديوهات المدمجة ] ---
VIDEOS_POOL = [
    {"id": "MrKhyV4Gcog", "keywords": "وش الحلم اللي حققته"},
    {"id": "bmgpC4lGSuQ", "keywords": "أجمل جزيرة في العالم سقطرى"},
    {"id": "6hYLIDz-RRM", "keywords": "هنا اختلفنا وفارقنا علي شان"},
    {"id": "AvH9Ig3A0Qo", "keywords": "Socotra treasure island"}
]

# --- [ مكتبة الأجهزة الحديثة ] ---
DEVICES = [
    {"name": "iPhone 16 Pro Max", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 430, "h": 932},
    {"name": "iPhone 15 Pro", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 393, "h": 852},
    {"name": "Samsung Galaxy S24 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 384, "h": 854},
    {"name": "Samsung Galaxy S23 Ultra", "ua": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 360, "h": 800},
    {"name": "Google Pixel 9 Pro", "ua": "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro Build/AD1A.240530.019) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.103 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915},
    {"name": "Huawei Mate 60 Pro", "ua": "Mozilla/5.0 (Linux; Android 12; ALN-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915},
    {"name": "Xiaomi 14 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; 24030PN60G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 393, "h": 873},
    {"name": "Windows 11 PC", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", "plat": "Win32", "w": 1920, "h": 1080},
    {"name": "MacBook Pro (macOS)", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36", "plat": "MacIntel", "w": 1440, "h": 900}
]

def get_current_ip():
    proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
    try:
        return requests.get('https://api.ipify.org', proxies=proxies, timeout=10).text
    except:
        return "Connection Error (Check Tor)"

def inject_stealth_v2(driver, dev):
    timezones = ['America/New_York', 'Europe/London', 'Asia/Riyadh', 'Asia/Dubai', 'Europe/Paris', 'Asia/Kuwait']
    tz = random.choice(timezones)
    battery_level = random.uniform(0.5, 0.95)
    
    js_code = f"""
    Object.defineProperty(navigator, 'languages', {{get: () => ['ar-SA', 'ar', 'en-US', 'en']}});
    Object.defineProperty(navigator, 'platform', {{get: () => '{dev["plat"]}'}});
    Object.defineProperty(Intl.DateTimeFormat().resolvedOptions(), 'timeZone', {{value: '{tz}'}});
    if (navigator.getBattery) {{
        navigator.getBattery = () => Promise.resolve({{
            charging: true,
            level: {battery_level},
            chargingTime: 0,
            dischargingTime: Infinity
        }});
    }}
    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_code})

def run_advanced_session(session_num):
    dev = random.choice(DEVICES)
    video_data = random.choice(VIDEOS_POOL)
    current_ip = get_current_ip()
    video_url = f"https://www.youtube.com/watch?v={video_data['id']}"

    print(f"\n🚀 [الجلسة {session_num}] | الجهاز: {dev['name']}")
    print(f"🌐 IP الحالي: {current_ip}")
    print(f"🌐 Loading: {video_url}")

    options = uc.ChromeOptions()
    profile_dir = os.path.abspath(f"linux_profile_{session_num % 10}") 
    
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument(f'--user-agent={dev["ua"]}')
    options.add_argument(f'--proxy-server={TOR_PROXY}')
    options.add_argument(f"--window-size={dev['w']},{dev['h']}")
    
    # الإضافات الجديدة لتحسين التوافق وحل أخطاء Linux
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-extensions')
    
    options.add_argument('--headless') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    driver = None
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        inject_stealth_v2(driver, dev)
        wait = WebDriverWait(driver, 30)

        driver.get("https://www.youtube.com")
        time.sleep(random.randint(5, 8))

        try:
            search_box = wait.until(EC.element_to_be_clickable((By.NAME, "search_query")))
            for char in video_data['keywords']:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            search_box.send_keys(Keys.ENTER)
            video_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '{video_data['id']}')]")))
            video_link.click()
        except:
            driver.get(video_url)

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        video_element = driver.find_element(By.TAG_NAME, "video")
        
        initial_speed = random.choice([1.25, 1.5, 2.0])
        driver.execute_script(f"arguments[0].playbackRate = {initial_speed};", video_element)
        print(f"⚡ السرعة الحالية: {initial_speed}x")

        watch_duration = random.randint(70, 110)
        time.sleep(watch_duration // 3)
        driver.execute_script(f"window.scrollBy(0, {random.randint(300, 700)});")
        time.sleep(watch_duration // 3)
        driver.execute_script("arguments[0].playbackRate = 1.0;", video_element)
        time.sleep(watch_duration // 3)
        print(f"✅ انتهت الجلسة بنجاح.")

    except Exception as e:
        print(f"⚠️ خطأ أثناء الجلسة: {str(e)[:100]}")
    finally:
        if driver:
            driver.quit()
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    os.system("pkill -f chrome")
    print("🔥 بدأ السكربت العملاق (هدف: مليون مشاهدة)...")
    for i in range(1, 1000001):
        run_advanced_session(i)
        delay = random.randint(5, 15)
        print(f"💤 انتظار {delay} ثانية قبل الجلسة القادمة...")
        time.sleep(delay)
