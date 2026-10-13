"""
Adım 11: İnternetsiz çalışma.

    python scripts/11_cevrimdisi.py   # web/cevrimdisi.js

Sayfaların ve kullandıkları dosyaların listesinden service worker'ı üretir; sürümü bu dosyaların içerik özetidir. 04 betiği de
her çalıştığında bu dosyayı yeniden üretir. Ayrıntı: veto_atlasi/cevrimdisi.py.
"""
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from veto_atlasi import cevrimdisi  # noqa: E402

if __name__ == "__main__":
    yol = cevrimdisi.yaz(KOK)
    sayfalar, dosyalar = cevrimdisi.listeler(KOK / "web")
    print(f"{yol.relative_to(KOK)}: {len(sayfalar)} sayfa, {len(dosyalar)} dosya")
