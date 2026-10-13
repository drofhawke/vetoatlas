import copy
import json
from pathlib import Path
import sys

import pytest

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

from veto_atlasi.genel_kurul import (KAPSAM_BASLANGICI, bekleyen_kayitlar, genel_kurul_ekle, raporlari_oku,
                                     tartismalari_oku)

TARTISMA = tartismalari_oku(KOK / "kaynaklar/genel_kurul_tartismalari.csv")
RAPOR = raporlari_oku(KOK / "kaynaklar/ozel_raporlar.csv")
VERI = json.loads((KOK / "data/processed/vetolar_mutabik.json").read_text(encoding="utf-8"))
T = {t["id"]: t for t in TARTISMA}


def _ekli():
    kayitlar = copy.deepcopy(VERI["kayitlar"])
    return kayitlar, genel_kurul_ekle(kayitlar, TARTISMA, RAPOR)


def test_kapsamdaki_her_veto_gorusuldu_ve_ozel_raporu_var():
    kayitlar, uyarilar = _ekli()
    assert uyarilar == []
    kapsam = [k for k in kayitlar if k["tarih"] >= KAPSAM_BASLANGICI]
    assert len(kapsam) == 22
    assert all(k["genel_kurul"]["durum"] == "yapildi" and k["genel_kurul"]["ozel_rapor"] for k in kapsam)
    assert all(k["genel_kurul"]["durum"] == "kapsam_disi" for k in kayitlar if k["tarih"] < KAPSAM_BASLANGICI)


def test_tartisma_turleri():
    vg = [t for t in TARTISMA if t["tur"] == "veto_girisimi"]
    oo = [t for t in TARTISMA if t["tur"] == "olaganustu_ozel_oturum"]
    assert len(vg) == 15 and len(oo) == 6
    # Olağanüstü özel oturumlarda konuşmacı sayısı yok, kabul edilen kararlar var
    assert all(t["konusmacilar"] is None and t["kabul_edilen_kararlar"] for t in oo)


def test_kontrol_olcutu_a_79_pv_60():
    k = T["GK-2025-03-06"]["konusmacilar"]
    assert k["aciklama_uye_devlet"] + k["aciklama_gozlemci"] == 35  # Başkanlık özeti: 35 delegasyon
    assert k["grup_adina_konusan"] == 6 and k["cevap_hakki"] == 2
    assert k["veto_eden_konustu"] == {"RUS": "aciklama"}


def test_cifte_vetoda_iki_ulke_ayri_tutulur():
    for tid in ("GK-2022-06-08", "GK-2024-04-08", "GK-2026-04-16", "GK-2026-10-01"):
        assert set(T[tid]["konusmacilar"]["veto_eden_konustu"]) == {"CHN", "RUS"}


def test_bir_veto_iki_tartismada():
    # 18 Nisan 2024 vetosu hem veto girişimi tartışmasında hem ES-10'da görüşüldü
    kayitlar, _ = _ekli()
    k = {x["id"]: x for x in kayitlar}["V-2024-04-18-1"]
    assert k["genel_kurul"]["tartismalar"] == ["GK-2024-05-01", "GK-ES10-2024-05-10"]


def test_bekleyen_kayitlar_ve_gayriresmi_isaret():
    bekleyen = bekleyen_kayitlar(TARTISMA)
    assert ("GK-2026-10-01", "A/81/PV.16", "gayriresmi_transkript") in bekleyen
    assert all(d in ("gayriresmi_transkript", "yayimlanmadi") for _, _, d in bekleyen)
    # Resmî kaydı olmayan tartışmanın konuşmacıları toplantı kaydından gelemez
    for t in TARTISMA:
        if t["konusmacilar"] and all(r["durum"] != "resmi" for r in t["toplanti_kayitlari"]):
            assert t["konusmacilar"]["kaynak"] != "toplanti_kaydi"


def test_gecersiz_kayit_durumu_reddedilir(tmp_path):
    satirlar = (KOK / "kaynaklar/genel_kurul_tartismalari.csv").read_text(encoding="utf-8").splitlines()
    p = tmp_path / "t.csv"
    p.write_text("\n".join([satirlar[0], satirlar[1].replace(";resmi", ";taslak", 1).replace(",resmi", ",taslak", 1)]),
                 encoding="utf-8")
    with pytest.raises(ValueError, match="kayıt durumu"):
        tartismalari_oku(p)
