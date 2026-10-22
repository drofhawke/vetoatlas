"""
Adım 6: Paylaşım önizleme görseli (Open Graph) üretir.

    python scripts/06_onizleme_gorseli.py

web/veri.js'teki kayıtlardan birim grafiğin sade bir hâlini çizer: her kare bir ret oyu,
sütunlar yıllar, renkler vetoyu kullanan daimi üye (arayüzdeki açık tema renkleri); sol üstte çubuk logosu (web/logo-cubuk-b.svg,
yazı işaretli). Kapalı
oturum vetoları gri kare olarak gösterilir. Sözcük yoktur, yalnızca sayı ve yıl (iki dilde aynı): sağ üstte
kayıt sayısı ve dönem, çentiklerin altında onyıllar, altta kartlardaki gibi çizgi ve adres; başlık ve açıklama
og: etiketlerinden gelir. Ek Python bağımlılığı yoktur (PNG standart kütüphaneyle okunur ve yazılır); yazılar
08 betiği gibi makinedeki Edge ya da Chrome ile başsız dizilir, kareler ve logo üstüne bu betikte çizilir.

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
IKINCIL = (0x5A, 0x65, 0x78)  # --murekkep-2
LOGO_YERI, LOGO_BOYU = (89, 74), 40  # çubuk logosunun sol üst köşesi ve yüksekliği (08'in sayfa önizlemeleri de kullanır)
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


def harf_gruplari(cokgenler: list[list[tuple[float, float]]]) -> list[list[list[tuple[float, float]]]]:
    """Bir yolun alt yollarını birlikte doldurulacak gruplara ayırır: iç kontur (harfin iç boşluğu: o, e, a, A) içinde durduğu dış
    konturla aynı grupta. Grup SVG'nin doldurma kuralıyla (nonzero) çizilir; tek konturlu gruplar eskisi gibi çizilir."""
    alan = lambda c: sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(c, c[1:] + c[:1])) / 2
    kutu = lambda c: (min(p[0] for p in c), min(p[1] for p in c), max(p[0] for p in c), max(p[1] for p in c))
    gruplar, sahibi = [], {}
    for i, c in enumerate(cokgenler):
        ki = kutu(c)
        for j, d in enumerate(cokgenler):
            kj = kutu(d)
            # Ters yönlü ve kutusu öbürünün içinde: iç kontur
            if j != i and alan(c) * alan(d) < 0 and kj[0] <= ki[0] and kj[1] <= ki[1] and ki[2] <= kj[2] and ki[3] <= kj[3]:
                sahibi[i] = j
                break
    for i, c in enumerate(cokgenler):
        if i not in sahibi:
            gruplar.append([c] + [cokgenler[k] for k, j in sahibi.items() if j == i])
    return gruplar


def svg_ciz(piksel: list[bytearray], dosya: str, x0: int, y0: int, boyut: int) -> None:
    """Bir SVG'deki yolları (renkleri SVG'den) boyut px yükseklikte, sol üst köşesi (x0, y0) olacak biçimde çizer (web/isaret.svg,
    web/logo-cubuk-b.svg). Kenarlar 4 x 4 alt örnekle yumuşatılır (alttaki renge karıştırılır); aynı dosya aynı pikselleri verir.
    Harfin dış ve iç konturu birlikte, nonzero kuralıyla doldurulur (tarayıcıdaki gibi): iç boşluk zemin renginde kalır."""
    import math
    import re
    svg = (KOK / dosya).read_text(encoding="utf-8")
    vb_g, vb_y = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
    olcek = boyut / vb_y
    ornek = [(k + 0.5) / 4 for k in range(4)]
    for m in re.finditer(r"<path\b([^>]*)>", svg):
        renk_hex = re.search(r'fill="(#[0-9A-Fa-f]{6})"', m[1])[1]
        renk = tuple(int(renk_hex[i:i + 2], 16) for i in (1, 3, 5))
        for grup in harf_gruplari(yol_cokgenleri(re.search(r'\bd="([^"]+)"', m[1])[1])):
            noktalar = [[(x0 + x * olcek, y0 + y * olcek) for x, y in cokgen] for cokgen in grup]
            nokta = noktalar[0]  # dış kontur: sınır kutusu
            kenar = [k for n in noktalar for k in zip(n, n[1:] + n[:1])]
            for py in range(max(0, math.floor(min(q[1] for q in nokta))), min(YUK, math.ceil(max(q[1] for q in nokta)) + 1)):
                for px in range(max(0, math.floor(min(q[0] for q in nokta))), min(GEN, math.ceil(max(q[0] for q in nokta)) + 1)):
                    icinde = 0
                    for oy in ornek:
                        sy = py + oy
                        for ox in ornek:
                            sx = px + ox
                            sarim = 0  # nonzero: kenarların yönlü sayımı
                            for (ax, ay), (bx, by) in kenar:
                                if (ay > sy) != (by > sy) and sx < ax + (sy - ay) * (bx - ax) / (by - ay):
                                    sarim += 1 if by > ay else -1
                            icinde += sarim != 0
                    if icinde:
                        a = icinde / 16
                        eski = piksel[py][3 * px:3 * px + 3]
                        piksel[py][3 * px:3 * px + 3] = bytes(round(e * (1 - a) + r * a) for e, r in zip(eski, renk))


TARAYICILAR = [  # scripts/08_paylasim_kartlari.py ile aynı
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def png_oku(veri: bytes) -> list[bytearray]:
    """Tarayıcının yazdığı PNG'yi (8 bit RGB ya da RGBA, geçmesiz) RGB satırlarına çevirir."""
    i, idat = 8, b""
    while i < len(veri):
        n, tur = struct.unpack(">I4s", veri[i:i + 8])
        govde = veri[i + 8:i + 8 + n]
        i += 12 + n
        if tur == b"IHDR":
            gen, yuk, bit, renk = struct.unpack(">IIBB", govde[:10])
            assert (gen, yuk, bit) == (GEN, YUK, 8) and renk in (2, 6) and govde[12] == 0, (gen, yuk, bit, renk)
        elif tur == b"IDAT":
            idat += govde
    bpp = 3 if renk == 2 else 4
    ham, st, satirlar, onceki, p = zlib.decompress(idat), GEN * bpp, [], bytearray(GEN * bpp), 0
    for _ in range(YUK):
        f, s = ham[p], bytearray(ham[p + 1:p + 1 + st])
        p += 1 + st
        for x in range(st):
            a = s[x - bpp] if x >= bpp else 0
            u = onceki[x]
            c = onceki[x - bpp] if x >= bpp else 0
            if f == 1:
                s[x] = (s[x] + a) & 255
            elif f == 2:
                s[x] = (s[x] + u) & 255
            elif f == 3:
                s[x] = (s[x] + (a + u) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(u - c), abs(a - c), abs(a + u - 2 * c)
                s[x] = (s[x] + (a if pa <= pb and pa <= pc else u if pb <= pc else c)) & 255
        satirlar.append(s if bpp == 3 else bytearray(b for k in range(GEN) for b in s[4 * k:4 * k + 3]))
        onceki = s
    return satirlar


def yazi_katmani(govde: str) -> list[bytearray]:
    """Sayı ve yıl yazılarını atlasın yazı tipleriyle zemin üzerine dizer (başsız Edge ya da Chrome ekran görüntüsü) ve piksel
    satırlarını döndürür. Tarayıcı yoksa durur: yazısız önizleme yazılmaz."""
    import shutil
    import subprocess
    import tempfile
    exe = next((y for y in TARAYICILAR if Path(y).exists()), None) or shutil.which("msedge") or shutil.which("chrome")
    if not exe:
        raise SystemExit("Chromium tabanlı tarayıcı (Edge/Chrome) bulunamadı; önizleme üretilmedi.")
    hex_ = lambda r: "#%02X%02X%02X" % r
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{(KOK / 'web/fonts/fonts.css').as_uri()}">
<style>
html, body {{ margin: 0; width: {GEN}px; height: {YUK}px; overflow: hidden; background: {hex_(ZEMIN)}; color: {hex_(MUREKKEP)}; }}
div {{ position: absolute; white-space: nowrap; font-variant-numeric: tabular-nums; }}
.sayi {{ top: 54px; font: 600 96px/1 "Source Serif 4", Georgia, serif; }}
.donem {{ top: 156px; font: 400 22px/1 "Source Sans 3", "Segoe UI", sans-serif; color: {hex_(IKINCIL)}; }}
.yil {{ transform: translateX(-50%); font: 400 18px/1 "Source Sans 3", "Segoe UI", sans-serif; color: {hex_(IKINCIL)}; }}
.alt {{ bottom: 36px; border-top: 1px solid {hex_(CIZGI)}; padding-top: 12px; text-align: right; font: 400 19px/1.2 "Source Sans 3", "Segoe UI", sans-serif; }}
</style></head><body>
{govde}
</body></html>"""
    gecici = Path(tempfile.mkdtemp(prefix="veto-onizleme-"))
    try:
        (gecici / "yazi.html").write_text(html, encoding="utf-8")
        png = gecici / "yazi.png"
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", f"--user-data-dir={gecici / 'profil'}",
                        "--force-device-scale-factor=1", f"--window-size={GEN},{YUK}", f"--screenshot={png}", (gecici / "yazi.html").as_uri()],
                       capture_output=True, timeout=120)
        if not png.exists():
            raise SystemExit("Tarayıcı ekran görüntüsü alamadı; önizleme üretilmedi.")
        return png_oku(png.read_bytes())
    finally:
        shutil.rmtree(gecici, ignore_errors=True)


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

    # Sayı ve yıllar (sözcük yok; iki dilde aynı): büyük kayıt sayısı ve dönem sağ üstte, grafiğin sağ kenarına hizalı; onyıl
    # etiketleri çentiklerin altında; alt bilgi çizgisi ve adres kartlardaki gibi. Yazı tarayıcıda dizilir, kareler ve logo üstüne
    # burada çizilir (logo eskisiyle aynı yerde ve boyda).
    sag = sol + adim * (son - ilk + 1)
    onyillar = list(range((ilk // 10 + 1) * 10, son + 1, 10))
    yazilar = [f'<div class="sayi" style="right:{GEN - sag}px">{len(kayitlar)}</div>',
               f'<div class="donem" style="right:{GEN - sag}px">{ilk}–{son}</div>',
               *(f'<div class="yil" style="left:{sol + (yil - ilk) * adim + adim // 2}px;top:{zemin_y + 24}px">{yil}</div>' for yil in onyillar),
               f'<div class="alt" style="left:{sol}px;right:{GEN - sag}px">vetoatlas.com</div>']
    piksel = yazi_katmani("\n".join(yazilar))

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
    # Sol üstte çubuk logosu (web/logo-cubuk-b.svg: halka işareti ve "Veto Atlası" yazısı; renkleri SVG'den), 40 px yükseklikte,
    # eski halkanın (86 px) bandında dikeyde ortalanmış
    assert (sol + 16, zemin_y - en_cok * adim - 150 + 13 + 23) == LOGO_YERI, "logo yeri değişti"
    svg_ciz(piksel, "web/logo-cubuk-b.svg", *LOGO_YERI, LOGO_BOYU)

    hedef = KOK / "web/onizleme.png"
    png_yaz(hedef, piksel)
    print(f"{hedef.relative_to(KOK)}: {GEN}x{YUK}, {ilk}-{son}, en yüksek sütun {en_cok} kare, {hedef.stat().st_size} bayt")


if __name__ == "__main__":
    main()
