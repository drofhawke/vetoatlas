"""
Yerel belgeler (kaynaklar/.belgeler/): depoya girmez; künyeleri, indirme adresleri ve SHA-256 değerleri
KAYNAKLAR.md "Yerel belgeler" tablosundadır. Yerelde bulunan her belge tablodakiyle aynı olmalı;
bulunmayan belge için test atlanır. Depoda hiçbir PDF izlenmez.
"""
import importlib.util
import subprocess

import pytest

from conftest import KOK

spec = importlib.util.spec_from_file_location("belgeleri_indir", KOK / "scripts/07_belgeleri_indir.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
TABLO = B.belgeler_tablosu()


def test_tablo_okunuyor_ve_adresler_tam():
    assert {b["dosya"] for b in TABLO} >= {"S_PV.704.pdf", "S_PV.1662.pdf", "S_PV.2191_Add.1.pdf", "A_58_47.pdf"}
    for b in TABLO:
        assert b["url"].startswith("https://") and b["bayt"] > 0 and (b["sayfa"] > 0 or not b["dosya"].endswith(".pdf")), b["dosya"]


@pytest.mark.parametrize("b", TABLO, ids=[b["dosya"] for b in TABLO])
def test_yerel_belge_tablodakiyle_ayni(b):
    yol = B.KLASOR / b["dosya"]
    if not yol.exists():
        pytest.skip(f"yerel belge yok: {b['dosya']} (scripts/07_belgeleri_indir.py)")
    assert B.durum(b) == "tamam"


def test_depoda_pdf_izlenmiyor():
    izlenen = subprocess.run(["git", "ls-files"], cwd=KOK, capture_output=True, text=True).stdout.split()
    assert not [d for d in izlenen if d.lower().endswith(".pdf")]
    assert "kaynaklar/.belgeler/" in (KOK / ".gitignore").read_text(encoding="utf-8")
