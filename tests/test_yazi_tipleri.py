"""Yazı tipleri (scripts/14_yazi_tipleri.py, web/fonts/README.md): woff2 kesimleri hinting'lidir ve fonts.css'teki tanımlarla
üretim betiğinin okuduğu tanımlar aynıdır. woff2 tablo dizini sıkıştırılmamıştır; brotli'siz okunur (fontTools gerekmez)."""
import re
import struct
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
FONTS = KOK / "web/fonts"
sys.path.insert(0, str(KOK))

# WOFF2 tablo dizini: bilinen 63 etiket 6 bitlik sırayla kodlanır (WOFF2 standardı, "Known Table Tags"; 63 = etiket açık yazılır)
BILINEN = [e.ljust(4) for e in (
    "cmap head hhea hmtx maxp name OS/2 post cvt fpgm glyf loca prep CFF VORG EBDT EBLC gasp hdmx kern LTSH PCLT VDMX vhea "
    "vmtx BASE GDEF GPOS GSUB EBSC JSTF MATH CBDT CBLC COLR CPAL SVG sbix acnt avar bdat bloc bsln cvar fdsc feat fmtx fvar "
    "gvar hsty just lcar mort morx opbd prop trak Zapf Silf Glat Gloc Feat Sill").split()]
assert len(BILINEN) == 63 and BILINEN[8] == "cvt " and BILINEN[47] == "fvar"


def _uint_base128(veri, i):
    deger = 0
    for _ in range(5):
        b = veri[i]; i += 1
        deger = (deger << 7) | (b & 0x7F)
        if not b & 0x80:
            return deger, i
    raise ValueError("UIntBase128")


def woff2_tablolari(veri: bytes) -> dict[str, int]:
    """{etiket: özgün uzunluk}; glyf/loca dönüştürülmüş olabilir (uzunluk yine özgün uzunluktur)."""
    assert veri[:4] == b"wOF2"
    tablo_sayisi = struct.unpack(">H", veri[12:14])[0]
    i, tablolar = 48, {}
    for _ in range(tablo_sayisi):
        bayrak = veri[i]; i += 1
        if bayrak & 0x3F == 0x3F:
            etiket = veri[i:i + 4].decode("latin-1"); i += 4
        else:
            etiket = BILINEN[bayrak & 0x3F]
        uzunluk, i = _uint_base128(veri, i)
        donusum = (bayrak >> 6) & 3
        if (etiket in ("glyf", "loca") and donusum == 0) or (etiket == "hmtx" and donusum == 1):
            _, i = _uint_base128(veri, i)  # dönüştürülmüş uzunluk
        tablolar[etiket] = uzunluk
    return tablolar


def test_kesimler_hintingli():
    """Her woff2'de ttfautohint'in yazdığı hinting tabloları (fpgm, prep, cvt) vardır ve prep yalnızca gasp satırından ibaret
    değildir; hinting'siz @fontsource dosyalarında (11 Ekim) fpgm ve cvt yoktu, prep 7 bayttı."""
    adlar = sorted(p.name for p in FONTS.glob("*.woff2"))
    assert len(adlar) == 13  # 12 site kesimi + çubuktaki logo yazısı (veto-atlasi-logo)
    for ad in adlar:
        t = woff2_tablolari((FONTS / ad).read_bytes())
        assert {"fpgm", "prep", "cvt ", "gasp", "glyf", "GPOS", "GSUB"} <= set(t), (ad, sorted(t))
        assert t["fpgm"] > 1000 and t["prep"] > 100 and t["cvt "] >= 100, (ad, t["fpgm"], t["prep"], t["cvt "])


def test_tanimlar_ve_kaynak_sabit():
    """Betik fonts.css'ten 12 tanım okur (aile, stil, ağırlık, dosya, unicode-range); kaynak dosyaların SHA-256'ları betikte
    sabittir ve README bu betiğe gönderir."""
    from veto_atlasi import yazi_tipleri
    tanimlar = yazi_tipleri.tanimlar((FONTS / "fonts.css").read_text(encoding="utf-8"))
    assert sorted(t["src"] for t in tanimlar) == sorted(p.name for p in FONTS.glob("*.woff2"))
    for t in tanimlar:
        assert t["family"] in yazi_tipleri.AILE and t["weight"] in (400, 500, 600) and t["style"] in ("normal", "italic")
        assert (t["style"] == "italic") <= (t["family"] == "Source Sans 3" and t["weight"] == 400)
        assert ("latin-ext" in t["ad"]) == (0x011E in t["unicodes"]) and (0x0131 in t["unicodes"])  # Ğ latin-ext'te, ı ikisinde
    assert len(yazi_tipleri.KAYNAK) == 3 and all(re.fullmatch(r"[0-9a-f]{64}", o) for _, o in yazi_tipleri.KAYNAK.values())
    assert yazi_tipleri.OPSZ == {"Source Serif 4": 14, "Veto Atlası Logo": 20} and yazi_tipleri.HINT["default_script"] == "latn"
    # Logo yazısı: yalnızca "Veto Atlası"nın harfleri, 600, optik boy 20 (logo paketindeki yola çevrilmiş yazıyla aynı kesim)
    logo = [t for t in tanimlar if t["family"] == "Veto Atlası Logo"]
    assert len(logo) == 1 and logo[0]["weight"] == 600 and logo[0]["src"] == "veto-atlasi-logo.woff2"
    assert logo[0]["unicodes"] == {ord(c) for c in "Veto Atlası"}
    readme = (FONTS / "README.md").read_text(encoding="utf-8")
    assert "scripts/14_yazi_tipleri.py" in readme and "ttfautohint" in readme and "veto-atlasi-logo.woff2" in readme
