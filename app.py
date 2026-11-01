import os
import re
import secrets

from flask import Flask, redirect, render_template, request, url_for

from bouquet import build_bouquet, build_stamp

app = Flask(__name__)

# Google Analytics: Render'da GA_MEASUREMENT_ID adıyla ortam değişkeni olarak ekle (G-XXXXXXXXXX).
GA_ID = os.environ.get("GA_MEASUREMENT_ID", "").strip()
if not re.fullmatch(r"G-[A-Z0-9]{4,}", GA_ID):
    GA_ID = ""

# False: renk isme göre belirlenir, aynı kişi hep aynı buketi görür.
# True: link her açıldığında buket rastgele farklı renkte çıkar.
RASTGELE_BUKET = False

# Çiçek kartındaki metinler: istediğin gibi değiştirebilirsin.
NOTE = [
    "ne ilk kasım,",
    "ne ilk kasımpatı,",
    "ne son kasımımız,",
    "ne son kasımpatın.",
]
NOTE_SIGN = "Sevgiyle, Bengüsu"
NAME_RE = re.compile(r"[^\W\d_]+(?: [^\W\d_]+)*")  # yalnızca harf ve tek boşluk
MAX_LEN = 30
ASCII = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")


@app.context_processor
def inject_ga():
    return {"ga_id": GA_ID}


def tr_title(text):
    """Türkçe kurallarıyla baş harfleri büyütür (i → İ, ı → I)."""
    out = []
    for word in text.split():
        first = {"i": "İ", "ı": "I"}.get(word[0], word[0].upper())
        rest = word[1:].replace("I", "ı").replace("İ", "i").lower()
        out.append(first + rest)
    return " ".join(out)


def clean_name(raw):
    name = " ".join((raw or "").split())
    if not name:
        return None, "Önce adını yaz."
    if len(name) > MAX_LEN:
        return None, f"İsim en fazla {MAX_LEN} karakter olabilir."
    if not NAME_RE.fullmatch(name):
        return None, "İsimde yalnızca harf kullanabilirsin."
    return tr_title(name), None


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.translate(ASCII).lower()).strip("-")


def render_home(error=None, value="", status=200):
    return render_template("index.html", error=error, value=value), status


@app.get("/")
def index():
    return render_home()


@app.get("/olustur")
def create():
    raw = request.args.get("isim", "")
    name, error = clean_name(raw)
    if error:
        return render_home(error, raw, 400)
    return redirect(url_for("bouquet", isim=name))


@app.get("/buket/<isim>")
def bouquet(isim):
    name, error = clean_name(isim)
    if error:
        return render_home(error, isim, 400)
    seed = secrets.randbits(64) if RASTGELE_BUKET else None
    return render_template("buket.html", ad=name, file_name=slug(name),
                           svg=build_bouquet(name, animate=True, seed=seed),
                           stamp=build_stamp(name, seed=seed),
                           note=NOTE, sign=NOTE_SIGN)


if __name__ == "__main__":
    app.run(debug=True)