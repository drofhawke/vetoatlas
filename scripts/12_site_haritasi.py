"""
Adım 12: Arama motorları için site haritası.

    python scripts/12_site_haritasi.py   # web/sitemap.xml

Sekiz sayfanın Türkçe ve İngilizce adresleri (sayfanın kendi hreflang bağlantılarıyla: tr, en, x-default) ve açık veri
dosyaları (web/veri/: CSV, XLSX, JSON). lastmod, git kaydından: sayfa için sayfanın ve yüklediği yerel dosyaların (betikler,
stiller, veri), veri dosyası için dosyanın kendisinin son değiştiği commit'in tarihi; işlenmemiş değişiklik varsa bugün. Sayfalar ya da
veri değiştiğinde yayından önce yeniden çalıştırılır (04 çalıştırmaz: lastmod deponun geçmişine bağlıdır).
tests/test_arama_motoru.py adresleri sayfalarla karşılaştırır.
"""
import datetime
import re
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from veto_atlasi import cevrimdisi  # noqa: E402

WEB = KOK / "web"
SITE = "https://vetoatlas.com"


def son_degisiklik(yollar: list[Path]) -> str:
    """Dosyaların en son değiştiği tarih (YYYY-AA-GG): işlenmemiş değişiklik varsa bugün, yoksa son commit'in tarihi."""
    goreli = [str(p.relative_to(KOK)) for p in yollar]
    git = lambda *a: subprocess.run(["git", "-C", str(KOK), *a], capture_output=True, text=True, check=True).stdout  # noqa: E731
    if git("status", "--porcelain", "--", *goreli).strip():
        return datetime.date.today().isoformat()
    return git("log", "-1", "--format=%cs", "--", *goreli).strip()


def sayfa_dosyalari(ad: str) -> list[Path]:
    """Sayfa ve yüklediği yerel dosyalar (script src, link href; canonical ve alternate hariç)."""
    s = (WEB / f"{ad}.html").read_text(encoding="utf-8")
    yollar = {WEB / f"{ad}.html"}
    for etiket in cevrimdisi._ETIKET.findall(s):
        if re.search(r'\brel="(?:canonical|alternate)"', etiket):
            continue
        for adres in cevrimdisi._ADRES.findall(etiket):
            yol = cevrimdisi._yerel(adres)
            if yol and (WEB / yol.lstrip("/")).is_file():
                yollar.add(WEB / yol.lstrip("/"))
    return sorted(yollar)


def uret() -> str:
    satirlar = ['<?xml version="1.0" encoding="UTF-8"?>',
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for ad in cevrimdisi.SAYFALAR:
        h = (WEB / f"{ad}.html").read_text(encoding="utf-8")
        alt = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">', h)
        tarih = son_degisiklik(sayfa_dosyalari(ad))
        for adres in (a for d, a in alt if d in ("tr", "en")):
            satirlar += ["  <url>", f"    <loc>{adres}</loc>", f"    <lastmod>{tarih}</lastmod>"]
            satirlar += [f'    <xhtml:link rel="alternate" hreflang="{d}" href="{a}"/>' for d, a in alt]
            satirlar.append("  </url>")
    for yol in sorted((WEB / "veri").iterdir()):
        if yol.suffix in (".csv", ".json", ".xlsx"):
            satirlar += ["  <url>", f"    <loc>{SITE}/veri/{yol.name}</loc>", f"    <lastmod>{son_degisiklik([yol])}</lastmod>",
                         "  </url>"]
    satirlar.append("</urlset>")
    return "\n".join(satirlar) + "\n"


if __name__ == "__main__":
    (WEB / "sitemap.xml").write_text(uret(), encoding="utf-8", newline="\n")
    print("web/sitemap.xml:", (WEB / "sitemap.xml").read_text(encoding="utf-8").count("<loc>"), "adres")
