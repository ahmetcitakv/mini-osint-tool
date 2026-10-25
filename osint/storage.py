"""SQLite gecmis kaydi. Bulunan hesaplari kalici saklar."""

import sqlite3
from datetime import datetime

VARSAYILAN_DB = "osint_gecmis.db"


def kur(db_yolu=VARSAYILAN_DB):
    conn = sqlite3.connect(db_yolu)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS aramalar
           (id INTEGER PRIMARY KEY, tarih TEXT, kullanici_adi TEXT,
            platform TEXT, url TEXT)"""
    )
    conn.commit()
    conn.close()


def ekle(kullanici_adi, platform, url, db_yolu=VARSAYILAN_DB):
    conn = sqlite3.connect(db_yolu)
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO aramalar (tarih, kullanici_adi, platform, url) VALUES (?, ?, ?, ?)",
        (tarih, kullanici_adi, platform, url),
    )
    conn.commit()
    conn.close()


def bulunanlari_kaydet(kullanici_adi, sonuclar, db_yolu=VARSAYILAN_DB):
    """tara() sonuclarindan sadece 'found' olanlari veritabanina yazar."""
    kur(db_yolu)
    for r in sonuclar:
        if r["status"] == "found":
            ekle(kullanici_adi, r["site"], r["url"], db_yolu)
