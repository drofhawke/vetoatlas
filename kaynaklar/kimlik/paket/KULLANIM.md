# Veto Atlası — logo paketi

Bu paketteki bütün dosyalar tek bir kaynaktan, `kaynak/uret.py` betiğinden üretildi. Logolar gerçek vektördür: yazılar yola (path) çevrilmiştir, hiçbir cihazda yazı tipine ihtiyaç duymaz ve her boyutta keskin görünür. Dosyalar boşluksuz kırpılmıştır; logonun çevresindeki boşluğu sayfa düzeni verir.

Bütün dosyaları açık ve koyu zeminde, küçük boyutlarda ve ikon maskeleri içinde görmek için `onizleme.html` dosyasını tarayıcıda açın. `pano.png` aynı sayfanın görüntüsüdür.

## Hangi dosya nerede kullanılır

| İhtiyaç | Dosya |
|---|---|
| Site başlığı | `svg/logo-cubuk-b.svg` |
| Yatay alanlar: sayfa içi, sunum, belge başlığı | `svg/logo-yatay-a.svg`, `svg/logo-yatay-b.svg` |
| Kare ya da dikey alanlar: kapak, poster, afiş | `svg/logo-dikey-a.svg`, `svg/logo-dikey-b.svg`, `svg/logo-dikey-sade.svg` |
| Yalnızca işaret, 32 px ve üstü (telefonda her boyut) | `svg/isaret.svg` |
| Yalnızca işaret, 32 px'in altı | `svg/isaret-kucuk.svg` |
| Filigran, antetli kâğıt | `svg/isaret-tek-renk.svg` |
| Word, PowerPoint, e-posta imzası, SVG kabul etmeyen yerler | `png/` — 600 px küçük kullanım için, 2400 px belge ve sunum için |
| Matbaa, tabela, promosyon ürünü | `baski/pdf/` ya da `baski/eps/` |
| Tek renkli baskı: kaşe, gofre, kazıma, fotokopi | `-siyah` ve `-beyaz` dosyalar (`svg/tek-renk/`, `png/tek-renk/`, `baski/`) |
| Site ikonları ve paylaşım görseli | `web/` klasörünün tamamı |
| Instagram, X ve LinkedIn profil fotoğrafı | `sosyal/` |

Adında `-koyu` geçen dosyalar koyu zemin içindir. A sürümlerinde slogan "Dünya 5’ten büyüktür", B sürümlerinde "Daha adil bir dünya mümkün"dür. `cubuk` ve `sade` sürümlerinde slogan yoktur.

## Siteye kurulum

1. `web/` klasöründeki bütün dosyaları sitenin kök klasörüne, `index.html`'in yanına kopyalayın. Eski `isaret-*.png`, `ikon-maskable-*.png` ve eski `favicon.ico` dosyalarını silebilirsiniz.
2. Her sayfanın `<head>` bölümündeki eski ikon satırlarını silin ve yerine `web/head-etiketleri.html` içeriğini yapıştırın:

```html
<!-- Veto Atlası — her sayfanın <head> bölümüne. Dosyalar sitenin kök klasöründe olmalı. -->
<!-- ?v=2 eski (pikselli) ikonların tarayıcı önbelleğinden düşmesi içindir; ikonu yeniden değiştirirsen sayıyı artır. -->
<link rel="icon" href="/favicon.ico?v=2" sizes="32x32">
<link rel="icon" href="/favicon.svg?v=2" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#FBF8F1">

<!-- Bağlantı paylaşım önizlemesi (X, WhatsApp, LinkedIn, Telegram) -->
<meta property="og:site_name" content="Veto Atlası">
<meta property="og:image" content="https://vetoatlas.com/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Veto Atlası — Dünya 5’ten büyüktür">
<meta name="twitter:card" content="summary_large_image">
```

3. Tarayıcılar ikonları uzun süre önbellekte tutar. Bağlantılardaki `?v=2` eski ikonların düşmesini sağlar; ikonu ileride yeniden değiştirirseniz bu sayıyı artırın. Ana ekrana eklenmiş kısayollar ise ikonlarını hiç güncellemez; yayından sonra eski kısayolu silip siteyi yeniden ekleyin.

Eski kurulumdaki `sizes="any"` ayarı, Chrome'un vektör SVG yerine raster ICO dosyasını seçmesine yol açıyordu. Yeni satırlarda ICO yalnızca yedek olarak kalır; Chrome, Edge, Firefox ve Safari 26 ve üstü SVG ikonu kullanır.

Logolar artık boşluksuz kırpıldığı için, sitede logoya CSS ile yükseklik verdiyseniz aynı yükseklikte logo yaklaşık %30 büyük görünür. Eski boyutu korumak için yüksekliği %24 azaltın (örneğin 56 px yerine 42 px). Site başlığındaki logo en az 40 px yükseklikte kalmalıdır.

`site.webmanifest` içeriği:

```json
{
  "name": "Veto Atlası",
  "short_name": "Veto Atlası",
  "lang": "tr",
  "id": "/hikaye",
  "start_url": "/hikaye",
  "display": "standalone",
  "theme_color": "#FBF8F1",
  "background_color": "#FBF8F1",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    },
    {
      "src": "/icon-maskable-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    },
    {
      "src": "/icon-maskable-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ]
}
```

## Renkler

| Ad | HEX | RGB | Kullanım |
|---|---|---|---|
| Mürekkep | `#13213A` | 19, 33, 58 | İşaret, logo yazısı, koyu zemin |
| Ret kırmızısı | `#A4262C` | 164, 38, 44 | Yalnızca ayrılan kare |
| Kâğıt | `#FBF8F1` | 251, 248, 241 | Açık zemin |
| İkincil | `#5A6578` | 90, 101, 120 | Slogan |
| Kâğıt tonu, koyu zeminde | `#EDE8E0` | 237, 232, 224 | Koyu zeminde işaret ve yazı |
| Ret, koyu zeminde | `#E05A52` | 224, 90, 82 | Koyu zeminde ayrılan kare |
| İkincil, koyu zeminde | `#AEB8C4` | 174, 184, 196 | Koyu zeminde slogan |

Bu değerler sitenin CSS değişkenleriyle (`--murekkep`, `--ret`, `--zemin`, `--ikincil`) aynıdır. Koyu zemin tonları ayrı renkler değildir; aynı renklerin lacivert üzerinde yeterli kontrastla okunması için açılmış karşılıklarıdır.

Baskı için: PDF ve EPS dosyaları RGB renk kullanır. Matbaaya bu dosyaları ve HEX kodlarını verin; kullanacakları kâğıda göre CMYK dönüşümünü kendi profilleriyle yapıp prova göstermelerini isteyin. Kâğıt rengi basılmaz; krem ya da fildişi kâğıt seçilebilir.

## Kurallar

- **Boşluk:** Logonun çevresinde en az bir kare kenarı kadar boş alan bırakın. Kare, işaretteki tek bir karedir.
- **Ekranda en küçük boyut:** Sloganlı yatay logo en az 240 px, sloganlı dikey logo en az 160 px genişlikte kullanılır; daha küçükte slogan okunmaz, sloganı olmayan sürüme geçin. Site başlığındaki logo en az 40 px yüksekliktedir. İşaret 32 px'ten küçük kullanılacaksa `isaret-kucuk.svg` kullanılır. Telefonlar 2–3 kat piksel yoğunluğuyla çizdiği için sayfa içinde `isaret.svg` her boyutta nettir. İki dosya da aynı 15 kareden oluşur; küçük sürümde kareler biraz küçük, aralar biraz geniştir.
- **Baskıda en küçük boyut:** Sloganlı yatay logo 40 mm, sloganlı dikey logo ve sloganı olmayan logolar 25 mm, işaret 12 mm genişliğin altına inmez. Daha küçük baskıda (rozet, kalem) `isaret-kucuk.svg` kullanılır.
- Kırmızı kare başka renge boyanmaz ve yeri değiştirilmez. Tek renk gereken yerde `-siyah`, `-beyaz` ya da `isaret-tek-renk` dosyaları kullanılır.
- Logo esnetilmez, döndürülmez, öğeleri yeniden düzenlenmez; gölge, degrade, kontur ya da 3B efekt verilmez.
- Fotoğraf ya da desen üzerinde logo yalnızca sakin, düz bir alana konur; zemin karışıksa `-beyaz` sürüm kullanılır.

## Sekme ve uygulama ikonları

- `favicon.svg` ve `favicon.ico`: Sekme ikonu lacivert zeminli bir karedir. Şeffaf zeminli lacivert halka koyu sekme çubuklarında kayboluyordu ve Safari, SVG ikonun içindeki koyu mod ayarını uygulamıyor. Zeminli ikon açık ve koyu temada aynı netlikte görünür.
- Sekme ikonunda da aynı 15 kare vardır; küçük boy sürümdeki gibi kareler biraz küçültülüp aralar açılmıştır. `favicon.ico` 16, 32 ve 48 px görüntüleri içerir.
- `apple-touch-icon.png` (180 px): iPhone ve iPad ana ekranı. Zemini opaktır; iOS köşeleri kendisi yuvarlar.
- `icon-192.png`, `icon-512.png`: Android'de ve masaüstünde yüklenen uygulamanın ikonu. `icon-maskable-192.png`, `icon-maskable-512.png`: Android ana ekran ikonu. Samsung gibi bazı başlatıcılar bu görselin yalnızca ortadaki üçte ikisini gösterir; işaret o alanın içinde kalacak boyda çizildi, halka ve kırmızı kare kırpılmaz.
- `og-image.png` (1200×630): Bağlantı paylaşıldığında görünen önizleme. Logo ortada durduğu için görseli kare kırpan uygulamalarda da bütün kalır.

## Bu sürümde düzeltilenler

- İşaret bütün logolarda aynı oranlarla yeniden kuruldu; eski dosyalarda kurgudan kurguya küçük farklar vardı.
- Logolar boşluksuz kırpıldı; eski yatay logonun genişliğinin %44'ü boştu.
- Pakette iki farklı renk seti vardı; hepsi sitenin renklerine eşitlendi.
- "Veto Atlası" yazısında yazı tipinin harf çifti düzeltmeleri (kerning) açıldı; "V" ile "e" arasındaki boşluk kapandı. Slogandaki düz kesme işareti, rakama yaslanan tipografik kesme işaretiyle (’) değiştirildi. İşaretin ve harflerin biçimi değişmedi.
- Küçük boy işaret yeniden çizildi. Eski sürümde iri kareler üst üste binip halkayı kalın, testere dişli bir kurdeleye çeviriyordu; işaret telefonda başka bir şeye benziyordu. Yeni sürüm aynı 15 kareden oluşur; yalnızca kareler biraz küçültülüp aralar açıldı.
- iPhone ikonu artık opak; eskisinde iOS şeffaf alanı siyaha boyadığı için işaret görünmüyordu.
- Android ana ekran ikonu yeniden çizildi. Eskisinde aynı görsel hem normal hem maskable ikon olarak kullanılıyordu; başlatıcı görselin ortasını büyüterek gösterdiği için halkanın kenarları ve kırmızı kare kesiliyordu.

## Yeniden üretmek

Renkleri, slogan metnini ya da oranları değiştirmek için `kaynak/uret.py` dosyasının başındaki AYARLAR bölümünü düzenleyip paketin kök klasöründe şunu çalıştırın:

    pip install fonttools uharfbuzz resvg-py pillow cairosvg
    python kaynak/uret.py

Betik paketi bulunduğu yerde baştan üretir. Yazı tipleri `kaynak/fonts/` içindedir (Source Serif 4 ve Source Sans 3, SIL Open Font License). Cairo kurulamazsa PDF/EPS adımı atlanır; Playwright kuruluysa `pano.png` da yenilenir.
