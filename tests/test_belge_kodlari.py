"""
Verideki bütün belge kodlarının ve bağlantıların biçim denetimi.
Bağlantılara istek atılmaz; yalnızca kod ve adres yapısı doğrulanır.
"""
import csv
import json
import re
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]

# BM belge simgesi kalıpları
S_TASLAK = r"S/\d{1,5}(/(Rev|Add|Corr)\.\d+)*"            # 1946-1993: S/1653, S/4733/Rev.1
S_YILLI = r"S/(19|20)\d{2}/\d{1,4}(/(Rev|Add|Corr)\.\d+)*"  # 1994 sonrası: S/2026/740
S_PV = r"S/PV\.\d{1,5}"                                    # S/PV.49 ... S/PV.10224
A_BELGE = r"A/\d{2}/(\d{1,4}|L\.\d{1,3})(/(Rev|Add|Corr)\.\d+)*"  # A/76/853, A/76/L.52
A_PV = r"A/\d{2}/PV\.\d{1,3}"                              # A/76/PV.69
A_ES_PV = r"A/ES-\d{1,2}/PV\.\d{1,3}"                      # A/ES-11/PV.10
A_RES = r"A/RES/\d{2}/\d{1,4}"                             # A/RES/76/262
A_RES_ES = r"A/RES/ES-\d{1,2}/\d{1,3}"                     # A/RES/ES-11/1

SC_KOD = re.compile(f"{S_PV}|{S_YILLI}|{S_TASLAK}")
GA_KOD = re.compile(f"{A_PV}|{A_ES_PV}|{A_RES_ES}|{A_RES}|{A_BELGE}")
KOD = re.compile(f"{SC_KOD.pattern}|{GA_KOD.pattern}")
# undocs.org bağlantısı: https://undocs.org/<kod>, eski kayıtlar için isteğe bağlı (OR) eki
UNDOCS = re.compile(rf"https://undocs\.org/(?P<kod>{KOD.pattern})(?P<or>\(OR\))?")
DIGER_URL = [
    re.compile(r"https://digitallibrary\.un\.org/record/\d+"),
    re.compile(r"https://journal\.un\.org/en/new-york/all/\d{4}-\d{2}-\d{2}"),
    re.compile(r"https://press\.un\.org/en/\d{4}/sc\d{4,5}\.doc\.htm"),
]
METIN_URL = re.compile(r"https?://[^\s\"'<>)|;,]+")


def veri_js():
    s = (KOK / "web/veri.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"):s.rstrip().rindex(";")])


def csv_oku(ad):
    with open(KOK / "kaynaklar" / ad, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def url_gecerli(u):
    return bool(UNDOCS.fullmatch(u)) or any(r.fullmatch(u) for r in DIGER_URL)


def kod_url_esles(kod, url):
    m = UNDOCS.fullmatch(url)
    return bool(m) and m["kod"] == kod


def test_kalip_ornekleri():
    for iyi in ["S/1653", "S/4733/Rev.1", "S/2026/740", "S/PV.49", "S/PV.10224", "A/76/853", "A/76/L.52",
                "A/76/PV.69", "A/ES-11/PV.10", "A/RES/76/262", "A/RES/ES-11/1"]:
        assert KOD.fullmatch(iyi), iyi
    for kotu in ["S/S/PV.2602", "S/PV.PV.4842", "S/11400 as amended", "s/pv.49", "S/PV 49", "A/RES/76", "S/2026/",
                 "A/ES11/PV.1", "S/PV.49 "]:
        assert not KOD.fullmatch(kotu), kotu
    assert url_gecerli("https://undocs.org/S/PV.1443(OR)")
    for kotu in ["http://undocs.org/S/PV.49", "https://undocs.org/en/S/S/PV.2602", "https://undocs.org/S/11400 as amended",
                 "https://undocs.org/", "https://undocs.org/S/PV.49/"]:
        assert not url_gecerli(kotu), kotu


def test_arayuz_verisindeki_kodlar_ve_baglantilar():
    v = veri_js()
    sayi = 0
    for k in v["kayitlar"]:
        for b in k["belgeler"]:
            assert SC_KOD.fullmatch(b["kod"]), (k["id"], b["kod"])
            assert kod_url_esles(b["kod"], b["url"]), (k["id"], b)
            assert (b["tur"] == "toplanti") == b["kod"].startswith("S/PV."), (k["id"], b)
            sayi += 1
        for d in k["dogrulamaKaynagi"]:
            assert re.fullmatch(S_PV, d["toplanti"]) and url_gecerli(d["url"]), (k["id"], d)
            if "undocs.org" in d["url"]:
                assert UNDOCS.fullmatch(d["url"])["kod"] == d["toplanti"], (k["id"], d)
        gk = k.get("gk")
        if not gk:
            continue
        if gk.get("ozelRapor"):
            assert re.fullmatch(A_BELGE, gk["ozelRapor"]["kod"]), k["id"]
            assert kod_url_esles(gk["ozelRapor"]["kod"], gk["ozelRapor"]["url"]), k["id"]
        for t in gk["tartismalar"]:
            for r in t["kayitlar"]:
                assert re.fullmatch(f"{A_PV}|{A_ES_PV}", r["kod"]), (t["id"], r)
                assert kod_url_esles(r["kod"], r["url"]), (t["id"], r)
            for r in t["kararlar"]:
                assert re.fullmatch(f"{A_RES_ES}|{A_RES}", r["kod"]), (t["id"], r)
                assert kod_url_esles(r["kod"], r["url"]), (t["id"], r)
            for u in METIN_URL.findall(t.get("dogrulamaKaynagi") or ""):
                assert url_gecerli(u), (t["id"], u)
    assert sayi > 450  # 266 kayıt, taslak + toplantı kaydı


def test_islenmis_verideki_kodlar():
    v = json.loads((KOK / "data/processed/vetolar_mutabik.json").read_text(encoding="utf-8"))
    for k in v["kayitlar"]:
        for kod in k["taslak_belgeler"]:
            assert re.fullmatch(f"{S_YILLI}|{S_TASLAK}", kod), (k["id"], kod)
        for kod in k["toplanti_kayitlari"]:
            assert re.fullmatch(S_PV, kod), (k["id"], kod)


def test_kaynak_dosyalardaki_kodlar_ve_baglantilar():
    for i, s in enumerate(csv_oku("duzeltmeler.csv"), start=2):
        if s["toplanti"]:
            assert re.fullmatch(S_PV, s["toplanti"]), i
        for taslak in filter(None, s["taslak"].split(";")):  # "ekle" satırında "taslak;önerge" olabilir
            assert re.fullmatch(f"{S_YILLI}|{S_TASLAK}", taslak), i
        if s["kaynak_url"]:
            assert url_gecerli(s["kaynak_url"]), (i, s["kaynak_url"])
            if "undocs.org" in s["kaynak_url"]:
                assert UNDOCS.fullmatch(s["kaynak_url"])["kod"] == s["toplanti"], i
        for u in METIN_URL.findall(s["aciklama"] + " " + s["aciklama_en"]):
            assert url_gecerli(u), (i, u)
    for s in csv_oku("ozel_raporlar.csv"):
        assert re.fullmatch(A_BELGE, s["ozel_rapor"]) and re.fullmatch(S_PV, s["sc_toplanti"]), s
        assert kod_url_esles(s["ozel_rapor"], s["kaynak_url"]), s
    for s in csv_oku("genel_kurul_tartismalari.csv"):
        for kod in filter(None, s["toplanti_kayitlari"].split(";")):
            assert re.fullmatch(f"{A_PV}|{A_ES_PV}", kod), (s["tartisma_id"], kod)
        for kod in filter(None, s["kabul_edilen_kararlar"].split(";")):
            assert re.fullmatch(f"{A_RES_ES}|{A_RES}", kod), (s["tartisma_id"], kod)
        for u in METIN_URL.findall(s["dogrulama_kaynagi"]):
            assert url_gecerli(u), (s["tartisma_id"], u)


def test_acik_veri_baglantilari_koddan_kurulur():
    v = json.loads((KOK / "web/veri/vetolar.json").read_text(encoding="utf-8"))
    for k in v["kayitlar"]:
        kodlar = list(dict.fromkeys(k["taslak_belgeler"] + k["toplanti_kayitlari"]))
        assert k["belge_linkleri"] == [f"https://undocs.org/{kod}" for kod in kodlar], k["id"]
        assert all(url_gecerli(u) for u in k["belge_linkleri"]), k["id"]
    with open(KOK / "web/veri/vetolar.csv", encoding="utf-8-sig", newline="") as f:
        for s in csv.DictReader(f):
            for kod in filter(None, (s["taslak_belgeler"] + "; " + s["toplanti_kayitlari"]).split("; ")):
                assert SC_KOD.fullmatch(kod), (s["id"], kod)


def test_dhl_bozuk_baglantilari_hata_bildiriminde():
    # Ham DHL bağlantılarından biçimi bozuk olanlar DHL'ye yazılan iletide (1. bölüm) listelenmiş olmalı
    v = json.loads((KOK / "data/processed/vetolar_mutabik.json").read_text(encoding="utf-8"))
    dhl = re.compile(rf"https://undocs\.org/en/({KOD.pattern})(AND(CORR|ADD)\.\d+)*(\(OR\))?")
    bozuk = {u for k in v["kayitlar"] for u in k["belge_linkleri"]
             if "undocs.org/en/" in u and not dhl.fullmatch(u)}
    bildirim = (KOK / "kaynaklar/hata_bildirimi.md").read_text(encoding="utf-8")
    dhl_ileti = bildirim[bildirim.index("## 1."):bildirim.index("## 2.")]
    assert len(bozuk) == 5
    for u in bozuk:
        assert f"`{u}`" in dhl_ileti, u


def test_hata_bildiriminde_yer_tutucu_kalmadi():
    # İki ileti de yayın adresi, DOI ve imzayla gönderilmeye hazır; köşeli ayraçlı yer tutucu yok. Adres ve DOI her
    # iletide bir kez geçer: DHL iletisinde kapanış paragrafında, scprocedure iletisinde atıf paragrafında
    bildirim = (KOK / "kaynaklar/hata_bildirimi.md").read_text(encoding="utf-8")
    dhl, scp = bildirim[bildirim.index("## 1."):bildirim.index("## 2.")], bildirim[bildirim.index("## 2."):bildirim.index("## 3.")]
    assert "The dataset is available at https://vetoatlas.com (DOI: 10.5281/zenodo.23326362)." in dhl
    assert "\n\nTable 4 has been very helpful to us, and we would be\nglad to share the full reconciliation file" in scp
    for ileti in (dhl, scp):
        tek = " ".join(ileti.split())
        assert tek.count("https://vetoatlas.com") == 1 and tek.count("10.5281/zenodo.23326362") == 1, ileti
        assert ileti.rstrip().endswith("With kind regards,\n\nNuh Mehmet Yıldız, independent researcher · iletisim@vetoatlas.com")
        assert not re.search(r"\[[^\]]*\](?!\()", ileti), ileti  # bağlantılar ([S/PV.456](…)) hariç


def test_scprocedure_iletisi_yayindan_sonra_atif_bildirir():
    # Veri yayımlandıktan sonra yazılan ileti izin istemez; Tablo 4'ten alınan oy sayılarının atfını ve kaldırma teklifini bildirir
    bildirim = (KOK / "kaynaklar/hata_bildirimi.md").read_text(encoding="utf-8")
    ileti = " ".join(bildirim[bildirim.index("## 2."):bildirim.index("## 3.")].split())
    assert ("The Veto Atlas dataset has now been published at https://vetoatlas.com (DOI: 10.5281/zenodo.23326362). "
            "Overall vote counts for a number of records were taken from Table 4 and are attributed to it; where we could, "
            "we verified them against the meeting records, and the corrections listed above come from that process. "
            "The table itself is not redistributed. If you would prefer a different form of attribution, or would like us "
            "to remove any material derived from Table 4, please let us know and we will do so promptly.") in ileti
    assert "permission" not in ileti and "we would like to publish it" not in ileti


def test_aciklama_kutusundaki_belge_kodlari():
    s = (KOK / "web/vetolar.html").read_text(encoding="utf-8")
    kodlar = re.findall(r'BELGE\("([^"]+)"', s)
    assert len(kodlar) >= 9
    for kod in kodlar:
        assert GA_KOD.fullmatch(kod), kod
    for u in METIN_URL.findall(s):
        if "undocs.org" in u and u != "https://undocs.org/":
            assert url_gecerli(u), u
