"""
Adım 5: Resmî kaydı henüz yayımlanmamış Genel Kurul toplantılarını listeler ve BM belge
sisteminde (documents.un.org) yayımlanıp yayımlanmadığını kontrol eder.

    python scripts/05_bekleyen_kayitlar.py
    python scripts/05_bekleyen_kayitlar.py --cevrimdisi     # yalnızca listele, ağa çıkma

Veriyi değiştirmez. Yayımlanan bir kayıt bulunursa rapor eder; kaynaklar/genel_kurul_tartismalari.csv
dosyası elle güncellenir (kayit_durumlari -> resmi, gerekirse konuşmacı sayımı toplantı kaydından
yeniden yapılır; METODOLOJI.md 2.5).
"""
import argparse
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

from veto_atlasi.genel_kurul import bekleyen_kayitlar, tartismalari_oku  # noqa: E402

ODS = "https://documents.un.org/api/symbol/access?s={}&l=en&t=pdf"


def yayimlandi_mi(kod: str) -> bool:
    import requests
    for sembol in (kod, f"{kod}(OR)"):
        y = requests.get(ODS.format(sembol), headers={"User-Agent": "VetoAtlasi/0.1 (akademik arastirma)"}, timeout=60)
        if y.ok and y.headers.get("content-type", "").startswith("application/pdf"):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cevrimdisi", action="store_true", help="Belge sistemine sormadan yalnızca listele")
    args = ap.parse_args()

    bekleyen = bekleyen_kayitlar(tartismalari_oku(KOK / "kaynaklar/genel_kurul_tartismalari.csv"))
    print(f"Resmî kaydı beklenen toplantı: {len(bekleyen)}\n")
    yayimlanan = []
    for tartisma, kod, durum in bekleyen:
        if args.cevrimdisi:
            print(f"  {kod:16} {durum:22} ({tartisma})")
            continue
        var = yayimlandi_mi(kod)
        print(f"  {kod:16} {durum:22} ({tartisma}) -> {'YAYIMLANDI' if var else 'henüz yok'}")
        if var:
            yayimlanan.append((tartisma, kod))
    if yayimlanan:
        print(f"\n{len(yayimlanan)} kayıt yayımlanmış; genel_kurul_tartismalari.csv elle güncellenmeli:")
        for tartisma, kod in yayimlanan:
            print(f"  {tartisma}: {kod} -> https://undocs.org/{kod}")


if __name__ == "__main__":
    main()
