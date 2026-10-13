# Favicon ve uygulama ikonları (zeminli)

Zeminli ikonlar koyu ve açık sekme çubuklarında aynı netlikte görünür.
Önerilen: favicon-kagit (kâğıt zemin, lacivert halka). favicon-lacivert koyu alternatiftir.

- favicon-kagit.ico            16 + 32 + 48 px (sekme simgesi; sık halkalı küçük sürüm)
- favicon-kagit.svg            SVG sekme simgesi (küçük boyut geometrisi)
- favicon-kagit-{16,32,48}.png küçük boyutlar
- favicon-kagit-{64,180,192,512}.png  ana ekran ve uygulama ikonları (normal halka geometrisi)
- favicon-lacivert-*           aynı set, koyu zemin

<head> satırları:
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">   (favicon-kagit-180.png)
<link rel="manifest" href="/site.webmanifest">               (192 ve 512; maskable olarak da aynı dosyalar)
<meta name="theme-color" content="#FBF8F1">
