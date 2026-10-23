"""
Adım 8: Paylaşım kartları.

    python scripts/08_paylasim_kartlari.py            # HTML kartları ve kartlar.json'u yazar, PNG'leri üretir
    python scripts/08_paylasim_kartlari.py --png-yok  # yalnızca HTML ve kartlar.json

Her kartın sayısı web/veri.js'teki veri setinden, alıntısı alıntı bankasından (veri.js içindeki
doğrulanmış alıntılar) gelir; kartta sabit yazılmış sayı yoktur. Sayı kartlarının görseli (kare
ızgarası, oy kareleri, çubuklar) ana grafiğin diliyle SVG/HTML olarak aynı sayılardan çizilir;
alıntı kartlarında görsel yoktur. Kartlar önce HTML olarak yazılır
(atlasın yazı tipleri ve renkleriyle, web/kartlar/*.html), sonra PNG'ye çevrilir. PNG için yeni bir
Python bağımlılığı yoktur: 06 betiği gibi standart kütüphaneyle çalışır; metin dizgisi için
makinedeki Chromium tabanlı tarayıcı (Edge ya da Chrome) başsız modda ekran görüntüsü alır.
Tarayıcı bulunamazsa HTML'ler ve kartlar.json yine yazılır, PNG atlanır ve durum bildirilir.

Ayrıca iki sayfaya özel, sözcüksüz paylaşım önizlemesi yazar: web/onizleme-simulasyon.png (kart-01'in
kare ızgarası) ve web/onizleme-vizyon.png (kart-03'ün kareleri); çerçeve web/onizleme.png ile aynıdır (06 betiği).

web/kartlar/kartlar.json: her kartın kimliği, sayıları, metinleri ve dayandığı veri setinin
SHA-256'sı. tests/test_kartlar.py sayıları veri setinden yeniden hesaplar ve bu dosyayla
karşılaştırır; 04, veri.js yeniden üretildiğinde SHA tutmuyorsa kartların yenilenmesi gerektiğini
bildirir.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
WEB = KOK / "web"
HEDEF = WEB / "kartlar"
BOYUTLAR = {"1200x630": (1200, 630), "1080x1080": (1080, 1080)}
UYE_AD = {
    "SSCB": {"tr": "Sovyetler Birliği", "en": "Soviet Union"}, "RUS": {"tr": "Rusya Federasyonu", "en": "Russian Federation"},
    "USA": {"tr": "ABD", "en": "United States"}, "GBR": {"tr": "Birleşik Krallık", "en": "United Kingdom"},
    "FRA": {"tr": "Fransa", "en": "France"}, "CHN": {"tr": "Çin", "en": "China"},
}
UYE_SIRASI = ["SSCB", "RUS", "USA", "GBR", "FRA", "CHN"]
RENK = {"SSCB": "#7E2F3C", "RUS": "#C2666F", "USA": "#24507F", "GBR": "#2F7A6E", "FRA": "#A8782A", "CHN": "#5E4E9A"}
TARAYICILAR = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def veri_oku() -> dict:
    s = (WEB / "veri.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"):s.rstrip().rindex(";")])


def konsey_buyuklugu(k: dict) -> int:
    return 11 if k["tarih"] < "1966-01-01" else 15


def sayilar(V: dict) -> dict:
    """Kartların bütün sayıları; tests/test_kartlar.py aynı hesabı bağımsız olarak yapar."""
    K = V["kayitlar"]
    oylu = [k for k in K if not k["kapali"] and k["oy"]]
    kapali = [k for k in K if k["kapali"]]
    cogunluk = lambda k: 9 if konsey_buyuklugu(k) == 15 else 7
    tek = [k for k in K if k["oy"] and k["oy"]["aleyhte"] == 1 and k["oy"]["lehte"] + 1 == konsey_buyuklugu(k)]
    G = [k for k in K if k["tarih"] >= "2022-04-26"]
    gorusulen = [k for k in G if k.get("gk") and k["gk"]["durum"] == "yapildi"]
    tartismalar = {x["id"]: x for k in gorusulen for x in k["gk"]["tartismalar"] if x["tur"] == "veto_girisimi"}
    soz_alan = sum(1 for x in tartismalar.values() if all(d != "hayir" for d in x["konusmacilar"]["veto_eden_konustu"].values()))
    uye = Counter(u for k in K if not k["kapali"] for u in k["uyeler"])
    konular = {}
    for konu in ("Filistin ve Arap-İsrail meselesi", "Suriye", "Güney Afrika, Namibya ve Rodezya", "Üyelik başvuruları"):
        c = Counter(u for k in K if k["konu"] == konu and not k["kapali"] for u in k["uyeler"])
        en_cok, sayi = c.most_common(1)[0]
        konular[konu] = {"uye": en_cok, "oy": sayi, "toplam": sum(c.values()), "en": (V["meta"].get("konularEn") or {}).get(konu, konu)}
    return {
        "toplam": len(K), "kapali": len(kapali), "oylu": len(oylu),
        "vetosuz_kabul": sum(1 for k in oylu if k["oy"]["lehte"] >= cogunluk(k)),
        "tek_ret": len(tek), "tek_ret_1966_oncesi": sum(1 for k in tek if konsey_buyuklugu(k) == 11),
        "gk_sonrasi": len(G), "gk_gorusulen": len(gorusulen), "vg_tartisma": len(tartismalar), "vg_soz_alan": soz_alan,
        "uye_ret": {u: uye[u] for u in UYE_SIRASI}, "ret_toplam": sum(uye.values()),
        "konu": konular,
        "son_tarih": max(k["tarih"] for k in K),
        "temsil": temsil_sayilari(temsil_oku()),
    }


def temsil_oku() -> dict:
    return json.loads((KOK / "data/processed/temsil.json").read_text(encoding="utf-8"))


def yuzde(p: float, dil: str) -> str:
    s = f"{100 * p:.1f}"
    return ("%" + s.replace(".", ",")) if dil == "tr" else (s + "%")


_BIRLER = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
_ONLAR = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]
_UNLU = "aeıioöuü"


def _son_kelime(sayi: str) -> str:
    """Sayının (1946, 264, %37,9) Türkçe okunuşundaki son kelime: ekin uyumu buna bakar (%37,9: "virgül dokuz")."""
    tam, _, kesir = re.sub(r"[^0-9,]", "", sayi).partition(",")
    n = int(kesir or tam)
    if n == 0:
        return "sıfır"
    if n % 10:
        return _BIRLER[n % 10]
    if n % 100:
        return _ONLAR[n % 100 // 10]
    return "yüz" if n % 1000 else "bin"


def ek(sayi, tur: str = "i") -> str:
    """Sayı, kıvrık kesme ve okunuşuna uyan Türkçe ek. tur: "i" iyelik (264’ü, 27’si), "ini" iyelik ve belirtme
    (%39,1’ini, %37,9’unu), "inde" iyelik ve bulunma (15’inde), "den" çıkma (1946’dan, 2022’den). Sayı veriden
    geldiği için ek sabit yazılmaz: değer değişince ek de değişir."""
    s = str(sayi)
    k = _son_kelime(s)
    u = [c for c in k if c in _UNLU][-1]
    kalin, yuvarlak = u in "aıou", u in "oöuü"
    if tur == "den":
        return f"{s}’" + ("t" if k[-1] in "çfhkpsşt" else "d") + ("an" if kalin else "en")
    v = ("u" if yuvarlak else "ı") if kalin else ("ü" if yuvarlak else "i")
    return f"{s}’" + ("s" if k[-1] in _UNLU else "") + v + {"i": "", "ini": "n" + v, "inde": "nd" + ("a" if kalin else "e")}[tur]


def temsil_sayilari(T: dict) -> dict:
    """Kart 09–11'in sayıları temsil.json'dan; tests/test_kartlar.py aynı hesabı bağımsız yapar."""
    g = {x["kod"]: x for x in T["gruplar"] + T["kumeler"]}
    sec = lambda x: {"uye": x["uye_sayisi"], "nufus": x["paylar"]["nufus_2023"], "butce": x["paylar"]["butce"], "personel": x["paylar"]["personel"],
                     "koltuk": x["koltuk"]["toplam_payi"], "daimi": x["koltuk"]["daimi"], "secilmis": x["koltuk"]["secilmis"], "toplam": x["koltuk"]["toplam"]}
    return {"ASP": sec(g["ASP"]), "AFR": sec(g["AFR"]), "P5": sec(g["P5"]), "koltuk_toplam": T["meta"]["toplamlar"]["koltuk"], "daimi_toplam": T["meta"]["toplamlar"]["daimi"],
            "nufus_yili": 2023, "personel_tarihi": T["meta"]["personel_tarihi"], "olcek_donemi": T["meta"]["olcek_donemi"]}


def alinti(V: dict, kimlik: str) -> dict:
    return next(a for a in V["alintilar"] if a["id"] == kimlik)


def tarih_uzun(x: str, dil: str) -> str:
    aylar = {"tr": ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
             "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]}[dil]
    y, a, g = x.split("-")
    return f"{int(g)} {aylar[int(a) - 1]} {y}"


def hitap_kunyesi(a: dict, dil: str) -> str:
    oturum = "".join(ch for ch in a["etkinlik"].split(".")[0] if ch.isdigit())
    if dil == "tr":
        return f"{a['etkinlik']} · {tarih_uzun(a['tarih'], 'tr')} · s. {a['basili_sayfa']}"
    son = {"1": "st", "2": "nd", "3": "rd"}.get(oturum[-1], "th") if oturum[-2:] not in ("11", "12", "13") else "th"
    # Resmî İngilizce metnin sayfası; BM kaydından geliyorsa belge simgesiyle (A/74/PV.3, p. 22). Resmî İngilizcesi olmayan
    # alıntıda Türkçe kaynağın sayfası.
    sayfa = f"{a['belge_en']}, p. {a['basili_sayfa_en']}" if a["belge_en"] else f"p. {a['basili_sayfa_en'] or a['basili_sayfa']}"
    return f"Address to the {oturum}{son} Session of the UN General Assembly · {tarih_uzun(a['tarih'], 'en')} · {sayfa}"


def kartlar(V: dict, S: dict) -> list[dict]:
    """Kart listesi: her kart iki dilde başlık/sayı, en fazla iki cümle ve kaynak satırı taşır."""
    k2026, k2025, k2019 = alinti(V, "2026-1"), alinti(V, "2025-1"), alinti(V, "2019-1")
    # Alt bilgi tek satırdır: kaynak ve veri tarihi solda, atlasın adı ve adresi sağda (orta nokta yalnızca künyede).
    veri_kaynak = {"tr": f"DHL veto listesi ve S/PV kayıtları, {tarih_uzun(S['son_tarih'], 'tr')}",
                   "en": f"DHL veto list and S/PV records, {tarih_uzun(S['son_tarih'], 'en')}"}
    return [
        {"id": "kart-01-vetosuz", "tur": "sayi",
         "buyuk": {"tr": f"{S['vetosuz_kabul']} / {S['toplam']}", "en": f"{S['vetosuz_kabul']} / {S['toplam']}"},
         "metin": {"tr": f"Veto nedeniyle kabul edilemeyen {S['toplam']} önerinin {ek(S['vetosuz_kabul'])}, veto olmasaydı kayıtlı oylarla kabul edilmiş olacaktı. Kalan {S['kapali']} veto kapalı oturumda kullanılmış olup oy dağılımları kayıtlı değildir.",
                   "en": f"Of the {S['toplam']} proposals not adopted owing to a veto, {S['vetosuz_kabul']} would have been adopted on the recorded votes had there been no veto. The remaining {S['kapali']} vetoes were cast in private meetings, and their votes are not on record."},
         "kaynak": veri_kaynak},
        {"id": "kart-02-tek-ret", "tur": "sayi",
         "buyuk": {"tr": str(S["tek_ret"]), "en": str(S["tek_ret"])},
         "metin": {"tr": f"{S['tek_ret']} öneri, Konseyin diğer bütün üyeleri olumlu oy kullanmış olmasına rağmen tek bir ret oyu nedeniyle kabul edilememiştir.",
                   "en": f"{S['tek_ret']} proposals were not adopted on a single negative vote, although every other member of the Council voted in favour."},
         "kaynak": veri_kaynak},
        {"id": "kart-03-genel-kurul", "tur": "sayi",
         "buyuk": {"tr": f"{S['gk_gorusulen']} / {S['gk_sonrasi']}", "en": f"{S['gk_gorusulen']} / {S['gk_sonrasi']}"},
         # Pay paydaya eşitse "hepsi" / "all"; tartışma sayısı görselin notunda
         "metin": {"tr": f"Nisan {ek(2022, 'den')} bu yana veto nedeniyle kabul edilemeyen {S['gk_sonrasi']} önerinin "
                         + ("tamamı" if S["gk_gorusulen"] == S["gk_sonrasi"] else ek(S['gk_gorusulen'])) + " Genel Kurulda görüşülmüştür.",
                   "en": (f"All {S['gk_sonrasi']} proposals vetoed since April 2022 have" if S["gk_gorusulen"] == S["gk_sonrasi"]
                          else f"Since April 2022, {S['gk_gorusulen']} of the {S['gk_sonrasi']} vetoed proposals have") + " been debated in the General Assembly."},
         "kaynak": {"tr": f"A/RES/76/262, A/…/PV kayıtları ve BM Günlüğü, {tarih_uzun(S['son_tarih'], 'tr')}",
                    "en": f"A/RES/76/262, A/…/PV records and UN Journal, {tarih_uzun(S['son_tarih'], 'en')}"}},
        {"id": "kart-04-besi-de", "tur": "uyeler",
         "buyuk": {"tr": str(S["ret_toplam"]), "en": str(S["ret_toplam"])},
         "metin": {"tr": f"{ek(1946, 'den')} bu yana {S['ret_toplam']} ret oyu kullanılmış olup beş daimî üyenin tamamı vetoya başvurmuştur. Kapalı oturumdaki {S['kapali']} veto üye toplamlarına dâhil değildir.",
                   "en": f"{S['ret_toplam']} negative votes have been cast since 1946, and all five permanent members have used the veto. The {S['kapali']} private-meeting vetoes are not included in the member totals."},
         "kaynak": veri_kaynak},
        {"id": "kart-05-konular", "tur": "sayi",
         "buyuk": {"tr": "4 konu", "en": "4 topics"},
         # Çiftler ve sayılar çubuklarda; gri izin ucunda konunun bütün ret oyları
         "metin": {"tr": "Dört konuda en çok ret oyu kullanan üye, konudaki bütün ret oylarıyla birlikte gösterilmektedir. Sayımda yalnızca kaydın ana konusu esas alınmaktadır.",
                   "en": "The member with the most negative votes on each of four topics is shown against all negative votes on that topic. Only the main topic of each record is counted."},
         "kaynak": {"tr": f"Gündem sözlüğü (ana konu), {tarih_uzun(S['son_tarih'], 'tr')}",
                    "en": f"Agenda glossary (main topic), {tarih_uzun(S['son_tarih'], 'en')}"}},
        *temsil_kartlari(S["temsil"]),
        {"id": "kart-06-alinti-2026", "tur": "alinti",
         "buyuk": {"tr": k2026["metin_tr"], "en": k2026["metin_en"] or k2026["metin_tr"]},
         "metin": {"tr": "Cumhurbaşkanı Recep Tayyip Erdoğan", "en": "President Recep Tayyip Erdoğan"},
         "kaynak": {"tr": hitap_kunyesi(k2026, "tr"), "en": hitap_kunyesi(k2026, "en")}},
        {"id": "kart-07-alinti-2025", "tur": "alinti",
         "buyuk": {"tr": k2025["metin_tr"], "en": k2025["metin_en"] or k2025["metin_tr"]},
         "metin": {"tr": "Cumhurbaşkanı Recep Tayyip Erdoğan", "en": "President Recep Tayyip Erdoğan"},
         "kaynak": {"tr": hitap_kunyesi(k2025, "tr"), "en": hitap_kunyesi(k2025, "en")}},
        {"id": "kart-08-alinti-2019", "tur": "alinti",
         "buyuk": {"tr": k2019["metin_tr"], "en": k2019["metin_en"] or k2019["metin_tr"]},
         "metin": {"tr": "Cumhurbaşkanı Recep Tayyip Erdoğan", "en": "President Recep Tayyip Erdoğan"},
         "kaynak": {"tr": hitap_kunyesi(k2019, "tr"), "en": hitap_kunyesi(k2019, "en")}},
    ]


def temsil_kartlari(R: dict) -> list[dict]:
    """Temsil endeksinden üç kart: nüfus ve koltuk çubukları yan yana; sayılar temsil.json'dan."""
    a, f, p = R["ASP"], R["AFR"], R["P5"]
    # Tarih ve kaynak yalnızca alt bilgide, tek biçimde (cümlede değil); her kart yalnız gösterdiği ölçülerin kaynağını sayar
    # (alt bilgi kare kartta da tek satıra sığsın diye barış gücü tarihi ay ve yılla, nüfus kaynağı yalnız WPP adıyla)
    ay_yil = {d: tarih_uzun(R['personel_tarihi'], d).split(' ', 1)[1] for d in ("tr", "en")}
    parca = {"nufus": {"tr": "WPP 2024", "en": "WPP 2024"},
             "butce": {"tr": f"bütçe ölçeği {R['olcek_donemi']}", "en": f"budget scale {R['olcek_donemi']}"},
             "personel": {"tr": f"barış gücü {ay_yil['tr']}", "en": f"peacekeeping {ay_yil['en']}"},
             "koltuk": {"tr": "Konsey 2026", "en": "Council 2026"}}
    kaynak = lambda *olculer: {d: (lambda s: s[0].upper() + s[1:])(", ".join(parca[o][d] for o in olculer)) for d in ("tr", "en")}
    gorsel = lambda x, ilk="nufus": {"ilk": ilk, ilk: x[ilk], "koltuk": x["koltuk"], "daimi": x["daimi"], "secilmis": x["secilmis"],
                                     **({"personel_tarihi": ay_yil} if ilk == "personel" else {})}
    return [
        {"id": "kart-09-asya-pasifik", "tur": "temsil", "gorsel": gorsel(a),
         "buyuk": {"tr": yuzde(a["nufus"], "tr"), "en": yuzde(a["nufus"], "en")},
         "metin": {"tr": f"Asya-Pasifik Grubunun {a['uye']} üyesi, BM üyesi devletlerin nüfusunun {ek(yuzde(a['nufus'], 'tr'), 'ini')} oluşturmaktadır; Güvenlik Konseyinin {R['koltuk_toplam']} koltuğundan {ek(a['toplam'])} ({yuzde(a['koltuk'], 'tr')}) bu gruba ait olup bunların {ek(a['daimi'])} daimî koltuktur.",
                   "en": f"The {a['uye']} members of the Asia-Pacific Group account for {yuzde(a['nufus'], 'en')} of the population of UN Member States; {a['toplam']} of the Security Council’s {R['koltuk_toplam']} seats ({yuzde(a['koltuk'], 'en')}) belong to this group, {a['daimi']} of them permanent."},
         "kaynak": kaynak("nufus", "koltuk")},
        # Cümle tek ölçüyü (barış gücü personeli) anlatır; ilk çubuk da o ölçüdür
        {"id": "kart-10-afrika", "tur": "temsil", "gorsel": gorsel(f, "personel"),
         "buyuk": {"tr": f"{f['daimi']} / {R['daimi_toplam']}", "en": f"{f['daimi']} / {R['daimi_toplam']}"},
         "metin": {"tr": f"Afrika Grubunun {f['uye']} üyesi, barış gücü üniformalı personelinin {ek(yuzde(f['personel'], 'tr'), 'ini')} sağlamaktadır. Grubun Konseyde {f['secilmis']} seçilmiş koltuğu bulunmakta, daimî koltuğu bulunmamaktadır.",
                   "en": f"The {f['uye']} members of the African Group provide {yuzde(f['personel'], 'en')} of uniformed peacekeeping personnel. The group holds {f['secilmis']} elected seats on the Council and no permanent seat."},
         "kaynak": kaynak("personel", "koltuk")},
        {"id": "kart-11-p5", "tur": "temsil", "gorsel": gorsel(p),
         "buyuk": {"tr": f"{p['daimi']} / {R['daimi_toplam']}", "en": f"{p['daimi']} / {R['daimi_toplam']}"},
         "metin": {"tr": f"Beş daimî üye, BM üyesi devletlerin nüfusunun {ek(yuzde(p['nufus'], 'tr'), 'ini')} oluşturmakta, olağan bütçenin {ek(yuzde(p['butce'], 'tr'), 'ini')} karşılamakta ve Konseyin {R['koltuk_toplam']} koltuğundan {ek(p['toplam'], 'ini')} elinde bulundurmaktadır.",
                   "en": f"The five permanent members account for {yuzde(p['nufus'], 'en')} of the population of UN Member States, contribute {yuzde(p['butce'], 'en')} of the regular budget and hold {p['toplam']} of the Council’s {R['koltuk_toplam']} seats."},
         "kaynak": kaynak("nufus", "butce", "koltuk")},
    ]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


LEHTE, MUREKKEP, MUREKKEP2, VURGU, CIZGI, BOS = "#9AA3B2", "#13213A", "#5A6578", "#A4262C", "#E1DBCF", "#EDE7DA"
PERSONEL = "#5E4E9A"  # web/temsil.html --g-personel (açık tema)


def kare_izgarasi(n: int, dolu: int, sutun: int, adim: float, kare: float, renk: str = LEHTE) -> str:
    """Ana grafiğin dilinde kare ızgarası: ilk `dolu` kare dolu, kalanı kesikli çerçeveli boş (kapalı oturum)."""
    satir = -(-n // sutun)
    r = kare * 0.14
    parcalar = []
    for i in range(n):
        x, y = (i % sutun) * adim + (adim - kare) / 2, (i // sutun) * adim + (adim - kare) / 2
        if i < dolu:
            parcalar.append(f'<rect class="k" x="{x:.1f}" y="{y:.1f}" width="{kare}" height="{kare}" rx="{r:.1f}" fill="{renk}"/>')
        else:
            parcalar.append(f'<rect class="k bos" x="{x:.1f}" y="{y:.1f}" width="{kare}" height="{kare}" rx="{r:.1f}" fill="none" '
                            f'stroke="{MUREKKEP2}" stroke-width="{max(1.5, kare / 9):.1f}" stroke-dasharray="{kare / 4:.1f} {kare / 6:.1f}"/>')
    return f'<svg width="{sutun * adim:.0f}" height="{satir * adim:.0f}" viewBox="0 0 {sutun * adim:.0f} {satir * adim:.0f}" role="img">' + "".join(parcalar) + "</svg>"


def oy_kareleri(n: int, vurgulu: int, kare: int = 16, ara: int = 6) -> str:
    """Bir sıra oy karesi (sitedeki gibi kare): `vurgulu` tanesi vurgu renginde (ret), kalanı lehte."""
    g = n * kare + (n - 1) * ara
    parcalar = [f'<rect class="n{" ret" if i >= n - vurgulu else ""}" x="{i * (kare + ara)}" y="0" width="{kare}" height="{kare}" rx="{kare * 0.14:.1f}" '
                f'fill="{VURGU if i >= n - vurgulu else LEHTE}"/>' for i in range(n)]
    return f'<svg width="{g}" height="{kare}" viewBox="0 0 {g} {kare}" role="img">' + "".join(parcalar) + "</svg>"


def cubuklar(satirlar: list[tuple[str, int, str, int | None]], genislik: int, punto: int, etiket_g: int = 0) -> str:
    """Yatay çubuklar: (etiket, değer, renk, arka plan toplamı ya da None). Uzunluk en büyük değere ya da toplama göre.
    etiket_g > 0: etiket solda sabit genişlikte; 0: etiket çubuğun üstünde."""
    azami = max(max(v, t or 0) for _, v, _, t in satirlar)
    if any(t for *_, t in satirlar):
        azami /= 0.86  # en uzun izin ucunda "/ N" yazısına yer
    parcalar = []
    for etiket, deger, renk, toplam in satirlar:
        # Gri iz arka plan toplamıdır; ucunda toplam ikincil renkte ("/ N")
        arka = (f'<span class="arka" style="width:{100 * toplam / azami:.1f}%"></span>'
                f'<span class="ct" style="left:calc({100 * toplam / azami:.1f}% + 10px);font-size:{punto}px">/ {toplam}</span>') if toplam else ""
        parcalar.append(f'<div class="cs{" ustte" if not etiket_g else ""}" style="grid-template-columns:{f"{etiket_g}px 1fr" if etiket_g else "1fr"}">'
                        f'<div class="ce" style="font-size:{punto}px">{etiket}</div>'
                        f'<div class="cb">{arka}<span class="on" style="width:{100 * deger / azami:.1f}%;background:{renk}"></span>'
                        f'<span class="cd" style="font-size:{punto}px">{deger}</span></div></div>')
    return f'<div class="cubuklar" style="width:{genislik}px">' + "".join(parcalar) + "</div>"


def gorsel(kart: dict, dil: str, S: dict, genislik: int, yukseklik: int) -> str:
    """Kartın sağ yarısı (yatay) ya da sayının altı (kare): kartın verisini gösteren sade görsel."""
    kimlik = kart["id"]
    if kimlik == "kart-01-vetosuz":
        sutun = 19  # 19 × 14 = 266
        adim = min(genislik / sutun, yukseklik / -(-S["toplam"] // sutun))
        return kare_izgarasi(S["toplam"], S["vetosuz_kabul"], sutun, adim, adim * 0.78)
    if kimlik == "kart-02-tek-ret":
        not_ = {"tr": f"Bunların {ek(S['tek_ret_1966_oncesi'])} {ek(1966, 'den')} önce, Konsey 11 üyeliyken ona karşı bir oyla kabul edilememiştir.",
                "en": f"{S['tek_ret_1966_oncesi']} of them were not adopted ten to one before 1966, when the Council had 11 members."}[dil]
        return oy_kareleri(15, 1) + f'<div class="not">{not_}</div>'
    if kimlik == "kart-03-genel-kurul":
        sutun = 11
        adim = min(genislik / sutun, 48)
        hepsi = S["vg_soz_alan"] == S["vg_tartisma"]
        etiket = {"tr": f"Vetoyu kullanan ülke {S['vg_tartisma']} tartışmanın " + ("tamamında" if hepsi else ek(S['vg_soz_alan'], 'inde')) + " söz almıştır.",
                  "en": "The vetoing country spoke in " + (f"all {S['vg_tartisma']}" if hepsi else f"{S['vg_soz_alan']} of the {S['vg_tartisma']}") + " debates."}[dil]
        return (kare_izgarasi(S["gk_sonrasi"], S["gk_gorusulen"], sutun, adim, adim * 0.78)
                + '<div class="isaretler">' + kare_izgarasi(S["vg_tartisma"], S["vg_soz_alan"], 15, adim * 0.5, adim * 0.36, MUREKKEP)
                + f'<div class="not">{etiket}</div></div>')
    if kart["tur"] == "temsil":
        g = kart["gorsel"]
        ilk = g["ilk"]
        pt = g.get("personel_tarihi", {})
        et = {"tr": ({"nufus": "Nüfus payı 2023", "personel": f"Barış gücü personeli payı, {pt.get('tr')}"}[ilk], "Koltuk payı"),
              "en": ({"nufus": "Population share 2023", "personel": f"Share of peacekeeping personnel, {pt.get('en')}"}[ilk], "Seat share")}[dil]
        renk = {"nufus": LEHTE, "personel": PERSONEL}[ilk]  # Kim temsil ediliyor? sayfasındaki göstergenin rengi
        ayrim = {"tr": f"{g['daimi']} daimî ve {g['secilmis']} seçilmiş", "en": f"{g['daimi']} permanent and {g['secilmis']} elected"}[dil]
        return (f'<div class="cubuklar" style="width:{genislik}px">'
                f'<div class="cs ustte" style="grid-template-columns:1fr"><div class="ce" style="font-size:22px">{et[0]}</div>'
                f'<div class="cb"><span class="arka" style="width:100%"></span><span class="on" style="width:{100 * g[ilk]:.1f}%;background:{renk}"></span><span class="cd" style="font-size:22px">{yuzde(g[ilk], dil)}</span></div></div>'
                f'<div class="cs ustte" style="grid-template-columns:1fr"><div class="ce" style="font-size:22px">{et[1]}, {ayrim}</div>'
                f'<div class="cb"><span class="arka" style="width:100%"></span><span class="on" style="width:{100 * g["koltuk"]:.1f}%;background:{MUREKKEP}"></span><span class="cd" style="font-size:22px">{yuzde(g["koltuk"], dil)}</span></div></div>'
                "</div>")
    if kimlik == "kart-04-besi-de":
        return cubuklar([(UYE_AD[u][dil], S["uye_ret"][u], RENK[u], None) for u in UYE_SIRASI], genislik, 22, 230)
    if kimlik == "kart-05-konular":
        satirlar = []
        for ad, v in S["konu"].items():
            kisa = (ad.split(" ve ")[0] if ad.startswith("Filistin") else ad.split(",")[0] if ad.startswith("Güney") else ad) if dil == "tr" else \
                   (v["en"].split(" and ")[0] if ad.startswith("Filistin") else v["en"].split(",")[0] if ad.startswith("Güney") else v["en"])
            satirlar.append((f"{kisa} – {UYE_AD[v['uye']][dil]}", v["oy"], RENK[v["uye"]], v["toplam"]))
        return cubuklar(satirlar, genislik, 22, 0)
    return ""


def html(kart: dict, dil: str, boyut: str, S: dict) -> str:
    g, y = BOYUTLAR[boyut]
    kare = g == y
    alinti = kart["tur"] == "alinti"
    uzunluk = len(kart["buyuk"][dil])
    ust_bosluk, yan = 48, 72  # üst bant yok; kimlik alt bilgideki işaret ve çizgiyle
    ic_g = g - 2 * yan
    if alinti:
        punto = 56 if uzunluk < 90 else 46 if uzunluk < 160 else 38
        if kare:
            punto += 6
    else:
        punto = 150 if uzunluk <= 6 else (118 if kare else 96) if uzunluk <= 10 else 72
    if alinti:
        gorsel_html = ""
    elif kare:
        gorsel_html = gorsel(kart, dil, S, ic_g, 500)
    else:
        gorsel_html = gorsel(kart, dil, S, (ic_g - 48) // 2, y - ust_bosluk - 44 - 40 - 72)
    yer = {"tr": "Veto Atlası · vetoatlas.com", "en": "Veto Atlas · vetoatlas.com"}[dil]
    # Köşedeki işaret (web/isaret.svg, boşluksuz kırpılmış): eski dosyadaki gibi 44 × 44 px kutu, çizim içinde ortalanmış 34 px
    # yükseklikte (eski kutudaki halka 33,9 px görünüyordu). Kutu aynı kaldığı için alt bilgi satırının yüksekliği ve yeri değişmez.
    isaret = (WEB / "isaret.svg").read_text(encoding="utf-8")
    vb_g, vb_y = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', isaret).groups())
    kutu = vb_y * 44 / 34  # 44 px'lik kutunun viewBox birimi; çizim 34 px
    isaret = re.sub(r'viewBox="0 0 [\d.]+ [\d.]+" width="[\d.]+" height="[\d.]+"',
                    f'viewBox="{-(kutu - vb_g) / 2:.2f} {-(kutu - vb_y) / 2:.2f} {kutu:.2f} {kutu:.2f}" width="44" height="44"', isaret, count=1)
    # Kartta işaret adın yanında süstür (eski dosyadaki gibi): görsel rolü ve başlığı alınmaz
    isaret = re.sub(r"<title>[^<]*</title>", "", re.sub(r' role="img" aria-label="[^"]*"', ' aria-hidden="true"', isaret, count=1), count=1)
    # Sol üst etiket yalnızca alıntı kartlarında ("Söz ve Kayıt"); sayı kartlarında atlasın adı alt bilgide zaten var
    baslik = ("Söz ve Kayıt" if dil == "tr" else "Word and Record") if alinti else ""
    buyuk_metin = kart["buyuk"][dil]
    if alinti:  # kart alıntıyı “ ” içine alır: alıntının içindeki çift tırnak tek tırnak olur (kaynak metin değişmez)
        buyuk_metin = buyuk_metin.replace("“", "‘").replace("”", "’")
    buyuk = f'<div class="buyuk{" alinti" if alinti else ""}" lang="{"tr" if alinti and not kart["buyuk"].get("en") else dil}">{esc(buyuk_metin)}</div>'
    metin = f'<div class="metin">{esc(kart["metin"][dil])}</div>'
    if alinti:
        govde = f'<div class="govde dikey">{buyuk}{metin}</div>'
    elif kare:
        govde = f'<div class="govde dikey">{buyuk}<div class="gorsel">{gorsel_html}</div>{metin}</div>'
    else:
        govde = f'<div class="govde yatay"><div class="sol">{buyuk}{metin}</div><div class="gorsel">{gorsel_html}</div></div>'
    return f"""<!doctype html>
<html lang="{dil}"><head><meta charset="utf-8"><title>{esc(kart['id'])} · {dil} · {boyut}</title>
<link rel="stylesheet" href="../fonts/fonts.css">
<style>
html, body {{ margin: 0; width: {g}px; height: {y}px; overflow: hidden; background: #FBF8F1; color: {MUREKKEP}; }}
.kart {{ box-sizing: border-box; width: {g}px; height: {y}px; padding: {ust_bosluk}px {yan}px 36px; display: flex; flex-direction: column; }}
.ust {{ font-family: "Source Sans 3", "Segoe UI", sans-serif; font-weight: 600; font-size: 22px; color: {MUREKKEP2}; }}
.govde {{ flex: 1; min-height: 0; display: flex; }}
.govde.dikey {{ flex-direction: column; justify-content: center; gap: {26 if kare else 20}px; }}
.govde.yatay {{ flex-direction: row; align-items: center; gap: 48px; }}
.govde.yatay .sol {{ flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; gap: 20px; }}
.govde.yatay .gorsel {{ flex: 0 0 {(ic_g - 48) // 2}px; display: flex; flex-direction: column; justify-content: center; align-items: flex-start; gap: 12px; }}
.govde.dikey .gorsel {{ display: flex; flex-direction: column; gap: 12px; }}
.buyuk {{ font-family: "Source Serif 4", Georgia, serif; font-weight: 600; font-size: {punto}px; line-height: {1.0 if not alinti else 1.25}; font-variant-numeric: tabular-nums; }}
.buyuk.alinti::before {{ content: "“"; }} .buyuk.alinti::after {{ content: "”"; }}
.metin {{ font-family: "Source Sans 3", "Segoe UI", sans-serif; font-size: {34 if kare else 30}px; line-height: 1.35; }}
.not {{ font-family: "Source Sans 3", "Segoe UI", sans-serif; font-size: 20px; color: {MUREKKEP2}; line-height: 1.3; }}
.isaretler {{ display: flex; flex-direction: column; gap: 6px; margin-top: 8px; }}
.cubuklar {{ display: flex; flex-direction: column; gap: {16 if kare else 12}px; font-family: "Source Sans 3", "Segoe UI", sans-serif; }}
.cs {{ display: grid; align-items: center; gap: 14px; }}
.cs.ustte {{ gap: 4px; }}
.cs .ce {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: {MUREKKEP}; }}
.cb {{ position: relative; height: 24px; display: flex; align-items: center; }}
.cb .arka {{ position: absolute; left: 0; top: 0; height: 100%; background: {BOS}; border-radius: 3px; }}
.cb .on {{ position: relative; display: block; height: 100%; border-radius: 3px; }}
.cb .cd {{ position: relative; margin-left: 10px; font-variant-numeric: tabular-nums; color: {MUREKKEP}; }}
.cb .ct {{ position: absolute; white-space: nowrap; font-variant-numeric: tabular-nums; color: {MUREKKEP2}; }}
.alt {{ font-family: "Source Sans 3", "Segoe UI", sans-serif; font-size: {19 if not kare else 18}px; color: {MUREKKEP2}; display: flex; justify-content: space-between; gap: 32px; align-items: baseline; border-top: 1px solid {CIZGI}; padding-top: 12px; margin-top: 16px; white-space: nowrap; }}
.alt .kaynak {{ overflow: hidden; text-overflow: ellipsis; min-width: 0; }}
.alt .ad {{ flex: none; color: {MUREKKEP}; display: inline-flex; align-items: center; gap: 12px; }}
.alt .ad svg {{ display: block; }}
</style></head><body><div class="kart">
{f'<div class="ust">{baslik}</div>' if baslik else ""}
{govde}
<div class="alt"><div class="kaynak">{esc(kart['kaynak'][dil])}</div><div class="ad">{esc(yer)}{isaret}</div></div>
</div></body></html>
"""


ONIZLEMELER = ("onizleme-simulasyon", "onizleme-vizyon")  # web/ kökünde (kartlar klasörü robots.txt'de kapalı)


def onizleme_html(ad: str, S: dict) -> str:
    """Sayfaya özel paylaşım önizlemesi (1200 × 630, sözcüksüz): web/onizleme.png ile aynı çerçeve (sağ üstte büyük sayı, altta
    çizgi ve adres; sol üstteki çubuk logosu PNG'ye logo_ekle ile çizilir); görsel kart-01 (Ya veto olmasaydı?) ve kart-03 (Söz ve
    Kayıt) öğelerinden."""
    g, y = BOYUTLAR["1200x630"]
    sol, sag = 73, 74  # onizleme.png'deki grafiğin kenarları
    genislik = g - sol - sag
    sutun = 38  # 38 × 7 = 266
    ust = round(430 - 7 * genislik / sutun)  # iki önizlemede grafik aynı yükseklikte başlar (büyük sayıyla arası aynı)
    if ad == "onizleme-simulasyon":
        adim = genislik / sutun
        buyuk = f"{S['vetosuz_kabul']} / {S['toplam']}"
        gorsel_html = f'<div class="gorsel" style="top:{ust}px">' + kare_izgarasi(S["toplam"], S["vetosuz_kabul"], sutun, adim, round(adim * 0.78, 1)) + "</div>"
    else:
        # Sözcüksüz görselde açıklamasız sayı yok: küçük karelerin anlamı sayfanın og:image:alt metnindedir.
        # Kareler iki sırada (22 → 11 + 11): grafik simülasyon önizlemesindeki kareyle aynı yükseklikte başlar ve büyük sayı ile
        # alt çizgi arasındaki alanı doldurur (tek sırada alt üçte biri boş kalıyordu).
        # Görünen karelerin dış kenarı simülasyon önizlemesindekiyle aynı çizgide durur (sol, sağ ve üst).
        sutun_v = -(-S["gk_sonrasi"] // 2)
        adim_s = genislik / sutun
        pay_s = (adim_s - round(adim_s * 0.78, 1)) / 2
        adim = (genislik - 2 * pay_s) / (sutun_v - 0.22)
        pay = (adim - round(adim * 0.78, 1)) / 2
        ust += round(pay_s - pay)
        buyuk = f"{S['gk_gorusulen']} / {S['gk_sonrasi']}"
        gorsel_html = (f'<div class="gorsel" style="top:{ust}px; left:{sol + pay_s - pay:.1f}px; right:auto">'
                       + kare_izgarasi(S["gk_sonrasi"], S["gk_gorusulen"], sutun_v, adim, round(adim * 0.78, 1))
                       + f'<div class="isaretler" style="margin-left:{pay - (adim * 0.5 - round(adim * 0.36, 1)) / 2:.1f}px">'
                       + kare_izgarasi(S["vg_tartisma"], S["vg_soz_alan"], S["vg_tartisma"], adim * 0.5, round(adim * 0.36, 1), MUREKKEP)
                       + '</div></div>')
    yazi = lambda s: f'"{s}", "Segoe UI", sans-serif'
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{ad}</title>
<link rel="stylesheet" href="{(WEB / 'fonts/fonts.css').as_uri()}">
<style>
html, body {{ margin: 0; width: {g}px; height: {y}px; overflow: hidden; background: #FBF8F1; color: {MUREKKEP}; }}
body > div {{ position: absolute; }}
.sayi {{ top: 54px; right: {sag}px; font: 600 96px/1 "Source Serif 4", Georgia, serif; font-variant-numeric: tabular-nums; white-space: nowrap; }}
.gorsel {{ left: {sol}px; right: {sag}px; display: flex; flex-direction: column; gap: 16px; }}
.isaretler {{ display: flex; align-items: center; gap: 14px; font: 400 22px/1 {yazi("Source Sans 3")}; color: {MUREKKEP2}; font-variant-numeric: tabular-nums; }}
.alt {{ left: {sol}px; right: {sag}px; bottom: 36px; border-top: 1px solid {CIZGI}; padding-top: 12px; text-align: right; font: 400 19px/1.2 {yazi("Source Sans 3")}; }}
</style></head><body>
<div class="sayi">{buyuk}</div>
{gorsel_html}
<div class="alt">vetoatlas.com</div>
</body></html>
"""


def logo_ekle(kaynak: Path, hedef: Path) -> None:
    """Çubuk logosunu 06 betiğinin çizicisiyle ekler: üç önizlemede logo aynı yerde (89, 74), 40 px ve piksel piksel aynı."""
    import importlib.util
    tanim = importlib.util.spec_from_file_location("onizleme06", KOK / "scripts/06_onizleme_gorseli.py")
    m = importlib.util.module_from_spec(tanim)
    tanim.loader.exec_module(m)
    piksel = m.png_oku(kaynak.read_bytes())
    m.svg_ciz(piksel, "web/logo-cubuk-b.svg", *m.LOGO_YERI, m.LOGO_BOYU)
    m.png_yaz(hedef, piksel)


def tarayici() -> str | None:
    for yol in TARAYICILAR:
        if Path(yol).exists():
            return yol
    return shutil.which("msedge") or shutil.which("chrome") or shutil.which("chromium")


def png_uret(html_yolu: Path, png_yolu: Path, g: int, y: int, exe: str, profil: Path) -> bool:
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", f"--user-data-dir={profil}",
                    f"--window-size={g},{y}", f"--screenshot={png_yolu}", html_yolu.resolve().as_uri()],
                   capture_output=True, timeout=120)
    return png_yolu.exists() and png_yolu.stat().st_size > 1000


def main() -> int:
    png = "--png-yok" not in sys.argv
    V = veri_oku()
    S = sayilar(V)
    liste = kartlar(V, S)
    HEDEF.mkdir(exist_ok=True)
    manifest = {"kaynak_sha256": V["meta"]["kaynak_sha256"], "veri_surumu": V["meta"].get("veri_surumu"), "sayilar": S,
                "kartlar": liste, "dosyalar": []}
    exe = tarayici() if png else None
    profil = Path(tempfile.mkdtemp(prefix="veto-kart-")) if exe else None
    eksik = 0
    for kart in liste:
        for dil in ("tr", "en"):
            for boyut, (g, y) in BOYUTLAR.items():
                ad = f"{kart['id']}-{dil}-{boyut}"
                h = HEDEF / f"{ad}.html"
                h.write_text(html(kart, dil, boyut, S), encoding="utf-8")
                kayit = {"kart": kart["id"], "dil": dil, "boyut": boyut, "html": h.name, "png": None}
                if exe:
                    p = HEDEF / f"{ad}.png"
                    if png_uret(h, p, g, y, exe, profil):
                        kayit["png"] = p.name
                        kayit["png_sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
                    else:
                        eksik += 1
                manifest["dosyalar"].append(kayit)
    # Sayfaya özel önizlemeler: HTML geçici klasörde, PNG web/ kökünde
    if exe:
        gecici = Path(tempfile.mkdtemp(prefix="veto-onizleme-"))
        for ad in ONIZLEMELER:
            h = gecici / f"{ad}.html"
            h.write_text(onizleme_html(ad, S), encoding="utf-8")
            if png_uret(h, gecici / f"{ad}.png", *BOYUTLAR["1200x630"], exe, profil):
                logo_ekle(gecici / f"{ad}.png", WEB / f"{ad}.png")
            else:
                eksik += 1
        shutil.rmtree(gecici, ignore_errors=True)
    if profil:
        shutil.rmtree(profil, ignore_errors=True)
    (HEDEF / "kartlar.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(liste)} kart × 2 dil × {len(BOYUTLAR)} boyut -> {HEDEF.relative_to(KOK)}/ (HTML)")
    if not png:
        print("PNG atlandı (--png-yok).")
    elif not exe:
        print("UYARI: Chromium tabanlı tarayıcı (Edge/Chrome) bulunamadı; PNG üretilmedi, HTML kartlar hazır.")
    else:
        print(f"PNG: {len(manifest['dosyalar']) - eksik} üretildi, {eksik} üretilemedi ({Path(exe).name})")
    print(f"Veri SHA-256: {manifest['kaynak_sha256'][:16]}… -> kartlar.json")
    return 1 if eksik else 0


if __name__ == "__main__":
    sys.exit(main())
