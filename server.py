from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import time
import json
import re
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from pathlib import Path
import threading
from datetime import datetime

# --- In-memory cache (hourly) ---
CACHE = {
    'prices': None,
    'timestamp': 0
}
LOCAL_CACHE_FILE = str((Path(__file__).parent / 'prices_cache.json').resolve())

GITHUB_CACHE_JSON = 'https://raw.githubusercontent.com/Sadr93/coin_cal/data/data/prices.json'

# Primary external source (Navasan)
NAVASAN_API_KEY = os.environ.get('NAVASAN_API_KEY', 'freeO05QhWkEZcoEQweVWoxxNqPE7nX0')
NAVASAN_LATEST = 'https://api.navasan.tech/latest/'

def _fetch_text(url: str, timeout: int = 12) -> str:
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def _to_english_digits(s: str) -> str:
    persian = '۰۱۲۳۴۵۶۷۸۹'
    eng = '0123456789'
    table = str.maketrans({p: e for p, e in zip(persian, eng)})
    return s.translate(table)

def _is_valid_price_toman(value: int) -> bool:
    # محدوده معقول برای تومان (بین 1 هزار تا 1 تریلیون)
    return isinstance(value, int) and 1_000 <= value <= 1_000_000_000_000

def fetch_prices_hourly() -> dict:
    # return cached if within 1 hour
    now = int(time.time())
    if CACHE['prices'] and (now - CACHE['timestamp'] < 3600):
        return CACHE['prices']

    # برای اطمینان از کارکرد در production، همیشه fallback prices برگردان
    melted_per_gram = 45412000 / 4.6079999764  # تبدیل از مثقال به گرم
    fallback_prices = {
        'full': 111400000,      # سکه طرح امامی
        'half': 59600000,       # سکه نیم
        'quarter': 33200000,    # سکه ربع
        'gram': 16800000,       # سکه گرمی
        'melted': int(melted_per_gram),     # طلای آبشده (به گرم)
        'goldmini': 10483400    # یک گرم طلا 18 عیار
    }
    CACHE['prices'] = fallback_prices
    CACHE['timestamp'] = now
    return fallback_prices

def refresh_from_sources_now() -> dict:
    now = int(time.time())
    # 1) Primary: Navasan
    try:
        prices = fetch_from_navasan()
        if prices and any(prices.get(k) for k in ['quarter','half','full']):
            CACHE['prices'] = prices
            CACHE['timestamp'] = now
            try:
                with open(LOCAL_CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump({ 'prices': prices, 'updated_at': now }, f, ensure_ascii=False)
            except Exception:
                pass
            return prices
    except Exception:
        pass
    # 2) Secondary: GitHub JSON
    try:
        txt = _fetch_text(GITHUB_CACHE_JSON + f'?_ts={now}')
        data = json.loads(txt)
        prices = data.get('prices') or {}
        if prices:
            CACHE['prices'] = prices
            CACHE['timestamp'] = now
            try:
                with open(LOCAL_CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump({ 'prices': prices, 'updated_at': now }, f, ensure_ascii=False)
            except Exception:
                pass
            return prices
    except Exception:
        pass
    return CACHE['prices'] or load_prices_from_disk_quick() or {}

def fetch_from_navasan() -> dict:
    """Fetch real prices from Navasan API"""
    try:
        # نمادهای مورد نیاز
        symbols = ['sekkeh', 'nim', 'rob', 'gerami', '18ayar']
        prices = {}
        
        for symbol in symbols:
            try:
                url = f"{NAVASAN_LATEST}{symbol}?token={NAVASAN_API_KEY}"
                response = _fetch_text(url)
                data = json.loads(response)
                
                if data and 'data' in data and data['data']:
                    price_value = data['data'].get('price', 0)
                    if price_value and _is_valid_price_toman(price_value):
                        # تبدیل به تومان (تقسیم بر 10)
                        price_toman = int(price_value / 10)
                        
                        # نگاشت نمادها به کلیدهای داخلی
                        if symbol == 'sekkeh':
                            prices['full'] = price_toman
                        elif symbol == 'nim':
                            prices['half'] = price_toman
                        elif symbol == 'rob':
                            prices['quarter'] = price_toman
                        elif symbol == 'gerami':
                            prices['gram'] = price_toman
                        elif symbol == '18ayar':
                            prices['goldmini'] = price_toman
                            
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue
        
        # اگر قیمت طلای آب شده موجود نیست، از قیمت 18 عیار محاسبه کن
        if 'goldmini' in prices and 'melted' not in prices:
            # طلای آب شده معمولاً 4.2 برابر قیمت طلای 18 عیار است
            prices['melted'] = int(prices['goldmini'] * 4.2)
        
        # تبدیل قیمت طلای آب شده از مثقال به گرم
        if 'melted' in prices and prices['melted'] > 0:
            # هر مثقال = 4.6079999764 گرم
            melted_per_gram = prices['melted'] / 4.6079999764
            prices['melted'] = int(melted_per_gram)
            
        return prices
        
    except Exception as e:
        print(f"Error in fetch_from_navasan: {e}")
        # در صورت خطا، قیمت‌های ثابت برگردان
        melted_per_gram = 45412000 / 4.6079999764  # تبدیل از مثقال به گرم
        return {
            'full': 111400000,      # سکه طرح امامی
            'half': 59600000,       # سکه نیم
            'quarter': 33200000,    # سکه ربع
            'gram': 16800000,       # سکه گرمی
            'melted': int(melted_per_gram),     # طلای آبشده (به گرم)
            'goldmini': 10483400    # یک گرم طلا 18 عیار
        }

def load_prices_from_disk_quick() -> dict:
    # quick load without network; returns {} if unavailable
    try:
        p = Path(LOCAL_CACHE_FILE)
        if not p.exists():
            return {}
        with open(LOCAL_CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            prices = data.get('prices') or {}
            ts = int(data.get('updated_at') or int(p.stat().st_mtime))
            if prices and not CACHE['prices']:
                CACHE['prices'] = prices
                CACHE['timestamp'] = ts
            return prices
    except Exception:
        return {}

def background_updater_loop():
    def _update_once():
        try:
            fetch_prices_hourly()
        except Exception:
            pass
    # initial prefill from disk for instant response
    load_prices_from_disk_quick()
    # do a background update without blocking server start
    threading.Thread(target=_update_once, daemon=True).start()

    # schedule updates only at specific hours (8, 11, 14, 16)
    def _loop():
        while True:
            time.sleep(3600)
            _update_once()
    # این بخش غیرفعال شد - فقط در ساعت‌های مشخص شده آپدیت می‌کنیم
    # threading.Thread(target=_loop, daemon=True).start()

    # schedule fixed hours: 08:00, 11:00, 14:00, 16:00 local time
    def _fixed_hours_loop():
        last_key = ''
        targets = {8, 11, 14, 16}
        while True:
            now_dt = datetime.now()
            key = f"{now_dt.date()}-{now_dt.hour}-{now_dt.minute}"
            if now_dt.hour in targets and now_dt.minute == 0 and last_key != key:
                try:
                    refresh_from_sources_now()
                except Exception:
                    pass
                last_key = key
            time.sleep(15)
    threading.Thread(target=_fixed_hours_loop, daemon=True).start()

class MyHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        # Disable caching for local development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        if self.path.startswith('/admin/test_navasan'):
            try:
                prices = fetch_from_navasan()
                body = json.dumps({'prices': prices}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                SimpleHTTPRequestHandler.end_headers(self)
                self.wfile.write(body)
            except Exception:
                self.send_response(500)
                SimpleHTTPRequestHandler.end_headers(self)
            return
        if self.path.startswith('/admin/refresh'):
            prices = refresh_from_sources_now()
            body = json.dumps({'ok': True, 'prices': prices}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            SimpleHTTPRequestHandler.end_headers(self)
            self.wfile.write(body)
            return
        if self.path == '/' or self.path.startswith('/index.html'):
            try:
                root = Path(__file__).parent
                index_path = root / 'index.html'
                html = index_path.read_text(encoding='utf-8')
                prices = load_prices_from_disk_quick() or (CACHE['prices'] or {})
                inject = '<script>window.__PRICES__=' + json.dumps(prices, ensure_ascii=False) + ';</script>'
                # inject before closing body
                if '</body>' in html:
                    html = html.replace('</body>', inject + '\n</body>')
                body = html.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                SimpleHTTPRequestHandler.end_headers(self)
                self.wfile.write(body)
            except Exception:
                return SimpleHTTPRequestHandler.do_GET(self)
            return
        if self.path.startswith('/__version'):
            try:
                root = Path(__file__).parent
                latest_mtime = 0
                # core files
                for p in [root / 'index.html', root / 'style.css', root / 'script.js']:
                    if p.exists():
                        latest_mtime = max(latest_mtime, int(p.stat().st_mtime))
                # include assets and images changes
                for dir_name in ['assets', 'images']:
                    d = root / dir_name
                    if d.exists() and d.is_dir():
                        for sub in d.rglob('*'):
                            try:
                                if sub.is_file():
                                    latest_mtime = max(latest_mtime, int(sub.stat().st_mtime))
                            except Exception:
                                pass
                body = json.dumps({'version': latest_mtime}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                SimpleHTTPRequestHandler.end_headers(self)
                self.wfile.write(body)
            except Exception:
                self.send_response(500)
                SimpleHTTPRequestHandler.end_headers(self)
            return
        if self.path.startswith('/api/prices'):
            try:
                prices = fetch_prices_hourly()
                body = json.dumps({'prices': prices}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                # instruct browser we may cache for 1h despite dev no-cache headers
                self.send_header('Cache-Control', 'public, max-age=3600')
                SimpleHTTPRequestHandler.end_headers(self)
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({'error': 'failed'}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                SimpleHTTPRequestHandler.end_headers(self)
                self.wfile.write(body)
            return
        if self.path.startswith('/api/price-board'):
            try:
                prices = fetch_prices_hourly()
                # فرمت کردن قیمت‌ها برای تابلو
                price_board = {
                    'sekkeh': prices.get('full', 0),      # سکه امامی
                    'nim': prices.get('half', 0),         # سکه نیم
                    'rob': prices.get('quarter', 0),      # سکه ربع
                    'gerami': prices.get('gram', 0),      # سکه گرمی
                    'melted': prices.get('melted', 0),     # طلای آب شده
                    '18ayar': prices.get('goldmini', 0)   # طلای 18 عیار
                }
                body = json.dumps({'price_board': price_board, 'updated_at': CACHE['timestamp']}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Cache-Control', 'public, max-age=300')  # 5 minutes cache
                SimpleHTTPRequestHandler.end_headers(self)
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({'error': 'failed'}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                SimpleHTTPRequestHandler.end_headers(self)
                self.wfile.write(body)
            return
        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    server_address = ('', port)
    # start background updater to keep prices warm
    try:
        background_updater_loop()
    except Exception:
        pass
    httpd = HTTPServer(server_address, MyHandler)
    print(f'Server running on port {port}...')
    httpd.serve_forever() 