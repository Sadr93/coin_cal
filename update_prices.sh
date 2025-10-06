#!/bin/bash

# اسکریپت آپدیت قیمت‌ها
# این اسکریپت می‌تواند در cron job استفاده شود

echo "🚀 شروع آپدیت قیمت‌ها در $(date)"

# تغییر به دایرکتوری پروژه
cd "$(dirname "$0")"

# اجرای اسکریپت Python
python3 update_prices.py

# اگر در محیط git هست، تغییرات را commit کن
if [ -d ".git" ]; then
    echo "📝 ثبت تغییرات در git..."
    git add prices.json
    git commit -m "Auto-update prices at $(date '+%Y-%m-%d %H:%M:%S')" || echo "⚠️ هیچ تغییر جدیدی برای commit وجود ندارد"
    git push || echo "⚠️ خطا در push کردن تغییرات"
fi

echo "✅ آپدیت قیمت‌ها تکمیل شد در $(date)"
