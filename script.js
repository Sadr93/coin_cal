function formatNumber(number) {
    if (!number) return '';
    return new Intl.NumberFormat('fa-IR').format(Math.round(number));
}

function convertToPersianNumbers(text) {
    if (!text) return '';
    
    const englishNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
    const persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    
    let result = text.toString();
    for (let i = 0; i < 10; i++) {
        result = result.replace(new RegExp(englishNumbers[i], 'g'), persianNumbers[i]);
    }
    return result;
}

// فرمت ورودی تعداد سکه‌ها به اعداد فارسی و محدود به 0..20
function formatCountInput(input) {
    const persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    const englishNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

    let value = input.value || '';

    // تبدیل فارسی به انگلیسی برای اعتبارسنجی
    for (let i = 0; i < 10; i++) {
        value = value.replace(new RegExp(persianNumbers[i], 'g'), englishNumbers[i]);
    }

    // حذف کاراکتر غیرعددی
    value = value.replace(/[^0-9]/g, '');

    // حذف صفرهای پیشرو
    value = value.replace(/^0+(\d)/, '$1');

    // محدودیت طول به حداکثر دو رقم (برای 0..20 کافی است)
    if (value.length > 2) value = value.slice(0, 2);

    // محدود به بازه 0..20
    let numeric = Number(value || '0');
    if (numeric > 20) numeric = 20;
    if (numeric < 0) numeric = 0;

    // تبدیل دوباره به فارسی برای نمایش
    input.value = convertToPersianNumbers(String(numeric));

    // بعد از تغییر مقدار، محاسبه را به‌روزرسانی کن
    computeTotals();
}

// هنگام فوکوس روی فیلد تعداد، اگر مقدار غیرصفر باشد، صفر شود
function resetCountOnFocus(input) {
    const numeric = getNumericValue(input.value);
    if (numeric !== 0) {
        input.value = '۰';
        computeTotals();
    }
}

function formatInput(input) {
    // تبدیل اعداد فارسی به انگلیسی
    const persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    const englishNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
    
    let value = input.value;
    
    // تبدیل اعداد فارسی به انگلیسی
    for (let i = 0; i < 10; i++) {
        value = value.replace(new RegExp(persianNumbers[i], 'g'), englishNumbers[i]);
    }
    
    // حذف همه کاراکترهای غیر عددی
    value = value.replace(/\D/g, '');
    
    // اگر مقداری وجود داره، فرمت می‌کنیم
    if (value) {
        value = parseInt(value).toLocaleString('fa-IR');
    }
    
    input.value = value;
}

function getNumericValue(formattedValue) {
    if (!formattedValue) return 0;
    
    // تبدیل اعداد فارسی به انگلیسی
    const persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    const englishNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
    
    let value = formattedValue;
    
    // تبدیل اعداد فارسی به انگلیسی
    for (let i = 0; i < 10; i++) {
        value = value.replace(new RegExp(persianNumbers[i], 'g'), englishNumbers[i]);
    }
    
    // حذف همه کاراکترهای غیر عددی و تبدیل به عدد
    return Number(value.replace(/\D/g, ''));
}

function calculate() {
    // دریافت و اعتبارسنجی مبلغ سرمایه‌گذاری
    const amountInput = document.getElementById('amount');
    if (!amountInput) {
        // فرم قدیمی حذف شده؛ فعلاً محاسبه‌ای انجام نمی‌دهیم
        return;
    }
    const amount = getNumericValue(amountInput.value);
    console.log('مبلغ وارد شده:', amount);
    
    if (!amount || isNaN(amount)) {
        alert('لطفاً مبلغ سرمایه‌گذاری را وارد کنید');
        return;
    }

    // محاسبه سود و اقساط
    const annualInterest = 0.37; // 37% سود سالیانه
    const quarterlyInterest = annualInterest / 4; // سود سه‌ماهه
    const totalInterest = amount * annualInterest; // کل سود یک سال
    const quarterlyPayment = amount * quarterlyInterest; // مبلغ سود هر سه ماه

    console.log('سود سه‌ماهه:', quarterlyPayment);

    // نمایش خلاصه اطلاعات
    document.getElementById('investment-amount').textContent = formatNumber(amount);
    document.getElementById('total-interest').textContent = formatNumber(totalInterest);
    document.getElementById('total-payment').textContent = formatNumber(amount + totalInterest);

    // ایجاد جدول اقساط
    const installments = [
        { period: 'پایان سه‌ماه اول', amount: quarterlyPayment },
        { period: 'پایان سه‌ماه دوم', amount: quarterlyPayment },
        { period: 'پایان سه‌ماه سوم', amount: quarterlyPayment },
        { period: 'پایان سه‌ماه چهارم', amount: quarterlyPayment + amount } // اضافه کردن اصل سرمایه به قسط آخر
    ];

    console.log('اقساط:', installments);

    const tbody = document.getElementById('installments');
    console.log('tbody:', tbody);
    tbody.innerHTML = '';
    let totalPayment = 0;

    installments.forEach((installment, index) => {
        const row = document.createElement('tr');
        totalPayment += installment.amount;
        
        row.innerHTML = `
            <td>${convertToPersianNumbers(index + 1)}</td>
            <td>${installment.period}</td>
            <td>${formatNumber(installment.amount)}</td>
        `;
        tbody.appendChild(row);
    });

    // نمایش نتایج
    document.getElementById('results').style.display = 'block';
} 

// --- پیکربندی دریافت قیمت ربع سکه ---
const quarterPriceConfig = {
    enabled: true,
    // آدرس صفحه پروفایل ربع سکه TGJU
    url: 'https://www.tgju.org/profile/rob',
    // سلکتور CSS که کاربر ارسال کرده است
    selector: '#main > div.stocks-profile > div.stocks-header > div.stocks-header-main > div > div.fs-cell.fs-xl-5.fs-lg-5.fs-md-12.fs-sm-12.fs-xs-12.top-header-item-block-1 > div.top-mobile-block > div.block-last-change-percentage > span.price',
};

function toTomanFromRialText(text) {
    if (!text) return '';
    // حذف جداکننده‌ها و غیرعددها، تبدیل فارسی به انگلیسی
    const persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    const englishNumbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
    let clean = text.trim();
    for (let i = 0; i < 10; i++) clean = clean.replace(new RegExp(persianNumbers[i], 'g'), englishNumbers[i]);
    clean = clean.replace(/[^0-9]/g, '');
    if (!clean) return '';
    const rial = Number(clean);
    const toman = Math.round(rial / 10);
    return convertToPersianNumbers(new Intl.NumberFormat('fa-IR').format(toman));
}

async function fetchPriceOnce(config, targetElementId) {
    if (!config.enabled || !config.url || !config.selector) return;

    const priceEl = document.getElementById(targetElementId);
    if (!priceEl) return;

    // نمایش حالت بارگذاری هنگام رفرش دوره‌ای
    priceEl.textContent = 'درحال بارگذاری...';
    priceEl.classList.add('loading-text');

    const tryFetchAndParse = async (url) => {
        const res = await fetch(url, { credentials: 'omit' });
        const html = await res.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const target = doc.querySelector(config.selector);
        if (target && target.textContent) {
            const extracted = target.textContent.replace(/\s+/g, ' ').trim();
            priceEl.textContent = (toTomanFromRialText(extracted) || convertToPersianNumbers(extracted)) + ' تومان';
            priceEl.classList.remove('loading-text');
            computeTotals();
            return true;
        }
        return false;
    };

    try {
        const ok = await tryFetchAndParse(config.url);
        if (ok) return;
    } catch (_) {}

    try {
        const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(config.url)}`;
        const ok2 = await tryFetchAndParse(proxyUrl);
        if (!ok2) {
            priceEl.textContent = 'ناموفق';
            priceEl.classList.remove('loading-text');
            computeTotals();
        }
    } catch (_) {
        priceEl.textContent = 'ناموفق';
        priceEl.classList.remove('loading-text');
        computeTotals();
    }
}

// محاسبه مبلغ کل = جمع (قیمت هر نوع × تعداد)
function computeTotals() {
    const priceQuarterText = (document.getElementById('price-quarter') || {}).textContent || '';
    const priceHalfText = (document.getElementById('price-half') || {}).textContent || '';
    const priceFullText = (document.getElementById('price-full') || {}).textContent || '';

    const countQuarterText = (document.getElementById('count-quarter') || {}).value || '۰';
    const countHalfText = (document.getElementById('count-half') || {}).value || '۰';
    const countFullText = (document.getElementById('count-full') || {}).value || '۰';

    const priceQuarter = getNumericValue(priceQuarterText); // به تومان
    const priceHalf = getNumericValue(priceHalfText);
    const priceFull = getNumericValue(priceFullText);

    const countQuarter = getNumericValue(countQuarterText);
    const countHalf = getNumericValue(countHalfText);
    const countFull = getNumericValue(countFullText);

    const baseTotal = (priceQuarter * countQuarter) + (priceHalf * countHalf) + (priceFull * countFull);

    // تعداد اقساط (ماه‌ها) و افزایش ۳.۹٪ به ازای هر ماه
    const installmentsEl = document.getElementById('installments-count');
    const months = installmentsEl ? getNumericValue(installmentsEl.value) : 0;
    const increaseRate = 0.039 * months;
    const total = baseTotal ? Math.round(baseTotal * (1 + increaseRate)) : 0;

    const totalEl = document.getElementById('detail-total');
    if (totalEl) {
        totalEl.textContent = total ? formatNumber(total) + ' تومان' : '—';
    }

    // مبلغ هر قسط = مبلغ کل / تعداد اقساط
    const perInstallmentEl = document.getElementById('detail-installment');
    if (perInstallmentEl) {
        const per = total && months ? Math.round(total / months) : 0;
        perInstallmentEl.textContent = per ? formatNumber(per) + ' تومان' : '—';
    }

    // وثیقه = (مبلغ کل + ۲۰٪) / قیمت هر گرم طلای دست دوم
    const goldMiniText = (document.getElementById('price-goldmini') || {}).textContent || '';
    const goldMiniPrice = getNumericValue(goldMiniText); // به تومان
    const collateralEl = document.getElementById('detail-collateral');
    if (collateralEl) {
        if (total && goldMiniPrice) {
            const collateral = Math.ceil((total * 1.2) / goldMiniPrice);
            collateralEl.textContent = convertToPersianNumbers(new Intl.NumberFormat('fa-IR').format(collateral)) + ' گرم طلا';
        } else {
            collateralEl.textContent = '—';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const halfConfig = {
        enabled: true,
        url: 'https://www.tgju.org/profile/nim',
        selector: '#main > div.stocks-profile > div.stocks-header > div.stocks-header-main > div > div.fs-cell.fs-xl-3.fs-lg-3.fs-md-6.fs-sm-12.fs-xs-12.top-header-item-block-2.mobile-top-item-hide > div > h3.line.clearfix.mobile-hide-block > span.value > span:nth-child(1)'
    };
    const fullConfig = {
        enabled: true,
        url: 'https://www.tgju.org/profile/sekee',
        selector: '#main > div.stocks-profile > div.stocks-header > div.stocks-header-main > div > div.fs-cell.fs-xl-3.fs-lg-3.fs-md-6.fs-sm-12.fs-xs-12.top-header-item-block-2.mobile-top-item-hide > div > h3.line.clearfix.mobile-hide-block > span.value > span:nth-child(1)'
    };
    const goldMiniConfig = {
        enabled: true,
        url: 'https://www.tgju.org/profile/gold_mini_size',
        selector: '#main > div.stocks-profile > div.stocks-header > div.stocks-header-main > div > div.fs-cell.fs-xl-3.fs-lg-3.fs-md-6.fs-sm-12.fs-xs-12.top-header-item-block-2.mobile-top-item-hide > div > h3.line.clearfix.mobile-hide-block > span.value > span:nth-child(1)'
    };

    const withCacheBust = (url) => url + (url.includes('?') ? '&' : '?') + '_ts=' + Date.now();
    const refreshAllPrices = () => {
        fetchPriceOnce({ ...quarterPriceConfig, url: withCacheBust(quarterPriceConfig.url) }, 'price-quarter');
        fetchPriceOnce({ ...halfConfig, url: withCacheBust(halfConfig.url) }, 'price-half');
        fetchPriceOnce({ ...fullConfig, url: withCacheBust(fullConfig.url) }, 'price-full');
        fetchPriceOnce({ ...goldMiniConfig, url: withCacheBust(goldMiniConfig.url) }, 'price-goldmini');
    };

    // بارگذاری اولیه با کش‌بسـت
    refreshAllPrices();

    const installmentsEl = document.getElementById('installments-count');
    if (installmentsEl) {
        installmentsEl.addEventListener('change', computeTotals);
    }

    // رفرش خودکار هر یک ساعت (۳,۶۰۰,۰۰۰ میلی‌ثانیه)
    setInterval(refreshAllPrices, 3600000);

    // FAQ removed
});