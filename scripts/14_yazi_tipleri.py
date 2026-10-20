"""
Adım 14: Yazı tipleri.

    python scripts/14_yazi_tipleri.py   # web/fonts/*.woff2 ve web/fonts/README.md'deki SHA-256 tablosu

Google Fonts'un Source Sans 3 ve Source Serif 4 değişken yazı tiplerinden (ilk çalıştırmada kaynaklar/.yazi_tipleri/
altına indirilir, özetleri denetlenir) kesimleri çıkarır, ttfautohint ile hinting ekler, fonts.css'teki alt kümelere böler ve
woff2 yazar. Yazı tipleri değişince 10 (tek dosya) ve 11 (internetsiz çalışma) betikleri yeniden çalıştırılır.
Ayrıntı: veto_atlasi/yazi_tipleri.py.

    pip install fonttools brotli ttfautohint-py
"""
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from veto_atlasi import yazi_tipleri  # noqa: E402

if __name__ == "__main__":
    ozetler = yazi_tipleri.uret(KOK)
    yazi_tipleri.readme_guncelle(KOK, ozetler)
    print(f"web/fonts: {len(ozetler)} woff2, README.md tablosu güncellendi")
