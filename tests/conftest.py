"""
Ortak test yardımcıları.

Çalışma metinleri (konuşma derlemeleri, kitap) depoya girmez; künyeleri ve SHA-256 değerleri
kaynaklar/KAYNAKLAR.md "Çalışma metinleri" tablosundadır. Alıntı testleri `calisma_metni`
fikstürünü kullanır: dosya yerelde yoksa ya da özeti tablodakiyle uyuşmuyorsa test atlanır.
"""
import hashlib
import re
import shutil
import subprocess
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
CALISMA = KOK / "kaynaklar" / "calisma_metinleri"
_METIN_ONBELLEK: dict[tuple[str, bool], str] = {}


def calisma_metinleri_tablosu() -> dict[str, dict]:
    """KAYNAKLAR.md tablosundan dosya adı -> {bayt, sha256}."""
    s = (KOK / "kaynaklar/KAYNAKLAR.md").read_text(encoding="utf-8")
    bolum = s[s.index("## Çalışma metinleri"):]
    bolum = bolum[:bolum.index("\n## ", 3)]
    tablo = {}
    for satir in bolum.splitlines():
        m = re.match(r"^\| `([^`]+)` \|.*\| (\d+) \| `([0-9a-f]{64})` \|$", satir)
        if m:
            tablo[m[1]] = {"bayt": int(m[2]), "sha256": m[3]}
    return tablo


@pytest.fixture
def calisma_metni():
    """
    calisma_metni("BM2026-2022-web.pdf") -> PDF'in düz metni (pdftotext, sayfalar \\f ile ayrılır).
    Dosya yoksa, özeti KAYNAKLAR.md'dekiyle uyuşmuyorsa ya da pdftotext kurulu değilse testi atlar.
    """
    tablo = calisma_metinleri_tablosu()

    def oku(ad: str, ham: bool = False) -> str:
        if ad not in tablo:
            raise KeyError(f"{ad} KAYNAKLAR.md 'Çalışma metinleri' tablosunda yok")
        yol = CALISMA / ad
        if not yol.exists():
            pytest.skip(f"çalışma metni yerelde yok: {ad}")
        if hashlib.sha256(yol.read_bytes()).hexdigest() != tablo[ad]["sha256"]:
            pytest.skip(f"çalışma metninin SHA-256'sı KAYNAKLAR.md'dekinden farklı: {ad}")
        if not shutil.which("pdftotext"):
            pytest.skip("pdftotext kurulu değil")
        # ham=True: düzen korunmadan (alıntı doğrulamasının kullandığı metin katmanı)
        if (ad, ham) not in _METIN_ONBELLEK:
            secenek = [] if ham else ["-layout"]
            _METIN_ONBELLEK[(ad, ham)] = subprocess.run(["pdftotext", "-enc", "UTF-8", *secenek, str(yol), "-"],
                                                        capture_output=True, check=True).stdout.decode("utf-8")
        return _METIN_ONBELLEK[(ad, ham)]

    return oku
