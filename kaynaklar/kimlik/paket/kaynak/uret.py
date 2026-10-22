#!/usr/bin/env python3
"""
Veto Atlası — logo paketi üreteci.

Bütün logo, ikon ve web dosyaları bu tek betikten üretilir. Renkleri, slogan metnini ya da
oranları değiştirmek için yalnızca aşağıdaki AYARLAR bölümünü düzenleyip betiği çalıştırın:

    pip install fonttools uharfbuzz resvg-py pillow cairosvg
    python kaynak/uret.py         # paketi bulunduğu yerde baştan üretir

Yazı tipleri (Source Serif 4, Source Sans 3 — SIL OFL) ilk çalıştırmada GitHub'dan indirilir.
cairosvg kurulamazsa (Windows'ta Cairo gerekir) PDF/EPS adımı atlanır, gerisi üretilir.
"""
import io
import json
import math
import re
import struct
import sys
import urllib.request
from pathlib import Path

# ════════════════════════════════════════════════════════════════════════════════
# AYARLAR
# ════════════════════════════════════════════════════════════════════════════════
RENK = {
    "murekkep": "#13213A",   # mürekkep (lacivert) — sitedeki --murekkep ile aynı
    "ret":      "#A4262C",   # ret kırmızısı — sitedeki --ret ile aynı
    "kagit":    "#FBF8F1",   # kâğıt — sitedeki --zemin ile aynı
    "ikincil":  "#5A6578",   # slogan grisi — sitedeki --ikincil ile aynı
    # koyu zemin karşılıkları (koyu zeminde yeterli kontrast için açılmış tonlar)
    "acik":     "#EDE8E0",   # koyu zeminde mürekkebin yerine geçen kâğıt tonu
    "ret_acik": "#E05A52",   # koyu zeminde ret kırmızısı
    "ikincil_acik": "#AEB8C4",
}
AD = "Veto Atlası"
SLOGAN = {
    "a": "DÜNYA 5\u2019TEN BÜYÜKTÜR",          # tipografik kesme işareti (’)
    "b": "DAHA ADİL BİR DÜNYA MÜMKÜN",
}
SLOGAN_ETIKET = {"a": "Dünya 5\u2019ten büyüktür", "b": "Daha adil bir dünya mümkün"}
SITE = "https://vetoatlas.com"
BASLANGIC = "/hikaye"   # ana ekran ikonundan açılınca gelinecek sayfa (sitenin ana sayfası)

# İşaret geometrisi (birim: kare kenarı s)
KARE_SAYISI = 15
HALKA = 3.0        # halka yarıçapı / s
ITME = 0.85        # kırmızı karenin dışarı itilmesi / s
KOSE = 0.17        # köşe yarıçapı / s
RET_SIRA = 14      # 336° — saat 11 yönü

FONT_URL = {
    "SourceSerif4-Semibold.otf": "https://raw.githubusercontent.com/adobe-fonts/source-serif/release/OTF/SourceSerif4-Semibold.otf",
    "SourceSans3-Regular.otf": "https://raw.githubusercontent.com/adobe-fonts/source-sans/release/OTF/SourceSans3-Regular.otf",
}

BURASI = Path(__file__).resolve().parent
FONT_DIR = BURASI / "fonts"
CIKTI = Path(sys.argv[1]) if len(sys.argv) > 1 else BURASI.parent   # paketin kök klasörü

# ════════════════════════════════════════════════════════════════════════════════
# Yol (path) yardımcıları
# ════════════════════════════════════════════════════════════════════════════════
def fmt(v, prec=2):
    s = f"{v:.{prec}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s

def to_d(subs, prec=2):
    """Alt yolları kısa, mutlak SVG path verisine çevirir (H/V kısaltmaları dahil)."""
    out = []
    for sub in subs:
        pos = None
        for c, pts in sub:
            if c == "M":
                x, y = pts[0]; out.append(f"M{fmt(x,prec)} {fmt(y,prec)}"); pos = (round(x, prec), round(y, prec))
            elif c == "L":
                x, y = pts[0]; r = (round(x, prec), round(y, prec))
                if pos and r == pos: continue
                if pos and r[1] == pos[1]: out.append(f"H{fmt(x,prec)}")
                elif pos and r[0] == pos[0]: out.append(f"V{fmt(y,prec)}")
                else: out.append(f"L{fmt(x,prec)} {fmt(y,prec)}")
                pos = r
            elif c in ("C", "Q"):
                out.append(c + " ".join(f"{fmt(x,prec)} {fmt(y,prec)}" for x, y in pts))
                pos = (round(pts[-1][0], prec), round(pts[-1][1], prec))
            elif c == "Z":
                out.append("Z")
    return "".join(out).replace(" -", "-")

def move(subs, dx, dy, k=1.0):
    return [[(c, [(x * k + dx, y * k + dy) for x, y in pts]) for c, pts in s] for s in subs]

def bbox(subs, steps=24):
    xs, ys = [], []
    for sub in subs:
        pos = None
        for c, pts in sub:
            if c in ("M", "L"):
                pos = pts[0]; xs.append(pos[0]); ys.append(pos[1])
            elif c == "C":
                p0 = pos; p1, p2, p3 = pts
                for i in range(steps + 1):
                    t = i / steps; m = 1 - t
                    xs.append(m**3*p0[0] + 3*m*m*t*p1[0] + 3*m*t*t*p2[0] + t**3*p3[0])
                    ys.append(m**3*p0[1] + 3*m*m*t*p1[1] + 3*m*t*t*p2[1] + t**3*p3[1])
                pos = p3
            elif c == "Q":
                p0 = pos; p1, p2 = pts
                for i in range(steps + 1):
                    t = i / steps; m = 1 - t
                    xs.append(m*m*p0[0] + 2*m*t*p1[0] + t*t*p2[0]); ys.append(m*m*p0[1] + 2*m*t*p1[1] + t*t*p2[1])
                pos = p2
    return (min(xs), min(ys), max(xs), max(ys))

def union_bbox(boxes):
    boxes = [b for b in boxes if b]
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))

# ════════════════════════════════════════════════════════════════════════════════
# İşaret
# ════════════════════════════════════════════════════════════════════════════════
K = 0.5522847498  # çeyrek çember için Bézier katsayısı

def rounded_square(cx, cy, s, angle_deg, r):
    """Merkezi (cx,cy), kenarı s, köşe yarıçapı r olan, angle kadar (saat yönünde) döndürülmüş kare."""
    a = math.radians(angle_deg); ca, sa = math.cos(a), math.sin(a)
    T = lambda x, y: (cx + x * ca - y * sa, cy + x * sa + y * ca)
    h = s / 2.0; k = K * r
    return [
        ("M", [T(-h + r, -h)]), ("L", [T(h - r, -h)]),
        ("C", [T(h - r + k, -h), T(h, -h + r - k), T(h, -h + r)]), ("L", [T(h, h - r)]),
        ("C", [T(h, h - r + k), T(h - r + k, h), T(h - r, h)]), ("L", [T(-h + r, h)]),
        ("C", [T(-h + r - k, h), T(-h, h - r + k), T(-h, h - r)]), ("L", [T(-h, -h + r)]),
        ("C", [T(-h, -h + r - k), T(-h + r - k, -h), T(-h + r, -h)]), ("Z", []),
    ]

def isaret(cx, cy, s, kare=1.0, ret_kare=1.0, itme=ITME):
    """Ana işaret. (cx,cy) halka merkezi, s kare kenarı. (mürekkep_kareler, ret_karesi) döner.
    kare / ret_kare: karelerin s'ye oranı (ana işarette 1), itme: ret karesinin dışarı itilmesi / s."""
    ink, red = [], []
    for k in range(KARE_SAYISI):
        ang = k * 360.0 / KARE_SAYISI
        rr = HALKA * s + (itme * s if k == RET_SIRA else 0.0)
        x = cx + rr * math.sin(math.radians(ang)); y = cy - rr * math.cos(math.radians(ang))
        ts = s * (ret_kare if k == RET_SIRA else kare)
        (red if k == RET_SIRA else ink).append(rounded_square(x, y, ts, ang, KOSE * ts))
    return ink, red

# Küçük boy (32 px altı) ve sekme ikonu için optik düzeltme: AYNI 15 KARE. Kareler biraz küçültülüp
# aralar açılır, ret karesi tam boyda kalıp biraz daha dışarı itilir; küçükte kareler birbirine karışmaz.
KUCUK_KARE = 0.86
KUCUK_RET_KARE = 1.0
KUCUK_ITME = 0.95

def kucuk_isaret(cx, cy, s):
    return isaret(cx, cy, s, kare=KUCUK_KARE, ret_kare=KUCUK_RET_KARE, itme=KUCUK_ITME)

def kutuya_sigdir(fn, kutu, pay):
    """İşareti kutu×kutu alana, kenarlarda en az 'pay' kadar boşluk kalacak biçimde ortalar."""
    ink, red = fn(0.0, 0.0, 1.0)
    b = union_bbox([bbox(ink), bbox(red)])
    s = (kutu - 2 * pay) / max(b[2] - b[0], b[3] - b[1])
    return fn(kutu / 2 - s * (b[0] + b[2]) / 2, kutu / 2 - s * (b[1] + b[3]) / 2, s)

# ════════════════════════════════════════════════════════════════════════════════
# Yazı (HarfBuzz ile dizilim + fontTools ile dış hatlar)
# ════════════════════════════════════════════════════════════════════════════════
def fontlari_hazirla():
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    for ad, url in FONT_URL.items():
        p = FONT_DIR / ad
        if not p.exists():
            print("indiriliyor:", ad)
            urllib.request.urlretrieve(url, p)

class Yazi:
    def __init__(self, path):
        import uharfbuzz as hb
        from fontTools.ttLib import TTFont
        self.hb = hb
        self.tt = TTFont(str(path)); self.gs = self.tt.getGlyphSet(); self.upm = self.tt["head"].unitsPerEm
        self.order = self.tt.getGlyphOrder()
        self.font = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
        os2 = self.tt["OS/2"]; self.cap = os2.sCapHeight

    def yol(self, metin, boyut, x, taban, izleme_px=0.0, ek=None):
        """izleme_px: her harften sonra eklenen boşluk (px). ek: {karakter_sırası: em} ek aralık."""
        from fontTools.pens.basePen import BasePen
        from fontTools.pens.transformPen import TransformPen
        class Pen(BasePen):
            def __init__(s): super().__init__(None); s.subs = []; s.cur = None
            def _moveTo(s, p): s.cur = [("M", [p])]; s.subs.append(s.cur)
            def _lineTo(s, p): s.cur.append(("L", [p]))
            def _curveToOne(s, a, b, c): s.cur.append(("C", [a, b, c]))
            def _qCurveToOne(s, a, b): s.cur.append(("Q", [a, b]))
            def _closePath(s): s.cur.append(("Z", []))
            def _endPath(s): pass
        buf = self.hb.Buffer(); buf.add_str(metin); buf.guess_segment_properties(); buf.language = "tr"
        self.hb.shape(self.font, buf, {"kern": True, "liga": False})
        sc = boyut / self.upm; pen = Pen(); px = x
        infos, poss = buf.glyph_infos, buf.glyph_positions
        for i, (inf, pos) in enumerate(zip(infos, poss)):
            tp = TransformPen(pen, (sc, 0, 0, -sc, px + pos.x_offset * sc, taban - pos.y_offset * sc))
            self.gs[self.order[inf.codepoint]].draw(tp)
            px += pos.x_advance * sc
            if i < len(infos) - 1:
                px += izleme_px
                if ek and inf.cluster in ek: px += ek[inf.cluster] * boyut
        return pen.subs

# Kesme işaretini rakama yaslamak için ek aralıklar (tracking'li büyük harf dizisinde)
def slogan_ek(metin):
    i = metin.find("\u2019")
    return {i - 1: -0.16, i: -0.10} if i > 0 else None

# ════════════════════════════════════════════════════════════════════════════════
# Logo kurguları (özgün dosyalardaki ölçüler korunarak)
# ════════════════════════════════════════════════════════════════════════════════
def kurgu(tur, slogan, serif, sans):
    """Katmanları döner: {'isaret': [...], 'ret': [...], 'ad': [...], 'slogan': [...]} (tasarım birimleri)."""
    L = {"isaret": [], "ret": [], "ad": [], "slogan": []}
    if tur == "isaret":
        L["isaret"], L["ret"] = isaret(0, 0, 128.0 / 7.6188)   # doğal boy: 128 px yükseklik
    elif tur == "yatay":                       # özgün: 560×120 tuval, s=12, halka merkezi (62,60)
        L["isaret"], L["ret"] = isaret(62, 60, 12.0)
        L["ad"] = serif.yol(AD, 34, 130, 58, izleme_px=0.5)
        if slogan:
            m = SLOGAN[slogan]; L["slogan"] = sans.yol(m, 13, 131, 84, izleme_px=2.6, ek=slogan_ek(m))
    elif tur == "cubuk":                       # özgün: 378×100 tuval, s=10, halka merkezi (50,52)
        L["isaret"], L["ret"] = isaret(50, 52, 10.0)
        L["ad"] = serif.yol(AD, 52, 112, 68, izleme_px=0.4)
    elif tur == "dikey":                       # özgün: 360×250 tuval, s=14, ortalanmış
        L["isaret"], L["ret"] = isaret(180, 70, 14.0)
        ad = serif.yol(AD, 38, 0, 186, izleme_px=0.5)
        b = bbox(ad); L["ad"] = move(ad, 180 - (b[0] + b[2]) / 2, 0)
        if slogan:
            m = SLOGAN[slogan]; sl = sans.yol(m, 13, 0, 216, izleme_px=2.6, ek=slogan_ek(m))
            b = bbox(sl); L["slogan"] = move(sl, 180 - (b[0] + b[2]) / 2, 0)
    return L

def svg_yaz(L, renkler, etiket, pad=0.0, prec=2):
    """Katmanları sıkı kırpılmış bir SVG'ye çevirir. renkler: (mürekkep, ret, slogan)."""
    bx = union_bbox([bbox(v) for v in L.values() if v])
    dx, dy = -bx[0] + pad, -bx[1] + pad
    W, H = bx[2] - bx[0] + 2 * pad, bx[3] - bx[1] + 2 * pad
    ink, red, tag = renkler
    parts = []
    if L["isaret"]: parts.append(f'<path fill="{ink}" d="{to_d(move(L["isaret"], dx, dy), prec)}"/>')
    if L["ret"]:    parts.append(f'<path fill="{red}" d="{to_d(move(L["ret"], dx, dy), prec)}"/>')
    if L["ad"]:     parts.append(f'<path fill="{ink}" d="{to_d(move(L["ad"], dx, dy), prec)}"/>')
    if L["slogan"]: parts.append(f'<path fill="{tag}" d="{to_d(move(L["slogan"], dx, dy), prec)}"/>')
    w, h = fmt(W), fmt(H)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{etiket}"><title>{etiket}</title>' + "".join(parts) + "</svg>\n"), (W, H)

TEMA = {
    "":       lambda: (RENK["murekkep"], RENK["ret"], RENK["ikincil"]),
    "-koyu":  lambda: (RENK["acik"], RENK["ret_acik"], RENK["ikincil_acik"]),
    "-siyah": lambda: ("#000000", "#000000", "#000000"),
    "-beyaz": lambda: ("#FFFFFF", "#FFFFFF", "#FFFFFF"),
}

LOGOLAR = [  # dosya adı, tür, slogan, erişilebilirlik etiketi
    ("logo-cubuk-b", "cubuk", None, AD),
    ("logo-yatay-a", "yatay", "a", f"{AD} — {SLOGAN_ETIKET['a']}"),
    ("logo-yatay-b", "yatay", "b", f"{AD} — {SLOGAN_ETIKET['b']}"),
    ("logo-dikey-a", "dikey", "a", f"{AD} — {SLOGAN_ETIKET['a']}"),
    ("logo-dikey-b", "dikey", "b", f"{AD} — {SLOGAN_ETIKET['b']}"),
    ("logo-dikey-sade", "dikey", None, AD),
    ("isaret", "isaret", None, AD),
]

# ════════════════════════════════════════════════════════════════════════════════
# İkonlar
# ════════════════════════════════════════════════════════════════════════════════
def ikon_svg(boyut, zemin, isaret_rengi, ret_rengi, kose_orani=0.0, dolgu=None, olcek=0.0862):
    """Kare uygulama ikonu. Halka tuvalin merkezinde (dairesel maskelerde eş merkezli durur).
    olcek: s / boyut. İşaretin en uzak noktası (ret karesi) merkezden 4,36·s uzaktadır. Maskable ikonda 0.072 →
    0,31×boyut: görselin yalnızca ortadaki 72/108'ini gösteren Android başlatıcılarında (Samsung) da kırpılmaz."""
    s = olcek * boyut; c = boyut / 2.0
    ink, red = isaret(c, c, s)
    bg = ""
    if zemin:
        rx = f' rx="{fmt(kose_orani * boyut)}"' if kose_orani else ""
        bg = f'<rect width="{boyut}" height="{boyut}"{rx} fill="{zemin}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {boyut} {boyut}" width="{boyut}" height="{boyut}">'
            f'{bg}<path fill="{isaret_rengi}" d="{to_d(ink, 3)}"/><path fill="{ret_rengi}" d="{to_d(red, 3)}"/></svg>\n')

def favicon_svg():
    """Sekme ikonu: mürekkep zeminli yuvarlak kare + 15 kareli küçük boy işaret. Zemin sayesinde açık ve
    koyu sekme çubuğunda, medya sorgusuna gerek kalmadan okunur (Safari SVG ikonlarda koyu mod ayarını yok sayıyor)."""
    ink, red = kutuya_sigdir(kucuk_isaret, 32.0, 3.4)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">'
            f'<rect width="32" height="32" rx="7" fill="{RENK["murekkep"]}"/>'
            f'<path fill="{RENK["acik"]}" d="{to_d(ink, 3)}"/><path fill="{RENK["ret_acik"]}" d="{to_d(red, 3)}"/></svg>\n')

def kucuk_isaret_svg(koyu=False):
    ink, red = kucuk_isaret(0.0, 0.0, 128.0 / 7.6188)
    L = {"isaret": ink, "ret": red, "ad": [], "slogan": []}
    return svg_yaz(L, TEMA["-koyu" if koyu else ""](), AD, prec=3)[0]

# ════════════════════════════════════════════════════════════════════════════════
# Raster ve dosya biçimleri
# ════════════════════════════════════════════════════════════════════════════════
def png(svg, w=None, h=None, zemin=None):
    import resvg_py
    from PIL import Image
    data = bytes(resvg_py.svg_to_bytes(svg_string=svg, width=w, height=h, background=zemin))
    return Image.open(io.BytesIO(data)).convert("RGBA")

def png_kaydet(img, path, opak=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if opak:
        img = img.convert("RGB")
    img.save(path, optimize=True)

def ico_yaz(images, path):
    """Çok boyutlu ICO (32 bit BGRA BMP girdileri — en eski Windows/IE dahil her yerde açılır)."""
    entries, blobs = [], []
    for im in images:
        w, h = im.size
        px = im.convert("RGBA").tobytes()
        rows = [px[y * w * 4:(y + 1) * w * 4] for y in range(h)]
        xor = bytearray()
        for row in reversed(rows):                                  # BMP satırları alttan üste
            for x in range(w):
                r, g, b, a = row[x * 4:x * 4 + 4]; xor += bytes((b, g, r, a))
        mask_row = ((w + 31) // 32) * 4
        andm = bytearray()
        for row in reversed(rows):
            bits = bytearray(mask_row)
            for x in range(w):
                if row[x * 4 + 3] == 0: bits[x // 8] |= 0x80 >> (x % 8)
            andm += bits
        hdr = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0, len(xor) + len(andm), 0, 0, 0, 0)
        blob = hdr + bytes(xor) + bytes(andm)
        entries.append((w, h, blob)); blobs.append(blob)
    out = bytearray(struct.pack("<HHH", 0, 1, len(entries)))
    offset = 6 + 16 * len(entries)
    for w, h, blob in entries:
        out += struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, 1, 32, len(blob), offset); offset += len(blob)
    for blob in blobs: out += blob
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(bytes(out))

def vektor_baski(svg, pdf_path, eps_path):
    try:
        import cairosvg
    except Exception as e:  # Cairo yoksa bir kez uyar, atla
        if not getattr(vektor_baski, "uyarildi", False):
            print("  (PDF/EPS atlandı: cairosvg kullanılamıyor —", e, ")"); vektor_baski.uyarildi = True
        return False
    pdf_path.parent.mkdir(parents=True, exist_ok=True); eps_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), write_to=str(pdf_path))
    cairosvg.svg2eps(bytestring=svg.encode("utf-8"), write_to=str(eps_path))
    return True

def tuvale_ortala(svg, W, H, zemin, alan):
    """Logoyu düz renk zeminli bir tuvalin ortasına yerleştirir (paylaşım görselleri için)."""
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg); lw, lh = float(m.group(1)), float(m.group(2))
    k = min(alan[0] / lw, alan[1] / lh)
    tx, ty = (W - lw * k) / 2, (H - lh * k) / 2
    inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", svg.strip())
    inner = re.sub(r"<title>.*?</title>", "", inner)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<rect width="{W}" height="{H}" fill="{zemin}"/>'
            f'<g transform="translate({fmt(tx,3)} {fmt(ty,3)}) scale({fmt(k,5)})">{inner}</g></svg>')

# ════════════════════════════════════════════════════════════════════════════════
# Üretim
# ════════════════════════════════════════════════════════════════════════════════
def main():
    fontlari_hazirla()
    serif = Yazi(FONT_DIR / "SourceSerif4-Semibold.otf")
    sans = Yazi(FONT_DIR / "SourceSans3-Regular.otf")
    out = CIKTI
    (out / "svg" / "tek-renk").mkdir(parents=True, exist_ok=True)
    olcu = {}

    # 1) Vektör logolar ----------------------------------------------------------
    for ad, tur, slogan, etiket in LOGOLAR:
        L = kurgu(tur, slogan, serif, sans)
        for tema, renk in TEMA.items():
            prec = 3 if tur == "isaret" else 2
            svg, (W, H) = svg_yaz(L, renk(), etiket, prec=prec)
            hedef = out / "svg" / ("tek-renk" if tema in ("-siyah", "-beyaz") else "") / f"{ad}{tema}.svg"
            hedef.write_text(svg, encoding="utf-8")
            olcu[f"{ad}{tema}"] = (svg, W, H)
            # baskı: PDF + EPS
            vektor_baski(svg, out / "baski" / "pdf" / f"{ad}{tema}.pdf", out / "baski" / "eps" / f"{ad}{tema}.eps")
    # geriye dönük uyumluluk: tek renk mürekkep işaret
    L = kurgu("isaret", None, serif, sans)
    svg, _ = svg_yaz(L, (RENK["murekkep"],) * 3, AD, prec=3)
    (out / "svg" / "isaret-tek-renk.svg").write_text(svg, encoding="utf-8")
    # küçük boy işaret
    (out / "svg" / "isaret-kucuk.svg").write_text(kucuk_isaret_svg(False), encoding="utf-8")
    (out / "svg" / "isaret-kucuk-koyu.svg").write_text(kucuk_isaret_svg(True), encoding="utf-8")

    # 2) PNG'ler ------------------------------------------------------------------
    for ad, tur, slogan, etiket in LOGOLAR:
        for tema in ("", "-koyu", "-siyah", "-beyaz"):
            svg, W, H = olcu[f"{ad}{tema}"]
            alt = "tek-renk" if tema in ("-siyah", "-beyaz") else ""
            boylar = (128, 512, 2048) if tur == "isaret" else (600, 2400)
            if alt: boylar = boylar[-1:]
            for uzun in boylar:
                img = png(svg, w=uzun) if W >= H else png(svg, h=uzun)
                png_kaydet(img, out / "png" / alt / f"{ad}{tema}-{uzun}.png")

    # 3) Web ikonları --------------------------------------------------------------
    web = out / "web"; web.mkdir(parents=True, exist_ok=True)
    fav = favicon_svg(); (web / "favicon.svg").write_text(fav, encoding="utf-8")
    ico_yaz([png(fav, w=16), png(fav, w=32), png(fav, w=48)], web / "favicon.ico")
    m, kz, ra = RENK["murekkep"], RENK["acik"], RENK["ret_acik"]
    png_kaydet(png(ikon_svg(180, m, kz, ra, olcek=0.0905)), web / "apple-touch-icon.png", opak=True)
    for b in (192, 512):
        png_kaydet(png(ikon_svg(b, m, kz, ra, kose_orani=0.22, olcek=0.0905)), web / f"icon-{b}.png")
        png_kaydet(png(ikon_svg(b, m, kz, ra, olcek=0.072)), web / f"icon-maskable-{b}.png", opak=True)
    manifest = {
        "name": AD, "short_name": AD, "description": "1946’dan bu yana BM Güvenlik Konseyinde kullanılan vetolar, kaynaklarıyla.",
        "lang": "tr", "id": BASLANGIC, "start_url": BASLANGIC, "scope": "/", "display": "standalone",
        "theme_color": RENK["kagit"], "background_color": RENK["kagit"],
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/icon-maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
            {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2)
    (web / "site.webmanifest").write_text(manifest_json + "\n", encoding="utf-8")
    # paylaşım görseli (1200×630): dikey sloganlı logo ortada — kare kırpan önizlemelerde de bütün kalır
    svg, W, H = olcu["logo-dikey-a"]
    png_kaydet(png(tuvale_ortala(svg, 1200, 630, RENK["kagit"], (640, 460))), web / "og-image.png", opak=True)
    head = HEAD.format(kagit=RENK["kagit"], site=SITE, ad=AD, slogan=SLOGAN_ETIKET["a"])
    (web / "head-etiketleri.html").write_text(head, encoding="utf-8")

    # 4) Sosyal medya profil görselleri (daire kırpmaya göre eş merkezli) --------------------
    sos = out / "sosyal"
    png_kaydet(png(ikon_svg(1080, RENK["kagit"], RENK["murekkep"], RENK["ret"], olcek=0.0805)),
               sos / "profil-kagit-1080.png", opak=True)
    png_kaydet(png(ikon_svg(1080, RENK["murekkep"], kz, ra, olcek=0.0805)), sos / "profil-murekkep-1080.png", opak=True)
    # 5) Belgeler ve önizleme ------------------------------------------------------
    kullanim_yaz(out, head, manifest_json)
    onizleme_yaz(out)
    pano_yaz(out)
    print("tamam →", out)

HEAD = """<!-- Veto Atlası — her sayfanın <head> bölümüne. Dosyalar sitenin kök klasöründe olmalı. -->
<!-- ?v=2 eski (pikselli) ikonların tarayıcı önbelleğinden düşmesi içindir; ikonu yeniden değiştirirsen sayıyı artır. -->
<link rel="icon" href="/favicon.ico?v=2" sizes="32x32">
<link rel="icon" href="/favicon.svg?v=2" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="{kagit}">

<!-- Bağlantı paylaşım önizlemesi (X, WhatsApp, LinkedIn, Telegram) -->
<meta property="og:site_name" content="{ad}">
<meta property="og:image" content="{site}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{ad} — {slogan}">
<meta name="twitter:card" content="summary_large_image">
"""

# ════════════════════════════════════════════════════════════════════════════════
# Belgeler: KULLANIM.md, onizleme.html, pano.png
# ════════════════════════════════════════════════════════════════════════════════
from string import Template

AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

def rgb(h):
    h = h.lstrip("#"); return ", ".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))

def kullanim_yaz(out, head, manifest_json):
    d = dict(RENK); d.update({f"{k}_rgb": rgb(v) for k, v in RENK.items()})
    d.update(head=head.strip(), manifest=manifest_json.strip())
    (out / "KULLANIM.md").write_text(Template(KULLANIM).safe_substitute(d), encoding="utf-8")

def onizleme_yaz(out):
    import base64, datetime
    from PIL import Image
    ico = Image.open(out / "web" / "favicon.ico"); d = dict(RENK)
    for n in (16, 32, 48):
        ico.size = (n, n); b = io.BytesIO(); ico.convert("RGBA").save(b, "PNG")
        d[f"ico{n}"] = "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
    t = datetime.date.today(); d["tarih"] = f"{AYLAR[t.month - 1]} {t.year}"
    (out / "onizleme.html").write_text(Template(ONIZLEME).safe_substitute(d), encoding="utf-8")

def pano_yaz(out):
    """onizleme.html'in tam sayfa görüntüsü (Playwright + Chromium kuruluysa)."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            tarayici = p.chromium.launch()
            sayfa = tarayici.new_page(viewport={"width": 1200, "height": 900}, device_scale_factor=2)
            sayfa.goto((out / "onizleme.html").resolve().as_uri(), wait_until="networkidle")
            sayfa.evaluate("document.fonts.ready.then(() => true)")
            sayfa.screenshot(path=str(out / "pano.png"), full_page=True)
            tarayici.close()
        from PIL import Image
        Image.open(out / "pano.png").convert("RGB").save(out / "pano.png", optimize=True)
    except Exception as e:
        print("  (pano.png atlandı:", e, ")")

KULLANIM = """# Veto Atlası — logo paketi

Bu paketteki bütün dosyalar tek bir kaynaktan, `kaynak/uret.py` betiğinden üretildi. Logolar gerçek vektördür: yazılar yola (path) çevrilmiştir, hiçbir cihazda yazı tipine ihtiyaç duymaz ve her boyutta keskin görünür. Dosyalar boşluksuz kırpılmıştır; logonun çevresindeki boşluğu sayfa düzeni verir.

Bütün dosyaları açık ve koyu zeminde, küçük boyutlarda ve ikon maskeleri içinde görmek için `onizleme.html` dosyasını tarayıcıda açın. `pano.png` aynı sayfanın görüntüsüdür.

## Hangi dosya nerede kullanılır

| İhtiyaç | Dosya |
|---|---|
| Site başlığı | `svg/logo-cubuk-b.svg` |
| Yatay alanlar: sayfa içi, sunum, belge başlığı | `svg/logo-yatay-a.svg`, `svg/logo-yatay-b.svg` |
| Kare ya da dikey alanlar: kapak, poster, afiş | `svg/logo-dikey-a.svg`, `svg/logo-dikey-b.svg`, `svg/logo-dikey-sade.svg` |
| Yalnızca işaret, 32 px ve üstü (telefonda her boyut) | `svg/isaret.svg` |
| Yalnızca işaret, 32 px'in altı | `svg/isaret-kucuk.svg` |
| Filigran, antetli kâğıt | `svg/isaret-tek-renk.svg` |
| Word, PowerPoint, e-posta imzası, SVG kabul etmeyen yerler | `png/` — 600 px küçük kullanım için, 2400 px belge ve sunum için |
| Matbaa, tabela, promosyon ürünü | `baski/pdf/` ya da `baski/eps/` |
| Tek renkli baskı: kaşe, gofre, kazıma, fotokopi | `-siyah` ve `-beyaz` dosyalar (`svg/tek-renk/`, `png/tek-renk/`, `baski/`) |
| Site ikonları ve paylaşım görseli | `web/` klasörünün tamamı |
| Instagram, X ve LinkedIn profil fotoğrafı | `sosyal/` |

Adında `-koyu` geçen dosyalar koyu zemin içindir. A sürümlerinde slogan "Dünya 5’ten büyüktür", B sürümlerinde "Daha adil bir dünya mümkün"dür. `cubuk` ve `sade` sürümlerinde slogan yoktur.

## Siteye kurulum

1. `web/` klasöründeki bütün dosyaları sitenin kök klasörüne, `index.html`'in yanına kopyalayın. Eski `isaret-*.png`, `ikon-maskable-*.png` ve eski `favicon.ico` dosyalarını silebilirsiniz.
2. Her sayfanın `<head>` bölümündeki eski ikon satırlarını silin ve yerine `web/head-etiketleri.html` içeriğini yapıştırın:

```html
${head}
```

3. Tarayıcılar ikonları uzun süre önbellekte tutar. Bağlantılardaki `?v=2` eski ikonların düşmesini sağlar; ikonu ileride yeniden değiştirirseniz bu sayıyı artırın. Ana ekrana eklenmiş kısayollar ise ikonlarını hiç güncellemez; yayından sonra eski kısayolu silip siteyi yeniden ekleyin.

Eski kurulumdaki `sizes="any"` ayarı, Chrome'un vektör SVG yerine raster ICO dosyasını seçmesine yol açıyordu. Yeni satırlarda ICO yalnızca yedek olarak kalır; Chrome, Edge, Firefox ve Safari 26 ve üstü SVG ikonu kullanır.

Logolar artık boşluksuz kırpıldığı için, sitede logoya CSS ile yükseklik verdiyseniz aynı yükseklikte logo yaklaşık %30 büyük görünür. Eski boyutu korumak için yüksekliği %24 azaltın (örneğin 56 px yerine 42 px). Site başlığındaki logo en az 40 px yükseklikte kalmalıdır.

`site.webmanifest` içeriği:

```json
${manifest}
```

## Renkler

| Ad | HEX | RGB | Kullanım |
|---|---|---|---|
| Mürekkep | `${murekkep}` | ${murekkep_rgb} | İşaret, logo yazısı, koyu zemin |
| Ret kırmızısı | `${ret}` | ${ret_rgb} | Yalnızca ayrılan kare |
| Kâğıt | `${kagit}` | ${kagit_rgb} | Açık zemin |
| İkincil | `${ikincil}` | ${ikincil_rgb} | Slogan |
| Kâğıt tonu, koyu zeminde | `${acik}` | ${acik_rgb} | Koyu zeminde işaret ve yazı |
| Ret, koyu zeminde | `${ret_acik}` | ${ret_acik_rgb} | Koyu zeminde ayrılan kare |
| İkincil, koyu zeminde | `${ikincil_acik}` | ${ikincil_acik_rgb} | Koyu zeminde slogan |

Bu değerler sitenin CSS değişkenleriyle (`--murekkep`, `--ret`, `--zemin`, `--ikincil`) aynıdır. Koyu zemin tonları ayrı renkler değildir; aynı renklerin lacivert üzerinde yeterli kontrastla okunması için açılmış karşılıklarıdır.

Baskı için: PDF ve EPS dosyaları RGB renk kullanır. Matbaaya bu dosyaları ve HEX kodlarını verin; kullanacakları kâğıda göre CMYK dönüşümünü kendi profilleriyle yapıp prova göstermelerini isteyin. Kâğıt rengi basılmaz; krem ya da fildişi kâğıt seçilebilir.

## Kurallar

- **Boşluk:** Logonun çevresinde en az bir kare kenarı kadar boş alan bırakın. Kare, işaretteki tek bir karedir.
- **Ekranda en küçük boyut:** Sloganlı yatay logo en az 240 px, sloganlı dikey logo en az 160 px genişlikte kullanılır; daha küçükte slogan okunmaz, sloganı olmayan sürüme geçin. Site başlığındaki logo en az 40 px yüksekliktedir. İşaret 32 px'ten küçük kullanılacaksa `isaret-kucuk.svg` kullanılır. Telefonlar 2–3 kat piksel yoğunluğuyla çizdiği için sayfa içinde `isaret.svg` her boyutta nettir. İki dosya da aynı 15 kareden oluşur; küçük sürümde kareler biraz küçük, aralar biraz geniştir.
- **Baskıda en küçük boyut:** Sloganlı yatay logo 40 mm, sloganlı dikey logo ve sloganı olmayan logolar 25 mm, işaret 12 mm genişliğin altına inmez. Daha küçük baskıda (rozet, kalem) `isaret-kucuk.svg` kullanılır.
- Kırmızı kare başka renge boyanmaz ve yeri değiştirilmez. Tek renk gereken yerde `-siyah`, `-beyaz` ya da `isaret-tek-renk` dosyaları kullanılır.
- Logo esnetilmez, döndürülmez, öğeleri yeniden düzenlenmez; gölge, degrade, kontur ya da 3B efekt verilmez.
- Fotoğraf ya da desen üzerinde logo yalnızca sakin, düz bir alana konur; zemin karışıksa `-beyaz` sürüm kullanılır.

## Sekme ve uygulama ikonları

- `favicon.svg` ve `favicon.ico`: Sekme ikonu lacivert zeminli bir karedir. Şeffaf zeminli lacivert halka koyu sekme çubuklarında kayboluyordu ve Safari, SVG ikonun içindeki koyu mod ayarını uygulamıyor. Zeminli ikon açık ve koyu temada aynı netlikte görünür.
- Sekme ikonunda da aynı 15 kare vardır; küçük boy sürümdeki gibi kareler biraz küçültülüp aralar açılmıştır. `favicon.ico` 16, 32 ve 48 px görüntüleri içerir.
- `apple-touch-icon.png` (180 px): iPhone ve iPad ana ekranı. Zemini opaktır; iOS köşeleri kendisi yuvarlar.
- `icon-192.png`, `icon-512.png`: Android'de ve masaüstünde yüklenen uygulamanın ikonu. `icon-maskable-192.png`, `icon-maskable-512.png`: Android ana ekran ikonu. Samsung gibi bazı başlatıcılar bu görselin yalnızca ortadaki üçte ikisini gösterir; işaret o alanın içinde kalacak boyda çizildi, halka ve kırmızı kare kırpılmaz.
- `og-image.png` (1200×630): Bağlantı paylaşıldığında görünen önizleme. Logo ortada durduğu için görseli kare kırpan uygulamalarda da bütün kalır.

## Bu sürümde düzeltilenler

- İşaret bütün logolarda aynı oranlarla yeniden kuruldu; eski dosyalarda kurgudan kurguya küçük farklar vardı.
- Logolar boşluksuz kırpıldı; eski yatay logonun genişliğinin %44'ü boştu.
- Pakette iki farklı renk seti vardı; hepsi sitenin renklerine eşitlendi.
- "Veto Atlası" yazısında yazı tipinin harf çifti düzeltmeleri (kerning) açıldı; "V" ile "e" arasındaki boşluk kapandı. Slogandaki düz kesme işareti, rakama yaslanan tipografik kesme işaretiyle (’) değiştirildi. İşaretin ve harflerin biçimi değişmedi.
- Küçük boy işaret yeniden çizildi. Eski sürümde iri kareler üst üste binip halkayı kalın, testere dişli bir kurdeleye çeviriyordu; işaret telefonda başka bir şeye benziyordu. Yeni sürüm aynı 15 kareden oluşur; yalnızca kareler biraz küçültülüp aralar açıldı.
- iPhone ikonu artık opak; eskisinde iOS şeffaf alanı siyaha boyadığı için işaret görünmüyordu.
- Android ana ekran ikonu yeniden çizildi. Eskisinde aynı görsel hem normal hem maskable ikon olarak kullanılıyordu; başlatıcı görselin ortasını büyüterek gösterdiği için halkanın kenarları ve kırmızı kare kesiliyordu.

## Yeniden üretmek

Renkleri, slogan metnini ya da oranları değiştirmek için `kaynak/uret.py` dosyasının başındaki AYARLAR bölümünü düzenleyip paketin kök klasöründe şunu çalıştırın:

    pip install fonttools uharfbuzz resvg-py pillow cairosvg
    python kaynak/uret.py

Betik paketi bulunduğu yerde baştan üretir. Yazı tipleri `kaynak/fonts/` içindedir (Source Serif 4 ve Source Sans 3, SIL Open Font License). Cairo kurulamazsa PDF/EPS adımı atlanır; Playwright kuruluysa `pano.png` da yenilenir.
"""

ONIZLEME = """<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Veto Atlası — logo paketi</title>
<link rel="icon" href="web/favicon.ico" sizes="32x32">
<link rel="icon" href="web/favicon.svg" type="image/svg+xml">
<style>
@font-face{font-family:"Source Serif 4";src:url("kaynak/fonts/SourceSerif4-Semibold.otf") format("opentype");font-weight:600}
@font-face{font-family:"Source Sans 3";src:url("kaynak/fonts/SourceSans3-Regular.otf") format("opentype");font-weight:400}
:root{--kagit:${kagit};--murekkep:${murekkep};--ikincil:${ikincil};--ikincil-koyu:${ikincil_acik};--cizgi:#E1DBCF}
*{box-sizing:border-box}
html{background:var(--kagit)}
body{margin:0;color:var(--murekkep);font:16px/1.5 "Source Sans 3",system-ui,sans-serif}
img{display:block;max-width:100%;height:auto}
.kap{max-width:1200px;margin:0 auto;padding:64px 56px 88px}
header{display:flex;justify-content:space-between;align-items:flex-end;gap:32px;padding-bottom:36px;border-bottom:1px solid var(--cizgi)}
header img{height:80px;width:auto}
header p{margin:0;text-align:right;color:var(--ikincil);font-size:15px}
section{margin-top:64px}
h2{font:600 24px/1.25 "Source Serif 4",Georgia,serif;margin:0 0 6px}
.not{margin:0 0 24px;color:var(--ikincil);font-size:15px;max-width:72ch}
.izgara{display:grid;gap:1px;background:var(--cizgi);border:1px solid var(--cizgi)}
.izgara+.izgara{border-top:0}
.k1{grid-template-columns:1fr}.k2{grid-template-columns:repeat(2,1fr)}.k3{grid-template-columns:repeat(3,1fr)}.k4{grid-template-columns:repeat(4,1fr)}
.hucre{background:var(--kagit);padding:40px 32px 18px;display:flex;flex-direction:column;gap:28px;min-height:200px}
.hucre .gorsel{flex:1;display:flex;align-items:center}
.hucre .serit{align-items:flex-end;gap:40px;flex-wrap:wrap}
.orta .gorsel{justify-content:center}
.hucre .gorsel img{width:auto}
.etiket{font-size:13px;color:var(--ikincil)}
.izgara.koyu{background:#0A1322;border-color:#0A1322}
.koyu .hucre{background:var(--murekkep)}
.koyu .etiket,.koyu figcaption{color:var(--ikincil-koyu)}
.hucre.beyaz{background:#FFFFFF}
.hucre.gri{background:#3B3F46}
.hucre.gri .etiket{color:#C9CDD3}
figure{margin:0;display:flex;flex-direction:column;align-items:center;gap:12px}
figcaption{font-size:13px;color:var(--ikincil);text-align:center}
.ayrac{width:1px;align-self:stretch;background:var(--cizgi)}
.koyu .ayrac{background:#2A3A57}
.tarayici{border-radius:10px 10px 0 0;padding:8px 10px 0;display:flex;gap:2px;align-items:flex-end}
.tarayici.acik{background:#DEE1E6}.tarayici.karanlik{background:#202124}
.sekme{display:flex;align-items:center;gap:9px;height:36px;padding:0 14px;border-radius:9px 9px 0 0;font-size:13px;min-width:210px}
.acik .sekme{background:#FFFFFF;color:#1F1F1F}.karanlik .sekme{background:#35363A;color:#E8EAED}
.tarayici .sekme.pasif{background:transparent;min-width:150px}
.acik .sekme.pasif{color:#5F6368}.karanlik .sekme.pasif{color:#9AA0A6}
.hucre .sekme img{width:16px;height:16px}
.sekme .kapat{margin-left:auto;opacity:.6}
.adres{height:42px;border-radius:0 0 10px 10px}
.acik+.adres{background:#FFFFFF;border:1px solid #DEE1E6;border-top:0}
.karanlik+.adres{background:#35363A}
.hucre .piksel img{image-rendering:pixelated;width:96px;height:96px}
.ios{border-radius:22.5%}
.daire{clip-path:circle(33.3% at 50% 50%)}
.yumusak{clip-path:inset(16.7% round 23%)}
.yuvarlak{border-radius:50%}
.renkler{display:grid;grid-template-columns:repeat(4,1fr);gap:28px 24px}
.renk .ornek{height:88px;border:1px solid var(--cizgi)}
.renk b{display:block;font:600 16px/1.3 "Source Serif 4",Georgia,serif;margin-top:12px}
.renk span{display:block;font-size:14px;color:var(--ikincil)}
</style>
</head>
<body><div class="kap">

<header>
  <img src="svg/logo-yatay-a.svg" alt="Veto Atlası — Dünya 5’ten büyüktür">
  <p>Logo paketi<br>${tarih}</p>
</header>

<section>
  <h2>Logolar</h2>
  <p class="not">Açık zemin sürümleri. Dosyalar boşluksuz kırpılmıştır; çevredeki boşluğu sayfa düzeni verir.</p>
  <div class="izgara k2">
    <div class="hucre"><div class="gorsel"><img src="svg/logo-yatay-a.svg" style="height:96px" alt=""></div><div class="etiket">logo-yatay-a</div></div>
    <div class="hucre"><div class="gorsel"><img src="svg/logo-yatay-b.svg" style="height:96px" alt=""></div><div class="etiket">logo-yatay-b</div></div>
  </div>
  <div class="izgara k3">
    <div class="hucre orta"><div class="gorsel"><img src="svg/logo-dikey-a.svg" style="height:180px" alt=""></div><div class="etiket">logo-dikey-a</div></div>
    <div class="hucre orta"><div class="gorsel"><img src="svg/logo-dikey-b.svg" style="height:180px" alt=""></div><div class="etiket">logo-dikey-b</div></div>
    <div class="hucre orta"><div class="gorsel"><img src="svg/logo-dikey-sade.svg" style="height:156px" alt=""></div><div class="etiket">logo-dikey-sade</div></div>
  </div>
  <div class="izgara k3">
    <div class="hucre"><div class="gorsel"><img src="svg/logo-cubuk-b.svg" style="height:60px" alt=""></div><div class="etiket">logo-cubuk-b</div></div>
    <div class="hucre orta"><div class="gorsel"><img src="svg/isaret.svg" style="height:132px" alt=""></div><div class="etiket">isaret</div></div>
    <div class="hucre orta"><div class="gorsel"><img src="svg/isaret-kucuk.svg" style="height:48px" alt=""></div><div class="etiket">isaret-kucuk</div></div>
  </div>
</section>

<section>
  <h2>Koyu zemin</h2>
  <p class="not">Adında -koyu geçen dosyalar. Kırmızı kare ve yazı, lacivert üzerinde okunacak kadar açılmış tonlarla çizilir.</p>
  <div class="izgara k2 koyu">
    <div class="hucre"><div class="gorsel"><img src="svg/logo-yatay-a-koyu.svg" style="height:96px" alt=""></div><div class="etiket">logo-yatay-a-koyu</div></div>
    <div class="hucre"><div class="gorsel"><img src="svg/logo-cubuk-b-koyu.svg" style="height:60px" alt=""></div><div class="etiket">logo-cubuk-b-koyu</div></div>
  </div>
  <div class="izgara k3 koyu">
    <div class="hucre orta"><div class="gorsel"><img src="svg/logo-dikey-b-koyu.svg" style="height:180px" alt=""></div><div class="etiket">logo-dikey-b-koyu</div></div>
    <div class="hucre orta"><div class="gorsel"><img src="svg/isaret-koyu.svg" style="height:132px" alt=""></div><div class="etiket">isaret-koyu</div></div>
    <div class="hucre orta"><div class="gorsel"><img src="svg/isaret-kucuk-koyu.svg" style="height:48px" alt=""></div><div class="etiket">isaret-kucuk-koyu</div></div>
  </div>
</section>

<section>
  <h2>Tek renk</h2>
  <p class="not">Kaşe, gofre, kazıma, fotokopi ve karışık zeminler için. Kırmızı kare de aynı renge döner ama yerinden ayrılmış hâliyle kalır.</p>
  <div class="izgara k4">
    <div class="hucre beyaz"><div class="gorsel"><img src="svg/tek-renk/logo-yatay-a-siyah.svg" style="height:60px" alt=""></div><div class="etiket">logo-yatay-a-siyah</div></div>
    <div class="hucre beyaz orta"><div class="gorsel"><img src="svg/tek-renk/isaret-siyah.svg" style="height:96px" alt=""></div><div class="etiket">isaret-siyah</div></div>
    <div class="hucre gri"><div class="gorsel"><img src="svg/tek-renk/logo-yatay-a-beyaz.svg" style="height:60px" alt=""></div><div class="etiket">logo-yatay-a-beyaz</div></div>
    <div class="hucre gri orta"><div class="gorsel"><img src="svg/tek-renk/isaret-beyaz.svg" style="height:96px" alt=""></div><div class="etiket">isaret-beyaz</div></div>
  </div>
</section>

<section>
  <h2>Küçük boyutlar</h2>
  <p class="not">İşaret her boyutta aynı 15 kareden oluşur. 32 px'in altında kareler birbirine karışmasın diye isaret-kucuk kullanılır: kareler biraz küçük, aralar biraz geniş. Sekme ikonu lacivert zemine oturtulmuştur; açık ve koyu sekme çubuğunda aynı netlikte görünür.</p>
  <div class="izgara k1">
    <div class="hucre"><div class="gorsel serit">
      <figure><img src="svg/isaret.svg" style="height:96px" alt=""><figcaption>96</figcaption></figure>
      <figure><img src="svg/isaret.svg" style="height:64px" alt=""><figcaption>64</figcaption></figure>
      <figure><img src="svg/isaret.svg" style="height:40px" alt=""><figcaption>40</figcaption></figure>
      <figure><img src="svg/isaret.svg" style="height:32px" alt=""><figcaption>32</figcaption></figure>
      <div class="ayrac"></div>
      <figure><img src="svg/isaret-kucuk.svg" style="height:24px" alt=""><figcaption>24</figcaption></figure>
      <figure><img src="svg/isaret-kucuk.svg" style="height:16px" alt=""><figcaption>16</figcaption></figure>
    </div><div class="etiket">isaret 32 px ve üstünde, isaret-kucuk 32 px'in altında (CSS piksel)</div></div>
  </div>
  <div class="izgara k1 koyu">
    <div class="hucre"><div class="gorsel serit">
      <figure><img src="svg/isaret-koyu.svg" style="height:96px" alt=""><figcaption>96</figcaption></figure>
      <figure><img src="svg/isaret-koyu.svg" style="height:64px" alt=""><figcaption>64</figcaption></figure>
      <figure><img src="svg/isaret-koyu.svg" style="height:40px" alt=""><figcaption>40</figcaption></figure>
      <figure><img src="svg/isaret-koyu.svg" style="height:32px" alt=""><figcaption>32</figcaption></figure>
      <div class="ayrac"></div>
      <figure><img src="svg/isaret-kucuk-koyu.svg" style="height:24px" alt=""><figcaption>24</figcaption></figure>
      <figure><img src="svg/isaret-kucuk-koyu.svg" style="height:16px" alt=""><figcaption>16</figcaption></figure>
    </div><div class="etiket">koyu zemin karşılıkları</div></div>
  </div>
  <div class="izgara k2">
    <div class="hucre"><div class="gorsel" style="display:block">
      <div class="tarayici acik"><div class="sekme"><img src="web/favicon.svg" alt=""><span>Veto Atlası</span><span class="kapat">×</span></div><div class="sekme pasif">Yeni sekme</div></div><div class="adres"></div>
    </div><div class="etiket">favicon.svg, açık tema</div></div>
    <div class="hucre"><div class="gorsel" style="display:block">
      <div class="tarayici karanlik"><div class="sekme"><img src="web/favicon.svg" alt=""><span>Veto Atlası</span><span class="kapat">×</span></div><div class="sekme pasif">Yeni sekme</div></div><div class="adres"></div>
    </div><div class="etiket">favicon.svg, koyu tema</div></div>
  </div>
  <div class="izgara k1">
    <div class="hucre"><div class="gorsel serit piksel">
      <figure><img src="${ico16}" alt=""><figcaption>16 px</figcaption></figure>
      <figure><img src="${ico32}" alt=""><figcaption>32 px</figcaption></figure>
      <figure><img src="${ico48}" alt=""><figcaption>48 px</figcaption></figure>
    </div><div class="etiket">favicon.ico içindeki üç görüntü, piksel piksel büyütülmüş</div></div>
  </div>
</section>

<section>
  <h2>Uygulama ikonları ve paylaşım</h2>
  <p class="not">iPhone ana ekranı, Android uyarlanır ikon maskeleri, bağlantı önizlemesi ve profil fotoğrafları.</p>
  <div class="izgara k4">
    <div class="hucre orta"><div class="gorsel"><img class="ios" src="web/apple-touch-icon.png" style="width:132px;height:132px" alt=""></div><div class="etiket">apple-touch-icon, iOS maskesiyle</div></div>
    <div class="hucre orta"><div class="gorsel"><img class="daire" src="web/icon-maskable-512.png" style="width:198px;height:198px;margin:-33px" alt=""></div><div class="etiket">icon-maskable, Android daire maske</div></div>
    <div class="hucre orta"><div class="gorsel"><img class="yumusak" src="web/icon-maskable-512.png" style="width:198px;height:198px;margin:-33px" alt=""></div><div class="etiket">icon-maskable, Samsung tipi maske</div></div>
    <div class="hucre orta"><div class="gorsel"><img src="web/icon-512.png" style="width:132px;height:132px" alt=""></div><div class="etiket">icon-512</div></div>
  </div>
  <div class="izgara" style="grid-template-columns:2fr 1fr 1fr">
    <div class="hucre"><div class="gorsel"><img src="web/og-image.png" style="width:100%;border:1px solid var(--cizgi)" alt=""></div><div class="etiket">og-image, 1200×630</div></div>
    <div class="hucre orta"><div class="gorsel"><img class="yuvarlak" src="sosyal/profil-kagit-1080.png" style="width:150px;height:150px;border:1px solid var(--cizgi)" alt=""></div><div class="etiket">profil-kagit</div></div>
    <div class="hucre orta"><div class="gorsel"><img class="yuvarlak" src="sosyal/profil-murekkep-1080.png" style="width:150px;height:150px" alt=""></div><div class="etiket">profil-murekkep</div></div>
  </div>
</section>

<section>
  <h2>Renkler</h2>
  <p class="not">Sitenin CSS değişkenleriyle aynıdır. Alt sıradaki tonlar, aynı renklerin koyu zemindeki karşılıklarıdır.</p>
  <div class="renkler">
    <div class="renk"><div class="ornek" style="background:${murekkep}"></div><b>Mürekkep</b><span>${murekkep}</span></div>
    <div class="renk"><div class="ornek" style="background:${ret}"></div><b>Ret kırmızısı</b><span>${ret}</span></div>
    <div class="renk"><div class="ornek" style="background:${kagit}"></div><b>Kâğıt</b><span>${kagit}</span></div>
    <div class="renk"><div class="ornek" style="background:${ikincil}"></div><b>İkincil</b><span>${ikincil}</span></div>
    <div class="renk"><div class="ornek" style="background:${acik}"></div><b>Kâğıt tonu, koyu zeminde</b><span>${acik}</span></div>
    <div class="renk"><div class="ornek" style="background:${ret_acik}"></div><b>Ret, koyu zeminde</b><span>${ret_acik}</span></div>
    <div class="renk"><div class="ornek" style="background:${ikincil_acik}"></div><b>İkincil, koyu zeminde</b><span>${ikincil_acik}</span></div>
  </div>
</section>

</div></body></html>
"""

if __name__ == "__main__":
    main()
