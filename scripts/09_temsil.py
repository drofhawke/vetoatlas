"""
Adım 9: Temsil endeksi.

    python scripts/09_temsil.py --girdi   # ham kaynaklardan kaynaklar/temsil/*.csv üretir (yerel belgeler gerekir)
    python scripts/09_temsil.py           # CSV'lerden data/processed/temsil.json ve web/temsil_veri.js üretir

Birim: BM bölgesel grupları (DGACM listesi). Türkiye iki grupta listelenir, seçimlerde yalnızca WEOG
sayılır; ABD hiçbir grubun üyesi değildir, seçimlerde WEOG sayılır (DGACM notları). Her ikisi WEOG'da
sayılır ve notlanır. Ayrı kümeler: beş daimî üye (P5) ve İslam İşbirliği Teşkilatı (İİT) üyeleri.

Göstergeler (pay = BM üyeleri toplamı içindeki pay):
  nüfus payı 2023 (WPP 2024 tahmini, 1 Ocak, bin), nüfus payı 1963 (o tarihteki 113 üye; ardıl devletler
  toplanır), üye payı, bütçe payı (2025–2027 olağan bütçe ölçeği), personel payı (BM barış gücü üniformalı
  personel, 28 Şubat 2026), daimî koltuk payı (daimî koltuk / 5), toplam koltuk payı (mevcut dönem, / 15)
  ve her gösterge için koltuk/gösterge oranı (toplam koltuk payı / gösterge payı). Bileşik puan yoktur.

Ham kaynaklar: data/raw/temsil/*.html (BM üye devletler, DGACM bölgesel gruplar, İİT üyeler, Güvenlik
Konseyi üyeleri; erişim 10 Ekim 2026) ve kaynaklar/.belgeler/ altındaki WPP 2024 Excel'i, bütçe ölçeği
Excel'i, barış gücü sıralama PDF'i (künye ve SHA-256: kaynaklar/KAYNAKLAR.md).
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import subprocess
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
RAW = KOK / "data/raw/temsil"
BELGELER = KOK / "kaynaklar/.belgeler"
GIRDI = KOK / "kaynaklar/temsil"
CIKTI = KOK / "data/processed/temsil.json"
WEB = KOK / "web/temsil_veri.js"
ERISIM = "2026-10-10"

GRUPLAR = {
    "AFR": {"tr": "Afrika Grubu", "en": "African Group", "dgacm": "African States"},
    "ASP": {"tr": "Asya-Pasifik Grubu", "en": "Asia-Pacific Group", "dgacm": "Asia-Pacific States"},
    "EEG": {"tr": "Doğu Avrupa Grubu", "en": "Eastern European Group", "dgacm": "Eastern European States"},
    "GRULAC": {"tr": "Latin Amerika ve Karayipler Grubu", "en": "Latin American and Caribbean Group", "dgacm": "Latin American and Caribbean States"},
    "WEOG": {"tr": "Batı Avrupa ve Diğerleri Grubu", "en": "Western European and Others Group", "dgacm": "Western European and other States"},
}
P5 = ["CHN", "FRA", "RUS", "GBR", "USA"]
# Seçilmiş koltuk dağılımı: A/RES/1991 (XVIII) A par. 3 (Afrika ve Asya 5, Doğu Avrupa 1, Latin Amerika 2, Batı Avrupa ve
# diğerleri 2); Afrika 3 / Asya-Pasifik 2 ayrımı mevcut uygulama (BM Güvenlik Konseyi üyeleri sayfası, 2026 dönemi).
SECILMIS_KOLTUK = {"AFR": 3, "ASP": 2, "EEG": 1, "GRULAC": 2, "WEOG": 2}

# 1963 üyeleri: bugünkü üyelerden kabul tarihi 1963 sonu ve öncesi olanlar + o tarihte üye olup bugün olmayanlar.
# Ardıl devletler: 1963 üyesinin o tarihteki ülkesini bugünkü ISO3 kodlarıyla toplar (WPP serileri bugünkü sınırlara göre).
ESKI_UYELER = {  # ad: (grup, [ISO3], not {tr, en})
    "Czechoslovakia": ("EEG", ["CZE", "SVK"], {"tr": "Çekoslovakya (üye 1945–1992): Çekya + Slovakya", "en": "Czechoslovakia (member 1945–1992): Czechia + Slovakia"}),
    "Yugoslavia": ("EEG", ["SVN", "HRV", "BIH", "SRB", "MNE", "MKD", "XKX"],
                   {"tr": "Yugoslavya (üye 1945–1992): Slovenya, Hırvatistan, Bosna-Hersek, Sırbistan, Karadağ, Kuzey Makedonya ve Kosova (WPP: 'Kosovo (under UNSC res. 1244)') serilerinin toplamı",
                    "en": "Yugoslavia (member 1945–1992): sum of the series for Slovenia, Croatia, Bosnia and Herzegovina, Serbia, Montenegro, North Macedonia and Kosovo (WPP: 'Kosovo (under UNSC res. 1244)')"}),
    "Zanzibar": ("AFR", [], {"tr": "Zanzibar (üye 16 Aralık 1963 – 26 Nisan 1964): nüfusu WPP'de Tanzanya serisinin içinde, Tanganyika satırında sayıldı",
                             "en": "Zanzibar (member 16 December 1963 – 26 April 1964): its population is within the WPP series for Tanzania, counted in the Tanganyika row"}),
}
ARDIL_1963 = {  # bugünkü üye ISO3 -> (1963'teki ülkesinin ISO3 bileşenleri, not {tr, en})
    "RUS": (["RUS", "ARM", "AZE", "GEO", "KAZ", "KGZ", "TJK", "TKM", "UZB", "EST", "LVA", "LTU", "MDA"],
            {"tr": "SSCB: Rusya Federasyonu ile 1963'te ayrı BM üyesi olmayan 12 cumhuriyetin toplamı; Ukrayna SSC ve Beyaz Rusya SSC ayrı üye olarak kendi satırlarında",
             "en": "USSR: sum of the Russian Federation and the 12 republics that were not separate UN members in 1963; the Ukrainian SSR and the Byelorussian SSR are separate members in their own rows"}),
    "TZA": (["TZA"], {"tr": "Tanganyika: WPP Tanzanya serisi (Zanzibar dâhil)", "en": "Tanganyika: WPP series for Tanzania (including Zanzibar)"}),
    "MYS": (["MYS", "SGP"], {"tr": "Malezya 1963 (16 Eylül'den itibaren Singapur dâhil): Malezya + Singapur", "en": "Malaysia 1963 (including Singapore from 16 September): Malaysia + Singapore"}),
    "PAK": (["PAK", "BGD"], {"tr": "Pakistan 1963: Pakistan + Bangladeş", "en": "Pakistan 1963: Pakistan + Bangladesh"}),
    "ETH": (["ETH", "ERI"], {"tr": "Etiyopya 1963: Etiyopya + Eritre", "en": "Ethiopia 1963: Ethiopia + Eritrea"}),
    "SDN": (["SDN", "SSD"], {"tr": "Sudan 1963: Sudan + Güney Sudan", "en": "Sudan 1963: Sudan + South Sudan"}),
    "CHN": (["CHN", "TWN"], {"tr": "Çin 1963 (koltuk Çin Cumhuriyeti'nde): WPP 'China' + 'China, Taiwan Province of China'", "en": "China 1963 (seat held by the Republic of China): WPP 'China' + 'China, Taiwan Province of China'"}),
    "YEM": (["YEM"], {"tr": "Yemen 1963 (Yemen Arap Cumhuriyeti): WPP serisi bütün Yemen'i kapsar, ayrılamadı", "en": "Yemen 1963 (Yemen Arab Republic): the WPP series covers all of Yemen and cannot be split"}),
    "EGY": (["EGY"], {"tr": "Birleşik Arap Cumhuriyeti 1963: yalnızca Mısır (Suriye 1961'de ayrıldı)", "en": "United Arab Republic 1963: Egypt only (Syria withdrew in 1961)"}),
}

AD_1963 = {"RUS": "Union of Soviet Socialist Republics", "CHN": "China (seat: Republic of China)", "EGY": "United Arab Republic",
           "TZA": "Tanganyika", "MYS": "Malaysia (Federation of Malaya until 16 September 1963)"}  # 1963'teki üye adı

IIT = {  # İİT sayfasındaki ad -> ISO3 (57 üye; Filistin BM üyesi değildir, paylara girmez)
    "Republic of AZERBAIJAN": "AZE", "Hashemite Kingdom of JORDAN": "JOR", "Islamic Republic of AFGHANISTAN": "AFG",
    "Republic of ALBANIA": "ALB", "State of The UNITED ARAB EMIRATES": "ARE", "Republic of INDONESIA": "IDN",
    "Republic of UZBEKISTAN": "UZB", "Republic of UGANDA": "UGA", "Islamic Republic of IRAN": "IRN",
    "Islamic Republic of PAKISTAN": "PAK", "Kingdom of BAHRAIN": "BHR", "BRUNEI-DARUSSALAM": "BRN",
    "People’s Republic of BANGLADESH": "BGD", "Republic of BENIN": "BEN", "Burkina Faso": "BFA",
    "Republic of TAJIKISTAN": "TJK", "Republic of Türkiye": "TUR", "Turkmenistan": "TKM", "Republic of CHAD": "TCD",
    "Republic of TOGO": "TGO", "Republic of TUNISIA": "TUN", "People’s Democratic Republic of ALGERIA": "DZA",
    "Republic of DJIBOUTI": "DJI", "Kingdom of SAUDI ARABIA": "SAU", "Republic of SENEGAL": "SEN",
    "Republic of The SUDAN": "SDN", "SYRIAN Arab Republic": "SYR", "Republic of SURINAME": "SUR",
    "Republic of SIERRA LEONE": "SLE", "Federal Republic of Somalia": "SOM", "Republic of IRAQ": "IRQ",
    "Sultanate of OMAN": "OMN", "Republic of GABON": "GAB", "Republic of The Gambia": "GMB",
    "Cooperative Republic of GUYANA": "GUY", "Republic of GUINEA": "GIN", "Republic of GUINEA-BISSAU": "GNB",
    "State of PALESTINE": "PSE", "Union of The COMOROS": "COM", "KYRGYZ Republic": "KGZ", "State of QATAR": "QAT",
    "Republic of KAZAKHSTAN": "KAZ", "Republic of CAMEROON": "CMR", "Republic of COTE D'IVOIRE": "CIV",
    "State of KUWAIT": "KWT", "Republic of LEBANON": "LBN", "Libya": "LBY", "Republic of MALDIVES": "MDV",
    "Republic of MALI": "MLI", "MALAYSIA": "MYS", "Arab Republic of EGYPT": "EGY", "Kingdom of MOROCCO": "MAR",
    "Islamic Republic of MAURITANIA": "MRT", "Republic of MOZAMBIQUE": "MOZ", "Republic of NIGER": "NER",
    "Federal Republic of NIGERIA": "NGA", "Republic of YEMEN": "YEM",
}

# Kaynaklardaki ad -> WPP adı (eşleşmeyenler için); anahtarlar normalize edilmiş hâliyle karşılaştırılır
TAKMA = {
    "china (the people's republic of)": "China", "cote d'ivoire": "Côte d'Ivoire", "gambia (republic of the)": "Gambia",
    "guinea bissau": "Guinea-Bissau", "netherlands (kingdom of the)": "Netherlands", "venezuela, bolivarian republic of": "Venezuela (Bolivarian Republic of)",
    "democratic people's republic of korea": "Dem. People's Republic of Korea", "micronesia (federated states of)": "Micronesia (Fed. States of)",
    "united kingdom of great britain and northern ireland": "United Kingdom", "turkiye": "Türkiye", "czech republic": "Czechia",
    "bolivia": "Bolivia (Plurinational State of)", "iran": "Iran (Islamic Republic of)", "tanzania": "United Republic of Tanzania",
    "bahamas (the)": "Bahamas", "naoero": "Nauru", "turkiye (formerly turkey)": "Türkiye", "czechia (formerly czech republic)": "Czechia", "eswatini (formerly swaziland)": "Eswatini",
    "north macedonia (formerly the former yugoslav republic of macedonia)": "North Macedonia", "cabo verde (formerly cape verde)": "Cabo Verde",
    "netherlands (kingdom of the) (formerly netherlands)": "Netherlands", "republic of korea": "Republic of Korea", "viet nam": "Viet Nam",
}


def norm(s: str) -> str:
    s = s.replace("’", "'").replace(" ", " ").replace("*", "")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def xlsx_satirlar(p: Path, sheet: str = "xl/worksheets/sheet1.xml") -> list[list[str]]:
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    z = zipfile.ZipFile(p)
    ss = ["".join(t.text or "" for t in si.iter("{%s}t" % ns["m"])) for si in ET.fromstring(z.read("xl/sharedStrings.xml"))]
    out = []
    for r in ET.fromstring(z.read(sheet)).iter("{%s}row" % ns["m"]):
        vals = []
        for c in r.findall("m:c", ns):
            v = c.find("m:v", ns)
            vals.append(ss[int(v.text)] if (c.get("t") == "s" and v is not None) else (v.text if v is not None else ""))
        out.append(vals)
    return out


def yaz(ad: str, alanlar: list[str], satirlar: list[dict]) -> None:
    GIRDI.mkdir(exist_ok=True)
    with (GIRDI / ad).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=alanlar)
        w.writeheader()
        w.writerows(satirlar)
    print(f"  {ad}: {len(satirlar)} satır")


# ---------------------------------------------------------------- girdi üretimi
def girdi_uret() -> None:
    # WPP: ülke/alan satırları, 1963 ve 2023
    W = xlsx_satirlar(BELGELER / "WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx")
    wpp = {}
    for r in W:
        if len(r) > 11 and r[8] in ("Country/Area", "World") and r[10] in ("1963", "2023"):
            # Dünya toplamı (Type "World", ISO3 boş) dünya payı için ayrıca tutulur
            wpp.setdefault(r[5] or "WORLD", {"iso3": r[5], "ad_wpp": r[2], "kod_m49": r[4]})[f"nufus_{r[10]}_bin"] = f"{float(r[11]):.3f}"
    yaz("nufus_wpp2024.csv", ["iso3", "kod_m49", "ad_wpp", "nufus_1963_bin", "nufus_2023_bin"], sorted(wpp.values(), key=lambda x: x["iso3"]))
    ad2iso = {norm(v["ad_wpp"]): k for k, v in wpp.items()}

    def iso(ad: str) -> str:
        n = norm(ad)
        if n in ad2iso:
            return ad2iso[n]
        if n in TAKMA:
            return ad2iso[norm(TAKMA[n])]
        raise KeyError(f"ISO3 eşleşmedi: {ad!r}")

    # BM üye devletleri (193) ve kabul tarihleri
    u = RAW.joinpath(f"uye_devletler_{ERISIM}.html").read_text(encoding="utf-8")
    kartlar = re.findall(r'<h2(?: class="mb-0")?>(.*?)</h2>\s*<div class="mb-1 text-muted">Date of Admission:\s*([0-9-]+)', u, re.S)
    uyeler = []
    for ad, tarih in kartlar:
        ad = html.unescape(re.sub(r"<[^>]+>", "", ad)).strip()
        g, a, y = tarih.split("-")
        uyeler.append({"iso3": iso(ad), "ad_bm": ad, "kabul_tarihi": f"{y}-{a}-{g}"})
    assert len(uyeler) == 193, len(uyeler)
    yaz("uye_devletler.csv", ["iso3", "ad_bm", "kabul_tarihi"], sorted(uyeler, key=lambda x: x["iso3"]))
    uye_iso = {x["iso3"] for x in uyeler}

    # DGACM bölgesel grupları
    g = RAW.joinpath(f"bolgesel_gruplar_{ERISIM}.html").read_text(encoding="utf-8")
    L = [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", g)).splitlines() if l.strip()]
    dg2kod = {v["dgacm"]: k for k, v in GRUPLAR.items()}
    listede = defaultdict(list)
    cur = None
    basla = next(i for i, l in enumerate(L) if l == "African States")
    for l in L[basla:]:
        if l in dg2kod:
            cur = dg2kod[l]
            continue
        if l.startswith("*Special"):
            break
        listede[cur].append((iso(l.rstrip("*").strip()), l.endswith("*")))
    satirlar = []
    for kod, liste in listede.items():
        for kod3, yildiz in liste:
            satirlar.append((kod3, kod, yildiz))
    gruplar = defaultdict(list)
    for kod3, kod, _ in satirlar:
        gruplar[kod3].append(kod)
    bg = []
    for x in uyeler:
        k = x["iso3"]
        listeler = gruplar.get(k, [])
        not_, not_en = "", ""
        if k == "TUR":
            secim = "WEOG"
            not_ = "DGACM: iki grupta (WEOG ve Asya-Pasifik) listelenir; seçimlerde yalnızca WEOG üyesi sayılır. Burada WEOG'da sayıldı."
            not_en = "DGACM: listed in two groups (WEOG and Asia-Pacific); for electoral purposes a member of WEOG only. Counted in WEOG here."
        elif k == "USA":
            secim = "WEOG"
            not_ = "DGACM: hiçbir bölgesel grubun üyesi değildir; WEOG toplantılarına gözlemci katılır ve seçimlerde WEOG üyesi sayılır. Burada WEOG'da sayıldı."
            not_en = "DGACM: not a member of any regional group; attends WEOG meetings as an observer and is considered a WEOG member for electoral purposes. Counted in WEOG here."
        elif k == "ISR":
            secim = "WEOG"
            not_ = "DGACM: Mayıs 2000'de geçici, 2004'te kalıcı olarak WEOG üyesi."
            not_en = "DGACM: WEOG member on a temporary basis from May 2000, permanent from 2004."
        else:
            assert len(listeler) == 1, (k, listeler)
            secim = listeler[0]
        bg.append({"iso3": k, "ad_bm": x["ad_bm"], "grup": secim, "dgacm_listeleri": ";".join(listeler), "not": not_, "not_en": not_en})
    assert len(satirlar) == 194 and {s[0] for s in satirlar} == uye_iso
    yaz("bolgesel_gruplar.csv", ["iso3", "ad_bm", "grup", "dgacm_listeleri", "not", "not_en"], sorted(bg, key=lambda x: (x["grup"], x["iso3"])))

    # İİT üyeleri (tarayıcıyla kaydedilen sayfa; adlar sayfadaki yazımıyla)
    o = RAW.joinpath(f"iit_uyeler_{ERISIM}.html").read_text(encoding="utf-8")
    metin = html.unescape(re.sub(r"<[^>]+>", "\n", o))
    bulunan = re.findall(r"\n\s*([^\n]+?)\s*\n\s*Member since\s*\n?\s*(\d{4})", metin)
    iit = []
    for ad, yil in bulunan:
        kod3 = IIT[ad]
        iit.append({"iso3": kod3, "ad_iit": ad, "uyelik_yili": yil, "bm_uyesi": "evet" if kod3 in uye_iso else "hayir"})
    assert len(iit) == 57 and len({x["iso3"] for x in iit}) == 57, len(iit)
    yaz("iit_uyeleri.csv", ["iso3", "ad_iit", "uyelik_yili", "bm_uyesi"], sorted(iit, key=lambda x: x["iso3"]))

    # Bütçe ölçeği 2025–2027 (Excel'in son sütunu; başlık satırlarında 2025/2026/2027 alt alta)
    S = xlsx_satirlar(BELGELER / "Scale_of_Assessments_for_RB_1946-2027.xlsx")
    ust = [r for r in S[:3]]
    assert ust[0][-1] == "2025" and ust[1][-1] == "2026" and len(ust[0]) == len(ust[1]), ust[0][-2:]
    bas = next(i for i, r in enumerate(S) if r and r[0] == "Member State")
    olcek = []
    for r in S[bas + 2:]:
        ad = (r[0] if r else "").strip()
        if ad == "Total":
            assert abs(float(r[-1]) - 100) < 1e-6
            break
        if not ad:
            continue
        try:
            yuzde = float(r[-1])
        except ValueError:
            continue  # eski üyeler (ör. Çekoslovakya, SSCB): 2025–2027 sütunu "-"
        kod3 = iso(re.sub(r"\s+[a-z]/$", "", re.sub(r"\s*\(formerly[^)]*\)", "", ad)))  # dipnot imleri (ör. "Germany e/")
        olcek.append({"iso3": kod3, "ad_olcek": ad, "yuzde": f"{yuzde:.3f}"})
    assert len(olcek) == 193, len(olcek)
    yaz("butce_olcegi_2025_2027.csv", ["iso3", "ad_olcek", "yuzde"], sorted(olcek, key=lambda x: x["iso3"]))

    # Barış gücü: ülke sıralaması PDF'i (pdftotext -layout); satır sonu taşan adlar birleştirilir
    pdf = BELGELER / "02_country_ranking_95_february_2026.pdf"
    metin = subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", str(pdf), "-"], capture_output=True, text=True, encoding="utf-8", check=True).stdout
    assert "As of: 28/02/2026" in metin
    pk = []
    for l in metin.splitlines():
        m = re.match(r"^\s*(\d+)\s+(\d+)\s+(.+?)\s{2,}(\d+)\s+(\d+)\s+(\d+)\s+28/02/2026\s*$", l)
        if m:
            pk.append({"sira": int(m[2]), "ad_rapor": m[3].strip(), "erkek": int(m[4]), "kadin": int(m[5]), "toplam": int(m[6])})
            continue
        m = re.match(r"^\s*(\d+)\s+([A-Za-z][^\d]+?)\s{2,}(\d+)\s+(\d+)\s+(\d+)\s+28/02/2026\s*$", l)
        if m and pk:
            pk[-1]["ad_rapor"] += " " + m[2].strip()
    genel = re.search(r"Grand Total\s+(\d+)\s+(\d+)\s+(\d+)", metin)
    assert genel and sum(x["toplam"] for x in pk) == int(genel[3]), (genel and genel[3], sum(x["toplam"] for x in pk))
    for x in pk:
        x["iso3"] = iso(x["ad_rapor"])
    yaz("baris_gucu_2026-02.csv", ["iso3", "ad_rapor", "sira", "erkek", "kadin", "toplam"], sorted(pk, key=lambda x: x["sira"]))

    # Güvenlik Konseyi üyeleri (mevcut dönem)
    s = RAW.joinpath(f"gk_uyeler_{ERISIM}.html").read_text(encoding="utf-8")
    L = [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", s)).splitlines() if l.strip()]
    i = L.index("Five permanent members:")
    j = next(k for k, l in enumerate(L) if l.startswith("Non-Council Member States"))
    gk = [{"iso3": k, "ad_bm": next(x["ad_bm"] for x in uyeler if x["iso3"] == k), "tur": "daimi", "donem_sonu": ""} for k in P5]
    parca = " ".join(L[i + 1:j])
    for ad, yil in re.findall(r"([A-Z][A-Za-z' ]+?)\s*\((\d{4})\)", parca):
        gk.append({"iso3": iso(ad.strip()), "ad_bm": ad.strip(), "tur": "secilmis", "donem_sonu": yil})
    assert len(gk) == 15 and len({x["iso3"] for x in gk}) == 15, gk
    yaz("gk_uyeleri_2026.csv", ["iso3", "ad_bm", "tur", "donem_sonu"], gk)


# ---------------------------------------------------------------- hesap
def oku(ad: str) -> list[dict]:
    with (GIRDI / ad).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def pay(a: float, b: float) -> float:
    return round(a / b, 6) if b else 0.0


def hesapla() -> dict:
    nufus = {r["iso3"]: r for r in oku("nufus_wpp2024.csv") if r["iso3"]}
    dunya = next(r for r in oku("nufus_wpp2024.csv") if r["ad_wpp"] == "World")
    dunya_2023, dunya_1963 = float(dunya["nufus_2023_bin"]), float(dunya["nufus_1963_bin"])
    uyeler = oku("uye_devletler.csv")
    grup = {r["iso3"]: r for r in oku("bolgesel_gruplar.csv")}
    iit = {r["iso3"]: r for r in oku("iit_uyeleri.csv")}
    olcek = {r["iso3"]: float(r["yuzde"]) for r in oku("butce_olcegi_2025_2027.csv")}
    pk = {r["iso3"]: int(r["toplam"]) for r in oku("baris_gucu_2026-02.csv")}
    gk = {r["iso3"]: r for r in oku("gk_uyeleri_2026.csv")}
    assert len(uyeler) == 193 and set(grup) == {u["iso3"] for u in uyeler}

    # Üye satırları (2023)
    U = []
    for u in uyeler:
        k = u["iso3"]
        U.append({"iso3": k, "ad": u["ad_bm"], "kabul_tarihi": u["kabul_tarihi"], "grup": grup[k]["grup"],
                  "iit": k in iit, "p5": k in P5, "nufus_2023": float(nufus[k]["nufus_2023_bin"]),
                  "butce_yuzde": olcek[k], "personel": pk.get(k, 0),
                  "gk": {"tur": gk[k]["tur"], "donem_sonu": gk[k]["donem_sonu"] or None} if k in gk else None,
                  "not": {"tr": grup[k]["not"], "en": grup[k]["not_en"]} if grup[k]["not"] else None})
    toplam_nufus = sum(x["nufus_2023"] for x in U)
    toplam_butce = sum(x["butce_yuzde"] for x in U)
    toplam_pk = sum(x["personel"] for x in U)

    # 1963 üyeleri: kabul tarihi ≤ 1963-12-31 olan bugünkü üyeler (ardıl toplamlarıyla) + eski üyeler
    U63 = []
    for u in U:
        if u["kabul_tarihi"] <= "1963-12-31":
            parcalar, not_ = ARDIL_1963.get(u["iso3"], ([u["iso3"]], None))
            U63.append({"uye_1963": AD_1963.get(u["iso3"], u["ad"]), "iso3": u["iso3"], "grup": u["grup"], "bilesenler": parcalar,
                        "nufus_1963": sum(float(nufus[p]["nufus_1963_bin"]) for p in parcalar), "iit_bugun": u["iit"], "p5": u["p5"], "not": not_})
    for ad, (g, parcalar, not_) in ESKI_UYELER.items():
        U63.append({"uye_1963": ad, "iso3": None, "grup": g, "bilesenler": parcalar,
                    "nufus_1963": sum(float(nufus[p]["nufus_1963_bin"]) for p in parcalar), "iit_bugun": False, "p5": False, "not": not_})
    toplam_nufus_63 = sum(x["nufus_1963"] for x in U63)
    kullanilan = [p for x in U63 for p in x["bilesenler"]]
    assert len(kullanilan) == len(set(kullanilan)), "1963 bileşenlerinde çift sayım"

    def kume(ad_tr, ad_en, kod, secili, secili63, daimi, secilmis, notlar):
        n23 = sum(x["nufus_2023"] for x in secili)
        n63 = sum(x["nufus_1963"] for x in secili63)
        b = sum(x["butce_yuzde"] for x in secili)
        p = sum(x["personel"] for x in secili)
        paylar = {"nufus_2023": pay(n23, toplam_nufus), "nufus_1963": pay(n63, toplam_nufus_63), "uye": pay(len(secili), len(U)),
                  "nufus_2023_dunya": pay(n23, dunya_2023), "nufus_1963_dunya": pay(n63, dunya_1963),  # WPP dünya toplamı içinde
                  "butce": pay(b, toplam_butce), "personel": pay(p, toplam_pk)}
        toplam_koltuk_payi = pay(daimi + secilmis, 15)
        return {"kod": kod, "ad": {"tr": ad_tr, "en": ad_en}, "uyeler": sorted(x["iso3"] for x in secili),
                "uye_sayisi": len(secili), "uye_sayisi_1963": len(secili63),
                "nufus_2023_bin": round(n23, 3), "nufus_1963_bin": round(n63, 3), "butce_yuzde": round(b, 3), "personel": p,
                "paylar": paylar,
                "koltuk": {"daimi": daimi, "secilmis": secilmis, "toplam": daimi + secilmis,
                           "daimi_payi": pay(daimi, 5), "toplam_payi": toplam_koltuk_payi},
                "oranlar": {g: (round(toplam_koltuk_payi / paylar[g], 3) if paylar[g] else None) for g in ("nufus_2023", "uye", "butce", "personel")},
                "notlar": notlar}

    gruplar = []
    for kod, adlar in GRUPLAR.items():
        secili = [x for x in U if x["grup"] == kod]
        secili63 = [x for x in U63 if x["grup"] == kod]
        daimi = sum(1 for x in secili if x["p5"])
        secilmis = sum(1 for x in secili if x["gk"] and x["gk"]["tur"] == "secilmis")
        assert secilmis == SECILMIS_KOLTUK[kod], (kod, secilmis)
        notlar = [x["not"] for x in secili if x["not"]] + [x["not"] for x in secili63 if x["not"]]  # her biri {tr, en}
        gruplar.append(kume(adlar["tr"], adlar["en"], kod, secili, secili63, daimi, secilmis, notlar))
    p5 = [x for x in U if x["p5"]]
    p5_63 = [x for x in U63 if x["p5"]]
    iit_u = [x for x in U if x["iit"]]
    iit_63 = [x for x in U63 if x["iit_bugun"]]
    kumeler = [
        kume("Beş daimî üye", "Five permanent members", "P5", p5, p5_63, 5, 0,
             [{"tr": "1963 nüfusu: Çin koltuğu Çin Cumhuriyeti'ndeydi, nüfus WPP 'China' + 'China, Taiwan Province of China' serilerinin toplamıdır; SSCB 13 cumhuriyetin toplamıdır (Ukrayna ve Beyaz Rusya ayrı üye).",
               "en": "1963 population: the China seat was held by the Republic of China; the population is the sum of the WPP series 'China' and 'China, Taiwan Province of China'; the USSR is the sum of 13 republics (Ukraine and Byelorussia separate members)."}]),
        kume("İslam İşbirliği Teşkilatı üyeleri", "Organisation of Islamic Cooperation members", "IIT", iit_u, iit_63, 0,
             sum(1 for x in iit_u if x["gk"] and x["gk"]["tur"] == "secilmis"),
             [{"tr": "İİT'nin 57 üyesinden Filistin BM üyesi değildir; paylara 56 üye girer.", "en": "Of the 57 OIC members, Palestine is not a UN Member State; 56 members enter the shares."},
              {"tr": "1963: İİT 1969'da kuruldu; 1963 değeri bugünkü üyelerden o tarihte BM üyesi olanların 1963 sınırlarıyla toplamıdır (Pakistan Bangladeş'i, Malezya Singapur'u, Sudan Güney Sudan'ı kapsar).",
               "en": "1963: the OIC was founded in 1969; the 1963 value is the sum of today's members that were UN members at that time, with their 1963 borders (Pakistan includes Bangladesh, Malaysia includes Singapore, Sudan includes South Sudan)."}]),
    ]
    return {
        "meta": {
            "uretim": date.today().isoformat(), "erisim_tarihi": ERISIM, "uye_sayisi": len(U), "uye_sayisi_1963": len(U63),
            "nufus_yillari": [1963, 2023], "olcek_donemi": "2025–2027", "personel_tarihi": "2026-02-28", "gk_donemi": "2026",
            "toplamlar": {"nufus_2023_bin": round(toplam_nufus, 3), "nufus_1963_bin": round(toplam_nufus_63, 3),
                          "dunya_nufus_2023_bin": dunya_2023, "dunya_nufus_1963_bin": dunya_1963, "butce_yuzde": round(toplam_butce, 3),
                          "personel": toplam_pk, "koltuk": 15, "daimi": 5},
            "secilmis_koltuk_dagilimi": SECILMIS_KOLTUK,
            "girdi_sha256": {ad: sha(GIRDI / ad) for ad in sorted(p.name for p in GIRDI.glob("*.csv"))},
        },
        "gruplar": gruplar, "kumeler": kumeler,
        "uyeler": U,
        "uyeler_1963": [{k: v for k, v in x.items()} for x in U63],
    }


def main() -> int:
    if "--girdi" in sys.argv:
        print("Girdi CSV'leri:")
        girdi_uret()
    V = hesapla()
    CIKTI.write_text(json.dumps(V, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    WEB.write_text("// scripts/09_temsil.py üretir; elle düzenlenmez.\nwindow.TEMSIL_VERISI = " + json.dumps(V, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"{CIKTI.relative_to(KOK)} ve {WEB.relative_to(KOK)} yazıldı: {V['meta']['uye_sayisi']} üye, 1963'te {V['meta']['uye_sayisi_1963']}")
    for g in V["gruplar"] + V["kumeler"]:
        p = g["paylar"]
        print(f"  {g['kod']:7} üye {g['uye_sayisi']:3} nüfus23 {p['nufus_2023']:.3f} nüfus63 {p['nufus_1963']:.3f} üye {p['uye']:.3f} bütçe {p['butce']:.3f} personel {p['personel']:.3f} koltuk {g['koltuk']['toplam_payi']:.3f} (daimî {g['koltuk']['daimi']}, seçilmiş {g['koltuk']['secilmis']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
