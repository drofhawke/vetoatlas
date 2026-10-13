/*
 * Veto Atlası ortak üst çubuk ve tema (kaynaklar/kimlik/KILAVUZ.md).
 *
 * Her sayfa <head> içinde bu betiği yükler ve <body> başında <header id="cubuk" class="cubuk"></header> taşır.
 * Çubuk: solda logo (ana sayfaya bağlantı), sağda sayfa bağlantıları, en sağda TR/EN ve tema düğmesi.
 * Logo iki parçadır: işaret satır içi SVG (isaret-kucuk.svg geometrisi), ad HTML metni; renkler temadan gelir.
 * Çubuğun üstünde ince beta şeridi (hata bildirimi adresiyle); sayfayla kayar, yazdırılmaz.
 * Dar ekranda sayfa bağlantıları "Menü" düğmesine toplanır; çok dar ekranda yalnızca işaret görünür.
 * Yazdırmada çubuktan yalnızca logo (işaret ve ad) basılır.
 *
 * Tema: site her zaman kâğıt (açık) temada açılır; işletim sisteminin koyu tema tercihi dikkate alınmaz.
 * Koyu kâğıt yalnızca çubuktaki düğmeyle seçilir ve localStorage'da hatırlanır (erişilemezse açık kalır).
 *
 * Tek dosya sürümü (veto_atlasi/tek_dosya.py): üst belge aynı çubuğu VetoCubuk.kur({ tek: {...} }) ile kurar ve
 * sekme geçişini oradan yapar; sayfa çerçevelerinde window.__CUBUK_GIZLI tanımlıdır, çubuk çizilmez ve tema üst
 * belgeden (window.__TEMA, "tema" iletisi) gelir.
 */
(function () {
  "use strict";
  var KOK = document.documentElement;
  var ANAHTAR = "veto-atlasi-tema";

  // ---------- Tema ----------
  function temaOku() {
    if (window.__TEMA === "koyu" || window.__TEMA === "kagit") return window.__TEMA;
    try { return window.localStorage.getItem(ANAHTAR) === "koyu" ? "koyu" : "kagit"; } catch (e) { return "kagit"; }
  }
  function temaYaz(v) { try { window.localStorage.setItem(ANAHTAR, v); } catch (e) { /* özel pencere ya da engelli depolama: seçim yalnızca bu sayfada geçerli */ } }
  function temaUygula(v) { if (v === "koyu") KOK.setAttribute("data-theme", "dark"); else KOK.removeAttribute("data-theme"); }
  var tema = temaOku();
  temaUygula(tema);
  window.addEventListener("message", function (e) {
    var m = e.data || {};
    if (m.tur === "tema" && (m.tema === "koyu" || m.tema === "kagit")) { tema = m.tema; temaUygula(tema); }
  });

  // ---------- Stil (bir kez, sayfanın kendi stilinden önce) ----------
  var CSS = [
    ".cubuk { display: block; position: sticky; top: 0; z-index: 20; background: color-mix(in srgb, var(--zemin) 92%, transparent); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px); box-shadow: inset 0 -1px 0 var(--cizgi); font-family: var(--sans); font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); min-height: 76px; }",
    ".c-cubuklu { scroll-padding-top: 84px; }",
    "/* Beta şeridi: çubuğun üstünde, yapışkan değil (sayfayla kayar); 32 px */",
    ".beta-serit { display: block; flex: none; background: var(--yuzey); box-shadow: inset 0 -1px 0 var(--cizgi); color: var(--murekkep-2); font-family: var(--sans); font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); }",
    ".beta-serit .beta-ic { max-width: 1180px; margin: 0 auto; padding: 4px 24px; }",
    ".beta-serit a { color: var(--murekkep); text-underline-offset: 3px; }",
    ".beta-serit a:focus-visible { outline: 2px solid var(--murekkep); outline-offset: 2px; }",
    ".cubuk-ic { max-width: 1180px; margin: 0 auto; padding: 12px 24px; display: flex; align-items: center; gap: 24px; min-height: 76px; }",
    ".cubuk a { color: inherit; }",
    "/* Logo: işaret (satır içi SVG, 40 px) ve ad (Source Serif 4 600, 26 px); işaretteki kırmızı kare marka rengidir */",
    ".cubuk { --c-isaret-kirmizi: #A4262C; }",
    ":root[data-theme=\"dark\"] .cubuk { --c-isaret-kirmizi: #E05A52; }",
    ".cubuk .c-logo { display: inline-flex; align-items: center; gap: 12px; flex: none; text-decoration: none; color: var(--murekkep); }",
    ".cubuk .c-logo .c-isaret { display: block; flex: none; width: 40px; height: 40px; }",
    ".cubuk .c-logo .c-isaret .c-ik { fill: var(--murekkep); }",
    ".cubuk .c-logo .c-isaret .c-iv { fill: var(--c-isaret-kirmizi); }",
    ".cubuk .c-logo .c-ad { display: block; font-family: var(--serif); font-weight: 600; font-size: 26px; line-height: 40px; color: var(--murekkep); white-space: nowrap; }",
    ".cubuk .c-not { font-size: var(--yz-kucuk); color: var(--murekkep-2); white-space: nowrap; flex: none; line-height: var(--sa-kucuk); }",
    ".cubuk .c-sayfalar { margin-left: auto; }",
    ".cubuk .c-sayfalar ul { list-style: none; margin: 0; padding: 0; display: flex; gap: 12px; }",
    ".cubuk .c-sayfalar li { margin: 0; padding: 0; max-width: none; }",
    ".cubuk .c-sayfalar a { display: block; text-decoration: none; color: var(--murekkep); white-space: nowrap; padding: 8px 0; border-bottom: 2px solid transparent; }",
    ".cubuk .c-sayfalar a:hover { border-bottom-color: var(--cizgi); }",
    ".cubuk .c-sayfalar a[aria-current=\"page\"] { color: var(--murekkep); border-bottom-color: var(--murekkep); font-weight: 600; }",
    ".cubuk .c-araclar { display: inline-flex; gap: 8px; align-items: center; flex: none; margin-left: 8px; }",
    ".cubuk .c-dil { display: inline-flex; gap: 8px; }",
    ".cubuk .c-dil a, .cubuk .c-tema, .cubuk .c-menu { font: inherit; font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); padding: 4px 8px; border: 1px solid var(--cizgi); border-radius: 999px; background: transparent; color: var(--murekkep); text-decoration: none; cursor: pointer; white-space: nowrap; }",
    ".cubuk .c-dil a[aria-current=\"true\"] { background: var(--murekkep); color: var(--zemin); border-color: var(--murekkep); }",
    ".cubuk .c-tema[aria-pressed=\"true\"] { border-color: var(--murekkep); box-shadow: inset 0 0 0 1px var(--murekkep); }",
    ".cubuk .c-tema::before { content: \"\"; display: inline-block; width: 8px; height: 8px; border-radius: 50%; border: 1.5px solid currentColor; background: linear-gradient(90deg, currentColor 50%, transparent 50%); margin-right: 8px; vertical-align: -1px; }",
    ".cubuk .c-menu { display: none; margin-left: auto; }",
    ".cubuk :focus-visible { outline: 2px solid var(--murekkep); outline-offset: 2px; }",
    "/* Menü kipi (.c-dar): bağlantılar tek satıra sığmadığında betik ölçerek açar */",
    ".cubuk.c-dar .c-araclar { margin-left: 0; }",
    ".cubuk.c-notsuz .c-not { display: none; }",
    "@media all {",
    "  .cubuk.c-dar .c-menu { display: inline-block; }",
    "  .cubuk.c-dar .c-sayfalar { display: none; position: absolute; top: 100%; left: 0; right: 0; margin: 0; background: var(--zemin); border-bottom: 1px solid var(--cizgi); box-shadow: 0 6px 14px rgba(0, 0, 0, .08); }",
    "  .cubuk.c-dar.c-menu-acik .c-sayfalar { display: block; }",
    "  .cubuk.c-dar .c-sayfalar ul { flex-direction: column; gap: 0; max-width: 1180px; margin: 0 auto; padding: 8px 24px 12px; }",
    "  .cubuk.c-dar .c-sayfalar a { padding: 12px 0; border-bottom: 1px solid var(--cizgi); font-size: var(--yz-govde); line-height: var(--sa-govde); }",
    "  .cubuk.c-dar .c-sayfalar li:last-child a { border-bottom: 0; }",
    "  .cubuk.c-dar .c-sayfalar a[aria-current=\"page\"] { border-bottom-color: var(--cizgi); box-shadow: inset 3px 0 0 var(--murekkep); padding-left: 12px; }",
    "}",
    "@media (max-width: 760px) {",
    "  .cubuk-ic { padding: 12px 16px; gap: 12px; }",
    "  .cubuk.c-dar .c-sayfalar ul { padding: 4px 16px 8px; }",
    "  .cubuk .c-not { display: none; }",
    "  .beta-serit .beta-ic { padding: 4px 16px; }",
    "}",
    "@media (max-width: 520px) {",
    "  .cubuk { min-height: 64px; }",
    "  .cubuk-ic { min-height: 64px; }",
    "  .c-cubuklu { scroll-padding-top: 72px; }",
    "  .cubuk .c-logo .c-isaret { width: 32px; height: 32px; }",
    "  .cubuk .c-logo .c-ad { display: none; }",
    "  .cubuk .c-araclar { gap: 8px; }",
    "  .cubuk .c-dil a, .cubuk .c-tema, .cubuk .c-menu { padding: 4px 8px; }",
    "  .cubuk .c-araclar { margin-left: 0; }",
    "}",
    "@media print {",
    "  .beta-serit, .cubuk .c-sayfalar, .cubuk .c-menu, .cubuk .c-araclar, .cubuk .c-not { display: none !important; }",
    "  .cubuk { position: static; min-height: 0; background: none; -webkit-backdrop-filter: none; backdrop-filter: none; box-shadow: none; }",
    "  .cubuk-ic { min-height: 0; padding: 0 0 16px; }",
    "  .cubuk .c-logo { --murekkep: #13213A; --c-isaret-kirmizi: #A4262C; }",
    "  .cubuk .c-logo .c-isaret { width: 40px; height: 40px; }",
    "  .cubuk .c-logo .c-ad { display: block; }",
    "}",
  ].join("\n");
  var stil = document.createElement("style");
  stil.id = "cubuk-stil";
  stil.textContent = CSS;
  (document.head || KOK).insertBefore(stil, (document.head || KOK).firstChild);

  // ---------- Çubuk ----------
  var SAYFALAR = [
    ["hikaye", "Hikâye", "Story"],
    ["vetolar", "Vetolar", "Vetoes"],
    ["vizyon", "Söz ve Kayıt", "Word and Record"],
    ["reform", "Reform modelleri", "Reform models"],
    ["simulasyon", "Ya veto olmasaydı?", "What if there were no veto?"],
    ["temsil", "Kim temsil ediliyor?", "Who is represented?"],
    ["hakkinda", "Nasıl yaptık?", "How we did it"],
  ];
  var YAZI = {
    tr: { logo: "Veto Atlası", ana: "Veto Atlası, ana sayfa", sayfalar: "Sayfalar", dil: "Dil", menu: "Menü", beta: "Beta sürümü", hata: "Hata bildirin",
          tema: "Koyu", temaUzun: "Koyu kâğıt teması", not: "İnceleme sürümü", notUzun: "İnceleme sürümü: sekiz sayfa yedi sekmede, tek dosyada. Paylaşım kartları bu dosyada yer almaz (web/kartlar/)." },
    en: { logo: "Veto Atlas", ana: "Veto Atlas, home", sayfalar: "Pages", dil: "Language", menu: "Menu", beta: "Beta", hata: "Report an error",
          tema: "Dark", temaUzun: "Dark paper theme", not: "Review version", notUzun: "Review version: eight pages in seven tabs, in one file. Share cards are not included (web/kartlar/)." },
  };
  var SAYFA_GRUBU = { metodoloji: "hakkinda", index: "hikaye" };
  var ILETISIM = "iletisim@vetoatlas.com";

  // İşaret: kaynaklar/kimlik/isaret-kucuk.svg geometrisi (viewBox 128; kare 18.56, köşe 3.16), [x, y, açı, dönme merkezi x, y].
  // On dört kare mürekkep, sonuncusu kırmızı; renkler CSS'ten (koyu kâğıtta değişir). Satır içi çizildiği için görüntü
  // yeniden örneklenmez; geometricPrecision kenarları kesirli ölçekte de düzgün yumuşatır.
  var KARELER = [
    [54.72, 21.44, 0, 64, 30.72], [69.82, 24.65, 24, 79.1, 33.93], [82.31, 33.72, 48, 91.59, 43], [90.02, 47.09, 72, 99.3, 56.37],
    [91.64, 62.44, 96, 100.92, 71.72], [86.87, 77.12, 120, 96.15, 86.4], [76.54, 88.59, 144, 85.82, 97.87], [62.44, 94.87, 168, 71.72, 104.15],
    [47, 94.87, 192, 56.28, 104.15], [32.9, 88.59, 216, 42.18, 97.87], [22.57, 77.12, 240, 31.85, 86.4], [17.8, 62.44, 264, 27.08, 71.72],
    [19.42, 47.09, 288, 28.7, 56.37], [27.13, 33.72, 312, 36.41, 43], [34.94, 14.13, 336, 44.22, 23.41],
  ];
  function isaretSvg() {
    var kare = function (k) { return '<rect x="' + k[0] + '" y="' + k[1] + '" width="18.56" height="18.56" rx="3.16" transform="rotate(' + k[2] + " " + k[3] + " " + k[4] + ')"/>'; };
    return '<svg class="c-isaret" viewBox="0 0 128 128" width="40" height="40" shape-rendering="geometricPrecision" aria-hidden="true" focusable="false">' +
      '<g class="c-ik">' + KARELER.slice(0, 14).map(kare).join("") + '</g><g class="c-iv">' + kare(KARELER[14]) + "</g></svg>";
  }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function gecerliDil() {
    var d = window.__DIL || (new URL(location.href)).searchParams.get("lang");
    return d === "en" ? "en" : "tr";
  }
  function gecerliSayfa() {
    var s = (document.body && document.body.getAttribute("data-sayfa")) || (location.pathname.split("/").pop() || "").replace(/\.html$/, "") || "hikaye";
    return SAYFA_GRUBU[s] || s;
  }
  // Dil bağlantısı tıklama anında hesaplanır: sayfanın adres çubuğuna yazdığı parametreler (ör. ?kayit=) ve bölüm korunur
  function dilAdresi(d) {
    var u = new URL(location.href);
    if (d === "tr") u.searchParams.delete("lang"); else u.searchParams.set("lang", d);
    var q = u.searchParams.toString();
    return (u.pathname.split("/").pop() || "hikaye.html") + (q ? "?" + q : "") + u.hash;
  }

  function kur(secenek) {
    secenek = secenek || {};
    var yer = document.getElementById("cubuk");
    if (!yer) return;
    var dil = secenek.dil || gecerliDil(), Y = YAZI[dil];
    var sayfa = SAYFA_GRUBU[secenek.sayfa] || secenek.sayfa || gecerliSayfa();
    var tek = secenek.tek || null;
    var ek = dil === "tr" ? "" : "?lang=" + dil;
    yer.classList.add("cubuk");
    yer.classList.remove("c-menu-acik");
    // Beta şeridi çubuğun hemen önünde; yeniden kurulumda (tek dosyada dil değişimi) aynı öğe güncellenir
    var serit = document.getElementById("beta-serit");
    if (!serit) { serit = document.createElement("div"); serit.id = "beta-serit"; serit.className = "beta-serit"; yer.parentNode.insertBefore(serit, yer); }
    serit.innerHTML = '<div class="beta-ic">' + esc(Y.beta) + " · " + esc(Y.hata) + ': <a href="mailto:' + ILETISIM + '">' + ILETISIM + "</a></div>";
    // Yayın adresi (vetoatlas.com): İngilizce görünümde canonical ve og:url ?lang=en adresini gösterir
    if (!tek && dil === "en") {
      var can = document.querySelector('link[rel="canonical"]'), og = document.querySelector('meta[property="og:url"]');
      if (can) can.setAttribute("href", can.getAttribute("href").split("?")[0] + "?lang=en");
      if (og) og.setAttribute("content", og.getAttribute("content").split("?")[0] + "?lang=en");
    }
    yer.innerHTML =
      '<div class="cubuk-ic">' +
        '<a class="c-logo" href="hikaye.html' + ek + '" data-sayfa="hikaye" aria-label="' + esc(Y.ana) + '">' +
          isaretSvg() + '<span class="c-ad">' + esc(Y.logo) + "</span></a>" +
        (tek ? '<span class="c-not" title="' + esc(Y.notUzun) + '">' + esc(Y.not) + "</span>" : "") +
        '<button type="button" class="c-menu" aria-expanded="false" aria-controls="cubuk-sayfalar">' + esc(Y.menu) + "</button>" +
        '<nav class="c-sayfalar" id="cubuk-sayfalar" aria-label="' + esc(Y.sayfalar) + '"><ul>' +
          SAYFALAR.map(function (s) {
            return '<li><a href="' + s[0] + ".html" + ek + '" data-sayfa="' + s[0] + '"' + (s[0] === sayfa ? ' aria-current="page"' : "") + ">" + esc(dil === "tr" ? s[1] : s[2]) + "</a></li>";
          }).join("") +
        "</ul></nav>" +
        '<span class="c-araclar">' +
          '<span class="c-dil" role="group" aria-label="' + esc(Y.dil) + '">' +
            ["tr", "en"].map(function (d) { return '<a href="' + esc(tek ? "#" : dilAdresi(d)) + '" lang="' + d + '" data-dil="' + d + '"' + (d === dil ? ' aria-current="true"' : "") + ">" + d.toUpperCase() + "</a>"; }).join("") +
          "</span>" +
          '<button type="button" class="c-tema" aria-pressed="' + (tema === "koyu") + '" aria-label="' + esc(Y.temaUzun) + '" title="' + esc(Y.temaUzun) + '">' + esc(Y.tema) + "</button>" +
        "</span>" +
      "</div>";

    var menu = yer.querySelector(".c-menu");
    function menuKapat() { yer.classList.remove("c-menu-acik"); menu.setAttribute("aria-expanded", "false"); }
    menu.addEventListener("click", function () {
      var ac = !yer.classList.contains("c-menu-acik");
      yer.classList.toggle("c-menu-acik", ac); menu.setAttribute("aria-expanded", String(ac));
    });
    yer.addEventListener("keydown", function (e) { if (e.key === "Escape" && yer.classList.contains("c-menu-acik")) { menuKapat(); menu.focus(); } });
    if (!kur.disariBagli) {
      kur.disariBagli = true;
      document.addEventListener("click", function (e) { var c = document.getElementById("cubuk"); if (c && c.classList.contains("c-menu-acik") && !c.contains(e.target)) { c.classList.remove("c-menu-acik"); var m = c.querySelector(".c-menu"); if (m) m.setAttribute("aria-expanded", "false"); } });
    }
    yer.querySelectorAll("a[data-sayfa]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        menuKapat();
        if (tek) { e.preventDefault(); tek.git(a.getAttribute("data-sayfa")); }
      });
    });
    yer.querySelectorAll("a[data-dil]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        var d = a.getAttribute("data-dil");
        if (d === dil) return;
        if (tek) tek.dil(d); else location.href = dilAdresi(d);
      });
    });
    KOK.classList.add("c-cubuklu");
    sigdir();
    yer.querySelector(".c-tema").addEventListener("click", function () {
      tema = tema === "koyu" ? "kagit" : "koyu";
      temaUygula(tema); temaYaz(tema);
      this.setAttribute("aria-pressed", String(tema === "koyu"));
      if (tek && tek.tema) tek.tema(tema);
    });
  }

  // Bağlantılar çubuğa tek satırda sığmıyorsa önce inceleme notu (tek dosya) gizlenir, yine sığmıyorsa menü kipine
  // geçilir; menü kipinde not yeniden görünür (dil ve yazı tipine göre genişlik değişir)
  function sigdir() {
    var c = document.getElementById("cubuk"); if (!c) return;
    var ic = c.querySelector(".cubuk-ic"); if (!ic) return;
    var acikti = c.classList.contains("c-menu-acik");
    var tasiyor = function () { return ic.scrollWidth > ic.clientWidth + 1; };
    c.classList.remove("c-dar", "c-notsuz");
    var dar = false;
    if (tasiyor() && c.querySelector(".c-not")) { c.classList.add("c-notsuz"); }
    if (tasiyor()) { c.classList.remove("c-notsuz"); c.classList.add("c-dar"); dar = true; }
    if (!dar && acikti) { c.classList.remove("c-menu-acik"); var m = c.querySelector(".c-menu"); if (m) m.setAttribute("aria-expanded", "false"); }
  }
  window.addEventListener("resize", sigdir);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(sigdir);
  window.addEventListener("load", sigdir);

  window.VetoCubuk = { kur: kur, tema: function () { return tema; } };
  function basla() {
    if (window.__CUBUK_GIZLI) { var c = document.getElementById("cubuk"); if (c) c.remove(); return; }
    if (!window.__CUBUK_ELLE) kur();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", basla); else basla();
})();
