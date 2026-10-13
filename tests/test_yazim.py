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
    assert '.map(([u, d]) => `${uyeAdMetin(u)} ${t("gk.konustu." + d)}`)' in vet
    assert "with the negative ${n > 1 ? `votes of ${uye}, permanent members` : `vote of ${uye}, a permanent member`}" in sim
    assert sim.count("As the negative vote of ${uye} is that of a permanent member") == 2 and "the negative vote of ${uye} defeats" in sim
    assert "no veto by ${uye} among the" in sim
