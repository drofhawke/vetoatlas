"""
Yayın hazırlığı: yayın adresi (vetoatlas.com) etiketleri, beta şeridi, Hakkında'daki yayımlayan, iletişim ve atıf
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


def test_beta_seridi():
    c = (WEB / "cubuk.js").read_text(encoding="utf-8")
    assert 'beta: "Beta sürümü", hata: "Hata bildirin"' in c and 'beta: "Beta", hata: "Report an error"' in c
    assert 'var ILETISIM = "iletisim@vetoatlas.com";' in c and """<a href="mailto:' + ILETISIM + '">' + ILETISIM""" in c
    assert 'serit.id = "beta-serit"' in c and "yer.parentNode.insertBefore(serit, yer)" in c
    assert '"@media print { .cubuk, .beta-serit { display: none; } }",' in c


def test_hakkinda_yayimlayan_iletisim_atif():
    h = (WEB / "hakkinda.html").read_text(encoding="utf-8")
    orcid = f'ORCID <a href="https://orcid.org/{ORCID}">{ORCID}</a>'
    posta = '<a href="mailto:iletisim@vetoatlas.com">iletisim@vetoatlas.com</a>'
    assert f"<p>Yayımlayan: Nuh Mehmet Yıldız, bağımsız araştırmacı · {orcid}</p>" in h
    assert f"<p>Published by Nuh Mehmet Yıldız, independent researcher · {orcid}</p>" in h
    assert f"<p>İletişim: {posta}. Hata bildirimleri" in h and f"<p>Contact: {posta}. Error reports" in h
    assert '<h2 id="atif">Bu çalışmaya atıf</h2>' in h and '<h2 id="en-atif">Cite this work</h2>' in h
    assert "Yıldız, Nuh Mehmet (2026). <i>Veto Atlası</i> (sürüm 1.0.0)." in h
    assert 'Yıldız, Nuh Mehmet (2026). <i lang="tr">Veto Atlası</i> (version 1.0.0).' in h
    assert h.count(f'<a href="{ADRES}">{ADRES}</a> · DOI: <a href="https://doi.org/{DOI}">{DOI}</a></p></div>') == 2
    assert "[DOI]" not in h
    # Kutuların içinde paragraf ve liste alt boşluğu yok (üst ve alt iç boşluk eşit)
    assert ".kutu .atif, .kutu .indir { margin: 0; }" in h
    assert "yer-tutucu" not in h
    # Lisans cümlesi atıf kutusunun altında; LICENSE-DATA'nın sitedeki kopyasına bağlanır
    assert ('<p class="lisans">Atlasın kodu MIT lisansıyla, derlemesi CC BY 4.0 lisansıyla yayımlanır; üçüncü taraf içerikler\n'
            '    kendi lisans ve koşullarına tabidir. Ayrıntılar: <a href="LICENSE-DATA.txt">LICENSE-DATA</a>.</p>') in h
    assert ('<p class="lisans">The atlas code is released under the MIT licence and the compilation under CC BY 4.0; third-party\n'
            '    content remains subject to its own licences and terms. Details: <a href="LICENSE-DATA.txt">LICENSE-DATA</a>.</p>') in h


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
