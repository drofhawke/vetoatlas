"""
Adım 1: DHL veto listesini indirir, ham HTML'i arşivler, ayrıştırır.

Çalıştırma (proje kök klasöründen):
    python scripts/01_veto_listesini_cek.py
    python scripts/01_veto_listesini_cek.py --yerel data/raw/veto_dhl_2026-10-10.html   # internetsiz tekrar

Çıktılar:
    data/raw/veto_dhl_<tarih>.html          -> kaynağın değişmez kopyası (atıf ve tekrarlanabilirlik için)
                                               Sunucudan gelen baytlar olduğu gibi yazılır; var olan
                                               dosyanın üzerine asla yazılmaz (bkz. veto_atlasi/kaynak.py).
    data/processed/vetolar.json / .csv      -> ayrıştırılmış kayıtlar
    data/review/inceleme.csv                -> elle kontrol edilmesi gereken satırlar
"""
import argparse
import csv
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

import requests  # noqa: E402
from veto_atlasi.kaynak import dosya_sha256, ham_html_oku, ham_kaydet  # noqa: E402
from veto_atlasi.parser import KAYNAK_URL, tablo_ayristir  # noqa: E402

HAM = KOK / "data" / "raw"
ISLENMIS = KOK / "data" / "processed"
INCELEME = KOK / "data" / "review"


def indir() -> Path:
    yanit = requests.get(
        KAYNAK_URL,
        headers={"User-Agent": "VetoAtlasi/0.1 (akademik arastirma)"},
        timeout=60,
    )
    yanit.raise_for_status()
    # .text değil .content: baytlar çözülmeden ve satır sonları değişmeden arşivlenir
    return ham_kaydet(yanit.content, HAM, date.today())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yerel", help="İndirmek yerine kayıtlı HTML dosyasını kullan")
    args = ap.parse_args()

    for k in (HAM, ISLENMIS, INCELEME):
        k.mkdir(parents=True, exist_ok=True)

    yol = Path(args.yerel).resolve() if args.yerel else indir()
    try:
        kaynak_dosya = yol.relative_to(KOK).as_posix()
    except ValueError:
        sys.exit(f"Ham dosya proje klasörünün içinde olmalı (03 ve 04 özetini oradan doğrular): {yol}")
    sha = dosya_sha256(yol)

    kayitlar, inceleme = tablo_ayristir(ham_html_oku(yol))

    meta = {
        "kaynak_url": KAYNAK_URL,
        "kaynak_dosya": kaynak_dosya,
        "kaynak_sha256": sha,
        "olusturma_zamani": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kayit_sayisi": len(kayitlar),
        "inceleme_sayisi": len(inceleme),
    }

    (ISLENMIS / "vetolar.json").write_text(
        json.dumps({"meta": meta, "kayitlar": [k.sozluk() for k in kayitlar]},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with open(ISLENMIS / "vetolar.csv", "w", newline="", encoding="utf-8-sig") as f:
        alanlar = ["id", "tarih", "tarih_ham", "taslak_belgeler", "toplanti_kayitlari",
                   "gundem_maddesi", "veto_eden_uyeler", "kismi_veto_suphesi", "notlar"]
        w = csv.DictWriter(f, fieldnames=alanlar)
        w.writeheader()
        for k in kayitlar:
            d = k.sozluk()
            w.writerow({a: "; ".join(d[a]) if isinstance(d[a], list) else d[a] for a in alanlar})

    with open(INCELEME / "inceleme.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["satir_no", "neden", "metin"])
        w.writeheader()
        w.writerows(inceleme)

    print(f"Kaynak       : {kaynak_dosya}")
    print(f"SHA-256      : {sha}")
    print(f"Kayıt        : {len(kayitlar)}")
    print(f"İncelenecek  : {len(inceleme)}  -> data/review/inceleme.csv")
    if not kayitlar:
        print("UYARI: Hiç kayıt çıkmadı. Sayfa yapısı değişmiş olabilir; ham HTML'i kontrol et.")
        sys.exit(1)


if __name__ == "__main__":
    main()
