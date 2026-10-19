"""
Temsil endeksi (scripts/09_temsil.py, data/processed/temsil.json, web/temsil.html): paylar 1'e toplanır, 193 üye
eksiksiz ve her üye tek grupta, Türkiye ve ABD WEOG'da sayılıp notlanır, P5 nüfus payı elle hesaplanmış değerle tutar.
"""
import csv
import json
import re

from conftest import KOK

V = json.loads((KOK / "data/processed/temsil.json").read_text(encoding="utf-8"))
G = {g["kod"]: g for g in V["gruplar"]}
K = {k["kod"]: k for k in V["kumeler"]}
GIRDI = KOK / "kaynaklar/temsil"


def oku(ad):
    with (GIRDI / ad).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_paylar_bire_toplanir():
    for g in ("nufus_2023", "nufus_1963", "uye", "butce", "personel"):
        assert abs(sum(x["paylar"][g] for x in V["gruplar"]) - 1) < 1e-5, g
    assert sum(x["koltuk"]["toplam"] for x in V["gruplar"]) == 15 and sum(x["koltuk"]["daimi"] for x in V["gruplar"]) == 5
    assert {x["kod"]: x["koltuk"]["secilmis"] for x in V["gruplar"]} == {"AFR": 3, "ASP": 2, "EEG": 1, "GRULAC": 2, "WEOG": 2}
    assert V["meta"]["toplamlar"]["koltuk"] == 15 and abs(V["meta"]["toplamlar"]["butce_yuzde"] - 100) < 1e-6


def test_193_uye_eksiksiz_ve_tek_grupta():
    uyeler = V["uyeler"]
    assert len(uyeler) == 193 == V["meta"]["uye_sayisi"] and len({u["iso3"] for u in uyeler}) == 193
    listeler = [set(g["uyeler"]) for g in V["gruplar"]]
    assert sum(len(l) for l in listeler) == 193 and set().union(*listeler) == {u["iso3"] for u in uyeler}
    assert {g["kod"]: g["uye_sayisi"] for g in V["gruplar"]} == {"AFR": 54, "ASP": 54, "EEG": 23, "GRULAC": 33, "WEOG": 29}
    # Girdi CSV'leri aynı kümeyi taşır
    assert {r["iso3"] for r in oku("uye_devletler.csv")} == {r["iso3"] for r in oku("bolgesel_gruplar.csv")} == {r["iso3"] for r in oku("butce_olcegi_2025_2027.csv")}
    assert all(u["gk"] is None or u["gk"]["tur"] in ("daimi", "secilmis") for u in uyeler)
    assert sum(1 for u in uyeler if u["gk"]) == 15 and sum(1 for u in uyeler if u["p5"]) == 5


def test_turkiye_ve_abd_kurali():
    bg = {r["iso3"]: r for r in oku("bolgesel_gruplar.csv")}
    assert bg["TUR"]["grup"] == "WEOG" and set(bg["TUR"]["dgacm_listeleri"].split(";")) == {"ASP", "WEOG"} and "seçimlerde" in bg["TUR"]["not"]
    assert bg["USA"]["grup"] == "WEOG" and "hiçbir bölgesel grubun üyesi değildir" in bg["USA"]["not"]
    assert "TUR" in G["WEOG"]["uyeler"] and "USA" in G["WEOG"]["uyeler"] and "TUR" not in G["ASP"]["uyeler"]
    assert any("iki grupta" in n["tr"] for n in G["WEOG"]["notlar"]) and any("hiçbir bölgesel grubun" in n["tr"] for n in G["WEOG"]["notlar"])
    assert all(n["tr"] and n["en"] for x in V["gruplar"] + V["kumeler"] for n in x["notlar"])
    # DGACM listesi: 194 satır (Türkiye iki kez), 193 ayrı üye
    assert sum(len(r["dgacm_listeleri"].split(";")) for r in bg.values()) == 194


def test_p5_nufus_payi_elle_hesaplanan_degerle_tutuyor():
    # WPP 2024, 1 Ocak 2023 tahmini (bin): Çin 1 424 260,946; Fransa 66 381,485; Birleşik Krallık 68 442,882;
    # Rusya Federasyonu 145 675,420; ABD 342 475,098. 193 üyenin toplamı 8 009 406,047 (WPP toplamı 8 009 868,794'ten Kıbrıs'taki
    # KKTC nüfusu 462,747 çıkarılmış; test_kktc_nufusu_kibristan_ayri).
    p5 = 1424260.946 + 66381.485 + 68442.882 + 145675.420 + 342475.098
    assert abs(p5 / 8009406.047 - K["P5"]["paylar"]["nufus_2023"]) < 1e-6
    assert round(K["P5"]["paylar"]["nufus_2023"], 3) == 0.256
    nufus = {r["iso3"]: float(r["nufus_2023_bin"]) for r in oku("nufus_wpp2024.csv")}
    assert abs(sum(nufus[k] for k in ("CHN", "FRA", "GBR", "RUS", "USA")) - p5) < 1e-3
    assert abs(sum(u["nufus_2023"] for u in V["uyeler"]) - (8009868.794 - 462.747)) < 1e-3


def test_1963_uyeleri_ve_ardil_devletler():
    U63 = V["uyeler_1963"]
    assert len(U63) == 113 == V["meta"]["uye_sayisi_1963"]
    parcalar = [p for x in U63 for p in x["bilesenler"]]
    assert len(parcalar) == len(set(parcalar)), "çift sayım"
    sscb = next(x for x in U63 if x["iso3"] == "RUS")
    assert len(sscb["bilesenler"]) == 13 and "UKR" not in sscb["bilesenler"] and "BLR" not in sscb["bilesenler"]
    assert {x["uye_1963"] for x in U63 if x["iso3"] is None} == {"Czechoslovakia", "Yugoslavia", "Zanzibar"}
    assert all(x["not"] for x in U63 if x["iso3"] in ("RUS", "PAK", "CHN", "MYS", "SDN", "ETH") or x["iso3"] is None)
    assert sum(g["uye_sayisi_1963"] for g in V["gruplar"]) == 113


def test_iit_kumesi():
    iit = oku("iit_uyeleri.csv")
    assert len(iit) == 57 and sum(1 for r in iit if r["bm_uyesi"] == "evet") == 56 and next(r for r in iit if r["iso3"] == "PSE")["bm_uyesi"] == "hayir"
    assert K["IIT"]["uye_sayisi"] == 56 and "PSE" not in K["IIT"]["uyeler"] and K["IIT"]["koltuk"]["daimi"] == 0
    assert any("Filistin" in n["tr"] and "Palestine" in n["en"] for n in K["IIT"]["notlar"])


def test_oranlar_ve_girdi_ozetleri():
    for x in V["gruplar"] + V["kumeler"]:
        for g in ("nufus_2023", "uye", "butce", "personel"):
            if x["paylar"][g]:
                assert abs(x["oranlar"][g] - round(x["koltuk"]["toplam_payi"] / x["paylar"][g], 3)) < 1e-9
    import hashlib
    for ad, sha in V["meta"]["girdi_sha256"].items():
        assert hashlib.sha256((GIRDI / ad).read_bytes()).hexdigest() == sha, ad
    js = (KOK / "web/temsil_veri.js").read_text(encoding="utf-8")
    assert json.loads(js[js.index("{"):js.rstrip().rindex(";")]) == V


def test_sayfa_ve_baglantilar():
    sayfa = (KOK / "web/temsil.html").read_text(encoding="utf-8")
    assert 'src="temsil_veri.js"' in sayfa and "TEMSIL_VERISI" in sayfa
    for s in ("DGACM", "2025–2027", "28 Şubat 2026", "prefers-reduced-motion"):
        assert s in sayfa, s
    # ADIM 46: nüfus payı BM üyelerinin toplamı içinde (payda 193 üye; dünya toplamına göre pay ayrı alan)
    assert "beş payı yan yana gösterir: BM üyelerinin toplam nüfusundaki pay," in sayfa and "share of the total population of UN Member States" in sayfa
    assert "dünya nüfusundaki pay" not in sayfa and "share of world population" not in sayfa
    # ADIM 45: tanımlar ve kaynak listesi (künyeler, lisans) "Nasıl yaptık?"ta, Metodoloji 2.9'da; sayfada değil
    for md in ("METODOLOJI.md", "METODOLOJI_EN.md"):
        m = (KOK / md).read_text(encoding="utf-8")
        for s in ("A/RES/1991", "CC BY 3.0 IGO", "DGACM", "28/02/2026", "A/RES/79/249", "WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx",
                  "oic-oci.org/en/members", "main.un.org/securitycouncil/en/content/current-members", "Porto Riko" if md == "METODOLOJI.md" else "Puerto Rico"):
            assert s in m, (md, s)
    for s in ("CC BY 3.0 IGO", "WPP2024_GEN_F01", "scripts/09_temsil.py", 'id="tanimlar"', 'id="alt"'):
        assert s not in sayfa, s
    # Sayfada sabit pay yok: değerler veri dosyasından okunur
    betik = sayfa[sayfa.index("<script>"):]
    assert not re.search(r"\b0\.25[56]\b", betik)
    yasak = re.compile(r"\b(adalet|adil|haks[ıi]z|orantısız|unfair|unjust|disproportionate|should|must)\b", re.I)
    assert not yasak.search(re.sub(r"<[^>]+>", " ", sayfa))
    assert '["temsil", "Kim temsil ediliyor?", "Who is represented?"],' in (KOK / "web/cubuk.js").read_text(encoding="utf-8")
    for md in ("METODOLOJI.md", "METODOLOJI_EN.md"):
        assert "09_temsil" in (KOK / md).read_text(encoding="utf-8"), md


def test_kktc_nufusu_kibristan_ayri():
    """Kullanıcı kararı (19 Ekim 2026): WPP 2024'ün Kıbrıs verisi adanın tamamını kapsar ("Refers to the whole country"); KKTC
    İstatistik Kurumu'nun 2022 yıl sonu projeksiyonu (WPP'nin 1 Ocak 2023 tahminiyle aynı an) Kıbrıs'tan çıkarılır. KKTC BM üyesi
    olmadığı için paydaya girmez; 1963 değişmez. Verideki tek BM dışı nüfus kaynağı."""
    import hashlib
    wpp = {r["iso3"]: r for r in csv.DictReader(open(GIRDI / "nufus_wpp2024.csv", encoding="utf-8")) if r["iso3"]}
    k = list(csv.DictReader(open(GIRDI / "kktc_nufus.csv", encoding="utf-8")))
    assert len(k) == 1 and k[0]["kaynak"] == "KKTC İstatistik Kurumu" and k[0]["referans"] == "2022 yıl sonu" and k[0]["nufus_bin"] == "462.747"
    kibris = next(u for u in V["uyeler"] if u["iso3"] == "CYP")
    assert kibris["nufus_2023"] == round(float(wpp["CYP"]["nufus_2023_bin"]) - 462.747, 3) == 875.367
    assert "462.747" in kibris["not"]["tr"] and "462,747" in kibris["not"]["en"] and V["meta"]["kktc_nufus_bin"] == 462.747
    assert abs(V["meta"]["toplamlar"]["nufus_2023_bin"] - sum(u["nufus_2023"] for u in V["uyeler"])) < 1e-6
    assert next(u for u in V["uyeler_1963"] if u["iso3"] == "CYP")["nufus_1963"] == float(wpp["CYP"]["nufus_1963_bin"])
    pdf = KOK / "kaynaklar/.belgeler/kktc" / k[0]["dosya"]
    if pdf.exists():
        assert hashlib.sha256(pdf.read_bytes()).hexdigest() == k[0]["sha256"]
    for md, s in (("METODOLOJI.md", "Bu, verideki tek BM dışı nüfus kaynağıdır"), ("METODOLOJI_EN.md", "This is the only non-UN population source in the data")):
        assert s in (KOK / md).read_text(encoding="utf-8"), md
    for lisans in (KOK / "LICENSE-DATA", KOK / "web/LICENSE-DATA.txt"):
        t = lisans.read_text(encoding="utf-8")
        for s in ("9. Kuzey Kıbrıs Türk Cumhuriyeti nüfusu. KKTC İstatistik Kurumu", "7. Harita sınırları. Natural Earth",
                  "8. Ülke ve alan adları.", "Unicode Lisansı v3", "10. İslam İşbirliği Teşkilatı üye listesi", "7. Map borders. Natural Earth",
                  "9. Population of the Turkish Republic of Northern Cyprus."):
            assert s in t, (lisans.name, s)
