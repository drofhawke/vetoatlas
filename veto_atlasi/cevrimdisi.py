"""
İnternetsiz çalışma: web/cevrimdisi.js (service worker) üretir.

Site sunucuda açıldığında web/cubuk.js bu betiği kaydeder (tek dosyada ve dosya olarak açılışta kaydetmez). Strateji önce
ağdır: internet varken her istek her zamanki gibi sunucudan gelir; internet yokken sayfalar ve onların kullandığı dosyalar
(betikler, stiller, yazı tipleri, veri, logolar, ikonlar) kayıtlı kopyadan sunulur. Kaydedilecek dosyaların listesi sayfaların
kendisinden çıkarılır; sürüm, bu dosyaların içeriğinin SHA-256 özetidir: biri değişince tarayıcı yeni sürümü indirir ve eski
kopyayı siler. Paylaşım kartları, indirme dosyaları (web/veri/) ve tek dosya kaydedilmez. Betik yalnızca site içi isteklere
karışır; dış adres içermez.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

SAYFALAR = ["hikaye", "vetolar", "vizyon", "reform", "simulasyon", "temsil", "hakkinda", "metodoloji"]
_ETIKET = re.compile(r"<(?:script|link)\b[^>]*>", re.I)
_ADRES = re.compile(r'\b(?:src|href)="([^"]+)"')
_CSS_URL = re.compile(r"url\(\s*['\"]?([^'\")]+)")
_CUBUK_GORSEL = re.compile(r'gorsel\("[^"]+", "([^"]+)"')

SABLON = """/*
 * Veto Atlası – internetsiz çalışma (service worker). veto_atlasi/cevrimdisi.py üretir; elle düzenlenmez.
 * Önce ağ: internet varken istekler sunucudan gelir; internet yokken sayfalar ve kullandıkları dosyalar kayıtlı kopyadan
 * sunulur. Yalnızca site içi GET isteklerine karışır.
 */
"use strict";
const SURUM = "veto-atlasi-__SURUM__";
const SAYFALAR = __SAYFALAR__;
const DOSYALAR = __DOSYALAR__;

self.addEventListener("install", (olay) => {
  olay.waitUntil((async () => {
    const depo = await caches.open(SURUM);
    await Promise.all(DOSYALAR.map(async (yol) => {
      const yanit = await fetch(yol, { cache: "reload" });
      if (!yanit.ok) throw new Error(yol + " " + yanit.status);
      await depo.put(yol, yanit);
    }));
    // Sayfalar uzantısız adresten alınır (sunucu .html adresini oraya yönlendirir); kopya iki adla ve hikâye kök adla da saklanır
    await Promise.all(SAYFALAR.map(async (yol) => {
      const yanit = await fetch(yol, { cache: "reload" });
      if (!yanit.ok) throw new Error(yol + " " + yanit.status);
      const govde = await yanit.blob();
      const kopya = () => new Response(govde, { status: 200, headers: yanit.headers });
      await depo.put(yol, kopya());
      await depo.put(yol + ".html", kopya());
      if (yol === "/hikaye") await depo.put("/", kopya());
    }));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (olay) => {
  olay.waitUntil((async () => {
    for (const ad of await caches.keys()) {
      if (ad.startsWith("veto-atlasi-") && ad !== SURUM) await caches.delete(ad);
    }
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (olay) => {
  const istek = olay.request;
  const adres = new URL(istek.url);
  if (istek.method !== "GET" || adres.origin !== self.location.origin) return;
  olay.respondWith(fetch(istek).catch(async () => {
    const kayitli = await (await caches.open(SURUM)).match(adres.pathname);
    return kayitli || Response.error();
  }));
});
"""


def _yerel(adres: str) -> str | None:
    """Sayfadaki göreli adresi site köküne göre yola çevirir; dış ve özel adresler None."""
    if re.match(r"^[a-z][a-z0-9+.-]*:", adres, re.I) or adres.startswith(("#", "//")):
        return None
    return "/" + adres.split("?")[0].split("#")[0].lstrip("./")


def listeler(web: Path) -> tuple[list[str], list[str]]:
    """(sayfalar, dosyalar): uzantısız sayfa yolları ve sayfaların kullandığı yerel dosyalar (sıralı, tekrarsız)."""
    dosyalar: set[str] = set()
    for ad in SAYFALAR:
        s = (web / f"{ad}.html").read_text(encoding="utf-8")
        for etiket in _ETIKET.findall(s):
            if re.search(r'\brel="(?:canonical|alternate)"', etiket):
                continue
            for adres in _ADRES.findall(etiket):
                yol = _yerel(adres)
                if yol:
                    dosyalar.add(yol)
    # Stillerin istediği yazı tipleri (adres stil dosyasının klasörüne göre)
    for yol in sorted(d for d in dosyalar if d.endswith(".css")):
        klasor = Path(yol).parent.as_posix().rstrip("/")
        for adres in _CSS_URL.findall((web / yol.lstrip("/")).read_text(encoding="utf-8")):
            ic = _yerel(adres)
            if ic:
                dosyalar.add(f"{klasor}/{ic.lstrip('/')}" if klasor else ic)
    # Çubuğun çizdiği logolar ve manifestteki uygulama ikonları
    dosyalar.update("/" + ad for ad in _CUBUK_GORSEL.findall((web / "cubuk.js").read_text(encoding="utf-8")))
    if "/site.webmanifest" in dosyalar:
        manifest = json.loads((web / "site.webmanifest").read_text(encoding="utf-8"))
        dosyalar.update("/" + i["src"].lstrip("/") for i in manifest.get("icons", []))
    eksik = sorted(d for d in dosyalar if not (web / d.lstrip("/")).is_file())
    assert not eksik, f"sayfaların istediği dosya yok: {eksik}"
    return ["/" + ad for ad in SAYFALAR], sorted(dosyalar)


METIN_UZANTILARI = {".html", ".js", ".css", ".svg", ".webmanifest", ".json", ".txt"}


def metin(kok: Path) -> str:
    web = kok / "web"
    sayfalar, dosyalar = listeler(web)
    ozet = hashlib.sha256(SABLON.encode("utf-8"))
    for yol in [f"{s}.html" for s in sayfalar] + dosyalar:
        veri = (web / yol.lstrip("/")).read_bytes()
        # Metin dosyalarında satır sonu git'teki gibi LF sayılır: CRLF'li bir Windows çalışma ağacı da aynı sürümü verir
        if Path(yol).suffix in METIN_UZANTILARI:
            veri = veri.replace(b"\r\n", b"\n")
        ozet.update(yol.encode("utf-8") + b"\0" + veri)
    return (SABLON.replace("__SURUM__", ozet.hexdigest()[:16])
            .replace("__SAYFALAR__", json.dumps(sayfalar, ensure_ascii=False))
            .replace("__DOSYALAR__", json.dumps(dosyalar, ensure_ascii=False)))


def yaz(kok: Path) -> Path:
    hedef = kok / "web/cevrimdisi.js"
    hedef.write_text(metin(kok), encoding="utf-8", newline="\n")
    return hedef
