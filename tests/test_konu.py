import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

from veto_atlasi.konu import (KONULAR, SINIFLANDIRILMADI, duzeltmeleri_oku, konu_dagilimi,
                              siniflandir, sozluk_oku)

SOZLUK = sozluk_oku(KOK / "kaynaklar/gundem_sozlugu.csv")
DUZELTME = duzeltmeleri_oku(KOK / "kaynaklar/konu_duzeltmeleri.csv")
VERI = json.loads((KOK / "data/processed/vetolar_mutabik.json").read_text(encoding="utf-8"))
SEMA = json.loads((KOK / "schema/veto_kaydi.schema.json").read_text(encoding="utf-8"))

_spec = importlib.util.spec_from_file_location("web_verisi", KOK / "scripts/04_web_verisi.py")
web_verisi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(web_verisi)

BEKLENEN = {  # konu: (öneri, oy) — yalnızca ana konu
    "Üyelik başvuruları": (60, 60), "Güney Afrika, Namibya ve Rodezya": (25, 54),
    "Filistin ve Arap-İsrail meselesi": (50, 53), "Suriye": (18, 28), "Asya": (20, 22),
    "Diğer Avrupa": (21, 22), "Diğer Ortadoğu ve Kuzey Afrika": (11, 19),
    "Latin Amerika ve Karayipler": (15, 19), "Lübnan": (12, 12), "Diğer Afrika": (10, 11),
    "Silahsızlanma ve askerî gerilimler": (11, 11), "Ukrayna": (6, 6), "Kıbrıs": (3, 3),
    "Genel Sekreter seçimi": (2, 0), "Tematik konular": (2, 2),
}


def _siniflanmis():
    kayitlar = copy.deepcopy(VERI["kayitlar"])
    return kayitlar, siniflandir(kayitlar, SOZLUK, DUZELTME)


def test_sozluk_veri_setindeki_tum_basliklari_kapsar():
    assert len(SOZLUK) == 136
    _, uyarilar = _siniflanmis()
    assert uyarilar == []


def test_konu_dagilimi_beklenen_tabloyla_ayni():
    kayitlar, _ = _siniflanmis()
    d = konu_dagilimi(kayitlar)
    assert {k: (v["oneri"], v["oy"]) for k, v in d.items()} == BEKLENEN
    assert set(BEKLENEN) == set(KONULAR)


def test_ikincil_konular_toplama_girmez():
    kayitlar, _ = _siniflanmis()
    k = {x["id"]: x for x in kayitlar}
    assert k["V-2024-04-18-1"]["konu_kategorisi"] == "Üyelik başvuruları"
    assert k["V-2024-04-18-1"]["ikincil_konular"] == ["Filistin ve Arap-İsrail meselesi"]
    for i in ("V-1956-10-30-1", "V-1956-10-30-2"):
        assert k[i]["konu_kategorisi"] == "Diğer Ortadoğu ve Kuzey Afrika"
        assert k[i]["ikincil_konular"] == ["Filistin ve Arap-İsrail meselesi"]
    for i in ("V-1958-07-18-1", "V-1958-07-22-1"):
        assert k[i]["konu_kategorisi"] == "Lübnan"
        assert k[i]["ikincil_konular"] == ["Diğer Ortadoğu ve Kuzey Afrika"]
    d = konu_dagilimi(kayitlar)
    assert d["Filistin ve Arap-İsrail meselesi"]["ikincil"] == 3
    assert d["Diğer Ortadoğu ve Kuzey Afrika"]["ikincil"] == 2
    assert sum(v["oneri"] for v in d.values()) == 266  # ikincil bağlar toplamı şişirmez


def test_04_sozlukte_olmayan_basligi_uyarir_ve_siniflandirmaz():
    veri = copy.deepcopy(VERI)
    yeni = copy.deepcopy(veri["kayitlar"][0])
    yeni.update(id="V-2026-12-01-1", tarih="2026-12-01", gundem_maddesi="A brand-new agenda item")
    veri["kayitlar"].append(yeni)
    paket, uyarilar, _ = web_verisi.paket_olustur(veri, SOZLUK, DUZELTME, SEMA, "0" * 64)
    k = {x["id"]: x for x in paket["kayitlar"]}["V-2026-12-01-1"]
    assert k["konu"] == SINIFLANDIRILMADI and k["gundemTr"] is None and k["ikincil"] == []
    konu_uyarilari = [u for u in uyarilar if "gündem başlığı" in u]
    assert len(konu_uyarilari) == 1 and "A brand-new agenda item" in konu_uyarilari[0]
    assert SINIFLANDIRILMADI in konu_uyarilari[0]
    assert paket["meta"]["konular"][-1] == SINIFLANDIRILMADI
    # Yeni veto 76/262 kapsamında: Genel Kurul tartışması henüz yoksa "bekleniyor" olur ve uyarı verilir
    assert k["gk"]["durum"] == "bekleniyor" and any("V-2026-12-01-1" in u and "Genel Kurul" in u for u in uyarilar)


def test_gecersiz_konu_reddedilir(tmp_path):
    p = tmp_path / "konu_duzeltmeleri.csv"
    p.write_text("id,konu,ikincil_konular,gerekce\nV-2000-01-01-1,Uzay,,deneme\n", encoding="utf-8")
    with pytest.raises(ValueError, match="bilinmeyen konu"):
        duzeltmeleri_oku(p)
