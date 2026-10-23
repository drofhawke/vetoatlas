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
    assert 'gorsel: gkKareleri(), bag: "vizyon.html#h-cizelge" },' in BETIK and "tur=genel-kurul" not in BETIK
    # Kapanış: 2026 hitabı alıntısı alıntı bankasından (kimlikle), yorum cümlesi yok
    assert '"2025-1"' in BETIK and 'kesfet: "Bütün kayıtlar"' in BETIK and 'kesfet: "All records"' in BETIK
    # Her adımın altında alıntı bankasından söz: 1→2019-1, 2→2023-1, 3→2024-1, 4→2026-1, 5→2023-2, 6→2022-1, 7→kitap-4
    assert 'const SOZLER = ["2019-1", "2023-1", "2024-1", "2026-1", "2023-2", "2022-1", "kitap-4"];' in BETIK
    # Yedi adımın hepsinde alıntı gösterilir; adımın bağlantısı "Ayrıntı" / "Details", 7. adımda "Sayımı kendiniz yapın"
    # (21 Ekim 2026 kullanıcı kararı: adımlar yayındaki hâliyle; KILAVUZ "Hikâye, yedi adım")
    assert "      ${soz(SOZLER[i])}\n" in BETIK and "GOSTERILEN" not in BETIK and "sozBag" not in BETIK
    assert '<p class="ayrinti"><a href="${bagla(a.bag)}">${esc(a.bagMetni || t("ayrinti"))}</a></p>' in BETIK
    assert 'ayrinti: "Ayrıntı",' in BETIK and 'ayrinti: "Details",' in BETIK
    assert '"7.bag": "Sayımı kendiniz yapın",' in BETIK and '"7.bag": "Run the count yourself",' in BETIK
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
    # Parantez içi sözlük yok (20 Ekim 2026): "evet", "hayır", "Kısmi veto"
    assert "(lehte)" not in atlas and "(aleyhte)" not in atlas and '"etiket.kismi": "Kısmi veto"' in atlas
    assert "(lehte)" not in (KOK / "web/simulasyon.html").read_text(encoding="utf-8")


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
    # Bölüm başlıkları (h2) ile gezilebilir; ray bağlantıları adlandırılmış, etkin adım aria-current
    assert '<h2 class="adim-baslik" id="adim-${i + 1}-baslik">' in BETIK and 'aria-labelledby="adim-${i + 1}-baslik" tabindex="-1"' in BETIK
    assert 'a.setAttribute("aria-current", "step")' in BETIK
    assert 'behavior: azHareket ? "auto" : "smooth"' in BETIK and '"14 evet, 1 hayır → kabul edilmedi"' in BETIK
    # Taslaktaki yerel OTF yazı tipleri değil, sitenin woff2 dosyaları
    assert ".otf" not in SAYFA and 'href="fonts/fonts.css"' in SAYFA


def test_kucuk_kararlar_adim38():
    # 7. adım metni başlığı tekrar etmez (ADIM 47 metni: tests/test_hikaye.py::test_hikaye_metinleri_node_ile)
    assert "Ya veto olmasaydı? Veto" not in BETIK and "What if there were no veto? ${n}" not in BETIK
    # Sunuş kaldırıldı (yayın hazırlığı): başlık ve özetten sonra doğrudan 1. adım; kutunun kodu KILAVUZ bölüm 6'da
    assert "sunus" not in SAYFA and "[İmza" not in SAYFA and "[Signature" not in SAYFA
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "**Sunuş kutusu (sitede yok).**" in kilavuz and '<details class="sunus">' in kilavuz and ".sunus summary { list-style: none;" in kilavuz
    # Tasarım referansı depoda; yerel OTF yolları kılavuzda not edilmiş
    taslak = (KOK / "kaynaklar/kimlik/hikaye-taslak.html").read_text(encoding="utf-8")
    assert "SourceSerif4-Regular.otf" in taslak
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "hikaye-taslak.html" in kilavuz and "SourceSerif4-Regular.otf" in kilavuz


def test_giris_sikilastirma_adim40():
    assert ".giris { padding: 48px 0 24px; text-align: left; }" in SAYFA and "@media (max-width: 760px) {\n  .giris { padding-top: 32px; }" in SAYFA
    # Kaydırma ipucu yok (20 Ekim 2026): girişin hemen altında ilk adım
    govde = SAYFA[SAYFA.index("<body"):]
    assert "asagi" not in SAYFA and '      <p class="ozet" data-t="giris1"></p>\n    </div>\n    <div id="adimlar"></div>' in govde


def test_alt_bilgi_ve_giris_adim45():
    """Alt bilgide yalnızca son vetonun tarihi (kayıtlardan) ve veri tarihi (veri sürümünden); kaynaklar ve yöntem "Nasıl yaptık?"ta. Girişteki "Sayılar sayfa
    açılırken …" notu ve alt bilgideki slogan yok. Kapanıştaki sayfa listesinde Reform modelleri (çubuktaki sırayla)."""
    assert "alt: ({ son, sonEk, tarih, tarihEk }) => `Son veto ${son}’${sonEk} kullanılmış, veri ${tarih}’${tarihEk} güncellenmiştir.`," in BETIK
    assert "alt: ({ son, tarih }) => `The most recent veto was cast on ${son}; the data were last updated on ${tarih}.`," in BETIK
    assert 'const sonVeto = K.map((k) => k.tarih).sort().pop(), surum = V.meta.veri_surumu;' in BETIK
    assert ('t("alt", { son: zaman(sonVeto), sonEk: sayiEki(+sonVeto.slice(0, 4), "de"), tarih: zaman(surum), '
            'tarihEk: sayiEki(+surum.slice(0, 4), "de") })') in BETIK and "web/veri.js ve web/temsil_veri.js dosyalarından" not in BETIK
    for eski in ('data-t="not"', "sayfa açılırken", "when the page opens", "veri setinden hesaplanır", "computed from the atlas dataset", "Metodoloji</a>"):
        assert eski not in SAYFA, eski
    assert "sayfaListesi" not in BETIK and "sayfa-listesi" not in SAYFA  # sayfa listesi yok, üst çubuk yeter (20 Ekim 2026)
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
    (kaynakta parça parça doğrulama: tests/test_alintilar.py). Alıntı bankasında tam metin kalır. 3. istisna (21 Ekim 2026,
    kullanıcı kararı): İngilizce kısa biçim Türkçedeki yerden kısaltılır, iki dilde aynı parça; ikisi de tam metnin başından
    başlar, tek atlama işareti taşır. Öteki adımların alıntıları tam metindir."""
    kisa = json.loads(re.search(r"const KISA = (\{.*?\});", BETIK)[1])
    kisa_en = json.loads(re.search(r"const KISA_EN = (\{.*?\});", BETIK)[1])
    banka = {a["id"]: a for a in A.oku(KOK / "kaynaklar/alintilar.csv")}
    assert set(kisa) == set(kisa_en) == {"kitap-4"} and "kitap-4" == re.search(r'const SOZLER = \[(.*?)\];', BETIK)[1].split(", ")[6].strip('"')
    for kimlik in kisa:
        for metin, tam in ((kisa[kimlik], banka[kimlik]["metin_tr"]), (kisa_en[kimlik], banka[kimlik]["metin_en"])):
            assert metin.count(A.ATLAMA) == 1 and A.ATLAMA not in tam and len(metin) < len(tam)
            assert A.yerlesimler(metin, tam) == [0], kimlik  # tam metnin başından, parçalar sırasıyla
            assert all(len(p.split()) >= 3 for p in A.parcalar(metin)), kimlik
    assert kisa["kitap-4"] == ("Reform ve yeniden yapılandırma konusunda bir teklif türünün başarılı olabilmesinin öncelikli "
                               "koşulu mevcut şekliyle daimî üyelik paradigmasının ve üyelerin … veto yetkilerini kaldırmaktır.")
    assert kisa_en["kitap-4"] == ("To ensure that a reform and restructuring proposal will succeed, it is crucial to challenge the "
                                  "current approach to permanent membership and to abolish the veto powers of permanent members …")
    assert "${esc(ingilizce ? (KISA_EN[id] || a.metin_en) : (KISA[id] || a.metin_tr))}" in BETIK


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
                  't("3.metin", { daimi: daimiSayisi })',
                  't("4.metin", { n11: tek11, yil: BUYUME.slice(0, 4), boy: ESKI_BOYUT })',
                  't("5.metin", { yil: DAGILIM_YILI, koltuk: koltukSayisi, asp: ASP.koltuk.toplam, afr: AFR.uye_sayisi, kat: Math.round(AFR.paylar.nufus_2023 / AFR.paylar.nufus_1963) })',
                  't("6.etiket", { ay: AY[+GK_BAS.slice(5, 7) - 1], yil: +GK_BAS.slice(0, 4) })',
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
    assert "gkGruplari" not in BETIK and "ozelOturum" not in BETIK and "RUS_CIN_YILI" not in BETIK  # 6. adımda kareler gruplanmaz
    T = json.loads((KOK / "data/processed/temsil.json").read_text(encoding="utf-8"))
    g = {x["kod"]: x for x in T["gruplar"]}
    assert g["ASP"]["paylar"]["nufus_2023"] > 0.5 and (g["ASP"]["koltuk"]["toplam"], T["meta"]["toplamlar"]["koltuk"]) == (3, 15)
    assert (g["AFR"]["uye_sayisi"], g["AFR"]["koltuk"]["daimi"]) == (54, 0) and 1963 in T["meta"]["nufus_yillari"]
    # "Afrika grubunun payı iki katına çıktı" (1963'ten 2023'e, BM üyesi ülkelerin nüfusu içinde)
    assert round(g["AFR"]["paylar"]["nufus_2023"] / g["AFR"]["paylar"]["nufus_1963"]) == 2
    # 2. adımın ekran okuyucu metni: "322 ret oyu, her kare bir oy. Kesik çizgili iki kare …"
    assert sum(len(k["uyeler"]) for k in acik) == 322 and len(kapali) == 2


# Yedi adımın metni 23 Ekim 2026'dan beri resmî rapor dilinde (kullanıcı kararı; KILAVUZ "Hikâye, yedi adım"); site geneli yazım kuralları
# uygulanır (kıvrık kesme, kurum adlarına gelen ekler kesmesiz). Üç istisna: 5. adımda Afrika payı cümlesi, 6. adımın alt
# yazısında ay, 7. adımda iki dilde aynı kısa alıntı (test_kisaltilmis_alinti_adim42). Giriş cümlesi ayrı karardır (resmî rapor dili, 22 Ekim 2026).
BEKLENEN = {
    "tr": {
        "giris": "Bu sayfada, 1946’dan bu yana Güvenlik Konseyinde kullanılan vetolar BM kayıtlarına dayanılarak yedi adımda ele alınmaktadır.",
        "adimlar": [
            ["on beş üyeden beşi, daimî",
             "Birleşmiş Milletler Güvenlik Konseyi on beş üyeden oluşmakta olup bunların beşi daimî üye statüsündedir. Daimî üyeler, "
             "diğer üyelerde bulunmayan bir yetkiyle donatılmıştır: usule ilişkin olmayan herhangi bir karar, bu üyelerden yalnızca "
             "birinin ret oyuyla kabul edilememektedir. Söz konusu yetki veto olarak adlandırılmaktadır."],
            ["karar, 1946’dan bugüne",
             "Konseyin kuruluşundan bu yana daimî üyelerin ret oyuyla kabul edilemeyen karar taslaklarının toplamı bu sayıdır. Aşağıdaki "
             "ızgarada her kare bir ret oyunu göstermekte, seksen yıllık dönemin tamamı tek bakışta görülebilmektedir."],
            ["daimî üyelerin tamamı",
             "Veto, beş daimî üyenin tamamı tarafından kullanılmıştır. Dağılım dönemlere göre farklılık göstermektedir: Soğuk Savaş’ın ilk "
             "yıllarında Sovyetler Birliği, 1970’lerden itibaren ABD, son on beş yılda ise Rusya Federasyonu ve Çin öne çıkmaktadır."],
            ["karar, tek bir ret oyuyla",
             "Söz konusu kararların her birinde Konseyin diğer bütün üyeleri olumlu oy kullanmış, ancak ret oyunu veren tek ülkenin daimî "
             "üye olması nedeniyle karar kabul edilememiştir. Yirmi yedisi, 1966 öncesinde görev yapan on bir üyeli Konseyde oylanmıştır."],
            ["Asya-Pasifik grubunun BM nüfusundaki payı",
             "Konseyin bugünkü koltuk dağılımı 1963’te belirlenmiş ve o tarihten bu yana değişmemiştir. Aynı dönemde Afrika Grubunun BM "
             "üyesi ülkelerin nüfusundaki payı iki katına çıkmıştır. BM üyesi ülkelerin nüfusunun yarısından fazlasını barındıran "
             "Asya-Pasifik Grubu on beş koltuğun üçüne sahip bulunmakta, elli dört üyeli Afrika Grubu ise hiçbir daimî koltuğa sahip "
             "bulunmamaktadır."],
            ["veto, Nisan 2022’den bu yana Genel Kurulda görüşüldü",
             "Nisan 2022’de kabul edilen ve Türkiye’nin ilk sunucuları arasında yer aldığı bir karar uyarınca Genel Kurul, her vetonun "
             "ardından toplanmaktadır. O tarihten bu yana kullanılan vetoların tamamı Genel Kurulda görüşülmüş; vetoyu kullanan ülke, on "
             "beş veto girişimi tartışmasının on beşinde söz almıştır."],
            ["karar, 266 içinde",
             "Veto hakkının bulunmaması ve üyelerin kayıtlardaki oylarını korumuş olması hâlinde, kabul edilemeyen kararların neredeyse "
             "tamamı kabul edilmiş olacaktı. Kapsam dışında kalan ikisi, oy dağılımı kayıtlı olmayan kapalı oturum vetolarıdır. Sayım, "
             "istenen kayıt üzerinde yeniden yapılabilmektedir."],
        ],
    },
    "en": {
        "giris": ("Drawing on UN records, this page examines in seven steps the vetoes cast in the UN Security Council since 1946. "
                  "Its starting point is a statement made in 2019 by President Recep Tayyip Erdoğan of Türkiye."),
        "adimlar": [
            ["five of the fifteen members, permanent",
             "The United Nations Security Council is composed of fifteen members, five of which hold permanent seats. The permanent "
             "members are vested with a power that the other members do not possess: any decision on a non-procedural matter is "
             "defeated by the negative vote of a single permanent member. This power is referred to as the veto."],
            ["decisions, from 1946 to today",
             "This figure represents the total number of draft resolutions that have not been adopted owing to the negative votes of "
             "permanent members since the establishment of the Council. In the grid below, each square represents one negative vote, "
             "so that the entire period of eighty years may be viewed at a glance."],
            ["all of the permanent members",
             "The veto has been exercised by all five permanent members. Its distribution has varied from one period to another: the "
             "Soviet Union stands out in the early years of the Cold War, the United States from the 1970s onwards, and the Russian "
             "Federation and China over the past fifteen years."],
            ["decisions, on a single negative vote",
             "In each of these cases, all other members of the Council voted in favour; the draft was nevertheless not adopted, since "
             "the sole negative vote had been cast by a permanent member. Twenty-seven of these votes took place in the eleven-member "
             "Council of the period before 1966."],
            ["the Asia-Pacific Group’s share of the population of UN Member States",
             "The current distribution of seats in the Council was determined in 1963 and has remained unchanged since. Over the same "
             "period, the share of the African Group in the population of UN Member States has doubled. The Asia-Pacific Group, which "
             "accounts for more than half of the population of UN Member States, holds three of the fifteen seats, whereas the "
             "fifty-four-member African Group holds no permanent seat."],
            ["vetoes debated in the General Assembly since April 2022",
             "Pursuant to a resolution adopted in April 2022, of which Türkiye was one of the original sponsors, the General Assembly "
             "now convenes after every veto. All vetoes cast since that date have been debated; the vetoing member took the floor in "
             "fifteen of the fifteen veto initiative debates."],
            ["decisions, out of 266",
             "In the absence of the veto, and provided that members had maintained the votes on record, almost all of the drafts that "
             "were not adopted would have been adopted. The two excluded are private-meeting vetoes, for which no vote count is on "
             "record. The count may be repeated on any record."],
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
    [f("5.etiket"), f("5.metin", { yil: p.dagilim, koltuk: p.koltuk, asp: p.asp, afr: p.afr, kat: p.kat })],
    [f("6.etiket", { ay: p.ay[DIL], yil: p.gkYil }), f("6.metin", { ay: p.ay[DIL], yil: p.gkYil, v: p.v, s: p.s })],
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
    for md, cumle in (("METODOLOJI.md", 'İngilizcede İngilizce kitapçıktaki “The world is bigger than five!” cümlesi.'),
                      ("METODOLOJI_EN.md", 'in English, “The world is bigger than five!” from the English booklet.')):
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
    G = [k for k in K if k["tarih"] >= "2022-04-26"]
    assert all(k.get("gk") and k["gk"]["durum"] == "yapildi" for k in G)  # "vetonun tamamı görüşüldü"
    vg = {x["id"]: x for k in G for x in k["gk"]["tartismalar"] if x["tur"] == "veto_girisimi" and x.get("konusmacilar")}
    T = json.loads((KOK / "data/processed/temsil.json").read_text(encoding="utf-8"))
    g = {x["kod"]: x for x in T["gruplar"]}
    yillar = [int(k["tarih"][:4]) for k in K]
    girdi = {"koltuk": T["meta"]["toplamlar"]["koltuk"], "daimi": T["meta"]["toplamlar"]["daimi"], "ilkYil": min(yillar),
             "sure": max(yillar) - min(yillar), "n": str(len(K)), "tek": len(tek), "tek11": sum(1 for k in tek if boyut(k) == 11),
             "buyume": "1966", "eski": 11, "dagilim": 1963, "asp": g["ASP"]["koltuk"]["toplam"], "afr": g["AFR"]["uye_sayisi"],
             "gkYil": 2022, "ay": {"tr": "Nisan", "en": "April"}, "v": len(vg),
             "s": sum(1 for x in vg.values() if all(d != "hayir" for d in x["konusmacilar"]["veto_eden_konustu"].values())),
             "dis": len(K) - len(vetosuz), "kat": round(g["AFR"]["paylar"]["nufus_2023"] / g["AFR"]["paylar"]["nufus_1963"])}
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


def test_terim_istisnasi_yalniz_adim_metinlerinde():
    """KILAVUZ "Hikâye, yedi adım": terim kuralları ("öneri", "evet oyu") adım metinlerinde uygulanmaz; adımlar "karar" ve
    "lehte oy kullandı" der (21 Ekim 2026 kullanıcı kararı). İstisna dar: "karar" / "decisions" / "draft" yalnız yedi adımın
    başlıklarında, alt yazılarında ve paragraflarında; "lehte oy" yalnız 4. adımın paragrafında bir kez. Giriş, meta açıklama ve
    paylaşım görseli metni "öneri" / "proposals" der."""
    tr = BETIK[BETIK.index("    tr: {"):BETIK.index("    en: {")]
    en = BETIK[BETIK.index("    en: {"):BETIK.index("  const t = (a, p)")]
    ADIM_ANAHTARI = re.compile(r'^\s*(?:basliklar\b|"[1-7]\.(?:etiket|metin)")')
    for blok, terim in ((tr, r"\bkarar(?:ı|ın|lar\w*| taslak\w*)?\b|\blehte oy\b"), (en, r"\bdecisions?\b|\bdrafts?\b|\bvoted in favour\b")):
        for satir in blok.splitlines():
            if re.search(terim, satir) and not satir.lstrip().startswith("//"):
                assert ADIM_ANAHTARI.match(satir), satir.strip()[:120]
    assert len(re.findall(r"\blehte oy\b", SAYFA)) == 0  # 23 Ekim 2026: 4. adım da resmî dilde, "olumlu oy kullanmış"
    assert re.search(r'"4\.metin": \(\{ n11, yil, boy \}\) => `Söz konusu kararların her birinde Konseyin diğer bütün üyeleri olumlu oy kullanmış,', BETIK)
    # Adımların dışında terim "öneri" / "proposals"
    assert "veto nedeniyle kabul edilemeyen ${n} öneri" in tr and "${n} proposals not adopted owing to the veto" in en
    for ad in ("sayfaAciklamasi", "giris1", "kesfet"):
        satir = next(x for x in tr.splitlines() if x.strip().startswith(ad + ":"))
        assert "karar" not in satir, satir


def test_ucuncu_adim_donemleri_veriyle_tutarli():
    """ADIM 47 (c): 3. adımdaki dönem ifadeleri veriyle sınanır; her dönemde en çok ret oyu kullanan üye veriden hesaplanır
    (kapalı oturum vetoları hariç). "Soğuk Savaş’ın ilk yıllarında Sovyetler Birliği": 1946–1959 ve 1946–1965;
    "1970’lerden sonra ABD": 1970–1991 ve 1970’ten son on beş yılın başına kadar; "son on beş yılda Rusya ve Çin": son veri yılı
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
    assert "Soğuk Savaş’ın ilk yıllarında Sovyetler Birliği, 1970’lerden itibaren ABD, son on beş yılda ise Rusya Federasyonu ve Çin öne çıkmaktadır." in BETIK
    assert ("the Soviet Union stands out in the early years of the Cold War, the United States from the 1970s onwards, and the Russian "
            "Federation and China over the past fifteen years.") in BETIK


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


def test_kunye_tarihi_ve_parca_satiri():
    """KILAVUZ "Satır sonu": künye tarihinde gün, ay ve yıl bölünmez boşlukla birleşir (G-hikaye-1). 3. adımın görseli 21 Ekim
    2026'da yayındaki hâlinde: Sovyetler Birliği ve Rusya tek çubukta, iki renkli; çubuğun altında parça satırı yoktur."""
    s = (KOK / "web/hikaye.html").read_text(encoding="utf-8")
    assert 'const tarihUzun = (x) => { const [y, m, g] = x.split("-"); return `${+g}\u00a0${AY[+m - 1]}\u00a0${y}`; };' in s
    assert '[["sscbRus", ["SSCB", "RUS"]], ["USA", ["USA"]], ["GBR", ["GBR"]], ["CHN", ["CHN"]], ["FRA", ["FRA"]]]' in s
    assert '<div class="cb">${u.map((x) => `<span style="width:${(100 * (uyeSay[x] || 0) / enCok).toFixed(1)}%;background:${RENK[x]}"></span>`).join("")}</div>' in s
    assert ".parca" not in s and 'class="parca"' not in s
