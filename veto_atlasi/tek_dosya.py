"""
Tek dosyalık inceleme sürümü: web/ altındaki sekiz sayfa (hikâye, atlas, Söz ve Kayıt, reform modelleri,
simülasyon, temsil endeksi, hakkında, metodoloji) yedi sekmede tek bir HTML dosyasında (web/veto-atlasi-tek-dosya.html);
hakkında ve metodoloji "Nasıl yaptık?" sekmesinde alt alta.

Yapı: üstte sitenin ortak çubuğu (web/cubuk.js; sekme geçişi, TR/EN ve tema oradan); her sayfa kendi
`<iframe srcdoc>` içinde çalışır (sayfaların kimlikleri ve betikleri birbirine karışmaz), sayfa çerçevelerinde çubuk çizilmez. Veri (veri.js, temsil_veri.js) ana belgeye bir kez gömülür, sayfalar `parent` üzerinden
okur. Yazı tipleri (woff2) base64 olarak bir kez gömülür; sayfa şablonlarındaki data: adreslerine açılışta yerleştirilir.
Sayfalar arası bağlantılar sekme geçişine dönüşür; üst çubuktaki TR/EN ve tema seçimi bütün sekmelere uygulanır. Metin sayfalarının "Bu sayfada" dizini (web/metin.js) gömülür; alt alta dizilen sekmede kaydırma konumu çerçevelere bildirilir, dizin bağımsız sayfadaki gibi yerinde durur. Dış istek yoktur. Önizleme görseli ve paylaşım kartları dosyada yer almaz (web/kartlar/).
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
from pathlib import Path

SAYFALAR = [  # dosya, sekme adı (tr, en); hakkinda ve metodoloji son sekmede alt alta
    ("hikaye.html", "Hikâye", "Story"),
    ("vetolar.html", "Vetolar", "Vetoes"),
    ("vizyon.html", "Söz ve Kayıt", "Word and Record"),
    ("reform.html", "Reform modelleri", "Reform models"),
    ("simulasyon.html", "Ya veto olmasaydı?", "What if there were no veto?"),
    ("temsil.html", "Kim temsil ediliyor?", "Who is represented?"),
    ("hakkinda.html", "Nasıl yaptık?", "How we did it"),
    ("metodoloji.html", "Nasıl yaptık?", "How we did it"),
]
SEKMELER = [  # sekme kodu, (tr, en), içerdiği sayfalar
    ("hikaye", ("Hikâye", "Story"), ["hikaye"]),
    ("vetolar", ("Vetolar", "Vetoes"), ["vetolar"]),
    ("vizyon", ("Söz ve Kayıt", "Word and Record"), ["vizyon"]),
    ("reform", ("Reform modelleri", "Reform models"), ["reform"]),
    ("simulasyon", ("Ya veto olmasaydı?", "What if there were no veto?"), ["simulasyon"]),
    ("temsil", ("Kim temsil ediliyor?", "Who is represented?"), ["temsil"]),
    ("nasil", ("Nasıl yaptık?", "How we did it"), ["hakkinda", "metodoloji"]),
]
SAYFA_SEKME = {s: kod for kod, _, sayfalar in SEKMELER for s in sayfalar}
CIKTI = "veto-atlasi-tek-dosya.html"

# Her sayfanın sonuna eklenen köprü betiği: bağlantı tıklamalarını üst belgeye iletir, üst belgeden gelen
# bölüm (hash) isteğini uygular.
KOPRU = r"""
<script>
(() => {
  const SAYFA = /^(index|hikaye|vetolar|vizyon|reform|simulasyon|temsil|hakkinda|metodoloji)\.html(\?[^#]*)?(#.*)?$/;
  document.addEventListener("click", (e) => {
    const a = e.target.closest("a[href]");
    if (!a) return;
    const href = a.getAttribute("href") || "";
    // Sayfa içi bağlantı (#bölüm; içindekiler): srcdoc çerçevesi üst belgenin adresine gitmesin, kaydırma burada yapılır
    if (href.length > 1 && href[0] === "#") { e.preventDefault(); git(href); return; }
    const m = href.match(SAYFA);
    if (m) {
      e.preventDefault();
      parent.postMessage({ tur: "sayfa", sayfa: m[1], hash: m[3] || "" }, "*");
    }
  });
  const git = (hash) => {
    if (!hash || hash === "#") return;
    const hedef = document.getElementById(decodeURIComponent(hash.slice(1)));
    if (!hedef) return;
    const pay = parseFloat(getComputedStyle(hedef).scrollMarginTop) || 0;  // başlığın kaydırma payı, bağımsız sayfadaki gibi
    if (window.__YIGIN) parent.postMessage({ tur: "kaydir", sayfa: window.__SAYFA, y: hedef.getBoundingClientRect().top + scrollY - pay }, "*");
    else hedef.scrollIntoView();
    if (hedef.tabIndex < 0) hedef.tabIndex = -1; hedef.focus({ preventScroll: true });
  };
  addEventListener("message", (e) => { if (e.data && e.data.tur === "hash") git(e.data.hash); });
  if (window.__HASH) addEventListener("load", () => git(window.__HASH));
  // Alt alta dizilen sayfalar (Nasıl yaptık?): yükseklik üst belgeye bildirilir
  if (window.__YIGIN) {
    const bildir = () => parent.postMessage({ tur: "yukseklik", sayfa: window.__SAYFA, h: document.documentElement.scrollHeight }, "*");
    new ResizeObserver(bildir).observe(document.documentElement); addEventListener("load", bildir);
  }
})();
</script>
"""


def sayfa_hazirla(html: str, fonts_css: str, cubuk_js: str, suzgec_js: str = "", temel_css: str = "", metin_js: str = "") -> str:
    """Sayfa şablonu: yazı tipi stili gömülü (url'ler __FONT__ad), veri parent'tan, dil __DIL ve tema __TEMA ile; ortak çubuk gizli."""
    s = html
    s = s.replace('<link rel="stylesheet" href="fonts/fonts.css">', "<style>\n" + fonts_css + "\n</style>")
    assert "fonts/fonts.css" not in s
    # Temel tasarım dili (web/temel.css: ızgara, yazı ölçeği, iki yana yaslama, bölüm ayrımları) gömülür
    assert s.count('<link rel="stylesheet" href="temel.css">') == 1 and temel_css, "temel.css bağlantısı yok"
    s = s.replace('<link rel="stylesheet" href="temel.css">', "<style>\n" + temel_css + "\n</style>")
    # İkon ve bildirim bağlantıları üst belgede; ortak çubuk betiği gömülür (çerçevede çubuk çizmez, temayı uygular)
    s = re.sub(r'<link rel="(icon|apple-touch-icon|manifest)"[^>]*>\n?', "", s)
    s = re.sub(r'<link rel="(canonical|alternate)"[^>]*>\n?', "", s)
    assert s.count('<script src="cubuk.js"></script>') == 1
    s = s.replace('<script src="cubuk.js"></script>', "<script>\n" + cubuk_js + "\n</script>")
    # Simülasyon sayfasının filtre modülü (web/suzgec.js) gömülür
    if '<script src="suzgec.js"></script>' in s:
        assert suzgec_js, "suzgec.js okunmadı"
        s = s.replace('<script src="suzgec.js"></script>', "<script>\n" + suzgec_js + "\n</script>")
    # Metin sayfalarının "Bu sayfada" dizini (web/metin.js) gömülür
    if '<script src="metin.js"></script>' in s:
        assert metin_js, "metin.js okunmadı"
        s = s.replace('<script src="metin.js"></script>', "<script>\n" + metin_js + "\n</script>")
    s = s.replace('<script src="veri.js"></script>', "<script>window.VETO_VERISI = parent.VETO_VERISI;</script>")
    s = s.replace('<script src="temsil_veri.js"></script>', "<script>window.TEMSIL_VERISI = parent.TEMSIL_VERISI;</script>")
    assert '<script src=' not in s and 'href="favicon' not in s, "gömülmemiş kaynak"
    n = s.count('new URLSearchParams(location.search).get("lang")')
    assert n == 1, n
    s = s.replace('new URLSearchParams(location.search).get("lang")', "window.__DIL")
    # Dil ve bölüm bilgisi üst belge tarafından baş etikete yazılır
    s = s.replace("<head>", "<head>\n<script>window.__DIL = \"__DIL__\"; window.__TEMA = \"__TEMA__\"; window.__HASH = \"__HASH__\"; window.__SAYFA = \"__SAYFA__\"; window.__YIGIN = __YIGIN__; window.__CUBUK_GIZLI = true;</script>", 1)
    s = s.replace("</body>", KOPRU + "</body>", 1)
    return s


def fonts_hazirla(web: Path) -> tuple[str, dict[str, str]]:
    css = (web / "fonts/fonts.css").read_text(encoding="utf-8")
    fontlar = {}
    for ad in sorted(set(re.findall(r"url\(([^)]+\.woff2)\)", css))):
        fontlar[ad] = base64.b64encode((web / "fonts" / ad).read_bytes()).decode()
        css = css.replace(f"url({ad})", f"url(data:font/woff2;base64,__FONT__{ad})")
    return css, fontlar


def varliklar_hazirla(web: Path) -> dict[str, str]:
    """Logo, çubuk işareti ve sekme simgeleri (kâğıt zeminli set): dosya adı -> data: adresi (SVG, PNG ve ICO base64)."""
    v = {}
    for ad in ("logo-cubuk-b.svg", "logo-cubuk-b-koyu.svg", "isaret-kucuk.svg", "isaret-kucuk-koyu.svg", "favicon.svg"):
        v[ad] = "data:image/svg+xml;base64," + base64.b64encode((web / ad).read_bytes()).decode()
    v["favicon.ico"] = "data:image/x-icon;base64," + base64.b64encode((web / "favicon.ico").read_bytes()).decode()
    v["apple-touch-icon.png"] = "data:image/png;base64," + base64.b64encode((web / "apple-touch-icon.png").read_bytes()).decode()
    return v


def uret(kok: Path) -> Path:
    web = kok / "web"
    fonts_css, fontlar = fonts_hazirla(web)
    varliklar = varliklar_hazirla(web)
    cubuk_js = (web / "cubuk.js").read_text(encoding="utf-8")
    suzgec_js = (web / "suzgec.js").read_text(encoding="utf-8")
    metin_js = (web / "metin.js").read_text(encoding="utf-8")
    temel_css = (web / "temel.css").read_text(encoding="utf-8")
    assert "</script" not in cubuk_js and "</script" not in suzgec_js and "</script" not in metin_js and "</style" not in temel_css
    sayfalar = {}
    girdi_ozeti = hashlib.sha256()
    girdi_ozeti.update(cubuk_js.encode("utf-8"))
    girdi_ozeti.update(suzgec_js.encode("utf-8"))
    girdi_ozeti.update(metin_js.encode("utf-8"))
    girdi_ozeti.update(temel_css.encode("utf-8"))
    for dosya, _, _ in SAYFALAR:
        ham = (web / dosya).read_text(encoding="utf-8")
        girdi_ozeti.update(ham.encode("utf-8"))
        sayfalar[dosya.split(".")[0]] = sayfa_hazirla(ham, fonts_css, cubuk_js, suzgec_js, temel_css, metin_js)
    veri = (web / "veri.js").read_text(encoding="utf-8")
    temsil = (web / "temsil_veri.js").read_text(encoding="utf-8")
    for ek in (veri, temsil, fonts_css, (web / "fonts/fonts.css").read_text(encoding="utf-8")):
        girdi_ozeti.update(ek.encode("utf-8"))
    for ad in list(fontlar.values()) + list(varliklar.values()):
        girdi_ozeti.update(ad.encode())
    ozet = girdi_ozeti.hexdigest()
    sekmeler = [{"kod": kod, "tr": tr, "en": en, "sayfalar": sayfalar} for kod, (tr, en), sayfalar in SEKMELER]
    # JSON içindeki "</script>" dizilerini betik etiketi kapanmasın diye kaçır
    j = lambda x: json.dumps(x, ensure_ascii=False).replace("</", "<\\/")
    html = f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Veto Atlası · tek dosya / Veto Atlas · single file</title>
<meta name="description" content="Veto Atlası'nın sekiz sayfası yedi sekmede, tek dosyada; inceleme sürümü. / The eight pages of the Veto Atlas in seven tabs, in one file; review version.">
<meta name="veto-atlasi-girdi-sha256" content="{ozet}">
<link rel="icon" href="{varliklar['favicon.ico']}" sizes="any">
<link rel="icon" href="{varliklar['favicon.svg']}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{varliklar['apple-touch-icon.png']}">
<meta name="theme-color" content="#FBF8F1">
<style id="fontlar"></style>
<style id="temel">
{temel_css}
</style>
<script>window.__CUBUK_ELLE = true;</script>
<script>
{cubuk_js}
</script>
<style>
:root {{ --zemin: #FBF8F1; --yuzey: #FFFFFF; --murekkep: #13213A; --murekkep-2: #5A6578; --cizgi: #E1DBCF; --vurgu: #A4262C;
  --serif: "Source Serif 4", Georgia, "Times New Roman", serif; --sans: "Source Sans 3", "Segoe UI", system-ui, -apple-system, sans-serif; }}
:root[data-theme="dark"] {{ --zemin: #1C1A17; --yuzey: #272420; --murekkep: #EDE8E0; --murekkep-2: #ABA496; --cizgi: #3B3731; --vurgu: #E05A52; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; height: 100%; background: var(--zemin); color: var(--murekkep); font-family: var(--sans); }}
body {{ display: flex; flex-direction: column; }}
#cubuk {{ flex: none; }}
#alan {{ flex: 1; position: relative; min-height: 0; }}
#alan > iframe, #alan > .yigin {{ position: absolute; inset: 0; width: 100%; height: 100%; border: 0; background: var(--zemin); }}
#alan > [hidden] {{ display: none; }}
.yigin {{ overflow: auto; }}
.yigin iframe {{ display: block; width: 100%; height: 600px; border: 0; border-bottom: 1px solid var(--cizgi); }}
</style>
</head>
<body>
<header id="cubuk" class="cubuk"></header>
<div id="alan"></div>
<script>{veri}</script>
<script>{temsil}</script>
<script>
(() => {{
  const SEKMELER = {j(sekmeler)};
  const SAYFALAR = {j(sayfalar)};
  const FONTLAR = {j(fontlar)};
  const FONT_CSS = {j(fonts_css)};
  const VARLIKLAR = {j(varliklar)};
  window.__VARLIK = VARLIKLAR;
  const $ = (s) => document.querySelector(s);
  let DIL = "tr", ACIK = "hikaye";
  const cerceveler = {{}};
  const fontGom = (html) => html.replace(/__FONT__([\\w.-]+\\.woff2)/g, (m, ad) => FONTLAR[ad] || m).replace(/__VARLIK__([\\w.-]+)/g, (m, ad) => VARLIKLAR[ad] || m);
  $("#fontlar").textContent = fontGom(FONT_CSS);
  const SAYFA_SEKME = {{}};
  for (const s of SEKMELER) for (const p of s.sayfalar) SAYFA_SEKME[p] = s.kod;
  const cerceve = (sayfa, hash, yigin) => {{
    const f = document.createElement("iframe");
    f.title = sayfa; f.dataset.sayfa = sayfa;
    f.srcdoc = fontGom(SAYFALAR[sayfa]).replace('"__DIL__"', JSON.stringify(DIL)).replace('"__TEMA__"', JSON.stringify(VetoCubuk.tema()))
      .replace('"__HASH__"', JSON.stringify(hash || "")).replace('"__SAYFA__"', JSON.stringify(sayfa)).replace("__YIGIN__", yigin ? "true" : "false");
    return f;
  }};
  // Alt alta dizilen sayfalarda (Nasıl yaptık?) hedefe kaydırma: çerçevelerin yükseklikleri sonradan geldikçe hedef yeniden
  // uygulanır (yoksa ilk açılışta Metodoloji bağlantısı Hakkında'da kalır); okur kaydırınca ya da 3 s sonra bırakılır
  let hedef = null;
  const hedefeKaydir = () => {{
    if (!hedef) return;
    if (Date.now() > hedef.son) {{ hedef = null; return; }}
    const f = hedef.yigin.querySelector(`iframe[data-sayfa="${{hedef.sayfa}}"]`);
    if (f) {{ hedef.yigin.scrollTop = f.offsetTop + hedef.y; hedef.konum = hedef.yigin.scrollTop; }}
  }};
  const hedefKoy = (yigin, sayfa, y) => {{ hedef = {{ yigin, sayfa, y, son: Date.now() + 3000, konum: -1 }}; hedefeKaydir(); }};
  // Alt alta dizilen çerçeveler kendisi kaymaz: kaydırma konumu ve görünen yükseklik çerçevelere bildirilir ("Bu sayfada"
  // dizini yerinde durur ve okunan bölümü vurgular; web/metin.js)
  const gorunumBildir = (yigin) => {{ for (const f of yigin.querySelectorAll("iframe")) if (f.contentWindow) f.contentWindow.postMessage({{ tur: "gorunum", ust: yigin.scrollTop - f.offsetTop, h: yigin.clientHeight }}, "*"); }};
  const bekleyen = new Set();
  const gorunumIste = (yigin) => {{ if (bekleyen.has(yigin)) return; bekleyen.add(yigin); requestAnimationFrame(() => {{ bekleyen.delete(yigin); gorunumBildir(yigin); }}); }};
  addEventListener("resize", () => document.querySelectorAll("#alan > .yigin").forEach(gorunumIste));
  const kur = (kod, sayfa, hash) => {{
    const s = SEKMELER.find((x) => x.kod === kod);
    let el;
    if (s.sayfalar.length === 1) el = cerceve(s.sayfalar[0], hash, false);
    else {{
      el = document.createElement("div"); el.className = "yigin"; for (const p of s.sayfalar) el.appendChild(cerceve(p, p === sayfa ? hash : "", true));
      const yigin = el;
      yigin.addEventListener("scroll", () => {{ if (hedef && hedef.yigin === yigin && Math.abs(yigin.scrollTop - hedef.konum) > 2) hedef = null; gorunumIste(yigin); }}, {{ passive: true }});
      if (!hash && sayfa !== s.sayfalar[0]) hedefKoy(yigin, sayfa, 0);  // hash yoksa sayfanın başına
    }}
    el.hidden = true;
    $("#alan").appendChild(el);
    cerceveler[kod] = el;
    return el;
  }};
  // Ortak çubuk: sekme geçişi, dil ve tema buradan
  const cubuk = () => VetoCubuk.kur({{ dil: DIL, sayfa: SEKMELER.find((x) => x.kod === ACIK).sayfalar[0], tek: {{ git: (s) => goster(s === "index" ? "hikaye" : s), dil: dilDegistir, tema: temaYay }} }});
  const temaYay = (tema) => document.querySelectorAll("#alan iframe").forEach((f) => f.contentWindow && f.contentWindow.postMessage({{ tur: "tema", tema }}, "*"));
  const goster = (sayfa, hash) => {{
    const kod = SAYFA_SEKME[sayfa] || sayfa;
    ACIK = kod;
    for (const [k, f] of Object.entries(cerceveler)) f.hidden = k !== kod;
    const vardi = !!cerceveler[kod];
    const el = cerceveler[kod] || kur(kod, sayfa, hash);
    el.hidden = false;
    if (el.classList.contains("yigin")) gorunumIste(el);
    if (hash && vardi) {{
      const f = el.tagName === "IFRAME" ? el : el.querySelector(`iframe[data-sayfa="${{sayfa}}"]`);
      if (f) f.contentWindow.postMessage({{ tur: "hash", hash }}, "*");
    }} else if (!hash && el.classList.contains("yigin") && vardi && sayfa !== SEKMELER.find((x) => x.kod === kod).sayfalar[0]) {{
      hedefKoy(el, sayfa, 0);
    }}
    cubuk();
    document.title = SEKMELER.find((s) => s.kod === kod)[DIL] + (DIL === "tr" ? " · Veto Atlası" : " · Veto Atlas");
  }};
  const dilDegistir = (d) => {{
    if (d === DIL || !["tr", "en"].includes(d)) return;
    DIL = d;
    document.documentElement.lang = d;
    for (const f of Object.values(cerceveler)) f.remove();
    for (const k of Object.keys(cerceveler)) delete cerceveler[k];
    goster(SEKMELER.find((s) => s.kod === ACIK).sayfalar[0]);
  }};
  addEventListener("message", (e) => {{
    const m = e.data || {{}};
    if (m.tur === "sayfa" && (SAYFALAR[m.sayfa] || m.sayfa === "index")) goster(m.sayfa === "index" ? "hikaye" : m.sayfa, m.hash);
    else if (m.tur === "dil") dilDegistir(m.dil);
    else if (m.tur === "yukseklik") {{ const f = document.querySelector(`.yigin iframe[data-sayfa="${{m.sayfa}}"]`); if (f) {{ f.style.height = Math.max(200, m.h) + "px"; hedefeKaydir(); gorunumIste(f.parentElement); }} }}
    else if (m.tur === "kaydir") {{ const f = document.querySelector(`.yigin iframe[data-sayfa="${{m.sayfa}}"]`); if (f) hedefKoy(f.parentElement, m.sayfa, m.y); }}
  }});
  const ilk = new URLSearchParams(location.search).get("lang");
  if (ilk === "en") {{ DIL = "en"; document.documentElement.lang = "en"; }}
  goster("hikaye");
}})();
</script>
</body>
</html>
"""
    yol = web / CIKTI
    yol.write_text(html, encoding="utf-8")
    return yol


def girdi_ozeti(kok: Path) -> str:
    """Dosyadaki girdi özeti (tests: dosyanın güncel olup olmadığı)."""
    s = (kok / "web" / CIKTI).read_text(encoding="utf-8")
    m = re.search(r'name="veto-atlasi-girdi-sha256" content="([0-9a-f]{64})"', s)
    return m[1] if m else ""
