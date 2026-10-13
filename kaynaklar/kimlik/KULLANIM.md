# Veto Atlası – kimlik dosyaları

Bütün SVG'lerde metinler yola (path) çevrildi; hiçbir cihazda yazı tipine bağlı kalmadan,
her boyutta net görünürler. Renkler: mürekkep #1F2A37, ret kırmızısı #B3272D, kâğıt #F7F3EC.

## Dosyalar
- logo-yatay-a.svg / logo-yatay-a-koyu.svg      Yatay logo, slogan: "Dünya 5'ten büyüktür" (açık / koyu zemin)
- logo-yatay-b.svg / logo-yatay-b-koyu.svg      Yatay logo, slogan: "Daha adil bir dünya mümkün"
- logo-dikey-a.svg, logo-dikey-b.svg (+ -koyu)  Dikey (ortalanmış) sürümler
- isaret.svg / isaret-koyu.svg                   Yalnızca işaret (64 px ve üstü için)
- isaret-kucuk.svg                               Yalnızca işaret, küçük boyutlar için (48 px ve altı)
- isaret-tek-renk.svg                            Tek renkli baskı, filigran ve antetli kâğıt için
- ikon-maskable.svg                              Zeminli uygulama ikonu (Android "maskable")
- favicon.ico                                    16 + 32 + 48 px, çok boyutlu
- png/isaret-{16,32,48,64,180,192,512}.png        Tarayıcı ve cihaz ikonları
- png/ikon-maskable-{192,512}.png                 Android ana ekran ikonu
- png/logo-*@2x.png                              Yüksek çözünürlüklü PNG (sunum, belge, sosyal medya)

## Siteye ekleme (her sayfanın <head> bölümüne)
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/isaret-kucuk.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/isaret-180.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#F7F3EC">

## site.webmanifest
{
  "name": "Veto Atlası",
  "short_name": "Veto Atlası",
  "icons": [
    { "src": "/isaret-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/isaret-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/ikon-maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable" },
    { "src": "/ikon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "theme_color": "#F7F3EC",
  "background_color": "#F7F3EC",
  "display": "standalone"
}

## Kurallar
- İşaretin etrafında en az bir kare genişliğinde boşluk bırakılır.
- Kırmızı kare asla başka renge çevrilmez; tek renkli kullanımda isaret-tek-renk.svg kullanılır.
- 48 px ve altında isaret-kucuk.svg / isaret-16,32,48.png kullanılır.
- Logo gölge, degrade ya da 3B efektle kullanılmaz.
