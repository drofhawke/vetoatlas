/*
 * Veto Atlası – "Ya veto olmasaydı?" sayfasının birbirine bağlı filtreleri (konu, yıl, veto eden üye).
 *
 * Saf işlevler; tarayıcıda window.VetoSuzgec, Node'da module.exports. tests/test_simulasyon.py bu dosyayı Node ile
 * bütün geçerli filtre durumlarında çalıştırır; sayfa (web/simulasyon.html) aynı işlevleri kullanır.
 *
 * Kurallar
 * 1. Konu birincil filtredir: listesinde kaydı olan bütün konular bulunur. Konu değişince, yeni konuda kaydı olmayan
 *    yıl "Tümü"ye döner; ardından konu ve yılla kaydı kalmayan üye "Tümü"ye döner. Dönen filtreler çağırana bildirilir.
 * 2. Yıl ve üye listeleri konuya ve birbirine bağlıdır: yalnızca öbür seçimlerle en az bir kayıt veren seçenekler
 *    bulunur. Bu yüzden yıl ya da üye seçimi hiçbir filtreyi geçersiz kılmaz.
 * 3. Her seçeneğin yanındaki sayı, o seçenek seçildiğinde (konu için gerekli sıfırlamalardan sonra) eşleşecek kayıt
 *    sayısıdır; "Tümü" de aynı kurala uyar.
 * 4. Geçerli bir durumdan (en az bir kayıt) yapılan her seçim yine en az bir kayıt verir; sıfır eşleşme oluşmaz.
 */
(function (kok) {
  "use strict";
  var SIRA = ["konu", "yil", "uye"];
  var BOS = { konu: "", yil: "", uye: "" };

  function uyar(k, ad, deger) {
    if (ad === "konu") return k.konu === deger;
    if (ad === "yil") return k.tarih.slice(0, 4) === deger;
    return k.uyeler.indexOf(deger) >= 0;
  }
  function kopya(f) { return { konu: f.konu || "", yil: f.yil || "", uye: f.uye || "" }; }
  // Filtre durumuyla eşleşen kayıtlar (boş değer "Tümü" demektir)
  function eslesenler(kayitlar, f) {
    return kayitlar.filter(function (k) {
      for (var i = 0; i < SIRA.length; i++) { var ad = SIRA[i]; if (f[ad] && !uyar(k, ad, f[ad])) return false; }
      return true;
    });
  }
  function sayi(kayitlar, f) { return eslesenler(kayitlar, f).length; }

  // ad filtresine deger verildiğinde oluşan durum ve "Tümü"ye dönen filtreler ([{ ad, deger }], eski değerleriyle)
  function sec(kayitlar, f, ad, deger) {
    var y = kopya(f);
    y[ad] = deger || "";
    var sifirlanan = [];
    if (ad === "konu") {
      if (y.yil && !sayi(kayitlar, { konu: y.konu, yil: y.yil, uye: "" })) { sifirlanan.push({ ad: "yil", deger: y.yil }); y.yil = ""; }
      if (y.uye && !sayi(kayitlar, y)) { sifirlanan.push({ ad: "uye", deger: y.uye }); y.uye = ""; }
    }
    return { durum: y, sifirlanan: sifirlanan };
  }

  // Bir açılır listenin seçenekleri: [{ deger, sayi }]. İlk öğe "Tümü" (deger ""); ardından sira dizisindeki sırayla,
  // yalnızca seçildiğinde en az bir kayıt veren değerler. sira verilmezse veri setindeki değerler (yıl artan) kullanılır.
  function secenekler(kayitlar, f, ad, sira) {
    var adaylar = sira ? sira.slice() : degerListesi(kayitlar, ad);
    var liste = [{ deger: "", sayi: sayi(kayitlar, sec(kayitlar, f, ad, "").durum) }];
    adaylar.forEach(function (d) {
      if (!d) return;
      var n = sayi(kayitlar, sec(kayitlar, f, ad, d).durum);
      if (n > 0) liste.push({ deger: d, sayi: n });
    });
    return liste;
  }
  // Bir boyuttaki bütün değerler: konu ve üye ilk görülme sırasıyla, yıl artan
  function degerListesi(kayitlar, ad) {
    var gorulen = {}, liste = [];
    kayitlar.forEach(function (k) {
      var d = ad === "konu" ? [k.konu] : ad === "yil" ? [k.tarih.slice(0, 4)] : k.uyeler;
      d.forEach(function (x) { if (!gorulen[x]) { gorulen[x] = true; liste.push(x); } });
    });
    return ad === "yil" ? liste.sort() : liste;
  }

  var api = { SIRA: SIRA, BOS: BOS, uyar: uyar, eslesenler: eslesenler, sayi: sayi, sec: sec, secenekler: secenekler, degerListesi: degerListesi };
  if (typeof module === "object" && module.exports) module.exports = api;
  else kok.VetoSuzgec = api;
})(typeof window !== "undefined" ? window : this);
