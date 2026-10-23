/*
 * Veto Atlası – internetsiz çalışma (service worker). veto_atlasi/cevrimdisi.py üretir; elle düzenlenmez.
 * Önce ağ: internet varken istekler sunucudan gelir; internet yokken sayfalar ve kullandıkları dosyalar kayıtlı kopyadan
 * sunulur. Ağ 4 saniyede yanıt vermezse kayıtlı kopya verilir; internet yokken kaydı olmayan bir sayfa adresinde 404 sayfası
 * açılır. Yalnızca site içi GET isteklerine karışır.
 */
"use strict";
const SURUM = "veto-atlasi-34a484724d0f88bd";
const SAYFALAR = ["/hikaye", "/vetolar", "/vizyon", "/temsil", "/reform", "/simulasyon", "/hakkinda", "/metodoloji"];
const DOSYALAR = ["/apple-touch-icon.png", "/cubuk.js", "/favicon.ico", "/favicon.svg", "/fonts/fonts.css", "/fonts/source-sans-3-latin-400-italic.woff2", "/fonts/source-sans-3-latin-400-normal.woff2", "/fonts/source-sans-3-latin-500-normal.woff2", "/fonts/source-sans-3-latin-600-normal.woff2", "/fonts/source-sans-3-latin-ext-400-italic.woff2", "/fonts/source-sans-3-latin-ext-400-normal.woff2", "/fonts/source-sans-3-latin-ext-500-normal.woff2", "/fonts/source-sans-3-latin-ext-600-normal.woff2", "/fonts/source-serif-4-latin-400-normal.woff2", "/fonts/source-serif-4-latin-600-normal.woff2", "/fonts/source-serif-4-latin-ext-400-normal.woff2", "/fonts/source-serif-4-latin-ext-600-normal.woff2", "/fonts/veto-atlasi-logo.woff2", "/harita_veri.js", "/icon-192.png", "/icon-512.png", "/icon-maskable-192.png", "/icon-maskable-512.png", "/isaret-koyu.svg", "/isaret.svg", "/metin.js", "/site.webmanifest", "/suzgec.js", "/temel.css", "/temsil_veri.js", "/veri.js"];
const YEDEK = "/404";
const BEKLEME = 4000;

self.addEventListener("install", (olay) => {
  olay.waitUntil((async () => {
    const depo = await caches.open(SURUM);
    await Promise.all(DOSYALAR.map(async (yol) => {
      const yanit = await fetch(yol, { cache: "no-cache" });
      if (!yanit.ok) throw new Error(yol + " " + yanit.status);
      await depo.put(yol, yanit);
    }));
    // Sayfalar uzantısız adresten alınır (sunucu .html adresini oraya yönlendirir); kopya iki adla ve hikâye kök adla da saklanır
    await Promise.all(SAYFALAR.map(async (yol) => {
      const yanit = await fetch(yol, { cache: "no-cache" });
      if (!yanit.ok) throw new Error(yol + " " + yanit.status);
      const govde = await yanit.blob();
      const kopya = () => new Response(govde, { status: 200, headers: yanit.headers });
      await depo.put(yol, kopya());
      await depo.put(yol + ".html", kopya());
      if (yol === "/hikaye") await depo.put("/", kopya());
    }));
    // 404 sayfası alınamazsa kurulum yine tamamlanır; internetsizken bilinmeyen adres tarayıcı hatası verir
    try {
      const yanit = await fetch(YEDEK, { cache: "no-cache" });
      const govde = await yanit.blob();
      await depo.put(YEDEK, new Response(govde, { status: 404, headers: yanit.headers }));
    } catch (hata) { /* yedek sayfa yok */ }
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
  olay.respondWith((async () => {
    const depo = await caches.open(SURUM);
    const ag = fetch(istek);
    ag.catch(() => {});
    const sure = new Promise((coz) => setTimeout(coz, BEKLEME));
    try {
      return await Promise.race([ag, sure.then(async () => (await depo.match(adres.pathname)) || ag)]);
    } catch (hata) {
      const kayitli = await depo.match(adres.pathname);
      if (kayitli) return kayitli;
      const yedek = istek.mode === "navigate" ? await depo.match(YEDEK) : undefined;
      return yedek || Response.error();
    }
  })());
});
