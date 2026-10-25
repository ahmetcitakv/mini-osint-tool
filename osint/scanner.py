"""Çekirdek tarama motoru. GUI'den tamamen bagimsiz, CLI de ayni motoru kullanir."""

import json
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

# Tarama kimligi. Gercek bir tarayici gibi davranmak WAF/rate-limit'i azaltir.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# sites.json'un bu dosyanin yanindaki varsayilan yolu.
VARSAYILAN_SITES = pathlib.Path(__file__).with_name("sites.json")


def siteleri_yukle(yol=None):
    """sites.json dosyasini okuyup platform sozlugu dondurur."""
    yol = pathlib.Path(yol) if yol else VARSAYILAN_SITES
    with open(yol, "r", encoding="utf-8") as f:
        return json.load(f)


def site_kontrol(ad, ayar, kullanici_adi, oturum, timeout=8):
    """Tek bir sitede kullanici adini kontrol eder. Dict sonuc dondurur.

    status alani: 'found' | 'not_found' | 'error'
    """
    url = ayar["url"].format(kullanici_adi)
    hata_tipi = ayar.get("errorType", "status_code")

    try:
        cevap = oturum.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
    except requests.RequestException as e:
        return {"site": ad, "url": url, "status": "error", "detay": str(e)}

    if hata_tipi == "status_code":
        bulundu = cevap.status_code == 200
    elif hata_tipi == "message":
        # Hata metni sayfada YOKSA hesap vardir.
        bulundu = ayar["errorMsg"] not in cevap.text
    elif hata_tipi == "contains":
        # Belirteç sayfada VARSA hesap vardir (ters mantik).
        bulundu = ayar["foundMsg"] in cevap.text
    elif hata_tipi == "response_url":
        # Giris/ana sayfaya yonlendirilmediyse hesap vardir.
        bulundu = ayar["errorUrl"] not in cevap.url
    else:
        return {"site": ad, "url": url, "status": "error",
                "detay": f"bilinmeyen errorType: {hata_tipi}"}

    return {
        "site": ad,
        "url": cevap.url if bulundu else url,
        "status": "found" if bulundu else "not_found",
        "http": cevap.status_code,
    }


def tara(kullanici_adi, siteler=None, max_worker=20, timeout=8, on_result=None):
    """Tum siteleri PARALEL tarar. Sonuc listesi dondurur.

    on_result verilirse her site bitince o callback cagrilir (canli akis icin).
    """
    if siteler is None:
        siteler = siteleri_yukle()

    oturum = requests.Session()
    sonuclar = []

    with ThreadPoolExecutor(max_workers=max_worker) as ex:
        gorevler = {
            ex.submit(site_kontrol, ad, ayar, kullanici_adi, oturum, timeout): ad
            for ad, ayar in siteler.items()
        }
        for gorev in as_completed(gorevler):
            sonuc = gorev.result()
            sonuclar.append(sonuc)
            if on_result:
                on_result(sonuc)

    # Bulunanlari basa al, sonra alfabetik.
    oncelik = {"found": 0, "not_found": 1, "error": 2}
    sonuclar.sort(key=lambda r: (oncelik[r["status"]], r["site"].lower()))
    return sonuclar
