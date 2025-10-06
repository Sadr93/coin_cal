# راهنمای آپدیت خودکار قیمت‌ها

## روش‌های آپدیت خودکار

### 1. GitHub Actions (پیشنهادی)
GitHub Actions به صورت خودکار در ساعت‌های زیر قیمت‌ها را آپدیت می‌کند:
- **8:00 صبح** (11:30 تهران)
- **11:00 صبح** (14:30 تهران)  
- **2:00 بعدازظهر** (17:30 تهران)
- **4:00 بعدازظهر** (19:30 تهران)

### 2. اجرای دستی
```bash
# اجرای اسکریپت Python
python3 update_prices.py

# یا اجرای اسکریپت bash
./update_prices.sh
```

### 3. Cron Job (برای سرور شخصی)
```bash
# اضافه کردن به crontab
crontab -e

# اضافه کردن خطوط زیر:
0 8 * * * /path/to/coin_cal/update_prices.sh
0 11 * * * /path/to/coin_cal/update_prices.sh
0 14 * * * /path/to/coin_cal/update_prices.sh
0 16 * * * /path/to/coin_cal/update_prices.sh
```

## فایل‌های مرتبط

- `update_prices.py`: اسکریپت اصلی آپدیت قیمت‌ها
- `update_prices.sh`: اسکریپت bash برای اجرای آسان
- `.github/workflows/update-prices.yml`: GitHub Action
- `prices.json`: فایل قیمت‌های آپدیت شده
- `requirements.txt`: وابستگی‌های Python

## نحوه کارکرد

1. **دریافت قیمت‌ها**: از API Navasan
2. **تبدیل واحد**: از ریال به تومان
3. **محاسبه طلای آب شده**: از طلای 18 عیار
4. **آپدیت فایل**: `prices.json`
5. **Commit خودکار**: در GitHub (در صورت استفاده از GitHub Actions)

## تنظیمات

برای تغییر ساعت‌های آپدیت، فایل `.github/workflows/update-prices.yml` را ویرایش کنید.

## عیب‌یابی

- لاگ‌های GitHub Actions در تب "Actions" قابل مشاهده است
- برای اجرای دستی، از `python3 update_prices.py` استفاده کنید
- در صورت خطا، قیمت‌های ثابت استفاده می‌شود
