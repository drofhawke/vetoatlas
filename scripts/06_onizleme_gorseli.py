"""
Adım 6: Paylaşım önizleme görseli (Open Graph) üretir.

    python scripts/06_onizleme_gorseli.py

web/veri.js'teki kayıtlardan birim grafiğin sade bir hâlini çizer: her kare bir ret oyu,
sütunlar yıllar, renkler vetoyu kullanan daimi üye (arayüzdeki açık tema renkleri); sol üstte halka işareti (web/isaret.svg). Kapalı
oturum vetoları gri kare olarak gösterilir. Metin yoktur; başlık ve açıklama og: etiketlerinden
gelir. Ek bağımlılık gerektirmez (PNG, standart kütüphaneyle yazılır); aynı veri aynı dosyayı verir.

Çıktı: web/onizleme.png (1200 x 630)
"""
import json
import struct
import zlib
from collections import defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
GEN, YUK = 1200, 630
ZEMIN = (0xFB, 0xF8, 0xF1)
CIZGI = (0xE1, 0xDB, 0xCF)
KAPALI = (0x9A, 0xA3, 0xB2)
MUREKKEP = (0x13, 0x21, 0x3A)
RENK = {  # web/vetolar.html --u-* (açık tema)
    "SSCB": (0x7E, 0x2F, 0x3C), "RUS": (0xC2, 0x66, 0x6F), "USA": (0x24, 0x50, 0x7F),
    "GBR": (0x2F, 0x7A, 0x6E), "FRA": (0xA8, 0x78, 0x2A), "CHN": (0x5E, 0x4E, 0x9A),
}
UYE_SIRASI = ["SSCB", "RUS", "USA", "GBR", "FRA", "CHN"]


def png_yaz(yol: Path, piksel: list[bytearray]) -> None:
    def parca(tur: bytes, veri: bytes) -> bytes:
        return struct.pack(">I", len(veri)) + tur + veri + struct.pack(">I", zlib.crc32(tur + veri) & 0xFFFFFFFF)

    ham = b"".join(b"\x00" + bytes(satir) for satir in piksel)
    yol.write_bytes(b"\x89PNG\r\n\x1a\n" + parca(b"IHDR", struct.pack(">IIBBBBB", GEN, YUK, 8, 2, 0, 0, 0))
                    + parca(b"IDAT", zlib.compress(ham, 9)) + parca(b"IEND", b""))


def isaret_ciz(piksel: list[bytearray], x0: int, y0: int, boyut: int) -> None:
    """web/isaret.svg'deki döndürülmüş kareleri (viewBox 128) verilen boyutta çizer; rx yuvarlaması atlanır."""
    import math
    import re
    svg = (KOK / "web/isaret.svg").read_text(encoding="utf-8")
    olcek = boyut / 128
    for m in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"[^>]*fill="(#[0-9A-Fa-f]{6})" transform="rotate\(([\d.]+) ([\d.]+) ([\d.]+)\)"', svg):
        x, y, g, h, renk, aci, cx, cy = m.groups()
        x, y, g, h, aci, cx, cy = map(float, (x, y, g, h, aci, cx, cy))
        r = tuple(int(renk[i:i + 2], 16) for i in (1, 3, 5))
        a = math.radians(aci); ca, sa = math.cos(a), math.sin(a)
        yarim = g / 2
        for py in range(int((cy - yarim * 1.5) * olcek) + y0, int((cy + yarim * 1.5) * olcek) + y0 + 1):
            for px in range(int((cx - yarim * 1.5) * olcek) + x0, int((cx + yarim * 1.5) * olcek) + x0 + 1):
                if not (0 <= px < GEN and 0 <= py < YUK):
                    continue
                # Piksel merkezini SVG koordinatına, sonra karenin kendi eksenine döndür
                sx, sy = (px + 0.5 - x0) / olcek - cx, (py + 0.5 - y0) / olcek - cy
                ux, uy = sx * ca + sy * sa, -sx * sa + sy * ca
                if abs(ux) <= yarim and abs(uy) <= yarim:
                    piksel[py][3 * px:3 * px + 3] = bytes(r)


def main():
    s = (KOK / "web/veri.js").read_text(encoding="utf-8")
    kayitlar = json.loads(s[s.index("{"):s.rstrip().rindex(";")])["kayitlar"]
    yillar = defaultdict(list)
    for k in sorted(kayitlar, key=lambda k: (k["tarih"], k["id"])):
        if k["kapali"]:
            yillar[int(k["tarih"][:4])].append(KAPALI)
        else:
            yillar[int(k["tarih"][:4])] += [RENK[u] for u in sorted(k["uyeler"], key=UYE_SIRASI.index)]
    ilk, son = min(yillar), max(yillar)
    en_cok = max(len(v) for v in yillar.values())

    kenar_x, ust, alt = 70, 70, 90
    adim = min((GEN - 2 * kenar_x) // (son - ilk + 1), (YUK - ust - alt) // en_cok)
    kare = max(adim - 3, 2)
    sol = (GEN - adim * (son - ilk + 1)) // 2
    # Grafik dikeyde ortalanır
    zemin_y = ust + (YUK - ust - alt + en_cok * adim) // 2

    piksel = [bytearray(ZEMIN * GEN) for _ in range(YUK)]

    def dikdortgen(x0, y0, g, y, renk):
        for yy in range(max(y0, 0), min(y0 + y, YUK)):
            satir = piksel[yy]
            for xx in range(max(x0, 0), min(x0 + g, GEN)):
                satir[3 * xx:3 * xx + 3] = bytes(renk)

    for yil, renkler in yillar.items():
        x = sol + (yil - ilk) * adim + (adim - kare) // 2
        for j, renk in enumerate(renkler):
            dikdortgen(x, zemin_y - (j + 1) * adim + (adim - kare) // 2, kare, kare, renk)
    dikdortgen(sol, zemin_y + 3, adim * (son - ilk + 1), 2, CIZGI)
    # Onyıl işaretleri
    for yil in range((ilk // 10 + 1) * 10, son + 1, 10):
        dikdortgen(sol + (yil - ilk) * adim + adim // 2 - 1, zemin_y + 8, 2, 10, KAPALI)
    # Sol üstte halka işareti (web/isaret.svg; döndürülmüş kareler, renkleri SVG'den)
    isaret_ciz(piksel, sol, zemin_y - en_cok * adim - 150, 112)

    hedef = KOK / "web/onizleme.png"
    png_yaz(hedef, piksel)
    print(f"{hedef.relative_to(KOK)}: {GEN}x{YUK}, {ilk}-{son}, en yüksek sütun {en_cok} kare, {hedef.stat().st_size} bayt")


if __name__ == "__main__":
    main()
