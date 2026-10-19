"""
Hikâye sayfası (web/hikaye.html): yedi adım, sayılar veri setinden canlı (sabit yazılı değil), görseller mevcut
bileşenlerden, her adımda ayrıntı bağlantısı, hareket azaltma tercihi; giriş sayfası (index.html) hikâyeye yönlendirir.
"""
import json
import re
import shutil
import subprocess

import pytest

from conftest import KOK
from veto_atlasi import alinti as A

SAYFA = (KOK / "web/hikaye.html").read_text(encoding="utf-8")
BETIK = SAYFA[SAYFA.index("<script>"):]


def test_sayilar_sabit_yazili_degil():
    # 266, 322, 55, 264, 22, 157, 94, 30, 23, 18 ve yüzdeler betikte sabit geçmez; hepsi veri setinden hesaplanır
    for n in ("266", "322", "55", "264", "157", "94", "30", "23", "18", "57,8", "58", "20"):
        assert not re.search(rf"(?<![\w.-]){n}(?![\w.-])", BETIK), n
    assert 'src="veri.js"' in SAYFA and 'src="temsil_veri.js"' in SAYFA and "window.VETO_VERISI" in BETIK and "window.TEMSIL_VERISI" in BETIK


def test_yedi_adim_ve_baglantilar():
    assert BETIK.count('.metin"') >= 7 and all(f'"{i}.metin"' in BETIK for i in range(1, 8))
    for hedef in ("metodoloji.html", "vetolar.html", "vizyon.html#h-konu", "vizyon.html#h-galeri", "temsil.html", "vizyon.html#h-cizelge", "simulasyon.html"):
        assert hedef in BETIK, hedef
    # Kapanış: 2026 hitabı alıntısı alıntı bankasından (kimlikle), yorum cümlesi yok
    assert '"2025-1"' in BETIK and "Veriyi keşfet" in BETIK and "Explore the data" in BETIK
    # Her adımın altında alıntı bankasından söz: 1→2019-1, 2→2023-1, 3→2024-1, 4→2026-1, 5→2023-2, 6→2022-1, 7→kitap-4
    assert 'const SOZLER = ["2019-1", "2023-1", "2024-1", "2026-1", "2023-2", "2022-1", "kitap-4"];' in BETIK
    assert "Sunuş" not in SAYFA and "Foreword" not in SAYFA and 'EPIGRAF = { tr: ["2019-1", "“Dünya 5’ten Büyüktür.”"], en: ["2019-1", "The world is bigger than five!"] }[DIL];' in BETIK
    assert not re.search(r"müttefik|korumak için|adalet|haks[ıi]z", SAYFA, re.I)
    assert "prefers-reduced-motion" in SAYFA and "IntersectionObserver" in BETIK


def test_metinler_veri_setiyle_tutarli():
    """Sayfadaki şablonlar veri setinin bugünkü değerleriyle doldurulduğunda ADIM 33 metnini verir."""
    s = (KOK / "web/veri.js").read_text(encoding="utf-8")
    V = json.loads(s[s.index("{"):s.rstrip().rindex(";")])
    K = V["kayitlar"]
    acik = [k for k in K if not k["kapali"]]
    uye = {}
    for k in acik:
        for u in k["uyeler"]:
            uye[u] = uye.get(u, 0) + 1
    assert len(K) == 266 and uye["SSCB"] + uye["RUS"] == 157 and uye["USA"] == 94 and uye["GBR"] == 30 and uye["CHN"] == 23 and uye["FRA"] == 18
    boyut = lambda k: 11 if k["tarih"] < "1966-01-01" else 15
    assert sum(1 for k in K if k["oy"] and k["oy"]["aleyhte"] == 1 and k["oy"]["lehte"] + 1 == boyut(k)) == 55
    G = [k for k in K if k["tarih"] >= "2022-04-26"]
    assert len(G) == 22 == sum(1 for k in G if k.get("gk") and k["gk"]["durum"] == "yapildi")
    assert sum(1 for k in acik if k["oy"] and k["oy"]["lehte"] >= (9 if boyut(k) == 15 else 7)) == 264
    T = json.loads((KOK / "data/processed/temsil.json").read_text(encoding="utf-8"))
    g = {x["kod"]: x for x in T["gruplar"]}
    assert round(100 * g["ASP"]["paylar"]["nufus_2023"]) == 58 and round(100 * g["ASP"]["koltuk"]["toplam_payi"]) == 20
    assert g["AFR"]["uye_sayisi"] == 54 and g["AFR"]["koltuk"]["daimi"] == 0


def test_giris_sayfasi_hikayeye_yonlendirir():
    s = (KOK / "web/index.html").read_text(encoding="utf-8")
    assert 'url=hikaye.html' in s and 'href="hikaye.html"' in s
    assert (KOK / "web/vetolar.html").exists()
    # Sayfalar arası gezinme ortak çubukta (web/cubuk.js): atlas vetolar.html'dir, index.html'e bağlantı yok
    cubuk = (KOK / "web/cubuk.js").read_text(encoding="utf-8")
    assert '["vetolar", "Vetolar", "Vetoes"]' in cubuk and "index.html" not in cubuk
    for ad in ("vizyon.html", "simulasyon.html", "temsil.html", "hakkinda.html", "metodoloji.html"):
        t = (KOK / "web" / ad).read_text(encoding="utf-8")
        assert '<script src="cubuk.js"></script>' in t and 'href="index.html"' not in t, ad


def test_sadelestirme():
    atlas = (KOK / "web/vetolar.html").read_text(encoding="utf-8")
    assert '<details class="filtre"' in atlas and 'id="arama"' in atlas and '<header id="cubuk" class="cubuk"></header>' in atlas
    assert 'class="oy-kisa"' not in atlas and "const et = etiketler(k);" in atlas
    for ad in ("vizyon.html", "temsil.html"):
        t = (KOK / "web" / ad).read_text(encoding="utf-8")
        assert 'class="tablo-ac"' in t and "tabloGoster" in t, ad
    # Jargon: ilk görünen yerde düz karşılık
    assert "evet (lehte)" in atlas and "Kısmi veto (metnin yalnızca bir bölümü" in atlas
    assert "Evet (lehte)" in (KOK / "web/simulasyon.html").read_text(encoding="utf-8")


def test_adim_tasarimi_taslaktaki_gibi():
    """ADIM 37: kaynaklar/kimlik/hikaye-taslak.html düzeni (web/temel.css'teki 4 px ızgarası ve dört yazı boyutuyla;
    ADIM 41'den beri üst yazı büyük harfsiz); adım başlıkları; ilerleme rayı; erişilebilirlik."""
    for kural in (".kap { max-width: 760px; margin: 0 auto; padding: 0 24px; }", ".giris { padding: 48px 0 24px;",
                  ".epigraf blockquote { margin: 0; font-family: var(--serif); font-weight: 600; font-size: var(--yz-baslik); line-height: var(--sa-baslik);",
                  ".giris h1 { font-family: var(--serif); font-weight: 600; font-size: var(--yz-gosterge); line-height: var(--sa-gosterge);",
                  ".adim { padding: 64px 0 48px; border-top: 1px solid var(--cizgi); }", ".adim-bas { display: flex; align-items: baseline; gap: 16px; margin-bottom: 32px; }",
                  ".adim-no { font-family: var(--serif); font-weight: 600; font-size: var(--yz-baslik);", ".adim-baslik { font-family: var(--serif); font-weight: 600; font-size: var(--yz-govde);",
                  ".istat { font-family: var(--serif); font-weight: 600; font-size: var(--yz-gosterge); line-height: var(--sa-gosterge);",
                  ".metin { font-family: var(--serif); font-size: var(--yz-govde); line-height: var(--sa-govde); max-width: var(--olcu); margin: 0 0 32px; }",
                  ".alinti { border-left: 3px solid var(--murekkep); padding: 8px 0 8px 24px; margin: 0 0 24px; }",
                  ".ray { position: fixed; left: 24px; top: 50%;", ".kareler { display: grid; grid-template-columns: repeat(23, 1fr); gap: 4px; max-width: 560px; }",
                  "@media (max-width: 760px) {\n  .giris { padding-top: 32px; }\n  .ray { display: none; }", "@media (prefers-reduced-motion: reduce) {"):
        assert kural in SAYFA, kural
    assert 'basliklar: ["Veto nedir?", "Kaç karar düştü?", "Kim kullandı?", "Tek ülke, bütün Konsey", "Kim temsil ediliyor?", "Her vetodan sonra Genel Kurul", "Ya veto olmasaydı?"]' in BETIK
    assert 'basliklar: ["What is the veto?", "How many decisions failed?", "Who used it?", "One country, the whole Council", "Who is represented?", "After every veto, the General Assembly", "What if there were no veto?"]' in BETIK
    # Bölüm başlıkları (h2) ile gezilebilir; ray bağlantıları adlandırılmış, etkin adım aria-current; aşağı işareti ilk adımdan sonra gizli
    assert '<h2 class="adim-baslik" id="adim-${i + 1}-baslik">' in BETIK and 'aria-labelledby="adim-${i + 1}-baslik" tabindex="-1"' in BETIK
    assert 'a.setAttribute("aria-current", "step")' in BETIK and 'if (i >= 0 && kaydirma) asagi.classList.add("gecti");' in BETIK
    assert 'behavior: azHareket ? "auto" : "smooth"' in BETIK and '"14 evet · 1 hayır → düştü"' in BETIK
    # Taslaktaki yerel OTF yazı tipleri değil, sitenin woff2 dosyaları
    assert ".otf" not in SAYFA and 'href="fonts/fonts.css"' in SAYFA


def test_kucuk_kararlar_adim38():
    # 7. adım metni başlığı tekrar etmez (ADIM 47 metni: tests/test_hikaye.py::test_hikaye_metinleri_node_ile)
    assert "Ya veto olmasaydı? Veto" not in BETIK and "What if there were no veto? ${n}" not in BETIK
    # Sunuş kaldırıldı (yayın hazırlığı): başlık ve özetten sonra doğrudan 1. adım; kutunun kodu KILAVUZ bölüm 6'da
    assert "sunus" not in SAYFA and "[İmza" not in SAYFA and "[Signature" not in SAYFA
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "**Sunuş kutusu (kaldırıldı).**" in kilavuz and '<details class="sunus">' in kilavuz and ".sunus summary { list-style: none;" in kilavuz
    # Tasarım referansı depoda; yerel OTF yolları kılavuzda not edilmiş
    taslak = (KOK / "kaynaklar/kimlik/hikaye-taslak.html").read_text(encoding="utf-8")
    assert "SourceSerif4-Regular.otf" in taslak
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "hikaye-taslak.html" in kilavuz and "SourceSerif4-Regular.otf" in kilavuz


def test_giris_sikilastirma_adim40():
    assert ".giris { padding: 48px 0 24px; text-align: left; }" in SAYFA and "@media (max-width: 760px) {\n  .giris { padding-top: 32px; }" in SAYFA
    # "Kaydırarak ilerleyin" girişin hemen altında, ilk adımdan önce
    govde = SAYFA[SAYFA.index("<body"):]
    assert '  </header>\n  <p class="asagi" id="asagi"' in govde
    assert govde.index('<header class="giris">') < govde.index('<p class="asagi" id="asagi"') < govde.index('<main id="adimlar">')


def test_alt_bilgi_ve_giris_adim45():
    """Alt bilgide yalnızca veri tarihi (veri sürümünden); kaynaklar ve yöntem "Nasıl yaptık?"ta. Girişteki "Sayılar sayfa
    açılırken …" notu ve alt bilgideki slogan yok. Kapanıştaki sayfa listesinde Reform modelleri (çubuktaki sırayla)."""
    assert "alt: ({ tarih }) => `Veri tarihi: ${tarih}.`," in BETIK and "alt: ({ tarih }) => `Data as of ${tarih}.`," in BETIK
    assert '$("#alt").innerHTML = t("alt", { tarih: veriTarihi });' in BETIK
    assert "tarihUzun(V.meta.veri_surumu)" in BETIK and "web/veri.js ve web/temsil_veri.js dosyalarından" not in BETIK
    for eski in ('data-t="not"', "sayfa açılırken", "when the page opens", "veri setinden hesaplanır", "computed from the atlas dataset", "Metodoloji</a>"):
        assert eski not in SAYFA, eski
    assert 'const SAYFALAR = ["vetolar", "vizyon", "reform", "simulasyon", "temsil", "hakkinda", "metodoloji"];' in BETIK
    assert 'reform: "Reform modelleri"' in BETIK and 'reform: "Reform models"' in BETIK
    # Listede sayfaların kendi adları: "Nasıl yaptık?" yerine Hakkında ve Metodoloji (çubuktaki sekme adı değişmez)
    assert 'hakkinda: "Hakkında", metodoloji: "Metodoloji" },' in BETIK and 'hakkinda: "About", metodoloji: "Methodology" },' in BETIK
    cubuk = (KOK / "web/cubuk.js").read_text(encoding="utf-8")
    assert '["hakkinda", "Nasıl yaptık?", "How we did it"],' in cubuk


def test_belirme_animasyonu_adim42():
    """En fazla 300 ms; bir kez görünen adım bir daha solmaz; eşik 0 ve hızlı kaydırmada geçilen adımlar da görünür."""
    kural = re.search(r"\.adim > \* \{[^}]*\}", SAYFA)[0]
    sureler = re.findall(r"([\d.]+)(m?s)\b", kural[kural.index("transition"):])
    assert sureler and all((float(n) if b == "ms" else 1000 * float(n)) <= 300 for n, b in sureler), kural
    assert "{ threshold: 0 }" in BETIK and "threshold: 0.15" not in BETIK
    assert 'e.getBoundingClientRect().top < innerHeight) { goster(e); io.unobserve(e); }' in BETIK
    assert 'addEventListener("scroll", gecilenler, { passive: true });' in BETIK
    assert not re.search(r"classList\.(remove|toggle)\(\"goster\"", BETIK)  # gösterilen adım geri alınmaz


def test_kisaltilmis_alinti_adim42():
    """7. adımda kitap alıntısı atlama işaretiyle kısaltılır; her parça alıntı bankasındaki tam metinde sırasıyla geçer
    (kaynakta parça parça doğrulama: tests/test_alintilar.py). Alıntı bankasında tam metin kalır."""
    kisa = json.loads(re.search(r"const KISA = (\{.*?\});", BETIK)[1])
    banka = {a["id"]: a for a in A.oku(KOK / "kaynaklar/alintilar.csv")}
    assert set(kisa) == {"kitap-4"} and "kitap-4" == re.search(r'const SOZLER = \[(.*?)\];', BETIK)[1].split(", ")[6].strip('"')
    for kimlik, metin in kisa.items():
        tam = banka[kimlik]["metin_tr"]
        assert A.ATLAMA in metin and A.ATLAMA not in tam and len(metin) < len(tam)
        assert A.yerlesimler(metin, tam) == [0], kimlik  # tam metnin başından, parçalar sırasıyla
        assert all(len(p.split()) >= 3 for p in A.parcalar(metin)), kimlik
    assert kisa["kitap-4"] == ("Reform ve yeniden yapılandırma konusunda bir teklif türünün başarılı olabilmesinin öncelikli "
                               "koşulu mevcut şekliyle daimî üyelik paradigmasının ve üyelerin … veto yetkilerini kaldırmaktır.")
    assert "${esc(ingilizce ? a.metin_en : (KISA[id] || a.metin_tr))}" in BETIK


def test_hikaye_metinleri_adim47():
    """ADIM 47: yedi adımın büyük sayısı, alt yazısı (italik) ve gövde metni. Metindeki sayılar (yazıyla yazılanlar ve ekleri
    dâhil) veriden gelir; nitel ifadeler ("tamamı", "yarısından fazlası", "neredeyse tamamı", "dışarıda kalan ikisi") verinin
    bugünkü değerleriyle sınanır. ADIM 46'nın olgusal düzeltmeleri korunur: veto usul işlerinde işlemez; Asya-Pasifik payı BM
    üyelerinin nüfusu içindedir; A/RES/76/262 Genel Kurul'u toplar ve görüşme ile söz alma sayıları veriden gelir."""
    assert (".istat-alt { font-size: var(--yz-kucuk); color: var(--murekkep-2); margin: 0 0 24px; line-height: var(--sa-kucuk); "
            "font-style: italic; }") in SAYFA
    assert 'const BUYUME = "1966-01-01", ESKI_BOYUT = 11, YENI_BOYUT = 15, GK_BAS = "2022-04-26", DAGILIM_YILI = 1963;' in BETIK
    for parca in ('t("1.metin", { uye: koltukSayisi, daimi: daimiSayisi })', 't("2.etiket", { yil: ilkYil })',
                  't("2.metin", { sure: sonYil - ilkYil })', "sayi: `${sayi(kullananKoltuk)} / ${sayi(daimiSayisi)}`",
                  't("4.metin", { n11: tek11, yil: BUYUME.slice(0, 4), boy: ESKI_BOYUT })',
                  't("5.metin", { yil: DAGILIM_YILI, koltuk: koltukSayisi, asp: ASP.koltuk.toplam, afr: AFR.uye_sayisi })',
                  't("6.etiket", { yil: +GK_BAS.slice(0, 4) })',
                  't("6.metin", { ay: AY[+GK_BAS.slice(5, 7) - 1], yil: +GK_BAS.slice(0, 4), v: vgTartismalar.length, s: vgSozAlinan.length })',
                  't("7.etiket", { t: sayi(K.length) })', 't("7.metin", { dis: K.length - vetosuz.length })',
                  'const kullananKoltuk = new Set(acik.flatMap((k) => k.uyeler.map((u) => (u === "RUS" ? "SSCB" : u)))).size;',
                  "const tek11 = tek.filter((k) => boyut(k) === ESKI_BOYUT).length;"):
        assert parca in BETIK, parca
    for eski in ("dünya nüfusunun yüzde", "diyerek her kararı", "Genel Kurul'un karşısına çıkıyor", "Hesap sorulmaya başlandı",
                 "Dünyanın değişen yüzü", "hesap veriyor", "answer for it", "Beşi de kullandı", "${n} kez diğer"):
        assert eski not in SAYFA, eski
    # Verinin bugünkü değerleri ve metindeki nitel ifadelerin dayanağı
    s = (KOK / "web/veri.js").read_text(encoding="utf-8")
    K = json.loads(s[s.index("{"):s.rstrip().rindex(";")])["kayitlar"]
    acik = [k for k in K if not k["kapali"]]
    boyut = lambda k: 11 if k["tarih"] < "1966-01-01" else 15
    tek = [k for k in K if k["oy"] and k["oy"]["aleyhte"] == 1 and k["oy"]["lehte"] + 1 == boyut(k)]
    vetosuz = [k for k in acik if k["oy"] and k["oy"]["lehte"] >= (9 if boyut(k) == 15 else 7)]
    yillar = [int(k["tarih"][:4]) for k in K]
    assert len({("SSCB" if u == "RUS" else u) for k in acik for u in k["uyeler"]}) == 5  # "beş daimî üyenin tamamı"
    assert (min(yillar), max(yillar) - min(yillar)) == (1946, 80)  # "1946'dan bugüne", "seksen yılın tamamı"
    assert (len(tek), sum(1 for k in tek if boyut(k) == 11)) == (55, 27)  # büyük sayı 55; "Yirmi yedisi"
    kapali = [k for k in K if k["kapali"]]
    assert len(K) - len(vetosuz) == len(kapali) == 2 and all(k["oy"] is None for k in kapali)  # "Dışarıda kalan ikisi … kapalı oturum"
    G = [k for k in K if k["tarih"] >= "2022-04-26"]
    gorusulen = [k for k in G if k.get("gk") and k["gk"]["durum"] == "yapildi"]
    vg = {x["id"]: x for k in gorusulen for x in k["gk"]["tartismalar"] if x["tur"] == "veto_girisimi" and x.get("konusmacilar")}
    soz = [x for x in vg.values() if all(d != "hayir" for d in x["konusmacilar"]["veto_eden_konustu"].values())]
    assert (len(G), len(gorusulen), len(vg), len(soz)) == (22, 22, 15, 15)  # "vetoların tamamı görüşüldü", "on beşinde de"
    T = json.loads((KOK / "data/processed/temsil.json").read_text(encoding="utf-8"))
    g = {x["kod"]: x for x in T["gruplar"]}
    assert g["ASP"]["paylar"]["nufus_2023"] > 0.5 and (g["ASP"]["koltuk"]["toplam"], T["meta"]["toplamlar"]["koltuk"]) == (3, 15)
    assert (g["AFR"]["uye_sayisi"], g["AFR"]["koltuk"]["daimi"]) == (54, 0) and 1963 in T["meta"]["nufus_yillari"]


BEKLENEN = {
    "tr": {
        "giris": "Güvenlik Konseyi'nde kim, kaç kez, neyi durdurdu? Yedi adımda, kayıtlarla.",
        "adimlar": [
            ["on beş üyeden beşi, daimî",
             "Güvenlik Konseyi on beş üyeden oluşur. Bunların beşi daimî üyedir ve diğerlerinde bulunmayan bir yetkiye sahiptir: tek bir ret "
             "oyuyla, usul işleri dışındaki her kararı düşürebilirler. Bu yetkinin adı vetodur."],
            ["karar, 1946'dan bugüne",
             "Konsey'in kuruluşundan bu yana daimî üyelerin ret oyuyla düşen karar taslaklarının toplamı budur. Aşağıdaki ızgarada her kare "
             "bir ret oyunu gösterir; seksen yılın tamamı tek bakışta görülür."],
            ["daimî üyelerin tamamı",
             "Veto, beş daimî üyenin tamamı tarafından kullanıldı. Dağılım dönemlere göre değişir: Soğuk Savaş'ın ilk yıllarında Sovyetler "
             "Birliği, 1970'lerden sonra ABD, son on beş yılda Rusya ve Çin öne çıkar."],
            ["karar, tek bir ret oyuyla",
             "Bu kararların her birinde Konsey'in diğer bütün üyeleri lehte oy kullandı; karar yine de düştü, çünkü ret oyunu veren tek ülke "
             "bir daimî üyeydi. Yirmi yedisi, 1966 öncesinin on bir üyeli Konseyi'nde oylandı."],
            ["Asya-Pasifik grubunun BM nüfusundaki payı",
             "Konsey'in bugünkü koltuk dağılımı 1963'te belirlendi ve o günden beri değişmedi; dünya nüfusu ise değişti. BM üyesi ülkelerin "
             "nüfusunun yarısından fazlasını barındıran Asya-Pasifik grubu on beş koltuğun üçüne sahip. Elli dört üyeli Afrika grubunun ise hiç "
             "daimî koltuğu yok."],
            ["veto, 2022'den bu yana Genel Kurul'da görüşüldü",
             "Nisan 2022'de kabul edilen ve Türkiye'nin ilk sunucuları arasında yer aldığı bir kararla, Genel Kurul artık her vetodan sonra "
             "toplanıyor. O tarihten bu yana kullanılan vetoların tamamı görüşüldü; veto eden ülke, on beş veto girişimi tartışmasının on "
             "beşinde de söz aldı."],
            ["karar, 266 içinde",
             "Veto olmasaydı ve üyeler kayıtlardaki oylarını değiştirmeseydi, düşen kararların neredeyse tamamı kabul edilmiş olurdu. Dışarıda "
             "kalan ikisi, oy dağılımı kayıtlı olmayan kapalı oturum vetolarıdır. Sayımı istediğiniz kayıt üzerinde kendiniz yapabilirsiniz."],
        ],
    },
    "en": {
        "giris": "Who stopped what in the Security Council, and how many times? In seven steps, from the records.",
        "adimlar": [
            ["five of the fifteen members, permanent",
             "The Security Council has fifteen members. Five of them are permanent members and hold a power the others lack: with a single "
             "negative vote, any one of them can defeat any decision other than a procedural one. This power is called the veto."],
            ["decisions, from 1946 to today",
             "This is the number of draft resolutions that have failed on the negative votes of permanent members since the Council was "
             "established. In the grid below, each square is one negative vote; all eighty years can be seen at a glance."],
            ["all of the permanent members",
             "All five permanent members have used the veto. The distribution changes from period to period: the Soviet Union stands out in "
             "the early years of the Cold War, the United States from the 1970s onwards, and Russia and China in the last fifteen years."],
            ["decisions, on a single negative vote",
             "In each of these cases, every other member of the Council voted in favour; the draft still failed, because the only country "
             "voting against was a permanent member. Twenty-seven of them were voted on in the eleven-member Council before 1966."],
            ["the Asia-Pacific Group's share of the population of UN Member States",
             "The Council's current distribution of seats was set in 1963 and has not changed since, while the world's population has. The "
             "Asia-Pacific Group, home to more than half of the population of UN Member States, holds three of the fifteen seats. The "
             "fifty-four-member African Group holds no permanent seat."],
            ["vetoes debated in the General Assembly since 2022",
             "Under a resolution adopted in April 2022, of which Türkiye was one of the original sponsors, the General Assembly now meets "
             "after every veto. Every veto cast since then has been debated; the vetoing country took the floor in fifteen of the fifteen "
             "veto initiative debates."],
            ["decisions, out of 266",
             "Had there been no veto, and had members kept the votes on record, almost all of the failed drafts would have been adopted. The "
             "two left out are private-meeting vetoes, for which no vote count is on record. You can run the count yourself on any record."],
        ],
    },
}

HIKAYE_BETIGI = r"""
const fs = require("fs");
const s = fs.readFileSync(process.argv[2] + "/web/hikaye.html", "utf8");
const parca = (bas, son) => { const i = s.indexOf(bas), j = s.indexOf(son, i); if (i < 0 || j < 0) throw new Error(bas); return s.slice(i, j); };
const yardimci = parca("  const BIRLER = ", "  const koltukSayisi");
const sozluk = parca("  const SOZLUK = {", "  const t = (a, p)");
const p = JSON.parse(fs.readFileSync(0, "utf8"));
const cikti = {};
for (const DIL of ["tr", "en"]) {
  const { SOZLUK, yazi, yaziEn, sayiEki } = new Function("DIL", yardimci + sozluk + "\nreturn { SOZLUK, yazi, yaziEn, sayiEki };")(DIL);
  const S = SOZLUK[DIL], f = (a, x) => (typeof S[a] === "function" ? S[a](x || {}) : S[a]);
  cikti[DIL] = { giris: S.giris1, adimlar: [
    [f("1.etiket", { uye: p.koltuk, daimi: p.daimi }), f("1.metin", { uye: p.koltuk, daimi: p.daimi })],
    [f("2.etiket", { yil: p.ilkYil }), f("2.metin", { sure: p.sure })],
    [f("3.etiket"), f("3.metin", { daimi: p.daimi })],
    [f("4.etiket"), f("4.metin", { n11: p.tek11, yil: p.buyume, boy: p.eski })],
    [f("5.etiket"), f("5.metin", { yil: p.dagilim, koltuk: p.koltuk, asp: p.asp, afr: p.afr })],
    [f("6.etiket", { yil: p.gkYil }), f("6.metin", { ay: p.ay[DIL], yil: p.gkYil, v: p.v, s: p.s })],
    [f("7.etiket", { t: p.n }), f("7.metin", { dis: p.dis })],
  ] };
  if (DIL === "tr") {
    cikti.ekler = Object.fromEntries([1, 2, 3, 4, 6, 9, 10, 13, 15, 20, 22, 40, 58, 60, 100, 1000].map((n) => [n, sayiEki(n)]));
    cikti.yilEkleri = [sayiEki(1946, "den"), sayiEki(1963, "de"), sayiEki(2022, "de"), sayiEki(1970, "den")];
    cikti.yazi = [yazi(4, "iyelik"), yazi(9, "bulunma"), yazi(6, "yonelme"), yazi(1946), yazi(2022, "iyelik")];
  } else {
    cikti.yaziEn = [yaziEn(21), yaziEn(100), yaziEn(115), yaziEn(1946), yaziEn(2022)];
  }
}
process.stdout.write(JSON.stringify(cikti));
"""


def test_baslik_tek_satir():
    """Türkçe başlık ("Yedi adımda veto", 96 px'te 776 px) 712 px'lik sütuna sığmaz; 960 px ve üstünde sütunun sağına taşarak
    tek satırda kalır (960 px'te sağ kenara 60 px kalır; tarayıcıda ölçüldü). Kural yalnızca Türkçe başlık içindir:
    İngilizce başlık (1038 px) bu genişliklerde sayfadan taşardı, sütunda iki satır kalır."""
    assert "@media (min-width: 960px) { .giris h1:lang(tr) { white-space: nowrap; } }" in SAYFA
    assert 'baslik: "Yedi adımda veto",' in BETIK and 'baslik: "The veto in seven steps",' in BETIK
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "Türkçe başlık 960 px ve üstünde tek satırdır" in kilavuz


def test_giris_alintisi_bankadan():
    """Öneri C: başlığın üstünde atlasın çıkış noktası kaynaklı bir alıntı olarak (taslaktaki üst yazının yerinde). İki dilde de
    2019 hitabından (2019-1): Türkçede Türkçe kitapçıktaki “Dünya 5’ten Büyüktür.”, İngilizcede İngilizce kitapçıktaki
    "The world is bigger than five!" (kaynakta tırnaksız). Gösterilen metin bankadaki doğrulanmış metnin içinde birebir geçer;
    künye bankanın tarih, etkinlik ve sayfa alanlarından. Eskiden İngilizce giriş alıntısı olan 2023-3 bankada durur; Söz ve
    Kayıt'ta ve Vetolar grafiğinde gösterilmez."""
    banka = {a["id"]: a for a in A.oku(KOK / "kaynaklar/alintilar.csv")}
    x = banka["2019-1"]
    assert "“Dünya 5’ten Büyüktür.”" in x["metin_tr"] and x["metin_en"].endswith("I say again: The world is bigger than five!")
    assert (x["kaynak_en"], x["basili_sayfa_en"], x["basili_sayfa"]) == ("Birlesmis_Milletler_EN_2019.pdf", "6", "6")
    assert banka["2023-3"]["iliskili_veri"] == "giris" and '"2023-3"' not in BETIK
    ids = list(banka)
    assert ids.index("2023-1") < ids.index("2023-3")  # Vetolar'daki hitap işareti 2023 için 2023-1'e bağlanır
    s = SAYFA
    assert '<figure class="epigraf" id="epigraf"></figure>' in s and "ustyazi" not in s and "altbaslik" not in s
    assert "if (epigraf && (DIL === \"en\" ? epigraf.metin_en : epigraf.metin_tr).includes(EPIGRAF[1])) {" in s
    # Künye bütün sayfalardaki tek biçimle (test_okunurluk.test_kunye_tek_bicim)
    assert "<figcaption>${kunye(epigraf)}</figcaption>" in s
    assert ".epigraf figcaption { margin: var(--b2) 0 0; font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); color: var(--murekkep-2); }" in s
    assert ".giris h1 { font-family: var(--serif); font-weight: 600; font-size: var(--yz-gosterge); line-height: var(--sa-gosterge);" in s
    for ad, kalip in (("vizyon.html", 'a.iliskili_veri !== "model" && a.iliskili_veri !== "giris")'),
                      ("vetolar.html", 'a.iliskili_veri !== "model" && a.iliskili_veri !== "giris" && ')):
        assert kalip in (KOK / "web" / ad).read_text(encoding="utf-8"), ad
    for md, cumle in (("METODOLOJI.md", 'İngilizcede İngilizce kitapçıktaki "The world is bigger than five!" cümlesi.'),
                      ("METODOLOJI_EN.md", 'in English, "The world is bigger than five!" from the English booklet.')):
        assert cumle in " ".join((KOK / md).read_text(encoding="utf-8").split()), md


def test_hikaye_metinleri_node_ile(tmp_path):
    """Sayfanın kendi sözlüğü ve sayı yardımcıları (Türkçe yazı ve ekler, İngilizce yazı) Node ile, veriden hesaplanan
    değerlerle çalıştırılır; iki dilde yedi adımın alt yazısı ve gövde metni beklenen metinle birebir aynıdır."""
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js kurulu değil; sözlük doğrudan çalıştırılamadı (çağrılar ve veri yine denetlendi)")
    s = (KOK / "web/veri.js").read_text(encoding="utf-8")
    K = json.loads(s[s.index("{"):s.rstrip().rindex(";")])["kayitlar"]
    acik = [k for k in K if not k["kapali"]]
    boyut = lambda k: 11 if k["tarih"] < "1966-01-01" else 15
    tek = [k for k in K if k["oy"] and k["oy"]["aleyhte"] == 1 and k["oy"]["lehte"] + 1 == boyut(k)]
    vetosuz = [k for k in acik if k["oy"] and k["oy"]["lehte"] >= (9 if boyut(k) == 15 else 7)]
    G = [k for k in K if k["tarih"] >= "2022-04-26" and k.get("gk") and k["gk"]["durum"] == "yapildi"]
    vg = {x["id"]: x for k in G for x in k["gk"]["tartismalar"] if x["tur"] == "veto_girisimi" and x.get("konusmacilar")}
    T = json.loads((KOK / "data/processed/temsil.json").read_text(encoding="utf-8"))
    g = {x["kod"]: x for x in T["gruplar"]}
    yillar = [int(k["tarih"][:4]) for k in K]
    girdi = {"koltuk": T["meta"]["toplamlar"]["koltuk"], "daimi": T["meta"]["toplamlar"]["daimi"], "ilkYil": min(yillar),
             "sure": max(yillar) - min(yillar), "n": str(len(K)), "tek": len(tek), "tek11": sum(1 for k in tek if boyut(k) == 11),
             "buyume": "1966", "eski": 11, "dagilim": 1963, "asp": g["ASP"]["koltuk"]["toplam"], "afr": g["AFR"]["uye_sayisi"],
             "gkYil": 2022, "ay": {"tr": "Nisan", "en": "April"}, "v": len(vg),
             "s": sum(1 for x in vg.values() if all(d != "hayir" for d in x["konusmacilar"]["veto_eden_konustu"].values())),
             "dis": len(K) - len(vetosuz)}
    betik = tmp_path / "hikaye.js"
    betik.write_text(HIKAYE_BETIGI, encoding="utf-8")
    r = subprocess.run([node, str(betik), str(KOK)], input=json.dumps(girdi), capture_output=True, text=True, encoding="utf-8", check=True)
    cikti = json.loads(r.stdout)
    for dil in ("tr", "en"):
        assert cikti[dil]["giris"] == BEKLENEN[dil]["giris"], dil
        for i, (gercek, beklenen) in enumerate(zip(cikti[dil]["adimlar"], BEKLENEN[dil]["adimlar"]), 1):
            assert gercek == beklenen, (dil, i)
    assert cikti["ekler"] == {"1": "i", "2": "si", "3": "ü", "4": "ü", "6": "sı", "9": "u", "10": "u", "13": "ü", "15": "i", "20": "si", "22": "si",
                              "40": "ı", "58": "i", "60": "ı", "100": "ü", "1000": "i"}
    assert cikti["yilEkleri"] == ["dan", "te", "de", "ten"]  # 1946'dan, 1963'te, 2022'de, 1970'ten
    assert cikti["yazi"] == ["dördü", "dokuzunda", "altısına", "bin dokuz yüz kırk altı", "iki bin yirmi ikisi"]
    assert cikti["yaziEn"] == ["twenty-one", "one hundred", "one hundred and fifteen", "one thousand nine hundred and forty-six", "two thousand and twenty-two"]


def test_ucuncu_adim_donemleri_veriyle_tutarli():
    """ADIM 47 (c): 3. adımdaki dönem ifadeleri veriyle sınanır; her dönemde en çok ret oyu kullanan üye veriden hesaplanır
    (kapalı oturum vetoları hariç). "Soğuk Savaş'ın ilk yıllarında Sovyetler Birliği": 1946–1959 ve 1946–1965;
    "1970'lerden sonra ABD": 1970–1991 ve 1970'ten son on beş yılın başına kadar; "son on beş yılda Rusya ve Çin": son veri yılı
    dâhil son on beş yılda en çok ret oyu kullanan iki üye."""
    s = (KOK / "web/veri.js").read_text(encoding="utf-8")
    K = [k for k in json.loads(s[s.index("{"):s.rstrip().rindex(";")])["kayitlar"] if not k["kapali"]]

    def sira(bas, son):
        c = {}
        for k in K:
            if bas <= int(k["tarih"][:4]) <= son:
                for u in k["uyeler"]:
                    c[u] = c.get(u, 0) + 1
        return sorted(c, key=lambda u: -c[u])

    son_yil = max(int(k["tarih"][:4]) for k in K)
    for bas, son in ((1946, 1959), (1946, 1965)):
        assert sira(bas, son)[0] == "SSCB", (bas, son, sira(bas, son))
    for bas, son in ((1970, 1991), (1970, son_yil - 15)):
        assert sira(bas, son)[0] == "USA", (bas, son, sira(bas, son))
    assert set(sira(son_yil - 14, son_yil)[:2]) == {"RUS", "CHN"}, sira(son_yil - 14, son_yil)
    assert "Soğuk Savaş'ın ilk yıllarında Sovyetler Birliği, 1970'lerden sonra ABD, son on beş yılda Rusya ve Çin öne çıkar." in BETIK
    assert ("the Soviet Union stands out in the early years of the Cold War, the United States from the 1970s onwards, and Russia and "
            "China in the last fifteen years.") in BETIK


def test_birinci_adim_koltuk_kodlari():
    """Daimî koltukta üyenin kısa kodu (Şart'ın 23. maddesindeki sıra; kodlar simülasyondakilerle aynı), veto karesi sol üstte,
    kodların açılımı diyagramın altında; üye listesi veriden (P5 kümesi). KILAVUZ "Hikâye", 1. adımın koltuk diyagramı."""
    h = (KOK / "web/hikaye.html").read_text(encoding="utf-8")
    s = (KOK / "web/simulasyon.html").read_text(encoding="utf-8")
    assert 'const SART_SIRASI = ["CHN", "FRA", "RUS", "GBR", "USA"], KOD = { CHN: "CN", FRA: "FR", RUS: "RU", GBR: "UK", USA: "US" };' in h
    kisa = dict(re.findall(r'(\w+): "(\w\w)"', re.search(r"const kisa = \{([^}]*)\}", s)[1]))
    kod = dict(re.findall(r'(\w+): "(\w\w)"', re.search(r"KOD = \{([^}]*)\}", h)[1]))
    assert kod and all(kisa[u] == k for u, k in kod.items())
    assert 'const p5 = new Set((T.kumeler.find((k) => k.kod === "P5")' in h
    assert ".konsey .koltuk.daimi::after { position: absolute; top: 8px; left: 8px; width: 8px; height: 8px; margin: 0; }" in h
    assert '<p class="koltuk-kodlari">' in h and "konsey: ({ n, daimi }) =>" in h
    assert ".koltuklar.konsey { display: grid; grid-template-columns: repeat(5, 40px); gap: 12px; }" in h  # dar ekranda beşerli
