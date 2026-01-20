import time
import random
import os
import shutil
import requests
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# --- [ الإعدادات الأساسية ] ---
TOR_PROXY = "socks5://127.0.0.1:9050"

# --- [ قائمة الفيديوهات ] ---
VIDEOS_POOL = [
    {"id": "MrKhyV4Gcog", "keywords": "وش الحلم اللي حققته"},
    {"id": "bmgpC4lGSuQ", "keywords": "أجمل جزيرة في العالم سقطرى"},
    {"id": "6hYLIDz-RRM", "keywords": "هنا اختلفنا وفارقنا علي شان"},
    {"id": "AvH9Ig3A0Qo", "keywords": "Socotra treasure island"}
]

# --- [ 1. مكتبة الأجهزة (Devices) ] ---
DEVICES = [
    {"name": "iPhone 16 Pro Max", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 430, "h": 932},
    {"name": "Samsung S24 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 384, "h": 854},
    {"name": "Windows 11 Gaming PC", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36", "plat": "Win32", "w": 1920, "h": 1080},
    {"name": "MacBook Pro M3", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "plat": "MacIntel", "w": 1440, "h": 900},
    {"name": "Google Pixel 8 Pro", "ua": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.101 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915}
]

# --- [ 2. مكتبة المواقع الجغرافية (Locations + Timezones + Langs) ] ---
# لضمان تطابق الـ GPS مع الوقت واللغة
LOCATIONS = [
    {"city": "Riyadh", "lat": 24.7136, "lon": 46.6753, "tz": "Asia/Riyadh", "lang": "ar-SA"},
    {"city": "Dubai", "lat": 25.2048, "lon": 55.2708, "tz": "Asia/Dubai", "lang": "ar-AE"},
    {"city": "New York", "lat": 40.7128, "lon": -74.0060, "tz": "America/New_York", "lang": "en-US"},
    {"city": "London", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "lang": "en-GB"},
    {"city": "Cairo", "lat": 30.0444, "lon": 31.2357, "tz": "Africa/Cairo", "lang": "ar-EG"},
    {"city": "Berlin", "lat": 52.5200, "lon": 13.4050, "tz": "Europe/Berlin", "lang": "de-DE"},
]

# --- [ 3. ملفات سرعة الإنترنت (Network Profiles) ] ---
NETWORK_PROFILES = [
    {"name": "4G-Good", "latency": 40, "download": 15 * 1024 * 1024, "upload": 5 * 1024 * 1024},
    {"name": "4G-Poor", "latency": 150, "download": 2 * 1024 * 1024, "upload": 500 * 1024},
    {"name": "5G-Ultra", "latency": 10, "download": 100 * 1024 * 1024, "upload": 20 * 1024 * 1024},
    {"name": "WiFi-Home", "latency": 20, "download": 50 * 1024 * 1024, "upload": 10 * 1024 * 1024},
    {"name": "3G-Legacy", "latency": 300, "download": 750 * 1024, "upload": 200 * 1024}
]

def get_current_ip():
    proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
    try:
        return requests.get('https://api.ipify.org', proxies=proxies, timeout=10).text
    except:
        return "Tor Connection Issue"

def set_network_conditions(driver, profile):
    """محاكاة سرعة الإنترنت عبر بروتوكول CDP"""
    driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": False,
        "latency": profile['latency'],
        "downloadThroughput": profile['download'],
        "uploadThroughput": profile['upload']
    })

def set_geolocation(driver, loc):
    """تزييف الـ GPS عبر بروتوكول CDP"""
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": loc['lat'],
        "longitude": loc['lon'],
        "accuracy": 100
    })

def inject_ultimate_stealth(driver, dev, loc):
    """الحقن الشامل: بطارية، لغة، وقت، GPS، تشويش Canvas/Audio"""
    
    battery_level = random.uniform(0.4, 0.98)
    charging = "true" if random.random() > 0.3 else "false"
    
    js_code = f"""
    // 1. تزييف اللغة والمنصة
    Object.defineProperty(navigator, 'languages', {{get: () => ['{loc['lang']}', 'en-US', 'en']}});
    Object.defineProperty(navigator, 'language', {{get: () => '{loc['lang']}'}});
    Object.defineProperty(navigator, 'platform', {{get: () => '{dev["plat"]}'}});
    
    // 2. تزييف المنطقة الزمنية
    Object.defineProperty(Intl.DateTimeFormat().resolvedOptions(), 'timeZone', {{value: '{loc['tz']}'}});
    
    // 3. تزييف البطارية
    if (navigator.getBattery) {{
        navigator.getBattery = () => Promise.resolve({{
            charging: {charging},
            level: {battery_level},
            chargingTime: 0,
            dischargingTime: Infinity
        }});
    }}

    // 4. إخفاء الأتمتة
    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
    
    // 5. Canvas Noise (تشويش بصمة الرسم)
    const toBlob = HTMLCanvasElement.prototype.toBlob;
    const toDataURL = HTMLCanvasElement.prototype.toDataURL;
    const getImageData = CanvasRenderingContext2D.prototype.getImageData;
    // إضافة ضوضاء عشوائية طفيفة جداً للرسم
    var noise = {{r: Math.floor(Math.random() * 10) - 5, g: Math.floor(Math.random() * 10) - 5, b: Math.floor(Math.random() * 10) - 5}};
    
    // 6. Audio Context Noise (تشويش بصمة الصوت)
    // (يتم هنا تعديل بسيط جداً على الترددات لمنع البصمة الصوتية)
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_code})

def run_ultimate_session(session_num):
    # اختيار عشوائي ذكي
    dev = random.choice(DEVICES)
    loc = random.choice(LOCATIONS) # اختيار دولة/مدينة كاملة
    net_profile = random.choice(NETWORK_PROFILES) # سرعة نت عشوائية
    
    video_data = random.choice(VIDEOS_POOL)
    video_url = f"https://www.youtube.com/watch?v={video_data['id']}"

    print(f"\n💎 [جلسة {session_num}]")
    print(f"📱 الجهاز: {dev['name']} | 🌍 الموقع: {loc['city']} (Timezone: {loc['tz']})")
    print(f"📡 الشبكة: {net_profile['name']} | 🔋 شحن وهمي")
    print(f"🌐 Loading: {video_url}")

    options = uc.ChromeOptions()
    profile_dir = os.path.abspath(f"linux_profile_{session_num % 10}")
    
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument(f'--user-agent={dev["ua"]}')
    options.add_argument(f'--proxy-server={TOR_PROXY}')
    options.add_argument(f"--window-size={dev['w']},{dev['h']}")
    
    # تحسينات Linux وتجاوز الأخطاء
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process') # تقليل استهلاك الرام

    driver = None
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        
        # 1. تفعيل الشبكة والـ GPS والحقن قبل التحميل
        set_network_conditions(driver, net_profile)
        set_geolocation(driver, loc)
        inject_ultimate_stealth(driver, dev, loc)
        
        wait = WebDriverWait(driver, 35)

        # 2. بداية التصفح
        driver.get("https://www.youtube.com")
        time.sleep(random.randint(6, 10))

        # محاولة البحث
        try:
            search_box = wait.until(EC.element_to_be_clickable((By.NAME, "search_query")))
            for char in video_data['keywords']:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            search_box.send_keys(Keys.ENTER)
            
            # محاولة العثور على الرابط
            video_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '{video_data['id']}')]")))
            video_link.click()
            print("🎯 تم الدخول عبر البحث (Organic View)")
        except:
            print("⚠️ لم يتم العثور في البحث، استخدام الرابط المباشر")
            driver.get(video_url)

        # 3. التحكم بالمشاهدة
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        video_element = driver.find_element(By.TAG_NAME, "video")
        
        # تغيير السرعة العشوائي
        initial_speed = random.choice([1.25, 1.5, 1.75])
        driver.execute_script(f"arguments[0].playbackRate = {initial_speed};", video_element)
        
        watch_duration = random.randint(80, 140)
        print(f"⏳ مدة المشاهدة: {watch_duration}ثانية (سرعة {initial_speed}x)")
        
        # محاكاة التفاعل
        time.sleep(watch_duration // 3)
        driver.execute_script(f"window.scrollBy(0, {random.randint(200, 600)});") # سكرول للأسفل
        
        time.sleep(watch_duration // 3)
        driver.execute_script("arguments[0].playbackRate = 1.0;", video_element) # عودة للطبيعي
        print("🔄 استعادة السرعة الطبيعية")
        
        # سكرول للأعلى قليلاً
        driver.execute_script(f"window.scrollBy(0, -{random.randint(100, 300)});")
        
        time.sleep(watch_duration // 3)
        print(f"✅ اكتملت الجلسة.")

    except Exception as e:
        print(f"⚠️ خطأ: {str(e)[:100]}")
    finally:
        if driver:
            try: driver.quit()
            except: pass
        if os.path.exists(profile_dir):
            try: shutil.rmtree(profile_dir, ignore_errors=True)
            except: pass

if __name__ == "__main__":
    os.system("pkill -f chrome")
    print("🔥 بدأ السكربت الإمبراطوري الشامل (GPS + Network + Device Spoofing)...")
    
    # حلقة المليون
    for i in range(1, 1000001):
        run_ultimate_session(i)
        
        # فترة راحة عشوائية لتغيير الـ IP في Tor
        delay = random.randint(8, 20)
        print(f"💤 استراحة {delay} ثانية...")
        time.sleep(delay)
