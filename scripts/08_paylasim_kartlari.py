"""
Adım 8: Paylaşım kartları.

    python scripts/08_paylasim_kartlari.py            # HTML kartları ve kartlar.json'u yazar, PNG'leri üretir
    python scripts/08_paylasim_kartlari.py --png-yok  # yalnızca HTML ve kartlar.json

Her kartın sayısı web/veri.js'teki veri setinden, alıntısı alıntı bankasından (veri.js içindeki
doğrulanmış alıntılar) gelir; kartta sabit yazılmış sayı yoktur. Sayı kartlarının görseli (kare
ızgarası, nokta dizisi, çubuklar) ana grafiğin diliyle SVG/HTML olarak aynı sayılardan çizilir;
alıntı kartlarında görsel yoktur. Kartlar önce HTML olarak yazılır
(atlasın yazı tipleri ve renkleriyle, web/kartlar/*.html), sonra PNG'ye çevrilir. PNG için yeni bir
Python bağımlılığı yoktur: 06 betiği gibi standart kütüphaneyle çalışır; metin dizgisi için
makinedeki Chromium tabanlı tarayıcı (Edge ya da Chrome) başsız modda ekran görüntüsü alır.
Tarayıcı bulunamazsa HTML'ler ve kartlar.json yine yazılır, PNG atlanır ve durum bildirilir.

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
    sayfa = a["basili_sayfa_en"] or a["basili_sayfa"]
    return f"Address to the {oturum}{son} Session of the UN General Assembly · {tarih_uzun(a['tarih'], 'en')} · p. {sayfa}"


def kartlar(V: dict, S: dict) -> list[dict]:
    """Kart listesi: her kart iki dilde başlık/sayı, en fazla iki cümle ve kaynak satırı taşır."""
    k2026, k2025, k2019 = alinti(V, "2026-1"), alinti(V, "2025-1"), alinti(V, "2019-1")
    konu = S["konu"]
    konu_tr = " · ".join(f"{ad.split(' ve ')[0] if ad.startswith('Filistin') else ad.split(',')[0] if ad.startswith('Güney') else ad} – {UYE_AD[v['uye']]['tr']} {v['oy']}" for ad, v in konu.items())
    konu_en = " · ".join(f"{v['en'].split(' and ')[0] if ad.startswith('Filistin') else v['en'].split(',')[0] if ad.startswith('Güney') else v['en']} – {UYE_AD[v['uye']]['en']} {v['oy']}" for ad, v in konu.items())
    # Alt bilgi tek satırdır: kısa kaynak ve veri tarihi solda, atlasın adı ve adresi sağda.
    veri_kaynak = {"tr": f"Veto Atlası veri seti, {tarih_uzun(S['son_tarih'], 'tr')} · DHL veto listesi ve S/PV kayıtları",
                   "en": f"Veto Atlas dataset, {tarih_uzun(S['son_tarih'], 'en')} · DHL veto list and S/PV records"}
    return [
        {"id": "kart-01-vetosuz", "tur": "sayi",
         "buyuk": {"tr": f"{S['vetosuz_kabul']} / {S['toplam']}", "en": f"{S['vetosuz_kabul']} / {S['toplam']}"},
         "metin": {"tr": f"Veto ile düşen {S['toplam']} önerinin {S['vetosuz_kabul']}'ü, veto olmasaydı kayıtlı oylarla kabul edilmiş olurdu. Oy dağılımı kayıtlı olmayan {S['kapali']} kapalı oturum vetosu hariç.",
                   "en": f"Of the {S['toplam']} vetoed proposals, {S['vetosuz_kabul']} would have been adopted on the recorded votes had there been no veto. Excluding {S['kapali']} private-meeting vetoes with no recorded vote breakdown."},
         "kaynak": veri_kaynak},
        {"id": "kart-02-tek-ret", "tur": "sayi",
         "buyuk": {"tr": str(S["tek_ret"]), "en": str(S["tek_ret"])},
         "metin": {"tr": f"{S['tek_ret']} öneri, Konsey'in öbür bütün üyeleri lehte oy verirken tek bir ret oyuyla düştü. {S['tek_ret_1966_oncesi']}'si 11 üyeli Konsey'de (1966 öncesi) oylandı.",
                   "en": f"{S['tek_ret']} proposals failed on a single negative vote while every other member of the Council voted in favour. {S['tek_ret_1966_oncesi']} of them were voted on in the 11-member Council (before 1966)."},
         "kaynak": veri_kaynak},
        {"id": "kart-03-genel-kurul", "tur": "sayi",
         "buyuk": {"tr": f"{S['gk_gorusulen']} / {S['gk_sonrasi']}", "en": f"{S['gk_gorusulen']} / {S['gk_sonrasi']}"},
         "metin": {"tr": f"Nisan 2022'den bu yana veto ile düşen {S['gk_sonrasi']} önerinin {S['gk_gorusulen']}'si Genel Kurul'da görüşüldü. Veto eden ülke {S['vg_tartisma']} veto girişimi tartışmasının {S['vg_soz_alan']}'inde söz aldı.",
                   "en": f"Since April 2022, {S['gk_gorusulen']} of the {S['gk_sonrasi']} vetoed proposals have been debated in the General Assembly. The vetoing country took the floor in {S['vg_soz_alan']} of the {S['vg_tartisma']} veto initiative debates."},
         "kaynak": {"tr": f"A/RES/76/262 · A/…/PV kayıtları ve BM Günlüğü · {tarih_uzun(S['son_tarih'], 'tr')}",
                    "en": f"A/RES/76/262 · A/…/PV records and UN Journal · {tarih_uzun(S['son_tarih'], 'en')}"}},
        {"id": "kart-04-besi-de", "tur": "uyeler",
         "buyuk": {"tr": str(S["ret_toplam"]), "en": str(S["ret_toplam"])},
         "metin": {"tr": f"1946'dan bu yana {S['ret_toplam']} ret oyu; beş daimî üyenin hepsi veto kullandı. Kapalı oturumdaki {S['kapali']} veto üye toplamına girmez.",
                   "en": f"{S['ret_toplam']} negative votes since 1946; all five permanent members have used the veto. The {S['kapali']} private-meeting vetoes are not included in the member totals."},
         "kaynak": veri_kaynak},
        {"id": "kart-05-konular", "tur": "sayi",
         "buyuk": {"tr": "4 konu", "en": "4 topics"},
         "metin": {"tr": f"Dört konuda en çok ret oyu kullanan üyeler: {konu_tr}. Yalnızca kaydın ana konusu sayılır.",
                   "en": f"The members with the most negative votes on four topics: {konu_en}. Only the main topic of each record is counted."},
         "kaynak": {"tr": f"Veto Atlası veri seti, {tarih_uzun(S['son_tarih'], 'tr')} · gündem sözlüğü (ana konu)",
                    "en": f"Veto Atlas dataset, {tarih_uzun(S['son_tarih'], 'en')} · agenda glossary (main topic)"}},
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
         "buyuk": {"tr": k2019["metin_tr"], "en": k2019["metin_tr"]},
         "metin": {"tr": "Cumhurbaşkanı Recep Tayyip Erdoğan", "en": "President Recep Tayyip Erdoğan (Turkish original; the source has no English text)"},
         "kaynak": {"tr": hitap_kunyesi(k2019, "tr"), "en": hitap_kunyesi(k2019, "en")}},
    ]


def temsil_kartlari(R: dict) -> list[dict]:
    """Temsil endeksinden üç kart: nüfus ve koltuk çubukları yan yana; sayılar temsil.json'dan."""
    a, f, p = R["ASP"], R["AFR"], R["P5"]
    kaynak = {"tr": "Temsil endeksi · WPP 2024 · ölçek 2025–27 · barış gücü Şubat 2026 · Konsey 2026",
              "en": "Representation index · WPP 2024 · scale 2025–27 · peacekeeping Feb 2026 · Council 2026"}
    gorsel = lambda x: {"nufus": x["nufus"], "koltuk": x["koltuk"], "daimi": x["daimi"], "secilmis": x["secilmis"]}
    return [
        {"id": "kart-09-asya-pasifik", "tur": "temsil", "gorsel": gorsel(a),
         "buyuk": {"tr": yuzde(a["nufus"], "tr"), "en": yuzde(a["nufus"], "en")},
         "metin": {"tr": f"Asya-Pasifik Grubu'nun {a['uye']} üyesi BM üyeleri nüfusunun {yuzde(a['nufus'], 'tr')}'ini oluşturuyor; Güvenlik Konseyi'nin {R['koltuk_toplam']} koltuğundan {a['toplam']}'ü ({yuzde(a['koltuk'], 'tr')}) bu grupta, bunun {a['daimi']}'i daimî. Nüfus 2023 tahmini (WPP 2024), koltuklar mevcut dönem (2026).",
                   "en": f"The {a['uye']} members of the Asia-Pacific Group make up {yuzde(a['nufus'], 'en')} of the population of UN Member States; {a['toplam']} of the Security Council's {R['koltuk_toplam']} seats ({yuzde(a['koltuk'], 'en')}) are in this group, {a['daimi']} of them permanent. Population: 2023 estimate (WPP 2024); seats: current term (2026)."},
         "kaynak": kaynak},
        {"id": "kart-10-afrika", "tur": "temsil", "gorsel": gorsel(f),
         "buyuk": {"tr": f"{f['daimi']} / {R['daimi_toplam']}", "en": f"{f['daimi']} / {R['daimi_toplam']}"},
         "metin": {"tr": f"Afrika Grubu'nun {f['uye']} üyesi barış gücü üniformalı personelinin {yuzde(f['personel'], 'tr')}'ini sağlıyor ve olağan bütçe ölçeğinin {yuzde(f['butce'], 'tr')}'ini ödüyor; Konsey'de {f['secilmis']} seçilmiş koltuğu ({yuzde(f['koltuk'], 'tr')}) var, daimî koltuğu yok. Personel 28 Şubat 2026, ölçek 2025–2027, nüfus 2023.",
                   "en": f"The {f['uye']} members of the African Group provide {yuzde(f['personel'], 'en')} of peacekeeping uniformed personnel and pay {yuzde(f['butce'], 'en')} of the regular budget scale; the group holds {f['secilmis']} elected seats on the Council ({yuzde(f['koltuk'], 'en')}) and no permanent seat. Personnel 28 February 2026, scale 2025–2027, population 2023."},
         "kaynak": kaynak},
        {"id": "kart-11-p5", "tur": "temsil", "gorsel": gorsel(p),
         "buyuk": {"tr": f"{p['daimi']} / {R['daimi_toplam']}", "en": f"{p['daimi']} / {R['daimi_toplam']}"},
         "metin": {"tr": f"Beş daimî üye BM üyeleri nüfusunun {yuzde(p['nufus'], 'tr')}'sını oluşturuyor, olağan bütçe ölçeğinin {yuzde(p['butce'], 'tr')}'unu ödüyor ve {R['koltuk_toplam']} koltuğun {p['toplam']}'ini ({yuzde(p['koltuk'], 'tr')}) tutuyor; daimî koltukların tamamı bu beş üyede. Nüfus 2023 tahmini (WPP 2024), ölçek 2025–2027.",
                   "en": f"The five permanent members make up {yuzde(p['nufus'], 'en')} of the population of UN Member States, pay {yuzde(p['butce'], 'en')} of the regular budget scale and hold {p['toplam']} of the {R['koltuk_toplam']} seats ({yuzde(p['koltuk'], 'en')}); all permanent seats are theirs. Population: 2023 estimate (WPP 2024); scale 2025–2027."},
         "kaynak": kaynak},
    ]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


LEHTE, MUREKKEP, MUREKKEP2, VURGU, CIZGI, BOS = "#9AA3B2", "#13213A", "#5A6578", "#A4262C", "#E1DBCF", "#EDE7DA"


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


def nokta_dizisi(n: int, vurgulu: int, adim: float) -> str:
    """Bir sıra nokta: `vurgulu` tanesi vurgu renginde (ret), kalanı lehte."""
    cap = adim * 0.72
    parcalar = [f'<circle class="n{" ret" if i >= n - vurgulu else ""}" cx="{i * adim + adim / 2:.1f}" cy="{adim / 2:.1f}" r="{cap / 2:.1f}" '
                f'fill="{VURGU if i >= n - vurgulu else LEHTE}"/>' for i in range(n)]
    return f'<svg width="{n * adim:.0f}" height="{adim:.0f}" viewBox="0 0 {n * adim:.0f} {adim:.0f}" role="img">' + "".join(parcalar) + "</svg>"


def cubuklar(satirlar: list[tuple[str, int, str, int | None]], genislik: int, punto: int, etiket_g: int = 0) -> str:
    """Yatay çubuklar: (etiket, değer, renk, arka plan toplamı ya da None). Uzunluk en büyük değere ya da toplama göre.
    etiket_g > 0: etiket solda sabit genişlikte; 0: etiket çubuğun üstünde."""
    azami = max(max(v, t or 0) for _, v, _, t in satirlar)
    parcalar = []
    for etiket, deger, renk, toplam in satirlar:
        arka = f'<span class="arka" style="width:{100 * toplam / azami:.1f}%"></span>' if toplam else ""
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
        n = 15
        adim = min(genislik / n, 64)
        not_ = {"tr": f"1966 öncesi 11 üyeli Konsey'de ona karşı bir: {S['tek_ret_1966_oncesi']} öneri",
                "en": f"Before 1966, in the 11-member Council, ten to one: {S['tek_ret_1966_oncesi']} proposals"}[dil]
        return nokta_dizisi(n, 1, adim) + f'<div class="not">{not_}</div>'
    if kimlik == "kart-03-genel-kurul":
        sutun = 11
        adim = min(genislik / sutun, 48)
        etiket = {"tr": f"{S['vg_soz_alan']} / {S['vg_tartisma']} tartışmada veto eden söz aldı",
                  "en": f"vetoing country spoke in {S['vg_soz_alan']} / {S['vg_tartisma']} debates"}[dil]
        return (kare_izgarasi(S["gk_sonrasi"], S["gk_gorusulen"], sutun, adim, adim * 0.78)
                + '<div class="isaretler">' + kare_izgarasi(S["vg_tartisma"], S["vg_soz_alan"], 15, adim * 0.5, adim * 0.36, MUREKKEP)
                + f'<div class="not">{etiket}</div></div>')
    if kart["tur"] == "temsil":
        g = kart["gorsel"]
        et = {"tr": ("Nüfus payı 2023", "Koltuk payı"), "en": ("Population share 2023", "Seat share")}[dil]
        ayrim = {"tr": f"{g['daimi']} daimî + {g['secilmis']} seçilmiş", "en": f"{g['daimi']} permanent + {g['secilmis']} elected"}[dil]
        return (f'<div class="cubuklar" style="width:{genislik}px">'
                f'<div class="cs ustte" style="grid-template-columns:1fr"><div class="ce" style="font-size:22px">{et[0]}</div>'
                f'<div class="cb"><span class="arka" style="width:100%"></span><span class="on" style="width:{100 * g["nufus"]:.1f}%;background:{LEHTE}"></span><span class="cd" style="font-size:22px">{yuzde(g["nufus"], dil)}</span></div></div>'
                f'<div class="cs ustte" style="grid-template-columns:1fr"><div class="ce" style="font-size:22px">{et[1]} · {ayrim}</div>'
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
    ust_bosluk, yan = (48, 72) if kare else (36, 72)
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
        gorsel_html = gorsel(kart, dil, S, (ic_g - 48) // 2, y - 12 - ust_bosluk - 44 - 40 - 72)
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
    baslik = "Söz ve Kayıt" if alinti and dil == "tr" else "Word and Record" if alinti else "Veto Atlası" if dil == "tr" else "Veto Atlas"
    buyuk = f'<div class="buyuk{" alinti" if alinti else ""}" lang="{"tr" if alinti and not kart["buyuk"].get("en") else dil}">{esc(kart["buyuk"][dil])}</div>'
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
.kart {{ box-sizing: border-box; width: {g}px; height: {y}px; padding: {ust_bosluk}px {yan}px 36px; display: flex; flex-direction: column; border-top: 12px solid {MUREKKEP}; }}
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
.alt {{ font-family: "Source Sans 3", "Segoe UI", sans-serif; font-size: {19 if not kare else 18}px; color: {MUREKKEP2}; display: flex; justify-content: space-between; gap: 32px; align-items: baseline; border-top: 1px solid {CIZGI}; padding-top: 12px; margin-top: 16px; white-space: nowrap; }}
.alt .kaynak {{ overflow: hidden; text-overflow: ellipsis; min-width: 0; }}
.alt .ad {{ flex: none; color: {MUREKKEP}; display: inline-flex; align-items: center; gap: 12px; }}
.alt .ad svg {{ display: block; }}
</style></head><body><div class="kart">
<div class="ust">{baslik}</div>
{govde}
<div class="alt"><div class="kaynak">{esc(kart['kaynak'][dil])}</div><div class="ad">{esc(yer)}{isaret}</div></div>
</div></body></html>
"""


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
