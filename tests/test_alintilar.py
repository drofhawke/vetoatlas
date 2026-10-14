"""
Alıntı bankası: her alıntı kaynağın metin katmanında kelimesi kelimesine geçer.
Kaynak yerelde yoksa ya da SHA-256'sı tutmuyorsa kaynağa dayanan testler atlanır; doğrulama
kaydıyla karşılaştırma ve biçim kuralları her zaman çalışır.
"""
import copy
import csv
import json
import re

import pytest

from conftest import KOK
from veto_atlasi import alinti as A

ALINTILAR = A.oku(KOK / "kaynaklar/alintilar.csv")
KONUSMA = [a for a in ALINTILAR if a["kaynak"] not in A.BOLUMLE_ATIF]
KITAP = [a for a in ALINTILAR if a["kaynak"] in A.BOLUMLE_ATIF]


def kayit():
    with open(KOK / "kaynaklar/alintilar_dogrulama.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_bicim_kurallari():
    for a in ALINTILAR:
        assert A.bicim_hatalari(a) == [], a["id"]
    # Kitap alıntılarının Türkçesinde sayfa numarası yok (bölüm başlığıyla); İngilizcesi İngilizce baskıdan, sayfa ve bölümüyle
    for a in KITAP:
        assert not a["basili_sayfa"] and not a["pdf_sayfa"]
        assert a["bolum"] in {ad for _, ad in A.KITAP_BOLUMLERI}
        assert a["kaynak_en"] == "A_Fairer_World_is_Possible_EN.pdf" and a["basili_sayfa_en"] and a["metin_en"]
        assert a["bolum_en"] in {ad for _, ad in A.KITAP_BOLUMLERI_EN}


def test_her_alintinin_resmi_ingilizcesi_var():
    """Bütün alıntıların resmî İngilizcesi bulundu: gayriresmî çeviri (ceviri_en) şu an hiçbir alıntıda yok. 2019 hitabı:
    2019-1 İngilizce kitapçıktan, 2019-2 BM toplantı kaydından (kitapçıkta yok; KAYNAKLAR.md "İngilizce metinler")."""
    assert all(a["metin_en"] and not a["ceviri_en"] for a in ALINTILAR)
    kaynak_en = {a["id"]: (a["kaynak_en"], a["belge_en"], a["basili_sayfa_en"]) for a in ALINTILAR}
    assert kaynak_en["2019-1"] == ("Birlesmis_Milletler_EN_2019.pdf", "", "6")
    assert kaynak_en["2019-2"] == ("A_74_PV.3.pdf", "A/74/PV.3", "22")
    assert kaynak_en["kitap-7"] == ("A_Fairer_World_is_Possible_EN.pdf", "", "184–185")


def test_resmi_ingilizce_ya_da_isaretli_ceviri_kurali():
    """Resmî İngilizcesi bulunamayan alıntı: metin_en ve İngilizce kaynak alanları boş, ceviri_en dolu. İkisi birden ya da
    hiçbiri olmaz."""
    a = next(x for x in ALINTILAR if x["id"] == "2019-2")
    ceviri = dict(a, metin_en="", kaynak_en="", belge_en="", basili_sayfa_en="", pdf_sayfa_en="", ceviri_en="Translation.")
    assert A.bicim_hatalari(ceviri) == []
    assert A.bicim_hatalari(dict(a, ceviri_en="Translation."))  # ikisi birden
    assert A.bicim_hatalari(dict(ceviri, ceviri_en=""))  # hiçbiri
    assert A.bicim_hatalari(dict(ceviri, pdf_sayfa_en="22"))  # çeviride İngilizce kaynak alanı olmaz
    assert A.bicim_hatalari(dict(a, belge_en=""))  # BM kaydından gelen İngilizcede belge simgesi zorunlu
    assert A.bicim_hatalari(dict(a, basili_sayfa_en="21"))  # PV'de sayfa = PDF sayfası


def test_her_alinti_dogrulama_kaydiyla_ayni():
    assert A.kayitla_karsilastir(ALINTILAR, kayit()) == []


def test_kayitta_olmayan_ya_da_degistirilen_alinti_giremez():
    uydurma = copy.deepcopy(ALINTILAR[0]) | {"id": "uydurma-1"}
    degisik = copy.deepcopy(ALINTILAR[1])
    degisik["metin_tr"] = degisik["metin_tr"].replace("karar", "kararlar")
    hatalar = A.kayitla_karsilastir([uydurma, degisik], kayit())
    assert any("uydurma-1" in h for h in hatalar) and any(degisik["id"] in h for h in hatalar)


@pytest.mark.parametrize("a", KONUSMA, ids=[a["id"] for a in KONUSMA])
def test_konusma_alintisi_sayfada_birebir(a, calisma_metni):
    sayfalar = [""] + calisma_metni(a["kaynak"], ham=True).split("\f")
    assert A.kaynakta_dogrula(a, sayfalar) == []


@pytest.mark.parametrize("a", KITAP, ids=[a["id"] for a in KITAP])
def test_kitap_alintisi_metinde_birebir_ve_bolumu_dogru(a, calisma_metni):
    sayfalar = [""] + calisma_metni(a["kaynak"], ham=True).split("\f")
    assert A.kaynakta_dogrula(a, sayfalar) == []


INGILIZCE = [a for a in ALINTILAR if a["metin_en"]]


@pytest.mark.parametrize("a", INGILIZCE, ids=[a["id"] for a in INGILIZCE])
def test_ingilizce_alinti_kaynakta_birebir(a, kaynak_sayfalari):
    """Resmî İngilizce metin, kendi kaynağının (kaynak_en) belirtilen sayfasında kelimesi kelimesine geçer; kitapta İngilizce
    bölüm başlığı da tutar."""
    assert A.kaynakta_dogrula_en(a, kaynak_sayfalari(a["kaynak_en"])) == []


def test_ingilizce_metinde_degisiklik_reddedilir(kaynak_sayfalari):
    banka = {a["id"]: a for a in ALINTILAR}
    pv = kaynak_sayfalari("A_74_PV.3.pdf")
    a = banka["2019-2"]
    assert A.kaynakta_dogrula_en(dict(a, metin_en=a["metin_en"].replace("enforced", "enforce")), pv)
    assert A.kaynakta_dogrula_en(dict(a, pdf_sayfa_en="21", basili_sayfa_en="21"), pv)
    kitap = kaynak_sayfalari("A_Fairer_World_is_Possible_EN.pdf")
    a = banka["kitap-4"]
    # Basılı sayfadaki kısa tire (–); metin katmanındaki OCR uzun tiresi (—) kabul edilmez
    assert "members – one" in a["metin_en"]
    assert A.kaynakta_dogrula_en(dict(a, metin_en=a["metin_en"].replace("–", "—")), kitap)
    assert A.kaynakta_dogrula_en(dict(a, bolum_en="Part II: A United Nations Reform"), kitap)
    a = banka["kitap-6"]
    assert A.kaynakta_dogrula_en(dict(a, bolum_en="Introduction"), kitap)


def test_ocr_duzeltmesi_tam_bir_kez_ve_yalnizca_orada(kaynak_sayfalari):
    """İngilizce kitabın metin katmanı OCR: tek düzeltme PDF s. 34'te (basılı 32), sayfa görüntüsündeki kısa tire."""
    from conftest import CALISMA
    assert A.OCR_DUZELTMELERI == {("A_Fairer_World_is_Possible_EN.pdf", 34): [("permanent members — one", "permanent members – one")]}
    duzeltilmis = kaynak_sayfalari("A_Fairer_World_is_Possible_EN.pdf")
    ham = A.pdf_sayfalari(CALISMA / "A_Fairer_World_is_Possible_EN.pdf")
    farkli = [i for i in range(len(ham)) if ham[i] != duzeltilmis[i]]
    assert farkli == [34]
    assert ham[34].count("permanent members — one") == 1 and ham[34].replace("—", "–") == duzeltilmis[34].replace("—", "–")


def test_iki_sayfaya_yayilan_alinti(kaynak_sayfalari):
    """kitap-7 basılı s. 184–185'e yayılır ("Secu-/rity"): iki sayfanın hiçbirinde tek başına yok, birleşik gövdede var."""
    kitap = kaynak_sayfalari("A_Fairer_World_is_Possible_EN.pdf")
    a = next(x for x in ALINTILAR if x["id"] == "kitap-7")
    assert a["pdf_sayfa_en"] == "186–187"
    assert not A.sayfada_mi(a["metin_en"], kitap[186]) and not A.sayfada_mi(a["metin_en"], kitap[187])
    assert A.sayfada_mi(a["metin_en"], A.sayfa_metni(kitap, "186–187"))
    with pytest.raises(ValueError):
        A.sayfa_araligi("186–188")


def test_ingilizce_kitapta_basili_sayfa_pdf_sayfasindan_iki_eksik(kaynak_sayfalari):
    kitap = kaynak_sayfalari("A_Fairer_World_is_Possible_EN.pdf")
    tutan, tutmayan = 0, []
    for i in range(1, len(kitap)):
        satirlar = [x.strip() for x in kitap[i].splitlines() if x.strip()]
        if satirlar and re.fullmatch(r"\d{1,3}", satirlar[-1]):
            if int(satirlar[-1]) == i - 2:
                tutan += 1
            else:
                tutmayan.append((i, satirlar[-1]))
    assert tutan == 162 and tutmayan == [(155, "133")]  # PDF s. 155: OCR "153"ü "133" okuyor


def test_2019_ingilizce_kitapcik_ve_pv(kaynak_sayfalari):
    """2019-1 İngilizce kitapçıkta, Türkçe kitapçıkla aynı basılı sayfada (s. 6). 2019-2 kitapçıkta yok (hazırlanmış metin);
    İngilizcesi A/74/PV.3'ten. Kayıttaki konuşma Türkçe yapıldı ve İngilizcesi delegasyonun verdiği tercümedir."""
    kitapcik = A.normalize(" ".join(kaynak_sayfalari("Birlesmis_Milletler_EN_2019.pdf")))
    assert "Today, in your presence, I say again: The world is bigger than five!" in kitapcik
    assert "resolutions being activated" not in kitapcik and "what purpose does the United Nations serve" not in kitapcik
    pv = kaynak_sayfalari("A_74_PV.3.pdf")
    assert "President Erdoğan (spoke in Turkish; English interpretation provided by the delegation):" in A.normalize(pv[19])
    assert "22/60" in pv[22]


def test_karma_dogrulama_kaynak_olmadan_kayitla(tmp_path):
    """Kaynakların hiçbiri yerelde değilken (açık depo) her iki dil kayıtla karşılaştırılır; İngilizce metni değişen alıntı
    reddedilir ve kayıt yazılmaz."""
    import shutil
    (tmp_path / "kaynaklar").mkdir()
    for ad in ("alintilar.csv", "alintilar_dogrulama.csv", "KAYNAKLAR.md"):
        shutil.copy(KOK / "kaynaklar" / ad, tmp_path / "kaynaklar" / ad)
    alintilar, hatalar, yontem = A.dogrula(tmp_path)
    assert hatalar == [] and yontem == "doğrulama kaydından"
    kayit_once = (tmp_path / "kaynaklar/alintilar_dogrulama.csv").read_bytes()
    yol = tmp_path / "kaynaklar/alintilar.csv"
    yol.write_text(yol.read_text(encoding="utf-8").replace("what purpose does", "what purpose do"), encoding="utf-8")
    _, hatalar, _ = A.dogrula(tmp_path)
    assert hatalar == ["2019-2: İngilizce metin doğrulama kaydındakinden farklı ya da kaydı yok (A_74_PV.3.pdf yerelde değil)"]
    assert (tmp_path / "kaynaklar/alintilar_dogrulama.csv").read_bytes() == kayit_once


def test_atlama_isaretiyle_ayrilan_parcalar_ayri_ayri_aranir():
    metin = "Birinci parça burada. Arada atlanan bir cümle var. İkinci parça da burada."
    assert A.parcalar("Birinci parça … İkinci parça") == ["Birinci parça", "İkinci parça"]
    assert A.parcalar("Atlamasız alıntı.") == ["Atlamasız alıntı."]
    assert A.yerlesimler("Birinci parça burada. … İkinci parça da burada.", metin) == [0]
    assert A.yerlesimler("İkinci parça … Birinci parça", metin) == []  # sırası kaynaktaki gibi olmalı
    assert A.yerlesimler("Birinci parça … Üçüncü parça", metin) == []  # her parça kelimesi kelimesine geçmeli
    uzak = "Birinci parça. " + "atlanan " * 60 + "İkinci parça."
    assert A.yerlesimler("Birinci parça. … İkinci parça.", uzak) == []  # atlanan metin ATLAMA_PAYI'ndan uzun: aynı pasaj değil


HIKAYE = (KOK / "web/hikaye.html").read_text(encoding="utf-8")
KISA = json.loads(re.search(r"const KISA = (\{.*?\});", HIKAYE)[1])


@pytest.mark.parametrize("kimlik", sorted(KISA))
def test_hikayedeki_kisaltilmis_alinti_kaynakta_parca_parca(kimlik, calisma_metni):
    """Hikâyedeki kısa biçim: atlama işaretiyle ayrılan her parça kaynakta ayrı ayrı, kelimesi kelimesine, sırasıyla ve
    aynı pasajda; bölüm başlığı da tutar. Bir harfi değişen ya da sırası bozulan biçim reddedilir."""
    a = next(x for x in ALINTILAR if x["id"] == kimlik)
    sayfalar = [""] + calisma_metni(a["kaynak"], ham=True).split("\f")
    kisa = dict(a, metin_tr=KISA[kimlik])
    assert A.kaynakta_dogrula(kisa, sayfalar) == []
    son = A.parcalar(KISA[kimlik])[-1]
    assert A.kaynakta_dogrula(dict(a, metin_tr=KISA[kimlik].replace(son, son[:-2] + "x.")), sayfalar)
    assert A.kaynakta_dogrula(dict(a, metin_tr=" … ".join(reversed(KISA[kimlik].split(" … ")))), sayfalar)


def test_metinde_olmayan_alinti_reddedilir(calisma_metni):
    sayfalar = [""] + calisma_metni("BM2026-2022-web.pdf", ham=True).split("\f")
    a = copy.deepcopy(next(x for x in KONUSMA if x["id"] == "2026-1"))
    a["metin_tr"] = a["metin_tr"].replace("190’dan", "200’den")
    assert A.kaynakta_dogrula(a, sayfalar)
    a = copy.deepcopy(next(x for x in KONUSMA if x["id"] == "2026-1"))
    a["pdf_sayfa"] = "18"
    assert A.kaynakta_dogrula(a, sayfalar)


def test_2025_son_sayfa_dizgi_cakismasi(calisma_metni):
    """
    Derlemenin 2025 Türkçe bölümünün son sayfası (PDF s. 50, basılı 49): metin katmanında
    konuşmanın son satırlarına önsözün metni karışıyor (sayfa görüntüsünde yalnızca konuşma var).
    Bu sayfadaki alıntı, karışmanın başladığı yerden önce bitmeli ve önsöz parçası içermemeli.
    """
    sayfa = A.normalize(calisma_metni("BM2026-2022-web.pdf", ham=True).split("\f")[49])
    karisma = sayfa.index("Türkiye olarak tüm çabamız")  # önsözün cümlesi; görüntüde bu sayfada yok
    for a in KONUSMA:
        if a["kaynak"] == "BM2026-2022-web.pdf" and a["pdf_sayfa"] == "50":
            konum = sayfa.index(A.normalize(a["metin_tr"]))
            assert konum + len(A.normalize(a["metin_tr"])) <= karisma, a["id"]
            for parca in ("Elinizdeki", "Kitabın hazırlanmasında", "kakların", "soğuk"):
                assert parca not in a["metin_tr"], (a["id"], parca)
    # İngilizce karşılığının sayfası (PDF s. 152) bu sorundan etkilenmiyor: önsözün İngilizcesi karışmıyor
    en = A.normalize(calisma_metni("BM2026-2022-web.pdf", ham=True).split("\f")[151])
    assert "Our duty is not to abandon the system" in en and "foreword" not in en.lower()


def test_derlemede_basili_sayfa_pdf_sayfasindan_bir_eksik(calisma_metni):
    sayfalar = calisma_metni("BM2026-2022-web.pdf", ham=True).split("\f")
    # Türkçe ve İngilizce bölümlerde sayfa başlığındaki basılı numara = PDF sayfası - 1
    import re
    sinanan = 0
    for i, s in enumerate(sayfalar[:209], start=1):
        d = A.normalize(s).replace("G E NE L", "GENEL").replace("HI TA P LA R I", "HITAPLARI")
        for n in re.findall(r"HITAPLARI (\d{1,3})\b|N.S (\d{1,3}) ADDRESSES", d):
            sayi = int(n[0] or n[1])
            assert sayi == i - 1, (i, sayi)
            sinanan += 1
    assert sinanan > 40


def test_reform_tablosundaki_kitap_ifadeleri_dogrulanmis_alintilardan():
    """Karşılaştırma tablosunda kitaptan tırnak içinde verilen her ifade, doğrulanmış bir alıntıda birebir geçer."""
    import re
    with open(KOK / "kaynaklar/reform_modelleri.csv", encoding="utf-8", newline="") as f:
        satirlar = [s for s in csv.DictReader(f) if s["model"] == "Daha Adil Bir Dünya Mümkün"]
    assert {s["olcut"] for s in satirlar} == {"toplam", "yeni_daimi", "veto", "genel_kurul"}
    alintilar = " ".join(A.normalize(a["metin_tr"]) for a in KITAP)
    for s in satirlar:
        for ifade in re.findall(r"“(.+?)”", s["tr"]):
            assert A.normalize(ifade) in alintilar, (s["olcut"], ifade)
        # Kitapta sayfa numarası yok: dayanak yalnızca bölüm başlığı
        assert not re.search(r"\b(s|p|sayfa|page)\.? ?\d", s["dayanak"] + s["tr"]), s["olcut"]


def test_hitaplar_arasinda_donemleri_yalnizca_hitaplardan():
    """ADIM 46: "Hitaplar arasında" tablosunun dönem sınırları yalnızca Genel Kurul hitaplarıdır; kitap alıntısı (kitap-8, tarih
    2021-09, bölüm alanı dolu) Söz ve Kayıt listesinde durur ama sınır sayılmaz. İlk dönem, tablonun açıklamasındaki gibi,
    24 Eylül 2019 – 20 Eylül 2022 (8 öneri, 12 ret oyu)."""
    sayfa = (KOK / "web/vizyon.html").read_text(encoding="utf-8")
    assert "const hitaplar = [...new Set(konusmalar.filter((a) => !a.bolum).map((a) => a.tarih))].sort();" in sayfa
    assert "2020 ve 2021 hitapları kaynaklarda bulunmadığı için ilk dönem 2019 ile 2022 hitapları arasıdır." in sayfa
    s = (KOK / "web/veri.js").read_text(encoding="utf-8")
    V = json.loads(s[s.index("{"):s.rstrip().rindex(";")])
    konusmalar = [a for a in V["alintilar"] if a["iliskili_veri"] not in ("model", "giris")]
    assert [a["id"] for a in konusmalar if a.get("bolum")] == ["kitap-8"] and next(a for a in konusmalar if a.get("bolum"))["tarih"] == "2021-09"
    hitaplar = sorted({a["tarih"] for a in konusmalar if not a.get("bolum")})
    assert hitaplar[:2] == ["2019-09-24", "2022-09-20"] and "2021-09" not in hitaplar
    ilk = [k for k in V["kayitlar"] if hitaplar[0] < k["tarih"] <= hitaplar[1]]
    assert len(ilk) == 8 and sum(len(k["uyeler"]) for k in ilk if not k["kapali"]) == 12
