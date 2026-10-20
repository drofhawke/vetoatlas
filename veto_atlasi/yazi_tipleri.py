"""
Yazı tipleri: web/fonts/*.woff2 ve web/fonts/README.md'deki SHA-256 tablosu (scripts/14_yazi_tipleri.py).

Kaynak, Google Fonts'un Source Sans 3 ve Source Serif 4 değişken (variable) yazı tipleridir (github.com/google/fonts,
Adobe'nin 3.052 ve 4.004 sürümlerinden derlenmiş; SIL OFL 1.1). Bu dosyalar hinting'siz dağıtılır: Windows'ta Chrome
ve Edge, 15–18 px metni dikey ızgaraya oturtamayınca gövde ve x-yüksekliği çizgileri iki piksele yayılıp bulanık
görünür (20 Ekim 2026'da %100 ölçekte ekran görüntüsüyle doğrulandı). Burada her kesim değişken dosyadan çıkarılır,
ttfautohint ile hinting eklenir ve fonts.css'teki unicode-range alt kümelerine (latin, latin-ext) bölünerek woff2
yazılır. Dış hatlar, ölçüler (hhea/OS/2) ve OpenType özellikleri Google'ın dağıttığı kesimlerle aynıdır; yalnızca
hinting programı (fpgm, prep, cvt, glif komutları) eklenir.

Üretim belirlenimlidir: aynı kaynak dosyalar ve aynı ayarlarla aynı baytlar çıkar (zaman damgası sabit). Kaynak
dosyalar ilk çalıştırmada kaynaklar/.yazi_tipleri/ altına indirilir ve SHA-256'ları aşağıdaki listeyle denetlenir.

    pip install fonttools brotli ttfautohint-py   # 20 Ekim 2026: fonttools 4.65–4.66, brotli 1.1, ttfautohint-py 0.6.1 (ttfautohint 1.8.4)
"""
from __future__ import annotations

import calendar
import hashlib
import io
import re
import urllib.request
from pathlib import Path

# Kaynak dosyalar: github.com/google/fonts, main dalı (indirme tarihi 20 Ekim 2026). SHA-256 sabit: dosya değişirse
# üretim durur; yeni sürüme bilerek geçilir (özet güncellenir, çıktı yeniden üretilir, README'deki tablo yenilenir).
KAYNAK = {
    "SourceSans3[wght].ttf": (
        "https://raw.githubusercontent.com/google/fonts/main/ofl/sourcesans3/SourceSans3%5Bwght%5D.ttf",
        "042fe2cc0b933e328410d7acbd0aa6a1873dca5aef81875f4bc214b08825c7b9"),
    "SourceSans3-Italic[wght].ttf": (
        "https://raw.githubusercontent.com/google/fonts/main/ofl/sourcesans3/SourceSans3-Italic%5Bwght%5D.ttf",
        "39e3ab05ccd7cb94907c31005bb5bec1d5432f0b096a2b782976e217a540eb6c"),
    "SourceSerif4[opsz,wght].ttf": (
        "https://raw.githubusercontent.com/google/fonts/main/ofl/sourceserif4/SourceSerif4%5Bopsz,wght%5D.ttf",
        "97b2d4da6e3cb494b5a1e66ae176914d852ccabef49e0c02c0df25f3e39aca0b"),
}
AILE = {  # fonts.css'teki aile adı -> (normal kaynak dosya, italik kaynak dosya, optik boy)
    "Source Sans 3": ("SourceSans3[wght].ttf", "SourceSans3-Italic[wght].ttf", None),
    # Source Serif 4 optik boyu 14: Google'ın dağıttığı statik kesimler (eski @fontsource dosyaları) bu değerdedir; ilerleme
    # genişlikleri birebir aynı (20 Ekim 2026'da ölçüldü), yani sayfalardaki satır ve başlık ölçüleri değişmez
    "Source Serif 4": ("SourceSerif4[opsz,wght].ttf", None, 14),
    # Çubuktaki logo yazısı "Veto Atlası" (web/cubuk.js): logo paketi yazıyı Adobe'nin Source Serif 4 Semibold kesimiyle,
    # yani optik boy 20 ile yola çevirmişti; canlı metin aynı harf biçimlerini kullanır. Yalnızca bu harflerin glifleri
    "Veto Atlası Logo": ("SourceSerif4[opsz,wght].ttf", None, 20),
}
OPSZ = {ad: a[2] for ad, a in AILE.items() if a[2]}

# ttfautohint ayarları (sürüm 1.8.4, ttfautohint-py 0.6.1). Yalnızca Latin; 8–50 ppem için eniyilenir, 200 ppem'e kadar
# uygulanır (başlık boyutları da ızgaraya oturur); -W, -c ve -X kullanılmaz; sürüm bilgisi eklenmez (no_info).
HINT = dict(default_script="latn", fallback_script="none", hinting_range_min=8, hinting_range_max=50, hinting_limit=200,
            no_info=True, windows_compatibility=False, hint_composites=False)
ZAMAN = calendar.timegm((2026, 10, 20, 0, 0, 0))  # head.modified: sabit (belirlenimli üretim)
# fontTools, uharfbuzz kuruluysa GSUB/GPOS tablolarını HarfBuzz'ın paketleyicisiyle yazar ve baytlar değişir (20 Ekim 2026'da
# görüldü: aynı girdi, uharfbuzz'lı ortamda 594 bayt küçük GPOS). Çıktı ortamdan bağımsız kalsın diye kapalı.
AYAR = {"fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER": False}
# Korunan OpenType özellikleri: Google'ın dağıttığı kesimlerdekilerin birleşimi (kerning, bağlaçlar, kesirler, orantılı ve
# tablo rakamları, aksan konumlandırma). Küçük büyük harf, biçem kümeleri gibi sitede kullanılmayan özellikler ve glifleri
# atılır; glif sayısı Google'ın alt kümeleriyle aynı kalır.
OZELLIKLER = ("ccmp", "dnom", "frac", "kern", "liga", "locl", "mark", "mkmk", "numr", "pnum", "tnum")

_BLOK = re.compile(r"/\* ([\w-]+) \*/\n@font-face \{(.*?)\}", re.S)
_ALAN = re.compile(r"^\s*([\w-]+):\s*(.+?);\s*$", re.M)


def tanimlar(css: str) -> list[dict]:
    """fonts.css'teki @font-face bloklarını okur: ad, family, style, weight, src, unicodes."""
    out = []
    for ad, govde in _BLOK.findall(css):
        alan = dict(_ALAN.findall(govde))
        src = re.fullmatch(r"url\(([^)]+)\) format\('woff2'\)", alan["src"])[1]
        unicodes: set[int] = set()
        for parca in alan["unicode-range"].split(","):
            a, _, b = parca.strip()[2:].partition("-")
            unicodes.update(range(int(a, 16), int(b or a, 16) + 1))
        out.append({"ad": ad, "family": alan["font-family"].strip("'\""), "style": alan["font-style"],
                    "weight": int(alan["font-weight"]), "src": src, "unicodes": unicodes})
    return out


def kaynaklari_indir(klasor: Path) -> dict[str, Path]:
    klasor.mkdir(parents=True, exist_ok=True)
    yollar = {}
    for ad, (url, ozet) in KAYNAK.items():
        p = klasor / ad
        if not p.exists():
            print("indiriliyor:", ad)
            with urllib.request.urlopen(url, timeout=120) as r:
                p.write_bytes(r.read())
        gercek = hashlib.sha256(p.read_bytes()).hexdigest()
        if gercek != ozet:
            raise SystemExit(f"{ad}: beklenmeyen içerik (SHA-256 {gercek}, beklenen {ozet}); dosyayı silip yeniden deneyin")
        yollar[ad] = p
    return yollar


def kesim(vf_yolu: Path, weight: int, opsz: int | None = None) -> bytes:
    """Değişken yazı tipinden statik kesim (TTF baytları). Konturlar Google'ın statik kesimlerindeki gibi bırakılır (çakışma
    bayrağı konmaz: bayrak woff2'nin glyf dönüşümünü engelleyip dosyayı iki kat büyütüyor; çağdaş çizerler bayrağa bakmaz)."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    vf = TTFont(str(vf_yolu), recalcTimestamp=False, cfg=AYAR)
    konum = {"wght": float(weight)}
    if any(a.axisTag == "opsz" for a in vf["fvar"].axes):
        assert opsz, vf_yolu.name
        konum["opsz"] = float(opsz)
    st = instancer.instantiateVariableFont(vf, konum, inplace=False, overlap=instancer.OverlapMode.KEEP_AND_DONT_SET_FLAGS,
                                           updateFontNames=True)
    st["head"].modified = ZAMAN
    b = io.BytesIO(); st.save(b); return b.getvalue()


def hinting(ttf: bytes) -> bytes:
    import ttfautohint
    return ttfautohint.ttfautohint(in_buffer=ttf, epoch=ZAMAN, **HINT)


def alt_kume(ttf: bytes, unicodes: set[int]) -> bytes:
    """fonts.css'teki unicode-range'e göre alt küme, woff2; hinting ve bütün OpenType özellikleri korunur."""
    from fontTools import subset
    from fontTools.ttLib import TTFont
    sec = subset.Options()
    sec.hinting = True
    sec.layout_features = list(OZELLIKLER)
    sec.glyph_names = False
    sec.notdef_outline = True
    sec.drop_tables = [t for t in sec.drop_tables if t != "BASE"]
    f = TTFont(io.BytesIO(ttf), recalcTimestamp=False, cfg=AYAR)
    s = subset.Subsetter(options=sec)
    s.populate(unicodes=unicodes)
    s.subset(f)
    f["head"].modified = ZAMAN
    f.flavor = "woff2"  # glyf/loca/hmtx dönüşümlü woff2 (Subsetter'ın flavor seçeneği yalnızca komut satırında uygulanır)
    b = io.BytesIO(); f.save(b); return b.getvalue()


def uret(kok: Path) -> dict[str, str]:
    """web/fonts/*.woff2 dosyalarını yazar; {dosya adı: SHA-256} döner."""
    fonts = kok / "web/fonts"
    css = (fonts / "fonts.css").read_text(encoding="utf-8")
    yollar = kaynaklari_indir(kok / "kaynaklar/.yazi_tipleri")
    kesimler: dict[tuple, bytes] = {}
    ozetler = {}
    for t in tanimlar(css):
        normal, italik, opsz = AILE[t["family"]]
        kaynak = italik if t["style"] == "italic" else normal
        anahtar = (kaynak, t["weight"], opsz)
        if anahtar not in kesimler:
            kesimler[anahtar] = hinting(kesim(yollar[kaynak], t["weight"], opsz))
        veri = alt_kume(kesimler[anahtar], t["unicodes"])
        (fonts / t["src"]).write_bytes(veri)
        ozetler[t["src"]] = hashlib.sha256(veri).hexdigest()
        print(f"{t['src']}: {len(veri) / 1e3:.1f} kB")
    return ozetler


def readme_guncelle(kok: Path, ozetler: dict[str, str]) -> None:
    """README'deki tabloyu yeniler (woff2 satırları; lisans satırları diskteki dosyalardan)."""
    fonts = kok / "web/fonts"
    yol = fonts / "README.md"
    metin = yol.read_text(encoding="utf-8")
    satirlar = [f"| `{ad}` | `{ozetler[ad]}` |" for ad in sorted(ozetler)]
    for lisans in sorted(p.name for p in fonts.glob("OFL-*.txt")):  # satır sonu git'teki gibi LF (CRLF'li Windows çalışma ağacı)
        lf = (fonts / lisans).read_bytes().replace(b"\r\n", b"\n")
        satirlar.append(f"| `{lisans}` | `{hashlib.sha256(lf).hexdigest()}` |")
    yeni = "| Dosya | SHA-256 |\n|---|---|\n" + "\n".join(satirlar) + "\n"
    metin, n = re.subn(r"\| Dosya \| SHA-256 \|\n\|---\|---\|\n(?:\|[^\n]*\|\n)+", yeni, metin)
    assert n == 1, "README'de tablo bulunamadı"
    yol.write_text(metin, encoding="utf-8", newline="\n")
