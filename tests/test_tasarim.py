"""
Tasarım dili (web/temel.css; kaynaklar/kimlik/KILAVUZ.md bölüm 2): 4 px ızgarası, iki yazı tipi, dört yazı boyutu,
bütün metin sola yaslı (iki yana yaslama ve heceleme yok; ADIM 41), etiketler büyük harfsiz, bölümler ince çizgi ve
boşlukla ayrılır.

Taranan stil kaynakları: sayfaların <style> blokları, ortak çubuk (web/cubuk.js), temel.css, metodoloji şablonu
(veto_atlasi/metodoloji.py) ve tek dosya üst belgesi (veto_atlasi/tek_dosya.py). Hesaplanmış değerler (her öğenin
boşluğu, yazı boyutu, satır yüksekliği ve ailesi) ayrıca tarayıcıda ölçülür.
"""
import re

from conftest import KOK

WEB = KOK / "web"
SAYFALAR = ["hikaye", "vetolar", "vizyon", "reform", "simulasyon", "temsil", "hakkinda", "metodoloji"]
BOSLUK = r"margin(?:-(?:top|right|bottom|left))?|padding(?:-(?:top|right|bottom|left))?|gap|row-gap|column-gap|inset"
BASAMAK = {0, 4, 8, 12, 16, 24, 32, 48, 64, 96}
# İki yana yaslama ya da otomatik heceleme (CSS bildirimi ya da betikten stil ataması)
YASLAMA = re.compile(r"text-align(?:-last)?\s*:\s*justify|text-justify\s*:|hyphens\s*:\s*auto"
                     r"|textAlign\s*=\s*[\"']justify|hyphens\s*=\s*[\"']auto|\.hyphens\s*=")
TEMEL = (WEB / "temel.css").read_text(encoding="utf-8")


def stil_kaynaklari():
    for ad in SAYFALAR:
        s = (WEB / f"{ad}.html").read_text(encoding="utf-8")
        yield f"{ad}.html", "\n".join(re.findall(r"<style>(.*?)</style>", s, re.S))
    c = (WEB / "cubuk.js").read_text(encoding="utf-8")
    # Çubuktaki logo yazısı (.c-yazi) yazı ölçeğinin dışındadır: logo-cubuk-b.svg'nin ölçüleriyle çizilir (27,3 px / 40 px, telefonda aynı
    # oranla 23,2 ve 20,8 px; kendi kesimi); KILAVUZ bölüm 3. Bu kurallar taramanın dışında tutulur
    yield "cubuk.js", "\n".join(satir for satir in c[c.index("var CSS = ["):c.index("].join(")].split("\n") if ".c-logo .c-yazi {" not in satir)
    yield "temel.css", TEMEL
    m = (KOK / "veto_atlasi/metodoloji.py").read_text(encoding="utf-8")
    yield "metodoloji.py", "\n".join(re.findall(r"<style>(.*?)</style>", m, re.S))
    t = (KOK / "veto_atlasi/tek_dosya.py").read_text(encoding="utf-8")
    yield "tek_dosya.py", "\n".join(re.findall(r"<style>(.*?)</style>", t, re.S))


def bildirimler(css, ozellik):
    return [d.strip() for d in re.findall(r"(?<![\w-])(?:" + ozellik + r")\s*:\s*([^;}\"]+)", css)]


def test_temel_dosya_her_sayfada_ve_tek_dosyada():
    for ad in SAYFALAR:
        s = (WEB / f"{ad}.html").read_text(encoding="utf-8")
        baglanti = '<link rel="stylesheet" href="fonts/fonts.css">\n<link rel="stylesheet" href="temel.css">'
        assert baglanti in s and s.index(baglanti) < s.index("<style>"), ad  # sayfanın kendi stilinden önce
    assert '<link rel="stylesheet" href="temel.css">' in (KOK / "veto_atlasi/metodoloji.py").read_text(encoding="utf-8")
    tek = (WEB / "veto-atlasi-tek-dosya.html").read_text(encoding="utf-8")
    assert '<style id="temel">' in tek and 'href=\\"temel.css\\"' not in tek and "--yz-gosterge: 96px" in tek


def test_dort_yazi_boyutu():
    """Dört boyut belirteci ve yalnızca metin sayfasının bölüm başlığı için beşincisi (--yz-bolum 24/32, dar ekranda 22/28;
    K12a); dar ekranda yalnızca bölüm başlığı, başlık ve gösterge küçülür. Bütün yazı boyutları belirteçten gelir."""
    kok = TEMEL[TEMEL.index(":root {"):TEMEL.index("}")]
    assert re.findall(r"--yz-([\w-]+):\s*(\d+)px", kok) == [("kucuk", "15"), ("govde", "18"), ("bolum", "24"), ("baslik", "40"), ("gosterge", "96")]
    assert re.findall(r"--sa-([\w-]+):\s*(\d+)px", kok) == [("kucuk", "24"), ("govde", "28"), ("bolum", "32"), ("baslik", "48"), ("gosterge", "96")]
    dar = TEMEL[TEMEL.index("@media (max-width: 760px)"):]
    dar = dar[:dar.index("}\n}") + 1]
    assert re.findall(r"--yz-([\w-]+):\s*(\d+)px", dar) == [("bolum", "22"), ("baslik", "32"), ("gosterge", "56")]
    assert re.findall(r"--sa-([\w-]+):\s*(\d+)px", dar) == [("bolum", "28"), ("baslik", "40"), ("gosterge", "56")]
    bolum_kullanan = []
    for ad, css in stil_kaynaklari():
        for d in bildirimler(css, "font-size"):
            assert d == "inherit" or re.fullmatch(r"var\(--yz-(kucuk|govde|bolum|baslik|gosterge)\)", d), (ad, d)
            if d == "var(--yz-bolum)":
                bolum_kullanan.append(ad)
        for d in bildirimler(css, "font"):
            assert d == "inherit" or re.search(r"var\(--yz-(kucuk|govde|baslik|gosterge)\)/var\(--sa-\1\)", d), (ad, d)
    # Beşinci boyut yalnızca metin sayfasının bölüm başlığında (temel.css .duz-yazi h2)
    assert bolum_kullanan == ["temel.css"] and "font-size: var(--yz-bolum); line-height: var(--sa-bolum); }" in TEMEL


def test_satir_yuksekligi_ve_boyutlar_izgarada():
    for ad, css in stil_kaynaklari():
        for d in bildirimler(css, "line-height"):
            assert re.fullmatch(r"var\(--sa-(kucuk|govde|bolum|baslik|gosterge)\)", d), (ad, d)
    for ad, deger in re.findall(r"--(sa-[\w]+|b\d+|kenar|olcu|kap):\s*(\d+)px", TEMEL):
        assert int(deger) % 4 == 0, (ad, deger)


def test_iki_yazi_tipi():
    for ad, css in stil_kaynaklari():
        for d in bildirimler(css, "font-family"):
            assert d in ("var(--serif)", "var(--sans)", "inherit"), (ad, d)
    aileler = set(re.findall(r"font-family:\s*[\"']([^\"']+)[\"']", (WEB / "fonts/fonts.css").read_text(encoding="utf-8")))
    assert aileler == {"Source Serif 4", "Source Sans 3", "Veto Atlası Logo"}  # üçüncüsü yalnızca çubuktaki logo yazısı (10 glif)
    # Kod ve özet değerleri tarayıcının eş aralıklı yazı tipine düşmez
    assert "code, kbd, samp, pre { font-family: var(--sans);" in TEMEL and "button, input, select, textarea { font: inherit; }" in TEMEL


def test_bosluklar_basamaklardan():
    """Bütün boşluklar 4 px'in katı ve 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 basamaklarından; em/rem boşluk yok.
    Tek istisna okuma metnindeki kod kutusunun yatay iç boşluğudur (temel.css, .duz-yazi code: 0 0.12em; H-belge-1)."""
    assert ".duz-yazi code { font-size: var(--yz-kucuk); padding: 0 0.12em;" in TEMEL and TEMEL.count("0.12em") == 1
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "Tek istisna okuma metnindeki kod kutusunun yatay iç boşluğudur (0.12em" in kilavuz
    for ad, css in stil_kaynaklari():
        for d in bildirimler(css, BOSLUK):
            if ad == "temel.css" and d == "0 0.12em":
                continue
            dis = re.sub(r"\([^()]*\)", "", d)  # env(), calc(), var() içi hariç
            for sayi, birim in re.findall(r"(-?\d*\.?\d+)(px|rem|em)\b", dis):
                assert birim == "px" and abs(float(sayi)) in BASAMAK, (ad, d)
    assert "--b1: 4px; --b2: 8px; --b3: 12px; --b4: 16px; --b6: 24px; --b8: 32px; --b12: 48px; --b16: 64px; --b24: 96px;" in TEMEL


def test_sola_yaslama_heceleme_yok():
    """ADIM 41, kalıcı kural: bütün metin sola yaslı; iki yana yaslama ve heceleme hiçbir genişlikte kullanılmaz.
    Sağa yaslama yalnızca tablolardaki sayılar ve sayaçlar için (tabular-nums taşıyan kurallar)."""
    assert "body { text-align: left; -webkit-hyphens: none; hyphens: none; }" in TEMEL
    for ad, css in stil_kaynaklari():
        assert not YASLAMA.search(css), ad
        for d in bildirimler(css, "hyphens|-webkit-hyphens"):
            assert d == "none", (ad, d)
        for kural in re.findall(r"[^{}]*\{[^{}]*\}", css):
            hiza = set(bildirimler(kural, "text-align"))
            assert hiza <= {"left", "right"}, (ad, kural.strip())
            if "right" in hiza:
                assert "font-variant-numeric: tabular-nums" in kural, (ad, kural.strip())
    # Sayfa dosyalarının tamamı (betikler dahil), ortak betikler ve tek dosya
    for yol in [WEB / f"{ad}.html" for ad in SAYFALAR] + [WEB / "veto-atlasi-tek-dosya.html", WEB / "cubuk.js", WEB / "suzgec.js", WEB / "metin.js"]:
        assert not YASLAMA.search(yol.read_text(encoding="utf-8")), yol.name
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "**Hizalama (kalıcı kural).** Bütün metin sola yaslıdır; iki yana yaslama ve heceleme hiçbir genişlikte kullanılmaz." in kilavuz


def test_etiketler_buyuk_harfsiz():
    """ADIM 41: etiketler cümle düzeninde; etiket oldukları küçük boyut ve ikincil renkle gösterilir. Büyük harf
    dönüşümü, küçük büyük harf ve açık harf aralığı yok (büyük başlıklardaki hafif daraltma hariç)."""
    for ad, css in stil_kaynaklari():
        assert not re.search(r"text-transform\s*:\s*(?!none\b)|small-caps|font-variant-caps", css), ad
        for d in bildirimler(css, "letter-spacing"):
            assert d.startswith("-") or d in ("0", "normal"), (ad, d)
    h = (WEB / "hikaye.html").read_text(encoding="utf-8")
    assert ".epigraf figcaption { margin: var(--b2) 0 0; font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); color: var(--murekkep-2); }" in h
    v = (WEB / "vizyon.html").read_text(encoding="utf-8")
    # Söz ve Kayıt'ın sütun başlıkları (ADIM 54; "Veri setinde" satır etiketinin yerine)
    assert "  font: 600 var(--yz-kucuk)/var(--sa-kucuk) var(--sans); color: var(--murekkep-2); }\n.c-cubuklu .sutun-basliklari" in v
    assert '"sutun.soz": "Söz", "sutun.kayit": "Kayıt"' in v and '"sutun.soz": "Word", "sutun.kayit": "Record"' in v
    s = (WEB / "simulasyon.html").read_text(encoding="utf-8")
    assert ".etiket { display: inline-block; font-size: var(--yz-kucuk); color: var(--murekkep-2); vertical-align: middle; margin-left: 8px;" in s  # çerçevesiz (20 Ekim 2026)
    assert "      kitapBolum: ({ b }) =>" in s and "      kitapBolumEn: ({ b }) =>" in s and "kitapta:" not in s  # "Kitabın girişinden" satırı
    # Paylaşım kartlarının üst etiketi ("Veto Atlası", "Söz ve Kayıt"): betik ve üretilmiş bütün kartlar
    kart = (KOK / "scripts/08_paylasim_kartlari.py").read_text(encoding="utf-8")
    assert '.ust {{ font-family: "Source Sans 3", "Segoe UI", sans-serif; font-weight: 600; font-size: 22px; color: {MUREKKEP2}; }}' in kart
    kartlar = sorted((WEB / "kartlar").glob("*.html"))
    assert len(kartlar) == 44
    for ad, kaynak in [("08_paylasim_kartlari.py", kart)] + [(p.name, p.read_text(encoding="utf-8")) for p in kartlar]:
        assert not re.search(r"text-transform\s*:\s*(?!none\b)|small-caps|font-variant-caps", kaynak), ad
        for d in bildirimler(kaynak, "letter-spacing"):
            assert d.startswith("-") or d in ("0", "normal"), (ad, d)
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "Büyük harf dönüşümü, küçük büyük harf ve açık harf aralığı kullanılmaz" in kilavuz
    assert "paylaşım kartlarının üst etiketi" in kilavuz


def test_bolum_ayrimi():
    assert "main > :is(section, aside) + section { margin-top: var(--b16); padding-top: var(--b8); border-top: 1px solid var(--cizgi); }" in TEMEL
    # ADIM 50, metin sayfalarında dikey ritim: bölümler arası 32 px, ayırıcı çizgi ile bölüm başlığı arası 24 px, başlığın
    # altı 12 px; alt bölüm başlığı çizgisiz, üstü 24 px, altı 12 px (tarayıcıda ölçüldü: 32 / 1 px çizgi / 24 / 12; h3 24 / 12)
    assert (".duz-yazi h2 { margin: var(--b8) 0 var(--b3); padding-top: var(--b6); border-top: 1px solid var(--cizgi); "
            "font-size: var(--yz-bolum); line-height: var(--sa-bolum); }") in TEMEL
    assert ".duz-yazi h3 { margin: var(--b6) 0 var(--b3); }" in TEMEL
    assert ".duz-yazi :is(p, ul, ol, dl, blockquote, table, pre) { margin-bottom: var(--b4); }" in TEMEL
    assert (WEB / "hakkinda.html").read_text(encoding="utf-8").count('class="icerik duz-yazi metin-duzen"') == 2
    assert 'class="duz-yazi metin-duzen"' in (KOK / "veto_atlasi/metodoloji.py").read_text(encoding="utf-8")
    assert "4 px" in (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")


def test_metin_sayfasi_duzeni():
    """ADIM 50: metin sayfası (Hakkında, Metodoloji). Okuma metni solda, 68ch (satır başına yaklaşık 70–80 karakter); 1100 px ve
    üstünde sağ sütunda kaydırdıkça yerinde duran "Bu sayfada" dizini (çubuğun 24 px altında), altında başlığın hemen altında
    katlanabilir kutu. Etkin bağlantı mürekkep rengi ve 2 px çizgiyle (kırmızı ret oyları ve vetolar içindir). Gizli dil
    <main> öğesi ızgarada da gizli kalır. Reform modellerinde giriş metni ve "Nasıl okunur?" aynı ölçüde."""
    assert "--olcu-metin: 68ch;" in TEMEL and "en fazla 68 karakter" not in TEMEL
    assert ".metin-duzen .metin, .metin-dizin { max-width: var(--olcu-metin); }" in TEMEL
    dar, genis = TEMEL[:TEMEL.index("@media (min-width: 1100px) {")], TEMEL[TEMEL.index("@media (min-width: 1100px) {"):]
    genis = genis[:genis.index("\n}\n")]
    assert ".bu-sayfada-yan { display: none; }" in dar and ".metin-dizin:empty { display: none; }" in dar
    assert ".metin-duzen:not([hidden]) { display: grid; grid-template-columns: minmax(0, var(--olcu-metin)) 288px; column-gap: var(--b16);" in genis
    assert ".metin-duzen > .metin-dizin { grid-column: 2; grid-row: 2;" in genis and ".bu-sayfada-kutu { display: none; }" in genis
    assert ".bu-sayfada-yan { display: block; position: sticky; top: var(--b6);" in genis
    assert ".c-cubuklu .bu-sayfada-yan { top: calc(76px + var(--b6));" in genis  # çubuk 76 px
    assert ".bu-sayfada a[aria-current] { color: var(--murekkep); border-left-color: var(--murekkep); }" in TEMEL
    assert "--vurgu" not in TEMEL
    r = (WEB / "reform.html").read_text(encoding="utf-8")
    assert "line-height: var(--sa-govde); max-width: var(--olcu-metin); margin: 0 0 12px; }" in r
    assert "details.yontem" not in r  # okuma kutusu yok (20 Ekim 2026)


# ADIM 52, kalıcı kural (KILAVUZ bölüm 2, "Kartlar"): tam genişlikteki (bulunduğu sütunu dolduran) hiçbir kart tek bir dar
# metin sütunu taşımaz; ya iki sütuna bölünür ya da genişliği metin sütununa (68ch, --olcu-metin) iner. Kart: işaretlemede ya
# da şablonda "kutu" sınıfı taşıyan öğe ya da zemini --yuzey olan çerçeveli kutu. Her kart çözümüyle burada sınıflandırılır;
# yeni bir kart eklenince test sınıflandırma ister.
#   iki: iki sütun (760 px altında tek)   olcu: genişlik metin sütunu   genis: tablo, grafik ya da form genişliği doldurur
#   izgara: kartlar yan yana   metin: kart bir metin sütununun içinde ya da metni kartı dolduruyor
KARTLAR = {
    "hikaye": {},
    "vetolar": {},  # grafik ve konular listesi kutusuz (20 Ekim 2026)
    "vizyon": {"soz-kayit kutu": "iki", "kutu": "iki", "tablo-kap kutu": "genis", ".kart": "izgara"},
    "reform": {"olcutler kutu": "olcu", "tablo-kap kutu": "genis"},
    "simulasyon": {"panel kutu": "izgara", "sonuc-blok kutu": "iki", "serit kutu": "genis", "tablo-kap kutu": "genis"},
    "temsil": {"kutu grup": "izgara", "kutu": "genis", "kutu ulke-karti": "genis"},  # ülke kartı: çok sütunlu bilgi ızgarası
    "hakkinda": {},  # doğrulama sayıları kutusuz (20 Ekim 2026)
    "metodoloji": {},
}
# İki sütunlu kartların düzeni ve 760 px altındaki tek sütun (içindekiler listesi sütun genişliğine göre kendisi tek sütuna iner)
IKI_SUTUN = {
    ("vizyon", "soz-kayit kutu"): (".soz-satir { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);",
                                   ".soz-satir { grid-template-columns: minmax(0, 1fr); }"),
    ("vizyon", "kutu"): (".model > .kutu { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr); }",
                         ".model > .kutu { grid-template-columns: 1fr; }"),
    ("simulasyon", "sonuc-blok kutu"): (".sonuc-kartlar { display: grid; grid-template-columns: 1fr 1fr;", ".sonuc-kartlar { grid-template-columns: 1fr; }"),
}
ETKILESIMLI = re.compile(r"button|select|input|dugme|\.atla|::before")


def test_kartlar_dar_metin_sutunu_tasimaz():
    for ad, kartlar in KARTLAR.items():
        s = (WEB / f"{ad}.html").read_text(encoding="utf-8")
        css = re.sub(r"/\*.*?\*/", "", "\n".join(re.findall(r"<style>(.*?)</style>", s, re.S)), flags=re.S)  # açıklamasız
        # İşaretlemedeki ve şablonlardaki kartlar ("kutu" sınıfı)
        isaret = {c for c in re.findall(r'class="([^"]*)"', s) if "kutu" in c.split()}
        assert isaret == {k for k in kartlar if not k.startswith(".")}, (ad, isaret)
        # Zemini --yuzey olan çerçeveli kutular (düğmeler ve form öğeleri hariç)
        for secici, govde in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
            secici = secici.strip()
            if ("background: var(--yuzey)" in govde and secici != ".kutu" and not ETKILESIMLI.search(secici)
                    and re.search(r"border: 1px solid var\(--cizgi\)|box-shadow: inset 0 0 0 1px var\(--cizgi\)", govde)):
                assert secici in kartlar, (ad, secici)
        for kart, cozum in kartlar.items():
            sinif = kart.lstrip(".").split()[0]
            if cozum == "olcu":
                assert re.search(rf"\.{sinif} \{{[^}}]*max-width: var\(--olcu-metin\);", css), (ad, kart)
            elif cozum == "iki":
                genis, dar = IKI_SUTUN[(ad, kart)]
                assert genis in css, (ad, kart)
                if dar:
                    m = css[css.index("@media (max-width: 760px) {"):]
                    assert dar in m[:m.index("\n}")], (ad, kart)
    # Ortak dosyadaki tek kart: dar ekranda "Bu sayfada" kutusu, metin sütunu genişliğinde
    temel = re.sub(r"/\*.*?\*/", "", TEMEL, flags=re.S)
    kutular = [k.strip() for k, g in re.findall(r"([^{}]+)\{([^{}]*)\}", temel) if "background: var(--yuzey)" in g and "dugme" not in k]
    assert kutular == [".bu-sayfada-kutu"] and ".metin-duzen .metin, .metin-dizin { max-width: var(--olcu-metin); }" in TEMEL
    # Kitaptaki model: solda bölüm başlığı ve özet, sağda kitaptan alıntılar ve künyeleri
    v = (WEB / "vizyon.html").read_text(encoding="utf-8")
    assert ('`<div class="kutu" role="row"><div class="model-ozet" role="cell"><h3>${t(b)}</h3><p>${t(o)}</p></div>'
            '<div class="model-alinti" role="cell">${ids.map(kitapAlinti).join("")}</div></div>`') in v
    assert ".model-alinti { padding: 24px; border-left: 2px solid var(--cizgi); }" in v
    assert ".model-alinti { border-left: none; border-top: 1px dashed var(--cizgi);" in v
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "**Kartlar (kalıcı kural).** Tam genişlikteki, yani bulunduğu sütunu dolduran hiçbir kart tek bir dar metin sütunu" in kilavuz


def test_cubuk_ve_alt_bilgi_notu_izgarada():
    """Alt çizgi iç gölgeyle: çubuk 76 px (dar ekranda 64 px). Beta şeridi yok (20 Ekim 2026); beta notu her sayfanın altında
    tek satır, sayfanın alt bilgisi yoksa ince çizgili alt bilgi (64 px üstten boşluk, 32 px iç boşluk)."""
    c = (WEB / "cubuk.js").read_text(encoding="utf-8")
    assert "box-shadow: inset 0 -1px 0 var(--cizgi);" in c and "border-bottom: 1px solid var(--cizgi); font-family" not in c
    assert "min-height: 76px; }" in c and '"  .cubuk { min-height: 64px; }"' in c
    assert "beta-serit" not in c and "beta-ic" not in c
    assert '".alt-not { font-family: var(--sans); font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); color: var(--murekkep-2); max-width: var(--olcu); margin: 0; }",' in c
    assert '"footer.alt-bilgi { border-top: 1px solid var(--cizgi); margin: 64px 0 0; padding: 32px 0 0; }",' in c


def test_koseler_ve_ok_isaretleri():
    """20 Ekim 2026: düğmeler, seçim düğmeleri, etiketler ve üst çubuğun dil/tema düğmeleri 6 px köşeli; hap biçimi
    (999 px) yok. Ok işareti bağlantı metninde yok; yalnızca yön düğmelerinde (Önceki, Sonraki) ve Hikâye 4. adımın sonuç
    satırında. Ya veto olmasaydı?'nın üç adım göstergesi kalktı (bölüm başlıkları yeter). Üst çubuğun dil, tema ve menü
    düğmeleri masaüstünde 40 px yükseklik (dokunma hedefi) ve 8 px yatay iç boşluk (21 Ekim 2026: İngilizce "Dark" düğmesi
    12 px ile kenara taşıyordu), telefonda 34 px ve 8 px."""
    for ad, css in stil_kaynaklari():
        assert "999px" not in css, ad
    c = (WEB / "cubuk.js").read_text(encoding="utf-8")
    assert (".cubuk .c-dil a, .cubuk .c-tema, .cubuk .c-menu { font: inherit; font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); "
            "min-height: 40px; display: inline-flex; align-items: center; padding: 0 8px; border: 1px solid var(--cizgi); border-radius: 6px;") in c
    assert '"  .cubuk .c-dil a, .cubuk .c-tema, .cubuk .c-menu { min-height: 34px; padding: 0 8px; }",' in c
    # İçeriğe atlama bağlantısı: odaklanınca görünür, 48 px
    assert ".cubuk .c-atla { position: absolute; left: 24px; top: -64px;" in c and '".cubuk .c-atla:focus { top: 16px; }",' in c
    oklu = set()
    for yol in [*(WEB / f"{ad}.html" for ad in SAYFALAR), WEB / "cubuk.js", WEB / "metin.js", WEB / "suzgec.js"]:
        oklu |= set(re.findall(r'"[^"\n]*[→↓←↑][^"\n]*"', yol.read_text(encoding="utf-8")))
    assert oklu == {'"14 evet, 1 hayır → düştü"', '"14 yes, 1 no → failed"', '"← Önceki"', '"Sonraki →"', '"← Previous"', '"Next →"'}
    s = (WEB / "simulasyon.html").read_text(encoding="utf-8")
    assert ".adimlar" not in s and 'aria-current="step"' not in s
    assert '"h.secim": "Kaydı seçin"' in s and '"h.secim": "Choose a record"' in s
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "**Köşeler ve oklar (20 Ekim 2026).**" in kilavuz
