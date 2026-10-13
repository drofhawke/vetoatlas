"""
Yerel belgeleri (toplantı kayıtları vb. PDF) KAYNAKLAR.md "Yerel belgeler" tablosundaki adresten
indirir ve SHA-256 özetini tablodakiyle karşılaştırır. Belgeler depoya girmez (kaynaklar/.belgeler/,
.gitignore); bu betik depoyu kopyalayan herkesin aynı belgeleri aynı özetle edinmesini sağlar.

    python scripts/07_belgeleri_indir.py            # eksik ya da özeti tutmayan belgeleri indirir
    python scripts/07_belgeleri_indir.py --kontrol  # indirmez, yalnızca yerel dosyaları denetler

Özeti tutmayan indirme saklanmaz. Otomatik erişimi engellenen adres (ör. BM Dijital Kütüphanesi
boş 202 döndürür) için betik durumu bildirir; belge tarayıcıyla elle indirilip klasöre konur.
Erişim engeli aşılmaz.
"""
from __future__ import annotations

import hashlib
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
KLASOR = KOK / "kaynaklar" / ".belgeler"
KAYNAKLAR = KOK / "kaynaklar" / "KAYNAKLAR.md"
SATIR = re.compile(r"^\| `([^`]+)` \| (.*?) \| (\S+) \| (\d+|–) \| (\d+) \| `([0-9a-f]{64})` \|$")  # sayfa: PDF değilse "–"


def belgeler_tablosu() -> list[dict]:
    """KAYNAKLAR.md 'Yerel belgeler' tablosu -> [{dosya, kunye, url, sayfa, bayt, sha256}]."""
    s = KAYNAKLAR.read_text(encoding="utf-8")
    bolum = s[s.index("## Yerel belgeler"):]
    bolum = bolum[:bolum.index("\n## ", 3)]
    satirlar = []
    for satir in bolum.splitlines():
        m = SATIR.match(satir)
        if m:
            satirlar.append({"dosya": m[1], "kunye": m[2], "url": m[3], "sayfa": int(m[4]) if m[4].isdigit() else 0, "bayt": int(m[5]), "sha256": m[6]})
    if not satirlar:
        raise ValueError("KAYNAKLAR.md 'Yerel belgeler' tablosu okunamadı")
    return satirlar


def ozet(yol: Path) -> str:
    return hashlib.sha256(yol.read_bytes()).hexdigest()


def durum(b: dict) -> str:
    yol = KLASOR / b["dosya"]
    if not yol.exists():
        return "yok"
    return "tamam" if yol.stat().st_size == b["bayt"] and ozet(yol) == b["sha256"] else "ozet_farkli"


def indir(b: dict) -> str:
    istek = urllib.request.Request(b["url"], headers={"User-Agent": "Mozilla/5.0 (Veto Atlasi belge indirme)"})
    try:
        with urllib.request.urlopen(istek, timeout=120) as y:
            veri = y.read()
    except (urllib.error.URLError, TimeoutError) as e:
        return f"indirilemedi ({e})"
    if len(veri) != b["bayt"] or hashlib.sha256(veri).hexdigest() != b["sha256"]:
        return f"indirilen dosya tablodakiyle uyuşmuyor ({len(veri)} bayt); saklanmadı"
    KLASOR.mkdir(exist_ok=True)
    (KLASOR / b["dosya"]).write_bytes(veri)
    return "indirildi ve özeti doğrulandı"


def main() -> int:
    kontrol = "--kontrol" in sys.argv
    eksik = 0
    for b in belgeler_tablosu():
        d = durum(b)
        if d == "tamam":
            print(f"tamam        {b['dosya']}")
            continue
        if kontrol:
            print(f"{d:12} {b['dosya']}")
            eksik += 1
            continue
        sonuc = indir(b)
        print(f"{d:12} {b['dosya']}: {sonuc}")
        if not sonuc.startswith("indirildi"):
            eksik += 1
            print(f"             elle indirin: {b['url']}  ->  kaynaklar/.belgeler/{b['dosya']}")
    return 1 if eksik else 0


if __name__ == "__main__":
    sys.exit(main())
