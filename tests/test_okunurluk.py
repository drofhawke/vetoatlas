"""
ADIM 41 ve 45 – okunurluk: sayfa yapısındaki kalıcı kararlar (kaynaklar/kimlik/KILAVUZ.md bölüm 2, "Okuma kolaylığı").

- Ya veto olmasaydı?: "Oyların sayım sırası bir gösterimdir…" notu panellerin altında bir kez.
- Vetolar: grafik açıklaması tek cümle; kalan cümleler hemen altındaki "Nasıl okunur?" kutusunda, metinleri aynen.
  Grafiğin işaretleri (kapalı oturum vetosu, hitap üçgeni) üye düğmelerinden ayrı, kendi satırında (ADIM 45).
- Yöntem yalnızca "Nasıl yaptık?"ta (ADIM 45, kalıcı kural): diğer sayfalarda kaynak dosyası, SHA-256, indirme
  listesi, "sayılar veri setinden hesaplanır" türü notlar, alt bilgide kaynak listesi, tanımlar bölümü ve slogan
  yok; alt bilgide yalnızca veri tarihi (Hikâye, Vetolar).
- Söz ve Kayıt: girişin altında her bölüme bağlantı veren içindekiler; tek dosyada sayfa içi bağlantılar sayfanın
  kendi çerçevesinde kalır. Reform modelleri ayrı sayfada (web/reform.html), tablo açık.
- Metodoloji: bölümler sayıyla (1, 2, 2.1 …); alt bölümler "Bu sayfada" dizininde girintili.
- Metin sayfaları (Hakkında, Metodoloji; ADIM 50): "Bu sayfada" dizini bölüm başlıklarından üretilir (web/metin.js);
  her bölüm başlığı kimlikli, İngilizce kimlikler Türkçenin "en-" önekli eşi.

Hizalama ve etiket kuralları tests/test_tasarim.py'dedir; hesaplanmış görünüm tarayıcıda ayrıca denetlenir.
"""
import html
import json
import re
import shutil
import subprocess

import pytest

from conftest import KOK

WEB = KOK / "web"


def oku(ad):
    return (WEB / ad).read_text(encoding="utf-8")


def govde(sayfa):
    """Sayfanın işaretlemesi (betikler hariç)."""
    return sayfa[sayfa.index("<body"):sayfa.index('<script src="veri.js">')]


def sozluk(sayfa, anahtar):
    """Sözlükteki düz metin değerleri, sırasıyla TR ve EN."""
    return re.findall(r'"' + re.escape(anahtar) + r'": "([^"]*)"', sayfa)


def cumleler(metin):
    return [c for c in re.split(r"(?<=[.!?])\s+", metin.strip()) if c]


def test_sira_notu_panellerin_altinda_bir_kez():
    s = oku("simulasyon.html")
    g = govde(s)
    assert g.count('data-t="siraNotu"') == 1
    for panel in re.findall(r'<article class="panel kutu".*?</article>', g, re.S):
        assert "sira-notu" not in panel
    # ADIM 51: panellerin altındaki sonuç bloğunun en altında, düğmelerden sonra (küçük yazıyla)
    assert '        </div>\n        <p class="sira-notu" data-t="siraNotu"></p>\n      </div>\n      <div class="serit kutu" id="serit" hidden>' in g
    assert g.index('<div class="sonuc-blok kutu" id="sonuc-blok">') < g.index('class="sira-notu"')
    assert 'siraNotu: "Oyların sayım sırası bir gösterimdir; toplantı kayıtlarında üye bazlı oylama sırası yoktur.",' in s
    assert ".sira-notu { font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); color: var(--murekkep-2);" in s


ESKI_ACIKLAMA = [  # ADIM 41 öncesi grafik açıklaması: cümleler bölünerek taşındı, metin aynı kaldı
    "Her kare bir ret oyunu gösterir; sütunlar yılları, renkler vetoyu kullanan daimi üyeyi. Bir sütuna tıklayınca o "
    "yılın vetoları aşağıda listelenir, bir kareye tıklayınca ilgili kayıt açılır. Üstteki küçük üçgenler, "
    "Cumhurbaşkanı Erdoğan’ın kaynaklarda yer alan Genel Kurul hitaplarının tarihlerini gösterir; üzerine gelince ya "
    "da Tab tuşuyla odaklanınca o yılın alıntısı görünür; tıklayınca ya da Enter’a basınca alıntı Söz ve Kayıt "
    "sayfasında açılır.",
    "Each square is one negative vote; columns are years, colours show the permanent member that cast the veto. Click "
    "a column to list that year's vetoes below; click a square to open the record. The small triangles at the top mark "
    "the dates of President Erdoğan’s addresses to the General Assembly that are in the sources; hover over one or "
    "focus it with the Tab key to see that year’s quotation; click it or press Enter to open the quotation on the Word "
    "and Record page.",
]


def test_vetolar_grafik_aciklamasi_tek_cumle():
    s = oku("vetolar.html")
    aciklama, okuma = sozluk(s, "grafik.aciklama"), sozluk(s, "grafik.okuma")
    assert len(aciklama) == len(okuma) == 2
    for a, o, eski in zip(aciklama, okuma, ESKI_ACIKLAMA):
        assert len(cumleler(a)) == 1, a
        assert a + " " + o == eski  # kalan cümleler "Nasıl okunur?" kutusunda, metin değişmeden
    assert sozluk(s, "grafik.okumaBaslik") == ["Nasıl okunur?", "How to read this chart"]
    g = govde(s)
    assert ('<figcaption id="grafik-aciklama" data-t="grafik.aciklama"></figcaption>\n'
            '    <details class="okuma"><summary data-t="grafik.okumaBaslik"></summary>'
            '<p id="grafik-okuma" data-t="grafik.okuma"></p></details>') in g
    assert 'aria-labelledby="grafik-aciklama" aria-describedby="grafik-okuma grafik-klavye"' in g


def test_vetolar_alt_bilgi_yalnizca_veri_tarihi():
    """ADIM 45 (ADIM 41'deki "Kaynak ve indirme ayrıntıları" kutusunun yerine): alt bilgide yalnızca veri tarihi; kaynak
    dosyası ve SHA-256 "Nasıl yaptık?"ta (Hakkında, Metodoloji). Hakkında'daki indirme listesi 13 Ekim'de kaldırıldı (kullanıcı
    kararı); veri setinin arşivi Zenodo'da, İletişim'in altındaki satırda."""
    s = oku("vetolar.html")
    kod = s[s.index("  // ---------- Alt bilgi ----------"):]
    kod = kod[:kod.index("guncelle();")]
    assert re.findall(r"<p\b[^>]*>", kod) == ['<p class="veri-tarihi">'] and "<details" not in kod
    for eski in ("alt-ayrinti", "alt.ayrinti", "alt.kaynak", "alt.baslik", "alt.surum", "alt.indir", 'class="indirmeler"', "m.indirmeler",
                 "kaynak_sha256", "SHA-256"):
        assert eski not in s, eski
    assert '"alt.veriTarihi": ({ tarih }) => `Veri tarihi: ${tarih}.`,' in s and '"alt.veriTarihi": ({ tarih }) => `Data as of ${tarih}.`,' in s
    assert '<time datetime="${esc(m.veri_surumu)}">${tarihUzun(m.veri_surumu)}</time>' in kod
    # Hakkında'da indirme listesi yok; veri setinin arşivi Zenodo (DOI bağlantısı iki dilde)
    h = oku("hakkinda.html")
    assert 'data-yer="indir"' not in h and "m.indirmeler" not in h
    assert h.count('href="https://doi.org/10.5281/zenodo.23326362"') == 2


ICERIK_SAYFALARI = ["hikaye", "vetolar", "vizyon", "reform", "simulasyon", "temsil"]
# Yöntem ve kaynak hatırlatmaları: depo dosyaları, SHA-256, "sayılar … hesaplanır/okunur", alt bilgide kaynak listesi,
# tanımlar bölümü, slogan. (Veri dosyası yoksa çıkan geliştirici uyarısı "scripts/04_web_verisi.py" der; bu kalıpta yok.)
YONTEM = re.compile(r"kaynaklar/|web/veri\.js|KAYNAKLAR\.md|scripts/09_temsil|SHA-256|sha256|sayfa açılırken|veri dosyasından|"
                    r"veri setinden hesaplanır|when the page (?:loads|opens)|from the data file|figures are computed from|"
                    r"Kaynaklar:|Sources:|altBaslik|h-tanimlar|c-slogan|alt-ayrinti|Kaynak ve indirme")


def yorumsuz(sayfa):
    """CSS/JS/HTML yorumları çıkarılmış kaynak (yorumlar okura görünmez)."""
    sayfa = re.sub(r"/\*.*?\*/", " ", sayfa, flags=re.S)
    sayfa = re.sub(r"<!--.*?-->", " ", sayfa, flags=re.S)
    return re.sub(r"(?m)(^|\s)//\s.*$", " ", sayfa)


def test_yontem_yalnizca_nasil_yaptikta():
    """ADIM 45, kalıcı kural: yöntem ve kaynak açıklamaları yalnızca "Nasıl yaptık?" sekmesinde (Hakkında, Metodoloji)."""
    for ad in ICERIK_SAYFALARI:
        s = yorumsuz(oku(f"{ad}.html"))
        bulunan = YONTEM.search(s)
        assert not bulunan, (ad, s[max(0, bulunan.start() - 80):bulunan.end() + 40])
        # Alt bilgi yalnızca veri tarihi taşıyan sayfalarda (Hikâye, Vetolar); diğerlerinde alt bilgi yok
        assert ("<footer" in s) == (ad in ("hikaye", "vetolar")), ad
    # Kalan okuma notları: kapalı oturum sayımı, "Küresel" tanımı, doğrulanmayan 1945 değeri, oran okuma notu
    v = oku("vizyon.html")
    assert "“Küresel”: belirli bir bölgeye bağlanmayan gündemler" in v and "kitaptaki 1945 değeri (yüzde 60) bu çalışmayla doğrulanmadı" in v
    assert 'giris2: "Hitaplarda basılı sayfa numarası, kitapta bölüm başlığı verilir. Alıntı ile sayı arasında bir neden-sonuç ilişkisi ileri sürülmez.",' in v
    t = oku("temsil.html")
    assert "Koltuk / gösterge oranı 1 ise grubun koltuk payı gösterge payına eşittir" in t and "Paylar BM üyelerinin toplamı içindedir." in t
    # Taşınan bilgiler Metodoloji'de: Gazze seçim dosyası, bölge ataması, 1963 nüfus kuralı, simülasyonun kapsamı
    m = (KOK / "METODOLOJI.md").read_text(encoding="utf-8")
    for parca in ("`kaynaklar/gazze_taslaklari.md`", "Bölge gündem başlığına göre atanır", "SSCB 13 cumhuriyet",
                  "varsayımsal bir öneri girilemez", "`kaynaklar/reform_modelleri.csv`"):
        assert parca in m, parca
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert '**Yöntem yalnızca "Nasıl yaptık?"ta (kalıcı kural).**' in kilavuz


def test_vetolar_isaretler_ayri_satirda():
    """ADIM 45: "Kapalı oturum vetosu" ve hitap üçgeni üye düğmelerinden (filtre) ayrı, kendi satırında; hitap etiketi
    kimin hitabı olduğunu söyler. "Bu atlas … hazırlanmıştır" satırı ve oklu sayfa bağlantıları Vetolar'da yok."""
    s = oku("vetolar.html")
    g = govde(s)
    assert '<ul class="uyeler-lejant" id="lejant"></ul>\n    <ul class="isaret-lejant" id="isaretler"></ul>' in g
    assert ".isaret-lejant { display: flex; flex-wrap: wrap; gap: 0 24px; margin: 8px 0 0; padding: 0; list-style: none; }" in s
    assert '"lejant.hitap": "Cumhurbaşkanı Erdoğan’ın Genel Kurul hitabı"' in s and '"lejant.hitap": "President Erdoğan’s address to the General Assembly"' in s
    kod = s[s.index("  // ---------- Lejant / üye filtresi ----------"):s.index("  // ---------- Konulara göre vetolar ----------")]
    assert "lejant.appendChild(kl)" not in kod and "lejant.appendChild(hl)" not in kod
    assert 'isaretler.setAttribute("aria-label", t("lejant.isaretler"));' in kod
    for eski in ("vizyon-satir", "vizyon.satir", "sim.bag", "temsil.bag"):
        assert eski not in s, eski


def test_reform_sayfasi():
    """ADIM 45: Güvenlik Konseyi reform modelleri ayrı sekmede; tablo açık (kapalı kutuda değil), dört model belgelerin
    tarih sırasıyla, dört ölçüt, her hücrenin altında dayanak; dar ekranda ölçüt ölçüt alt alta."""
    r = oku("reform.html")
    g = r[r.index("<body"):r.index('<script src="veri.js">')]
    assert '<body data-sayfa="reform">' in g and "<details class=\"tablo-ac\"" not in g
    assert '<div class="tablo-kap kutu"><table class="reform" id="reform" aria-labelledby="baslik"></table></div>' in g
    assert '<div class="olcutler kutu" id="olcutler"></div>' in g
    assert 'const MODELLER = ["Ezulwini Uzlaşısı", "G4", "Uzlaşı için Birlik", "Daha Adil Bir Dünya Mümkün"]' in r
    assert 'const OLCUTLER = ["toplam", "yeni_daimi", "veto", "genel_kurul"];' in r
    assert "<small>${t(\"dayanak\")}: " in r
    assert "@media (max-width: 960px) {\n  .tablo-kap { display: none; }\n  .olcutler { display: block; }\n}" in r
    # Sayfa başlığı sekme adıyla aynı; eski başlık giriş cümlesinde (denetim sonrası)
    assert 'baslik: "Reform modelleri"' in r and 'baslik: "Reform models"' in r
    assert 'giris: "Güvenlik Konseyi reformu için dört model aynı ölçütlerle, belgelerin tarih sırasıyla."' in r
    # Söz ve Kayıt'ta reform bölümü yok; kitaptaki model bölümü yerinde
    v = oku("vizyon.html")
    assert "h-reform" not in v and "reformModelleri" not in v and 'id="h-model"' in v


def test_soz_ve_kayit_icindekiler():
    s = oku("vizyon.html")
    g = govde(s)
    nav = g[g.index('<nav class="icindekiler" aria-labelledby="icindekiler-baslik">'):g.index("</nav>")]
    baglantilar = re.findall(r'<li><a href="#(h-[\w-]+)" data-t="(h\.\w+)"></a></li>', nav)
    bolumler = re.findall(r'<section aria-labelledby="(h-[\w-]+)">\s*<h2 id="\1" data-t="(h\.\w+)"', g)
    assert len(bolumler) == 7 and baglantilar == bolumler  # her bölüm, sayfadaki sırasıyla ve aynı başlıkla (reform ayrı sayfada)
    assert g.index('<header class="giris">') < g.index("</nav>") < g.index("</header>", g.index('<header class="giris">')) < g.index("<main>")  # girişte, ilk bölümden önce
    assert '<b id="icindekiler-baslik" data-t="icindekiler"></b>' in nav
    assert 'icindekiler: "İçindekiler"' in s and 'icindekiler: "Contents"' in s
    assert ".icindekiler ul { margin: var(--b2) 0 0; columns: 2 288px; column-gap: var(--b8); }" in s


def test_kitaptaki_model_basligi_ve_girisi():
    """ADIM 53: Söz ve Kayıt'ta model bölümünün başlığı "Kitaptaki model" (EN "The model in the book"); başlığın altında
    ikincil renkte kitabın künyesi (kaynak tablosundaki künyeyle aynı); giriş paragrafı modelin dört unsurunu sayar.
    İçindekiler bağlantısı başlıkla aynı anahtardan gelir. "Alıntılar kısa tutulmuş …" türü yöntem notu sayfada yok;
    Metodoloji 2.7'de iki dilde yer alır."""
    v = oku("vizyon.html")
    assert '"h.model": "Kitaptaki model",' in v and '"h.model": "The model in the book",' in v
    assert '<li><a href="#h-model" data-t="h.model"></a></li>' in v
    kunye = ("Recep Tayyip Erdoğan, <i lang=\"tr\">Daha Adil Bir Dünya Mümkün: Birleşmiş Milletler Reformu İçin Bir Model Önerisi</i>, "
             "Turkuvaz Kitap, 2021.")
    assert f'<h2 id="h-model" data-t="h.model"></h2>\n      <p class="model-kunye">{kunye}</p>\n' in v
    assert ".model-kunye { margin: 0 0 var(--b3); font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); color: var(--murekkep-2);" in v
    kaynaklar = (KOK / "kaynaklar/KAYNAKLAR.md").read_text(encoding="utf-8")
    assert ("Recep Tayyip Erdoğan, *Daha Adil Bir Dünya Mümkün: Birleşmiş Milletler Reformu İçin Bir Model Önerisi*, Turkuvaz Kitap, "
            "1. baskı, Eylül 2021") in kaynaklar
    assert ('"model.aciklama": "Kitap, Güvenlik Konseyi için dört unsurlu bir reform modeli önerir: temsil, üye sayısı, veto ile daimî '
            'üyelik ve Konsey’in Genel Kurul’la ilişkisi. Aşağıda her unsur kitabın kendi ifadesiyle yer alır; üye sayısı için kitabın '
            'sunduğu iki seçenek, kitaptaki sırayla verilmiştir.",') in v
    assert ('"model.aciklama": "The book proposes a four-part reform model for the Security Council: representation, the number of '
            'members, the veto and permanent membership, and the Council’s relationship with the General Assembly. Each element appears '
            'below in the book’s own words; the two options the book offers for the number of members are given in the book’s order.",') in v
    # Modelin dört unsuru, kartların sırasıyla
    assert 'const MADDELER = [["m.temsil", "m.temsilOzet", ["kitap-1"]], ["m.sayi", "m.sayiOzet", ["kitap-2", "kitap-3"]],' in v
    for eski in ("kitaptaki model\"", "the model in the book\"", "Kitap (Eylül 2021)", "The book (September 2021)", "kısa tutulmuş", "kept short"):
        assert eski not in v, eski
    tr_md = (KOK / "METODOLOJI.md").read_text(encoding="utf-8")
    en_md = (KOK / "METODOLOJI_EN.md").read_text(encoding="utf-8")
    tr_not = '"Kitaptaki model" bölümünde alıntılar kısa tutulur; her unsurun geri kalanı özetlenir.'
    en_not = 'In "The model in the book" section, quotations are kept short and the rest of each element is summarised.'
    assert tr_not in tr_md[tr_md.index("### 2.7."):tr_md.index("### 2.8.")]
    assert en_not in " ".join(en_md[en_md.index("### 2.7."):en_md.index("### 2.8.")].split())
    m = oku("metodoloji.html")
    assert tr_not in m and en_not in m


def test_soz_ve_kayit_sutun_basliklari():
    """ADIM 54: Söz ve Kayıt satırlarının ve Kitaptaki model kartlarının üstünde sütun başlıkları (Söz / Kayıt; Unsur /
    Kitaptan): ikincil renk, küçük boyut, alt çizgili, üst çubuğun altında yapışkan. Satırlardaki "Veri setinde" etiketi yok;
    hücrelerde etiket yok. 760 px altında başlıklar görünmez ama ekran okuyucuya açık kalır (display: none değil); Söz ve
    Kayıt satırlarında kayıt bölümünün başında yalnızca görsel "Kayıt" etiketi. Sütunlar tablo rolleriyle işaretli."""
    v = oku("vizyon.html")
    # İşaretleme: başlık satırı ve satırlar aynı tabloda; tablo bölüm başlığıyla adlandırılır
    for bolum, sutunlar, satirlar in (("h-soz", ("sutun.soz", "sutun.kayit"), '<div class="soz-kayit kutu" id="soz-kayit" role="rowgroup"></div>'),
                                      ("h-model", ("sutun.unsur", "sutun.kitaptan"), '<div class="model" id="model" role="rowgroup"></div>')):
        sinif = "sutun-basliklari" + (" model-sutunlari" if bolum == "h-model" else "")
        assert (f'<div role="table" aria-labelledby="{bolum}">\n'
                f'        <div class="{sinif}" role="row"><span role="columnheader" data-t="{sutunlar[0]}"></span>'
                f'<span role="columnheader" data-t="{sutunlar[1]}"></span></div>\n'
                f'        {satirlar}\n      </div>') in v, bolum
    assert '`<div class="soz-satir" id="alinti-${esc(a.id)}" role="row">' in v and '<div class="soz" role="cell">' in v
    assert '<div class="kayit-karsilik" role="cell"><p class="sutun-etiketi" aria-hidden="true">${t("sutun.kayit")}</p>' in v
    assert '`<div class="kutu" role="row"><div class="model-ozet" role="cell">' in v and '<div class="model-alinti" role="cell">' in v
    assert v.count("sutun-etiketi\"") == 1  # etiket yalnızca Söz ve Kayıt satırlarında; model kartlarında yok
    for eski in ("k.baslik", "Veri setinde", "In the dataset", '<ol class="soz-kayit', '<ul class="model"'):
        assert eski not in v, eski
    # Sözlük
    assert '"sutun.soz": "Söz", "sutun.kayit": "Kayıt", "sutun.unsur": "Unsur", "sutun.kitaptan": "Kitaptan",' in v
    assert '"sutun.soz": "Word", "sutun.kayit": "Record", "sutun.unsur": "Element", "sutun.kitaptan": "From the book",' in v
    # Görünüm: yapışkan başlık (çubuk 76 px; tek dosya çerçevesinde çubuk yok), alt çizgi; dar ekranda görsel gizleme
    assert ".sutun-basliklari { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr); position: sticky; top: 0; z-index: 2;" in v
    assert "background: var(--zemin); border: 1px solid transparent; border-top: 0; border-bottom-color: var(--cizgi);" in v
    assert ".c-cubuklu .sutun-basliklari { top: 76px; }" in v and ".sutun-etiketi { display: none; }" in v
    dar = v[v.index("@media (max-width: 760px) {"):]
    dar = dar[:dar.index("\n}")]
    assert "  .sutun-basliklari { position: absolute; width: 1px; height: 1px; margin: 0; overflow: hidden; clip-path: inset(50%);" in dar
    assert "  .sutun-etiketi { display: block;" in dar and "display: none" not in dar
    assert ".soz-satir { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr); gap: 0; border-top: 1px solid var(--cizgi); scroll-margin-top: var(--b12); }" in v
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "- Söz ve Kayıt satırlarının ve \"Kitaptaki model\" kartlarının üstünde bir sütun başlığı satırı vardır" in kilavuz


def test_kunye_tek_bicim():
    """Denetim sonrası: alıntı künyesi Hikâye'de, Söz ve Kayıt'ta ve paylaşım kartlarında aynı sıra ve ayraçla.
    Hitap: Cumhurbaşkanı Recep Tayyip Erdoğan · BM 74. Genel Kurulu konuşması · 24 Eylül 2019 · s. 6
    Kitap: Cumhurbaşkanı Recep Tayyip Erdoğan · Daha Adil Bir Dünya Mümkün · Giriş
    İngilizcede aynı yapı (President … · Address to the 74th Session of the UN General Assembly · 24 September 2019 · p. 6);
    Türkçe parçalar (kitap adı, bölüm adı) lang="tr". Sayfa kısaltması numarasından ayrılmaz. Kartlarda ad alıntının altında,
    kalan kısım alt bilgide aynı sıra ve ayraçla (kart düzeni iki satırdır)."""
    h, v = oku("hikaye.html"), oku("vizyon.html")
    for s in (h, v):
        assert 'const KITAP = "Daha Adil Bir Dünya Mümkün";' in s
        assert 'if (a.bolum) return `${kim} · ${DIL === "tr" ? KITAP : `<span lang="tr">${KITAP}</span>`} · ${t("bolum", { b: esc(a.bolum) })}`;' in s
        assert """'Chapter 2: <span lang="tr">Birleşmiş Milletler Reformu</span> (Reform of the United Nations)'""" in s
    assert 'kunyeKim: "Cumhurbaşkanı Recep Tayyip Erdoğan", sayfaKisa: "s.",' in h and 'kunyeKim: "President Recep Tayyip Erdoğan", sayfaKisa: "p.",' in h
    assert ('return `${kim} · ${esc(etkinlikAdi(a))} · ${esc(tarihUzun(a.tarih))} · ${esc(t("sayfaKisa"))}\\u00a0'
            '${esc(ingilizce ? a.basili_sayfa_en : a.basili_sayfa)}`;') in h
    assert 'konusmaci: "' not in h and 't("konusmaci")' not in h and "epigrafKunye" not in h
    assert '<p class="kaynak">${kunye(a)}' in h and '<p class="kunye">${kunye(a)} · <a href=' in h
    assert 'kunyeKim: "Cumhurbaşkanı Recep Tayyip Erdoğan",' in v and 'kunyeKim: "President Recep Tayyip Erdoğan",' in v
    assert "return `${kim} · ${esc(etk)} · ${tarihUzun(a.tarih)} · ${t(\"sayfa\", { s })}`;" in v
    assert "sayfa: ({ s }) => `s.\\u00a0${s}`" in v and "sayfa: ({ s }) => `p.\\u00a0${s}`" in v and "kitapEtkinlik" not in v
    # Kartlar: ad alıntının altında; alt bilgi etkinlik · tarih · sayfa
    import json
    m = json.loads((WEB / "kartlar/kartlar.json").read_text(encoding="utf-8"))
    k = next(x for x in m["kartlar"] if x["id"] == "kart-08-alinti-2019")
    assert k["metin"]["tr"] == "Cumhurbaşkanı Recep Tayyip Erdoğan"
    assert k["kaynak"]["tr"] == "BM 74. Genel Kurulu konuşması · 24 Eylül 2019 · s. 6"
    assert k["kaynak"]["en"] == "Address to the 74th Session of the UN General Assembly · 24 September 2019 · p. 6"


def test_denetim_sonrasi_duzeltmeler():
    """Denetim sonrası (1, 2, 3, 5, 6): dar ekranda satır içi tablolar kendi kabında kayar; İngilizce sayfalardaki Türkçe
    ifadeler lang="tr"; sabit yazılmış iki sayı veriden; Temsil'deki 1963 hesabı tek cümle ve Metodoloji 2.9'a bağlantı;
    sayfa başlıkları sekme adlarıyla aynı."""
    v = oku("vizyon.html")
    assert '<details class="tablo-ac"><summary>${t("tabloGoster")}</summary>\n      <div class="tablo-kap"><table>' in v
    assert '<details class="tablo-ac"><summary>${t("tabloGoster")}</summary>\n        <div class="tablo-kap"><table>' in v
    assert v.count("</tbody></table></div></details>") == 2 and "</tbody></table></details>" not in v
    # Sabit sayılar veriden
    assert '<p class="aciklama" id="konu-aciklama"></p>' in v and 'data-t="konu.aciklama"' not in v
    assert '$("#konu-aciklama").textContent = t("konu.aciklama", { n: sayi(kayitlar.filter((k) => k.kapali).length) });' in v
    assert "yazmayan 2 veto" not in v and "The 2 vetoes" not in v
    h = oku("hakkinda.html")
    assert h.count('<span data-yer="konu-sayisi"></span>') == 2 and "15 konudan" not in h and "one of 15 topics" not in h
    assert "yer('[data-yer=\"konu-sayisi\"]').textContent = sayi((m.konular || []).length);" in h
    # lang="tr" işaretleri
    assert 'const kunye = (a) => `${t("kitapta")}: ${DIL === "en" ? `<span lang="tr">${esc(a.bolum)}</span>` : esc(a.bolum)}`;' in oku("simulasyon.html")
    md = oku("metodoloji.html")
    assert '<span lang="tr">“Dünya 5’ten Büyüktür.”</span>' in md and '<span lang="tr">DHL listesinin kapsamı</span>' in md
    # Temsil: tek cümle + Metodoloji 2.9 bağlantısı (iki dilde doğru adres)
    t = oku("temsil.html")
    assert "ardıl ülkelerin WPP serileri" not in t and "successor countries" not in t
    assert '"nufus.aciklama": ({ u63, u }) => `1963 payı 1963 sonundaki ${u63} BM üyesinin, 2023 payı bugünkü ${u} üyenin toplamı içindedir.`,' in t
    assert '<a id="nufus-metodoloji" href="metodoloji.html#bolum-2-9" data-t="nufus.metodoloji"></a>' in t
    assert '$("#nufus-metodoloji").setAttribute("href", `metodoloji.html${ek}#${DIL === "tr" ? "" : "en-"}bolum-2-9`);' in t
    assert 'id="bolum-2-9"' in md and 'id="en-bolum-2-9"' in md
    # Sayfa başlıkları sekme adlarıyla aynı
    for ad, tr, en in (("vetolar.html", '"baslik": "Vetolar",', '"baslik": "Vetoes",'), ("reform.html", 'baslik: "Reform modelleri",', 'baslik: "Reform models",'),
                       ("temsil.html", 'baslik: "Kim temsil ediliyor?",', 'baslik: "Who is represented?",')):
        s = oku(ad)
        assert tr in s and en in s, ad
    assert "<title>Vetolar · Veto Atlası</title>" in oku("vetolar.html") and "<title>Kim temsil ediliyor? · Veto Atlası</title>" in t
    assert 'giris1: "Temsil endeksi, her BM bölgesel grubu için beş payı yan yana gösterir:' in t


def test_tek_dosyada_sayfa_ici_baglantilar_cercevede():
    """srcdoc çerçevesinde "#bölüm" bağlantısı üst belgenin adresine gider; köprü betiği tıklamayı yakalayıp kaydırır
    (Söz ve Kayıt içindekiler, Hakkında ve Metodoloji "Bu sayfada" dizini)."""
    t = (KOK / "veto_atlasi/tek_dosya.py").read_text(encoding="utf-8")
    assert 'if (href.length > 1 && href[0] === "#") { e.preventDefault(); git(href); return; }' in t
    assert t.index('href[0] === "#"') < t.index("const m = href.match(SAYFA);")
    assert oku("veto-atlasi-tek-dosya.html").count("e.preventDefault(); git(href); return; }") == 8  # sekiz sayfanın köprüsü
    # Alt alta dizilen sayfalarda (Nasıl yaptık?) hedef, çerçeve yükseklikleri sonradan geldikçe yeniden uygulanır:
    # "Nasıl yaptık?" hiç açılmamışken metodoloji.html bağlantısı da Metodoloji'nin başını açar (ADIM 42)
    assert "if (!hash && sayfa !== s.sayfalar[0]) hedefKoy(yigin, sayfa, 0);" in t
    assert 'f.style.height = Math.max(200, m.h) + "px"; hedefeKaydir();' in t and "if (f) hedefKoy(f.parentElement, m.sayfa, m.y);" in t


def test_metodoloji_sayi_ile_numaralanir():
    """ADIM 45: bölümler sayıyla (1, 2, 2.1, 2.2 …); harfli alt bölüm (2a) yok. Alt bölümler h3; "Bu sayfada" dizininde üst
    bölümün altında iç içe listede (girintili; ADIM 50, test_bu_sayfada_dizini_node_ile); metin içi atıflar yeni numaralarla."""
    from veto_atlasi import metodoloji
    for md in ("METODOLOJI.md", "METODOLOJI_EN.md"):
        metin = (KOK / md).read_text(encoding="utf-8")
        assert not re.search(r"^#+ \d+[a-z]\.", metin, re.M), md
        assert not re.search(r"\b2[a-i]\b", metin), md
        nolar = [n for n, _ in metodoloji.bolumler(metin)]
        assert nolar == ["1", "2"] + [f"2.{i}" for i in range(1, 11)] + ["3", "4", "5", "6"], (md, nolar)
    sayfa = oku("metodoloji.html")
    assert '<h3 id="bolum-2-1">2.1. Erken dönem kayıtları (1946–1953)</h3>' in sayfa
    assert '<h3 id="bolum-2-8">2.8. Reform modelleri</h3>' in sayfa and '<h3 id="en-bolum-2-8">2.8. Reform models</h3>' in sayfa
    assert 'class="icindekiler"' not in sayfa and sayfa.count('<div class="metin-dizin"></div>') == 2  # dizin web/metin.js'ten
    assert "Kayıt kimlikleri 2.3'teki Kural 2 gereği" in (KOK / "METODOLOJI.md").read_text(encoding="utf-8")


def metin_sayfasi(sayfa, dil):
    """Metin sayfasında dilin <main> öğesinin içi ve okuma metnindeki kimlikli başlıklar: (kimlik, düzey, görünen metin)."""
    m = re.search(rf'<main class="[^"]*metin-duzen[^"]*" lang="{dil}"[^>]*>(.*?)</main>', sayfa, re.S)
    basliklar = [(k, int(d), html.unescape(re.sub(r"<[^>]+>", "", t))) for d, k, t in re.findall(r'<h([23]) id="([\w-]+)">(.*?)</h\1>', m[1])]
    return m[1], basliklar


HAKKINDA_BOLUMLERI = {
    "tr": ["Kaynaklar", "Nasıl sayıyoruz", "Tarih kuralı", "Konular ve Türkçe başlıklar", "Genel Kurul tartışmaları",
           "Nedensellik dili", "Düzeltme ve doğrulama", "Bilinen sınırlar", "İletişim"],
    "en": ["Sources", "How we count", "Date rule", "Topics and agenda items", "General Assembly debates",
           "Language of causation", "Corrections and verification", "Known limitations", "Contact"],
}


def test_metin_sayfasi_yapisi():
    """ADIM 50: Hakkında ve Metodoloji metin sayfası düzeninde. Her dilin <main> öğesinde başlık, hemen altında "Bu sayfada"
    dizininin yeri (web/metin.js doldurur) ve okuma metni. Okuma metnindeki her bölüm başlığı kimlikli; İngilizce kimlikler
    Türkçenin "en-" önekli eşi. Statik içindekiler kutusu yok."""
    for ad in ("hakkinda.html", "metodoloji.html"):
        s = oku(ad)
        assert s.count('<script src="metin.js"></script>') == 1, ad
        assert s.index('<script src="cubuk.js"></script>') < s.index('<script src="metin.js"></script>') < s.index("<style>"), ad
        assert 'class="icindekiler"' not in s, ad
        kimlikler = {}
        for dil in ("tr", "en"):
            ic, basliklar = metin_sayfasi(s, dil)
            assert re.match(r'\s*<h1>[^<]+</h1>\n    <div class="metin-dizin"></div>\n    <div class="metin">\n', ic), (ad, dil)
            assert ic.rstrip().endswith("</div>") and "<h2>" not in ic and "<h3>" not in ic, (ad, dil)
            kimlikler[dil] = [k for k, _, _ in basliklar]
            assert len(set(kimlikler[dil])) == len(kimlikler[dil]), (ad, dil)
        assert kimlikler["en"] == ["en-" + k for k in kimlikler["tr"]], ad
    for dil in ("tr", "en"):
        _, basliklar = metin_sayfasi(oku("hakkinda.html"), dil)
        assert [(d, m) for _, d, m in basliklar] == [(2, m) for m in HAKKINDA_BOLUMLERI[dil]], dil


METIN_BETIGI = r"""
const M = require(process.argv[2] + "/web/metin.js");
const girdi = JSON.parse(require("fs").readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(girdi.map((b) => M.listeYap(b))));
"""


def test_bu_sayfada_dizini_node_ile(tmp_path):
    """ADIM 50: web/metin.js'in dizin listesi sayfalardaki başlıklarla Node'da üretilir ve bağımsız yazımla karşılaştırılır:
    h2 maddeleri sırayla, h3'ler bir önceki h2'nin altında iç içe (Metodoloji'de 2.1–2.10 "2. Sayım kuralları"nın altında)."""
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js kurulu değil; dizin üreticisi doğrudan çalıştırılamadı (sayfa yapısı yine denetlendi)")
    kac = lambda x: x.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")  # noqa: E731
    girdiler, beklenen = [], []
    for ad in ("hakkinda.html", "metodoloji.html"):
        for dil in ("tr", "en"):
            _, basliklar = metin_sayfasi(oku(ad), dil)
            girdiler.append([{"id": k, "metin": m, "duzey": d} for k, d, m in basliklar])
            maddeler = []
            for k, d, m in basliklar:
                bag = f'<a href="#{kac(k)}">{kac(m)}</a>'
                if d == 3 and maddeler:
                    maddeler[-1][1].append(bag)
                else:
                    maddeler.append((bag, []))
            beklenen.append("<ul>" + "".join(f"<li>{b}" + ("<ul>" + "".join(f"<li>{a}</li>" for a in alt) + "</ul>" if alt else "") + "</li>"
                                             for b, alt in maddeler) + "</ul>")
    betik = tmp_path / "dizin.js"
    betik.write_text(METIN_BETIGI, encoding="utf-8")
    r = subprocess.run([node, str(betik), str(KOK)], input=json.dumps(girdiler), capture_output=True, text=True, encoding="utf-8", check=True)
    cikti = json.loads(r.stdout)
    assert cikti == beklenen
    hakkinda_tr, _, metodoloji_tr, metodoloji_en = cikti
    assert hakkinda_tr.count("<li>") == 9 and "<ul>" not in hakkinda_tr[4:]  # Hakkında: dokuz bölüm, alt bölüm yok
    assert '<li><a href="#bolum-2">2. Sayım kuralları</a><ul><li><a href="#bolum-2-1">2.1. Erken dönem kayıtları (1946–1953)</a></li>' in metodoloji_tr
    assert '<li><a href="#bolum-2-10">2.10. &quot;Ya veto olmasaydı?&quot; sayfası</a></li></ul></li><li><a href="#bolum-3">' in metodoloji_tr
    assert '<li><a href="#en-bolum-5">5. The vetoing party&#39;s reasons</a></li>' in metodoloji_en


def test_bu_sayfada_tek_dosyada_ve_kilavuzda():
    """ADIM 50: dizin betiği tek dosyaya gömülür (iki metin sayfası); alt alta dizilen "Nasıl yaptık?" sekmesinde çerçeve
    kendisi kaymadığı için üst belge kaydırma konumunu ve görünen yüksekliği çerçevelere bildirir: kaydırınca, yükseklik
    değişince, pencere boyutu değişince ve sekme yeniden açılınca. Kılavuzda "Metin sayfası" düzeni."""
    t = (KOK / "veto_atlasi/tek_dosya.py").read_text(encoding="utf-8")
    assert "if '<script src=\"metin.js\"></script>' in s:" in t and '"</script" not in metin_js' in t
    assert 'f.contentWindow.postMessage({{ tur: "gorunum", ust: yigin.scrollTop - f.offsetTop, h: yigin.clientHeight }}, "*")' in t
    assert "hedef = null; gorunumIste(yigin); }}" in t and "hedefeKaydir(); gorunumIste(f.parentElement); }}" in t
    assert 'if (el.classList.contains("yigin")) gorunumIste(el);' in t
    assert 'addEventListener("resize", () => document.querySelectorAll("#alan > .yigin").forEach(gorunumIste));' in t
    assert oku("veto-atlasi-tek-dosya.html").count("kok.VetoMetin = api;") == 2
    m = oku("metin.js")
    assert 'if (m.tur !== "gorunum") return;' in m and 'var YAZI = { tr: "Bu sayfada", en: "On this page" };' in m
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "**Metin sayfası.**" in kilavuz and "`--olcu-metin: 68ch`" in kilavuz and '"Bu sayfada"' in kilavuz
    # 68ch, "0" rakamının genişliği: 18 px Source Sans 3'te satır başına yaklaşık 70–80 karakter (tarayıcıda ölçüldü)
    assert "satır başına yaklaşık 70–80 karakter" in kilavuz and "en fazla 68 karakter" not in kilavuz


def test_vetolar_kapali_oturum_etiketi_kaynaga_uygun():
    """ADIM 46: iki kapalı oturum kaydında (1953 SSCB, 1996 ABD) etiket kaynağın ifadesiyle. DHL listesi "Not identified in
    private meeting communiqué, but attributed to …" der; "sonradan kabul etti" kaynakta yoktur."""
    s = oku("vetolar.html")
    assert '"kapaliSatir": ({ uyeler }) => `Resmî bildiride adı yok; DHL listesine göre ${uyeler}`,' in s
    assert '"kapaliSatir": ({ uyeler }) => `Not named in the official communiqué; attributed to ${uyeler} by the DHL list`,' in s
    assert 'uyeBelirli = (u) => (DIL === "en" && CUMLE_EN.kisa[u]) || uyeKisa(u);' in s and 't("kapaliSatir", { uyeler: k.uyeler.map(uyeBelirli).join(", ") })' in s
    assert 'kisa: { SSCB: "the USSR", USA: "the US", GBR: "the UK" } };' in s  # İngilizcede "attributed to the US"
    assert "kabul etti" not in s and "acknowledged" not in s
    # Etiket bir cümle: kırılabilir (üye adları kırılmaz), en fazla 320 px; 390 px'te yatay taşma yapmaz (tarayıcıda ölçüldü)
    assert '`<span class="uye-ad kapali-ad">${esc(t("kapaliSatir",' in s and ".uye-ad.kapali-ad { white-space: normal; max-width: 320px; }" in s
    v = (KOK / "web/veri.js").read_text(encoding="utf-8")
    K = json.loads(v[v.index("{"):v.rstrip().rindex(";")])["kayitlar"]
    assert sorted((k["id"], k["uyeler"]) for k in K if k["kapali"]) == [("V-1953-03-13-1", ["SSCB"]), ("V-1996-11-19-1", ["USA"])]
    for k in K:
        if k["kapali"]:
            assert any("kaynak tarafından atfedilmiş" in n["tr"] for n in k["notlar"]), k["id"]
