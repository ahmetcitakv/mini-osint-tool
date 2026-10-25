"""Tkinter arayuzu. Cekirdek motoru (osint.scanner) kullanir.

Tkinter thread-safe degildir: tarama ayri thread'de doner, sonuclar bir
queue'ya konur, arayuz after() ile periyodik okuyup ekrana yazar.
"""

import queue
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

from osint.scanner import siteleri_yukle, tara
from osint import storage, report

SITELER = siteleri_yukle()

bulunan_hesaplar = []        # [(platform, url)] - rapor icin
aranan_kullanici = ""
sonuc_kuyrugu = queue.Queue()  # worker thread -> GUI


def tarama_motoru(kullanici_adi):
    """Ayri thread'de calisir; sonuclari kuyruga koyar."""
    def ilet(r):
        sonuc_kuyrugu.put(r)
    tara(kullanici_adi, siteler=SITELER, on_result=ilet)
    sonuc_kuyrugu.put({"status": "__bitti__"})


def kuyrugu_isle():
    """GUI thread'inde: kuyruktaki sonuclari ekrana yaz."""
    try:
        while True:
            r = sonuc_kuyrugu.get_nowait()
            if r["status"] == "__bitti__":
                tara_butonu.config(state=tk.NORMAL)
                if bulunan_hesaplar:
                    storage.bulunanlari_kaydet(
                        aranan_kullanici,
                        [{"status": "found", "site": p, "url": u}
                         for p, u in bulunan_hesaplar],
                    )
                return  # polling'i durdur
            if r["status"] == "found":
                sonuc_kutusu.insert(tk.END, f"[+] {r['site']} : BULUNDU\n", "basarili")
                sonuc_kutusu.insert(tk.END, f"    Link: {r['url']}\n", "link_tiklanabilir")
                bulunan_hesaplar.append((r["site"], r["url"]))
            elif r["status"] == "error":
                sonuc_kutusu.insert(tk.END, f"[!] {r['site']} : Baglanti hatasi\n", "uyari")
            else:
                sonuc_kutusu.insert(tk.END, f"[-] {r['site']} : yok\n", "pasif")
            yukleme_cubugu["value"] += 1
            sonuc_kutusu.see(tk.END)
    except queue.Empty:
        pass
    pencere.after(100, kuyrugu_isle)  # 100 ms sonra tekrar bak


def taramayi_baslat():
    global aranan_kullanici
    kullanici_adi = giris.get().strip()
    if not kullanici_adi:
        return
    sonuc_kutusu.delete(1.0, tk.END)
    bulunan_hesaplar.clear()
    aranan_kullanici = kullanici_adi
    yukleme_cubugu["maximum"] = len(SITELER)
    yukleme_cubugu["value"] = 0
    tara_butonu.config(state=tk.DISABLED)

    t = threading.Thread(target=tarama_motoru, args=(kullanici_adi,), daemon=True)
    t.start()
    pencere.after(100, kuyrugu_isle)


def html_rapor_al():
    if not bulunan_hesaplar:
        messagebox.showwarning("Uyari", "Raporlanacak sonuc yok!")
        return
    sonuclar = [{"status": "found", "site": p, "url": u} for p, u in bulunan_hesaplar]
    yol = report.html_rapor(aranan_kullanici, sonuclar)
    import os
    try:
        os.startfile(yol)
    except Exception:
        messagebox.showinfo("Basarili", f"Rapor kaydedildi: {yol}")


def linki_ac(event):
    try:
        index = sonuc_kutusu.index(f"@{event.x},{event.y}")
        if "link_tiklanabilir" in sonuc_kutusu.tag_names(index):
            satir = sonuc_kutusu.get(f"{index} linestart", f"{index} lineend")
            webbrowser.open_new(satir.replace("    Link: ", "").strip())
    except Exception:
        pass


# --- Arayuz cizimi ---
pencere = tk.Tk()
pencere.title("Mini OSINT Tarayici")
pencere.geometry("500x520")
pencere.configure(bg="#1a1a1a")

tk.Label(pencere, text="Hedef Profil Tarayici", font=("Arial", 16, "bold"),
         bg="#1a1a1a", fg="#00ff00").pack(pady=10)

giris = tk.Entry(pencere, font=("Arial", 12), width=28)
giris.pack(pady=5)
giris.bind("<Return>", lambda e: taramayi_baslat())

cerceve = tk.Frame(pencere, bg="#1a1a1a")
cerceve.pack(pady=10)
tara_butonu = tk.Button(cerceve, text="Hedefi Tara", command=taramayi_baslat)
tara_butonu.pack(side=tk.LEFT, padx=5)
tk.Button(cerceve, text="HTML Rapor Al", command=html_rapor_al).pack(side=tk.LEFT, padx=5)

sonuc_kutusu = tk.Text(pencere, width=58, height=18, font=("Courier", 10),
                       bg="#ffffff", fg="#000000")
sonuc_kutusu.pack(pady=10)
sonuc_kutusu.tag_config("basarili", foreground="#0a7d0a")
sonuc_kutusu.tag_config("uyari", foreground="#ff4444")
sonuc_kutusu.tag_config("pasif", foreground="#999999")
sonuc_kutusu.tag_config("link_tiklanabilir", foreground="#58a6ff", underline=True)
sonuc_kutusu.tag_bind("link_tiklanabilir", "<Button-1>", linki_ac)
sonuc_kutusu.tag_bind("link_tiklanabilir", "<Enter>", lambda e: sonuc_kutusu.config(cursor="hand2"))
sonuc_kutusu.tag_bind("link_tiklanabilir", "<Leave>", lambda e: sonuc_kutusu.config(cursor=""))

yukleme_cubugu = ttk.Progressbar(pencere, orient="horizontal", length=350, mode="determinate")
yukleme_cubugu.pack(pady=10)

if __name__ == "__main__":
    pencere.mainloop()
