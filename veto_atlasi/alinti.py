"""
Alıntı bankası (kaynaklar/alintilar.csv) ve doğrulaması.

Her alıntı, kaynağın metin katmanında belirtilen PDF sayfasında kelimesi kelimesine geçmelidir.
Karşılaştırma öncesi iki taraf da aynı biçimde normalize edilir: Unicode NFC, yumuşak tire
silinir, satır sonundaki heceleme tiresi (küçük harfle devam eden) birleştirilir, bütün boşluk ve
satır sonları tek boşluğa indirgenir. Başka hiçbir dönüşüm (tırnak, kesme işareti, büyük-küçük
harf) yapılmaz.

Atlama işaretiyle (…) kısaltılmış alıntıda her parça kaynakta ayrı ayrı ve kelimesi kelimesine aranır; parçalar
kaynaktaki sırasıyla ve aynı pasajdan gelmelidir (iki parça arasında atlanan metin en fazla ATLAMA_PAYI karakter).

Kaynak dosyalar depoda değildir (kaynaklar/calisma_metinleri/, .gitignore). Bu yüzden doğrulama
sonucu kaynaklar/alintilar_dogrulama.csv dosyasına yazılır: alıntı metinlerinin ve kaynağın
SHA-256 özetleri. Kaynaklar yerelde yoksa 04 betiği alıntıları bu kayda göre kabul eder; metni
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

ALANLAR = ["id", "tarih", "etkinlik", "metin_tr", "metin_en", "kaynak", "basili_sayfa", "pdf_sayfa",
           "basili_sayfa_en", "pdf_sayfa_en", "bolum", "iliskili_veri"]
KAYIT_ALANLARI = ["id", "kaynak", "kaynak_sha256", "pdf_sayfa", "metin_tr_sha256", "pdf_sayfa_en", "metin_en_sha256"]
# Basılı sayfa = PDF sayfası - fark (kaynak bazında; doğrulama notu KAYNAKLAR.md'de)
SAYFA_FARKI = {"Birlesmis_milletler_konuşması2019.pdf": 2, "BM2026-2022-web.pdf": 1}
# Basılı sayfa numarası taşımayan kaynak: sayfa numarası hiç yazılmaz, atıf bölüm başlığıyla
BOLUMLE_ATIF = {"DahaAdilBirDünyaMümkün.pdf"}


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


def bicim_hatalari(a: dict) -> list[str]:
    """Kaynağa bakmadan denetlenebilen kurallar."""
    h = []
    if not a["metin_tr"].strip():
        h.append("metin_tr boş")
    if a["kaynak"] in BOLUMLE_ATIF:
        if any(a[k] for k in ("basili_sayfa", "pdf_sayfa", "basili_sayfa_en", "pdf_sayfa_en")):
            h.append("bu kaynakta sayfa numarası yazılmaz; atıf yalnızca bölüm başlığıyla")
        if not a["bolum"]:
            h.append("bölüm başlığı yok")
        if a["metin_en"]:
            h.append("kitap alıntısının İngilizcesi boş bırakılır")
    else:
        fark = SAYFA_FARKI[a["kaynak"]]
        if not a["pdf_sayfa"] or int(a["basili_sayfa"]) != int(a["pdf_sayfa"]) - fark:
            h.append(f"basılı sayfa PDF sayfasından {fark} eksik olmalı")
        if a["metin_en"] and (not a["pdf_sayfa_en"] or int(a["basili_sayfa_en"]) != int(a["pdf_sayfa_en"]) - fark):
            h.append("İngilizce metnin sayfası eksik ya da tutarsız")
        if not a["metin_en"] and (a["pdf_sayfa_en"] or a["basili_sayfa_en"]):
            h.append("İngilizcesi olmayan alıntıda İngilizce sayfa var")
    return h


def pdf_sayfalari(yol: Path) -> list[str]:
    """PDF'in metin katmanı, sayfa sayfa (1'den başlayan dizin için [0] boş)."""
    if not shutil.which("pdftotext"):
        raise FileNotFoundError("pdftotext kurulu değil")
    cikti = subprocess.run(["pdftotext", "-enc", "UTF-8", str(yol), "-"], capture_output=True, check=True).stdout
    return [""] + cikti.decode("utf-8").split("\f")


# Kitabın bölümleri: metin katmanında bölümün ilk sayfasının başladığı ifade -> bölüm başlığı
KITAP_BOLUMLERI = [
    ("Ön Söz ", "Ön Söz"),
    ("Giriş ", "Giriş"),
    ("1. BÖLÜM Uluslararası Siyasette Çifte Standart ve BM’nin Reform İhtiyacı ",
     "1. Bölüm: Uluslararası Siyasette Çifte Standart ve BM’nin Reform İhtiyacı"),
    ("2. BÖLÜM Birleşmiş Milletler Reformu ", "2. Bölüm: Birleşmiş Milletler Reformu"),
    ("Sonuç ", "Sonuç"),
]


def kitap_bolumu(sayfalar: list[str], pdf_sayfa: int) -> str:
    """Bir sayfanın içinde bulunduğu kitap bölümü (bölümlerin başladığı sayfalardan)."""
    bolum = ""
    for i in range(1, pdf_sayfa + 1):
        s = normalize(sayfalar[i])
        for baslangic, ad in KITAP_BOLUMLERI:
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
    """Kaynak yerelde: alıntının belirtilen sayfada birebir geçtiğini denetler."""
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
    else:
        if not sayfada_mi(a["metin_tr"], sayfalar[int(a["pdf_sayfa"])]):
            h.append(f"metin_tr PDF s. {a['pdf_sayfa']} metninde birebir yok")
        if a["metin_en"] and not sayfada_mi(a["metin_en"], sayfalar[int(a["pdf_sayfa_en"])]):
            h.append(f"metin_en PDF s. {a['pdf_sayfa_en']} metninde birebir yok")
    return h


def dogrulama_kaydi(alintilar: list[dict], kaynak_sha: dict[str, str]) -> list[dict]:
    return [{"id": a["id"], "kaynak": a["kaynak"], "kaynak_sha256": kaynak_sha[a["kaynak"]],
             "pdf_sayfa": a["pdf_sayfa"], "metin_tr_sha256": ozet(a["metin_tr"]),
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
        beklenen = dogrulama_kaydi([a], {a["kaynak"]: k["kaynak_sha256"]})[0]
        if beklenen != k:
            h.append(f"{a['id']}: metin ya da sayfa doğrulama kaydındakinden farklı")
    return h


def calisma_metinleri_sha(kok: Path) -> dict[str, str]:
    """KAYNAKLAR.md 'Çalışma metinleri' tablosu: dosya adı -> SHA-256."""
    s = (kok / "kaynaklar/KAYNAKLAR.md").read_text(encoding="utf-8")
    bolum = s[s.index("## Çalışma metinleri"):]
    bolum = bolum[:bolum.index("\n## ", 3)]
    return {m[1]: m[2] for m in re.finditer(r"^\| `([^`]+)` \|.*\| `([0-9a-f]{64})` \|$", bolum, re.M)}


def dogrula(kok: Path) -> tuple[list[dict], list[str], str]:
    """
    Alıntıları okur ve doğrular. Döndürür: (alıntılar, hatalar, yöntem).
    Kaynakların hepsi yerelde ve özetleri tutuyorsa metinden doğrular ve kaydı yeniler;
    değilse doğrulama kaydıyla karşılaştırır.
    """
    alintilar = oku(kok / "kaynaklar/alintilar.csv")
    hatalar = [f"{a['id']}: {h}" for a in alintilar for h in bicim_hatalari(a)]
    beklenen_sha = calisma_metinleri_sha(kok)
    klasor = kok / "kaynaklar/calisma_metinleri"
    gerekli = sorted({a["kaynak"] for a in alintilar})
    yerel = {}
    for ad in gerekli:
        yol = klasor / ad
        if yol.exists() and hashlib.sha256(yol.read_bytes()).hexdigest() == beklenen_sha.get(ad):
            yerel[ad] = yol
    kayit_yolu = kok / "kaynaklar/alintilar_dogrulama.csv"
    if len(yerel) == len(gerekli) and shutil.which("pdftotext"):
        sayfa_onbellek = {ad: pdf_sayfalari(yol) for ad, yol in yerel.items()}
        for a in alintilar:
            hatalar += [f"{a['id']}: {h}" for h in kaynakta_dogrula(a, sayfa_onbellek[a["kaynak"]])]
        if not hatalar:
            with open(kayit_yolu, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=KAYIT_ALANLARI, lineterminator="\n")
                w.writeheader()
                w.writerows(dogrulama_kaydi(alintilar, beklenen_sha))
        return alintilar, hatalar, "kaynak metinden"
    if not kayit_yolu.exists():
        return alintilar, hatalar + ["kaynaklar yerelde yok ve doğrulama kaydı bulunmuyor"], "yok"
    with open(kayit_yolu, encoding="utf-8", newline="") as f:
        kayit = list(csv.DictReader(f))
    return alintilar, hatalar + kayitla_karsilastir(alintilar, kayit), "doğrulama kaydından"
