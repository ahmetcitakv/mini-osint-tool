"""Komut satiri arayuzu.

Ornek:
    python cli.py johndoe
    python cli.py johndoe --json
    python cli.py johndoe --output sonuc.json --save-db --report
"""

import argparse
import json
import sys

from osint.scanner import siteleri_yukle, tara
from osint import storage, report


def main():
    p = argparse.ArgumentParser(description="Mini OSINT kullanici adi tarayici")
    p.add_argument("kullanici_adi", help="Taranacak kullanici adi")
    p.add_argument("--sites", help="Alternatif sites.json yolu")
    p.add_argument("--workers", type=int, default=20, help="Paralel istek sayisi")
    p.add_argument("--timeout", type=int, default=8, help="Istek zaman asimi (sn)")
    p.add_argument("--json", action="store_true", help="Sonucu JSON bas")
    p.add_argument("--output", help="JSON'u dosyaya yaz")
    p.add_argument("--save-db", action="store_true", help="Bulunanlari SQLite'a kaydet")
    p.add_argument("--report", action="store_true", help="HTML rapor uret")
    args = p.parse_args()

    siteler = siteleri_yukle(args.sites)

    def canli(r):
        # JSON modunda canli yazi basma (ciktiyi kirletmemek icin).
        if args.json or args.output:
            return
        if r["status"] == "found":
            print(f"[+] {r['site']:<14} BULUNDU  {r['url']}")
        elif r["status"] == "error":
            print(f"[!] {r['site']:<14} HATA     {r.get('detay', '')}")
        else:
            print(f"[-] {r['site']:<14} yok")

    sonuclar = tara(
        args.kullanici_adi,
        siteler=siteler,
        max_worker=args.workers,
        timeout=args.timeout,
        on_result=canli,
    )

    bulunan = [r for r in sonuclar if r["status"] == "found"]

    if args.json or args.output:
        metin = json.dumps(sonuclar, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(metin)
            print(f"JSON yazildi: {args.output}", file=sys.stderr)
        else:
            print(metin)
    else:
        print(f"\nOzet: {len(bulunan)} bulundu / {len(sonuclar)} tarandi")

    if args.save_db:
        storage.bulunanlari_kaydet(args.kullanici_adi, sonuclar)
        print(f"Veritabanina {len(bulunan)} kayit eklendi.", file=sys.stderr)

    if args.report:
        yol = report.html_rapor(args.kullanici_adi, sonuclar)
        print(f"Rapor: {yol}", file=sys.stderr)


if __name__ == "__main__":
    main()
