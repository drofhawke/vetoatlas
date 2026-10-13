"""
Tasarım dili (kaynaklar/kimlik/KILAVUZ.md): bütün sayfalar, kartlar ve önizleme aynı paleti kullanır; kırmızı
(--vurgu) yalnızca ret oyu ve veto için; metin karşıtlığı WCAG eşiklerini karşılar; logo ve ikon dosyaları yerinde.
"""
import json
import re

from conftest import KOK

WEB = KOK / "web"
SAYFALAR = ["hikaye.html", "vetolar.html", "vizyon.html", "reform.html", "simulasyon.html", "temsil.html", "hakkinda.html", "metodoloji.html"]
ACIK = {"zemin": "#FBF8F1", "yuzey": "#FFFFFF", "murekkep": "#13213A", "murekkep-2": "#5A6578", "cizgi": "#E1DBCF", "vurgu": "#A4262C"}
KOYU = {"zemin": "#1C1A17", "yuzey": "#272420", "murekkep": "#EDE8E0", "murekkep-2": "#ABA496", "cizgi": "#3B3731", "vurgu": "#E05A52"}
UYE = {"sscb": "#7E2F3C", "rus": "#C2666F", "usa": "#24507F", "gbr": "#2F7A6E", "fra": "#A8782A", "chn": "#5E4E9A"}
ESKI = ("#F2F4F6", "#1D2733", "#566273", "#D3D9E0", "#7A2E3A", "#8C3441", "#C9707C", "#2E5B8A", "#3F8676", "#B4862A", "#6B57A6", "#6C8199")


def oran(a, b):
    def lum(h):
        r, g, bl = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
        f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(bl)
    x, y = lum(a), lum(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)


def test_palet_butun_sayfalarda_ayni():
    for ad in SAYFALAR:
        s = (WEB / ad).read_text(encoding="utf-8")
        for k, v in ACIK.items():
            assert f"--{k}: {v}" in s, (ad, k)
        for k, v in KOYU.items():
            assert f"--{k}: {v}" in s, (ad, k, "koyu")
        if ad in ("hikaye.html", "vetolar.html", "vizyon.html", "simulasyon.html"):
            for k, v in UYE.items():
                assert f"--u-{k}: {v}" in s, (ad, k)
        for eski in ESKI:
            assert eski.lower() not in s.lower(), (ad, eski)
    kart = (KOK / "scripts/08_paylasim_kartlari.py").read_text(encoding="utf-8")
    assert all(v in kart for v in UYE.values()) and ACIK["vurgu"] in kart and ACIK["murekkep"] in kart and ACIK["zemin"] in kart
    on = (KOK / "scripts/06_onizleme_gorseli.py").read_text(encoding="utf-8")
    assert "(0xFB, 0xF8, 0xF1)" in on and "(0x7E, 0x2F, 0x3C)" in on


def test_metin_karsitligi():
    for p in (ACIK, KOYU):
        assert oran(p["murekkep"], p["zemin"]) >= 7, p
        assert oran(p["murekkep"], p["yuzey"]) >= 7, p
        assert oran(p["murekkep-2"], p["zemin"]) >= 4.5, p
        assert oran(p["murekkep-2"], p["yuzey"]) >= 4.5, p
        assert oran(p["vurgu"], p["zemin"]) >= 4.5, p
        assert oran(p["zemin"], p["murekkep"]) >= 4.5, p  # mürekkep zeminli düğmede açık metin
    for v in UYE.values():
        assert oran(v, ACIK["zemin"]) >= 3, v  # grafik öğeler


def test_kirmizi_yalnizca_ret_ve_veto():
    v = (WEB / "vetolar.html").read_text(encoding="utf-8")
    assert ".serit .hitap-cizgi { stroke: var(--murekkep-2);" in v and ".etiket.dogrulaniyor { border-color: var(--murekkep-2); color: var(--murekkep-2); }" in v
    assert "border-top: 8px solid var(--murekkep)" in v  # hitap lejant üçgeni
    t = (WEB / "temsil.html").read_text(encoding="utf-8")
    assert "--g-secilmis: #5A6578" in t
    cubuk = (WEB / "cubuk.js").read_text(encoding="utf-8")
    assert "border-bottom-color: var(--murekkep)" in cubuk and "--vurgu" not in cubuk  # etkin sayfa çizgisi mürekkep
    for ad in SAYFALAR:
        s = (WEB / ad).read_text(encoding="utf-8")
        assert "outline: 2px solid var(--vurgu)" not in s, ad
    s = (WEB / "simulasyon.html").read_text(encoding="utf-8")
    assert ".etiket.kaynakli { border-color: var(--murekkep-2);" in s and "--lehte: #9AA3B2" in s and "--aleyhte: #13213A" in s
    h = (WEB / "hikaye.html").read_text(encoding="utf-8")
    # Hikâye (taslaktaki stil): daimî koltuk mürekkep, içinde küçük kırmızı kare (veto yetkisi); ret noktası kırmızı
    assert ".koltuk.daimi { background: var(--murekkep); }" in h and ".koltuk.daimi::after {" in h and "background: var(--vurgu); }  /* veto yetkisi" in h
    assert ".nokta.ret { background: var(--vurgu); }" in h and h.count("var(--vurgu)") == 2  # yalnızca koltuk karesi ve ret noktası
    assert ".cubuklar .cb span.koltuk-payi { background: var(--murekkep); }" in h and ".koltuk.gorusuldu { background: var(--murekkep); }" in h


def test_logo_ikon_ve_bildirim():
    for ad in ("favicon.ico", "favicon.svg", "apple-touch-icon.png", "ikon-192.png", "ikon-512.png", "isaret-kucuk.svg", "isaret.svg",
               "logo-yatay-a.svg", "logo-yatay-a-koyu.svg", "site.webmanifest"):
        assert (WEB / ad).exists(), ad
    # ADIM 47: sekme ve uygulama simgeleri kâğıt zeminli set (kaynaklar/kimlik/favicon/, favicon-kagit; KULLANIM.md orada), baytı
    # baytına; eski zeminsiz simgeler kaldırıldı. Çubuktaki işaret (isaret-kucuk.svg) ve kartlarla önizlemedeki işaret (isaret.svg) kalır.
    kaynak = KOK / "kaynaklar/kimlik/favicon"
    for ad, kaynak_ad in (("favicon.ico", "favicon-kagit.ico"), ("favicon.svg", "favicon-kagit.svg"), ("apple-touch-icon.png", "favicon-kagit-180.png"),
                          ("ikon-192.png", "favicon-kagit-192.png"), ("ikon-512.png", "favicon-kagit-512.png")):
        assert (WEB / ad).read_bytes() == (kaynak / kaynak_ad).read_bytes(), ad
    for eski in ("isaret-180.png", "isaret-192.png", "isaret-512.png", "ikon-maskable-192.png", "ikon-maskable-512.png"):
        assert not (WEB / eski).exists(), eski
    m = json.loads((WEB / "site.webmanifest").read_text(encoding="utf-8"))
    assert [(i["src"], i["sizes"], i.get("purpose", "any")) for i in m["icons"]] == [
        ("ikon-192.png", "192x192", "any"), ("ikon-512.png", "512x512", "any"), ("ikon-192.png", "192x192", "maskable"), ("ikon-512.png", "512x512", "maskable")]
    assert m["theme_color"] == "#FBF8F1"
    simge = ('<link rel="icon" href="favicon.ico" sizes="any">', '<link rel="icon" href="favicon.svg" type="image/svg+xml">',
             '<link rel="apple-touch-icon" href="apple-touch-icon.png">', '<link rel="manifest" href="site.webmanifest">', '<meta name="theme-color" content="#FBF8F1">')
    for ad in SAYFALAR:
        s = (WEB / ad).read_text(encoding="utf-8")
        for satir in simge + ('<script src="cubuk.js"></script>', '<header id="cubuk" class="cubuk"></header>'):
            assert satir in s, (ad, satir)
        assert "<h1" in s  # başlık h1 olarak kalır
    giris = (WEB / "index.html").read_text(encoding="utf-8")
    assert all(satir in giris for satir in simge)
    # Çubukta slogansız logo (logo-cubuk-b, 52 px; çubuk 76 px); 520 px altında işaret 40 px; koyu kâğıtta koyu sürümler
    cubuk = (WEB / "cubuk.js").read_text(encoding="utf-8")
    for ad in ("logo-cubuk-b.svg", "logo-cubuk-b-koyu.svg", "isaret-kucuk.svg", "isaret-kucuk-koyu.svg"):
        assert f'"{ad}"' in cubuk and (WEB / ad).exists(), ad
    for ad in ("logo-cubuk-b.svg", "logo-cubuk-b-koyu.svg"):
        assert (WEB / ad).read_bytes() == (KOK / "kaynaklar/kimlik" / ad).read_bytes(), ad
    assert '".cubuk .c-logo img { height: 52px; width: auto; display: block; }"' in cubuk and "min-height: 76px; }" in cubuk
    assert '"  .cubuk .c-logo img { height: 40px; }"' in cubuk and ".c-cubuklu { scroll-padding-top: 84px; }" in cubuk
    assert "logo-yatay-a" not in cubuk
    # Sayfaların içinde logo yok (ADIM 42: Hakkında'daki sloganlı tam logo kaldırıldı; üst çubuktaki logo yeterli).
    # ADIM 45: slogan sayfaların alt bilgisinde tekrarlanmaz (çubuk betiği alt bilgi eklemez); atlasın çıkış noktası
    # hikâyenin giriş alıntısında ve Hakkında'nın girişinde
    for ad in SAYFALAR:
        s = (WEB / ad).read_text(encoding="utf-8")
        assert "logo-yatay-a" not in s and "c-slogan" not in s, ad
    assert "tam-logo" not in (WEB / "hakkinda.html").read_text(encoding="utf-8")
    assert "slogan" not in cubuk.replace("slogansız", "").replace("sloganlı", "") and ".c-alt" not in cubuk
    assert "“Dünya 5’ten büyüktür” çağrısından hareketle hazırlanmıştır." in (WEB / "hakkinda.html").read_text(encoding="utf-8")
    assert "starting point President Recep Tayyip Erdoğan’s call\n    that “the world is bigger than five”." in (WEB / "hakkinda.html").read_text(encoding="utf-8")
    assert 'EPIGRAF = { tr: ["2019-1", "“Dünya 5’ten Büyüktür.”"]' in (WEB / "hikaye.html").read_text(encoding="utf-8")
    kart = (WEB / "kartlar/kart-01-vetosuz-tr-1200x630.html").read_text(encoding="utf-8")
    assert 'viewBox="0 0 128 128"' in kart and 'fill="#B3272D"' in kart  # köşede işaret
    tek = (WEB / "veto-atlasi-tek-dosya.html").read_text(encoding="utf-8")
    assert "data:image/x-icon;base64," in tek and "data:image/svg+xml;base64," in tek and "__VARLIK__" in tek
    import base64
    for ad, tur in (("favicon.ico", "image/x-icon"), ("favicon.svg", "image/svg+xml"), ("apple-touch-icon.png", "image/png")):
        assert f"data:{tur};base64," + base64.b64encode((WEB / ad).read_bytes()).decode() in tek, ad  # tek dosyada aynı simge
    assert "logo-yatay-a" not in tek  # kullanılmayan logo gömülmez
    assert (KOK / "kaynaklar/kimlik/KILAVUZ.md").exists()


def test_karsilastirmali_iddia_yok():
    yasak = re.compile(r"\b(ilk atlas|tek kaynak|ilk parça|first atlas|the only (source|atlas)|the first (part|platform))\b", re.I)
    for ad in SAYFALAR:
        assert not yasak.search((WEB / ad).read_text(encoding="utf-8")), ad
    for md in ("METODOLOJI.md", "METODOLOJI_EN.md", "README.md"):
        assert not yasak.search((KOK / md).read_text(encoding="utf-8")), md


def test_varsayilan_tema_kagit():
    """Site işletim sisteminin tercihinden bağımsız olarak kâğıt (açık) temada açılır; koyu kâğıt yalnızca çubuktaki düğmeyle."""
    tek = (KOK / "veto_atlasi/tek_dosya.py").read_text(encoding="utf-8")
    metodoloji = (KOK / "veto_atlasi/metodoloji.py").read_text(encoding="utf-8")
    for ad, s in [*((ad, (WEB / ad).read_text(encoding="utf-8")) for ad in SAYFALAR), ("tek_dosya.py", tek), ("metodoloji.py", metodoloji)]:
        assert "prefers-color-scheme" not in s and ':root:not([data-theme="light"])' not in s, ad
        assert ':root[data-theme="dark"]' in s, ad  # koyu kâğıt yalnızca açık seçimle
        kok = s[s.index(":root {"):]
        assert "--zemin: #FBF8F1" in kok[:kok.index("}")], ad  # varsayılan değişkenler kâğıt
    cubuk = (WEB / "cubuk.js").read_text(encoding="utf-8")
    # data-theme="dark" yalnızca kayıtlı seçim "koyu" ise (ya da tek dosyada üst belgeden) konur; depolama erişimi try/catch içinde
    assert 'try { return window.localStorage.getItem(ANAHTAR) === "koyu" ? "koyu" : "kagit"; } catch (e) { return "kagit"; }' in cubuk
    assert 'try { window.localStorage.setItem(ANAHTAR, v); } catch (e)' in cubuk
    assert 'if (v === "koyu") KOK.setAttribute("data-theme", "dark"); else KOK.removeAttribute("data-theme");' in cubuk
    assert cubuk.count('setAttribute("data-theme"') == 1 and "matchMedia" not in cubuk
    assert 'class="c-tema" aria-pressed=' in cubuk


def test_ortak_ust_cubuk():
    cubuk = (WEB / "cubuk.js").read_text(encoding="utf-8")
    sira = ["Hikâye", "Vetolar", "Söz ve Kayıt", "Reform modelleri", "Ya veto olmasaydı?", "Kim temsil ediliyor?", "Nasıl yaptık?"]
    konum = [cubuk.index(f'"{a}"') for a in sira]
    assert konum == sorted(konum)
    assert '["reform", "Reform modelleri", "Reform models"],' in cubuk
    # Yedi bağlantı iki dilde 1180 px'lik çubuğa tek satırda sığsın: bağlantı arası 12 px (tarayıcıda ölçüldü)
    assert '".cubuk .c-sayfalar ul { list-style: none; margin: 0; padding: 0; display: flex; gap: 12px; }",' in cubuk
    assert 'SAYFA_GRUBU = { metodoloji: "hakkinda", index: "hikaye" }' in cubuk
    # Bağlantılar sığmadığında menü (ölçülerek); taslaktaki gibi yapışkan çubuk
    assert "var tasiyor = function () { return ic.scrollWidth > ic.clientWidth + 1; };" in cubuk and 'class="c-menu" aria-expanded="false"' in cubuk
    # Sığmazsa önce inceleme notu (tek dosya) gizlenir, yine sığmazsa menü kipi
    assert 'if (tasiyor() && c.querySelector(".c-not")) { c.classList.add("c-notsuz"); }' in cubuk and '".cubuk.c-notsuz .c-not { display: none; }",' in cubuk
    assert ".cubuk { display: block; position: sticky; top: 0;" in cubuk
    assert '"İnceleme sürümü"' in cubuk  # tek dosya notu kısa
    for ad in SAYFALAR:
        s = (WEB / ad).read_text(encoding="utf-8")
        # Eski gezinme satırları ve sayfa içi dil seçicileri yok
        for eski in ("dil-secici", 'class="ust-cubuk"', '<nav class="ust"', 'id="geri"', "← Atlasa dön", 'id="logo"'):
            assert eski not in s, (ad, eski)
        assert s.count('<script src="cubuk.js"></script>') == 1 and s.index('<script src="cubuk.js"></script>') < s.index("<style>"), ad
    tek = (WEB / "veto-atlasi-tek-dosya.html").read_text(encoding="utf-8")
    assert 'id="sekmeler"' not in tek and '<header id="cubuk" class="cubuk"></header>' in tek and "window.__CUBUK_GIZLI = true;" in tek


def test_yesil_yalnizca_kabul_edilirdi():
    """ADIM 51: yeşil (--kabul) yalnızca simülasyon sonucundaki "Kabul edilirdi" için (sonuç kartı ve şerit); karşıtlık
    metin eşiğinin (4,5:1) üstünde. Kırmızı kuralı değişmez; şerit kâğıt zeminde (koyu temada kırmızı 4,76:1)."""
    kabul = {"acik": "#2D6A4F", "koyu": "#6FBF8E"}
    for zemin in (ACIK["zemin"], ACIK["yuzey"]):
        assert oran(kabul["acik"], zemin) >= 4.5, zemin
    for zemin in (KOYU["zemin"], KOYU["yuzey"]):
        assert oran(kabul["koyu"], zemin) >= 4.5, zemin
    assert oran(KOYU["vurgu"], KOYU["zemin"]) >= 4.5 > oran(KOYU["vurgu"], KOYU["yuzey"])  # şeridin zemini neden kâğıt
    s = (WEB / "simulasyon.html").read_text(encoding="utf-8")
    assert f"--kabul: {kabul['acik']};" in s and f"--kabul: {kabul['koyu']};" in s
    kullanim = sorted(x.strip() for x in re.findall(r"([^{}\n]*)\{[^{}]*var\(--kabul\)[^{}]*\}", s))
    assert kullanim == [".serit .kabul", ".sonuc.kabul"], kullanim
    for ad in SAYFALAR:
        if ad != "simulasyon.html":
            t = (WEB / ad).read_text(encoding="utf-8")
            assert "--kabul" not in t and kabul["acik"].lower() not in t.lower() and kabul["koyu"].lower() not in t.lower(), ad
    for yol in (WEB / "temel.css", WEB / "cubuk.js", KOK / "scripts/08_paylasim_kartlari.py", KOK / "scripts/06_onizleme_gorseli.py"):
        assert kabul["acik"].lower() not in yol.read_text(encoding="utf-8").lower(), yol.name
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "**Yeşil kuralı.**" in kilavuz and "6,03:1" in kilavuz and "7,87:1" in kilavuz and "| `--kabul` | `#2D6A4F` | `#6FBF8E` |" in kilavuz
