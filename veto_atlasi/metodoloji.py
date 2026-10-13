"""
METODOLOJI.md (Türkçe asıl metin) ve METODOLOJI_EN.md'den (çeviri) iki dilli web/metodoloji.html üretir.

Dış bağımlılık yoktur; yalnızca belgelerde kullanılan Markdown alt kümesi desteklenir:
"#"/"##"/"###" başlıklar, paragraflar, "- " ile başlayan liste maddeleri (iki boşlukla girintili devam
satırlarıyla), **kalın**, *italik*, `kod` ve dil işareti [metin]{lang=tr} (İngilizce metindeki Türkçe ifadeler). Bölümler sayıyla numaralanır ("## 2. ...", alt bölümler
"### 2.1. ..."); bağlantılar başlık numarasından üretilir (ör. "### 2.3. ..." -> #bolum-2-3), böylece iki
dilde aynıdır. "Bu sayfada" dizinini web/metin.js bu başlıklardan üretir; alt bölümler üst bölümün altında
girintilidir.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

BASLIK_NO = re.compile(r"^(\d+(?:\.\d+)?)\.\s")


def kimlik(numara: str) -> str:
    """Bölüm numarasından bağlantı kimliği: "2" -> bolum-2, "2.3" -> bolum-2-3."""
    return "bolum-" + numara.replace(".", "-")


def _satir_ici(metin: str) -> str:
    """Kod parçaları dışındaki metinde kalın ve italik işaretlerini dönüştürür."""
    parcalar = re.split(r"(`[^`]+`)", metin)
    cikti = []
    for p in parcalar:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            cikti.append(f"<code>{html.escape(p[1:-1])}</code>")
            continue
        p = html.escape(p, quote=False)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", p)
        p = re.sub(r"\[([^\]\n]+)\]\{lang=([a-z]{2})\}", r'<span lang="\2">\1</span>', p)
        cikti.append(p)
    return "".join(cikti)


def bolumler(md: str) -> list[tuple[str, str]]:
    """'##' (bölüm) ve '###' (alt bölüm) başlıklarının (numara, başlık) listesi, belgedeki sırasıyla."""
    sonuc = []
    for satir in md.splitlines():
        if satir.startswith(("## ", "### ")):
            baslik = satir.split(" ", 1)[1].strip()
            m = BASLIK_NO.match(baslik)
            sonuc.append((m[1] if m else "", baslik))
    return sonuc


def md_html(md: str) -> tuple[str, str]:
    """Döndürür: (h1 başlığı, gövde HTML'i)."""
    h1, bloklar = "", []
    paragraf: list[str] = []
    liste: list[str] = []

    def paragraf_bitir():
        if paragraf:
            bloklar.append(f"<p>{_satir_ici(' '.join(paragraf))}</p>")
            paragraf.clear()

    def liste_bitir():
        if liste:
            bloklar.append("<ul>" + "".join(f"<li>{_satir_ici(m)}</li>" for m in liste) + "</ul>")
            liste.clear()

    for satir in md.splitlines():
        if satir.startswith("# "):
            paragraf_bitir(); liste_bitir()
            h1 = satir[2:].strip()
        elif satir.startswith(("## ", "### ")):
            paragraf_bitir(); liste_bitir()
            duzey = 3 if satir.startswith("### ") else 2
            baslik = satir[duzey + 1:].strip()
            m = BASLIK_NO.match(baslik)
            kim = f' id="{kimlik(m[1])}"' if m else ""
            bloklar.append(f"<h{duzey}{kim}>{_satir_ici(baslik)}</h{duzey}>")
        elif satir.startswith("- "):
            paragraf_bitir()
            liste.append(satir[2:].strip())
        elif satir.startswith("  ") and liste and satir.strip():
            liste[-1] += " " + satir.strip()
        elif not satir.strip():
            paragraf_bitir(); liste_bitir()
        else:
            liste_bitir()
            paragraf.append(satir.strip())
    paragraf_bitir(); liste_bitir()
    return h1, "\n".join(bloklar)


def yapi_farklari(tr_md: str, en_md: str) -> list[str]:
    """İki dilin bölüm numaraları ve liste maddesi sayıları aynı değilse uyarılar."""
    uyarilar = []
    tr_no = [n for n, _ in bolumler(tr_md)]
    en_no = [n for n, _ in bolumler(en_md)]
    if tr_no != en_no:
        uyarilar.append(f"METODOLOJI_EN.md bölümleri Türkçe asıl metinle aynı değil: TR {tr_no}, EN {en_no}")
    say = lambda md: sum(1 for s in md.splitlines() if s.startswith("- "))  # noqa: E731
    if say(tr_md) != say(en_md):
        uyarilar.append(f"METODOLOJI_EN.md liste maddesi sayısı farklı: TR {say(tr_md)}, EN {say(en_md)}")
    return uyarilar


SAYFA = """<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Metodoloji · Veto Atlası</title>
<meta name="description" content="{aciklama_tr} / {aciklama_en}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Veto Atlası / Veto Atlas">
<meta property="og:title" content="Metodoloji · Veto Atlası / Methodology · Veto Atlas">
<meta property="og:description" content="{aciklama_tr} / {aciklama_en}">
<meta property="og:image" content="https://vetoatlas.com/onizleme.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="tr_TR">
<meta property="og:locale:alternate" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:url" content="https://vetoatlas.com/metodoloji">
<link rel="canonical" href="https://vetoatlas.com/metodoloji">
<link rel="alternate" hreflang="tr" href="https://vetoatlas.com/metodoloji">
<link rel="alternate" hreflang="en" href="https://vetoatlas.com/metodoloji?lang=en">
<link rel="alternate" hreflang="x-default" href="https://vetoatlas.com/metodoloji">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<meta name="theme-color" content="#FBF8F1">
<link rel="stylesheet" href="fonts/fonts.css">
<link rel="stylesheet" href="temel.css">
<script src="cubuk.js"></script>
<script src="metin.js"></script>
<style>
:root {{
  --zemin: #FBF8F1; --yuzey: #FFFFFF; --murekkep: #13213A; --murekkep-2: #5A6578; --cizgi: #E1DBCF; --vurgu: #A4262C;
  --serif: "Source Serif 4", Georgia, "Times New Roman", serif;
  --sans: "Source Sans 3", "Segoe UI", system-ui, -apple-system, sans-serif;
}}
:root[data-theme="dark"] {{--zemin: #1C1A17; --yuzey: #272420; --murekkep: #EDE8E0; --murekkep-2: #ABA496; --cizgi: #3B3731; --vurgu: #E05A52; }}
* {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; }}
body {{ margin: 0; background: var(--zemin); color: var(--murekkep); font-family: var(--sans); font-size: var(--yz-govde); line-height: var(--sa-govde); }}
.kap {{ max-width: 1180px; margin: 0 auto; padding: 0 24px 64px; }}
a {{ color: inherit; text-underline-offset: 3px; }}
:focus-visible {{ outline: 2px solid var(--murekkep); outline-offset: 2px; }}
[hidden] {{ display: none !important; }}
h1 {{ font-family: var(--serif); font-weight: 600; font-size: var(--yz-baslik); line-height: var(--sa-baslik); margin: 48px 0 12px; }}
h2 {{ font-family: var(--serif); font-weight: 600; font-size: var(--yz-govde); margin: 32px 0 8px; line-height: var(--sa-govde); }}
p, li {{ max-width: var(--olcu); }}
ul {{ padding-left: 24px; }}
li + li {{ margin-top: 8px; }}
code {{ word-break: break-all; font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); }}
.ikincil {{ color: var(--murekkep-2); font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); }}
@media (max-width: 760px) {{ body {{ font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); }} .kap {{ padding: 0 16px 48px; }} h1 {{ margin-top: 32px; }} }}

</style>
</head>
<body data-sayfa="metodoloji">
<header id="cubuk" class="cubuk"></header>
<div class="kap">
{govdeler}
</div>
<script>
(function () {{
  "use strict";
  // Dil adres çubuğunda (?lang=en) tutulur; bağlantı paylaşılınca seçim korunur.
  const DILLER = ["tr", "en"];
  const parametre = new URLSearchParams(location.search).get("lang");
  const DIL = DILLER.includes(parametre) ? parametre : "tr";
  const SOZLUK = {{
    tr: {{ baslik: "Metodoloji · Veto Atlası", aciklama: "{aciklama_tr}" }},
    en: {{ baslik: "Methodology · Veto Atlas", aciklama: "{aciklama_en}" }},
  }}[DIL];
  const ek = DIL === "tr" ? "" : "?lang=" + DIL;
  document.documentElement.lang = DIL;
  document.title = SOZLUK.baslik;
  document.querySelector('meta[name="description"]').setAttribute("content", SOZLUK.aciklama);
  document.querySelector('meta[property="og:title"]').setAttribute("content", SOZLUK.baslik);
  document.querySelector('meta[property="og:description"]').setAttribute("content", SOZLUK.aciklama);
  document.querySelectorAll("main[data-dil]").forEach((m) => {{ m.hidden = m.dataset.dil !== DIL; }});
}})();
</script>
</body>
</html>
"""

ACIKLAMA_TR = "Veto Atlası'nın kategorileri, sayım kuralları, kaynak mutabakatı, tarih kuralları ve doğrulama yöntemi."
ACIKLAMA_EN = "Categories, counting rules, source reconciliation, date rules and verification method of the Veto Atlas."
KAYNAK_NOTU = {
    "tr": "Bu sayfa depodaki <code>METODOLOJI.md</code> dosyasından üretilir; asıl metin odur.",
    # İngilizce metin çeviri olduğunu kendi ilk paragrafında söyler.
    "en": "",
}


def govde(md: str, dil: str) -> str:
    h1, ic = md_html(md)
    gizli = " hidden" if dil != "tr" else ""
    not_ = f'    <p class="ikincil">{KAYNAK_NOTU[dil]}</p>\n' if KAYNAK_NOTU[dil] else ""
    # Metin sayfası düzeni (web/temel.css): "Bu sayfada" dizininin yeri başlığın hemen altı; dizini web/metin.js üretir
    return (f'  <main class="duz-yazi metin-duzen" lang="{dil}" data-dil="{dil}"{gizli}>\n'
            f"    <h1>{html.escape(h1)}</h1>\n"
            '    <div class="metin-dizin"></div>\n'
            '    <div class="metin">\n'
            f"{not_}"
            f"{ic}\n    </div>\n  </main>")


def sayfa_uret(tr_md: str, en_md: str) -> str:
    # Bölüm kimlikleri iki dilde aynı; tek sayfada çakışmasın diye İngilizcede önek eklenir.
    en_govde = govde(en_md, "en").replace('id="bolum-', 'id="en-bolum-').replace('href="#bolum-', 'href="#en-bolum-')
    return SAYFA.format(govdeler=govde(tr_md, "tr") + "\n" + en_govde,
                        aciklama_tr=ACIKLAMA_TR, aciklama_en=ACIKLAMA_EN)


def yaz(kok: Path) -> tuple[Path, list[str]]:
    tr_md = (kok / "METODOLOJI.md").read_text(encoding="utf-8")
    en_yol = kok / "METODOLOJI_EN.md"
    if not en_yol.exists():
        return kok / "web/metodoloji.html", ["METODOLOJI_EN.md yok; metodoloji.html üretilmedi"]
    en_md = en_yol.read_text(encoding="utf-8")
    hedef = kok / "web/metodoloji.html"
    hedef.write_text(sayfa_uret(tr_md, en_md), encoding="utf-8", newline="\n")
    return hedef, yapi_farklari(tr_md, en_md)
