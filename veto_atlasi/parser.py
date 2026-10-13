"""
Dag Hammarskjöld Kütüphanesi (DHL) veto listesini ayrıştırır.

Kaynak: https://www.un.org/Depts/dhl/resguide/scact_veto_table_en.htm
Tablo sütunları (soldan sağa): Tarih | Karar taslağı | Toplantı kaydı | Gündem maddesi | Ret oyu veren daimi üye

İlke: Hiçbir satır sessizce atılmaz. Ayrıştırılamayan her satır
"inceleme" listesine düşer ve elle kontrol edilir.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from datetime import date

from bs4 import BeautifulSoup

KAYNAK_URL = "https://www.un.org/Depts/dhl/resguide/scact_veto_table_en.htm"
SOZLU_DEGISIKLIK_RE = re.compile(r"\boral amendment\b", re.I)

AYLAR = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

# "25 February 2022", "7-9 January 1980", "06 February 1986"
TARIH_RE = re.compile(
    r"(?P<gun1>\d{1,2})(?:\s*[-–]\s*(?P<gun2>\d{1,2}))?\s+"
    r"(?P<ay>" + "|".join(AYLAR) + r")\s+(?P<yil>\d{4})",
    re.IGNORECASE,
)

# S/2022/155, S/21084, S/17796/Rev.1  (S/PV ile eşleşmez: slash'tan sonra rakam şart)
TASLAK_RE = re.compile(r"S/\d+(?:/\d+)?(?:/Rev\.\s?\d+)?")
TOPLANTI_RE = re.compile(r"S/PV\.\d+(?:\s*\(Resumption\s*\d*\))?", re.IGNORECASE)

# Metin çıkarımında isimler bitişik gelebiliyor ("ChinaRussian Federation"),
# bu yüzden bölmek yerine bilinen isimleri arıyoruz. Uzun isimler önce.
UYE_DESENLERI = [
    (re.compile(r"Russian\s+Federation", re.I), "RUS"),
    (re.compile(r"Soviet\s+Union", re.I), "SSCB"),
    (re.compile(r"(?<![A-Z])USSR(?![A-Za-z])"), "SSCB"),
    (re.compile(r"United\s+Kingdom", re.I), "GBR"),
    (re.compile(r"(?<![A-Z])UK(?![A-Za-z])"), "GBR"),
    (re.compile(r"United\s+States", re.I), "USA"),
    (re.compile(r"(?<![A-Z])USA?(?![A-Za-z])"), "USA"),
    (re.compile(r"China", re.I), "CHN"),
    (re.compile(r"France", re.I), "FRA"),
]

ATIF_BELIRSIZ_RE = re.compile(r"not\s+identified|attributed\s+to", re.I)
ON_SORU_RE = re.compile(r"preliminary\s+question", re.I)

# 1971 öncesi Çin koltuğu Çin Cumhuriyeti'ndeydi (Tayvan). Kaynak bunu "China"
# olarak gösteriyor; ayrımı tarih üzerinden işaretliyoruz.
CIN_KOLTUK_DEGISIMI = date(1971, 10, 25)


@dataclass
class VetoKaydi:
    id: str
    tarih: str | None
    tarih_ham: str
    tarih_aralik_mi: bool
    taslak_belgeler: list[str]
    toplanti_kayitlari: list[str]
    gundem_maddesi: str
    veto_eden_uyeler: list[str]
    kategori: str = "resmi_veto"
    kismi_veto_suphesi: bool = False
    taslak_kaynagi: str = "belge"          # "belge" | "toplanti_kaydi" (erken dönem sözlü öneriler)
    on_soru_vetosu: bool = False           # "preliminary question": usul/esas ayrımına veto (çifte veto)
    atif_belirsiz: bool = False            # kapalı oturum, veto eden üye kaynakta kesin değil
    notlar: list[str] = field(default_factory=list)
    kaynak_url: str = KAYNAK_URL
    belge_linkleri: list[str] = field(default_factory=list)
    # --- Elle zenginleştirilecek alanlar (ilk aşamada boş) ---
    bolge: str | None = None
    konu_kategorisi: str | None = None
    oy_dagilimi: dict | None = None
    ga_tartisma_belgesi: str | None = None
    baglam_ozeti: str | None = None
    vaka_analizi_var: bool = False

    def sozluk(self) -> dict:
        return asdict(self)


def _temizle(metin: str) -> str:
    return re.sub(r"\s+", " ", metin.replace("\xa0", " ")).strip()


def tarih_ayristir(ham: str) -> tuple[str | None, bool]:
    """ISO tarih döndürür. Aralıkta ('7-9 January 1980') ilk günü alır ve işaretler."""
    m = TARIH_RE.search(ham)
    if not m:
        return None, False
    gun = int(m.group("gun1"))
    ay = AYLAR[m.group("ay").lower()]
    yil = int(m.group("yil"))
    try:
        return date(yil, ay, gun).isoformat(), m.group("gun2") is not None
    except ValueError:
        return None, False


def uyeleri_bul(metin: str) -> list[str]:
    bulunan: list[str] = []
    kalan = metin
    for desen, kod in UYE_DESENLERI:
        if desen.search(kalan):
            if kod not in bulunan:
                bulunan.append(kod)
            kalan = desen.sub(" ", kalan)  # "Russian Federation" sonra "US" ile çakışmasın
    return bulunan


def _uye_notlari(uyeler: list[str], iso_tarih: str | None) -> list[str]:
    notlar = []
    if "CHN" in uyeler and iso_tarih and date.fromisoformat(iso_tarih) < CIN_KOLTUK_DEGISIMI:
        notlar.append("Çin koltuğu bu tarihte Çin Cumhuriyeti'ndeydi (Tayvan), ÇHC değil.")
    if "SSCB" in uyeler:
        notlar.append("SSCB vetosu; Rusya Federasyonu koltuğun halefidir, analizde ayrı tutulur.")
    return notlar


def tablo_ayristir(html: str) -> tuple[list[VetoKaydi], list[dict]]:
    """
    Döndürür: (kayıtlar, inceleme_satırları)
    inceleme_satırları: ayrıştırılamayan veya şüpheli satırlar, elle kontrol için.
    """
    soup = BeautifulSoup(html, "lxml")
    kayitlar: list[VetoKaydi] = []
    inceleme: list[dict] = []
    sayac: dict[str, int] = {}

    for sira, tr in enumerate(soup.find_all("tr")):
        hucreler = tr.find_all(["td", "th"])
        metinler = [_temizle(h.get_text(" ")) for h in hucreler]
        tum_metin = " | ".join(metinler)

        if not any(metinler):
            continue

        iso, aralik = tarih_ayristir(metinler[0]) if metinler else (None, False)

        if iso is None:
            # Başlık satırı ya da devam satırı olabilir. Veto bilgisi içeriyorsa incelemeye al.
            if TASLAK_RE.search(tum_metin) or uyeleri_bul(metinler[-1] if metinler else ""):
                inceleme.append({"satir_no": sira, "neden": "tarih_yok", "metin": tum_metin})
            continue

        if len(hucreler) < 5:
            inceleme.append({"satir_no": sira, "neden": f"eksik_hucre({len(hucreler)})", "metin": tum_metin})
            continue

        tarih_h, taslak_h, toplanti_h, gundem_h, uye_h = metinler[:5]
        taslaklar = list(dict.fromkeys(TASLAK_RE.findall(taslak_h)))  # tekrar eden belge numaralarını ayıkla
        toplantilar = [_temizle(t) for t in TOPLANTI_RE.findall(toplanti_h + " " + taslak_h)]
        uyeler = uyeleri_bul(uye_h)
        linkler = [a["href"] for a in tr.find_all("a", href=True)]

        taslak_kaynagi = "belge"
        if not taslaklar and TOPLANTI_RE.search(taslak_h):
            taslak_kaynagi = "toplanti_kaydi"

        atif_belirsiz = bool(ATIF_BELIRSIZ_RE.search(tum_metin))
        on_soru = bool(ON_SORU_RE.search(gundem_h))
        # Yıldız işareti kaynakta iki farklı anlamda kullanılıyor: kısmi veto ve belirsiz atıf.
        kismi = "*" in tum_metin and not atif_belirsiz
        # "oral amendment": veto, taslağa toplantıda sözlü önerilen değişikliğe yöneliktir (kısmi veto).
        # "(as amended)" ve "(incorporating the amendment)" taslağın bütününe yapılan oylamadır; kısmi değildir.
        sozlu_degisiklik = bool(SOZLU_DEGISIKLIK_RE.search(taslak_h))
        kismi = kismi or sozlu_degisiklik

        notlar = _uye_notlari(uyeler, iso)
        if taslak_kaynagi == "toplanti_kaydi":
            notlar.append("Taslak ayrı belge olarak yayımlanmamış; öneri toplantı kaydında yer alıyor.")
        if atif_belirsiz:
            notlar.append("Kapalı oturum: veto eden üye resmi bildiride yok, kaynak tarafından atfedilmiş.")
        if on_soru:
            notlar.append("Ön soru vetosu: konunun usul meselesi sayılıp sayılmayacağına dair oylama (çifte veto).")
        if aralik:
            notlar.append("Kaynakta tarih aralığı var; oylama günü toplantı kaydından doğrulanmalı.")
        if sozlu_degisiklik:
            notlar.append("Kaynakta 'oral amendment': veto, taslağa toplantıda sözlü olarak önerilen değişikliğe yöneliktir.")

        sorunlar = []
        if not taslaklar and taslak_kaynagi != "toplanti_kaydi":
            sorunlar.append("taslak_belge_yok")
        if not uyeler:
            sorunlar.append("veto_eden_uye_yok")
        if sorunlar:
            inceleme.append({"satir_no": sira, "neden": ",".join(sorunlar), "metin": tum_metin})

        # Kararlı kimlik: tarih + sıra (aynı gün birden fazla veto olabilir)
        sayac[iso] = sayac.get(iso, 0) + 1
        kayit_id = f"V-{iso}-{sayac[iso]}"

        kayitlar.append(VetoKaydi(
            id=kayit_id,
            tarih=iso,
            tarih_ham=tarih_h,
            tarih_aralik_mi=aralik,
            taslak_belgeler=taslaklar,
            toplanti_kayitlari=toplantilar,
            gundem_maddesi=gundem_h,
            veto_eden_uyeler=uyeler,
            kismi_veto_suphesi=kismi,
            taslak_kaynagi=taslak_kaynagi,
            on_soru_vetosu=on_soru,
            atif_belirsiz=atif_belirsiz,
            notlar=notlar,
            belge_linkleri=linkler,
        ))

    return kayitlar, inceleme
