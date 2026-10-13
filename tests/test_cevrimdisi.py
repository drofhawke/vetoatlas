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
    assert sayfalar == ["/hikaye", "/vetolar", "/vizyon", "/reform", "/simulasyon", "/temsil", "/hakkinda", "/metodoloji"]
    for yol in dosyalar:
        assert (WEB / yol.lstrip("/")).is_file(), yol
    assert not any(y.startswith(("/kartlar/", "/veri/")) or "tek-dosya" in y or y.endswith(".html") for y in dosyalar)
    for gerekli in ("/cubuk.js", "/temel.css", "/metin.js", "/veri.js", "/temsil_veri.js", "/fonts/fonts.css", "/logo-cubuk-b.svg",
                    "/logo-cubuk-b-koyu.svg", "/isaret.svg", "/isaret-koyu.svg", "/site.webmanifest", "/icon-maskable-512.png"):
        assert gerekli in dosyalar, gerekli
    # fonts.css'teki her yazı tipi dosyası kayıtlı
    css = (WEB / "fonts/fonts.css").read_text(encoding="utf-8")
    assert {"/fonts/" + f for f in re.findall(r"url\(\s*['\"]?([^'\")]+\.woff2)", css)} <= set(dosyalar)
    js = (WEB / "cevrimdisi.js").read_text(encoding="utf-8")
    # Yalnızca site içi GET; önce ağ, internet yokken kayıtlı kopya; eski sürümler silinir
    assert "http" not in js and 'if (istek.method !== "GET" || adres.origin !== self.location.origin) return;' in js
    assert "olay.respondWith(fetch(istek).catch(async () => {" in js and '(await caches.open(SURUM)).match(adres.pathname)' in js
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
