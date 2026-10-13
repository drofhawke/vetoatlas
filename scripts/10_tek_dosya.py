"""
Adım 10: Tek dosyalık inceleme sürümü.

    python scripts/10_tek_dosya.py   # web/veto-atlasi-tek-dosya.html

web/ altındaki altı sayfayı, veriyi, stilleri, betikleri ve yazı tiplerini (woff2, base64) tek HTML dosyasında
birleştirir; dış istek yoktur. 04 betiği de her çalıştığında bu dosyayı yeniden üretir. Ayrıntı:
veto_atlasi/tek_dosya.py.
"""
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from veto_atlasi import tek_dosya  # noqa: E402

if __name__ == "__main__":
    yol = tek_dosya.uret(KOK)
    print(f"{yol.relative_to(KOK)}: {yol.stat().st_size / 1e6:.2f} MB")
