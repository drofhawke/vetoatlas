"""
Yayın denetimleri: sayfalar üçüncü taraf adrese istek atmaz; metodoloji sayfası güncel ve iki dilli.
Ağ isteği yapılmaz; sayfa kaynakları ve stil dosyaları okunarak denetlenir.
"""
import re
from html.parser import HTMLParser
from pathlib import Path

from veto_atlasi import metodoloji

KOK = Path(__file__).resolve().parents[1]
WEB = KOK / "web"
SAYFALAR = sorted(WEB.glob("*.html"))


class KaynakToplayici(HTMLParser):
    """Tarayıcının sayfa yüklenirken kendiliğinden istediği adresler (bağlantılar <a> hariç)."""

    def __init__(self):
        super().__init__()
        self.adresler, self.satir_ici_stil, self.betikler = [], [], []
        self._betik = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "img", "iframe", "audio", "video", "source", "embed", "track", "input") and a.get("src"):
            self.adresler.append(a["src"])
        if tag == "link" and a.get("href") and a.get("rel") not in ("alternate", "canonical"):
            self.adresler.append(a["href"])
        if tag == "object" and a.get("data"):
            self.adresler.append(a["data"])
        for ad in ("srcset", "poster", "background"):
            if a.get(ad):
                self.adresler.append(a[ad])
        if a.get("style"):
            self.satir_ici_stil.append(a["style"])
        self._betik = tag in ("script", "style")

    def handle_endtag(self, tag):
        self._betik = False

    def handle_data(self, data):
        if self._betik:
            self.betikler.append(data)


def dis_adres_mi(u: str) -> bool:
    return bool(re.match(r"^\s*(https?:)?//", u, re.I))


def css_adresleri(css: str) -> list[str]:
    return re.findall(r"url\(\s*['\"]?([^'\")]+)", css) + re.findall(r"@import\s+['\"]([^'\"]+)", css)


def test_sayfalar_ucuncu_taraf_adrese_istek_atmaz():
    assert {p.name for p in SAYFALAR} >= {"index.html", "hikaye.html", "vetolar.html", "hakkinda.html", "metodoloji.html"}
    for sayfa in SAYFALAR:
        t = KaynakToplayici()
        t.feed(sayfa.read_text(encoding="utf-8"))
        adresler = [u for u in t.adresler + [u for s in t.satir_ici_stil + t.betikler for u in css_adresleri(s)]
                    if not u.startswith("data:")]  # gömülü (data:) adresler dosya değildir
        dis = [u for u in adresler if dis_adres_mi(u)]
        assert not dis, (sayfa.name, dis)
        # Yerel kaynaklar gerçekten var
        for u in adresler:
            yol = (WEB / u.split("?")[0].split("#")[0])
            assert yol.exists(), (sayfa.name, u)
        # Betikler ağ isteği başlatmaz (fetch, XHR, dinamik içe aktarma, WebSocket, beacon)
        betik = "\n".join(t.betikler)
        for kalip in (r"\bfetch\s*\(", r"XMLHttpRequest", r"\bimport\s*\(", r"WebSocket", r"sendBeacon", r"new\s+Image\b",
                      r"EventSource"):
            assert not re.search(kalip, betik), (sayfa.name, kalip)


def test_tek_dosya_surumu_guncel_ve_kendine_yeter():
    from veto_atlasi import tek_dosya
    yol = WEB / tek_dosya.CIKTI
    assert yol.exists(), "python scripts/10_tek_dosya.py"
    s = yol.read_text(encoding="utf-8")
    # Girdi özeti: sekiz sayfa, iki veri dosyası, yazı tipleri değiştiyse dosya yeniden üretilmeli (04 üretir)
    import tempfile, shutil
    with tempfile.TemporaryDirectory() as d:
        kok = Path(d); (kok / "web").mkdir(); shutil.copytree(WEB / "fonts", kok / "web/fonts")
        for ad in ("veri.js", "temsil_veri.js", "harita_veri.js", "cubuk.js", "suzgec.js", "metin.js", "temel.css", "logo-cubuk-b.svg", "logo-cubuk-b-koyu.svg", "isaret.svg", "isaret-koyu.svg", "favicon.ico", "favicon.svg", "apple-touch-icon.png",
                   *[x[0] for x in tek_dosya.SAYFALAR]):
            shutil.copy(WEB / ad, kok / "web" / ad)
        yeni = tek_dosya.uret(kok)
        assert tek_dosya.girdi_ozeti(kok) == tek_dosya.girdi_ozeti(KOK), "web/veto-atlasi-tek-dosya.html eski; scripts/04_web_verisi.py çalıştırın"
        assert yeni.read_text(encoding="utf-8") == s
    assert yol.stat().st_size < 8 * 1024 * 1024
    # Hiçbir dış ya da yerel dosya adresi yok: her şey gömülü (data: ve parent üzerinden)
    assert not re.search(r'<(script|link|img|source)[^>]+(src|href|srcset)="(?!data:)', s)
    assert "window.VETO_VERISI" in s and "window.TEMSIL_VERISI" in s and s.count("__FONT__") >= 12
    for kod in ("hikaye", "vetolar", "vizyon", "reform", "simulasyon", "temsil", "hakkinda", "metodoloji"):
        assert f'"{kod}":' in s
    for ad in ("Hikâye", "Vetolar", "Reform modelleri", "Reform models", "Kim temsil ediliyor?", "Nasıl yaptık?", "Who is represented?", "How we did it"):
        assert ad in s, ad
    for ad in ("Söz ve Kayıt", "Word and Record", "web/kartlar/"):
        assert ad in s


def test_tek_dosya_satir_sonundan_bagimsiz(tmp_path):
    """CRLF'li bir Windows çalışma ağacı (core.autocrlf=true) da açık depodaki (LF) ile aynı tek dosyayı üretir."""
    import shutil
    from veto_atlasi import tek_dosya
    shutil.copytree(WEB, tmp_path / "web", ignore=shutil.ignore_patterns("kartlar", "veri"))
    for p in (tmp_path / "web").rglob("*"):
        if p.is_file() and p.suffix in {".html", ".js", ".css", ".svg"}:
            v = p.read_bytes().replace(b"\r\n", b"\n")
            p.write_bytes(v.replace(b"\n", b"\r\n"))
    yeni = tek_dosya.uret(tmp_path)
    assert yeni.read_text(encoding="utf-8") == (WEB / tek_dosya.CIKTI).read_text(encoding="utf-8")


def test_stil_ve_veri_dosyalari_dis_adres_istemez():
    for css in WEB.rglob("*.css"):
        dis = [u for u in css_adresleri(css.read_text(encoding="utf-8")) if dis_adres_mi(u)]
        assert not dis, (css.name, dis)
        for u in css_adresleri(css.read_text(encoding="utf-8")):
            assert (css.parent / u).exists(), (css.name, u)
    veri = (WEB / "veri.js").read_text(encoding="utf-8")
    assert not re.search(r"\bfetch\s*\(|XMLHttpRequest|<script|<img|<link", veri)


def test_yazi_tipi_lisanslari_yaninda():
    fonts = WEB / "fonts"
    assert list(fonts.glob("*.woff2"))
    for lisans in ("OFL-source-serif-4.txt", "OFL-source-sans-3.txt"):
        metin = (fonts / lisans).read_text(encoding="utf-8")
        assert "SIL Open Font License, Version 1.1" in metin and "Adobe" in metin, lisans


def test_metodoloji_sayfasi_guncel_ve_iki_dilli():
    tr = (KOK / "METODOLOJI.md").read_text(encoding="utf-8")
    en = (KOK / "METODOLOJI_EN.md").read_text(encoding="utf-8")
    assert metodoloji.yapi_farklari(tr, en) == []
    sayfa = (WEB / "metodoloji.html").read_text(encoding="utf-8")
    # 04 çalıştırıldıktan sonra sayfa iki Markdown dosyasıyla birebir aynı olmalı
    assert sayfa == metodoloji.sayfa_uret(tr, en), "web/metodoloji.html eski; scripts/04_web_verisi.py çalıştırın"
    assert 'data-dil="tr"' in sayfa and 'data-dil="en"' in sayfa
    for n, _ in metodoloji.bolumler(tr):
        assert f'id="{metodoloji.kimlik(n)}"' in sayfa and f'id="en-{metodoloji.kimlik(n)}"' in sayfa, n


def test_markdown_donusturucu():
    h1, govde = metodoloji.md_html("# Başlık\n\n## 2. Üst\n\n### 2.1. Alt\n\nMetin **kalın** ve *italik* `kod_*x*`.\n\n- bir\n  devam\n- iki <b>\n")
    assert h1 == "Başlık"
    assert '<h2 id="bolum-2">2. Üst</h2>' in govde and '<h3 id="bolum-2-1">2.1. Alt</h3>' in govde
    assert "<strong>kalın</strong>" in govde and "<em>italik</em>" in govde and "<code>kod_*x*</code>" in govde
    assert "<li>bir devam</li>" in govde and "<li>iki &lt;b&gt;</li>" in govde
    assert metodoloji.yapi_farklari("## 1. a\n## 2. b\n", "## 1. a\n") != []
    # İngilizce metindeki Türkçe ifadeler: [metin]{lang=tr}
    assert '<span lang="tr">“Dünya”</span> y.' in metodoloji.md_html("# B\n\nX [“Dünya”]{lang=tr} y.\n")[1]


def test_hakkinda_metodoloji_sayfasina_baglanir():
    s = (WEB / "hakkinda.html").read_text(encoding="utf-8")
    assert "../METODOLOJI.md" not in s
    assert 'href="metodoloji.html"' in s and 'href="metodoloji.html?lang=en"' in s


def test_yazi_tipleri_yerel_ozetli_ve_gomulu():
    """ADIM 48: fonts.css'teki her woff2 yereldir (dış adres yok), diskte vardır, woff2 imzası taşır ve SHA-256'sı
    web/fonts/README.md tablosundakiyle aynıdır; klasörde tanımsız woff2 yoktur. Source Sans 3'ün 400 ağırlıklı italik kesimi
    (latin, latin-ext) tanımlıdır; tarayıcı italiği yapay üretmez. Tek dosya bütün yazı tiplerini gömer."""
    import hashlib
    fonts = WEB / "fonts"
    css = (fonts / "fonts.css").read_text(encoding="utf-8")
    readme = (fonts / "README.md").read_text(encoding="utf-8")
    tablo = dict(re.findall(r"\| `([\w.-]+\.woff2)` \| `([0-9a-f]{64})` \|", readme))
    adlar = re.findall(r"src: url\(([^)]+)\) format\('woff2'\)", css)
    assert len(adlar) == 13 and sorted(adlar) == sorted(p.name for p in fonts.glob("*.woff2")) == sorted(tablo)
    for ad in adlar:
        assert not dis_adres_mi(ad), ad
        veri = (fonts / ad).read_bytes()
        assert veri[:4] == b"wOF2" and hashlib.sha256(veri).hexdigest() == tablo[ad], ad
    for alt in ("latin", "latin-ext"):
        blok = re.search(r"/\* source-sans-3-" + alt + r"-400-italic \*/\n@font-face \{(.*?)\}", css, re.S)[1]
        assert "font-family: 'Source Sans 3';" in blok and "font-style: italic;" in blok and "font-weight: 400;" in blok, alt
    tek = (WEB / "veto-atlasi-tek-dosya.html").read_text(encoding="utf-8")
    for ad in adlar:
        assert f'"{ad}":' in tek and f"__FONT__{ad}" in tek, ad  # FONTLAR sözlüğünde ve gömülü @font-face'te
    # Alt yazılar Source Sans 3 (400) italik: gerçek kesimi kullanır
    h = (WEB / "hikaye.html").read_text(encoding="utf-8")
    assert "font-style: italic; }" in h[h.index(".istat-alt {"):h.index("}", h.index(".istat-alt {")) + 2]
