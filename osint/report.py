"""HTML rapor uretimi."""

import html


def html_rapor(kullanici_adi, sonuclar, dosya_adi=None):
    """Bulunan hesaplardan HTML rapor uretir, dosya yolunu dondurur."""
    bulunanlar = [r for r in sonuclar if r["status"] == "found"]
    if dosya_adi is None:
        dosya_adi = f"{kullanici_adi}_Rapor.html"

    k = html.escape(kullanici_adi)
    satirlar = "".join(
        f"<li><b>{html.escape(r['site'])}:</b><br>"
        f"<a href='{html.escape(r['url'])}' target='_blank'>{html.escape(r['url'])}</a></li>"
        for r in bulunanlar
    ) or "<li>Hic hesap bulunamadi.</li>"

    icerik = f"""<!DOCTYPE html>
<html lang="tr"><head><meta charset="utf-8"><title>OSINT Raporu: {k}</title>
<style>
  body {{ font-family: Arial, sans-serif; background:#f4f4f9; color:#333; padding:20px; }}
  h2 {{ color:#2c3e50; border-bottom:2px solid #3498db; padding-bottom:10px; }}
  li {{ margin:15px 0; font-size:16px; }}
  a {{ color:#3498db; text-decoration:none; font-weight:bold; }}
  a:hover {{ text-decoration:underline; }}
  .not {{ background:#fff3cd; border-left:6px solid #ffc107; color:#856404;
          padding:15px; margin-top:30px; border-radius:4px; font-size:14px; line-height:1.5; }}
</style></head>
<body>
  <h2>Hedef Analiz Raporu: {k}</h2>
  <p>Bulunan hesap: <b>{len(bulunanlar)}</b> / Taranan: <b>{len(sonuclar)}</b></p>
  <ul>{satirlar}</ul>
  <div class="not">
    <strong>Teknik Not:</strong><br>
    Negatif sonuclar kesin degildir. Bazi platformlar WAF ve rate-limit nedeniyle
    anonim sorgulari giris ekranina yonlendirir; bu durumda hesap var olsa bile
    "bulunamadi" gorunebilir. Arac yalnizca egitim ve yetkili kullanim icindir.
  </div>
</body></html>"""

    with open(dosya_adi, "w", encoding="utf-8") as f:
        f.write(icerik)
    return dosya_adi
