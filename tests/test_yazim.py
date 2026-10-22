"""
Yazım (ADIM 42; kaynaklar/kimlik/KILAVUZ.md bölüm 2, "Yüzde"): Türkçede yüzde işareti sayının önüne gelir
("%58", "%18,3"), İngilizcede arkasına ("58%", "18.3%"); sayı ile işaret arasında boşluk yoktur.

Sayfaların kaynakları (sözlükler ve yüzde biçimleyicileri), tek dosya sürümü ve paylaşım kartları denetlenir; sayfa
açılırken oluşan metin tarayıcıda ayrıca denetlenir.
"""
import json
import re

from conftest import KOK

WEB = KOK / "web"
SAYFALAR = ["hikaye", "vetolar", "vizyon", "reform", "simulasyon", "temsil", "hakkinda", "metodoloji"]
BOSLUK = "[   ]"  # boşluk, bölünmez boşluk, dar bölünmez boşluk
SAYI_BOSLUK_YUZDE = re.compile(r"\d" + BOSLUK + "%")  # "58 %": hiçbir dilde yok
SAYI_YUZDE = re.compile(r"\d" + BOSLUK + "?%")  # "58%" ya da "58 %": Türkçede yok
YUZDE_SAYI = re.compile("%" + BOSLUK + r"?\d")  # "%58": İngilizcede yok
BICIMLEYICI = re.compile(r"[\"'`]" + BOSLUK + r"%[\"'`]|\}" + BOSLUK + "%")  # + " %" ya da `${x} %` ile sona ekleme


def gorunen_metin(html):
    """HTML'den görünen metin: stil blokları ve etiketler (öznitelikleriyle) çıkarılır."""
    html = re.sub(r"<style>.*?</style>", " ", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html)


def test_sayfalarda_sayi_bosluk_yuzde_yok():
    for ad in SAYFALAR:
        s = (WEB / f"{ad}.html").read_text(encoding="utf-8")
        assert not SAYI_BOSLUK_YUZDE.search(s), (ad, SAYI_BOSLUK_YUZDE.search(s))
        assert not BICIMLEYICI.search(s), (ad, BICIMLEYICI.search(s))
    tek = (WEB / "veto-atlasi-tek-dosya.html").read_text(encoding="utf-8").replace('\\"', '"')
    assert not SAYI_BOSLUK_YUZDE.search(tek) and not BICIMLEYICI.search(tek)
    # Yüzde biçimleyicileri dile göre: Türkçede işaret sayının önünde
    for ad, bicim in (("temsil", 'return DIL === "tr" ? "%" + s : s + "%"; };'),
                      ("vizyon", 'return DIL === "tr" ? "%" + s : s + "%"; };'),
                      ("hikaye", 'const yuzdeIsaret = (p) => (DIL === "tr" ? `%${yuzde(p)}` : `${yuzde(p)}%`);')):
        assert bicim in (WEB / f"{ad}.html").read_text(encoding="utf-8"), ad


def test_kartlarda_yuzde_dile_gore():
    m = json.loads((WEB / "kartlar/kartlar.json").read_text(encoding="utf-8"))
    sinanan = 0
    for k in m["kartlar"]:
        for alan in ("buyuk", "metin", "kaynak"):
            tr, en = k[alan]["tr"], k[alan]["en"]
            assert not SAYI_YUZDE.search(tr), (k["id"], alan, tr)
            assert not YUZDE_SAYI.search(en) and not SAYI_BOSLUK_YUZDE.search(en), (k["id"], alan, en)
            sinanan += len(re.findall(r"%\d", tr))
    assert sinanan > 0  # temsil kartlarında Türkçe yüzdeler var: "%57,8"
    for yol in sorted((WEB / "kartlar").glob("*-tr-*.html")):
        assert not SAYI_YUZDE.search(gorunen_metin(yol.read_text(encoding="utf-8"))), yol.name
    for yol in sorted((WEB / "kartlar").glob("*-en-*.html")):
        g = gorunen_metin(yol.read_text(encoding="utf-8"))
        assert not YUZDE_SAYI.search(g) and not SAYI_BOSLUK_YUZDE.search(g), yol.name


def test_kalip_denetimi_kendini_sinar():
    assert SAYI_BOSLUK_YUZDE.search("nüfusun 58 %'i") and SAYI_BOSLUK_YUZDE.search("18,3 %")
    assert SAYI_YUZDE.search("58%") and not SAYI_YUZDE.search("%58 ve %18,3")
    assert YUZDE_SAYI.search("%58") and not YUZDE_SAYI.search("58% and 18.3%")
    assert BICIMLEYICI.search('toLocaleString() + " %"') and BICIMLEYICI.search("`${yuzde(p)} %`")
    assert not BICIMLEYICI.search('DIL === "tr" ? "%" + s : s + "%"')


def test_ingilizce_cumle_icinde_belirli_tanimlik():
    """İngilizce cümle içinde üye adları belirli tanımlıkla: "the negative vote of the United States", "the Russian Federation",
    "the USSR"; France, China ve kısa adlardan Russia tanımlıksız. Listelerde, düğmelerde ve etiketlerde ad tanımlıksız kalır.
    Şablonlar adı tanımlıksız varsayar ("of ${uye}"); tanımlığı adın cümle içi biçimi getirir."""
    sim = (WEB / "simulasyon.html").read_text(encoding="utf-8")
    vet = (WEB / "vetolar.html").read_text(encoding="utf-8")
    tam = 'SSCB: "the Soviet Union", RUS: "the Russian Federation", USA: "the United States", GBR: "the United Kingdom" }'
    assert f"const CUMLE_EN = {{ {tam};" in sim and f"const CUMLE_EN = {{ ad: {{ {tam}," in vet
    assert 'kisa: { SSCB: "the USSR", USA: "the US", GBR: "the UK" } };' in vet  # kısa adlardan Russia tanımlıksız
    assert 'const uyeAdMetin = (u) => (DIL === "en" && CUMLE_EN[u]) || uyeAd(u);' in sim
    # Cümle şablonlarına giden adlar: mevcut sistem kartı ve diğer modeller (ulkeAdi), filtre sıfırlama, Genel Kurul ayrıntısı
    assert 'const ulkeAdi = durum.ulke ? uyeAdMetin(durum.ulke) : k.uyeler.map(uyeAdMetin).join(DIL === "tr" ? " ve " : " and ");' in sim
    assert "uye: uyeAdMetin(x.deger) });" in sim
    assert 'const ayni = konusanlar.filter(([, x]) => x === d).map(([u]) => uyeAdMetin(u));' in vet  # "Veto eden ABD söz aldı."
    assert 't("gk.vetoCumle", { uyeler: ayni.join(t("ve")), durum: t("gk.konustu." + d), n: ayni.length })' in vet
    assert "With the negative ${n > 1 ? `votes of ${uye}, permanent members` : `vote of ${uye}, a permanent member`}" in sim
    # Öteki modeller için ortak cümle: ad cümle başında, tanımlığı büyük harfle ("The United States is a permanent member")
    assert ("${uye.charAt(0).toUpperCase() + uye.slice(1)} ${m > 1 ? \"are permanent members\" : \"is a permanent member\"}, so the proposal "
            "is not adopted under any of them.") in sim
    assert '$("#karsilastir-ortak").textContent = t("k.ortak", { uye: ulkeAdi, m: vetoSayisi, boy });' in sim
    assert "No veto by ${uye} among the" in sim


SAPKASIZ = re.compile(r"\b(daimi|resmi|dahil)\w*", re.I)  # Türkçe metinde şapkalı yazım tek biçimdir: daimî, resmî, dâhil
OY_SAYIMI = re.compile(r"\d+ (lehte|aleyhte)\b")  # "11 lehte" değil "11 evet"
OY_KALIBI = re.compile(r"\b(lehte|aleyhte) oy\b")  # "SSCB aleyhte oy verdi" değil "SSCB hayır oyu verdi"


def _veri():
    s = (WEB / "veri.js").read_text(encoding="utf-8")
    return json.loads(s[s.index("{"):s.rindex("}") + 1])


def test_turkce_notlarda_sapkali_yazim_ve_oy_terimi():
    """KILAVUZ bölüm 2, "Noktalama ve ses" ve "Kayıt notu biçimi": kayıt notları, düzeltme açıklamaları, alıntıların ve reform
    modellerinin Türkçesi şapkalı yazılır (daimî, resmî, dâhil); oy sayımı paneldeki terimlerle ("11 evet, 2 hayır, 2 çekimser").
    Kod değerleri (`resmi`, `gayriresmi_transkript`, `yeni_daimi`) metin değildir, denetlenmez. Üyenin oyu da aynı
    terimlerle yazılır: "SSCB hayır oyu verdi", "evet oyu verdi"; "aleyhte oy verdi" ve "lehte oy verdi" yazılmaz
    (G-veri-1, G-veri-2, H-veri-1). Paylaşım kartlarının Türkçe cümleleri de denetlenir."""
    import csv
    assert SAPKASIZ.search("yeni daimi üyeler dahil") and not SAPKASIZ.search("daimî resmî dâhil")
    assert OY_SAYIMI.search("11 lehte, 2 aleyhte") and not OY_SAYIMI.search("SSCB hayır oyu verdi")
    assert OY_KALIBI.search("SSCB aleyhte oy verdi") and OY_KALIBI.search("öbür üyeler lehte oy verirken")
    assert not OY_KALIBI.search("SSCB hayır oyu verdi") and not OY_KALIBI.search("evet oyu verirken")
    V = _veri()
    metinler = []
    for k in V["kayitlar"]:
        metinler += [(k["id"], n["tr"]) for n in k.get("notlar") or [] if isinstance(n, dict) and n.get("tr")]
    metinler += [(a["id"], a.get("metin_tr", "")) for a in V["alintilar"]]
    metinler += [(f'{r["model"]}/{r["olcut"]}', r["tr"]) for r in V["reformModelleri"]]
    with open(KOK / "kaynaklar/duzeltmeler.csv", encoding="utf-8", newline="") as f:
        metinler += [(f'duzeltmeler.csv {r["tarih"]}', r["aciklama"]) for r in csv.DictReader(f)]
    assert len(metinler) > 100
    sapkasiz = [(ad, m[0]) for ad, s in metinler for m in SAPKASIZ.finditer(s)]
    assert not sapkasiz, sapkasiz
    sayim = [(ad, m[0]) for ad, s in metinler for m in OY_SAYIMI.finditer(s)]
    assert not sayim, sayim
    # Kayıt notları, düzeltme satırı ve paylaşım kartları: "hayır oyu verdi" / "evet oyu verdi"
    kalip = metinler + [(k["id"], k["duzeltme"]) for k in V["kayitlar"] if k.get("duzeltme")]
    kartlar = json.loads((WEB / "kartlar/kartlar.json").read_text(encoding="utf-8"))["kartlar"]
    kalip += [(x["id"], x["metin"]["tr"]) for x in kartlar if x.get("metin", {}).get("tr")]
    kalip_bulunan = [(ad, m[0]) for ad, s in kalip for m in OY_KALIBI.finditer(s)]
    assert not kalip_bulunan, kalip_bulunan
    assert sum(s.count("hayır oyu verdi") for _, s in metinler) >= 26
    # Açık depodaki Markdown belgeleri de (satır içi kod hariç)
    for md in ("METODOLOJI.md", "README.md"):
        metin = re.sub(r"`[^`\n]*`", "", (KOK / md).read_text(encoding="utf-8"))
        assert not SAPKASIZ.search(metin), (md, SAPKASIZ.search(metin))


# Tek istisna: Hikâye 4. adımının paragrafı 21 Ekim 2026'da yayındaki hâliyle "lehte oy kullandı" der (kullanıcı kararı;
# KILAVUZ "Hikâye, yedi adım" ve "Kayıt notu biçimi"). İstisna yalnız bu cümle içindir ve sayfada bir kez geçer.
HIKAYE_LEHTE = "Bu kararların her birinde Konseyin diğer bütün üyeleri lehte oy kullandı;"


def test_sayfalarda_lehte_aleyhte_sayim_kalibi_yok():
    """Sayfa sözlüklerinde oy terimi "evet oyu" / "hayır oyu"dur: "lehte oy", "aleyhte oy" ve "11 lehte" yazılmaz. Oy alan adları
    (k.oy.lehte) ve CSS değişkenleri (--oy-lehte) metin değildir. Metodoloji yöntem metni olarak ayrı yazılır, burada yoktur.
    Hikâye'nin 4. adımı tek istisnadır (HIKAYE_LEHTE)."""
    kalip = re.compile(r"\b(lehte|aleyhte) oy|\d+ (lehte|aleyhte)\b")
    for ad in ("hikaye", "vetolar", "vizyon", "reform", "simulasyon", "temsil", "hakkinda"):
        s = (WEB / f"{ad}.html").read_text(encoding="utf-8")
        if ad == "hikaye":
            assert s.count(HIKAYE_LEHTE) == 1 and '"4.metin": ({ n11, yil, boy }) => `' + HIKAYE_LEHTE in s
            s = s.replace(HIKAYE_LEHTE, "")
        assert not kalip.search(s), (ad, kalip.search(s))


IC_ICE = re.compile(r"“[^“”<>]*“")  # açılan alıntının içinde ikinci açılış çift tırnağı


def test_ic_ice_alintida_ic_tirnak_tek():
    """KILAVUZ "Kesme ve tırnak": alıntı dış çift tırnak içinde gösterilince içteki çift tırnak tek tırnak olur (‘ ’);
    dönüşümü gösteren kod yapar, alıntı bankasındaki metin değişmez (G-vetolar-2, G-kart-2)."""
    V = _veri()
    ic_tirnakli = {a["id"] for a in V["alintilar"] if "“" in a.get("metin_tr", "") + (a.get("metin_en") or "")}
    assert {"2019-1", "2023-3"} <= ic_tirnakli  # kaynak metin aynı kalır
    # Alıntıyı “ ” içine alan her sayfa iç tırnağı icTirnak ile çevirir
    tanim = 'const icTirnak = (s) => String(s).replace(/“/g, "‘").replace(/”/g, "’");'
    for ad in ("vetolar", "simulasyon"):
        s = (WEB / f"{ad}.html").read_text(encoding="utf-8")
        assert tanim in s, ad
        assert not re.search(r"“\$\{esc\((?!icTirnak\()[^`]*?metin_(tr|en)", s), ad
    vet = (WEB / "vetolar.html").read_text(encoding="utf-8")
    assert "metin: icTirnak(DIL === \"en\" && a.metin_en ? a.metin_en : a.metin_tr)" in vet  # hitap.aria
    tek = (WEB / "veto-atlasi-tek-dosya.html").read_text(encoding="utf-8")
    assert tek.count(tanim.replace('"', '\\"')) == 2  # tek dosya iki sayfanın güncel hâlini taşır
    # Paylaşım kartları: alıntı gövdesinde çift tırnak yok (dış tırnak CSS'te)
    kartlar = sorted((WEB / "kartlar").glob("kart-*-alinti-*.html"))
    assert kartlar
    for yol in kartlar:
        govde = re.search(r'<div class="buyuk alinti"[^>]*>(.*?)</div>', yol.read_text(encoding="utf-8"), re.S)[1]
        assert "“" not in govde and "”" not in govde, yol.name
    assert "‘Dünya 5’ten Büyüktür.’" in (WEB / "kartlar/kart-08-alinti-2019-tr-1200x630.html").read_text(encoding="utf-8")


# K18 (21 Ekim 2026, kullanıcı kararı; KILAVUZ "Kesme ve tırnak"): kurum, kuruluş ve kurul adlarına gelen ekler kesmeyle
# ayrılmaz (TDK): "Güvenlik Konseyinde", "Konseyin", "Genel Kurulda", "Afrika Grubunun". Kısaltma, ülke ve devlet, kişi, yer,
# sayfa, belge ve bölüm adları kesmeli kalır (BM’nin, Türkiye’nin, Sovyetler Birliği’nin, Söz ve Kayıt’ın, Ezulwini Uzlaşısı’nı).
KURUM_KESME = re.compile(r"\b(?:Konseyi?|Kurulu?|Grubu|Bakanlığı|Merkezi|Komisyonu|Kütüphanesi|Sekreterliği|Meclisi|Örgütü|"
                         r"Mahkemesi|Afrika Birliği|Başkanlığı|Paneli|Teşkilatı|Divanı|Hükümeti|Kurumu|Dairesi|Komitesi|Konferansı|Ajansı)['’]\w")
ALINTI_TIRNAK = re.compile(r"“[^”]*”")  # alıntı tırnağı içi kaynaktaki gibi kalır


def _dizgeler(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from _dizgeler(v)
    elif isinstance(x, list):
        for v in x:
            yield from _dizgeler(v)


def test_kurum_adlarina_gelen_ek_kesmesiz():
    """Türkçe görünen metinde kesmeli kurum biçimi kalmaz: sayfa sözlükleri ve meta açıklamalar (sekiz sayfa, 404, giriş),
    kayıt verisi (notlar, gündem adları, düzeltmeler, reform modelleri, Genel Kurul tartışmaları; alıntı bankası hariç), Temsil
    verisi, paylaşım kartları, açık veri dosyaları ve veri sözlüğü, METODOLOJI, README, KAYNAKLAR ve KILAVUZ. Alıntı tırnağı
    (“…”) içindeki metin ve alıntı bankası kaynaktaki gibidir, denetlenmez."""
    assert KURUM_KESME.search("Güvenlik Konseyi’nde") and KURUM_KESME.search("Konsey’in") and KURUM_KESME.search("Genel Kurul’da")
    assert KURUM_KESME.search("BM Genel Kurulu’nda") and KURUM_KESME.search("Afrika Grubu’nun") and KURUM_KESME.search("Konsey'de")
    assert KURUM_KESME.search("Dışişleri Bakanlığı’nın") and KURUM_KESME.search("Afrika Birliği’nin")
    assert KURUM_KESME.search("Genel Kurul Başkanlığı’nın") and KURUM_KESME.search("Uzmanlar Paneli’nin")
    for dogru in ("Güvenlik Konseyinde", "Konseyin", "Genel Kurulda", "Afrika Grubunun", "BM’nin", "Türkiye’nin", "Sovyetler Birliği’nin",
                  "Rusya Federasyonu’nun", "Söz ve Kayıt’ın", "Ezulwini Uzlaşısı’nı", "2. Bölüm’de", "Genel Sekreter’in", "Council’s"):
        assert not KURUM_KESME.search(dogru), dogru
    bulunan = []

    def bak(ad, metin):
        bulunan.extend((ad, m[0]) for m in KURUM_KESME.finditer(ALINTI_TIRNAK.sub(" ", metin)))

    for ad in SAYFALAR + ["404", "index"]:
        bak(ad, (WEB / f"{ad}.html").read_text(encoding="utf-8"))
    V = _veri()
    bak("veri.js", " ".join(_dizgeler({k: v for k, v in V.items() if k != "alintilar"})))
    t = (WEB / "temsil_veri.js").read_text(encoding="utf-8")
    bak("temsil_veri.js", " ".join(_dizgeler(json.loads(t[t.index("{"):t.rindex("}") + 1]))))
    bak("kartlar.json", " ".join(_dizgeler(json.loads((WEB / "kartlar/kartlar.json").read_text(encoding="utf-8")))))
    for yol in sorted((WEB / "veri").glob("*.csv")) + sorted((KOK / "kaynaklar").glob("*.csv")):
        if not yol.name.startswith("alintilar"):
            bak(yol.name, yol.read_text(encoding="utf-8-sig"))
    for md in ("METODOLOJI.md", "README.md", "kaynaklar/KAYNAKLAR.md", "kaynaklar/kimlik/KILAVUZ.md", "kaynaklar/kart_katalogu.md"):
        bak(md, (KOK / md).read_text(encoding="utf-8"))
    assert not bulunan, bulunan
