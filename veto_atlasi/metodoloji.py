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


_AY_ADLARI = ("Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık|January|February|March|"
              "April|May|June|July|August|September|October|November|December")
# Tarihte gün, ay ve yıl satır sonunda ayrılmaz (kılavuz, Satır sonu): aralarına bölünmez boşluk (U+00A0)
_GUN_AY = re.compile(rf"\b(\d{{1,2}}) ({_AY_ADLARI})\b")
_AY_YIL = re.compile(rf"\b({_AY_ADLARI}) (\d{{4}})\b")
# Bu uzunluktan kısa, tire, eğik çizgi ya da boşluk taşıyan kodlar (ör. V-YYYY-AA-GG-n) satır sonunda bölünmez
_KISA_KOD = 24


def _tarih_bagla(metin: str) -> str:
    return _AY_YIL.sub("\\1\u00a0\\2", _GUN_AY.sub("\\1\u00a0\\2", metin))


# Satır sonunda ayrılmayan öteki parçalar (kılavuz, Satır sonu); kod parçalarına ve başlıklara uygulanmaz.
# Yıl ve madde aralığında yarım çizginin iki yanına sözcük birleştirici (U+2060): 1946–2004, 57–72
_ARALIK = re.compile(r"(?<=[\d)])–(?=[\d(])")
# Kısaltma ya da gönderme sözcüğü ile sayı: par. 54, para. 54, s. 8, p. 20, No. 119, Kural 2, Rule 2, Tablo 4
_KISALTMA_SAYI = re.compile(r"(?<![\w.])((?:par|paras|para|s|p|pp|No)\.|Kural|Rule|Madde|Article|Tablo|Table) (?=\d)")
# Sayı ile ardındaki ad (57 üye, 27 delegasyon, 13 words); bağlaç ve edatlar bağlanmaz
_BAGLAC = ("ve|ile|veya|ya|ise|ki|de|da|and|or|of|in|on|the|to|it|is|with|under|out|by|for|as|at|a|an|from|"
           "be|means|have|has|come|become|becomes|belong|match|merged|concerned|whose")
_SAYI_AD = re.compile(rf"(?<![\w./:,–\u2060-])(\d+(?:[.,]\d+)?) (?!(?:{_BAGLAC})\b)(?=[^\W\d_])")
# Sayı ile ardındaki madde harfi: 27 (3), A/59/L.67 (b)
_SAYI_HARF = re.compile(r"(\d) (?=\([a-z0-9]\))")


def _satir_bagla(metin: str) -> str:
    metin = _ARALIK.sub("\u2060–\u2060", metin)
    metin = _KISALTMA_SAYI.sub("\\1\u00a0", metin)
    metin = _SAYI_AD.sub("\\1\u00a0", metin)
    return _SAYI_HARF.sub("\\1\u00a0", metin)


def _satir_ici(metin: str, bagla: bool = True) -> str:
    """Kod parçaları dışındaki metinde kalın ve italik işaretlerini dönüştürür; bagla ise tarihleri, aralıkları ve
    sayılı göndermeleri satır sonunda ayrılmayacak biçimde bağlar (başlıklarda yalnız tarih)."""
    parcalar = re.split(r"(`[^`]+`)", metin)
    cikti = []
    for p in parcalar:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            kod = p[1:-1]
            sinif = ' class="kisa"' if len(kod) < _KISA_KOD and re.search(r"[-/ ]", kod) else ""
            cikti.append(f"<code{sinif}>{html.escape(kod)}</code>")
            continue
        p = html.escape(p, quote=False)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", p)
        p = re.sub(r"\[([^\]\n]+)\]\{lang=([a-z]{2})\}", r'<span lang="\2">\1</span>', p)
        p = _tarih_bagla(p)
        cikti.append(_satir_bagla(p) if bagla else p)
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
            bloklar.append(f"<h{duzey}{kim}>{_satir_ici(baslik, bagla=False)}</h{duzey}>")
        elif satir.startswith(">"):
            # Alıntı bloğu yalnızca depodaki dosya için not (ör. METODOLOJI_EN.md'nin çeviri notu); sayfada bu
            # bilgi girişin altındaki küçük satırdadır, iki kez görünmesin diye taşınmaz.
            paragraf_bitir(); liste_bitir()
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
<meta property="og:image:alt" content="{gorsel_alt_tr} / {gorsel_alt_en}">
<meta property="og:locale" content="tr_TR">
<meta property="og:locale:alternate" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image:alt" content="{gorsel_alt_tr} / {gorsel_alt_en}">
<meta property="og:url" content="https://vetoatlas.com/metodoloji">
<link rel="canonical" href="https://vetoatlas.com/metodoloji">
<link rel="alternate" hreflang="tr" href="https://vetoatlas.com/metodoloji">
<link rel="alternate" hreflang="en" href="https://vetoatlas.com/metodoloji?lang=en">
<link rel="alternate" hreflang="x-default" href="https://vetoatlas.com/metodoloji">
<link rel="icon" href="favicon.ico?v=2" sizes="32x32">
<link rel="icon" href="favicon.svg?v=2" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png?v=2">
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
.giris {{ font-family: var(--serif); font-size: var(--yz-govde); line-height: var(--sa-govde); }}
.ikincil {{ color: var(--murekkep-2); font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); }}
@media (max-width: 760px) {{ .kap {{ padding: 0 16px 48px; }} h1 {{ margin-top: 32px; }} }}

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
    tr: {{ baslik: "Metodoloji · Veto Atlası", aciklama: "{aciklama_tr}", gorselAlt: "{gorsel_alt_tr}" }},
    en: {{ baslik: "Methodology · Veto Atlas", aciklama: "{aciklama_en}", gorselAlt: "{gorsel_alt_en}" }},
  }}[DIL];
  const ek = DIL === "tr" ? "" : "?lang=" + DIL;
  document.documentElement.lang = DIL;
  document.title = SOZLUK.baslik;
  document.querySelector('meta[name="description"]').setAttribute("content", SOZLUK.aciklama);
  document.querySelector('meta[property="og:title"]').setAttribute("content", SOZLUK.baslik);
  document.querySelector('meta[property="og:description"]').setAttribute("content", SOZLUK.aciklama);
  document.querySelector('meta[property="og:image:alt"]').setAttribute("content", SOZLUK.gorselAlt);
  document.querySelector('meta[name="twitter:image:alt"]').setAttribute("content", SOZLUK.gorselAlt);
  document.querySelectorAll("main[data-dil]").forEach((m) => {{ m.hidden = m.dataset.dil !== DIL; }});
}})();
</script>
</body>
</html>
"""

ACIKLAMA_TR = "Veto Atlası’nın kategorileri, sayım kuralları, kaynak mutabakatı, tarih kuralları ve doğrulama yöntemi."
ACIKLAMA_EN = "Categories, counting rules, source reconciliation, date rules and verification method of the Veto Atlas."
# Önizleme görselinin (onizleme.png) alt metni; web/vetolar.html "onizlemeAlt" ile aynı
GORSEL_ALT_TR = "Veto Atlası: 1946’dan 2026’ya Güvenlik Konseyinde vetoyla düşen 266 öneri; her kare bir ret oyu, yıllara göre."
GORSEL_ALT_EN = "Veto Atlas: 266 proposals blocked by the veto in the Security Council, 1946–2026; each square is one negative vote, by year."
ACIK_DEPO = "https://github.com/drofhawke/vetoatlas"
# Girişin altındaki küçük satır: son değişiklik tarihi ve asıl metnin yeri ({tarih} iki dilde yazıyla)
KAYNAK_NOTU = {
    "tr": f'Son değişiklik {{tarih}}. Asıl metin <a href="{ACIK_DEPO}">açık depodaki</a> <code>METODOLOJI.md</code> dosyasıdır.',
    "en": f'Last changed {{tarih}}. This is a translation; the Turkish original, <code lang="tr">METODOLOJI.md</code> in the '
          f'<a href="{ACIK_DEPO}">public repository</a>, prevails where the two differ.',
}
AYLAR = {
    "tr": ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
           "November", "December"],
}
KOK = Path(__file__).resolve().parent.parent


def son_degisiklik(kok: Path = KOK) -> str:
    """METODOLOJI.md ve METODOLOJI_EN.md'nin son değiştiği gün (YYYY-AA-GG), git kaydından: işlenmemiş değişiklik
    varsa bugün, yoksa iki dosyanın son commit'inin tarihi (scripts/12_site_haritasi.py ile aynı kural)."""
    import datetime
    import subprocess
    yollar = ["METODOLOJI.md", "METODOLOJI_EN.md"]
    try:
        git = lambda *a: subprocess.run(["git", "-C", str(kok), *a], capture_output=True, text=True,  # noqa: E731
                                        check=True, encoding="utf-8").stdout
        if not git("status", "--porcelain", "--", *yollar).strip():
            tarih = git("log", "-1", "--format=%cs", "--", *yollar).strip()
            if tarih:
                return tarih
    except (OSError, subprocess.CalledProcessError):
        pass
    return datetime.date.today().isoformat()


def tarih_yazi(iso: str, dil: str) -> str:
    """'2026-10-21' -> '21 Ekim 2026' / '21 October 2026'."""
    y, a, g = (int(x) for x in iso.split("-"))
    return f"{g} {AYLAR[dil][a - 1]} {y}"


def govde(md: str, dil: str, tarih: str) -> str:
    h1, ic = md_html(md)
    gizli = " hidden" if dil != "tr" else ""
    # İlk paragraf giriş (Hakkında'daki gibi); altında tek satır küçük not
    not_ = f'<p class="ikincil">{KAYNAK_NOTU[dil].format(tarih=_tarih_bagla(tarih_yazi(tarih, dil)))}</p>'
    if ic.startswith("<p>"):
        son = ic.index("</p>") + len("</p>")
        ic = '<p class="giris">' + ic[3:son] + "\n" + not_ + ic[son:]
    else:
        ic = not_ + "\n" + ic
    # Metin sayfası düzeni (web/temel.css): "Bu sayfada" dizininin yeri başlığın hemen altı; dizini web/metin.js üretir
    return (f'  <main class="duz-yazi metin-duzen" lang="{dil}" data-dil="{dil}"{gizli}>\n'
            f"    <h1>{html.escape(h1)}</h1>\n"
            '    <div class="metin-dizin"></div>\n'
            '    <div class="metin">\n'
            f"{ic}\n    </div>\n  </main>")


def sayfa_uret(tr_md: str, en_md: str, tarih: str | None = None) -> str:
    tarih = tarih or son_degisiklik()
    # Bölüm kimlikleri iki dilde aynı; tek sayfada çakışmasın diye İngilizcede önek eklenir.
    en_govde = govde(en_md, "en", tarih).replace('id="bolum-', 'id="en-bolum-').replace('href="#bolum-', 'href="#en-bolum-')
    return SAYFA.format(govdeler=govde(tr_md, "tr", tarih) + "\n" + en_govde,
                        aciklama_tr=ACIKLAMA_TR, aciklama_en=ACIKLAMA_EN,
                        gorsel_alt_tr=GORSEL_ALT_TR, gorsel_alt_en=GORSEL_ALT_EN)


def yaz(kok: Path) -> tuple[Path, list[str]]:
    tr_md = (kok / "METODOLOJI.md").read_text(encoding="utf-8")
    en_yol = kok / "METODOLOJI_EN.md"
    if not en_yol.exists():
        return kok / "web/metodoloji.html", ["METODOLOJI_EN.md yok; metodoloji.html üretilmedi"]
    en_md = en_yol.read_text(encoding="utf-8")
    hedef = kok / "web/metodoloji.html"
    hedef.write_text(sayfa_uret(tr_md, en_md, son_degisiklik(kok)), encoding="utf-8", newline="\n")
    return hedef, yapi_farklari(tr_md, en_md)
