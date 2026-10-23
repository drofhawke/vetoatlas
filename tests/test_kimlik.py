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
    assert ".serit .hitap-cizgi { stroke: var(--murekkep-2);" in v and ".etiket { font: 500 var(--yz-kucuk)/var(--sa-kucuk) var(--sans); color: var(--murekkep-2);" in v  # etiketler çerçevesiz, gri
    assert "border-top: 8px solid var(--murekkep)" in v  # hitap lejant üçgeni
    t = (WEB / "temsil.html").read_text(encoding="utf-8")
    assert "--g-secilmis: #5A6578" in t
    cubuk = (WEB / "cubuk.js").read_text(encoding="utf-8")
    assert "border-bottom-color: var(--murekkep)" in cubuk and "--vurgu" not in cubuk  # etkin sayfa çizgisi mürekkep
    for ad in SAYFALAR:
        s = (WEB / ad).read_text(encoding="utf-8")
        assert "outline: 2px solid var(--vurgu)" not in s, ad
    s = (WEB / "simulasyon.html").read_text(encoding="utf-8")
    assert ".etiket { display: inline-block; font-size: var(--yz-kucuk); color: var(--murekkep-2);" in s and "--lehte: #9AA3B2" in s and "--aleyhte: #13213A" in s
    h = (WEB / "hikaye.html").read_text(encoding="utf-8")
    # Hikâye (taslaktaki stil): daimî koltuk mürekkep, içinde küçük kırmızı kare (veto yetkisi); 4. adımda ret noktası dolu
    # kırmızı (21 Ekim 2026'da yayındaki hâl). Renk tek başına kalmaz: noktaların yanındaki sonuç satırı oyları yazıyla söyler
    assert ".koltuk.daimi { background: var(--murekkep); }" in h and ".koltuk.daimi::after {" in h and "background: var(--vurgu); }  /* veto yetkisi" in h
    assert ".nokta.ret { background: var(--vurgu); }" in h
    assert '<span class="sonuc" aria-hidden="true">${esc(t("4.sonuc"))}</span>' in h and 'role="img" aria-label="${esc(t("4.sonuc"))}"' in h
    assert h.count("var(--vurgu)") == 2  # yalnızca koltuk karesi ve ret noktası
    assert ".cubuklar .cb span.koltuk-payi { background: var(--murekkep); }" in h and ".koltuk.gorusuldu { background: var(--murekkep); }" in h


def test_logo_ikon_ve_bildirim():
    # Logo paketi v3 (13 Ekim 2026; KILAVUZ bölüm 3). Kaynak kaynaklar/kimlik/paket/ (paketin kendisi; PNG, baskı dosyaları ve
    # pano hariç): sitedeki logo ve işaret dosyaları paket/svg/'dekilerle, sekme ve uygulama simgeleri (lacivert zeminli set)
    # paket/web/'dekilerle baytı baytına aynı.
    PAKET = KOK / "kaynaklar/kimlik/paket"
    SIMGE = ("favicon.ico", "favicon.svg", "apple-touch-icon.png", "icon-192.png", "icon-512.png", "icon-maskable-192.png",
             "icon-maskable-512.png", "site.webmanifest")
    LOGO = ("isaret.svg", "isaret-koyu.svg", "isaret-kucuk.svg", "isaret-kucuk-koyu.svg", "logo-cubuk-b.svg", "logo-cubuk-b-koyu.svg",
            "logo-yatay-a.svg", "logo-yatay-a-koyu.svg")
    for ad in SIMGE:
        assert (WEB / ad).read_bytes() == (PAKET / "web" / ad).read_bytes(), ad
    for ad in LOGO:
        assert (WEB / ad).read_bytes() == (PAKET / "svg" / ad).read_bytes(), ad
    # Eski simgeler, başlık satırları örneği ve paketin paylaşım görseli sitede yok: paylaşım görseli onizleme.png (13 Ekim kararı);
    # örnek (kökten yollu) ve og-image.png pakette
    for eski in ("isaret-180.png", "isaret-192.png", "isaret-512.png", "ikon-maskable-192.png", "ikon-maskable-512.png", "ikon-192.png",
                 "ikon-512.png", "head-etiketleri.html", "og-image.png"):
        assert not (WEB / eski).exists(), eski
    assert (PAKET / "web/head-etiketleri.html").exists() and (PAKET / "web/og-image.png").exists()
    # Kimlik klasöründe eski paketin dosyaları yok; pakette PDF yok (depoya PDF girmez), kullanım notu ve üretim betiği var
    kimlik = KOK / "kaynaklar/kimlik"
    for eski in ("png", "favicon", "KULLANIM.md", "pano.png", "ikon-maskable.svg", "favicon.ico", "isaret.svg", "logo-cubuk-b.svg"):
        assert not (kimlik / eski).exists(), eski
    assert not list(PAKET.rglob("*.pdf")) and (PAKET / "KULLANIM.md").exists() and (PAKET / "kaynak/uret.py").exists()
    m = json.loads((WEB / "site.webmanifest").read_text(encoding="utf-8"))
    assert [(i["src"], i["sizes"], i.get("purpose", "any")) for i in m["icons"]] == [
        ("/icon-192.png", "192x192", "any"), ("/icon-512.png", "512x512", "any"), ("/icon-maskable-192.png", "192x192", "maskable"),
        ("/icon-maskable-512.png", "512x512", "maskable")]
    assert m["theme_color"] == "#FBF8F1" and all((WEB / i["src"].lstrip("/")).exists() for i in m["icons"])
    # Başlık satırları göreli yolla (sitedeki öteki bağlantılar gibi); ICO yalnızca 32x32 yedek (sizes="any" Chrome'a pikselli ICO'yu
    # seçtiriyordu); ?v=2 eski simgelerin tarayıcı önbelleğinden düşmesi için
    simge = ('<link rel="icon" href="favicon.ico?v=2" sizes="32x32">', '<link rel="icon" href="favicon.svg?v=2" type="image/svg+xml">',
             '<link rel="apple-touch-icon" href="apple-touch-icon.png?v=2">', '<link rel="manifest" href="site.webmanifest">', '<meta name="theme-color" content="#FBF8F1">')
    for ad in SAYFALAR:
        s = (WEB / ad).read_text(encoding="utf-8")
        for satir in simge + ('<script src="cubuk.js"></script>', '<header id="cubuk" class="cubuk"></header>'):
            assert satir in s, (ad, satir)
        assert "<h1" in s  # başlık h1 olarak kalır
    giris = (WEB / "index.html").read_text(encoding="utf-8")
    assert all(satir in giris for satir in simge)
    bulunamadi = (WEB / "404.html").read_text(encoding="utf-8")
    assert all(satir in bulunamadi for satir in simge[:3] + simge[4:]) and '<base href="/">' in bulunamadi
    # Çubukta işaret (isaret.svg, 40 px) + canlı logo yazısı "Veto Atlası" (20 Ekim; KILAVUZ bölüm 3): yazı logo-cubuk-b.svg'nin
    # ölçülerinde (27,3 px, 14 px aralık) ve aynı kesimle (Veto Atlası Logo: Source Serif 4 Semibold, optik boy 20) canlı metindir;
    # %100 ölçekte SVG dış çizgisi gri tonlu yumuşatmayla bulanık çiziliyordu, canlı metin hinting ve ClearType alır. logo-cubuk-b.svg
    # sitede kullanılmaz, kimlik dosyası olarak web/ altında durur. 520 px ve altında işaret 34 px, yazı aynı oranla 23,2 px (380 px
    # altında 20,8 px, 340 px altında yalnızca işaret; 21 Ekim 2026, kullanıcı kararı); koyu kâğıtta koyu işaret, yazı rengi --murekkep.
    # Yazının sınıfı c-yazi: reklam engelleyicilerin ortak listesi EasyList "##.c-ad" kuralıyla eski sınıfı gizliyordu (21 Ekim 2026)
    cubuk = (WEB / "cubuk.js").read_text(encoding="utf-8")
    for ad in ("isaret.svg", "isaret-koyu.svg"):
        assert f'"{ad}"' in cubuk and (WEB / ad).exists(), ad
    assert "isaret-kucuk" not in cubuk and '"logo-cubuk-b' not in cubuk and "logo-yatay-a" not in cubuk  # dosya olarak anılmaz (yorumda ölçü kaynağı)
    assert 'gorsel("c-isaret", "isaret.svg", 37, 40, "")' in cubuk and 'gorsel("c-isaret-koyu", "isaret-koyu.svg", 37, 40, "")' in cubuk
    assert 'yazi.className = "c-yazi"; yazi.textContent = "Veto Atlası";' in cubuk
    assert '".cubuk .c-logo .c-yazi { font-family: \\"Veto Atlası Logo\\", var(--serif); font-weight: 600; font-size: 27.3px; line-height: 40px; letter-spacing: .2px; white-space: nowrap; margin-left: 14px; position: relative; top: 1px; }"' in cubuk
    assert '".cubuk .c-logo img { height: 40px; width: auto; display: block; }"' in cubuk and "min-height: 76px; }" in cubuk
    assert '"  .cubuk .c-logo img { height: 34px; }"' in cubuk
    assert '"  .cubuk .c-logo .c-yazi { font-size: 23.2px; line-height: 34px; letter-spacing: .17px; margin-left: 12px; }"' in cubuk
    assert '"  .cubuk .c-logo .c-yazi { font-size: 20.8px; letter-spacing: .15px; }"' in cubuk and '"  .cubuk .c-logo .c-yazi { display: none; }"' in cubuk
    assert '"  .cubuk .c-tema .c-tema-metin { display: none; }"' in cubuk and '<span class="c-tema-metin">' in cubuk
    assert ".c-cubuklu { scroll-padding-top: 84px; }" in cubuk
    fonts_css = (WEB / "fonts/fonts.css").read_text(encoding="utf-8")
    assert "font-family: 'Veto Atlası Logo';" in fonts_css and "font-display: block;" in fonts_css and (WEB / "fonts/veto-atlasi-logo.woff2").exists()
    # Sayfaların içinde logo yok (ADIM 42: Hakkında'daki sloganlı tam logo kaldırıldı; üst çubuktaki logo yeterli).
    # ADIM 45: slogan sayfaların alt bilgisinde tekrarlanmaz (çubuk betiği alt bilgi eklemez); atlasın çıkış noktası
    # hikâyenin giriş alıntısında ve Hakkında'nın girişinde
    for ad in SAYFALAR:
        s = (WEB / ad).read_text(encoding="utf-8")
        assert "logo-yatay-a" not in s and "c-slogan" not in s, ad
    assert "tam-logo" not in (WEB / "hakkinda.html").read_text(encoding="utf-8")
    assert "slogan" not in cubuk.replace("slogansız", "").replace("sloganlı", "") and ".c-alt" not in cubuk
    h = (WEB / "hakkinda.html").read_text(encoding="utf-8")
    # Slogan giriş paragrafında 2019 Genel Kurul sözü olarak (TR "Büyüktür" büyük harfle, EN ünlemle); paragraf resmî rapor
    # dilinde ve üçüncü kişiyle (kullanıcı kararı, 22 Ekim 2026)
    duz = " ".join(h.split())
    assert "Çalışmanın çıkış noktası, Cumhurbaşkanı Recep Tayyip Erdoğan’ın 2019’da BM Genel Kurulunda dile getirdiği “Dünya 5’ten Büyüktür” sözüdür." in duz
    assert ("The starting point of the work is a statement made by President Recep Tayyip Erdoğan in his address to the UN General Assembly in 2019: "
            "“The world is bigger than five!”") in duz
    assert 'EPIGRAF = { tr: ["2019-1", "“Dünya 5’ten Büyüktür.”"]' in (WEB / "hikaye.html").read_text(encoding="utf-8")
    # Köşede işaret: eski dosyadaki gibi 44 × 44 px kutu, çizim ortalanmış 34 px yükseklikte (eski kutudaki halkayla aynı görünür
    # boyut; alt bilgi satırı değişmez: 13 Ekim'de 44 kartın hepsi canlıdakiyle yalnızca işaretin 32 × 34 px'lik alanında farklı);
    # adın yanında süs (görsel rolü ve başlığı yok)
    kart = (WEB / "kartlar/kart-01-vetosuz-tr-1200x630.html").read_text(encoding="utf-8")
    assert 'viewBox="-23.75 -18.82 165.65 165.65" width="44" height="44" aria-hidden="true">' in kart and 'fill="#A4262C"' in kart
    tek = (WEB / "veto-atlasi-tek-dosya.html").read_text(encoding="utf-8")
    assert "data:image/x-icon;base64," in tek and "data:image/svg+xml;base64," in tek and "__VARLIK__" in tek
    import base64
    for ad, tur in (("favicon.ico", "image/x-icon"), ("favicon.svg", "image/svg+xml"), ("apple-touch-icon.png", "image/png")):
        veri = (WEB / ad).read_bytes()
        if ad.endswith(".svg"):
            veri = veri.replace(b"\r\n", b"\n")  # SVG'de satır sonu git'teki gibi LF (CRLF'li Windows çalışma ağacı)
        assert f"data:{tur};base64," + base64.b64encode(veri).decode() in tek, ad  # tek dosyada aynı simge
    assert "logo-yatay-a" not in tek and "isaret-kucuk" not in tek and '"logo-cubuk-b' not in tek  # kullanılmayan logo ve işaret gömülmez
    assert (KOK / "kaynaklar/kimlik/KILAVUZ.md").exists()


def test_reklam_engelleyiciye_takilan_sinif_yok():
    """21 Ekim 2026: çubuktaki logo yazısının sınıfı "c-ad" idi; reklam engelleyicilerin ortak listesi EasyList bunu genel kuralla
    ("##.c-ad") gizlediği için engelleyicili tarayıcılarda logo yazısı görünmüyordu. Sınıf ve kimlik adlarında "ad", "ads", "advert",
    "banner", "sponsor" gibi sözcüklerle başlamaz (listelerin genel kuralları bunları yakalar; "konu-ad" gibi Türkçe sonekler ve
    "adim" gibi sözcükler serbest). Simülasyonun "ad" sınıfı da aynı gün "sistem-adi" ve "kayit-baslik" oldu. Tam denetim: EasyList,
    AdGuard Temel, AdGuard Türkçe ve uBlock listelerinin 14.150 genel kuralı tarayıcıda sayfalara uygulandı, eşleşme 0."""
    yasak = re.compile(r"^(?:c-)?(?:ad|ads|advert|advertisement|banner|sponsor|sponsored|promo)(?:$|[-_])")
    adlar = set()
    for ad in [p.name for p in WEB.glob("*.html") if p.name != "veto-atlasi-tek-dosya.html"] + ["cubuk.js", "metin.js", "suzgec.js"]:
        s = (WEB / ad).read_text(encoding="utf-8")
        # Öznitelik değerleri ve sınıf atamaları (betik içindeki HTML dizgeleri dahil; şablon değişkenli değerler atlanır)
        degerler = re.findall(r'\b(?:class|id)="([^"$]+)"', s) + re.findall(r'className\s*=\s*"([^"]+)"', s)
        degerler += re.findall(r'classList\.(?:add|remove|toggle|contains)\("([^"]+)"', s)
        # CSS seçicileri: sayfalardaki <style> blokları ve çubuğun CSS dizisi (betikteki nesne.özellik erişimleri sayılmaz)
        css = "\n".join(re.findall(r"<style>(.*?)</style>", s, re.S))
        if ad == "cubuk.js":
            css = s[s.index("var CSS = ["):s.index("].join(")]
        for secici in re.findall(r"([^{}]+)\{", css):
            degerler += re.findall(r"[.#]([A-Za-z][\w-]*)", secici)
        for deger in degerler:
            for parca in deger.split():
                adlar.add((ad, parca))
    bulunan = sorted(f"{ad}: {parca}" for ad, parca in adlar if yasak.search(parca))
    assert not bulunan, bulunan


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
    # Sekme sırası (K4): Temsil, Reform'dan önce
    sira = ["Hikâye", "Vetolar", "Söz ve Kayıt", "Kim temsil ediliyor?", "Reform modelleri", "Ya veto olmasaydı?", "Nasıl yaptık?"]
    konum = [cubuk.index(f'"{a}"') for a in sira]
    assert konum == sorted(konum)
    assert '["reform", "Reform modelleri", "Reform models"],' in cubuk
    # Yedi bağlantı iki dilde 1180 px'lik çubuğa tek satırda sığsın: bağlantı arası 12 px (tarayıcıda ölçüldü)
    assert '".cubuk .c-sayfalar ul { list-style: none; margin: 0; padding: 0; display: flex; gap: 12px; }",' in cubuk
    assert 'SAYFA_GRUBU = { metodoloji: "hakkinda", index: "hikaye" }' in cubuk
    # Bağlantılar sığmadığında menü (ölçülerek); taslaktaki gibi yapışkan çubuk. Taşma iki yoldan ölçülür: kabın kaydırma
    # genişliği ve araç grubunun (dil, tema) sağ kenarının çubuk içeriğinin sağ kenarını aşması (İngilizce "Dark", 21 Ekim 2026)
    assert "if (ic.scrollWidth > ic.clientWidth + 1) return true;" in cubuk and 'class="c-menu" aria-expanded="false"' in cubuk
    assert 'var sinir = ic.getBoundingClientRect().right - parseFloat(getComputedStyle(ic).paddingRight);' in cubuk
    assert "return araclar.getBoundingClientRect().right > sinir + 1;" in cubuk
    # Sığmazsa önce inceleme notu (tek dosya) gizlenir, yine sığmazsa menü kipi
    assert 'if (tasiyor() && c.querySelector(".c-not")) { c.classList.add("c-notsuz"); }' in cubuk and '".cubuk.c-notsuz .c-not { display: none; }",' in cubuk
    assert ".cubuk { display: block; position: sticky; top: 0;" in cubuk
    assert 'not: "Çevrimdışı sürüm"' in cubuk and 'not: "Offline version"' in cubuk  # tek dosya notu kısa
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


def png_pikselleri(veri: bytes) -> tuple[int, int, int, list[bytearray]]:
    """Küçük PNG okuyucu (8 bit RGB ya da RGBA, geçmesiz): genişlik, yükseklik, piksel başına bayt, satırlar."""
    import struct
    import zlib
    assert veri[:8] == b"\x89PNG\r\n\x1a\n"
    i, idat = 8, b""
    while i < len(veri):
        n, tur = struct.unpack(">I4s", veri[i:i + 8])
        govde = veri[i + 8:i + 8 + n]
        i += 12 + n
        if tur == b"IHDR":
            gen, yuk, bit, renk, _, _, gecme = struct.unpack(">IIBBBBB", govde)
        elif tur == b"IDAT":
            idat += govde
    assert bit == 8 and renk in (2, 6) and gecme == 0, (bit, renk, gecme)
    bpp = 3 if renk == 2 else 4
    ham, adim = zlib.decompress(idat), gen * bpp
    onceki, satirlar = bytearray(adim), []
    for r in range(yuk):
        f, s = ham[r * (adim + 1)], bytearray(ham[r * (adim + 1) + 1:(r + 1) * (adim + 1)])
        for x in range(adim):
            a = s[x - bpp] if x >= bpp else 0
            b, c = onceki[x], (onceki[x - bpp] if x >= bpp else 0)
            if f == 1:
                s[x] = (s[x] + a) & 255
            elif f == 2:
                s[x] = (s[x] + b) & 255
            elif f == 3:
                s[x] = (s[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                s[x] = (s[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        satirlar.append(s)
        onceki = s
    return gen, yuk, bpp, satirlar


def test_ana_ekran_ikonu_ve_manifest():
    """Logo paketi v3: Android (Samsung dahil) maskable görselin yalnızca ortadaki üçte ikisini (72/108) gösterip kırpar. Maskable
    ikonlar ayrı çizilir; işaret merkezden en çok 1/3 genişlik uzakta kalır. Aynı görsel hem normal hem maskable olarak kullanılmaz
    (eski sitede ikon-512.png öyleydi; halkanın kenarı ve kırmızı kare kesiliyordu). Ana ekrandan açılınca hikâye."""
    m = json.loads((WEB / "site.webmanifest").read_text(encoding="utf-8"))
    assert m["id"] == "/hikaye" and m["start_url"] == "/hikaye" and (WEB / "hikaye.html").exists()
    normal = {i["src"] for i in m["icons"] if i.get("purpose", "any") == "any"}
    maskable = {i["src"] for i in m["icons"] if i.get("purpose") == "maskable"}
    assert normal and maskable and not normal & maskable
    for n in normal:
        for k in maskable:
            assert (WEB / n.lstrip("/")).read_bytes() != (WEB / k.lstrip("/")).read_bytes(), (n, k)
    for ad in ("icon-maskable-192.png", "icon-maskable-512.png"):
        gen, yuk, bpp, satirlar = png_pikselleri((WEB / ad).read_bytes())
        assert gen == yuk and bpp == 3, ad  # opak kare (saydamlık yok)
        zemin = satirlar[2][gen // 2 * 3:gen // 2 * 3 + 3]
        assert tuple(zemin) == (0x13, 0x21, 0x3A), ad  # lacivert zemin
        en_uzak = 0.0
        for y, satir in enumerate(satirlar):
            for x in range(gen):
                if sum(abs(satir[3 * x + k] - zemin[k]) for k in range(3)) > 60:
                    en_uzak = max(en_uzak, ((x + 0.5 - gen / 2) ** 2 + (y + 0.5 - yuk / 2) ** 2) ** 0.5 / gen)
        assert 0.25 < en_uzak <= 1 / 3, (ad, en_uzak)  # 13 Ekim ölçümü: 0,3145 (512) ve 0,3149 (192)

