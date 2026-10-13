import hashlib
from datetime import date
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from veto_atlasi.kaynak import dosya_sha256, ham_html_oku, ham_kaydet, kaynak_dogrula

GUN = date(2026, 10, 10)
ICERIK = b"<html>\r\n<td>25 February 2022</td>\r\n</html>\r\n"


def test_ham_kaydet_baytlari_degistirmez(tmp_path):
    yol = ham_kaydet(ICERIK, tmp_path, GUN)
    assert yol.name == "veto_dhl_2026-10-10.html"
    assert yol.read_bytes() == ICERIK
    assert dosya_sha256(yol) == hashlib.sha256(ICERIK).hexdigest()
    assert "\r\n" in ham_html_oku(yol)  # okurken de satır sonları korunur


def test_ham_kaydet_uzerine_yazmaz(tmp_path):
    ilk = ham_kaydet(ICERIK, tmp_path, GUN)
    assert ham_kaydet(ICERIK, tmp_path, GUN) == ilk          # aynı içerik: yeniden yazılmaz
    yeni = ham_kaydet(b"farkli", tmp_path, GUN)
    assert yeni.name == "veto_dhl_2026-10-10_2.html"
    assert ilk.read_bytes() == ICERIK                          # eski dosyaya dokunulmadı
    assert sorted(p.name for p in tmp_path.iterdir()) == ["veto_dhl_2026-10-10.html", "veto_dhl_2026-10-10_2.html"]


def test_kaynak_dogrula_ozet_tutmazsa_durur(tmp_path):
    yol = ham_kaydet(ICERIK, tmp_path / "data" / "raw", GUN)
    meta = {"kaynak_dosya": yol.relative_to(tmp_path).as_posix(), "kaynak_sha256": dosya_sha256(yol)}
    assert kaynak_dogrula(tmp_path, meta) == (yol, meta["kaynak_sha256"])
    with pytest.raises(ValueError, match="SHA-256 tutmuyor"):
        kaynak_dogrula(tmp_path, dict(meta, kaynak_sha256="0" * 64))
    # Dosya varken yoksa_kayitli özet denetimini atlatmaz
    with pytest.raises(ValueError, match="SHA-256 tutmuyor"):
        kaynak_dogrula(tmp_path, dict(meta, kaynak_sha256="0" * 64), yoksa_kayitli=True)


def test_kaynak_dogrula_ham_dosya_yoksa(tmp_path):
    """Açık depoda ham dosya yoktur: varsayılan durur, yoksa_kayitli kayıtlı özetle devam eder (03 ve 04)."""
    meta = {"kaynak_dosya": "data/raw/veto_dhl_2026-10-10.html", "kaynak_sha256": "a" * 64}
    with pytest.raises(ValueError, match="bulunamadı"):
        kaynak_dogrula(tmp_path, meta)
    assert kaynak_dogrula(tmp_path, meta, yoksa_kayitli=True) == (None, "a" * 64)


def test_03_referans_tablo_yoksa_aciklamayla_durur(tmp_path):
    """Açık depoda scprocedure Tablo 4 yoktur: 03 hata iziyle değil, açıklayan bir mesajla durur."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("mutabakat", Path(__file__).resolve().parents[1] / "scripts/03_mutabakat.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.REFERANS = tmp_path / "scprocedure_tablo4.csv"
    with pytest.raises(SystemExit, match="referans tablo depoda yok"):
        m.main()
