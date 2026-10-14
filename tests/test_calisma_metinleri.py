"""Çalışma metinleri depoda değil; yerelde varsa künye tablosuyla tutarlı olmalı."""
import hashlib
import subprocess

import pytest

from conftest import CALISMA, KOK, calisma_metinleri_tablosu


def test_tablo_bes_metni_iceriyor():
    assert set(calisma_metinleri_tablosu()) == {
        "Birlesmis_milletler_konuşması2019.pdf", "BM2026-2022-web.pdf", "DahaAdilBirDünyaMümkün.pdf",
        "Birlesmis_Milletler_EN_2019.pdf", "A_Fairer_World_is_Possible_EN.pdf"}


def test_calisma_metinleri_depoda_izlenmiyor():
    izlenen = subprocess.run(["git", "ls-files", "kaynaklar/calisma_metinleri"], cwd=KOK,
                             capture_output=True, text=True, check=True).stdout.strip()
    assert izlenen == ""


@pytest.mark.parametrize("ad", sorted(calisma_metinleri_tablosu()))
def test_yerel_kopya_tabloyla_ayni(ad):
    yol = CALISMA / ad
    if not yol.exists():
        pytest.skip(f"çalışma metni yerelde yok: {ad}")
    veri = yol.read_bytes()
    beklenen = calisma_metinleri_tablosu()[ad]
    assert len(veri) == beklenen["bayt"]
    assert hashlib.sha256(veri).hexdigest() == beklenen["sha256"]


def test_metin_okunabiliyor(calisma_metni):
    # Alıntı testleri bu fikstürle yazılacak (ADIM 16); burada yalnızca okuma denetlenir.
    metin = calisma_metni("Birlesmis_milletler_konuşması2019.pdf")
    assert "24 EYLÜL 2019" in metin
