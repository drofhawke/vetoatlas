"""İşlenmiş veri setinin (03 çıktısı) değişmezleri. Hat yeniden çalıştırıldıktan sonra da tutmalı."""
import json
import re
from pathlib import Path
import sys

import pytest

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

from veto_atlasi.kaynak import kaynak_dogrula

VERI = json.loads((KOK / "data/processed/vetolar_mutabik.json").read_text(encoding="utf-8"))
KAYIT = {k["id"]: k for k in VERI["kayitlar"]}


def test_toplamlar():
    assert len(VERI["kayitlar"]) == 266
    assert sum(len(k["veto_eden_uyeler"]) for k in VERI["kayitlar"] if not k["atif_belirsiz"]) == 322


def test_kaynak_ozeti_diskteki_dosyayla_ayni():
    if not (KOK / VERI["meta"]["kaynak_dosya"]).exists():
        pytest.skip(f"ham dosya yerelde yok (açık depo): {VERI['meta']['kaynak_dosya']}; künye data/raw/KAYNAK.md")
    kaynak_dogrula(KOK, VERI["meta"])


def test_eylul_2026_birincil_kaynaktan_eklendi():
    k = KAYIT["V-2026-09-17-1"]
    assert k["taslak_belgeler"] == ["S/2026/740"]
    assert k["taslak_kaynagi"] == "belge"          # taslak sütunu okunmazsa "toplanti_kaydi" olur
    assert k["toplanti_kayitlari"] == ["S/PV.10224"]
    assert sorted(k["veto_eden_uyeler"]) == ["CHN", "RUS"]
    assert k["oy_dagilimi"] == {"lehte": 11, "aleyhte": 2, "cekimser": 2}
    assert k["kaynak_url"] == "https://undocs.org/S/PV.10224"


def test_nisan_2026_oyu_birincil_kaynaktan():
    assert KAYIT["V-2026-04-07-1"]["oy_dagilimi"] == {"lehte": 11, "aleyhte": 2, "cekimser": 2}


# ---------- Toplantı kayıtlarından doğrulama (Adım 5) ----------

def test_fransa_ret_oyu_on_soru_oylamasinda():
    on_soru = KAYIT["V-1946-06-26-2"]
    assert on_soru["on_soru_vetosu"] and sorted(on_soru["veto_eden_uyeler"]) == ["FRA", "SSCB"]
    assert on_soru["oy_dagilimi"] == {"lehte": 8, "aleyhte": 2, "cekimser": 1}
    for i in ("V-1946-06-26-1", "V-1946-06-26-3"):
        assert KAYIT[i]["veto_eden_uyeler"] == ["SSCB"]
        assert KAYIT[i]["oy_dagilimi"] == {"lehte": 9, "aleyhte": 2, "cekimser": 0}


def test_oylama_gunleri_toplanti_kaydindan():
    beklenen = {"V-1950-09-05-1": "1950-09-06", "V-1960-12-03-1": "1960-12-04", "V-1961-02-21-1": "1961-02-21",
                "V-1961-02-21-2": "1961-02-21", "V-1968-08-22-1": "1968-08-23", "V-1995-05-17-1": "1995-05-17",
                "V-1980-01-11-1": "1980-01-13"}
    for i, gun in beklenen.items():
        assert KAYIT[i]["tarih"] == gun, i
        assert KAYIT[i]["toplanti_dogrulamasi"]["tarih"]["durum"] == "dogrulandi"
    # S/PV.2191 iki oturumlu: 11 Ocak'ta ara verildi, S/13735 13 Ocak'taki ikinci oturumda oylandı
    assert KAYIT["V-1980-01-11-1"]["oy_dagilimi"] == {"lehte": 10, "aleyhte": 2, "cekimser": 2}
    assert KAYIT["V-1980-01-11-1"]["toplanti_dogrulamasi"]["oy"]["sayfa"] == "16"


def test_her_acik_oturum_vetosunun_oy_dagilimi_var_ve_15i_asmiyor():
    for k in VERI["kayitlar"]:
        if k["atif_belirsiz"]:
            continue
        oy = k["oy_dagilimi"]
        assert oy, k["id"]
        assert oy["lehte"] + oy["aleyhte"] + oy["cekimser"] <= 15, k["id"]
    assert KAYIT["V-2015-07-08-1"]["oy_dagilimi"] == {"lehte": 10, "aleyhte": 1, "cekimser": 4}
    assert KAYIT["V-2021-12-13-1"]["oy_dagilimi"] == {"lehte": 12, "aleyhte": 2, "cekimser": 1}


def test_dogrulaniyor_etiketinde_kayit_kalmadi():
    import importlib.util
    from veto_atlasi.konu import duzeltmeleri_oku, sozluk_oku
    spec = importlib.util.spec_from_file_location("web_verisi", KOK / "scripts/04_web_verisi.py")
    web = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(web)
    paket, _, _ = web.paket_olustur(
        VERI, sozluk_oku(KOK / "kaynaklar/gundem_sozlugu.csv"), duzeltmeleri_oku(KOK / "kaynaklar/konu_duzeltmeleri.csv"),
        json.loads((KOK / "schema/veto_kaydi.schema.json").read_text(encoding="utf-8")), "0" * 64)
    kalan = {k["id"]: k["dogrulama"] for k in paket["kayitlar"] if k["dogrulama"]}
    assert kalan == {}


def test_ayni_icerikli_satirlar_toplanti_kaydindan_ayristi():
    # S/PV.456: S/1431 iki parça hâlinde oylandı; referans tablo ikisine de 8-2-1 veriyor
    assert KAYIT["V-1949-12-13-1"]["oy_dagilimi"] == {"lehte": 9, "aleyhte": 2, "cekimser": 0}
    assert KAYIT["V-1949-12-13-2"]["oy_dagilimi"] == {"lehte": 8, "aleyhte": 2, "cekimser": 1}
    # S/PV.2580: S/17172 paragraf paragraf oylandı
    assert [KAYIT[f"V-1985-05-10-{i}"]["oy_dagilimi"]["cekimser"] for i in (1, 2, 3)] == [1, 3, 1]
    for k in VERI["kayitlar"]:
        if k["id"].startswith(("V-1946-06-26", "V-1949-12-13", "V-1961-02-21", "V-1961-11-24", "V-1985-05-10")):
            assert k["toplanti_dogrulamasi"]["oy"]["durum"] == "dogrulandi", k["id"]


def test_dogrulanan_her_alanin_toplanti_kaydi_ve_sayfasi_var():
    sayi = 0
    for k in VERI["kayitlar"]:
        for alan, v in k["toplanti_dogrulamasi"].items():
            if v["durum"] == "dogrulandi":
                sayi += 1
                assert v["toplanti"].startswith("S/PV.") and v["sayfa"], (k["id"], alan)
                # BM belge sisteminde bulunmayan kayıt (S/PV.2191) Dijital Kütüphane'den elle indirildi
                assert re.fullmatch(r"https://undocs\.org/S/PV\.\d+(\(OR\))?|https://digitallibrary\.un\.org/record/\d+",
                                    v["kaynak_url"]), (k["id"], alan)
    assert sayi == 68  # 42 oy + 7 tarih + 19 üye
    # Yerel belgeler (kaynaklar/.belgeler/) tests/test_belgeler.py ile denetlenir

def test_referans_tabloya_dayanan_eklemeler_toplanti_kaydindan_dogrulandi():
    # 13 Aralık 1955 (S/PV.704, 16 veto) ve 10 Eylül 1972 (S/PV.1662) eklemeleri: oy ve üye toplantı kaydından
    eklenen = [k for k in VERI["kayitlar"] if (k.get("duzeltme") or "").startswith("eklendi: scprocedure")]
    assert len(eklenen) == 17
    for k in eklenen:
        td = k["toplanti_dogrulamasi"]
        assert td["oy"]["durum"] == td["uye"]["durum"] == "dogrulandi", k["id"]
        assert td["oy"]["toplanti"] in ("S/PV.704", "S/PV.1662") and k["toplanti_kayitlari"] == [td["oy"]["toplanti"]], k["id"]
        assert td["oy"]["paragraf"], k["id"]  # birincil atıf paragraf numarası
    # 13 Aralık 1955: S/3502'nin ikinci giriş paragrafındaki 14 kelime ayrı oylandı -> kısmi veto, taslak S/3502
    kelime = [k for k in eklenen if k["tarih"] == "1955-12-13" and k["taslak_belgeler"] == ["S/3502"]]
    assert len(kelime) == 14 and all(k["kismi_veto_suphesi"] for k in kelime)
    # S/3506'nın iki parçası: taslak S/3502 + değişiklik önergesi S/3506; 13 Aralık 1955'in 16 kaydı da kısmi veto
    onerge = [k for k in eklenen if k["tarih"] == "1955-12-13" and k["taslak_belgeler"] == ["S/3502", "S/3506"]]
    assert len(onerge) == 2 and all(k["kismi_veto_suphesi"] for k in eklenen if k["tarih"] == "1955-12-13")
    assert sum(1 for k in VERI["kayitlar"] if k["kismi_veto_suphesi"]) == 31
    # Moğolistan vetosu Çin Cumhuriyeti'nin (1971 öncesi "Çin" koltuğu); toplantıda 16 vetonun 3.'sü
    mog = KAYIT["V-1955-12-13-16"]
    assert mog["veto_eden_uyeler"] == ["CHN"] and "Republic of China" in mog["notlar"][0] and "3.'sü" in mog["notlar"][0]
    # 1972: değişiklik (S/10786 2 (a), 9-6-0) ABD vetosundan önce oylandı
    deg = KAYIT["V-1972-09-10-2"]
    assert deg["taslak_belgeler"] == ["S/10786"] and sorted(deg["veto_eden_uyeler"]) == ["CHN", "SSCB"]
    assert deg["kismi_veto_suphesi"] and "önce yapıldı" in deg["notlar"][0]


def test_acik_veri_dosyalari_ve_ozetleri():
    import hashlib
    s = (KOK / "web/veri.js").read_text(encoding="utf-8")
    meta = json.loads(s[s.index("{"):s.rstrip().rindex(";")])["meta"]
    adlar = sorted(f["dosya"] for f in meta["indirmeler"])
    assert adlar == ["veri/genel_kurul_tartismalari.csv", "veri/vetolar.csv", "veri/vetolar.json"]
    for f in meta["indirmeler"]:
        icerik = (KOK / "web" / f["dosya"]).read_bytes()
        assert hashlib.sha256(icerik).hexdigest() == f["sha256"] and len(icerik) == f["bayt"]
    acik = json.loads((KOK / "web/veri/vetolar.json").read_text(encoding="utf-8"))
    assert acik["meta"]["kayit_sayisi"] == 266 and acik["meta"]["veri_surumu"] == meta["veri_surumu"]


def test_notlarin_ingilizcesi_tam_ve_eksik_olursa_04_uyarir():
    import copy
    import importlib.util
    from veto_atlasi.konu import duzeltmeleri_oku, sozluk_oku
    spec = importlib.util.spec_from_file_location("web_verisi", KOK / "scripts/04_web_verisi.py")
    web = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(web)
    argumanlar = (sozluk_oku(KOK / "kaynaklar/gundem_sozlugu.csv"),
                  duzeltmeleri_oku(KOK / "kaynaklar/konu_duzeltmeleri.csv"),
                  json.loads((KOK / "schema/veto_kaydi.schema.json").read_text(encoding="utf-8")), "0" * 64)
    paket, uyarilar, _ = web.paket_olustur(VERI, *argumanlar)
    assert not [u for u in uyarilar if "İngilizce" in u]
    for k in paket["kayitlar"]:
        assert all(n["tr"] and n["en"] for n in k["notlar"]), k["id"]
        assert bool(k["duzeltme"]) == bool(k["duzeltmeEn"]), k["id"]
    # Belge kodları, sayfa numaraları ve öbür bütün sayılar çeviride korunur
    for k in VERI["kayitlar"]:
        for tr, en in zip(k["notlar"], k["notlar_en"]):
            assert re.findall(r"S/PV\.\d+|S/\d{4}/\d+|S/\d+", tr) == re.findall(r"S/PV\.\d+|S/\d{4}/\d+|S/\d+", en), tr
            assert sorted(re.findall(r"\d+", tr)) == sorted(re.findall(r"\d+", en)), tr

    eksik = copy.deepcopy(VERI)
    eksik["kayitlar"][0]["notlar_en"][0] = None
    _, uyarilar, _ = web.paket_olustur(eksik, *argumanlar)
    assert [u for u in uyarilar if "notun İngilizcesi eksik" in u and eksik["kayitlar"][0]["id"] in u]


def test_sozlu_degisiklik_vetosu_kismi_olarak_isaretli():
    # DHL: "S/2023/1029 oral amendment"; S/PV.9520 s. 4-5: sözlü değişiklik önergesi 10-1-4 ile düştü
    k = KAYIT["V-2023-12-22-1"]
    assert k["kismi_veto_suphesi"] and any("oral amendment" in n for n in k["notlar"])
    # "(as amended)" taslağın bütününe yapılan oylamadır
    for i in ("V-1974-07-31-1", "V-1972-09-29-1", "V-1964-12-21-1"):
        assert not KAYIT[i]["kismi_veto_suphesi"], i


def test_gazze_listesinde_degisiklik_onergesi_isaretli_ve_veriyle_tutarli():
    import copy
    import importlib.util
    import pytest
    spec = importlib.util.spec_from_file_location("web_verisi", KOK / "scripts/04_web_verisi.py")
    web = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(web)
    liste = web.gazze_oku(VERI["kayitlar"])
    assert len(liste) == 9
    assert [g["id"] for g in liste if g["hedef"] == "sozlu_degisiklik"] == ["V-2023-12-22-1"]
    # Kayıttaki "oral amendment" notu kalkarsa işaret tutmaz ve 04 durur
    kayitlar = copy.deepcopy(VERI["kayitlar"])
    k = next(x for x in kayitlar if x["id"] == "V-2023-12-22-1")
    k["notlar_en"] = []
    with pytest.raises(ValueError, match="veto_hedefi"):
        web.gazze_oku(kayitlar)
