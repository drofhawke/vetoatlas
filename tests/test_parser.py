from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from veto_atlasi.parser import tablo_ayristir, uyeleri_bul, tarih_ayristir

HTML = (Path(__file__).parent / "fixtures" / "veto_ornek.html").read_text(encoding="utf-8")


def test_kayit_ve_inceleme_sayisi():
    kayitlar, inceleme = tablo_ayristir(HTML)
    assert len(kayitlar) == 12
    assert len(inceleme) == 1 and inceleme[0]["neden"] == "tarih_yok"


def test_bitisik_uye_isimleri():
    assert uyeleri_bul("ChinaRussian Federation") == ["RUS", "CHN"]
    assert uyeleri_bul("FranceUK USA") == ["GBR", "USA", "FRA"]
    assert uyeleri_bul("USSR") == ["SSCB"]


def test_tarih_araligi():
    assert tarih_ayristir("7-9 January 1980") == ("1980-01-07", True)
    assert tarih_ayristir("06 February 1986") == ("1986-02-06", False)


def test_alanlar():
    kayitlar, _ = tablo_ayristir(HTML)
    k = {x.tarih: x for x in kayitlar}
    assert k["2020-08-31"].taslak_belgeler == ["S/2020/852", "S/2020/870"]
    assert k["2020-08-31"].kismi_veto_suphesi is True
    assert k["1986-02-06"].taslak_belgeler == ["S/17796/Rev.1"]
    assert k["2022-02-25"].toplanti_kayitlari == ["S/PV.8979"]
    assert any("Tayvan" in n for n in k["1955-12-13"].notlar)
    assert any("SSCB" in n for n in k["1980-01-07"].notlar)


def test_erken_donem_satirlari():
    kayitlar, inceleme = tablo_ayristir(HTML)
    k = {x.id: x for x in kayitlar}
    assert all(i["neden"] != "taslak_belge_yok" for i in inceleme)
    sg = k["V-1953-03-13-1"]
    assert sg.taslak_kaynagi == "toplanti_kaydi" and sg.atif_belirsiz and not sg.kismi_veto_suphesi
    assert sg.veto_eden_uyeler == ["SSCB"]
    assert k["V-1948-05-24-1"].on_soru_vetosu
    endo = k["V-1947-08-25-1"]
    assert endo.veto_eden_uyeler == ["FRA"] and endo.kismi_veto_suphesi
    assert {"V-1946-06-26-1", "V-1946-06-26-2"} <= set(k)


def test_tekrar_eden_taslak_ayiklanir():
    html = "<table><tr><td>19 August 1947</td><td>S/471 S/471</td><td>S/PV.188</td><td>Greek frontier incidents</td><td>USSR</td></tr></table>"
    kayitlar, _ = tablo_ayristir(html)
    assert kayitlar[0].taslak_belgeler == ["S/471"]
