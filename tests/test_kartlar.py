"""
Paylaşım kartları (scripts/08_paylasim_kartlari.py, web/kartlar/): her sayı veri setinden yeniden hesaplanır ve
kartlar.json ile karşılaştırılır; kartlar veri setinin güncel SHA-256'sına dayanmalı; kartlarda ve katalogda
değerlendirme içeren dil bulunmaz.
"""
import hashlib
import json
import re
from collections import Counter

from conftest import KOK

VERI = json.loads((KOK / "data/processed/vetolar_mutabik.json").read_text(encoding="utf-8"))
K = VERI["kayitlar"]
MANIFEST = json.loads((KOK / "web/kartlar/kartlar.json").read_text(encoding="utf-8"))
S = MANIFEST["sayilar"]
_js = (KOK / "web/veri.js").read_text(encoding="utf-8")
VERI_JS = json.loads(_js[_js.index("{"):_js.rstrip().rindex(";")])


def boyut(k):
    return 11 if k["tarih"] < "1966-01-01" else 15


def test_kartlar_guncel_veri_setine_dayaniyor():
    assert MANIFEST["kaynak_sha256"] == VERI_JS["meta"]["kaynak_sha256"] == VERI["meta"]["kaynak_sha256"]
    assert len(MANIFEST["kartlar"]) == 11 and len(MANIFEST["dosyalar"]) == 11 * 2 * 2
    for d in MANIFEST["dosyalar"]:
        assert (KOK / "web/kartlar" / d["html"]).exists()
        if d["png"]:  # PNG'ler kartlar.json ile birlikte üretilmiş: özet dosyayla aynı
            p = KOK / "web/kartlar" / d["png"]
            assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == d["png_sha256"], d["png"]


def test_kart_sayilari_veri_setinden():
    oylu = [k for k in K if not k["atif_belirsiz"] and k["oy_dagilimi"]]
    kapali = [k for k in K if k["atif_belirsiz"]]
    assert S["toplam"] == len(K) == 266 and S["kapali"] == len(kapali) == 2 and S["oylu"] == len(oylu)
    assert S["vetosuz_kabul"] == sum(1 for k in oylu if k["oy_dagilimi"]["lehte"] >= (9 if boyut(k) == 15 else 7)) == 264
    tek = [k for k in K if k["oy_dagilimi"] and k["oy_dagilimi"]["aleyhte"] == 1 and k["oy_dagilimi"]["lehte"] + 1 == boyut(k)]
    assert S["tek_ret"] == len(tek) == 55 and S["tek_ret_1966_oncesi"] == sum(1 for k in tek if boyut(k) == 11) == 27
    G = [k for k in K if k["tarih"] >= "2022-04-26"]
    assert S["gk_sonrasi"] == len(G) == 22
    uye = Counter(u for k in K if not k["atif_belirsiz"] for u in k["veto_eden_uyeler"])
    assert S["uye_ret"] == {"SSCB": 114, "RUS": 43, "USA": 94, "GBR": 30, "FRA": 18, "CHN": 23} == dict(uye)
    assert S["ret_toplam"] == sum(uye.values()) == 322
    for konu, beklenen in {"Filistin ve Arap-İsrail meselesi": ("USA", 42), "Suriye": ("RUS", 18),
                           "Güney Afrika, Namibya ve Rodezya": ("GBR", 24), "Üyelik başvuruları": ("SSCB", 51)}.items():
        # Konu sınıflandırması 04'te yapılır; veri.js'ten okunur
        c = Counter(u for k in VERI_JS["kayitlar"] if k["konu"] == konu and not k["kapali"] for u in k["uyeler"])
        assert c.most_common(1)[0] == beklenen == (S["konu"][konu]["uye"], S["konu"][konu]["oy"]), konu


def test_genel_kurul_sayilari_veri_js_ile_ayni():
    # Genel Kurul alanları (gk) veri.js'te; tartışma konuşmacı bilgisi oradan
    K2 = [k for k in VERI_JS["kayitlar"] if k["tarih"] >= "2022-04-26"]
    gorusulen = [k for k in K2 if k.get("gk") and k["gk"]["durum"] == "yapildi"]
    tart = {x["id"]: x for k in gorusulen for x in k["gk"]["tartismalar"] if x["tur"] == "veto_girisimi"}
    assert S["gk_gorusulen"] == len(gorusulen) == 22 and S["vg_tartisma"] == len(tart) == 15
    assert S["vg_soz_alan"] == sum(1 for x in tart.values() if all(d != "hayir" for d in x["konusmacilar"]["veto_eden_konustu"].values())) == 15


def test_alinti_kartlari_alinti_bankasindan_ve_sayfali():
    alintilar = {a["id"]: a for a in VERI_JS["alintilar"]}
    for kart, kimlik in (("kart-06-alinti-2026", "2026-1"), ("kart-07-alinti-2025", "2025-1"), ("kart-08-alinti-2019", "2019-1")):
        k = next(x for x in MANIFEST["kartlar"] if x["id"] == kart)
        a = alintilar[kimlik]
        assert k["buyuk"]["tr"] == a["metin_tr"]
        assert k["buyuk"]["en"] == (a["metin_en"] or a["metin_tr"])
        assert f"s. {a['basili_sayfa']}" in k["kaynak"]["tr"]
        assert f"p. {a['basili_sayfa_en'] or a['basili_sayfa']}" in k["kaynak"]["en"]


def _html(kart, dil="tr", boyut="1200x630"):
    return (KOK / "web/kartlar" / f"{kart}-{dil}-{boyut}.html").read_text(encoding="utf-8")


def test_gorseller_kartin_verisini_gosteriyor():
    """Sayı kartlarının görseli (SVG kare/nokta, çubuk) kartın sayılarıyla birebir; alıntı kartlarında görsel yok."""
    for boyut in ("1200x630", "1080x1080"):
        for dil in ("tr", "en"):
            h = _html("kart-01-vetosuz", dil, boyut)
            assert h.count('<rect class="k"') == 264 and h.count('<rect class="k bos"') == 2
            assert "stroke-dasharray" in h  # kapalı oturum: kesikli çerçeve (ana grafikle aynı)
            h = _html("kart-02-tek-ret", dil, boyut)
            assert h.count('<circle class="n"') == 14 and h.count('<circle class="n ret"') == 1 and "27" in h
            h = _html("kart-03-genel-kurul", dil, boyut)
            assert h.count('<rect class="k"') == 22 + 15 and h.count('<rect class="k bos"') == 0
            h = _html("kart-04-besi-de", dil, boyut)
            assert h.count('<div class="cs') == 6 and all(f">{n}</span>" in h for n in (114, 43, 94, 30, 18, 23))
            h = _html("kart-05-konular", dil, boyut)
            assert h.count('<div class="cs') == 4 and all(f">{n}</span>" in h for n in (42, 18, 24, 51))
            for kart in ("kart-06-alinti-2026", "kart-07-alinti-2025", "kart-08-alinti-2019"):
                h = _html(kart, dil, boyut)
                assert 'role="img"' not in h and 'class="buyuk alinti"' in h  # köşedeki işaret dışında görsel yok
            # Alt bilgi: solda kaynak, sağda ad/adres yer tutucusu; tek satır (nowrap)
            assert 'class="kaynak"' in h and 'class="ad"' in h and "white-space: nowrap" in h


def test_temsil_kartlari_temsil_json_ile_ayni():
    T = json.loads((KOK / "data/processed/temsil.json").read_text(encoding="utf-8"))
    g = {x["kod"]: x for x in T["gruplar"] + T["kumeler"]}
    R = S["temsil"]
    for kod in ("ASP", "AFR", "P5"):
        x = g[kod]
        assert R[kod] == {"uye": x["uye_sayisi"], "nufus": x["paylar"]["nufus_2023"], "butce": x["paylar"]["butce"], "personel": x["paylar"]["personel"],
                          "koltuk": x["koltuk"]["toplam_payi"], "daimi": x["koltuk"]["daimi"], "secilmis": x["koltuk"]["secilmis"], "toplam": x["koltuk"]["toplam"]}
    # Kart metinlerindeki sayılar temsil.json'dan (yüzde, 1 ondalık) üretilmiş
    k = {x["id"]: x for x in MANIFEST["kartlar"]}
    y = lambda p: "%" + f"{100 * p:.1f}".replace(".", ",")
    assert y(g["ASP"]["paylar"]["nufus_2023"]) in k["kart-09-asya-pasifik"]["metin"]["tr"] and y(g["ASP"]["koltuk"]["toplam_payi"]) in k["kart-09-asya-pasifik"]["metin"]["tr"]
    assert y(g["AFR"]["paylar"]["personel"]) in k["kart-10-afrika"]["metin"]["tr"] and y(g["AFR"]["paylar"]["butce"]) in k["kart-10-afrika"]["metin"]["tr"]
    assert y(g["P5"]["paylar"]["nufus_2023"]) in k["kart-11-p5"]["metin"]["tr"] and y(g["P5"]["paylar"]["butce"]) in k["kart-11-p5"]["metin"]["tr"]
    assert k["kart-10-afrika"]["buyuk"]["tr"] == "0 / 5" and k["kart-11-p5"]["buyuk"]["tr"] == "5 / 5"
    assert round(g["P5"]["paylar"]["nufus_2023"], 3) == 0.256 and g["ASP"]["koltuk"]["daimi"] == 1 and g["AFR"]["koltuk"]["daimi"] == 0
    for kart in ("kart-09-asya-pasifik", "kart-10-afrika", "kart-11-p5"):
        for dil in ("tr", "en"):
            h = _html(kart, dil, "1200x630")
            assert h.count('<div class="cs ustte"') == 2 and "Koltuk" in h or "Seat" in h


def test_kart_metinlerinde_degerlendirme_yok_ve_en_fazla_iki_cumle():
    yasak = re.compile(r"\b(adalet|adil|haks|skandal|utanç|başarı|başarısız|çöktü|iflas|unjust|shameful|failure|scandal|must|should)\b", re.I)
    for k in MANIFEST["kartlar"]:
        for dil in ("tr", "en"):
            metin = k["metin"][dil]
            assert not yasak.search(metin), (k["id"], dil)
            if k["tur"] != "alinti":
                assert len(re.findall(r"[.!?](\s|$)", metin)) <= 2, (k["id"], dil, metin)
    katalog = (KOK / "kaynaklar/kart_katalogu.md").read_text(encoding="utf-8")
    for k in MANIFEST["kartlar"]:
        assert k["id"] in katalog, k["id"]
