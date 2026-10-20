"""
Yayın hazırlığı: yayın adresi (vetoatlas.com) etiketleri, beta şeridi, Hakkında'daki iletişim ve lisans satırı (yayımlayan ve atıf
kutusu (DOI), lisans ve atıf dosyaları, kart alt bilgileri. Sitede yer tutucu kalmaz.
"""
import re

from conftest import KOK

WEB = KOK / "web"
ADRES = "https://vetoatlas.com"
SAYFALAR = ("hikaye", "vetolar", "vizyon", "reform", "simulasyon", "temsil", "hakkinda", "metodoloji")
ORCID = "0000-0002-0921-1256"
DOI = "10.5281/zenodo.23326362"


def test_yayin_adresi_etiketleri():
    for ad in SAYFALAR:
        s = (WEB / f"{ad}.html").read_text(encoding="utf-8")
        bas = s[:s.index("</head>")]
        u = f"{ADRES}/{ad}"  # uzantısız (Cloudflare Pages .html adresini uzantısıza yönlendirir); sayfa içi bağlantılar .html
        for etiket in (f'<meta property="og:url" content="{u}">', f'<link rel="canonical" href="{u}">',
                       f'<link rel="alternate" hreflang="tr" href="{u}">', f'<link rel="alternate" hreflang="en" href="{u}?lang=en">',
                       f'<link rel="alternate" hreflang="x-default" href="{u}">', f'<meta property="og:image" content="{ADRES}/onizleme.png">'):
            assert bas.count(etiket) == 1, (ad, etiket)
        assert not re.search(r"vetoatlas\.com/[a-z]+\.html", bas), ad
    assert f'<link rel="canonical" href="{ADRES}/hikaye">' in (WEB / "index.html").read_text(encoding="utf-8")
    c = (WEB / "cubuk.js").read_text(encoding="utf-8")
    assert 'if (!tek && dil === "en") {' in c and '"?lang=en"' in c
    # Tek dosyada sayfa çerçeveleri canonical ve hreflang taşımaz
    tek = (WEB / "veto-atlasi-tek-dosya.html").read_text(encoding="utf-8")
    assert '<link rel="canonical"' not in tek and '<link rel="alternate"' not in tek


def test_alt_bilgi_notu():
    """20 Ekim 2026: beta şeridi yerine her sayfanın altında tek satırlık not; sayfanın alt bilgisi (footer#alt) varsa ona eklenir,
    yoksa oluşturulur; tek dosyada her çerçeve kendi notunu taşır."""
    c = (WEB / "cubuk.js").read_text(encoding="utf-8")
    assert 'altNot: "Beta sürümü. Hata bildirmek için", altSon: " adresine yazın.",' in c and 'altNot: "Beta. To report an error, write to", altSon: ".",' in c
    assert 'var ILETISIM = "iletisim@vetoatlas.com";' in c and """<a href="mailto:' + ILETISIM + '">' + ILETISIM""" in c
    assert "function altBilgi(dil) {" in c and 'if (alt && alt.tagName === "FOOTER") { alt.appendChild(p); return; }' in c
    assert "if (!tek) altBilgi(dil);" in c and "altBilgi(gecerliDil()); return; }" in c
    assert "beta" not in c.lower().replace("alt-bilgi", "").replace("beta sürümü", "").replace("beta.", "").replace("beta şeridi", "")
    assert '"@media print { .cubuk { display: none; } }",' in c


def test_hakkinda_iletisim_ve_lisans_satiri():
    """13 Ekim kararı (kullanıcı): Hakkında'dan Açık veri, Bu çalışmaya atıf ve Yayımlayan kaldırıldı (iki dil); İletişim'in
    altında tek satır: lisans ve veri setinin Zenodo arşivi."""
    h = (WEB / "hakkinda.html").read_text(encoding="utf-8")
    for kimlik in ("acik-veri", "atif", "yayimlayan", "en-acik-veri", "en-atif", "en-yayimlayan"):
        assert f'id="{kimlik}"' not in h, kimlik
    for eski in ('data-yer="indir"', 'class="atif"', 'class="lisans"', "orcid.org", "Nuh Mehmet", "Yayımlayan", "Published by"):
        assert eski not in h, eski
    posta = '<a href="mailto:iletisim@vetoatlas.com">iletisim@vetoatlas.com</a>'
    assert f"<p>Hata bildirimi ve sorular için {posta}. Düzeltmeleri değişiklik günlüğüne işliyoruz.</p>" in h
    assert f"<p>For error reports and questions, {posta}. We enter corrections in the change log.</p>" in h
    doi = f'<a href="https://doi.org/{DOI}">{DOI}</a>'
    ld = '<a href="LICENSE-DATA.txt">LICENSE-DATA</a>'
    assert f"<p>Kod MIT, veri derlemesi CC BY 4.0 lisansıyla ({ld}). Veri setinin arşivi Zenodo'da, DOI {doi}.</p>" in h
    assert f"<p>Code under MIT, the data compilation under CC BY 4.0 ({ld}). The dataset is archived on Zenodo, DOI {doi}.</p>" in h
    assert "[DOI]" not in h and "yer-tutucu" not in h


def test_lisans_ve_atif_dosyalari():
    mit = (KOK / "LICENSE").read_text(encoding="utf-8")
    assert mit.startswith("MIT License\n\nCopyright (c) 2026 Nuh Mehmet Yıldız\n") and "THE SOFTWARE IS PROVIDED \"AS IS\"" in mit
    veri = (KOK / "LICENSE-DATA").read_text(encoding="utf-8")
    assert "https://creativecommons.org/licenses/by/4.0/" in veri and veri.count("CC BY 4.0") == 2
    for s in ("Daha Adil Bir Dünya Mümkün", "World Population Prospects", "CC BY 3.0 IGO", "Sievers", "Tablo 4", "Table 4",
              "SIL Open Font License 1.1", "Source Serif 4", "Source Sans 3",
              "5. Birleşmiş Milletler belgeleri.", "5. United Nations documents.", "veto listesi; BM'nin kendi kullanım koşullarına tabidir",
              "6. Test kesiti. tests/fixtures/veto_ornek.html, DHL veto listesi sayfasından alınmış 13 satırlık bir test kesitidir",
              "6. Test excerpt. tests/fixtures/veto_ornek.html is a 13-row test excerpt taken from the DHL veto list page"):
        assert s in veri, s
    # Sitedeki kopya (Hakkında bağlantısı) depodaki dosyayla aynı
    assert (WEB / "LICENSE-DATA.txt").read_bytes() == (KOK / "LICENSE-DATA").read_bytes()
    cff = (KOK / "CITATION.cff").read_text(encoding="utf-8")
    for s in ("cff-version: 1.2.0", 'title: "Veto Atlası"', "version: 1.0.0", 'family-names: "Yıldız"', 'given-names: "Nuh Mehmet"',
              f'orcid: "https://orcid.org/{ORCID}"', "  - MIT\n  - CC-BY-4.0\n", 'url: "https://vetoatlas.com"'):
        assert s in cff, s
    assert "version: 1.0.0\ndate-released: 2026-10-12\n" in cff
    assert f"date-released: 2026-10-12\ndoi: {DOI}\n" in cff


def test_kart_alt_bilgileri():
    kartlar = sorted((WEB / "kartlar").glob("*.html"))
    assert len(kartlar) == 44
    for k in kartlar:
        s = k.read_text(encoding="utf-8")
        ad = "Veto Atlası · vetoatlas.com" if "-tr-" in k.name else "Veto Atlas · vetoatlas.com"
        assert f'<div class="ad">{ad}<svg' in s, k.name
        assert "[Atlas" not in s, k.name


def test_yer_tutucu_kalmadi():
    """Köşeli ayraç içinde boşluk ya da Türkçe harf taşıyan (ya da bilinen) yer tutucu ifade kalmadı."""
    desen = re.compile(r"\[([^\]\[\n<>\"'{}()=;,+*/\\|`$]{2,80})\]")
    kalan = set()
    for yol in list(WEB.glob("*.html")) + list(WEB.glob("kartlar/*.html")) + [WEB / "cubuk.js", WEB / "metin.js"]:
        for m in desen.finditer(yol.read_text(encoding="utf-8")):
            ic = m.group(1)
            if (re.search(r"[A-Za-zÇĞİÖŞÜçğıöşü]", ic) and (" " in ic or re.search(r"[^\x00-\x7f]", ic) or ic == "DOI")
                    and not re.search(r"\.length - 1|% 10|^i - 1$", ic)):
                kalan.add(ic)
    assert not kalan, kalan
    tek = (WEB / "veto-atlasi-tek-dosya.html").read_text(encoding="utf-8")
    assert "[DOI]" not in tek and f"https://doi.org/{DOI}" in tek


def test_dar_ekran_tasmalari():
    """320 px: Temsil grup kartları sütuna iner, Vetolar süzgeç listeleri daralır, metin sayfalarında uzun adresler kırılır."""
    assert ".izgara { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(332px, 100%), 1fr)); gap: 16px; }" in (WEB / "temsil.html").read_text(encoding="utf-8")
    v = (WEB / "vetolar.html").read_text(encoding="utf-8")
    assert ".filtre { flex: 1 1 100%; min-width: 0; }" in v and ".alan select { max-width: 100%; }" in v
    assert ".alan { display: flex; flex-direction: column; gap: 4px; min-width: 0;" in v
    assert ".metin-duzen .metin p, .metin-duzen .metin li { overflow-wrap: break-word; }" in (WEB / "temel.css").read_text(encoding="utf-8")


def test_cloudflare_yapilandirmasi_ve_404_sayfasi():
    """wrangler.jsonc: web/ statik varlık olarak yayımlanır, bulunamayan adreste web/404.html döner. 404 sayfası her derinlikte
    (ör. /a/b) aynı görünür (<base href="/">, yerel varlıklar), sitenin paletini ve çubuğunu kullanır, iki dillidir ve
    arama motorlarına kapalıdır; canonical ve hreflang taşımaz."""
    import json
    w = json.loads((KOK / "wrangler.jsonc").read_text(encoding="utf-8"))
    assert w == {"name": "vetoatlas", "compatibility_date": "2026-10-01",
                 "assets": {"directory": "./web", "not_found_handling": "404-page"}}
    s = (WEB / "404.html").read_text(encoding="utf-8")
    bas = s[:s.index("</head>")]
    assert '<base href="/">' in bas and bas.index('<base href="/">') < bas.index('<link rel="icon"')
    assert '<meta name="robots" content="noindex">' in bas and 'rel="canonical"' not in bas and 'rel="alternate"' not in bas
    assert '<body data-sayfa="404">' in s and '<header id="cubuk" class="cubuk"></header>' in s and '<script src="cubuk.js"></script>' in bas
    assert "<h1>Sayfa bulunamadı</h1>" in s and "<h1>Page not found</h1>" in s and 'data-dil="en" hidden' in s
    for ad in ("hikaye", "vetolar", "hakkinda"):
        assert f'href="{ad}.html"' in s and f'href="{ad}.html?lang=en"' in s, ad
    assert "--zemin: #FBF8F1" in bas and ':root[data-theme="dark"]' in bas and "prefers-color-scheme" not in s


def test_kok_adres_sunucuda_hikayeye_yonlenir():
    """web/_redirects (Workers statik varlıkları): kök adres 302 ile /hikaye'ye gider; gelen sorgu (?lang=en) korunur
    (wrangler 4.150.0 dev ile denetlendi: /?lang=en -> 302 /hikaye?lang=en). Kurallar eşleşen dosyadan (index.html) önce
    uygulanır. web/index.html yedek kalır: yerel açılışta ve sunucusuz kopyada sorguyu koruyarak hikâyeye gider."""
    kurallar = [l for l in (WEB / "_redirects").read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    assert kurallar == ["/ /hikaye 302"]
    i = (WEB / "index.html").read_text(encoding="utf-8")
    assert '<meta http-equiv="refresh" content="0; url=hikaye.html">' in i
    assert 'location.replace("hikaye.html" + q + location.hash)' in i
