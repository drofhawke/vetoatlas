"""
Adım 13: Temsil haritası (web/harita_veri.js).

    python scripts/13_harita.py --indir   # Natural Earth dosyalarını kaynaklar/.belgeler/natural_earth/ altına indirir
    python scripts/13_harita.py           # web/harita_veri.js üretir

Kaynak: Natural Earth 1:50m Cultural Vectors, sürüm 5.1.2 (kamu malı): "Admin 0 – Countries" ve "Admin 0 – Breakaway and
Disputed Areas", GeoJSON (github.com/nvkelso/natural-earth-vector, v5.1.2 etiketi). Dosyalar depoya girmez; SHA-256
değerleri aşağıda ve kaynaklar/KAYNAKLAR.md'de.

Ülkeler BM üyesinin ISO3 koduyla eşlenir (ADM0_A3, yoksa ISO_A3). Üye olmayan ülke ve alanlar, bağımlı topraklar dahil,
"üye değil" olarak tek parça çizilir. Natural Earth'ün varsayılan çizimi fiilî durumdur; tartışmalı alanların ataması
kaynaklar/temsil/harita_kurallari.csv'de, gerekçesiyle. İzdüşüm Equal Earth (Šavrič, Patterson ve Jenny, 2018); Antarktika
çizilmez. Çizgiler 1000 birim genişlikte Douglas–Peucker ile sadeleşir, koordinatlar 0,1 birime yuvarlanır. Alanı çok küçük
üyeler (ada devletleri vb.) ayrıca nokta olarak işaretlenir (Natural Earth etiket noktası). Ülke adları: Türkçe
kaynaklar/temsil/ulke_adlari.csv (Türkçe ve İngilizce kısa adlar; Unicode CLDR 48 adlarından, site adlandırmasına
göre düzeltilmiş).
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
KLASOR = KOK / "kaynaklar/.belgeler/natural_earth"
GIRDI = KOK / "kaynaklar/temsil"
WEB = KOK / "web/harita_veri.js"
SURUM = "5.1.2"
ADRES = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v{}/geojson/{}"
DOSYALAR = {
    "ne_50m_admin_0_countries.geojson": "3e458fc036ad0a66411f2c1e6cac49c5d7bfb81cb1123bc513b22511a2b7fdeb",
    "ne_50m_admin_0_breakaway_disputed_areas.geojson": "e91f0f9518b24355ceec6668f4df874d6f39db7d0bc9ec22d9b14429bfb6be01",
}
GENISLIK = 1000.0
TOLERANS = 0.3     # birim (1000 birim genişlikte)
EN_KUCUK_HALKA = 0.4   # birim²; daha küçük adalar ve delikler düşer (ülkenin en büyük parçası hariç)
NOKTA_ESIGI = 6.0      # birim²; toplam alanı bundan küçük üye nokta olarak da işaretlenir


def indir() -> None:
    KLASOR.mkdir(parents=True, exist_ok=True)
    for ad, ozet in DOSYALAR.items():
        hedef = KLASOR / ad
        if not hedef.exists():
            with urllib.request.urlopen(ADRES.format(SURUM, ad), timeout=120) as y:
                hedef.write_bytes(y.read())
        gercek = hashlib.sha256(hedef.read_bytes()).hexdigest()
        if gercek != ozet:
            sys.exit(f"{ad}: SHA-256 beklenenden farklı ({gercek})")
        print(f"{ad}: {hedef.stat().st_size} bayt, SHA-256 tamam")


def oku(ad: str) -> list[dict]:
    yol = KLASOR / ad
    if not yol.exists():
        sys.exit(f"{yol} yok; önce: python scripts/13_harita.py --indir")
    veri = yol.read_bytes()
    if hashlib.sha256(veri).hexdigest() != DOSYALAR[ad]:
        sys.exit(f"{ad}: SHA-256 beklenenden farklı")
    return json.loads(veri.decode("utf-8"))["features"]


# Equal Earth: x = 2√3·λ·cos θ / (3·(9A4θ⁸ + 7A3θ⁶ + 3A2θ² + A1)), y = A4θ⁹ + A3θ⁷ + A2θ³ + A1θ, sin θ = (√3/2)·sin φ
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
M = math.sqrt(3) / 2
OLCEK = GENISLIK / (2 * 2 * math.sqrt(3) * math.pi / (3 * A1))


def izdusum(boylam: float, enlem: float) -> tuple[float, float]:
    lam, phi = math.radians(boylam), math.radians(enlem)
    t = math.asin(M * math.sin(phi))
    t2 = t * t
    t6 = t2 * t2 * t2
    x = 2 * math.sqrt(3) * lam * math.cos(t) / (3 * (9 * A4 * t6 * t2 + 7 * A3 * t6 + 3 * A2 * t2 + A1))
    y = A4 * t6 * t2 * t + A3 * t6 * t + A2 * t2 * t + A1 * t
    return GENISLIK / 2 + OLCEK * x, -OLCEK * y


def sadelestir(nk: list[tuple[float, float]], tol: float) -> list[tuple[float, float]]:
    """Douglas–Peucker (kapalı halka: ilk ve son nokta sabit)."""
    if len(nk) < 4:
        return nk
    tut = [False] * len(nk)
    tut[0] = tut[-1] = True
    yigin = [(0, len(nk) - 1)]
    while yigin:
        a, b = yigin.pop()
        (x1, y1), (x2, y2) = nk[a], nk[b]
        dx, dy = x2 - x1, y2 - y1
        uz = math.hypot(dx, dy)
        en, ei = 0.0, -1
        for i in range(a + 1, b):
            x, y = nk[i]
            d = abs(dy * (x - x1) - dx * (y - y1)) / uz if uz else math.hypot(x - x1, y - y1)
            if d > en:
                en, ei = d, i
        if en > tol:
            tut[ei] = True
            yigin += [(a, ei), (ei, b)]
    return [p for p, k in zip(nk, tut) if k]


def alan(h: list[tuple[float, float]]) -> float:
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(h, h[1:] + h[:1]))) / 2


def cokgenler(g: dict) -> list[list[list[tuple[float, float]]]]:
    p = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    return [[[izdusum(*n[:2]) for n in halka] for halka in cokgen] for cokgen in p]


def sayi(n: int) -> str:
    """Onda bir birimlik tam sayı -> en kısa yazım (0.5 -> .5, -0.5 -> -.5, 3.0 -> 3)."""
    s = f"{n / 10:.1f}".rstrip("0").rstrip(".")
    return s.replace("0.", ".", 1) if s.startswith("0.") else s.replace("-0.", "-.", 1) if s.startswith("-0.") else (s if s != "-0" else "0")


def yol(halkalar: list[list[tuple[float, float]]]) -> str:
    parca = []
    for h in halkalar:
        n = [(round(x * 10), round(y * 10)) for x, y in h]
        n = [p for i, p in enumerate(n) if i == 0 or p != n[i - 1]]
        if n[0] == n[-1]:
            n = n[:-1]
        if len(n) < 3:
            continue
        sayilar = []
        for (x0, y0), (x1, y1) in zip(n, n[1:]):
            sayilar += [x1 - x0, y1 - y0]
        metin = ""
        for s in map(sayi, sayilar):  # eksi işareti ayraç sayılır; öteki sayılar arasında bir boşluk
            metin += s if not metin or s.startswith("-") else " " + s
        parca.append(f"M{sayi(n[0][0])} {sayi(n[0][1])}l{metin}z")
    return "".join(parca)


def isle(cg: list[list[list[tuple[float, float]]]]) -> tuple[list[list[tuple[float, float]]], float, list[float]]:
    """Sadeleştirir, küçük adaları ve delikleri düşürür (en büyük parça kalır); halkalar, toplam alan ve en büyük parçanın kutusu
    (x0, y0, x1, y1; ana toprak: Fransa için Avrupa'daki Fransa, ABD için kıta ABD'si) döner."""
    parcalar = []
    for cokgen in cg:
        dis = sadelestir(cokgen[0], TOLERANS)
        delikler = [d for d in (sadelestir(h, TOLERANS) for h in cokgen[1:]) if alan(d) >= EN_KUCUK_HALKA]
        parcalar.append((alan(cokgen[0]), dis, delikler))
    en_buyuk = max(parcalar, key=lambda p: p[0])[0]
    halkalar, toplam = [], 0.0
    for a, dis, delikler in parcalar:
        toplam += a
        if a >= EN_KUCUK_HALKA or a == en_buyuk:
            halkalar += [dis] + delikler
    ana = max(zip(parcalar, cg), key=lambda pc: pc[0][0])[1][0]
    kutu = [round(min(x for x, _ in ana), 1), round(min(y for _, y in ana), 1), round(max(x for x, _ in ana), 1), round(max(y for _, y in ana), 1)]
    return halkalar, toplam, kutu


def main() -> None:
    if "--indir" in sys.argv:
        indir()
        return
    ulkeler = oku("ne_50m_admin_0_countries.geojson")
    ayrik = {f["properties"]["BRK_A3"]: f for f in oku("ne_50m_admin_0_breakaway_disputed_areas.geojson")}
    T = json.loads((KOK / "data/processed/temsil.json").read_text(encoding="utf-8"))
    uyeler = {u["iso3"]: u for u in T["uyeler"]}
    adlar = {r["iso3"]: r for r in csv.DictReader(open(GIRDI / "ulke_adlari.csv", encoding="utf-8"))}
    assert set(adlar) == set(uyeler), set(adlar) ^ set(uyeler)
    kurallar = list(csv.DictReader(open(GIRDI / "harita_kurallari.csv", encoding="utf-8")))
    ulke_kurali = {k["ne_kodu"]: k["atama"] for k in kurallar if k["katman"] == "ulke"}
    # BM üyesi olmayan alanların adları (BM'nin kullandığı biçim: WPP 2024, yoksa M49; Türkiye'nin tanıdığı devletler Dışişleri
    # Bakanlığının kullandığı adla) ve
    # durumu (üye değil, gözlemci devlet, kendi kendini yönetmeyen toprak; "sessiz": adı gösterilmez); her çizilen alan listede
    olmayan = {r["ne_kodu"]: r for r in csv.DictReader(open(GIRDI / "uye_olmayan_alanlar.csv", encoding="utf-8"))}
    assert all(r["durum"] in ("uye_degil", "gozlemci", "kyt", "sessiz") for r in olmayan.values())
    alanlar = []
    # Nüfus (WPP 2024, 2023, bin): her alan ve bölge kendi serisiyle; Natural Earth kodu WPP'ninkinden farklı olabilir
    wpp = {r["iso3"]: r for r in csv.DictReader(open(GIRDI / "nufus_wpp2024.csv", encoding="utf-8")) if r["iso3"]}
    WPP_KODU = {"SAH": "ESH", "B19": "ESH", "PSX": "PSE", "KOS": "XKX"}

    kktc = list(csv.DictReader(open(GIRDI / "kktc_nufus.csv", encoding="utf-8")))[0]

    def nufus(kod: str) -> float | None:
        if kod == "CYN":  # KKTC İstatistik Kurumu, 2022 yıl sonu projeksiyonu (Kıbrıs'tan çıkarılan sayı)
            return round(float(kktc["nufus_bin"]), 3)
        r = wpp.get(WPP_KODU.get(kod, kod))
        return round(float(r["nufus_2023_bin"]), 3) if r and r["nufus_2023_bin"] else None

    # BM istatistiklerinde ayrı sayılan, üyenin parçası olan bölgeler (WPP 2024 notları: Çin verisi Hong Kong ve Makao'yu, Fransa
    # verisi deniz aşırı bölgelerini, Hollanda verisi Karayip Hollandası'nı kapsamaz). Haritada üyenin renginde, kendi adı ve
    # nüfusuyla; üyenin nüfusuna eklenmez. Natural Earth'te ayrı alan olanlar ("ulke") ya da üyenin çokgenlerinden konumla ayrılanlar
    # ("parca", ağırlık merkezi kutunun içinde)
    bolge_satir = list(csv.DictReader(open(GIRDI / "ayri_sayilan_bolgeler.csv", encoding="utf-8")))
    assert all(r["uye"] in uyeler and r["kod"] in wpp and wpp[r["kod"]]["ad_wpp"] == r["ad_en"] for r in bolge_satir)
    bolge_ulke = {r["ne_kodu"]: r for r in bolge_satir if r["ne_kaynagi"] == "ulke"}
    bolge_parca: dict[str, list] = {}
    for r in bolge_satir:
        if r["ne_kaynagi"] == "parca":
            bolge_parca.setdefault(r["ne_kodu"], []).append(r)
    bolgeler = []

    def bolge(r: dict, cg: list) -> None:
        halkalar, _, kutu = isle(cg)
        bolgeler.append({"k": r["kod"], "uye": r["uye"], "tr": r["ad_tr"], "en": r["ad_en"], "n": nufus(r["kod"]), "b": kutu, "d": yol(halkalar)})

    def ayir(f: dict) -> dict:
        """Üyenin çokgenlerinden ayrı sayılan bölgeleri ayırır; kalan geometri döner."""
        g = f["geometry"]
        P = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        satir = bolge_parca[f["properties"]["ADM0_A3"]]
        ayri, kalan = {r["kod"]: [] for r in satir}, []
        for cokgen in P:
            boy = sum(c[0] for c in cokgen[0]) / len(cokgen[0])
            en = sum(c[1] for c in cokgen[0]) / len(cokgen[0])
            r = next((r for r in satir if float(r["boylam_en_az"]) <= boy <= float(r["boylam_en_cok"])
                      and float(r["enlem_en_az"]) <= en <= float(r["enlem_en_cok"])), None)
            (ayri[r["kod"]] if r else kalan).append(cokgen)
        for r in satir:
            assert ayri[r["kod"]], r["kod"]
            bolge(r, cokgenler({"type": "MultiPolygon", "coordinates": ayri[r["kod"]]}))
        return {"type": "MultiPolygon", "coordinates": kalan}

    def alan(kod: str, halkalar: list, kutu: list[float], ust: bool) -> None:
        r = olmayan[kod]
        a = {"k": kod, "tr": r["ad_tr"], "en": r["ad_en"], "durum": r["durum"], "b": kutu, "d": yol(halkalar)}
        if nufus(kod) is not None and r["durum"] != "sessiz":
            a["n"] = nufus(kod)
        if ust:
            a["ust"] = True  # ayrık alan katmanı: üyelerin üstüne çizilir
        alanlar.append(a)

    uye_halka: dict[str, list] = {k: [] for k in uyeler}
    uye_alan: dict[str, float] = {k: 0.0 for k in uyeler}
    etiket: dict[str, tuple[float, float]] = {}
    ana_kutu: dict[str, list[float]] = {}
    degil: list = []
    for f in ulkeler:
        p = f["properties"]
        if p["ADM0_A3"] == "ATA":
            continue
        if p["ADM0_A3"] in bolge_ulke:
            bolge(bolge_ulke[p["ADM0_A3"]], cokgenler(f["geometry"]))
            continue
        kod = ulke_kurali.get(p["ADM0_A3"])
        if kod is None:
            kod = next((k for k in (p["ADM0_A3"], p["ISO_A3"]) if k in uyeler), "-")
        geometri = ayir(f) if p["ADM0_A3"] in bolge_parca else f["geometry"]
        halkalar, a, kutu = isle(cokgenler(geometri))
        if kod == "-":
            degil += halkalar
            alan(p["ADM0_A3"], halkalar, kutu, False)
            continue
        uye_halka[kod] += halkalar
        uye_alan[kod] += a
        if kod in (p["ADM0_A3"], p["ISO_A3"]) and p.get("LABEL_X") is not None:
            etiket[kod] = izdusum(p["LABEL_X"], p["LABEL_Y"])
            ana_kutu[kod] = kutu
    eksik = [k for k, h in uye_halka.items() if not h]
    assert not eksik, eksik
    assert set(etiket) == set(uyeler) == set(ana_kutu), set(uyeler) - set(etiket)
    katmanlar = []
    for k in kurallar:
        if k["katman"] != "ayrik":
            continue
        halkalar, _, kutu = isle(cokgenler(ayrik[k["ne_kodu"]]["geometry"]))
        if k["atama"] == "-":
            alan(k["ne_kodu"], halkalar, kutu, True)
        else:
            katmanlar.append({"k": k["atama"], "d": yol(halkalar)})
    assert {a["k"] for a in alanlar} == set(olmayan), set(olmayan) ^ {a["k"] for a in alanlar}
    assert {b["k"] for b in bolgeler} == {r["kod"] for r in bolge_satir}

    tum = [n for h in list(uye_halka.values()) + [degil] for halka in h for n in halka]
    ust, alt = min(y for _, y in tum) - 4, max(y for _, y in tum) + 4
    yollar = {k: yol(uye_halka[k]) for k in uyeler}
    # Çok küçük üyeler nokta olarak da işaretlenir; çizgisi 0,1 birimde kaybolan üye yalnızca noktadır
    noktalar = [{"k": k, "x": round(etiket[k][0], 1), "y": round(etiket[k][1], 1)}
                for k in sorted(uyeler) if uye_alan[k] < NOKTA_ESIGI or not yollar[k]]
    V = {
        "kaynak": f"Natural Earth {SURUM} (1:50m)",
        "kutu": [0, round(ust, 1), GENISLIK, round(alt - ust, 1)],
        # m: etiket noktası (Natural Earth; nüfus balonu ve arama), b: ana toprağın kutusu (aramada yakınlaşma)
        "uyeler": [{"k": k, "tr": adlar[k]["ad_tr"], "en": adlar[k]["ad_en"], "m": [round(etiket[k][0], 1), round(etiket[k][1], 1)],
                    "b": ana_kutu[k], "d": yollar[k]} for k in sorted(uyeler)],
        "katmanlar": katmanlar,
        # Ayrı sayılan bölgeler: uye rengiyle çizilir, adı ve nüfusu (n, bin) kendi
        "bolgeler": sorted(bolgeler, key=lambda b: b["k"]),
        # BM üyesi olmayan alanlar: adı ve durumu; d boşsa bu ölçekte çizilmez (aramada yine bulunur)
        "alanlar": sorted(alanlar, key=lambda a: a["k"]),
        "noktalar": noktalar,
    }
    WEB.write_text("// scripts/13_harita.py üretir; elle düzenlenmez.\nwindow.HARITA_VERISI = "
                   + json.dumps(V, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    print(f"{WEB.name}: {WEB.stat().st_size} bayt; {len(noktalar)} nokta; kutu {V['kutu']}")


if __name__ == "__main__":
    main()
