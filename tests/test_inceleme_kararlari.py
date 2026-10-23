"""
İkinci incelemenin kararları (21 Ekim 2026; kaynaklar/kimlik/KILAVUZ.md): paylaşılabilir adresler (K5), Vetolar'da Genel Kurul
görünümü (K6), veto sayılmayan hayır oyları notu (K15), Hakkında'nın beş bölümü, indirme ve gizlilik satırları (K9, K10, K16,
K17) ve görünen metinde kıvrık kesme işareti ("Noktalama ve ses"). Sayfa davranışı tarayıcıda ayrıca denetlenir; burada
kaynak ve veri sınanır.
"""
import csv
import json
import re

from conftest import KOK

WEB = KOK / "web"


def oku(ad):
    return (WEB / ad).read_text(encoding="utf-8")


def kayitlar():
    s = oku("veri.js")
    return json.loads(s[s.index("{"):s.rstrip().rindex(";")])["kayitlar"]


# ---------- K5: paylaşılabilir adresler ----------

def test_vetolar_adresi_filtreleri_ve_acik_kaydi_tasir():
    """Filtreler ve açık kayıt adreste (?konu=&uye=&donem=&tur=&q=&yil=&kayit=); varsayılanlar yazılmaz, dil korunur; adresten
    gelen her değer doğrulanır (bilinmeyen konu, tür, dönem, üye ve biçimi bozuk kayıt kimliği yok sayılır). Paylaşılan kayıt
    filtrelerle gizleniyorsa filtreler bırakılır. Tek dosyada (about:srcdoc) adres yazılmaz."""
    v = oku("vetolar.html")
    assert 'const ADRES_PARAM = ["konu", "uye", "donem", "tur", "q", "yil", "kayit"];' in v
    assert r"const KAYIT_KIMLIGI = /^V-\d{4}-\d{2}-\d{2}-\d+$/;" in v
    assert 'ADRES_PARAM.forEach((p) => { if (deger[p]) u.searchParams.set(p, deger[p]); });' in v
    assert 'if (u.href !== location.href) history.replaceState(null, "", u);' in v and 'if (location.protocol === "about:") return;' in v
    for dogrulama in ('konu: KONULAR.includes(al("konu")) ? al("konu") : "",', 'tur: turlar.includes(al("tur")) ? al("tur") : "",',
                      r'yil: /^\d{4}$/.test(yil) && kayitlar.some((k) => k.tarih.startsWith(yil)) ? yil : null,',
                      'durum.uyeler = new Set(al("uye").split(",").filter((u) => UYELER[u]));',
                      'const id = KAYIT_KIMLIGI.test(al("kayit")) ? al("kayit")'):
        assert dogrulama in v, dogrulama
    assert "if (!kayitUyar(kayitById[id])) {" in v
    # Kayıt bağlantısı: yalnızca dil ve kayıt; tek dosyada yayın adresi
    assert 'const u = new URL(location.protocol === "about:" ? "https://vetoatlas.com/vetolar" : location.href);' in v
    assert 'if (DIL !== "tr") u.searchParams.set("lang", DIL);\n    u.searchParams.set("kayit", id);' in v
    # Biçim denetimi gerçek kimliklerin hepsini kabul eder
    assert all(re.fullmatch(r"V-\d{4}-\d{2}-\d{2}-\d+", k["id"]) for k in kayitlar())


def test_hikaye_adimi_adreste():
    h = oku("hikaye.html")
    assert 'try { history.replaceState(null, "", "#" + adimlar[i].id); } catch (_) {}' in h
    assert '<section class="adim" id="adim-${i + 1}"' in h


# ---------- K6: Vetolar'da Genel Kurul görünümü ----------

def test_vetolar_genel_kurul_gorunumu():
    """Kayıt türü "Genel Kurulda görüşülenler" (tur=genel-kurul): yalnızca Genel Kurulda görüşülen kayıtlar ve listenin
    üstünde her tartışmanın bir satır olduğu tablo (başlıklı, klavyeyle kaydırılabilir bölge). K20 (21 Ekim 2026, kullanıcı
    kararı): 520 px ve altında her tartışma bir blok, öteki blok tablolar gibi (değerin solunda sütun adı, sütun başlıkları
    ekran okuyucuya açık); masaüstünde tablo. Hikâye'nin 6. adımı Söz ve Kayıt'ın zaman çizelgesine bağlanır."""
    v = oku("vetolar.html")
    assert '<option value="genel-kurul" data-t="tur.gk"></option>' in v
    assert '"tur.gk": "Genel Kurulda görüşülenler",' in v and '"tur.gk": "Debated in the General Assembly",' in v
    assert '<div class="gk-tablo" id="gk-tablo" role="region" tabindex="0" hidden></div>' in v
    assert 'if (durum.tur === "genel-kurul") { if (!k.gk || k.gk.durum !== "yapildi") return false; }' in v
    assert 'gkKap.hidden = durum.tur !== "genel-kurul" || !uyan.length;' in v
    assert '`<table><caption>${t("gkt.baslik")}</caption>' in v and ".gk-tablo { overflow-x: auto;" in v
    assert '["vetoTarihi", "gundem", "vetoEden", "tarih", "konusan", "soz", "tutanak"]' in v
    assert 'bag: "vizyon.html#h-cizelge" }' in oku("hikaye.html") and "tur=genel-kurul" not in oku("hikaye.html")
    # K20: masaüstünde tablo (kendi kabında yatay kayar); 520 px ve altında blok düzeni
    assert ".gk-tablo table { border-collapse: collapse; width: 100%; min-width: 860px; }" in v
    dar = v[v.index("@media (max-width: 520px) {\n  .gk-tablo { overflow-x: visible; }"):]
    dar = dar[:dar.index("\n}\n")]
    for kural in (".gk-tablo table, .gk-tablo caption, .gk-tablo th, .gk-tablo td { display: block; }", ".gk-tablo table { min-width: 0; }",
                  ".gk-tablo thead { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%);",
                  ".gk-tablo tr { display: contents; }", ".gk-tablo td.gk-tt { order: 1; font-weight: 600;",
                  ".gk-tablo td[data-etiket] { display: grid; grid-template-columns: 10em minmax(0, 1fr);",
                  ".gk-tablo td[data-etiket]::before { content: attr(data-etiket);"):
        assert kural in dar, kural
    assert '<tbody role="rowgroup"><tr role="row"' in v and '<thead role="rowgroup">' in v and 'role="columnheader"' in v
    assert v.count('data-etiket="${esc(t("gkt.') == 6  # veto tarihi, gündem, veto eden, konuşan, söz, tutanak
    kilavuz = " ".join((KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8").split())
    assert "520 px ve altında, öteki blok tablolar gibi, her tartışma bir bloktur" in kilavuz
    # Veri: 26 Nisan 2022'den bu yana 22 veto, hepsi görüşüldü; tabloda 23 tartışma satırı
    K = kayitlar()
    G = [k for k in K if k.get("gk") and k["gk"]["durum"] == "yapildi"]
    assert len(G) == 22 and all(k["tarih"] >= "2022-04-26" for k in G)
    assert len([k for k in K if k["tarih"] >= "2022-04-26"]) == 22
    assert sum(len(k["gk"]["tartismalar"]) for k in G) == 23


# ---------- K15: veto sayılmayan hayır oyları ----------

def test_veto_sayilmayan_hayir_oylari_notu():
    """Aleyhte oy sayısı veto eden üye sayısından büyükse oy satırının altında tek cümle: öteki hayır oyları daimî olmayan
    üyelerindir, veto sayılmaz. Öteki hayır oyu tekse cümle tekildir. Bugünkü veride 88 kayıt (76'sında tek oy)."""
    v = oku("vetolar.html")
    assert '"oy.digerHayir": "Diğer hayır oyları daimî olmayan üyeler tarafından kullanılmış olup veto sayılmamaktadır.",' in v
    assert '"oy.digerHayir": "The other negative votes were cast by non-permanent members and do not constitute vetoes.",' in v
    assert '"oy.digerHayir1": "Diğer hayır oyu daimî olmayan bir üye tarafından kullanılmış olup veto sayılmamaktadır.",' in v
    assert '"oy.digerHayir1": "The other negative vote was cast by a non-permanent member and does not constitute a veto.",' in v
    assert ('${a > k.uyeler.length ? `\n      <p>${t(a - k.uyeler.length === 1 ? "oy.digerHayir1" : "oy.digerHayir")}</p>` : ""}'
            in v)
    K = kayitlar()
    assert sum(1 for k in K if k["oy"] and k["oy"]["aleyhte"] > len(k["uyeler"])) == 88
    assert sum(1 for k in K if k["oy"] and k["oy"]["aleyhte"] - len(k["uyeler"]) == 1) == 76
    # Bir kaydın hayır oyları veto eden üye sayısından az olamaz (veto eden üye aleyhte oy vermiştir)
    assert all(k["oy"]["aleyhte"] >= len(k["uyeler"]) for k in K if k["oy"])


# ---------- Hakkında (K9, K10, K16, K17) ----------

def test_hakkinda_indirme_sozluk_cevrimdisi_ve_gizlilik():
    h = oku("hakkinda.html")
    for dosya in ("vetolar.csv", "vetolar.xlsx", "vetolar.json", "genel_kurul_tartismalari.csv", "genel_kurul_tartismalari.xlsx", "veri_sozlugu.csv"):
        assert h.count(f'href="veri/{dosya}" download>') == 2, dosya  # iki dilde
        assert (WEB / "veri" / dosya).is_file(), dosya
    assert '<a href="veto-atlasi-tek-dosya.html">çevrimdışı sürüm</a>' in h and '<a href="veto-atlasi-tek-dosya.html?lang=en">offline version</a>' in h
    assert (WEB / "veto-atlasi-tek-dosya.html").is_file()
    assert "Sitede çerez ve ziyaretçi sayacı kullanılmamaktadır." in h and "No cookies or visitor tracking are used." in h
    # Kurallar Hakkında'da tek cümleyle Metodoloji'ye bağlanır
    assert 'Sayım, tarih, konu ve doğrulama kuralları <a href="metodoloji.html">Metodoloji</a> sayfasında numaralı bölümler hâlinde açıklanmaktadır.' in h
    assert '<dl class="terimler">' in h


# ---------- Kesme işareti ----------

DUZ_KESME = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşüâîû0-9)\]]'[A-Za-zÇĞİÖŞÜçğıöşüâîû]")


def yorumsuz(s):
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    return re.sub(r"(?m)(^|\s)//.*$", " ", s)


def test_kesme_kalibi_kendini_sinar():
    assert DUZ_KESME.search("Konsey'in") and DUZ_KESME.search("1946'dan") and DUZ_KESME.search("Council's")
    assert not DUZ_KESME.search("Konsey’in") and not DUZ_KESME.search("t('x')") and not DUZ_KESME.search("= 'tr'")


def test_gorunen_metinde_kesme_kivrik():
    """KILAVUZ "Noktalama ve ses": görünen metinde kesme kıvrık (’), iki dilde; kod, kimlik ve adreslerde düz kalır. Sayfalar
    (yorumlar hariç), Markdown belgeleri (kod parçaları hariç), görünen CSV sütunları ve paylaşım kartları denetlenir. BM'nin
    özgün adları (gundem_orijinal, ad_bm, ad_wpp gibi eşleştirme alanları) kaynaktaki gibi kalır ve denetlenmez."""
    for ad in ("hikaye", "vetolar", "vizyon", "reform", "simulasyon", "temsil", "hakkinda", "metodoloji", "404"):
        s = yorumsuz(oku(f"{ad}.html"))
        m = DUZ_KESME.search(s)
        assert not m, (ad, s[max(0, m.start() - 40):m.end() + 20])
    for md in ("METODOLOJI.md", "METODOLOJI_EN.md", "kaynaklar/kimlik/KILAVUZ.md"):
        s = re.sub(r"`[^`\n]*`", " ", re.sub(r"```.*?```", " ", (KOK / md).read_text(encoding="utf-8"), flags=re.S))
        m = DUZ_KESME.search(s)
        assert not m, (md, s[max(0, m.start() - 40):m.end() + 20])
    for yol, sutunlar in (("kaynaklar/gundem_sozlugu.csv", ["gundem_tr"]), ("kaynaklar/duzeltmeler.csv", ["aciklama", "aciklama_en"]),
                          ("kaynaklar/temsil/harita_kurallari.csv", ["gerekce_tr", "gerekce_en"]),
                          ("kaynaklar/temsil/bolgesel_gruplar.csv", ["not", "not_en"]), ("kaynaklar/notlar_en.csv", ["not", "not_en"]),
                          ("kaynaklar/reform_modelleri.csv", ["tr", "en", "dayanak"])):
        with open(KOK / yol, encoding="utf-8", newline="") as f:
            for satir in csv.DictReader(f):
                for s in sutunlar:
                    assert not DUZ_KESME.search(satir[s] or ""), (yol, s, satir[s])
    m = json.loads(oku("kartlar/kartlar.json"))
    for k in m["kartlar"]:
        for alan in ("metin", "kaynak") + (() if k["tur"] == "alinti" else ("buyuk",)):
            for dil in ("tr", "en"):
                assert not DUZ_KESME.search(k[alan][dil]), (k["id"], alan, dil)
