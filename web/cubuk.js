/*
 * Veto Atlası ortak üst çubuk ve tema (kaynaklar/kimlik/KILAVUZ.md).
 *
 * Her sayfa <head> içinde bu betiği yükler ve <body> başında <header id="cubuk" class="cubuk"></header> taşır.
 * Çubuk: solda logo (işaret + canlı logo yazısı; ana sayfaya bağlantı), sağda sayfa bağlantıları, en sağda TR/EN ve tema düğmesi.
 * Her sayfanın altında tek satırlık not (beta sürümü, hata bildirme adresi): sayfanın alt bilgisi varsa ona eklenir, yoksa
 * sayfa kabının sonunda ince çizgili bir alt bilgi oluşturulur. Çubuğun üstündeki beta şeridi 20 Ekim 2026'da kaldırıldı.
 * Dar ekranda sayfa bağlantıları "Menü" düğmesine toplanır; çok dar ekranda logo yerine işaret görünür.
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
  // Tarayıcı çubuğunun rengi (theme-color) temayla birlikte değişir: kâğıt #FBF8F1, koyu kâğıt #1C1A17
  function temaUygula(v) {
    if (v === "koyu") KOK.setAttribute("data-theme", "dark"); else KOK.removeAttribute("data-theme");
    var renk = document.querySelector('meta[name="theme-color"]');
    if (renk) renk.setAttribute("content", v === "koyu" ? "#1C1A17" : "#FBF8F1");
  }
  var tema = temaOku();
  temaUygula(tema);
  window.addEventListener("message", function (e) {
    var m = e.data || {};
    if (m.tur === "tema" && (m.tema === "koyu" || m.tema === "kagit")) { tema = m.tema; temaUygula(tema); }
  });

  // ---------- Dil ----------
  // Seçilen dil tema gibi localStorage'da hatırlanır. Adres parametresi her zaman önce gelir: ?lang=en ile açılan sayfa "en"
  // kaydeder, TR bağlantısına tıklamak "tr" kaydeder. Adreste ?lang yoksa ve kayıt "en" ise adrese ?lang=en yazılır
  // (history.replaceState; sayfa yeniden yüklenmez). Bu betik her sayfada ilk betiktir, sayfa betikleri dili adresten
  // okurken parametre yerindedir; adres yazılamazsa sayfa ?lang=en ile yeniden açılır. Ana ekrandan açılış /hikaye
  // adresine gider. Tek dosya ve sayfa çerçeveleri bu adıma karışmaz.
  var DIL_ANAHTAR = "veto-atlasi-dil";
  function dilYaz(v) { try { window.localStorage.setItem(DIL_ANAHTAR, v); } catch (e) { /* depolama yok: dil yalnızca adresten */ } }
  (function () {
    if (window.__DIL || window.__CUBUK_GIZLI || window.__CUBUK_ELLE || window.self !== window.top) return;
    var u = new URL(location.href), q = u.searchParams.get("lang");
    if (q === "en") { dilYaz("en"); return; }
    if (q) return;
    var kayit = null;
    try { kayit = window.localStorage.getItem(DIL_ANAHTAR); } catch (e) { return; }
    if (kayit !== "en") return;
    u.searchParams.set("lang", "en");
    try { history.replaceState(history.state, "", u.href); } catch (e) { location.replace(u.href); }
  })();

  // ---------- Stil (bir kez, sayfanın kendi stilinden önce) ----------
  var CSS = [
    ".cubuk { display: block; position: sticky; top: 0; z-index: 20; background: color-mix(in srgb, var(--zemin) 92%, transparent); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px); box-shadow: inset 0 -1px 0 var(--cizgi); font-family: var(--sans); font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); min-height: 76px; }",
    ".c-cubuklu { scroll-padding-top: 84px; }",
    "/* Alt bilgi notu: beta sürümü ve hata bildirme adresi, her sayfanın altında tek satır */",
    ".alt-not { font-family: var(--sans); font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); color: var(--murekkep-2); max-width: var(--olcu); margin: 0; }",
    ".alt-not a { color: var(--murekkep); text-underline-offset: 3px; }",
    "footer.alt-bilgi { border-top: 1px solid var(--cizgi); margin: 64px 0 0; padding: 32px 0 0; }",
    ".cubuk-ic { max-width: 1180px; margin: 0 auto; padding: 12px 24px; display: flex; align-items: center; gap: 24px; min-height: 76px; }",
    ".cubuk a { color: inherit; }",
    "/* İçeriğe atlama bağlantısı: ilk odak durağı; odaklanınca çubuğun solunda ikincil düğme olarak görünür */",
    ".cubuk .c-atla { position: absolute; left: 24px; top: -64px; z-index: 30; display: inline-flex; align-items: center; min-height: 48px; padding: 0 24px; background: var(--yuzey, var(--zemin)); color: var(--murekkep); border: 1px solid var(--cizgi); border-radius: 6px; font-family: var(--sans); font-size: var(--yz-govde); line-height: var(--sa-govde); font-weight: 600; text-decoration: none; }",
    ".cubuk .c-atla:focus { top: 16px; }",
    "[data-atla]:focus { outline: none; }",
    "/* Logo: işaret (isaret.svg, 40 px) + canlı logo yazısı. Ölçüler logo-cubuk-b.svg'nin 40 px'e ölçeklenmiş değerleridir: yazı 52/76,19 × 40 = 27,3 px,",
    "   işaretle arası 26,83 birim = 14 px, taban çizgisi işaretin üstünden 54,1 birim = 28,4 px (40 px satır kutusunda 1 px aşağı). Yazı SVG dış çizgisi",
    "   değil canlı metin olduğu için hinting ve ClearType alır; harfler logo paketindeki kesimle aynıdır (Veto Atlası Logo, KILAVUZ bölüm 3) */",
    ".cubuk .c-logo { display: inline-flex; align-items: flex-start; flex: none; height: 40px; text-decoration: none; color: var(--murekkep); }",
    ".cubuk .c-logo img { height: 40px; width: auto; display: block; }",
    ".cubuk .c-logo .c-isaret-koyu { display: none; }",
    ":root[data-theme=\"dark\"] .cubuk .c-logo .c-isaret { display: none; }",
    ":root[data-theme=\"dark\"] .cubuk .c-logo .c-isaret-koyu { display: block; }",
    "/* Sınıf adı c-yazi: reklam engelleyicilerin ortak listesi (EasyList) \"c-ad\" sınıfını genel kuralla gizliyordu (21 Ekim 2026) */",
    ".cubuk .c-logo .c-yazi { font-family: \"Veto Atlası Logo\", var(--serif); font-weight: 600; font-size: 27.3px; line-height: 40px; letter-spacing: .2px; white-space: nowrap; margin-left: 14px; position: relative; top: 1px; }",
    ".cubuk .c-not { font-size: var(--yz-kucuk); color: var(--murekkep-2); white-space: nowrap; flex: none; line-height: var(--sa-kucuk); }",
    ".cubuk .c-sayfalar { margin-left: auto; }",
    ".cubuk .c-sayfalar ul { list-style: none; margin: 0; padding: 0; display: flex; gap: 12px; }",
    ".cubuk .c-sayfalar li { margin: 0; padding: 0; max-width: none; }",
    ".cubuk .c-sayfalar a { display: block; text-decoration: none; color: var(--murekkep); white-space: nowrap; padding: 8px 0; border-bottom: 2px solid transparent; }",
    ".cubuk .c-sayfalar a:hover { border-bottom-color: var(--cizgi); }",
    ".cubuk .c-sayfalar a[aria-current=\"page\"] { color: var(--murekkep); border-bottom-color: var(--murekkep); font-weight: 600; }",
    ".cubuk .c-araclar { display: inline-flex; gap: 8px; align-items: center; flex: none; }",
    ".cubuk .c-dil { display: inline-flex; gap: 8px; }",
    ".cubuk .c-dil a, .cubuk .c-tema, .cubuk .c-menu { font: inherit; font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); min-height: 40px; display: inline-flex; align-items: center; padding: 0 8px; border: 1px solid var(--cizgi); border-radius: 6px; background: transparent; color: var(--murekkep); text-decoration: none; cursor: pointer; white-space: nowrap; }",
    ".cubuk .c-dil a[aria-current=\"true\"] { background: var(--murekkep); color: var(--zemin); border-color: var(--murekkep); }",
    ".cubuk .c-tema[aria-pressed=\"true\"] { border-color: var(--murekkep); box-shadow: inset 0 0 0 1px var(--murekkep); }",
    ".cubuk .c-tema::before { content: \"\"; display: inline-block; width: 8px; height: 8px; border-radius: 50%; border: 1.5px solid currentColor; background: linear-gradient(90deg, currentColor 50%, transparent 50%); margin-right: 8px; vertical-align: -1px; }",
    ".cubuk .c-menu { display: none; margin-left: auto; }",
    ".cubuk :focus-visible { outline: 2px solid var(--murekkep); outline-offset: 2px; }",
    "/* Menü kipi (.c-dar): bağlantılar tek satıra sığmadığında betik ölçerek açar */",
    ".cubuk.c-dar .c-araclar { margin-left: 0; }",
    ".cubuk.c-notsuz .c-not { display: none; }",
    "@media all {",
    "  .cubuk.c-dar .c-menu { display: inline-flex; }",
    "  .cubuk.c-dar .c-sayfalar { display: none; position: absolute; top: 100%; left: 0; right: 0; margin: 0; background: var(--zemin); border-bottom: 1px solid var(--cizgi); box-shadow: 0 6px 14px rgba(0, 0, 0, .08); }",
    "  .cubuk.c-dar.c-menu-acik .c-sayfalar { display: block; }",
    "  .cubuk.c-dar .c-sayfalar ul { flex-direction: column; gap: 0; max-width: 1180px; margin: 0 auto; padding: 8px 24px 12px; }",
    "  .cubuk.c-dar .c-sayfalar a { padding: 12px 0; border-bottom: 1px solid var(--cizgi); font-size: var(--yz-govde); line-height: var(--sa-govde); }",
    "  .cubuk.c-dar .c-sayfalar li:last-child a { border-bottom: 0; }",
    "  .cubuk.c-dar .c-sayfalar a[aria-current=\"page\"] { border-bottom-color: var(--cizgi); box-shadow: inset 3px 0 0 var(--murekkep); padding-left: 12px; }",
    "}",
    "@media (max-width: 760px) {",
    "  .cubuk-ic { padding: 12px 16px; gap: 12px; }",
    "  .cubuk .c-atla { left: 16px; }",
    "  .cubuk.c-dar .c-sayfalar ul { padding: 4px 16px 8px; }",
    "  .cubuk .c-not { display: none; }",
    "}",
    "@media (max-width: 520px) {",
    "  .cubuk { min-height: 64px; }",
    "  .cubuk-ic { min-height: 64px; }",
    "  .c-cubuklu { scroll-padding-top: 72px; }",
    "  .cubuk .c-logo { height: 40px; min-width: 40px; align-items: center; justify-content: center; }",
    "  .cubuk .c-logo img { height: 34px; }",
    "  .cubuk .c-logo .c-yazi { font-size: 23.2px; line-height: 34px; letter-spacing: .17px; margin-left: 12px; }",
    "  .cubuk .c-araclar { gap: 8px; }",
    "  .cubuk .c-araclar { margin-left: 0; }",
    "  /* Telefonda düğmeler 34 px (WCAG 2.2 AA en az 24 px): 40 px'lik masaüstü düğmeleriyle logo yazısı 360–390 px'te sığmıyordu */",
    "  .cubuk .c-dil a, .cubuk .c-tema, .cubuk .c-menu { min-height: 34px; padding: 0 8px; }",
    "  .cubuk .c-tema .c-tema-metin { display: none; }",
    "  .cubuk .c-tema { min-width: 34px; min-height: 34px; padding: 0; display: inline-flex; align-items: center; justify-content: center; }",
    "  .cubuk .c-tema::before { margin-right: 0; width: 10px; height: 10px; }",
    "}",
    "@media (max-width: 380px) {",
    "  .cubuk .c-logo .c-yazi { font-size: 20.8px; letter-spacing: .15px; }",
    "}",
    "@media (max-width: 340px) {",
    "  .cubuk .c-logo .c-yazi { display: none; }",
    "}",
    "@media print { .cubuk { display: none; } }",
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
    ["temsil", "Kim temsil ediliyor?", "Who is represented?"],
    ["reform", "Reform modelleri", "Reform models"],
    ["simulasyon", "Ya veto olmasaydı?", "What if there were no veto?"],
    ["hakkinda", "Nasıl yaptık?", "How we did it"],
  ];
  var YAZI = {
    tr: { logo: "Veto Atlası", ana: "Veto Atlası, ana sayfa", sayfalar: "Sayfalar", dil: "Dil", menu: "Menü", atla: "İçeriğe geç", altNot: "Beta sürümü. Hata bildirimleri", altSon: " adresine iletilebilir.",
          tema: "Koyu", temaUzun: "Koyu kâğıt teması", not: "Çevrimdışı sürüm", notUzun: "Çevrimdışı sürüm. Bütün sayfalar bu dosyada." },
    en: { logo: "Veto Atlas", ana: "Veto Atlas, home", sayfalar: "Pages", dil: "Language", menu: "Menu", atla: "Skip to content", altNot: "Beta version. Error reports may be sent to", altSon: ".",
          tema: "Dark", temaUzun: "Dark paper theme", not: "Offline version", notUzun: "Offline version. All pages are in this file." },
  };
  var SAYFA_GRUBU = { metodoloji: "hakkinda", index: "hikaye" };
  var ILETISIM = "iletisim@vetoatlas.com";

  function varlik(ad) { return (window.__VARLIK && window.__VARLIK[ad]) || ad; }
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
  // Atlama bağlantısının hedefi: görünen <main> (TR ve EN ayrı main taşıyan sayfalarda görünen dilinki). Kimliği yoksa
  // "icerik" verilir; adres çubuğundaki #… değişmez (Vetolar paylaşılan görünümü orada tutar)
  function anaIcerik() {
    var gorunen = function (e) { return !e.hidden && e.getClientRects().length; };
    // <main> taşımayan sayfada (Vetolar) sayfa kabı
    var m = Array.prototype.filter.call(document.querySelectorAll("main"), gorunen)[0] || document.querySelector("body > .kap");
    if (!m) return null;
    if (!m.id) m.id = "icerik";
    if (!m.hasAttribute("tabindex")) { m.setAttribute("tabindex", "-1"); m.setAttribute("data-atla", ""); }
    return m;
  }
  function gorsel(sinif, ad, en, boy, alt) {
    var i = document.createElement("img");
    i.className = sinif; i.src = varlik(ad); i.width = en; i.height = boy; i.alt = alt;
    return i;
  }

  // Alt bilgi notu: sayfanın kendi alt bilgisi (Hikâye, Vetolar: footer#alt) varsa ona eklenir; yoksa sayfa kabının sonunda
  // ince çizgili bir alt bilgi oluşturulur. Tek dosyada her sayfa çerçevesi kendi notunu taşır.
  function altBilgi(dil) {
    var Y = YAZI[dil];
    var eski = document.querySelector(".alt-not"); if (eski) eski.remove();
    var p = document.createElement("p"); p.className = "alt-not";
    p.innerHTML = esc(Y.altNot) + ' <a href="mailto:' + ILETISIM + '">' + ILETISIM + "</a>" + esc(Y.altSon);
    var alt = document.getElementById("alt");
    if (alt && alt.tagName === "FOOTER") { alt.appendChild(p); return; }
    var f = document.querySelector("footer.alt-bilgi");
    if (!f) { f = document.createElement("footer"); f.className = "alt-bilgi"; (document.querySelector(".kap") || document.body).appendChild(f); }
    f.appendChild(p);
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
    // Yayın adresi (vetoatlas.com): İngilizce görünümde canonical ve og:url ?lang=en adresini gösterir
    if (!tek && dil === "en") {
      var can = document.querySelector('link[rel="canonical"]'), og = document.querySelector('meta[property="og:url"]');
      if (can) can.setAttribute("href", can.getAttribute("href").split("?")[0] + "?lang=en");
      if (og) og.setAttribute("content", og.getAttribute("content").split("?")[0] + "?lang=en");
    }
    yer.innerHTML =
      (tek ? "" : '<a class="c-atla" href="#icerik">' + esc(Y.atla) + "</a>") +
      '<div class="cubuk-ic">' +
        '<a class="c-logo" href="hikaye.html' + ek + '" data-sayfa="hikaye" aria-label="' + esc(Y.ana) + '"></a>' +
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
          '<button type="button" class="c-tema" aria-pressed="' + (tema === "koyu") + '" aria-label="' + esc(Y.temaUzun) + '" title="' + esc(Y.temaUzun) + '"><span class="c-tema-metin">' + esc(Y.tema) + "</span></button>" +
        "</span>" +
      "</div>";
    var logo = yer.querySelector(".c-logo");
    // Çubukta işaret + canlı logo yazısı (slogansız; sloganlı tam logo sayfalarda kullanılmaz, KILAVUZ bölüm 3). Bağlantının adı
    // aria-label'dadır; işaret süs (alt boş), yazı her iki dilde de marka adıdır. 520 px ve altında işaret 34 px, yazı aynı oranla
    // 23,2 px (380 px altında 20,8 px, 340 px altında yalnızca işaret); tema düğmesi orada yalnızca simge, adı aria-label'da
    logo.appendChild(gorsel("c-isaret", "isaret.svg", 37, 40, ""));
    logo.appendChild(gorsel("c-isaret-koyu", "isaret-koyu.svg", 37, 40, ""));
    var yazi = document.createElement("span"); yazi.className = "c-yazi"; yazi.textContent = "Veto Atlası"; logo.appendChild(yazi);

    var atla = yer.querySelector(".c-atla");
    if (atla) {
      var hedefle = function () { var m = anaIcerik(); if (m) atla.setAttribute("href", "#" + m.id); return m; };
      atla.addEventListener("focus", hedefle);
      atla.addEventListener("click", function (e) { e.preventDefault(); var m = hedefle(); if (m) m.focus(); });
    }

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
      // Sayfa adresi sonradan değişebilir (#… ile paylaşılan görünüm): yeni sekmede açma ve kopyalama için bağlantı tazelenir
      var tazele = function () { if (!tek) a.setAttribute("href", dilAdresi(a.getAttribute("data-dil"))); };
      a.addEventListener("pointerenter", tazele);
      a.addEventListener("focus", tazele);
      a.addEventListener("click", function (e) {
        e.preventDefault();
        var d = a.getAttribute("data-dil");
        if (d === dil) return;
        if (tek) tek.dil(d); else { dilYaz(d); location.href = dilAdresi(d); }
      });
    });
    KOK.classList.add("c-cubuklu");
    if (!tek) altBilgi(dil);
    sigdir();
    yer.querySelector(".c-tema").addEventListener("click", function () {
      tema = tema === "koyu" ? "kagit" : "koyu";
      temaUygula(tema); temaYaz(tema);
      this.setAttribute("aria-pressed", String(tema === "koyu"));
      if (tek && tek.tema) tek.tema(tema);
    });
  }

  // Bağlantılar çubuğa tek satırda sığmıyorsa önce tek dosya notu gizlenir, yine sığmıyorsa menü kipine
  // geçilir; menü kipinde not yeniden görünür (dil ve yazı tipine göre genişlik değişir). Taşma iki yoldan ölçülür:
  // kabın kaydırma genişliği ve dil ile tema düğmelerinin sağ kenar boşluğuna girip girmediği (İngilizce "Dark" düğmesi
  // kaydırma genişliğini büyütmeden kenar boşluğuna 14 px taşıyordu, 21 Ekim 2026)
  function sigdir() {
    var c = document.getElementById("cubuk"); if (!c) return;
    var ic = c.querySelector(".cubuk-ic"); if (!ic) return;
    var acikti = c.classList.contains("c-menu-acik");
    var araclar = c.querySelector(".c-araclar");
    var tasiyor = function () {
      if (ic.scrollWidth > ic.clientWidth + 1) return true;
      if (!araclar) return false;
      var sinir = ic.getBoundingClientRect().right - parseFloat(getComputedStyle(ic).paddingRight);
      return araclar.getBoundingClientRect().right > sinir + 1;
    };
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
    if (window.__CUBUK_GIZLI) { var c = document.getElementById("cubuk"); if (c) c.remove(); altBilgi(gecerliDil()); return; }
    if (!window.__CUBUK_ELLE) kur();
    // İnternetsiz çalışma (web/cevrimdisi.js; veto_atlasi/cevrimdisi.py): yalnızca sunucudaki sayfalarda; tek dosya ve dosya
    // olarak açılış kaydetmez. Veri tasarrufu açıksa (navigator.connection.saveData) sekiz sayfa önceden indirilmez
    if (!window.__CUBUK_ELLE && window.isSecureContext && location.protocol !== "file:" && "serviceWorker" in navigator) {
      var tasarruf = navigator.connection && navigator.connection.saveData;
      var kaydet = function () { if (tasarruf) return; navigator.serviceWorker.register("cevrimdisi.js").catch(function () { /* desteklenmiyor: site yine çalışır */ }); };
      if (document.readyState === "complete") kaydet(); else window.addEventListener("load", kaydet);
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", basla); else basla();
})();
