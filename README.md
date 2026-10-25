# Mini OSINT Tarayıcı

Bir kullanıcı adının hangi platformlarda hesabı olduğunu paralel olarak tarayan
mini OSINT aracı. Hem komut satırı (CLI) hem grafik arayüz (GUI) ile çalışır.

> ⚠️ **Yalnızca eğitim ve yetkili kullanım içindir.** Bu araç, herkese açık
> profillerin varlığını kontrol eder. Başkalarını izlemek, taciz etmek veya
> yetkisiz istihbarat için kullanılması yasa dışıdır ve etik değildir.

## Özellikler

- **Paralel tarama** — `ThreadPoolExecutor` ile 24+ platform aynı anda.
- **Status-code tabanlı tespit** — eski metin-arama yöntemine göre daha sağlam.
- **GUI + CLI** — aynı çekirdek motoru (`osint/scanner.py`) paylaşır.
- **JSON çıktı** — sonuçları başka araçlara besleme.
- **SQLite geçmiş** + **HTML rapor**.
- **Genişletilebilir** — yeni site eklemek için sadece `osint/sites.json`.

## Kurulum

```bash
git clone https://github.com/<kullanici-adin>/mini-osint-tool.git
cd mini-osint-tool
pip install -r requirements.txt
```

## Kullanım

### CLI

```bash
python cli.py johndoe                      # canlı sonuç bas
python cli.py johndoe --json               # JSON çıktı
python cli.py johndoe --output sonuc.json  # JSON'u dosyaya yaz
python cli.py johndoe --save-db --report   # veritabanına kaydet + HTML rapor
python cli.py johndoe --workers 30 --timeout 10
```

### GUI

```bash
python gui.py
```

Kutuya kullanıcı adı yaz, **Hedefi Tara**'ya bas (veya Enter). Bulunan hesaplar
yeşil listelenir; linke tıklayınca tarayıcıda açılır. **HTML Rapor Al** ile rapor
üretilir.

## Yeni platform ekleme

`osint/sites.json` içine bir satır ekle:

```json
"PlatformAdi": { "url": "https://site.com/{}", "errorType": "status_code" }
```

`errorType` seçenekleri:

| Tip | Mantık | Ek alan |
|-----|--------|---------|
| `status_code` | HTTP 200 ise hesap var | — |
| `message` | Hata metni sayfada YOKSA hesap var | `errorMsg` |
| `response_url` | Giriş sayfasına yönlenmediyse hesap var | `errorUrl` |

## Doğruluk — sonuçlar kesin değildir

**Negatif sonuçlar:** Instagram/TikTok gibi katı platformlar WAF ve rate-limit
nedeniyle anonim sorguları giriş ekranına yönlendirebilir. Böyle durumda hesap
var olsa bile "bulunamadı" görünebilir. Bu bir hata değil, hedefin savunma
mekanizmasıdır.

**Pozitif sonuçlar (soft-404):** `status_code` yöntemi her platformda kesin
değildir. Bazı siteler var olmayan kullanıcı adına da HTTP 200 döner; bu yüzden
o platformlarda hesap olmadığı halde "bulundu" görünebilir. Her `BULUNDU`
sonucunu linke tıklayıp gözle doğrula. Kalıcı çözüm, her platformu tek tek test
edip `osint/sites.json`'daki `errorType`/`errorMsg` değerlerini sağlam bir
kurala oturtmaktır — bu, aracın sürekli bakım işidir.

## Proje yapısı

```
mini-osint-tool/
├── osint/
│   ├── __init__.py
│   ├── scanner.py     # çekirdek tarama motoru (GUI'den bağımsız)
│   ├── sites.json     # platform listesi
│   ├── storage.py     # SQLite geçmiş
│   └── report.py      # HTML rapor
├── cli.py             # komut satırı arayüzü
├── gui.py             # tkinter arayüzü
├── requirements.txt
├── LICENSE
└── README.md
```

## Lisans

MIT
