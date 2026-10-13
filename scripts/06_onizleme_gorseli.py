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


def yol_cokgenleri(d: str) -> list[list[tuple[float, float]]]:
    """SVG yolunu (mutlak M, L, H, V, C, Z) kapalı çokgenlere çevirir; kübik eğriler 8 doğru parçasına bölünür."""
    import re
    parca = re.findall(r"[MLHVCZ]|-?(?:\d+\.?\d*|\.\d+)", d)
    cokgenler, cokgen, x, y, i, komut = [], [], 0.0, 0.0, 0, None
    while i < len(parca):
        if parca[i] in "MLHVCZ":
            komut = parca[i]; i += 1
            if komut == "Z":
                if cokgen:
                    cokgenler.append(cokgen)
                cokgen = []
                continue
        sayi = lambda k: float(parca[i + k])
        if komut == "M":
            if cokgen:
                cokgenler.append(cokgen)
            x, y = sayi(0), sayi(1); cokgen = [(x, y)]; i += 2; komut = "L"
        elif komut == "L":
            x, y = sayi(0), sayi(1); cokgen.append((x, y)); i += 2
        elif komut == "H":
            x = sayi(0); cokgen.append((x, y)); i += 1
        elif komut == "V":
            y = sayi(0); cokgen.append((x, y)); i += 1
        elif komut == "C":
            x1, y1, x2, y2, x3, y3 = (sayi(k) for k in range(6))
            for n in range(1, 9):
                t = n / 8; u = 1 - t
                cokgen.append((u ** 3 * x + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3,
                               u ** 3 * y + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3))
            x, y = x3, y3; i += 6
        else:
            raise ValueError(f"desteklenmeyen yol komutu: {komut}")
    if cokgen:
        cokgenler.append(cokgen)
    return cokgenler


def isaret_ciz(piksel: list[bytearray], x0: int, y0: int, boyut: int) -> None:
    """web/isaret.svg'deki kareleri (yollar, renkleri SVG'den) boyut px yükseklikte, sol üst köşesi (x0, y0) olacak biçimde
    çizer. Kenarlar 4 x 4 alt örnekle yumuşatılır (alttaki renge karıştırılır); aynı dosya aynı pikselleri verir."""
    import math
    import re
    svg = (KOK / "web/isaret.svg").read_text(encoding="utf-8")
    vb_g, vb_y = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
    olcek = boyut / vb_y
    ornek = [(k + 0.5) / 4 for k in range(4)]
    for m in re.finditer(r"<path\b([^>]*)>", svg):
        renk_hex = re.search(r'fill="(#[0-9A-Fa-f]{6})"', m[1])[1]
        renk = tuple(int(renk_hex[i:i + 2], 16) for i in (1, 3, 5))
        for cokgen in yol_cokgenleri(re.search(r'\bd="([^"]+)"', m[1])[1]):
            nokta = [(x0 + x * olcek, y0 + y * olcek) for x, y in cokgen]
            kenar = list(zip(nokta, nokta[1:] + nokta[:1]))
            for py in range(max(0, math.floor(min(q[1] for q in nokta))), min(YUK, math.ceil(max(q[1] for q in nokta)) + 1)):
                for px in range(max(0, math.floor(min(q[0] for q in nokta))), min(GEN, math.ceil(max(q[0] for q in nokta)) + 1)):
                    icinde = 0
                    for oy in ornek:
                        sy = py + oy
                        for ox in ornek:
                            sx = px + ox
                            ic = False
                            for (ax, ay), (bx, by) in kenar:
                                if (ay > sy) != (by > sy) and sx < ax + (sy - ay) * (bx - ax) / (by - ay):
                                    ic = not ic
                            icinde += ic
                    if icinde:
                        a = icinde / 16
                        eski = piksel[py][3 * px:3 * px + 3]
                        piksel[py][3 * px:3 * px + 3] = bytes(round(e * (1 - a) + r * a) for e, r in zip(eski, renk))


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
    # Sol üstte halka işareti (web/isaret.svg; renkleri SVG'den). Dosya boşluksuz kırpıldığı için 86 px yükseklik ve (16, 13) px
    # içeride: eski 112 px'lik kutudaki halkayla aynı boyut ve yer
    isaret_ciz(piksel, sol + 16, zemin_y - en_cok * adim - 150 + 13, 86)

    hedef = KOK / "web/onizleme.png"
    png_yaz(hedef, piksel)
    print(f"{hedef.relative_to(KOK)}: {GEN}x{YUK}, {ilk}-{son}, en yüksek sütun {en_cok} kare, {hedef.stat().st_size} bayt")


if __name__ == "__main__":
    main()
