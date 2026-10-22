"""
Arama motorları için robots.txt, sitemap.xml, Hakkında'daki veri seti tanımı (schema.org Dataset, JSON-LD) ve sunucu
başlıkları (web/_headers: .txt ve açık veri CSV'leri UTF-8 olarak).

sitemap.xml (scripts/12_site_haritasi.py) sayfaların kendi canonical ve hreflang bağlantılarıyla aynı adresleri ve açık veri
dosyalarını taşır (İngilizce görünümde canonical ?lang=en olduğu için iki dil de listelenir). JSON-LD'nin değerleri
CITATION.cff, veri.js ve Vetolar'ın açıklamasıyla tutarlıdır: biri değişirse bu testler kalır.
"""
import datetime
import json
import re
import xml.etree.ElementTree as ET

from conftest import KOK
from veto_atlasi import cevrimdisi

WEB = KOK / "web"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}


def test_robots_txt():
    # Her şey taranabilir; paylaşım kartları ve tek dosya (sitenin kopyası) dizine eklenmez: bunu robots.txt'teki
    # Disallow değil, _headers'taki X-Robots-Tag: noindex sağlar (Disallow, tarayıcının noindex'i görmesini engellerdi).
    # Sitemap satırı en sonda.
    assert (WEB / "robots.txt").read_text(encoding="utf-8") == (
        "User-agent: *\nAllow: /\n\nSitemap: https://vetoatlas.com/sitemap.xml\n")
    basliklar = (WEB / "_headers").read_text(encoding="utf-8")
    for yol in ("/kartlar/*", "/veto-atlasi-tek-dosya", "/veto-atlasi-tek-dosya.html"):
        assert f"\n{yol}\n  X-Robots-Tag: noindex\n" in basliklar, yol


def test_sitemap_sayfalarin_canonical_ve_hreflang_baglantilariyla_ayni():
    kok = ET.parse(WEB / "sitemap.xml").getroot()
    adresler, tarihler = {}, {}
    for url in kok.findall("s:url", NS):
        loc = url.find("s:loc", NS).text
        tarihler[loc] = url.find("s:lastmod", NS).text
        if "/veri/" not in loc:
            adresler[loc] = sorted((a.get("hreflang"), a.get("href")) for a in url.findall("x:link", NS))
    beklenen = {}
    for s in cevrimdisi.SAYFALAR:
        h = (WEB / f"{s}.html").read_text(encoding="utf-8")
        alt = sorted(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">', h))
        assert re.search(rf'<link rel="canonical" href="https://vetoatlas.com/{s}">', h), s
        assert dict(alt) == {"tr": f"https://vetoatlas.com/{s}", "en": f"https://vetoatlas.com/{s}?lang=en",
                             "x-default": f"https://vetoatlas.com/{s}"}, s
        for dil in ("tr", "en"):
            beklenen[dict(alt)[dil]] = alt
    assert adresler == beklenen and len(adresler) == 16
    # Açık veri dosyaları da listede; lastmod her adreste geçerli bir tarih, bugünden ileri değil, iki dil aynı tarihte
    veri = {f"https://vetoatlas.com/veri/{p.name}" for p in (WEB / "veri").iterdir() if p.suffix in (".csv", ".json", ".xlsx")}
    assert set(tarihler) == set(beklenen) | veri and len(veri) == 6  # veri_sozlugu.csv dahil (K10)
    for loc, tarih in tarihler.items():
        assert datetime.date.fromisoformat(tarih) <= datetime.date.today(), loc
    for s in cevrimdisi.SAYFALAR:
        assert tarihler[f"https://vetoatlas.com/{s}"] == tarihler[f"https://vetoatlas.com/{s}?lang=en"], s
    # Arama dizinine girmemesi gerekenler sitemap'te yok
    metin = (WEB / "sitemap.xml").read_text(encoding="utf-8")
    for ad in ("404", "kartlar", "tek-dosya", "index"):
        assert ad not in metin, ad


def _jsonld():
    h = (WEB / "hakkinda.html").read_text(encoding="utf-8")
    bloklar = re.findall(r'<script type="application/ld\+json">\n(.*?)\n</script>', h, re.S)
    assert len(bloklar) == 1 and h.index(bloklar[0]) < h.index("</head>")
    return json.loads(bloklar[0])


def test_dataset_jsonld_atif_dosyasi_ve_veriyle_tutarli():
    d = _jsonld()
    cff = (KOK / "CITATION.cff").read_text(encoding="utf-8")
    deger = lambda a: re.search(rf'^{a}: "?([^"\n]+)"?$', cff, re.M)[1]  # noqa: E731
    assert d["@context"] == "https://schema.org" and d["@type"] == "Dataset"
    assert d["name"] == deger("title") == "Veto Atlası" and d["alternateName"] == "Veto Atlas"
    assert d["version"] == deger("version") and d["datePublished"] == deger("date-released")
    assert d["identifier"] == "https://doi.org/" + deger("doi") and d["sameAs"] == "https://zenodo.org/records/23326362"
    assert d["license"] == "https://creativecommons.org/licenses/by/4.0/" and "CC-BY-4.0" in cff
    # Yazar alanı yok: 13 Ekim kararıyla Hakkında'dan Yayımlayan (ad ve ORCID) kaldırıldı (test_yayin_hazirligi)
    assert "creator" not in d and "author" not in d and "publisher" not in d
    assert d["url"] == "https://vetoatlas.com/hakkinda" and d["isAccessibleForFree"] is True and d["inLanguage"] == ["tr", "en"]
    # Açıklama: Vetolar sayfasının yayımlanmış veri seti tanımı (iki dil)
    vetolar = (WEB / "vetolar.html").read_text(encoding="utf-8")
    assert d["description"] == re.search(r'<meta name="description" content="([^"]+)"', vetolar)[1]
    # Zaman kapsamı ve indirmeler veri setinden
    v = (WEB / "veri.js").read_text(encoding="utf-8")
    V = json.loads(v[v.index("{"):v.rstrip().rindex(";")])
    assert d["temporalCoverage"] == f'{min(k["tarih"] for k in V["kayitlar"])}/{V["meta"]["veri_surumu"]}'
    # Veri dosyaları ve sonda sütunları açıklayan veri sözlüğü (Hakkında'nın indirme bölümü ona bağlanır)
    assert [x["contentUrl"] for x in d["distribution"]] == (["https://vetoatlas.com/" + i["dosya"] for i in V["meta"]["indirmeler"]]
                                                            + ["https://vetoatlas.com/veri/veri_sozlugu.csv"])
    for x in d["distribution"]:
        yol = WEB / x["contentUrl"].removeprefix("https://vetoatlas.com/")
        assert yol.is_file() and x["@type"] == "DataDownload"
        assert x["encodingFormat"] == {".csv": "text/csv", ".json": "application/json",
                                       ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}[yol.suffix]


def test_jsonld_yalnizca_hakkinda_sayfasinda():
    for s in cevrimdisi.SAYFALAR:
        h = (WEB / f"{s}.html").read_text(encoding="utf-8")
        assert h.count("application/ld+json") == (1 if s == "hakkinda" else 0), s


def test_icerik_sayfalarinda_noindex_yok_404_gercek_404():
    """İçerik sayfaları dizine açık; yalnızca 404 sayfası noindex. Cloudflare Workers statik varlıklarında
    not_found_handling "404-page": olmayan adres 404.html'i 404 durum koduyla döner (canlıda curl ile denetlendi)."""
    for s in cevrimdisi.SAYFALAR:
        assert "noindex" not in (WEB / f"{s}.html").read_text(encoding="utf-8"), s
    assert '<meta name="robots" content="noindex">' in (WEB / "404.html").read_text(encoding="utf-8")
    w = (KOK / "wrangler.jsonc").read_text(encoding="utf-8")
    assert '"directory": "./web"' in w and '"not_found_handling": "404-page"' in w


def test_headers_metin_ve_csv_utf8():
    """Sunucu .txt (LICENSE-DATA, robots, yazı tipi lisansları) ve açık veri CSV'lerini charset=utf-8 ile gönderir; yoksa
    tarayıcı Türkçe karakterleri bozuk gösteriyordu (14 Ekim). Bütün adreslerde üç güvenlik başlığı; yazı tipleri bir yıl
    (immutable), görseller bir hafta önbellekte; HTML ve veri için önbellek kuralı yok. Kartlar ve tek dosya noindex."""
    assert (WEB / "_headers").read_text(encoding="utf-8") == (
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
        "/*.txt\n  Content-Type: text/plain; charset=utf-8\n/veri/*.csv\n  Content-Type: text/csv; charset=utf-8\n"
        "/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        "/*.png\n  Cache-Control: public, max-age=604800\n/*.svg\n  Cache-Control: public, max-age=604800\n"
        "/kartlar/*\n  X-Robots-Tag: noindex\n/veto-atlasi-tek-dosya\n  X-Robots-Tag: noindex\n"
        "/veto-atlasi-tek-dosya.html\n  X-Robots-Tag: noindex\n")
    assert {p.name for p in WEB.rglob("*.txt")} >= {"LICENSE-DATA.txt", "robots.txt", "OFL-source-sans-3.txt"}
    assert {p.name for p in (WEB / "veri").glob("*.csv")} == {"vetolar.csv", "genel_kurul_tartismalari.csv", "veri_sozlugu.csv"}
