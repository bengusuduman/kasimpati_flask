# Kasımpatı Buketi

İsmini alıp o kişiye özel dijital bir kasımpatı buketi çizen Flask uygulaması.
Buket sunucuda SVG olarak üretilir; aynı isim her zaman aynı buketi verir.

## Çalıştırma

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Tarayıcıda http://127.0.0.1:5000 adresini aç.

## Yapı

- `app.py`: rotalar, isim doğrulama, Türkçe büyük/küçük harf
- `bouquet.py`: isimden buket üreten SVG çizici
- `templates/`: sayfalar
- `static/`: stil ve küçük JavaScript (bağlantı kopyalama, PNG indirme)

## Özelleştirme

- Not kartı: `app.py` içindeki `NOTE` listesi
- Renkler: `bouquet.py` içindeki `PALETTES`, sayfa renkleri `static/style.css` başındaki değişkenler

## Yayına alma

Netlify yalnızca statik siteleri çalıştırır, Flask için uygun değildir.
Render, Railway veya PythonAnywhere kullanabilirsin. Başlatma komutu: `gunicorn app:app`.
