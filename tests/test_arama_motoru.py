"""
Arama motorları için robots.txt, sitemap.xml ve Hakkında'daki veri seti tanımı (schema.org Dataset, JSON-LD).

sitemap.xml sayfaların kendi canonical ve hreflang bağlantılarıyla aynı adresleri taşır (İngilizce görünümde canonical
?lang=en olduğu için iki dil de listelenir). JSON-LD'nin değerleri CITATION.cff, veri.js ve Vetolar'ın açıklamasıyla
tutarlıdır: biri değişirse bu testler kalır.
"""
import json
import re
import xml.etree.ElementTree as ET

from conftest import KOK
from veto_atlasi import cevrimdisi

WEB = KOK / "web"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}


def test_robots_txt():
    assert (WEB / "robots.txt").read_text(encoding="utf-8") == (
        "User-agent: *\nAllow: /\n\nSitemap: https://vetoatlas.com/sitemap.xml\n")


def test_sitemap_sayfalarin_canonical_ve_hreflang_baglantilariyla_ayni():
    kok = ET.parse(WEB / "sitemap.xml").getroot()
    adresler = {}
    for url in kok.findall("s:url", NS):
        adresler[url.find("s:loc", NS).text] = sorted((a.get("hreflang"), a.get("href")) for a in url.findall("x:link", NS))
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
    assert [x["contentUrl"] for x in d["distribution"]] == ["https://vetoatlas.com/" + i["dosya"] for i in V["meta"]["indirmeler"]]
    for x in d["distribution"]:
        yol = WEB / x["contentUrl"].removeprefix("https://vetoatlas.com/")
        assert yol.is_file() and x["@type"] == "DataDownload"
        assert x["encodingFormat"] == {".csv": "text/csv", ".json": "application/json"}[yol.suffix]


def test_jsonld_yalnizca_hakkinda_sayfasinda():
    for s in cevrimdisi.SAYFALAR:
        h = (WEB / f"{s}.html").read_text(encoding="utf-8")
        assert h.count("application/ld+json") == (1 if s == "hakkinda" else 0), s
