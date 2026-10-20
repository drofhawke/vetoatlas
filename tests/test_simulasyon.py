"""
"Ya veto olmasaydı?" sayfası (web/simulasyon.html): sayım yalnızca kayıtlı oyları kullanır.
Toplu görünümün sayıları burada veri setinden bağımsız olarak hesaplanır; sayfadaki JavaScript aynı kuralı uygular.
Kural: 1966 öncesi 11 üyeli Konsey, sonrası 15; eşikler 7/9, 8/10, 6/8.

Kitaptaki 20 üyeli Konsey (ADIM 43): seçili eşiğin oranı korunur (12, 14, 11); hesap yalnızca kayıtlı oylara dayanır, kayıtta
olmayan üyelerin oyu tahmin edilmez. Toplu görünümün 20 üyeli satırları burada bağımsız hesaplanır ve sayfanın kendi hesabı
(Node ile) bu sayılarla karşılaştırılır.

Birbirine bağlı filtreler (web/suzgec.js): Python modeli bütün geçerli filtre durumlarında denetlenir; sayfanın kullandığı
JavaScript modülü Node ile aynı durumlarda çalıştırılıp modelle birebir karşılaştırılır (Node yoksa bu test atlanır).
"""
import json
import math
import re
import shutil
import subprocess

import pytest

from conftest import KOK

VERI = json.loads((KOK / "data/processed/vetolar_mutabik.json").read_text(encoding="utf-8"))
K = VERI["kayitlar"]
SAYFA = (KOK / "web/simulasyon.html").read_text(encoding="utf-8")


def boyut(k):
    return 11 if k["tarih"] < "1966-01-01" else 15


ESIK = {"cogunluk": lambda n: 9 if n == 15 else 7, "ucteiki": lambda n: 10 if n == 15 else 8, "salt": lambda n: 8 if n == 15 else 6}


def test_toplu_gorunum_sayilari():
    kapali = [k for k in K if k["atif_belirsiz"]]
    oysuz = [k for k in K if not k["atif_belirsiz"] and not k["oy_dagilimi"]]
    oylu = [k for k in K if not k["atif_belirsiz"] and k["oy_dagilimi"]]
    assert len(kapali) + len(oysuz) + len(oylu) == len(K) == 266
    assert (len(kapali), len(oysuz), len(oylu)) == (2, 0, 264)
    kabul = {ad: sum(1 for k in oylu if k["oy_dagilimi"]["lehte"] >= f(boyut(k))) for ad, f in ESIK.items()}
    # Veto ile düşen her öneri, kayıtlı lehte oylarıyla mevcut çoğunluk eşiğini zaten karşılıyordu
    assert kabul == {"cogunluk": 264, "ucteiki": 232, "salt": 264}
    # Hiçbir kayıtta oy toplamı Konsey büyüklüğünü aşmaz
    for k in oylu:
        oy = k["oy_dagilimi"]
        assert oy["lehte"] + oy["aleyhte"] + oy["cekimser"] <= boyut(k), k["id"]
        assert oy["aleyhte"] >= len(k["veto_eden_uyeler"]), k["id"]


def test_sayfa_veriden_okur_ve_sabit_sayi_icermez():
    assert 'src="veri.js"' in SAYFA and "window.VETO_VERISI" in SAYFA
    betik = SAYFA[SAYFA.index("<script>"):]
    # Toplu görünümün sayıları betikte sabit yazılı değil, sayfa açılırken hesaplanıyor
    assert not re.search(r"\b(264|232|82|182|28|236|111|153)\b", betik)
    # Kitabın unsurları alıntı bankasından (bölüm başlığıyla); kitabın belirtmediği parametreler "Ayarlar" kutusunda (ADIM 44)
    for kimlik in ("kitap-3", "kitap-4", "kitap-6", "kitap-7"):
        assert kimlik in betik
    assert "Kitap karar eşiğini ve üye sayısını belirtmiyor. Bu iki seçenek bizim varsayımımız." in SAYFA
    assert "The book does not specify the decision threshold or the number of members. These two settings are our assumption." in SAYFA
    # Diğer modellerin dayanakları belge ve paragrafla
    for dayanak in ("A/59/L.64", "5 (b)", "6 (b)", "A/59/L.68", "dipnot 5", "Ext/EX.CL/2 (VII)", "A/59/L.67"):
        assert dayanak in SAYFA, dayanak
    # Sınırlar: değişmez oylar ve veto tehdidi sayfada; Madde 108 Metodoloji 2.10'da (20 Ekim 2026)
    assert "tehdid" in SAYFA and "108" not in SAYFA[SAYFA.index("<script>"):] and "108. maddesine" in (KOK / "METODOLOJI.md").read_text(encoding="utf-8")
    # Hareket azaltma tercihi
    assert "prefers-reduced-motion" in SAYFA


def test_baglantilar():
    # Sayfalar arası gezinme üst çubukta (ADIM 45: Vetolar'daki oklu bağlantı satırı kaldırıldı); Söz ve Kayıt'tan bağlantı
    assert '["simulasyon", "Ya veto olmasaydı?", "What if there were no veto?"],' in (KOK / "web/cubuk.js").read_text(encoding="utf-8")
    assert "simulasyon.html" in (KOK / "web/vizyon.html").read_text(encoding="utf-8")


# ---------- ADIM 35: bağlı filtreler, hazır örnekler, ?kayit= ----------
WEB_VERI = (KOK / "web/veri.js").read_text(encoding="utf-8")
KAYITLAR = json.loads(WEB_VERI[WEB_VERI.index("{"):WEB_VERI.rstrip().rindex(";")])["kayitlar"]
BETIK = SAYFA[SAYFA.index("<script>"):]
SIRA = ("konu", "yil", "uye")
BOS = {"konu": "", "yil": "", "uye": ""}
ORNEKLER = {  # kimlik -> (tarih, veto eden üyeler, lehte, aleyhte, çekimser); sayfadaki ORNEKLER sabitiyle ve veri setiyle karşılaştırılır
    "V-2024-02-20-1": ("2024-02-20", ["USA"], 13, 1, 1),
    "V-2012-02-04-1": ("2012-02-04", ["RUS", "CHN"], 13, 2, 0),
    "V-2015-07-08-1": ("2015-07-08", ["RUS"], 10, 1, 4),
    "V-1981-04-30-1": ("1981-04-30", ["GBR", "USA", "FRA"], 12, 3, 0),
    "V-2004-04-21-1": ("2004-04-21", ["RUS"], 14, 1, 0),
    "V-1955-12-15-1": ("1955-12-15", ["SSCB"], 10, 1, 0),
}


# Filtre kuralları web/suzgec.js başındaki açıklamadadır. Aşağıdaki Python modeli bu kuralların bağımsız yazımıdır;
# test, sayfanın kullandığı JavaScript modülünü Node ile bütün geçerli filtre durumlarında çalıştırıp modelle karşılaştırır.
KONULAR = sorted({k["konu"] for k in KAYITLAR})
YILLAR = sorted({k["tarih"][:4] for k in KAYITLAR})
UYELER = sorted({u for k in KAYITLAR for u in k["uyeler"]})
DEGERLER = {"konu": KONULAR, "yil": YILLAR, "uye": UYELER}


def uyar(k, ad, d):
    return k["konu"] == d if ad == "konu" else k["tarih"][:4] == d if ad == "yil" else d in k["uyeler"]


TUM = frozenset(range(len(KAYITLAR)))
KUME = {ad: {d: frozenset(i for i, k in enumerate(KAYITLAR) if uyar(k, ad, d)) for d in DEGERLER[ad]} for ad in SIRA}


def eslesen(f):
    """Durumla eşleşen kayıtların kümesi (kayıt sırası numaraları); boş değer Tümü."""
    s = TUM
    for a in SIRA:
        if f[a]:
            s = s & KUME[a][f[a]]
    return s


def gecis(f, ad, deger):
    """Kural 1: konu birincil; konu değişince yeni konuda kaydı olmayan yıl, sonra konu ve yılla kaydı olmayan üye Tümü'ye
    döner. Kural 2: yıl ve üye seçimi hiçbir filtreyi değiştirmez."""
    y = dict(f, **{ad: deger})
    sifir = []
    if ad == "konu":
        if y["yil"] and not eslesen({"konu": y["konu"], "yil": y["yil"], "uye": ""}):
            sifir.append(["yil", y["yil"]])
            y["yil"] = ""
        if y["uye"] and not eslesen(y):
            sifir.append(["uye", y["uye"]])
            y["uye"] = ""
    return y, sifir


def beklenen_secenekler(f, ad):
    """Kural 2 ve 3: konu listesinde bütün konular; yıl ve üye listelerinde yalnızca öbür seçimlerle en az bir kayıt veren
    değerler; sayı, seçilince eşleşecek kayıt sayısı."""
    tum = len(eslesen(dict(f, **{ad: ""})))
    if ad == "konu":
        return {"": tum, **{d: len(eslesen(gecis(f, ad, d)[0])) for d in KONULAR}}
    return {"": tum, **{d: n for d in DEGERLER[ad] if (n := len(eslesen(dict(f, **{ad: d}))))}}


def gecerli_durumlar():
    """En az bir kayıt veren bütün filtre durumları (her boyutta Tümü dahil)."""
    return [{"konu": a, "yil": b, "uye": c} for a in ["", *KONULAR] for b in ["", *YILLAR] for c in ["", *UYELER]
            if eslesen({"konu": a, "yil": b, "uye": c})]


NODE_BETIGI = r"""
const fs = require("fs");
const kok = process.argv[2];
const SZ = require(kok + "/web/suzgec.js");
const s = fs.readFileSync(kok + "/web/veri.js", "utf8");
const K = JSON.parse(s.slice(s.indexOf("{"), s.trimEnd().lastIndexOf(";"))).kayitlar;
const durumlar = JSON.parse(fs.readFileSync(0, "utf8"));
const cikti = durumlar.map((f) => {
  const o = {};
  for (const ad of SZ.SIRA) {
    o[ad] = SZ.secenekler(K, f, ad).map((x) => {
      const r = SZ.sec(K, f, ad, x.deger);
      return [x.deger, x.sayi, r.durum, r.sifirlanan.map((z) => [z.ad, z.deger]), SZ.sayi(K, r.durum)];
    });
  }
  return o;
});
process.stdout.write(JSON.stringify(cikti));
"""


def node_calistir(tmp_path, girdi):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js kurulu değil; web/suzgec.js doğrudan çalıştırılamadı (Python modeli yine de denetlendi)")
    betik = tmp_path / "suzgec_denetim.js"
    betik.write_text(NODE_BETIGI, encoding="utf-8")
    r = subprocess.run([node, str(betik), str(KOK)], input=json.dumps(girdi), capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(r.stdout)


def test_filtre_modeli_butun_durumlar():
    """Python modeli: her geçerli durumdan her görünür seçenek en az bir kayıt verir ve yanındaki sayı seçilince eşleşen
    kayıt sayısıdır; yıl ve üye seçimi bir filtreyi sıfırlamaz; seçili değer listede bulunur."""
    durumlar = gecerli_durumlar()
    assert len(durumlar) > 500
    for f in durumlar:
        for ad in SIRA:
            b = beklenen_secenekler(f, ad)
            assert f[ad] in b, (f, ad)
            for d, n in b.items():
                y, sifir = gecis(f, ad, d)
                assert n == len(eslesen(y)) >= 1, (f, ad, d)
                assert ad == "konu" or not sifir, (f, ad, d)


def test_suzgec_modulu_node_ile_butun_durumlar(tmp_path):
    """Sayfanın kullandığı web/suzgec.js, bütün geçerli durumlarda Python modeliyle birebir aynı seçenekleri, sayıları
    ve geçişleri verir; görünür hiçbir seçenek sıfır kayıt vermez."""
    durumlar = gecerli_durumlar()
    cikti = node_calistir(tmp_path, durumlar)
    assert len(cikti) == len(durumlar)
    secenek_sayisi = 0
    for f, o in zip(durumlar, cikti):
        for ad in SIRA:
            js = o[ad]
            assert js[0][0] == "", (f, ad)  # ilk seçenek Tümü
            if ad == "yil":
                assert [x[0] for x in js[1:]] == sorted(x[0] for x in js[1:]), f  # yıllar artan
            assert {x[0]: x[1] for x in js} == beklenen_secenekler(f, ad), (f, ad)
            for deger, n, durum, sifir, eslesen_n in js:
                secenek_sayisi += 1
                y, beklenen_sifir = gecis(f, ad, deger)
                assert durum == y and sifir == beklenen_sifir, (f, ad, deger)
                assert n == eslesen_n == len(eslesen(y)) >= 1, (f, ad, deger)
    assert secenek_sayisi > 20000


def test_tumuye_donus_ve_bildirim(tmp_path):
    # Madde 15 senaryosu: Suriye → yıl listesi 2011'den başlar → 2012'de 2 kayıt → konu Ukrayna: yıl sıfırlanır (2014'ten başlıyor)
    f = dict(BOS)
    f, s = gecis(f, "konu", "Suriye")
    assert not s and min(d for d in beklenen_secenekler(f, "yil") if d) == "2011" and beklenen_secenekler(BOS, "konu")["Suriye"] == 18
    f, s = gecis(f, "yil", "2012")
    assert not s and len(eslesen(f)) == 2 and beklenen_secenekler(dict(BOS, konu="Suriye"), "yil")["2012"] == 2
    f, s = gecis(f, "konu", "Ukrayna")
    assert s == [["yil", "2012"]] and f == {"konu": "Ukrayna", "yil": "", "uye": ""}
    assert min(KAYITLAR[i]["tarih"][:4] for i in eslesen(f)) == "2014"
    # Madde 1 örneği: önce 1990, sonra Suriye → "Yıl filtresi sıfırlandı: Suriye kayıtları 2011'den başlıyor"
    f, s = gecis(dict(BOS, yil="1990"), "konu", "Suriye")
    assert s == [["yil", "1990"]] and min(KAYITLAR[i]["tarih"][:4] for i in eslesen(f)) == "2011"
    # Üye sıfırlama: Ukrayna + Rusya → Lübnan
    f, s = gecis({"konu": "Ukrayna", "yil": "", "uye": "RUS"}, "konu", "Lübnan")
    assert s == [["uye", "RUS"]] and f["uye"] == ""
    # Önce üye seçilince yıl listesi o üyenin yıllarını ve o üyenin sayılarını gösterir (ADIM 35 düzeltmesi)
    abd = beklenen_secenekler(dict(BOS, uye="USA"), "yil")
    assert abd["1972"] == len(eslesen({"konu": "", "yil": "1972", "uye": "USA"})) == 1 and "1950" not in abd
    # Yıl seçiliyken konu listesindeki sayı, seçince gelen sayıdır
    assert beklenen_secenekler(dict(BOS, yil="2012"), "konu")["Suriye"] == 2
    # Aynı senaryolar sayfanın modülüyle
    cikti = node_calistir(tmp_path, [dict(BOS, konu="Suriye", yil="2012"), dict(BOS, uye="USA"), dict(BOS, yil="1990")])
    ukr = next(x for x in cikti[0]["konu"] if x[0] == "Ukrayna")
    assert ukr[2] == {"konu": "Ukrayna", "yil": "", "uye": ""} and ukr[3] == [["yil", "2012"]]
    assert dict((x[0], x[1]) for x in cikti[1]["yil"])["1972"] == 1
    sur = next(x for x in cikti[2]["konu"] if x[0] == "Suriye")
    assert sur[3] == [["yil", "1990"]] and sur[1] == 18
    # Sayfa modülü kullanır; bildirim metinleri ve sıfır eşleşme yedeği yerinde
    assert '<script src="suzgec.js"></script>' in SAYFA and "const SZ = window.VetoSuzgec;" in BETIK
    assert "SZ.secenekler(kayitlar, filtre, ad, SIRALAR[ad])" in BETIK and "const r = SZ.sec(kayitlar, filtre, ad, deger);" in BETIK
    for anahtar in ('"sifir.yilBaslar"', '"sifir.yilBiter"', '"sifir.yilYok"', '"sifir.uye"', "yıl seçimi kaldırıldı.", "the year filter was reset.", "Filtreleri temizle", "Clear the filters"):
        assert anahtar in BETIK, anahtar
    # Eski kaydın sayıları ekranda kalmaz: her gösterimde paneller önce temizlenir (ADIM 49: şeritten yeniden sayımda yalnızca
    # şerit yerinde kalır); sıfır eşleşmede paneller gizlenir
    assert "function goster(animasyon, kaynak) {\n    temizle();\n    panelleriTemizle(kaynak === \"serit\");" in BETIK
    assert '$("#paneller-bolum").hidden = !k;' in BETIK and '$("#bos").hidden = L.length > 0;' in BETIK
    # Rastgele yalnızca eşleşenler arasından, mümkünse ekrandakinden farklı bir kayıt
    assert "const aday = L.length > 1 && durum.kayit ? L.filter((k) => k.id !== durum.kayit.id) : L;" in BETIK


def test_hazir_ornekler_veri_setinde():
    m = re.search(r"const ORNEKLER = \[(.*?)\]\.filter", BETIK, re.S)
    assert m
    sayfadaki = re.findall(r'id: "([^"]+)"', m[1])
    assert sayfadaki == list(ORNEKLER)  # ilk örnek Gazze 2024: açılışta seçili
    kayit = {k["id"]: k for k in KAYITLAR}
    for kimlik, (tarih, uyeler, lehte, aleyhte, cekimser) in ORNEKLER.items():
        k = kayit[kimlik]
        assert not k["kapali"] and k["oy"], kimlik
        assert (k["tarih"], k["uyeler"], k["oy"]["lehte"], k["oy"]["aleyhte"], k["oy"]["cekimser"]) == (tarih, uyeler, lehte, aleyhte, cekimser), kimlik
    g = kayit["V-2024-02-20-1"]
    assert g["oy"]["lehte"] == 13 and (15 - g["oy"]["lehte"]) == 2  # "Bu örnekte 15 üyeden 13’ü evet dedi."
    assert "ornekNotu: ({ boy, lehte, ek }) => `Bu örnekte ${boy} üyeden ${lehte}’${ek} evet dedi.`" in BETIK
    assert "ORNEKLER[0].id" in BETIK  # açılışta ilk örnek


def test_adres_cubugu_ve_akis():
    assert 'new URLSearchParams(location.search).get("kayit")' in BETIK and 'u.searchParams.set("kayit", id)' in BETIK and "history.replaceState" in BETIK
    assert BETIK.count('new URLSearchParams(location.search).get("lang")') == 1  # tek dosya üretimi bu satırı değiştirir
    for anahtar in ("Kaydı seç", "Oyları say", "Karşılaştır", '"p.unsurBaslik": "Kitaptan"', "Aynı ${n} oy. Mevcut sistemde", "kayıtta sonuç", "(oy dağılımı kayıtlı değil)"):
        assert anahtar in BETIK, anahtar
    # Renk kuralı: mevcut sistemde daimî üyenin ret oyu kırmızı (veto), önerilen sistemde mürekkep (aleyhte)
    assert ".oy.veto { background: var(--vurgu);" in SAYFA and ".oy.aleyhte { background: var(--aleyhte);" in SAYFA
    assert 'o.uye && a === "mevcut" ? "veto" : o.tur' in BETIK
    # Yapışkan şerit ve toplu özet veriden
    assert ".serit { position: sticky; bottom: 0;" in SAYFA and '"toplu.ozet"' in BETIK
    assert not re.search(r"\b(264|232|266)\b", BETIK)


# ---------- Kitaptaki 20 üyeli Konsey (ADIM 43) ----------
ESIK20 = {ad: math.ceil(20 * f(15) / 15) for ad, f in ESIK.items()}  # seçili eşiğin oranı korunur


def sonuc20(lehte, boy, esik):
    """Yalnızca kayıtlı oylar: eşiği tek başına karşılıyorsa kabul; karşılamıyorsa kayıtta olmayan (20 - boy) üyeden en az
    (esik - lehte) evetle 'yeni üyelerin oyuna bağlı'; bu üyelerin hepsi evet dese de yetmiyorsa düşerdi."""
    yeni, k = 20 - boy, esik - lehte
    return "kabul" if k <= 0 else "bagli" if k <= yeni else "cogunlukYok"


def yirmi_uyeli_toplu():
    oylu = [k for k in K if not k["atif_belirsiz"] and k["oy_dagilimi"]]
    kapali = [k for k in K if k["atif_belirsiz"]]
    sonuc = {}
    for ad, esik in ESIK20.items():
        turler = [sonuc20(k["oy_dagilimi"]["lehte"], boyut(k), esik) for k in oylu]
        sonuc[ad] = (turler.count("kabul"), turler.count("bagli"), turler.count("cogunlukYok"), len(kapali))
    return sonuc


def test_yirmi_uyeli_konsey_toplu_sayilari():
    """Toplu görünümün 20 üyeli satırları: kayıtlı oylarla kesin kabul, yeni üyelerin oyuna bağlı, (yeni üyelerle de
    düşerdi), kapalı oturum. Hiçbir kayıt 'hesaplanamaz' değildir."""
    assert ESIK20 == {"cogunluk": 12, "ucteiki": 14, "salt": 11}
    sonuc = yirmi_uyeli_toplu()
    assert sonuc == {"cogunluk": (82, 182, 0, 2), "ucteiki": (28, 236, 0, 2), "salt": (111, 153, 0, 2)}
    for ad, satir in sonuc.items():
        assert sum(satir) == len(K) == 266, ad
    # Gereken evet sayısı kayıtta olmayan üye sayısını (15 üyeli Konsey'de 5, 11 üyelide 9) aşmaz
    for k in K:
        if k["oy_dagilimi"] and not k["atif_belirsiz"]:
            for esik in ESIK20.values():
                assert esik - k["oy_dagilimi"]["lehte"] <= 20 - boyut(k), k["id"]


SAYFA_20_BETIGI = r"""
const fs = require("fs");
const kok = process.argv[2];
const sayfa = fs.readFileSync(kok + "/web/simulasyon.html", "utf8").split(/\r?\n/);
const satir = (ad) => { const s = sayfa.find((x) => x.startsWith("  const " + ad + " = ")); if (!s) throw new Error(ad + " yok"); return s; };
const { ESIKLER, esik20, sonuc20, konseyBuyuklugu } = new Function(
  ["ESIKLER", "esik20", "sonuc20", "konseyBuyuklugu"].map(satir).join("\n") + "\nreturn { ESIKLER, esik20, sonuc20, konseyBuyuklugu };")();
const v = fs.readFileSync(kok + "/web/veri.js", "utf8");
const K = JSON.parse(v.slice(v.indexOf("{"), v.trimEnd().lastIndexOf(";"))).kayitlar;
const oylu = K.filter((k) => !k.kapali && k.oy), kapali = K.filter((k) => k.kapali).length;
const cikti = {};
for (const e of ["cogunluk", "ucteiki", "salt"]) {
  const turler = oylu.map((k) => sonuc20(k.oy.lehte, konseyBuyuklugu(k), esik20(e)));
  cikti[e] = { esik: esik20(e), satir: ["kabul", "bagli", "cogunlukYok"].map((t) => turler.filter((x) => x.tur === t).length).concat([kapali]),
               enCokK: Math.max(...turler.filter((x) => x.tur === "bagli").map((x) => x.k)) };
}
process.stdout.write(JSON.stringify(cikti));
"""


def test_yirmi_uyeli_sayfa_hesabi_node_ile(tmp_path):
    """Sayfanın kendi 20 üyeli hesabı (web/simulasyon.html: esik20, sonuc20) web/veri.js üzerinde Node ile çalıştırılır;
    toplu görünümde göreceği sayılar Python modeliyle aynı olmalı."""
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js kurulu değil; sayfanın hesabı doğrudan çalıştırılamadı (Python modeli yine de denetlendi)")
    betik = tmp_path / "yirmi_denetim.js"
    betik.write_text(SAYFA_20_BETIGI, encoding="utf-8")
    r = subprocess.run([node, str(betik), str(KOK)], capture_output=True, text=True, encoding="utf-8", check=True)
    sayfa = json.loads(r.stdout)
    beklenen = yirmi_uyeli_toplu()
    for ad in ESIK20:
        assert sayfa[ad]["esik"] == ESIK20[ad], ad
        assert tuple(sayfa[ad]["satir"]) == beklenen[ad], (ad, sayfa[ad], beklenen[ad])
    assert sayfa["ucteiki"]["enCokK"] == 7  # 11 üyeli Konsey'de 7 evetli kayıt: kayıtta olmayan 9 üyeden en az 7'si


def test_hesaplanamaz_yok_ve_yirmi_uyeli_metinler():
    for eski in ("Hesaplanamaz", "Cannot be computed", "r.hesaplanamaz", "a.oneriKitap20"):
        assert eski not in SAYFA, eski
    for metin in (
        '"r.bagli": "Yeni üyelerin oyuna bağlı"',
        '"a.kabul20": ({ lehte, esik }) => `Kayıtlı ${lehte} evet oyu 20 üyeli Konsey’in eşiğini (${esik}) tek başına karşılıyor. Yeni üyelerin oyuna bakmaya gerek yok.`',
        '"a.bagli20": ({ lehte, esik, yeni, k, ek }) => `Kayıtlı ${lehte} evet oyu var, 20 üyeli Konsey’de ${esik} gerekir. Kayıtta olmayan ${yeni} üyeden en az ${k}’${ek} evet derse kabul edilirdi.`',
        '"yeni.not": ({ yeni }) => `Kesikli kareler kayıtta olmayan ${yeni} üye.`',
        '"serit.bagli": ({ k }) => `Yeni üyelerin oyuna bağlı: en az ${k} evet`',
        "20 üyeli Konsey’de sonuç yeni üyelerin oyuna bağlı, en az ${k} evet.",
        '"t.kesin": "Kayıtlı oylarla kesin kabul", "t.bagli": "Yeni üyelerin oyuna bağlı"',
        '"r.bagli": "Depends on the new members’ votes"',
        "The dashed squares are the ${yeni} members not on record.",
        '"serit.bagli": ({ k }) => `Depends on the new members’ votes: at least ${k} yes`',
    ):
        assert metin in SAYFA, metin
    # Görsel: kayıtta olmayan üyeler kesikli boş kare, yalnızca önerilen sistem panelinde; sayaç yalnızca kayıtlı oyları sayar
    assert ".oy.yeni { background: transparent; border: 1px dashed var(--murekkep-2); opacity: 1; transform: none; }" in SAYFA
    assert '+ (a === "oneri" && yirmi ? `<span class="yeni-grup" aria-hidden="true">${\'<span class="oy yeni"></span>\'.repeat(s20.yeni)}</span>` : "");' in BETIK
    assert 'const sayacMetni = t("sayac", { lehte: oy.lehte, aleyhte: oy.aleyhte, cekimser: oy.cekimser, katilmadi });' in BETIK
    # Yapışkan şerit ve fark cümlesi üçüncü sonuç türünü taşır; toplu görünüm üye seçimi değişince yenilenir
    assert 'const seritOneri = sonucOneri === "bagli" ? t("serit.bagli", { k: sayi(s20.k) }) : so.textContent;' in BETIK
    assert 'sonucOneri === "bagli" ? t("fark.bagli", { n, k: sayi(s20.k) }) : t("fark", { n })' in BETIK
    assert 'durum.uye = e.target.value; esikEtiketleri(); ayarNotu(); goster(false); topluYaz();' in BETIK
    # Metodoloji 2.10 (ADIM 45'ten önce 2i)
    for yol, ifade in (("METODOLOJI.md", "### 2.10. \"Ya veto olmasaydı?\" sayfası"), ("METODOLOJI_EN.md", "### 2.10. The \"What if there were no veto?\" page")):
        md = (KOK / yol).read_text(encoding="utf-8")
        assert ifade in md and ("tahmin edilmez" in md or "not\nguessed" in md or "not guessed" in md), yol


def test_ayarlar_kutusu_adim44():
    """Karar eşiği ve üye seçimi varsayılan olarak kapalı "Ayarlar" kutusunda; panelin gövdesinde kural özeti ve sayım kalır
    (ADIM 51'den beri sonuç ve nedeni sonuç kartlarında). İki "Kitapta belirtilmemiştir" etiketi yerine kutuda listelerin
    üstünde tek cümle. Varsayılandan farklı ayarda kutu kapalıyken de tek satırlık not (önerilen sistemin sonuç kartında)."""
    oneri = SAYFA[SAYFA.index('<article class="panel kutu" id="panel-oneri"'):SAYFA.index('<article class="panel kutu" id="panel-mevcut"')]
    mevcut = SAYFA[SAYFA.index('<article class="panel kutu" id="panel-mevcut"'):SAYFA.index('<div class="sonuc-blok kutu"')]
    kutu = '<details class="ayarlar" id="ayarlar"><summary data-t="ayar.baslik"></summary><div class="parametre" id="parametre"></div></details>'
    assert kutu in oneri and oneri.index(kutu) > oneri.index('<div class="ayrinti">')  # açıklamanın altında, kapalı (open yok)
    satirlar = re.findall(r'\n          <(\w+) class="([\w -]+)"', oneri)
    assert [s[1] for s in satirlar] == ["kural", "sayac-kutu", "ayrinti"], satirlar
    kart = SAYFA[SAYFA.index('<div class="sonuc-kart" id="kart-oneri">'):SAYFA.index('<div class="sonuc-kart" id="kart-mevcut">')]
    assert kart.index('<p class="neden" id="aciklama-oneri"></p>') < kart.index('<p class="ayar-notu" id="ayar-notu" hidden></p>')
    assert "parametre-yok" not in mevcut and '<p class="kural-ayrinti" data-t="p.mevcutAyrinti"></p>' in mevcut[mevcut.index('<div class="ayrinti">'):]  # "Parametre yok" satırı kalktı (20 Ekim 2026)
    assert "grid-template-rows: repeat(4, auto);" in SAYFA and "grid-row: span 4;" in SAYFA  # iki panel aynı 4 satır
    # Etiket yok; tek cümle listelerin üstünde
    assert "belirtilmemis" not in SAYFA and "Kitapta belirtilmemiştir" not in SAYFA
    sablon = BETIK[BETIK.index('$("#parametre").innerHTML = `'):BETIK.index("</select></div>`;")]
    assert sablon.index('<p class="ayar-cumle">${t("ayar.cumle")}</p>') < sablon.index('<select id="pr-esik">') < sablon.index('<select id="pr-uye">')
    assert 'class="etiket"' not in sablon
    # Not: yalnızca varsayılandan farklı ayarlar
    assert '"ayar.not": ({ p }) => `${p} ile sayıldı`, "ayar.ucteiki": "üçte iki eşiği", "ayar.salt": "salt çoğunluk eşiği", "ayar.kitap20": "20 üyeli Konsey",' in SAYFA
    assert '"ayar.not": ({ p }) => `Counted with ${p}`, "ayar.ucteiki": "two-thirds threshold", "ayar.salt": "simple-majority threshold", "ayar.kitap20": "20-member Council",' in SAYFA
    assert 'const p = [durum.esik !== "cogunluk" ? t("ayar." + durum.esik) : "", durum.uye !== "kayitli" ? t("ayar." + durum.uye) : ""].filter(Boolean);' in BETIK
    assert "ayarNotu(); goster(false); topluYaz(); });" in BETIK and BETIK.count("ayarNotu();") == 2


def test_yeniden_sayim_dugmeleri_adim49():
    """ADIM 49: "Sayımı yeniden başlat" iki panelin altında ortada; birincil düğme (dolu mürekkep zemin, kâğıt rengi yazı, 48 px,
    solda döngü simgesi), yanında ikincil "Rastgele kayıt". Sayım sürerken birincil pasif ve soluk (aria-disabled; odak
    kaybolmaz), bitince etkin. Yapışkan şeritte küçük kopya ("Yeniden say"); şeritten başlatınca şerit yerinde kalır. Hareket
    azaltma tercihinde sonuç anında. Düğme tanımı web/temel.css'te; Hikâye'deki "Veriyi keşfet" ile aynı sınıf."""
    g = SAYFA[SAYFA.index("<body"):SAYFA.index('<script src="veri.js">')]
    bas = g.index('<div class="dugmeler">')
    dugmeler = g[bas:g.index("\n      </div>", bas)]
    assert '<button type="button" class="dugme" id="tekrar"><svg class="dongu" width="20" height="20"' in dugmeler
    assert '<span data-t="tekrar"></span></button>' in dugmeler
    assert '<button type="button" class="dugme ikincil" id="rastgele-kayit" data-t="rastgeleKayit"></button>' in dugmeler
    assert 'stroke="currentColor"' in dugmeler and "vurgu" not in dugmeler and "A4262C" not in dugmeler  # simge yazı renginde
    assert g.index('<p class="fark" id="fark" hidden></p>') < bas < g.index('<div class="serit kutu" id="serit" hidden>')
    assert ('<span class="serit-metin" id="serit-metin" aria-live="polite"></span><button type="button" class="dugme kucuk" '
            'id="serit-tekrar"><svg class="dongu" width="16" height="16"') in g
    # ADIM 51: düğmeler sonuç bloğunda, taslaktaki gibi sola yaslı
    assert ".dugmeler { display: flex; flex-wrap: wrap; justify-content: flex-start; gap: var(--b3); margin: var(--b6) 0 0; }" in SAYFA
    for parca in ('tekrar: "Sayımı yeniden başlat", tekrarKisa: "Yeniden say", rastgeleKayit: "Rastgele kayıt",',
                  'tekrar: "Run the count again", tekrarKisa: "Count again", rastgeleKayit: "Random record",',
                  'const sayimSuruyor = (v) => ["#tekrar", "#serit-tekrar"].forEach((s) => $(s).setAttribute("aria-disabled", String(v)));',
                  'const yenidenSay = (kaynak) => { if ($("#tekrar").getAttribute("aria-disabled") === "true") return; goster(true, kaynak); };',
                  '$("#rastgele").addEventListener("click", rastgeleSec);', '$("#rastgele-kayit").addEventListener("click", rastgeleSec);',
                  '$("#tekrar").addEventListener("click", () => yenidenSay("panel"));',
                  '$("#serit-tekrar").addEventListener("click", () => yenidenSay("serit"));',
                  'if (seritKalsin && seritDolu) $("#serit-metin").textContent = t("r.sayiliyor");',
                  'panelleriTemizle(kaynak === "serit");\n    sayimSuruyor(false);',
                  '    sayimSuruyor(true);\n    const ilkVeto',
                  '    if (!animasyon || azHareket) {'):
        assert parca in BETIK, parca
    bitir = BETIK[BETIK.index("    const bitir = () => {"):BETIK.index("    if (!animasyon || azHareket) {")]
    assert "seritDolu = true; seritGuncelle();\n      sayimSuruyor(false);" in bitir  # bitince etkin
    temel = (KOK / "web/temel.css").read_text(encoding="utf-8")
    for kural in (".dugme { display: inline-flex; align-items: center; justify-content: center; gap: var(--b2); min-height: 48px; padding: 0 var(--b6);",
                  "font: 600 var(--yz-govde)/var(--sa-govde) var(--sans); color: var(--zemin); background: var(--murekkep); border: 1px solid var(--murekkep);",
                  ".dugme.ikincil { color: var(--murekkep); background: var(--yuzey); border-color: var(--cizgi); }",
                  ".dugme.kucuk { min-height: 40px; padding: 0 var(--b4); font: 600 var(--yz-kucuk)/var(--sa-kucuk) var(--sans); }",
                  '.dugme[aria-disabled="true"], .dugme:disabled { opacity: .45; cursor: default; }'):
        assert kural in temel, kural
    h = (KOK / "web/hikaye.html").read_text(encoding="utf-8")
    assert '<a class="dugme" href="vetolar.html${ek}">' in h and ".kapanis .dugme { margin: 0 12px 12px 0; }" in h
    assert ".dugme { display: inline-block;" not in h  # Hikâye kendi düğme stilini tanımlamaz
    kilavuz = (KOK / "kaynaklar/kimlik/KILAVUZ.md").read_text(encoding="utf-8")
    assert "**Düğmeler.**" in kilavuz and "48 px yükseklik" in kilavuz and "`aria-disabled`" in kilavuz


def test_sonuc_kartlari_adim51():
    """ADIM 51 (kaynaklar/kimlik/sonuc-taslak.html): panellerin altında tek "Sonuç" bloğu: başlıkta kaydın tarihi ve belge
    numarası; iki sonuç kartı yan yana (sistem adı ve kural özeti, büyük sonuç sözcüğü, tek cümle neden); altında fark
    cümlesi, ADIM 49'daki düğmeler, en altta sayım sırası notu; mobilde kartlar alt alta. "Sınırlar" açık ve ayrı. Renkler:
    yeşil yalnızca "Kabul edilirdi", vetoyla "Düştü" kırmızı, "Yeni üyelerin oyuna bağlı" ikincil, çoğunluk yokken düşme
    mürekkep. Şerit aynı renklerle ve yalnızca sonuç kartları ekran dışındayken görünür. 20 üyeli ayarda neden cümlesi ilgili
    sonucu taşır, ayar notu önerilen sistem kartında tek satır."""
    g = SAYFA[SAYFA.index("<body"):SAYFA.index('<script src="veri.js">')]
    blok = g[g.index('<div class="sonuc-blok kutu" id="sonuc-blok">'):g.index('<div class="serit kutu" id="serit" hidden>')]
    sira = ['<h2 class="sonuc-baslik" id="h-sonuc"></h2>', '<div class="sonuc-kartlar" id="sonuc-kartlar">',
            '<div class="sonuc-kart" id="kart-oneri"><p class="ad" id="ad-oneri"></p><p class="sonuc" id="sonuc-oneri" aria-live="polite"></p><p class="neden" id="aciklama-oneri"></p><p class="ayar-notu" id="ayar-notu" hidden></p></div>',
            '<div class="sonuc-kart" id="kart-mevcut"><p class="ad" id="ad-mevcut"></p><p class="sonuc" id="sonuc-mevcut" aria-live="polite"></p><p class="neden" id="aciklama-mevcut"></p></div>',
            '<p class="fark" id="fark" hidden></p>', '<div class="dugmeler">']
    konum = [blok.index(x) for x in sira]
    assert konum == sorted(konum)
    for panel in re.findall(r'<article class="panel kutu".*?</article>', g, re.S):
        assert 'class="sonuc"' not in panel and "aciklama-" not in panel and "ayar-notu" not in panel
    # Sınırlar: kutusuz iki cümle, paneller bölümünün sonunda (20 Ekim 2026)
    assert '<p class="sinirlar-not" data-t="sinirlar"></p>' in g[g.index('id="paneller-bolum"'):g.index("</section>", g.index('id="paneller-bolum"'))] and "<aside" not in g
    for kural in (".sonuc-kartlar { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }",
                  ".sonuc-kart { padding: 16px 24px; background: var(--zemin); border: 1px solid var(--cizgi); border-radius: 6px;",
                  ".sonuc.kabul { color: var(--kabul); }", ".sonuc.dustu { color: var(--vurgu); }", ".sonuc.bagli { color: var(--murekkep-2); }",
                  ".sonuc.yok { color: var(--murekkep); }", ".serit .kabul { color: var(--kabul); }", ".serit .dustu { color: var(--vurgu); }",
                  ".serit .bagli { color: var(--murekkep-2); }", ".serit .yok { color: var(--murekkep); }",
                  "  .sonuc-kartlar { grid-template-columns: 1fr; }", "--kabul: #2D6A4F;", "--kabul: #6FBF8E;"):
        assert kural in SAYFA, kural
    assert ".serit { position: sticky; bottom: 0; margin: 16px 0 0; padding: 8px 16px; background: var(--zemin);" in SAYFA
    for parca in ('"sonuc.baslik": ({ tarih, belge }) => `Sonuç: ${tarih}${belge ? `, ${belge}` : ""}`,',
                  '"sonuc.baslik": ({ tarih, belge }) => `Result: ${tarih}${belge ? `, ${belge}` : ""}`,',
                  '"kart.oneri": ({ boy, esik }) => `veto yok, ${boy}’${sayiEki(boy, "de")} ${esik}`, "kart.mevcut": "Madde 27/3",',
                  '"kart.oneri": ({ boy, esik }) => `no veto, ${esik} of ${boy}`, "kart.mevcut": "Article 27 (3)",',
                  '"serit.oneri": "Önerilen:", "serit.mevcut": "Mevcut:",', '"serit.oneri": "Proposed:", "serit.mevcut": "Current:",',
                  'const belge = (k.belgeler.find((b) => b.tur === "taslak") || k.belgeler[0] || {}).kod;',
                  '$("#h-sonuc").textContent = t("sonuc.baslik", { tarih: tarihUzun(k.tarih), belge });',
                  '$("#ad-oneri").textContent = `${t("p.oneri")}: ${t("kart.oneri", { boy: yirmi ? 20 : boy, esik })}`;',
                  'so.className = "sonuc " + (sonucOneri === "kabul" ? "kabul" : sonucOneri === "bagli" ? "bagli" : "yok");',
                  'const seritGuncelle = () => { $("#serit").hidden = !seritDolu || kartlarGorunur; };',
                  'new IntersectionObserver((g) => { kartlarGorunur = g[g.length - 1].isIntersecting; seritGuncelle(); }).observe($("#sonuc-kartlar"));',
                  't({ kabul: "a.kabul20", bagli: "a.bagli20", cogunlukYok: "a.yok20" }[sonucOneri]'):
        assert parca in BETIK, parca
    # Sayılamayan kayıtta da başlık ve kartların sistem adı yazılır (sayılabilirlik denetiminden önce)
    assert BETIK.index('$("#h-sonuc").textContent') < BETIK.index("if (!sayilabilir(k)) {", BETIK.index("function goster("))
