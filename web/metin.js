/*
 * Veto Atlası – metin sayfalarının "Bu sayfada" dizini (Hakkında, Metodoloji; kaynaklar/kimlik/KILAVUZ.md bölüm 2,
 * "Metin sayfası").
 *
 * Görünen dilin <main class="metin-duzen"> öğesindeki kimlikli h2 ve h3 başlıklarından üretilir; h3'ler bir önceki h2'nin
 * altında iç içe listelenir. İki kopya yazılır: 1100 px ve üstünde sağ sütunda kaydırdıkça yerinde duran liste, altında
 * başlığın hemen altında katlanabilir kutu (hangisinin görüneceği web/temel.css'te). Okunan bölümün bağlantısı
 * aria-current="location" taşır: üstü eşiği geçen son başlık; sayfanın sonunda son başlık; dizinden seçilen bölüm, okur
 * kendisi kaydırana dek.
 *
 * Tek dosyanın alt alta dizilen sekmesinde (window.__YIGIN) çerçeve kendisi kaymaz: üst belge kaydırma konumunu ve görünen
 * yüksekliği bildirir ("gorunum" iletisi); yerinde durma burada aynı ölçülerle uygulanır.
 *
 * Saf işlev (listeYap) Node'da module.exports ile; tests/test_okunurluk.py çalıştırır.
 */
(function (kok) {
  "use strict";
  var YAZI = { tr: "Bu sayfada", en: "On this page" };

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; });
  }

  // Başlıklar ({ id, metin, duzey }) -> iç içe liste: h2 maddeleri, altlarında h3'ler
  function listeYap(basliklar) {
    var maddeler = [];
    basliklar.forEach(function (b) {
      var bag = '<a href="#' + esc(b.id) + '">' + esc(b.metin) + "</a>";
      if (b.duzey === 3 && maddeler.length) maddeler[maddeler.length - 1].alt.push(bag);
      else maddeler.push({ bag: bag, alt: [] });
    });
    return "<ul>" + maddeler.map(function (m) {
      return "<li>" + m.bag + (m.alt.length ? "<ul>" + m.alt.map(function (a) { return "<li>" + a + "</li>"; }).join("") + "</ul>" : "") + "</li>";
    }).join("") + "</ul>";
  }

  function kur() {
    var main = Array.prototype.filter.call(document.querySelectorAll("main.metin-duzen"), function (m) { return !m.hidden; })[0];
    if (!main) return;
    var yer = main.querySelector(".metin-dizin");
    var hedefler = Array.prototype.slice.call(main.querySelectorAll(".metin h2[id], .metin h3[id]"));
    if (!yer || !hedefler.length) return;
    var baslik = esc(YAZI[main.getAttribute("lang") === "en" ? "en" : "tr"]);
    var liste = listeYap(hedefler.map(function (h) { return { id: h.id, metin: h.textContent, duzey: h.tagName === "H3" ? 3 : 2 }; }));
    yer.innerHTML = '<details class="bu-sayfada-kutu"><summary>' + baslik + '</summary><nav class="bu-sayfada" aria-label="' + baslik + '">' + liste + "</nav></details>"
      + '<nav class="bu-sayfada bu-sayfada-yan" aria-label="' + baslik + '"><p class="bu-sayfada-baslik" aria-hidden="true">' + baslik + "</p>" + liste + "</nav>";
    var kutu = yer.querySelector(".bu-sayfada-kutu"), yan = yer.querySelector(".bu-sayfada-yan");
    var baglar = Array.prototype.slice.call(yer.querySelectorAll("a"));
    var yigin = !!window.__YIGIN, gorunum = { ust: 0, h: window.innerHeight }, secilen = null, son = null;

    // Görünen alan: bağımsız sayfada pencere, alt alta dizilen sekmede üst belgenin bildirdiği
    function alan() { return yigin ? gorunum : { ust: window.scrollY, h: window.innerHeight }; }

    function guncelle() {
      var a = alan();
      // Başlığın üstü bu çizgiyi geçince bölüm okunuyor sayılır: kaydırma payı (çubuk), başlığın payı (16 px) ve 24 px
      var sinir = a.ust + (parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0) + 40;
      var etkin = hedefler[0];
      for (var i = 0; i < hedefler.length; i++) {
        if (hedefler[i].getBoundingClientRect().top + window.scrollY <= sinir) etkin = hedefler[i]; else break;
      }
      if (a.ust + a.h >= document.documentElement.scrollHeight - 2) etkin = hedefler[hedefler.length - 1];
      if (secilen) etkin = secilen;
      if (yigin) yapistir(a);
      if (etkin === son) return;
      son = etkin;
      baglar.forEach(function (b) {
        if (b.getAttribute("href") === "#" + etkin.id) b.setAttribute("aria-current", "location"); else b.removeAttribute("aria-current");
      });
    }

    // Alt alta dizilen sekmede yerinde durma: dizin kendi sütununda kalarak görünen alanın üstünden "top" kadar aşağıda durur
    function yapistir(a) {
      if (getComputedStyle(yan).display === "none") return;
      var pay = parseFloat(getComputedStyle(yan).top) || 0;
      yan.style.maxHeight = Math.max(160, a.h - 2 * pay) + "px";
      var r = yan.parentNode.getBoundingClientRect();
      var kayma = Math.max(0, Math.min(a.ust + pay - (r.top + window.scrollY), r.height - yan.offsetHeight));
      yan.style.transform = kayma ? "translateY(" + kayma + "px)" : "";
    }

    // Dizinden seçilen bölüm, okur kendisi kaydırana dek vurgulu kalır (sayfanın sonundaki kısa bölümler de); dar ekranda
    // kutu seçimden sonra kapanır
    yer.addEventListener("click", function (e) {
      var b = e.target.closest("a[href^='#']");
      if (!b) return;
      secilen = document.getElementById(b.getAttribute("href").slice(1));
      if (kutu.contains(b)) kutu.open = false;
      guncelle();
    });
    ["wheel", "touchstart", "keydown"].forEach(function (olay) {
      window.addEventListener(olay, function () { if (secilen) { secilen = null; guncelle(); } }, { passive: true });
    });

    if (yigin) {
      window.addEventListener("message", function (e) {
        var m = e.data || {};
        if (m.tur !== "gorunum") return;
        gorunum = { ust: +m.ust || 0, h: +m.h || window.innerHeight };
        guncelle();
      });
    } else {
      var bekliyor = false;
      window.addEventListener("scroll", function () {
        if (bekliyor) return;
        bekliyor = true;
        window.requestAnimationFrame(function () { bekliyor = false; guncelle(); });
      }, { passive: true });
    }
    window.addEventListener("resize", guncelle);
    guncelle();
  }

  var api = { listeYap: listeYap };
  if (typeof module === "object" && module.exports) { module.exports = api; return; }
  kok.VetoMetin = api;
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", kur); else kur();
})(typeof window !== "undefined" ? window : this);
