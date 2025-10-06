# راهنمای آپدیت خودکار قیمت‌ها

## روش‌های آپدیت خودکار

### 1. Cron Job (پیشنهادی)
Cron job به صورت خودکار در ساعت‌های زیر قیمت‌ها را آپدیت می‌کند:
- **8:00 صبح** (ساعت تهران)
- **11:00 صبح** (ساعت تهران)  
- **14:00 بعدازظهر** (ساعت تهران)
- **16:00 بعدازظهر** (ساعت تهران)

### 2. اجرای دستی
```bash
# اجرای اسکریپت Python
python3 update_prices.py

# یا اجرای اسکریپت bash
./update_prices.sh
```

### 3. Cron Job (برای سرور شخصی)
```bash
# استفاده از فایل آماده crontab
crontab crontab_tehran.txt

# یا اضافه کردن دستی به crontab
crontab -e

# اضافه کردن خطوط زیر (ساعت تهران):
0 8 * * * /path/to/coin_cal/update_prices.sh
0 11 * * * /path/to/coin_cal/update_prices.sh
0 14 * * * /path/to/coin_cal/update_prices.sh
0 16 * * * /path/to/coin_cal/update_prices.sh
```

## فایل‌های مرتبط

- `update_prices.py`: اسکریپت اصلی آپدیت قیمت‌ها
- `update_prices.sh`: اسکریپت bash برای اجرای آسان
- `crontab_tehran.txt`: فایل آماده crontab برای ساعت تهران
- `prices.json`: فایل قیمت‌های آپدیت شده
- `requirements.txt`: وابستگی‌های Python

## نحوه کارکرد

1. **دریافت قیمت‌ها**: از API Navasan (قیمت‌ها به تومان)
2. **محاسبه طلای آب شده**: از طلای 18 عیار
3. **آپدیت فایل**: `prices.json`
4. **Commit خودکار**: در git (در صورت استفاده از bash script)

## تنظیمات

برای تغییر ساعت‌های آپدیت، فایل `crontab_tehran.txt` را ویرایش کنید.

## عیب‌یابی

- برای اجرای دستی، از `python3 update_prices.py` استفاده کنید
- در صورت خطا، قیمت‌های ثابت استفاده می‌شود
- لاگ‌های cron job در `/var/log/cron` قابل مشاهده است
