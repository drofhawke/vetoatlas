"""
Temsil haritası (scripts/13_harita.py; web/harita_veri.js; web/temsil.html, "BM üyeleri haritada"): 193 üyenin her biri
haritada, tartışmalı alanlar kural tablosundaki gibi, renk adımları iki temada da ayrışıyor, harita tablolardan önce ve
haritanın erişilebilir karşılığı (ülke listesi) var. Natural Earth dosyaları yereldeyse çıktı yeniden üretilip baytı baytına
karşılaştırılır.
"""
import csv
import hashlib
import importlib.util
import json
import math
import re

import pytest

from conftest import KOK

WEB = KOK / "web"
URETEC = KOK / "scripts/13_harita.py"


def harita():
    s = (WEB / "harita_veri.js").read_text(encoding="utf-8")
    assert s.startswith("// scripts/13_harita.py üretir; elle düzenlenmez.\nwindow.HARITA_VERISI = ")
    return json.loads(s[s.index("= ") + 2:].rstrip().rstrip(";"))


def temsil():
    return json.loads((KOK / "data/processed/temsil.json").read_text(encoding="utf-8"))


def test_her_uye_haritada_ve_adli():
    H, T = harita(), temsil()
    assert H["kaynak"] == "Natural Earth 5.1.2 (1:50m)" and H["kutu"][2] == 1000
    assert [u["k"] for u in H["uyeler"]] == sorted(u["iso3"] for u in T["uyeler"])
    noktali = {n["k"] for n in H["noktalar"]}
    for u in H["uyeler"]:
        # Her üye haritada: çizgiyle ya da (çizgisi 0,1 birimde kaybolan küçük devlet) noktayla
        assert re.fullmatch(r"(M[-\d. ]+l[-\d. ]+z)+", u["d"]) or (not u["d"] and u["k"] in noktali), u["k"]
        assert u["tr"] and u["en"], u["k"]
    ad = {u["k"]: u for u in H["uyeler"]}
    # Site adlandırması (Hikâye ve Söz ve Kayıt ile aynı)
    assert (ad["USA"]["tr"], ad["RUS"]["tr"], ad["GBR"]["tr"], ad["CHN"]["tr"], ad["TUR"]["tr"]) == ("ABD", "Rusya Federasyonu", "Birleşik Krallık", "Çin", "Türkiye")
    assert (ad["USA"]["en"], ad["RUS"]["en"], ad["COD"]["en"]) == ("United States", "Russian Federation", "Democratic Republic of the Congo")
    assert not any("&" in u["en"] or " - " in u["tr"] for u in H["uyeler"])
    # Küçük devletler ayrıca nokta: yalnızca üyeler, her biri haritada bir kez
    noktalar = [n["k"] for n in H["noktalar"]]
    assert len(noktalar) == len(set(noktalar)) and set(noktalar) <= set(ad) and {"MCO", "SMR", "LIE", "TUV", "NRU", "MLT"} <= set(noktalar)


def test_tartismali_alanlar_kural_tablosundaki_gibi():
    H, T = harita(), temsil()
    uyeler = {u["iso3"] for u in T["uyeler"]}
    kurallar = list(csv.DictReader(open(KOK / "kaynaklar/temsil/harita_kurallari.csv", encoding="utf-8")))
    for k in kurallar:
        assert k["katman"] in ("ulke", "ayrik") and (k["atama"] in uyeler or k["atama"] == "-"), k
        assert k["gerekce_tr"] and k["gerekce_en"], k
    atama = {k["ne_adi"]: k["atama"] for k in kurallar}
    assert atama["Crimea"] == "UKR" and atama["Golan Heights"] == "SYR" and atama["Somaliland"] == "SOM"
    assert atama["Northern Cyprus"] == "-" and atama["Western Sahara (Moroccan-administered)"] == "-"
    # Üye devletin parçası olup Natural Earth'te ayrı alan olanlar üyenin rengiyle (boş çizilmez)
    assert atama["Aland"] == "FIN" and "Hong Kong S.A.R." not in atama  # Hong Kong ve Makao: ayrı sayılan bölge (aşağıda)
    # WPP 2024'te Avustralya'nın verisine dahil adalar Avustralya'nın parçası
    assert (atama["Indian Ocean Territories"], atama["Norfolk Island"]) == ("AUS", "AUS")
    # Ayrık alan katmanları haritada, kuraldaki sırayla ve atamayla; "üye değil" atananlar adlı alan olarak üyelerin üstünde
    assert [k["k"] for k in H["katmanlar"]] == [k["atama"] for k in kurallar if k["katman"] == "ayrik" and k["atama"] != "-"]
    assert {a["k"] for a in H["alanlar"] if a.get("ust")} == {k["ne_kodu"] for k in kurallar if k["katman"] == "ayrik" and k["atama"] == "-"}
    # Sayfadaki not kural tablosuyla aynı şeyi söyler
    sayfa = (WEB / "temsil.html").read_text(encoding="utf-8")
    assert "Kırım Ukrayna’nın, Golan Suriye’nin parçası olarak gösterilir" in sayfa
    assert "Crimea is shown as part of Ukraine and the Golan as part of Syria" in sayfa
    assert "Üye olmayan ülke ve alanlar boş çizilir." in sayfa and "Countries and areas that are not UN Member States are drawn empty." in sayfa
    assert atama["Ashmore and Cartier Islands"] == "AUS"  # BM'nin M49 listesinde ayrı alan değil


def test_kaynak_dosyalar_sabit_ozetli_ve_cikti_yeniden_uretilir(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("harita13", URETEC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.SURUM == "5.1.2" and set(m.DOSYALAR) == {"ne_50m_admin_0_countries.geojson", "ne_50m_admin_0_breakaway_disputed_areas.geojson"}
    kaynaklar = (KOK / "kaynaklar/KAYNAKLAR.md").read_text(encoding="utf-8")
    for ad, ozet in m.DOSYALAR.items():
        assert ad in kaynaklar and ozet in kaynaklar, ad
    eksik = [ad for ad, ozet in m.DOSYALAR.items()
             if not (m.KLASOR / ad).exists() or hashlib.sha256((m.KLASOR / ad).read_bytes()).hexdigest() != ozet]
    if eksik:
        pytest.skip(f"Natural Earth dosyası yerelde yok: {eksik} (python scripts/13_harita.py --indir)")
    monkeypatch.setattr(m, "WEB", tmp_path / "harita_veri.js")
    m.main()
    # Satır sonundan bağımsız: core.autocrlf=true olan Windows çalışma ağacında dosya CRLF'dir, üreteç LF yazar
    lf = lambda yol: yol.read_bytes().replace(b"\r\n", b"\n")  # noqa: E731
    assert lf(tmp_path / "harita_veri.js") == lf(WEB / "harita_veri.js")


def _oklab(h):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(int(h[i:i + 2], 16)) for i in (1, 3, 5))
    l, m_, s = ((0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3),
                (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3),
                (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3))
    return (0.2104542553 * l + 0.7936177850 * m_ - 0.0040720468 * s, 1.9779984951 * l - 2.4285922050 * m_ + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m_ - 0.8086757660 * s)


def test_renk_adimlari_iki_temada_ayrisiyor():
    """Öteki üyeler (--bos) < grup üyesi (--h-grup) < seçilmiş koltuk (--g-secilmis) < daimî koltuk (--g-daimi): açıklık sırası
    kâğıtta koyulaşarak, koyu kâğıtta açılarak ilerler; komşu adımlar arasında OKLab ΔE ≥ 20."""
    s = (WEB / "temsil.html").read_text(encoding="utf-8")
    acik, koyu = s[s.index(":root {"):s.index("}", s.index(":root {"))], s[s.index(':root[data-theme="dark"] {'):]
    koyu = koyu[:koyu.index("}")]
    for blok, yon in ((acik, -1), (koyu, 1)):
        renk = [re.search(rf"--{ad}: (#[0-9A-F]{{6}})", blok)[1] for ad in ("bos", "h-grup", "g-secilmis", "g-daimi")]
        L = [_oklab(r)[0] for r in renk]
        assert all(yon * (b - a) > 0 for a, b in zip(L, L[1:])), renk
        assert all(100 * math.dist(_oklab(a), _oklab(b)) >= 20 for a, b in zip(renk[1:], renk[2:])), renk
        assert 100 * math.dist(_oklab(renk[0]), _oklab(renk[1])) >= 20, renk
    # Kırmızı ve yeşil haritada yok (renk kuralları)
    bas = s.index("/* Harita:")
    assert "--vurgu" not in s[bas:s.index("@media (max-width: 760px) { .harita-alt")] and "--kabul" not in s


def test_harita_tablolardan_once_ve_erisilebilir():
    s = (WEB / "temsil.html").read_text(encoding="utf-8")
    assert s.index('aria-labelledby="h-harita"') < s.index('aria-labelledby="h-gruplar"') < s.index('aria-labelledby="h-nufus"')
    assert '<script src="temsil_veri.js"></script>\n<script src="harita_veri.js"></script>' in s
    # Haritanın karşılığı: seçimle aynı ülke listesi; seçim düğmeleri aria-pressed; özet canlı bölge; harita etiketli
    for parca in ('id="harita-tablo"', 'aria-pressed="false"', 'id="harita-ozet" aria-live="polite"', 'svg.setAttribute("aria-label"',
                  '"harita.etiket"', '"liste": ({ n }) =>'):
        assert parca in s, parca
    # Hareket yalnızca renk geçişi; azaltılmış harekette yok
    assert "transition: fill .4s ease;" in s and ".harita path, .harita circle, .ipucu { transition: none; }" in s
    # Grubun kartına bağlantı: kartların kimlikleri
    assert 'id="grup-${esc(g.kod)}"' in s and '<a href="#grup-${secim}">' in s


def test_yakinlastirma_haritayi_degistirmez():
    """Yakınlaştırma yalnızca görünümü (viewBox) değiştirir: yollar ve veri aynı kalır; düğmeler etiketli, düz kaydırma sayfayı
    kaydırır (yalnızca Ctrl + kaydırma haritayı büyütür), hareket azaltma tercihinde geçiş anlık, en çok 8 kat."""
    s = (WEB / "temsil.html").read_text(encoding="utf-8")
    betik = s[s.index("function harita()"):]
    assert "TAM = { x, y, w, h }, EN_COK = 8;" in betik and 'svg.setAttribute("viewBox"' in betik
    # Harita yolları yeniden yazılmaz: "d" yalnızca vurgu ve seçim çizgilerine yazılır
    assert set(re.findall(r'(\w+)\.setAttribute\("d"', betik)) == {"vurgu", "secili"}
    for k in ("art", "azalt", "tum"):
        assert f'data-yakin="{k}"' in s
    for ad in ('"y.art": "Yakınlaştır"', '"y.azalt": "Uzaklaştır"', '"y.tum": "Tüm dünya"', '"y.art": "Zoom in"', '"y.tum": "Whole world"'):
        assert ad in s, ad
    assert "if (!e.ctrlKey) return;" in betik and "{ passive: false }" in betik
    assert "if (hemen || azHareket()) return uygula(hedef);" in betik
    assert ".harita svg.yakin { cursor: grab; touch-action: none; }" in s and "touch-action: manipulation;" in s


def test_ulke_arama_karti_balonlar_ve_adres():
    """Ülke arama (datalist; aksan ve büyük-küçük harf duyarsız), ülke kartı (temsil verisindeki alanlar; bütçe resmî üç ondalık),
    nüfus balonları (alan nüfusla orantılı, ekranda sabit boy) ve adreste saklanan görünüm (#grup=…&ulke=…&balon=1&gorunum=…)."""
    H, s = harita(), (WEB / "temsil.html").read_text(encoding="utf-8")
    # Üreteç her üye için etiket noktası ve ana toprak kutusu yazar
    for u in H["uyeler"]:
        assert len(u["m"]) == 2 and len(u["b"]) == 4 and u["b"][0] <= u["b"][2] and u["b"][1] <= u["b"][3], u["k"]
    fra = next(u for u in H["uyeler"] if u["k"] == "FRA")["b"]
    assert fra[2] - fra[0] < 40  # Fransa'nın kutusu Avrupa'daki Fransa (Guyana ve Réunion değil)
    for parca in ('<input type="search" id="ulke-ara" list="ulke-listesi"', '.normalize("NFD").replace(/[\u0300-\u036f]/g, "")',
                  "toLocaleLowerCase(YEREL)", 'e.inputType === "insertReplacementText"',
                  'satir(t("k.grup")', 'satir(t("k.kabul")', 'satir(t("k.nufus")', 'satir(t("k.butce"), butceYaz(u.butce_yuzde))',
                  'satir(t("k.personel")', 'satir(t("k.iit")', 'satir(t("k.konsey")', "minimumFractionDigits: 3, maximumFractionDigits: 3",
                  "Math.sqrt(n / NUFUS_EN)", 'circle[data-tur="balon"]', ".harita svg.balonlu .balonlar { display: inline; }",
                  'addEventListener("hashchange", () => adrestenOku(true));', 'if (location.protocol !== "about:"',
                  'navigator.share && matchMedia("(pointer: coarse)").matches', "navigator.clipboard.writeText(url)",
                  'if (!q.length && !location.hash.includes("=")) return;'):
        assert parca in s, parca
    # Varsayılan görünüm adrese yazılmaz; seçili ülke haritada mürekkep çizgiyle, dokunmatikte ipucu yerine kart
    assert 'if (secim !== "GK") q.push(`grup=${secim}`);' in s and 'if (sonTur === "mouse") (o.dataset.b ? bolgeIpucu(' in s
    # Dokunmatikte kart kaydırması 350 ms bekler; çift dokunma iptal eder (sayfa kayarsa ikinci dokunuş başka ülkeye düşerdi)
    assert "kartKaydir = setTimeout(" in s and "}, 350);" in s and s.count("clearTimeout(kartKaydir);") == 2
    yasak = re.compile(r"\b(adalet|adil|haks[ıi]z|orantısız|unfair|unjust|disproportionate|should|must)\b", re.I)
    assert not yasak.search(re.sub(r"<[^>]+>", " ", s))
    # Dil bağlantısı güncel adresle (paylaşılan görünüm TR/EN geçişinde korunur)
    c = (WEB / "cubuk.js").read_text(encoding="utf-8")
    assert 'var tazele = function () { if (!tek) a.setAttribute("href", dilAdresi(a.getAttribute("data-dil"))); };' in c
    assert "return (u.pathname.split(\"/\").pop() || \"hikaye.html\") + (q ? \"?\" + q : \"\") + u.hash;" in c


def test_hikaye_kucuk_harita():
    """Hikâye 5. adım: Asya-Pasifik ve Afrika gruplarını gösteren küçük harita; veri adım yaklaşınca yüklenir (ilk sayfa hafif
    kalır), tek dosyada üst belgeden okunur; iki renk iki temada da ayrışır (OKLab ΔE ≥ 20)."""
    h = (WEB / "hikaye.html").read_text(encoding="utf-8")
    assert '<script src="harita_veri.js"></script>' not in h
    for parca in ('b.src = "harita_veri.js"; b.onload = miniCiz;', '{ rootMargin: "800px 0px" }', "mio.observe($(\"#adim-5\"));",
                  "window.parent.HARITA_VERISI", '<div class="mini-harita" id="mini-harita"></div>', '"5.harita": ({ asp, afr }) =>'):
        assert parca in h, parca
    acik, koyu = h[h.index(":root {"):], h[h.index(':root[data-theme="dark"] {'):]
    for blok in (acik[:acik.index("}")], koyu[:koyu.index("}")]):
        a, b = (re.search(rf"--{ad}: (#[0-9A-F]{{6}})", blok)[1] for ad in ("murekkep-2", "m-afr"))
        assert 100 * math.dist(_oklab(a), _oklab(b)) >= 20, (a, b)


def test_uye_olmayan_alanlar_adli():
    """Kullanıcı kararı (19 Ekim 2026): BM üyesi olmayan alanlar BM'nin kullandığı adla (WPP 2024; WPP'de yoksa M49), tek istisna
    Kuzey Kıbrıs Türk Cumhuriyeti. Bağlı olunan devlet ve anlaşmazlıklar yazılmaz; ipucunda ad ve durum (üye değil, gözlemci
    devlet, kendi kendini yönetmeyen toprak). İki üye arasında tartışmalı Siachen adsızdır."""
    H = harita()
    satirlar = {r["ne_kodu"]: r for r in csv.DictReader(open(KOK / "kaynaklar/temsil/uye_olmayan_alanlar.csv", encoding="utf-8"))}
    assert {a["k"] for a in H["alanlar"]} == set(satirlar)
    wpp = {r["ad_wpp"] for r in csv.DictReader(open(KOK / "kaynaklar/temsil/nufus_wpp2024.csv", encoding="utf-8"))}
    for a in H["alanlar"]:
        r = satirlar[a["k"]]
        assert set(a) <= {"k", "tr", "en", "durum", "b", "d", "ust", "n"} and a["tr"] and a["en"], a["k"]
        assert r["ad_kaynagi"] in ("WPP 2024", "M49", "Dışişleri Bakanlığı", "Natural Earth"), a["k"]
        if r["ad_kaynagi"] == "WPP 2024":
            assert a["en"] in wpp, a["k"]  # İngilizce ad WPP'deki BM adıyla birebir
    # Türkiye'nin tanıdığı devletler Dışişleri Bakanlığı'nın adıyla (kural; istisna değil)
    assert [k for k, r in satirlar.items() if r["ad_kaynagi"] == "Dışişleri Bakanlığı"] == ["CYN", "KOS", "PSX", "VAT"]
    assert [k for k, r in satirlar.items() if r["durum"] == "sessiz"] == ["KAS"] == [k for k, r in satirlar.items() if r["ad_kaynagi"] == "Natural Earth"]
    al = {a["k"]: a for a in H["alanlar"]}
    assert (al["CYN"]["tr"], al["CYN"]["en"]) == ("Kuzey Kıbrıs Türk Cumhuriyeti", "Turkish Republic of Northern Cyprus")
    assert (al["FLK"]["en"], al["PSX"]["en"], al["TWN"]["en"], al["VAT"]["en"], al["KOS"]["tr"]) == (
        "Falkland Islands (Malvinas)", "Palestine", "China, Taiwan Province of China", "Vatican City", "Kosova")
    # Bakanlığın adları: yerel kopya varsa temsilcilik listesindeki adla karşılaştırılır
    bakanlik = KOK / "kaynaklar/.belgeler/disisleri"
    if (bakanlik / "temsilcilikler.tr_2026-10-19.js").exists():
        kod = {"CYN": "CYN", "KOS": "KOS", "PSX": "PSE", "VAT": "VAT"}
        for dil, alan in (("tr", "ad_tr"), ("en", "ad_en")):
            liste = (bakanlik / f"temsilcilikler.{dil}_2026-10-19.js").read_text(encoding="utf-8")
            for k, r in satirlar.items():
                if r["ad_kaynagi"] == "Dışişleri Bakanlığı":
                    assert re.search(r'"ulkeKod":\s*"' + kod[k] + r'",\s*"ulkeAd":\s*"' + re.escape(r[alan]) + '"', liste), (dil, k)
    assert al["PSX"]["durum"] == al["VAT"]["durum"] == "gozlemci" and al["SAH"]["durum"] == al["B19"]["durum"] == "kyt"
    # M49 adları: yerel kopya varsa sayfadaki adla karşılaştırılır
    m49 = KOK / "kaynaklar/.belgeler/m49/m49_overview_2026-10-19.html"
    if m49.exists():
        import html as h
        metin = h.unescape(m49.read_text(encoding="utf-8", errors="replace"))
        for k, r in satirlar.items():
            if r["ad_kaynagi"] == "M49":
                for parca in r["ad_en"].split(" and C") if k == "IOA" else [r["ad_en"]]:
                    parca = parca if parca.startswith("Christmas") or k != "IOA" else "C" + parca
                    assert f">{parca}<" in metin.replace("> ", ">").replace(" <", "<"), (k, parca)
    # Sayfa: ad parantezsiz, sessiz alanın adı yok; arama bu alanları da bulur
    s = (WEB / "temsil.html").read_text(encoding="utf-8")
    for parca in ("const alanAdi = (a) => a[DIL];", '${a.durum === "sessiz" ? "" : ` data-a="${a.k}"`}',
                  'const o = e.target.closest("[data-k], [data-a]");', "if (!L.length && LA.length === 1) return alanBul(LA[0]);",
                  "\"a.gozlemci\": \"BM’de üye olmayan gözlemci devlet\"", '"a.gozlemci": "Non-member observer State at the UN"'):
        assert parca in s, parca
    assert not re.search(r"\ba\.(bagli|not)\b", s)  # bağlı devlet ve not alanları kalktı


def test_ayri_sayilan_bolgeler():
    """Kullanıcı kararı (19 Ekim 2026): nüfus sayımları ayrı ayrı, özgün isimleriyle. BM istatistiklerinin (WPP 2024 notları) ayrı
    saydığı, üyenin parçası olan bölgeler haritada üyenin renginde ama kendi adı (WPP adı) ve kendi nüfusuyla; nüfusları üyeye
    eklenmez. Üye olmayan alanlar da WPP'de serileri varsa kendi nüfuslarıyla."""
    H, T = harita(), temsil()
    wpp = {r["iso3"]: r for r in csv.DictReader(open(KOK / "kaynaklar/temsil/nufus_wpp2024.csv", encoding="utf-8")) if r["iso3"]}
    B = {b["k"]: b for b in H["bolgeler"]}
    assert set(B) == {"HKG", "MAC", "GUF", "GLP", "MTQ", "MYT", "REU", "BES"}
    for k, b in B.items():
        assert b["en"] == wpp[k]["ad_wpp"] and b["n"] == round(float(wpp[k]["nufus_2023_bin"]), 3), k
    assert {b["uye"] for b in B.values()} == {"CHN", "FRA", "NLD"}
    uye = {u["iso3"]: u for u in T["uyeler"]}
    for k in ("CHN", "FRA", "NLD"):  # üyenin nüfusu yalnızca kendi serisi (bölgeler eklenmez)
        assert uye[k]["nufus_2023"] == float(wpp[k]["nufus_2023_bin"]), k
    al = {a["k"]: a for a in H["alanlar"]}
    assert al["PRI"]["n"] == round(float(wpp["PRI"]["nufus_2023_bin"]), 3) and al["TWN"]["n"] == round(float(wpp["TWN"]["nufus_2023_bin"]), 3)
    assert al["CYN"]["n"] == 462.747  # KKTC İstatistik Kurumu, 2022 yıl sonu (Kıbrıs'tan çıkarılan sayı)
    assert "n" not in al["KAS"] and "IOA" not in al and "NFK" not in al
    s = (WEB / "temsil.html").read_text(encoding="utf-8")
    for parca in ('`<path data-k="${b.uye}" data-b="${b.k}" d="${b.d}"/>`', 'else if (o.dataset.b) bolgeIpucu(o.dataset.b, e.clientX, e.clientY);',
                  '"b.parca": ({ u }) => `${u} toprağı, nüfusu BM istatistiklerinde ayrı sayılır`', '"k.ayri": ({ liste }) =>'):
        assert parca in s, parca
