"""
Alıntı bankası (kaynaklar/alintilar.csv) ve doğrulaması.

Her alıntı, kaynağın metin katmanında belirtilen PDF sayfasında kelimesi kelimesine geçmelidir. Türkçe metin
(metin_tr) `kaynak`ta, resmî İngilizce metin (metin_en) `kaynak_en`de aranır; iki dil ayrı kaynaklardan gelebilir
(2019 hitabı: Türkçe ve İngilizce kitapçıklar ya da BM toplantı kaydı; kitap: Türkçe ve İngilizce baskılar).
Karşılaştırma öncesi iki taraf da aynı biçimde normalize edilir: Unicode NFC, yumuşak tire
silinir, satır sonundaki heceleme tiresi (küçük harfle devam eden) birleştirilir, bütün boşluk ve
satır sonları tek boşluğa indirgenir. Başka hiçbir dönüşüm (tırnak, kesme işareti, büyük-küçük
harf) yapılmaz. Taranmış kaynağın metin katmanı (OCR) yalnızca OCR_DUZELTMELERI'ndeki, sayfa görüntüsüyle
karşılaştırılmış yerlerde düzeltilir.

Resmî İngilizcesi bulunamayan alıntıda metin_en boş kalır; İngilizce sayfalarda Türkçe özgün metin ve altında
"Unofficial translation by Veto Atlas" etiketli çeviri (ceviri_en) gösterilir. Çeviri bir kaynağa karşı doğrulanmaz.

Atlama işaretiyle (…) kısaltılmış alıntıda her parça kaynakta ayrı ayrı ve kelimesi kelimesine aranır; parçalar
kaynaktaki sırasıyla ve aynı pasajdan gelmelidir (iki parça arasında atlanan metin en fazla ATLAMA_PAYI karakter).

Kaynak dosyalar depoda değildir (kaynaklar/calisma_metinleri/ ve BM belgeleri için kaynaklar/.belgeler/, .gitignore).
Bu yüzden doğrulama sonucu kaynaklar/alintilar_dogrulama.csv dosyasına yazılır: alıntı metinlerinin ve kaynakların
SHA-256 özetleri. Kaynak yerelde yoksa 04 betiği o kaynaktan gelen metni bu kayda göre kabul eder; metni
kayıttakinden farklı olan ya da kaydı bulunmayan alıntı sisteme giremez.
"""
from __future__ import annotations

import csv
import hashlib
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

ALANLAR = ["id", "tarih", "etkinlik", "metin_tr", "metin_en", "ceviri_en", "kaynak", "basili_sayfa", "pdf_sayfa",
           "kaynak_en", "belge_en", "basili_sayfa_en", "pdf_sayfa_en", "bolum", "bolum_en", "iliskili_veri"]
KAYIT_ALANLARI = ["id", "kaynak", "kaynak_sha256", "pdf_sayfa", "metin_tr_sha256",
                  "kaynak_en", "kaynak_en_sha256", "pdf_sayfa_en", "metin_en_sha256"]
KAYIT_TR = ("kaynak", "kaynak_sha256", "pdf_sayfa", "metin_tr_sha256")
KAYIT_EN = ("kaynak_en", "kaynak_en_sha256", "pdf_sayfa_en", "metin_en_sha256")
# Basılı sayfa = PDF sayfası - fark (kaynak bazında; doğrulama notu KAYNAKLAR.md'de). BM toplantı kaydında sayfa
# numarası PDF sayfasıdır ("22/60").
SAYFA_FARKI = {"Birlesmis_milletler_konuşması2019.pdf": 2, "BM2026-2022-web.pdf": 1,
               "Birlesmis_Milletler_EN_2019.pdf": 2, "A_Fairer_World_is_Possible_EN.pdf": 2, "A_74_PV.3.pdf": 0}
# Basılı sayfa numarası taşımayan kaynak: sayfa numarası hiç yazılmaz, atıf bölüm başlığıyla
BOLUMLE_ATIF = {"DahaAdilBirDünyaMümkün.pdf"}
# İngilizce metni bir BM belgesinden gelen alıntıda künyede belge simgesi sayfadan önce yazılır (belge_en)
BELGE_SIMGESI = {"A_74_PV.3.pdf": "A/74/PV.3"}
# Taranmış kaynağın metin katmanında, sayfa görüntüsüyle karşılaştırılarak düzeltilen yerler: (kaynak, PDF sayfası) ->
# [(OCR'ın okuduğu, basılı sayfadaki)]. Her düzeltme sayfada tam bir kez geçmelidir. İngilizce kitap: basılı sayfadaki
# boşluklu kısa tireyi (–) OCR uzun tire (—) okuyor (s. 32).
OCR_DUZELTMELERI = {("A_Fairer_World_is_Possible_EN.pdf", 34): [("permanent members — one", "permanent members – one")]}


def normalize(metin: str) -> str:
    metin = unicodedata.normalize("NFC", metin).replace("­", "")
    metin = re.sub(r"(\w)-\s*\n\s*(?=[a-zçğıöşü])", r"\1", metin)
    return " ".join(metin.split())


def ozet(metin: str) -> str:
    return hashlib.sha256(normalize(metin).encode("utf-8")).hexdigest()


def oku(yol: Path) -> list[dict]:
    with open(yol, encoding="utf-8", newline="") as f:
        satirlar = list(csv.DictReader(f))
    if satirlar and list(satirlar[0].keys()) != ALANLAR:
        raise ValueError(f"{yol.name} sütunları beklenenden farklı: {list(satirlar[0].keys())}")
    kimlikler = [s["id"] for s in satirlar]
    if len(set(kimlikler)) != len(kimlikler):
        raise ValueError(f"{yol.name}: yinelenen alıntı kimliği")
    return satirlar


def sayfa_araligi(deger: str) -> tuple[int, int]:
    """'22' -> (22, 22); iki sayfaya yayılan alıntı '186–187' -> (186, 187)."""
    p = [int(x) for x in re.split("[–-]", deger)]
    if len(p) == 1:
        return p[0], p[0]
    if len(p) != 2 or p[1] != p[0] + 1:
        raise ValueError(f"sayfa aralığı ardışık iki sayfa olmalı: {deger}")
    return p[0], p[1]


def _sayfalar_tutarli(basili: str, pdf: str, fark: int) -> bool:
    try:
        b, p = sayfa_araligi(basili), sayfa_araligi(pdf)
    except ValueError:
        return False
    return b == (p[0] - fark, p[1] - fark)


def bicim_hatalari(a: dict) -> list[str]:
    """Kaynağa bakmadan denetlenebilen kurallar."""
    h = []
    if not a["metin_tr"].strip():
        h.append("metin_tr boş")
    if a["kaynak"] in BOLUMLE_ATIF:
        if a["basili_sayfa"] or a["pdf_sayfa"]:
            h.append("bu kaynakta Türkçe metne sayfa numarası yazılmaz; atıf yalnızca bölüm başlığıyla")
        if not a["bolum"]:
            h.append("bölüm başlığı yok")
    else:
        fark = SAYFA_FARKI[a["kaynak"]]
        if not a["pdf_sayfa"] or not _sayfalar_tutarli(a["basili_sayfa"], a["pdf_sayfa"], fark):
            h.append(f"basılı sayfa PDF sayfasından {fark} eksik olmalı")
    # İngilizcede ya resmî metin (kaynağa karşı doğrulanır) ya da açıkça işaretli gayriresmî çeviri bulunur
    if bool(a["metin_en"]) == bool(a["ceviri_en"]):
        h.append("İngilizcede ya resmî metin (metin_en) ya da gayriresmî çeviri (ceviri_en) bulunur, ikisi birden değil")
    if a["metin_en"]:
        if a["kaynak_en"] not in SAYFA_FARKI:
            h.append("İngilizce metnin kaynağı yok ya da tanımsız")
        elif not a["pdf_sayfa_en"] or not _sayfalar_tutarli(a["basili_sayfa_en"], a["pdf_sayfa_en"], SAYFA_FARKI[a["kaynak_en"]]):
            h.append("İngilizce metnin sayfası eksik ya da tutarsız")
        if a["belge_en"] != BELGE_SIMGESI.get(a["kaynak_en"], ""):
            h.append("belge simgesi İngilizce kaynakla tutmuyor")
        if bool(a["bolum_en"]) != (a["kaynak"] in BOLUMLE_ATIF):
            h.append("İngilizce bölüm başlığı yalnızca kitap alıntısında ve orada zorunlu")
    elif any(a[k] for k in ("kaynak_en", "belge_en", "basili_sayfa_en", "pdf_sayfa_en", "bolum_en")):
        h.append("resmî İngilizcesi olmayan alıntıda İngilizce kaynak alanları boş kalır")
    return h


def pdf_sayfalari(yol: Path) -> list[str]:
    """PDF'in metin katmanı, sayfa sayfa (1'den başlayan dizin için [0] boş)."""
    if not shutil.which("pdftotext"):
        raise FileNotFoundError("pdftotext kurulu değil")
    cikti = subprocess.run(["pdftotext", "-enc", "UTF-8", str(yol), "-"], capture_output=True, check=True).stdout
    return [""] + cikti.decode("utf-8").split("\f")


def kaynak_sayfalari(ad: str, yol: Path) -> list[str]:
    """Kaynağın metin katmanı, OCR_DUZELTMELERI uygulanmış olarak. Düzeltilecek metin sayfada tam bir kez geçmezse durur."""
    sayfalar = pdf_sayfalari(yol)
    for (kaynak, sayfa), duzeltmeler in OCR_DUZELTMELERI.items():
        if kaynak != ad:
            continue
        for eski, yeni in duzeltmeler:
            if sayfalar[sayfa].count(eski) != 1:
                raise ValueError(f"OCR düzeltmesi uygulanamadı: {ad} PDF s. {sayfa}: {eski!r}")
            sayfalar[sayfa] = sayfalar[sayfa].replace(eski, yeni)
    return sayfalar


def _govde(sayfa: str) -> str:
    """Sayfanın gövdesi: baştaki büyük harfli sayfa başlığı ve sondaki sayfa numarası satırı çıkarılır."""
    satirlar = sayfa.split("\n")
    dolu = [i for i, x in enumerate(satirlar) if x.strip()]
    if dolu and re.fullmatch(r"\d{1,4}", satirlar[dolu[-1]].strip()):
        del satirlar[dolu[-1]]
    if dolu and not re.search(r"[a-zçğıöşü]", satirlar[dolu[0]]):
        del satirlar[dolu[0]]
    return "\n".join(satirlar).strip("\n")


def sayfa_metni(sayfalar: list[str], aralik: str) -> str:
    """Tek sayfa ya da iki sayfaya yayılan alıntı için birleştirilmiş gövde (satır sonu hecelemesi normalize'da birleşir)."""
    bas, son = sayfa_araligi(aralik)
    if bas == son:
        return sayfalar[bas]
    return "\n".join(_govde(sayfalar[i]) for i in range(bas, son + 1))


# Kitabın bölümleri: metin katmanında bölümün ilk sayfasının başladığı ifade -> bölüm başlığı
KITAP_BOLUMLERI = [
    ("Ön Söz ", "Ön Söz"),
    ("Giriş ", "Giriş"),
    ("1. BÖLÜM Uluslararası Siyasette Çifte Standart ve BM’nin Reform İhtiyacı ",
     "1. Bölüm: Uluslararası Siyasette Çifte Standart ve BM’nin Reform İhtiyacı"),
    ("2. BÖLÜM Birleşmiş Milletler Reformu ", "2. Bölüm: Birleşmiş Milletler Reformu"),
    ("Sonuç ", "Sonuç"),
]
# İngilizce baskı (A Fairer World is Possible). "PART |": metin katmanı (OCR) "PART I"i böyle okur.
KITAP_BOLUMLERI_EN = [
    ("Foreword ", "Foreword"),
    ("Introduction ", "Introduction"),
    ("PART | Double Standards in International Politics and the Need for a UN Reform ",
     "Part I: Double Standards in International Politics and the Need for a UN Reform"),
    ("PART II A United Nations Reform ", "Part II: A United Nations Reform"),
    ("Conclusion ", "Conclusion"),
]


def kitap_bolumu(sayfalar: list[str], pdf_sayfa: int, bolumler: list[tuple[str, str]] = KITAP_BOLUMLERI) -> str:
    """Bir sayfanın içinde bulunduğu kitap bölümü (bölümlerin başladığı sayfalardan)."""
    bolum = ""
    for i in range(1, pdf_sayfa + 1):
        s = normalize(sayfalar[i])
        for baslangic, ad in bolumler:
            if s.startswith(baslangic):
                bolum = ad
    return bolum


ATLAMA = "…"
ATLAMA_PAYI = 400  # iki parça arasında atlanan metin en fazla bu kadar karakter: parçalar aynı pasajdan


def parcalar(alinti: str) -> list[str]:
    """Atlama işaretiyle (…) ayrılan parçalar, normalize edilmiş; işaretsiz alıntı tek parçadır."""
    return [normalize(p) for p in alinti.split(ATLAMA) if p.strip()]


def yerlesimler(alinti: str, metin: str) -> list[int]:
    """Alıntının metinde geçtiği yerler (normalize edilmiş metinde başlangıç konumları). Her parça ayrı ayrı ve kelimesi
    kelimesine aranır; sonraki parça bir öncekinin bittiği yerden sonra ve en fazla ATLAMA_PAYI karakter ötede başlar."""
    p, m = parcalar(alinti), normalize(metin)
    if not p:
        return []
    sonuc = []
    i = m.find(p[0])
    while i != -1:
        son, tamam = i + len(p[0]), True
        for parca in p[1:]:
            j = m.find(parca, son)
            if j == -1 or j - son > ATLAMA_PAYI:
                tamam = False
                break
            son = j + len(parca)
        if tamam:
            sonuc.append(i)
        i = m.find(p[0], i + 1)
    return sonuc


def sayfada_mi(alinti: str, sayfa_metni: str) -> bool:
    return bool(yerlesimler(alinti, sayfa_metni))


def kaynakta_dogrula(a: dict, sayfalar: list[str]) -> list[str]:
    """Türkçe kaynak yerelde: metin_tr'nin belirtilen sayfada (kitapta bütün metinde, tek yerde) birebir geçtiğini denetler."""
    h = []
    if a["kaynak"] in BOLUMLE_ATIF:
        # Sayfa yazılmadığı için bütün metinde aranır; tek bir yerde geçmeli
        n = len(yerlesimler(a["metin_tr"], "\n".join(sayfalar)))
        if n != 1:
            h.append(f"metin_tr kitapta {n} kez geçiyor (1 olmalı)")
        else:
            konum = next(i for i in range(1, len(sayfalar)) if sayfada_mi(a["metin_tr"], sayfalar[i])) \
                if any(sayfada_mi(a["metin_tr"], s) for s in sayfalar[1:]) else None
            if konum is None:
                h.append("metin_tr bir sayfa sınırını aşıyor")
            elif kitap_bolumu(sayfalar, konum) != a["bolum"]:
                h.append(f"bölüm başlığı tutmuyor: metinde '{kitap_bolumu(sayfalar, konum)}'")
    elif not sayfada_mi(a["metin_tr"], sayfalar[int(a["pdf_sayfa"])]):
        h.append(f"metin_tr PDF s. {a['pdf_sayfa']} metninde birebir yok")
    return h


def kaynakta_dogrula_en(a: dict, sayfalar: list[str]) -> list[str]:
    """İngilizce kaynak (kaynak_en) yerelde: metin_en'in belirtilen sayfada (ya da iki sayfada) birebir geçtiğini ve
    kitapta bölüm başlığının tuttuğunu denetler."""
    h = []
    if not sayfada_mi(a["metin_en"], sayfa_metni(sayfalar, a["pdf_sayfa_en"])):
        h.append(f"metin_en {a['kaynak_en']} PDF s. {a['pdf_sayfa_en']} metninde birebir yok")
    if a["bolum_en"]:
        bolum = kitap_bolumu(sayfalar, sayfa_araligi(a["pdf_sayfa_en"])[0], KITAP_BOLUMLERI_EN)
        if bolum != a["bolum_en"]:
            h.append(f"İngilizce bölüm başlığı tutmuyor: metinde '{bolum}'")
    return h


def dogrulama_kaydi(alintilar: list[dict], kaynak_sha: dict[str, str]) -> list[dict]:
    return [{"id": a["id"], "kaynak": a["kaynak"], "kaynak_sha256": kaynak_sha[a["kaynak"]],
             "pdf_sayfa": a["pdf_sayfa"], "metin_tr_sha256": ozet(a["metin_tr"]),
             "kaynak_en": a["kaynak_en"], "kaynak_en_sha256": kaynak_sha[a["kaynak_en"]] if a["metin_en"] else "",
             "pdf_sayfa_en": a["pdf_sayfa_en"], "metin_en_sha256": ozet(a["metin_en"]) if a["metin_en"] else ""}
            for a in alintilar]


def kayitla_karsilastir(alintilar: list[dict], kayit: list[dict]) -> list[str]:
    """Kaynaklar yerelde yokken: her alıntının metni kayıttaki doğrulanmış özetle aynı olmalı."""
    idx = {k["id"]: k for k in kayit}
    h = []
    for a in alintilar:
        k = idx.get(a["id"])
        if not k:
            h.append(f"{a['id']}: doğrulama kaydı yok")
            continue
        sha = {a["kaynak"]: k["kaynak_sha256"], a["kaynak_en"]: k["kaynak_en_sha256"]}
        if dogrulama_kaydi([a], sha)[0] != k:
            h.append(f"{a['id']}: metin ya da sayfa doğrulama kaydındakinden farklı")
    return h


def _tablo(s: str, baslik: str) -> dict[str, str]:
    bolum = s[s.index(baslik):]
    bolum = bolum[:bolum.index("\n## ", 3)]
    return {m[1]: m[2] for m in re.finditer(r"^\| `([^`]+)` \|.*\| `([0-9a-f]{64})` \|$", bolum, re.M)}


def calisma_metinleri_sha(kok: Path) -> dict[str, str]:
    """KAYNAKLAR.md 'Çalışma metinleri' tablosu: dosya adı -> SHA-256."""
    return _tablo((kok / "kaynaklar/KAYNAKLAR.md").read_text(encoding="utf-8"), "## Çalışma metinleri")


def kaynak_tablosu(kok: Path) -> dict[str, tuple[Path, str]]:
    """Alıntı kaynakları: dosya adı -> (yerel yol, SHA-256). Çalışma metinleri kaynaklar/calisma_metinleri/ altında,
    BM belgeleri (KAYNAKLAR.md 'Yerel belgeler'; scripts/07_belgeleri_indir.py indirir) kaynaklar/.belgeler/ altında."""
    s = (kok / "kaynaklar/KAYNAKLAR.md").read_text(encoding="utf-8")
    tablo = {ad: (kok / "kaynaklar/.belgeler" / ad, sha) for ad, sha in _tablo(s, "## Yerel belgeler").items()}
    tablo |= {ad: (kok / "kaynaklar/calisma_metinleri" / ad, sha) for ad, sha in _tablo(s, "## Çalışma metinleri").items()}
    return tablo


def yerel_kaynaklar(kok: Path, adlar: set[str]) -> dict[str, Path]:
    """Yerelde bulunan ve özeti KAYNAKLAR.md'dekiyle tutan kaynaklar (pdftotext yoksa hiçbiri)."""
    if not shutil.which("pdftotext"):
        return {}
    tablo = kaynak_tablosu(kok)
    return {ad: tablo[ad][0] for ad in sorted(adlar) if ad in tablo and tablo[ad][0].exists()
            and hashlib.sha256(tablo[ad][0].read_bytes()).hexdigest() == tablo[ad][1]}


def dogrula(kok: Path) -> tuple[list[dict], list[str], str]:
    """
    Alıntıları okur ve doğrular. Döndürür: (alıntılar, hatalar, yöntem).
    Her alıntının Türkçe ve İngilizce metni ayrı ayrı denetlenir: kaynağı yerelde ve özeti tutuyorsa metinden, değilse
    doğrulama kaydıyla. Hata yoksa kayıt yenilenir.
    """
    alintilar = oku(kok / "kaynaklar/alintilar.csv")
    hatalar = [f"{a['id']}: {h}" for a in alintilar for h in bicim_hatalari(a)]
    tablo = kaynak_tablosu(kok)
    gerekli = {a["kaynak"] for a in alintilar} | {a["kaynak_en"] for a in alintilar if a["metin_en"]}
    hatalar += [f"{ad}: KAYNAKLAR.md'de künyesi ve SHA-256'sı yok" for ad in sorted(gerekli - set(tablo))]
    if hatalar:
        return alintilar, hatalar, "yok"
    yerel = yerel_kaynaklar(kok, gerekli)
    sayfa_onbellek = {ad: kaynak_sayfalari(ad, yol) for ad, yol in yerel.items()}
    kayit_yolu = kok / "kaynaklar/alintilar_dogrulama.csv"
    eski = {}
    if kayit_yolu.exists():
        with open(kayit_yolu, encoding="utf-8", newline="") as f:
            eski = {k["id"]: k for k in csv.DictReader(f)}
    yeni = dogrulama_kaydi(alintilar, {ad: sha for ad, (_, sha) in tablo.items()})
    for a, k in zip(alintilar, yeni):
        o = eski.get(a["id"], {})
        if a["kaynak"] in yerel:
            hatalar += [f"{a['id']}: {h}" for h in kaynakta_dogrula(a, sayfa_onbellek[a["kaynak"]])]
        elif any(o.get(f) != k[f] for f in KAYIT_TR):
            hatalar.append(f"{a['id']}: Türkçe metin doğrulama kaydındakinden farklı ya da kaydı yok ({a['kaynak']} yerelde değil)")
        if not a["metin_en"]:
            continue
        if a["kaynak_en"] in yerel:
            hatalar += [f"{a['id']}: {h}" for h in kaynakta_dogrula_en(a, sayfa_onbellek[a["kaynak_en"]])]
        elif any(o.get(f) != k[f] for f in KAYIT_EN):
            hatalar.append(f"{a['id']}: İngilizce metin doğrulama kaydındakinden farklı ya da kaydı yok ({a['kaynak_en']} yerelde değil)")
    if not hatalar:
        with open(kayit_yolu, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=KAYIT_ALANLARI, lineterminator="\n")
            w.writeheader()
            w.writerows(yeni)
    if len(yerel) == len(gerekli):
        yontem = "kaynak metinden"
    elif not yerel:
        yontem = "doğrulama kaydından"
    else:
        yontem = f"{len(yerel)}/{len(gerekli)} kaynak metinden ({', '.join(yerel)}), kalanı doğrulama kaydından"
    return alintilar, hatalar, yontem
