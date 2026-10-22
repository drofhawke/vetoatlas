"""
İnternetsiz çalışma (web/cevrimdisi.js; veto_atlasi/cevrimdisi.py): betik güncel, yalnızca site içi, sayfaların kullandığı her
yerel dosyayı kaydeder; kartlar, indirme dosyaları ve tek dosya kaydedilmez; çubuk betiği yalnızca sunucudaki sayfalarda kaydeder.
"""
import re

from conftest import KOK

from veto_atlasi import cevrimdisi

WEB = KOK / "web"


def test_servis_iscisi_guncel():
    assert (WEB / "cevrimdisi.js").read_text(encoding="utf-8") == cevrimdisi.metin(KOK), \
        "web/cevrimdisi.js eski; python scripts/11_cevrimdisi.py (04 de üretir)"


def test_kayitli_dosyalar_ve_strateji():
    sayfalar, dosyalar = cevrimdisi.listeler(WEB)
    # Sıra üst çubuğun sekme sırası (K4), ardından çubukta olmayan Metodoloji
    assert sayfalar == ["/hikaye", "/vetolar", "/vizyon", "/temsil", "/reform", "/simulasyon", "/hakkinda", "/metodoloji"]
    cubuk = (WEB / "cubuk.js").read_text(encoding="utf-8")
    sekmeler = re.findall(r'^    \["(\w+)", "', cubuk[cubuk.index("var SAYFALAR = ["):], re.M)
    assert ["/" + s for s in sekmeler[:7]] == sayfalar[:7]
    for yol in dosyalar:
        assert (WEB / yol.lstrip("/")).is_file(), yol
    assert not any(y.startswith(("/kartlar/", "/veri/")) or "tek-dosya" in y or y.endswith(".html") for y in dosyalar)
    for gerekli in ("/cubuk.js", "/temel.css", "/metin.js", "/veri.js", "/temsil_veri.js", "/fonts/fonts.css", "/fonts/veto-atlasi-logo.woff2",
                    "/isaret.svg", "/isaret-koyu.svg", "/site.webmanifest", "/icon-maskable-512.png"):
        assert gerekli in dosyalar, gerekli
    for gereksiz in ("/logo-cubuk-b.svg", "/logo-cubuk-b-koyu.svg"):  # çubuk logosu canlı metin oldu (20 Ekim), SVG logo kayıtlı değil
        assert gereksiz not in dosyalar, gereksiz
    # fonts.css'teki her yazı tipi dosyası kayıtlı
    css = (WEB / "fonts/fonts.css").read_text(encoding="utf-8")
    assert {"/fonts/" + f for f in re.findall(r"url\(\s*['\"]?([^'\")]+\.woff2)", css)} <= set(dosyalar)
    js = (WEB / "cevrimdisi.js").read_text(encoding="utf-8")
    # Yalnızca site içi GET; önce ağ, ağ 4 saniyede yanıt vermezse ya da internet yokken kayıtlı kopya; kaydı olmayan sayfa
    # adresinde 404 yedeği; eski sürümler silinir
    assert "http" not in js and 'if (istek.method !== "GET" || adres.origin !== self.location.origin) return;' in js
    assert "const BEKLEME = 4000;" in js and 'const YEDEK = "/404";' in js
    assert "olay.respondWith((async () => {" in js and "const ag = fetch(istek);" in js
    assert "return await Promise.race([ag, sure.then(async () => (await depo.match(adres.pathname)) || ag)]);" in js
    assert "const kayitli = await depo.match(adres.pathname);" in js and 'istek.mode === "navigate" ? await depo.match(YEDEK) : undefined;' in js
    assert "await depo.put(YEDEK, new Response(govde, { status: 404, headers: yanit.headers }));" in js
    assert 'if (ad.startsWith("veto-atlasi-") && ad !== SURUM) await caches.delete(ad);' in js
    assert re.search(r'const SURUM = "veto-atlasi-[0-9a-f]{16}";', js)


def test_surum_satir_sonundan_bagimsiz(tmp_path):
    """Sürüm, CRLF'li bir Windows çalışma ağacında da açık depodaki (LF) ile aynıdır: metin dosyalarında satır sonu LF sayılır."""
    import shutil
    shutil.copytree(WEB, tmp_path / "web", ignore=shutil.ignore_patterns("kartlar", "veri", "veto-atlasi-tek-dosya.html"))
    for p in (tmp_path / "web").rglob("*"):
        if p.is_file() and p.suffix in cevrimdisi.METIN_UZANTILARI:
            v = p.read_bytes().replace(b"\r\n", b"\n")
            p.write_bytes(v.replace(b"\n", b"\r\n"))
    assert cevrimdisi.metin(tmp_path) == cevrimdisi.metin(KOK)


def test_kayit_yalnizca_sunucudaki_sayfalarda():
    c = (WEB / "cubuk.js").read_text(encoding="utf-8")
    assert ('if (!window.__CUBUK_ELLE && window.isSecureContext && location.protocol !== "file:" && "serviceWorker" in navigator) {'
            in c) and 'navigator.serviceWorker.register("cevrimdisi.js")' in c
    # Tek dosyanın üst belgesi çubuğu elle kurar (__CUBUK_ELLE), sayfa çerçeveleri çubuksuzdur (__CUBUK_GIZLI): kayıt yok
    tek = (WEB / "veto-atlasi-tek-dosya.html").read_text(encoding="utf-8")
    assert "<script>window.__CUBUK_ELLE = true;</script>" in tek
