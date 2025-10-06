#!/usr/bin/env python3
"""
اسکریپت آپدیت خودکار قیمت‌ها
این اسکریپت قیمت‌ها را از API Navasan دریافت کرده و فایل prices.json را آپدیت می‌کند
"""

import json
import requests
import time
from datetime import datetime
import os

# تنظیمات API
NAVASAN_API_KEY = 'freeO05QhWkEZcoEQweVWoxxNqPE7nX0'
NAVASAN_LATEST = 'https://api.navasan.tech/latest/'

def fetch_from_navasan():
    """دریافت قیمت‌ها از API Navasan"""
    symbols = ['sekkeh', 'nim', 'rob', 'gerami', '18ayar']
    prices = {}
    
    for symbol in symbols:
        try:
            url = f"{NAVASAN_LATEST}{symbol}?token={NAVASAN_API_KEY}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data and 'data' in data and data['data']:
                price_value = data['data'].get('price', 0)
                if price_value and 1000 <= price_value <= 1000000000000:
                    price_toman = int(price_value)  # قیمت‌ها در API به تومان هست
                    
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
    
    # محاسبه طلای آب شده از طلای 18 عیار
    if 'goldmini' in prices and 'melted' not in prices:
        prices['melted'] = int(prices['goldmini'] * 4.2)
    
    return prices

def get_fallback_prices():
    """قیمت‌های ثابت در صورت عدم دسترسی به API"""
    return {
        'full': 111400000,      # سکه طرح امامی
        'half': 59600000,       # سکه نیم
        'quarter': 33200000,    # سکه ربع
        'gram': 16800000,       # سکه گرمی
        'melted': 9855034,      # طلای آبشده (به گرم)
        'goldmini': 10483400    # یک گرم طلا 18 عیار
    }

def update_prices_file():
    """آپدیت فایل prices.json"""
    try:
        # تلاش برای دریافت قیمت‌های واقعی
        prices = fetch_from_navasan()
        if not prices or not any(prices.values()):
            raise Exception("No valid prices received")
        
        print("✅ قیمت‌های واقعی از API Navasan دریافت شد")
        
    except Exception as e:
        print(f"⚠️ خطا در دریافت قیمت‌های واقعی: {e}")
        print("🔄 استفاده از قیمت‌های ثابت...")
        prices = get_fallback_prices()
    
    # تبدیل به فرمت مورد نیاز
    price_board = {
        'sekkeh': prices.get('full', 0),
        'nim': prices.get('half', 0),
        'rob': prices.get('quarter', 0),
        'gerami': prices.get('gram', 0),
        'melted': prices.get('melted', 0),
        '18ayar': prices.get('goldmini', 0)
    }
    
    # آپدیت فایل prices.json
    updated_data = {
        'price_board': price_board,
        'updated_at': int(time.time())
    }
    
    with open('prices.json', 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    
    print(f"📅 آپدیت شده در: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💰 قیمت‌های جدید:")
    for key, value in price_board.items():
        print(f"  {key}: {value:,} تومان")
    
    return True

if __name__ == "__main__":
    print("🚀 شروع آپدیت قیمت‌ها...")
    success = update_prices_file()
    if success:
        print("✅ آپدیت قیمت‌ها با موفقیت انجام شد!")
    else:
        print("❌ خطا در آپدیت قیمت‌ها!")
        exit(1)
