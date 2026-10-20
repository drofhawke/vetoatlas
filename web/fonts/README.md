# Yazı tipleri

Sayfalar hiçbir üçüncü taraf adrese istek atmaz; yazı tipleri buradan yüklenir.

- Source Serif 4 ve Source Sans 3, © Adobe, SIL Open Font License 1.1 ("Source" ayrılmış yazı tipi adıdır).
  Lisans metinleri: `OFL-source-serif-4.txt`, `OFL-source-sans-3.txt` (https://github.com/adobe-fonts/source-serif ve
  https://github.com/adobe-fonts/source-sans, `release` dalı, `LICENSE.md`).
- woff2 dosyaları `scripts/14_yazi_tipleri.py` ile üretilir (20 Ekim 2026). Kaynak, Google Fonts'un değişken yazı tipleridir
  (https://github.com/google/fonts, `ofl/sourcesans3/` ve `ofl/sourceserif4/`; Adobe'nin 3.052 ve 4.004 sürümlerinden derlenmiş):
  betik 400, 400 italik, 500 ve 600 (Source Sans 3) ile 400 ve 600 (Source Serif 4, optik boy 14) kesimlerini çıkarır,
  ttfautohint 1.8.4 ile hinting ekler (yalnızca Latin, 8–50 ppem için eniyilenmiş, 200 ppem'e kadar uygulanır) ve
  `fonts.css`'teki latin ve latin-ext `unicode-range` alt kümelerine böler. Üretim belirlenimlidir: aynı kaynak ve ayarlarla
  aynı baytlar çıkar (kaynak dosyaların SHA-256'ları betikte sabittir; `kaynaklar/.yazi_tipleri/` depoya girmez).
- Neden hinting: 11–19 Ekim'deki @fontsource 5.3.0 dosyaları (aynı Google derlemesinin statik kesimleri) hinting'siz
  dağıtılıyordu. Windows'ta Chrome ve Edge, hinting'siz yazıyı dikey ızgaraya oturtamaz; 15–18 px metinde gövde çizgileri ve
  x-yüksekliği iki piksele yayılıp bulanık görünür (20 Ekim 2026, %100 ölçekte ekran görüntüsüyle doğrulandı). Hinting'li
  kesimler Windows'ta ızgaraya oturur; macOS, iOS ve Android hinting'i yok saydığı için orada hiçbir şey değişmez. Dış hatlar,
  ilerleme genişlikleri, dikey ölçüler (hhea, OS/2) ve OpenType özellikleri (kern, liga, locl, ccmp, frac, pnum, tnum, mark,
  mkmk) eski dosyalarla aynıdır; satır ve başlık ölçüleri değişmez. Dosyalar hinting programı kadar büyür (toplam 272 → 386 kB).
- Source Sans 3 italik yalnızca 400 ağırlıkta (hikâyede büyük sayının alt yazısı); tarayıcı italiği yapay üretmez.
- `veto-atlasi-logo.woff2`: çubuktaki logo yazısı "Veto Atlası" için (`web/cubuk.js`; KILAVUZ bölüm 3, "Keskinlik"). Source Serif 4
  Semibold, optik boy 20 (logo paketinin yazıyı yola çevirdiği kesim), yalnızca bu harflerin 10 glifi ve kerning'i, hinting'li;
  `fonts.css`'te `Veto Atlası Logo` ailesi, `font-display: block`.
- `fonts.css`'teki @font-face tanımları ve `unicode-range` listeleri @fontsource paketlerinden kalmıştır; betik yalnızca bu
  tanımları okur, değiştirmez.

| Dosya | SHA-256 |
|---|---|
| `source-sans-3-latin-400-italic.woff2` | `a4cff67cb7147dc0f1abfdab35a0e38c9acf00866a2c80c97a6b815e19811dbd` |
| `source-sans-3-latin-400-normal.woff2` | `282209faa93897acad594887b09ada9aa26141c389833e496b0312f79a20336d` |
| `source-sans-3-latin-500-normal.woff2` | `e6b0ec4c814bd69e0a1fcd6ab327815ecd991b34e8e05255a708ac1e7281e2e5` |
| `source-sans-3-latin-600-normal.woff2` | `ec8423800b6cef61b7a64bb0e5a9b0d496d185e5b56ed458d2b80ea1111cc5ed` |
| `source-sans-3-latin-ext-400-italic.woff2` | `34284fe1744224b09b5dacc677c4cdf3ba630e85d2b3a9c3f5bb350711a74d45` |
| `source-sans-3-latin-ext-400-normal.woff2` | `c9db9e9c75a5de097d8ddcee605e9381431a0ac8d07be90bb63c611238c6d89e` |
| `source-sans-3-latin-ext-500-normal.woff2` | `dbaeb43503274082f8445f21460c88debe73ab5d8c2b072515dd2cf6bd6b14c3` |
| `source-sans-3-latin-ext-600-normal.woff2` | `3e2596c5841508ecb29b7813410715b1f8d909eb5c080bdf76ca2dc754f9b1bf` |
| `source-serif-4-latin-400-normal.woff2` | `cc15f41ed6b118eb4c448350ab44dc6708eb678120f16767e23ca0da038b6375` |
| `source-serif-4-latin-600-normal.woff2` | `258d73264ca312ba3dc38b4142f9e12f0e4a568545f96de597fb6b81be048e07` |
| `source-serif-4-latin-ext-400-normal.woff2` | `4e1266d6a5e0dc4429d9a35a46cc8327df5e33813117f6d798eff52861b69eca` |
| `source-serif-4-latin-ext-600-normal.woff2` | `01f2b7086ac4b531864a140abf331d4b8274c2f7d9b48a2f72da501fa0b9ce65` |
| `veto-atlasi-logo.woff2` | `657eaf68f8e79b3c07fd54f09e552bb93cd9ed3d0d02e66f55b7b9ed67246e22` |
| `OFL-source-sans-3.txt` | `56af9b9c6715597e458284a474dc118a50a4150e9d547c70f7b4a33c3e6a9328` |
| `OFL-source-serif-4.txt` | `c21d7293d87b6d7ab1d0229a2f55b77f33a7613a6a4e66f6693d68d7d8d09464` |
