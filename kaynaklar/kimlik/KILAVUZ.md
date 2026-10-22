# Veto Atlası – tasarım kılavuzu

Bu kılavuz logo paketinin kullanım notunu (`paket/KULLANIM.md`) temel alır ve sitenin, kartların ve tek dosya sürümünün paylaştığı
tasarım dilini tanımlar. Değişkenler her sayfanın `:root` bloğunda, kartlar için
`scripts/08_paylasim_kartlari.py` ve önizleme görseli için `scripts/06_onizleme_gorseli.py` içinde
aynı değerlerle tanımlıdır; `tests/test_kimlik.py` bu tutarlılığı ve metin karşıtlığını denetler.

## 1. Renkler: "Fildişi ve lacivert"

| Değişken | Kâğıt (varsayılan) | Koyu kâğıt (düğmeyle) | Kullanım |
|---|---|---|---|
| `--zemin` | `#FBF8F1` | `#1C1A17` | Sayfa zemini |
| `--yuzey` | `#FFFFFF` | `#272420` | Kart ve kutu zemini |
| `--murekkep` | `#13213A` | `#EDE8E0` | Metin, başlık, büyük sayılar, daimî koltuk, etkin sekme çizgisi, odak halkası |
| `--murekkep-2` | `#5A6578` | `#ABA496` | İkincil metin, etiketler, seçilmiş koltuk, hitap işaretleri |
| `--cizgi` | `#E1DBCF` | `#3B3731` | Çizgiler, kutu kenarları |
| `--cizgi-denetim` | `#868E9D` | `#7A7368` | Seçim kutusu ve gezinme düğmesi çerçeveleri (Ya veto olmasaydı?; zeminle en az 3:1) |
| `--bos` | `#EDE7DA` | `#2E2A24` | Boş ve seçili alan, çubuk arka planı |
| `--oy-lehte` | `#9AA3B2` | `#8B94A3` | Nötr kare ve "evet (lehte)" oyu |
| `--oy-aleyhte` | `#13213A` | `#EDE8E0` | "Hayır (aleyhte)" oyu |
| `--oy-cekimser` | `#D9D3C7` | `#4A463F` | Çekimser oy (simülasyonda da dolu, 1 px `--cizgi-denetim` çerçeveli; orada "katılmadı" karesi boş ve kesik çizgilidir) |
| `--vurgu` | `#A4262C` | `#E05A52` | **Yalnızca ret oyu ve veto** |
| `--kabul` | `#2D6A4F` | `#6FBF8E` | **Yalnızca simülasyon sonucu "Kabul edilirdi"** |

Üye renkleri (açık tema; koyu temada açık tonları): Sovyetler Birliği `#7E2F3C`, Rusya Federasyonu
`#C2666F`, ABD `#24507F`, Birleşik Krallık `#2F7A6E`, Fransa `#A8782A`, Çin `#5E4E9A`.

**Tema.** Site her zaman kâğıt (açık) temada açılır; işletim sisteminin koyu tema tercihi dikkate
alınmaz (`prefers-color-scheme` kullanılmaz). Koyu kâğıt yalnızca üst çubuktaki "Koyu" düğmesiyle seçilir
(`:root[data-theme="dark"]`) ve tarayıcıda hatırlanır (`localStorage`, erişilemezse kâğıt kalır).
`tests/test_kimlik.py` varsayılanın kâğıt olduğunu denetler. Tarayıcı çubuğunun rengi (`theme-color`) temayla değişir:
kâğıtta `#FBF8F1`, koyu kâğıtta `#1C1A17` (`web/cubuk.js`). Dil seçimi de hatırlanır (`veto-atlasi-dil`); adresteki
`?lang=` her zaman önce gelir, adreste dil yoksa ve kayıtlı dil İngilizceyse adrese `?lang=en` yazılır (`history.replaceState`;
sayfa yeniden yüklenmez, adres yazılamazsa sayfa `?lang=en` ile yeniden açılır). `web/cubuk.js` her sayfanın ilk betiği
olduğu için sayfa betikleri dili adresten okur. Tek dosya ve sayfa çerçeveleri bu adıma karışmaz.

**Kırmızı kuralı.** `--vurgu` yalnızca ret oyunu ve vetoyu gösterir: birim grafikteki ret kareleri,
galerideki "bir hayır" noktası ve kartlardaki ret karesi, hikâyedeki beş daimî koltuğun içindeki küçük kare (koltuk mürekkep) ve
4. adımdaki ret noktası, Söz ve
Kayıt’ın zaman şeridindeki veto noktaları (kitap ve karar mürekkep halka), simülasyonda
ret oyu ve mevcut sistemde vetoyla düşen sonuç ("Düştü"), logodaki kırmızı kare. Bağlantı, düğme, odak halkası, etiket, sekme çizgisi, alıntı çizgisi,
seçilmiş koltuk ve hitap işaretleri mürekkep ya da ikincil renktedir. Yeni bir kırmızı kullanım
eklenmeden önce bu kurala göre gerekçelendirilir. Ret işareti renk tek başına kalmadan okunur: Hikâye 4. adımda ret noktası
dolu kırmızı dairedir ve hemen yanındaki sonuç satırı ("14 evet, 1 hayır → düştü") oyları yazıyla da söyler.

**Yeşil kuralı.** `--kabul` (kâğıtta `#2D6A4F`, koyu kâğıtta `#6FBF8E`) yalnızca simülasyon sonucundaki "Kabul edilirdi"
içindir (sonuç kartı ve yapışkan şerit); başka hiçbir yerde kullanılmaz. Karşıtlık: `#2D6A4F` kâğıt zeminde 6,03:1, beyaz
yüzeyde 6,39:1; `#6FBF8E` koyu kâğıtta 7,87:1, koyu yüzeyde 7,00:1. "Yeni üyelerin oyuna bağlı" ikincil renktedir; önerilen
sistemde çoğunluk olmadan düşme veto olmadığı için mürekkep rengindedir. Kırmızı kuralı değişmez. Yapışkan şeridin zemini kâğıt
rengidir: koyu temada `#E05A52` koyu yüzeyde 4,23:1’e iner, koyu kâğıtta 4,76:1’dir.

**Karşıtlık.** Metin için en az 4,5:1 (büyük metin 3:1), grafik öğeler için 3:1 hedeflenir;
`tests/test_kimlik.py` palet çiftlerini hesaplar, tarayıcı denetimi (`scratchpad/erisim.py`) sayfada
ölçer. Nötr kare rengi (`#9AA3B2`) fildişi zemin üzerinde 3:1’in altındadır; karelerin yanında
her zaman sayı ve metin bulunur, renk tek başına anlam taşımaz. Simülasyonda her oy karesinin adı vardır (`aria-label`
ve `title`: evet, hayır, çekimser, katılmadı; veto karesinde üyenin adı).

## 2. Yazı, ızgara ve hizalama (`web/temel.css`)

Her sayfa `web/temel.css` dosyasını kendi stilinden önce yükler; tek dosya sürümü gömer.
`tests/test_tasarim.py` bütün stil kaynaklarını bu kurallara göre tarar; hesaplanmış değerler (her öğenin
boşluğu, yazı boyutu, satır yüksekliği ve ailesi) tarayıcıda ayrıca ölçülür.

**İki yazı tipi.** Source Serif 4 (başlıklar, okuma metni, büyük sayılar; 600) ve Source Sans 3 (arayüz,
etiket, tablo, kod ve özet değerleri). Yazı tipleri yerel dosyalardır (`web/fonts/`, SIL OFL 1.1); dış istek yoktur.
Kesimler hinting’lidir (20 Ekim; `scripts/14_yazi_tipleri.py`, `web/fonts/README.md`): Windows’ta Chrome ve Edge hinting’siz
yazıyı dikey ızgaraya oturtamıyor, 15–18 px metin bulanık görünüyordu; macOS, iOS ve Android’de fark yoktur. Çubuktaki logo
yazısının kendi kesimi vardır (bölüm 3, "Keskinlik").
Source Sans 3’ün 400 ağırlıklı italik kesimi (latin ve latin-ext) hikâyede büyük sayının alt yazısı
içindir; italik metin bu kesimle gösterilir, tarayıcı yapay italik üretmez.

**Beş yazı boyutu** (boyut / satır yüksekliği; ikisi de 4 px ızgarasında):

| Belirteç | Masaüstü | 760 px ve altı | Kullanım |
|---|---|---|---|
| `--yz-kucuk` | 15 / 24 | 15 / 24 | Etiket, künye, açıklama, tablo, çubuk bağlantıları, grafik yazıları |
| `--yz-govde` | 18 / 28 | 18 / 28 | Okuma metni, ara başlıklar (veri sayfalarında h2, her yerde h3; 600), form alanları, sonuç şeridi |
| `--yz-bolum` | 24 / 32 | 22 / 28 | Metin sayfalarında (Hakkında, Metodoloji) bölüm başlığı (h2; 600) |
| `--yz-baslik` | 40 / 48 | 32 / 40 | Sayfa başlığı (h1), hikâyede adım numarası, simülasyonda sonuç, büyük sayılar (kartlarda) |
| `--yz-gosterge` | 96 / 96 | 56 / 56 | Hikâyenin başlığı ve büyük sayıları |

**4 px ızgarası.** Bütün boşluk ve hizalamalar 4 px’in katıdır ve şu basamaklardan seçilir:
4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 (`--b1` … `--b24`). Bileşen içi 4–12, bileşenler arası ve paragraflar
16–24, alt bölüm 32, bölüm 48–64. Sayfa üstü 48 px (dar ekranda 32 px), giriş ile ilk bölüm arası 48 px.
Tek istisna okuma metnindeki kod kutusunun yatay iç boşluğudur (0.12em; basamak değil, harf payı).
Çubuk 76 px (520 px ve altında 64 px); alt çizgisi iç gölgeyle çizilir, yüksekliğe eklenmez.
Kenar boşluğu 24 px (dar ekranda 16 px); okuma metninin satırı en fazla 640 px (`--olcu`), metin sayfalarında 68ch
(`--olcu-metin`; satır başına yaklaşık 70–80 karakter). Küçük boyuttaki açıklama ve notların satırı da sınırlıdır: Kim temsil
ediliyor?’da 68ch, Ya veto olmasaydı?’da en fazla 520 px (`--olcu-kucuk`, `web/temel.css`), panel içindeki kural metinlerinde 32em.

**Hizalama (kalıcı kural).** Bütün metin sola yaslıdır; iki yana yaslama ve heceleme hiçbir genişlikte kullanılmaz.
`web/temel.css` metni sola yaslar ve hecelemeyi kapatır (`text-align: left; hyphens: none`). Gerekçe: iki yana yaslı
satırlarda kelime aralıkları açılıyordu ve Edge 155 Türkçe ve İngilizce heceleme yapmıyordu (11 Ekim 2026 ölçümü: en
geniş kelime aralığı normal boşluğun 3 katını 390 px’te satırların %25’inde, 1280 px’te %11’inde aşıyordu). Sağa
yaslama yalnızca tablolardaki sayılar ve sayaçlar içindir (basamaklar alt alta gelir; `tabular-nums`).
`tests/test_tasarim.py` bu kuralı bütün stil kaynaklarında denetler.

**Etiketler.** Etiketler (Söz ve Kayıt’ın sütun başlıkları, "Kitapta: …" bölüm künyesi,
paylaşım kartlarının üst etiketi gibi) cümle düzeninde yazılır; etiket oldukları küçük boyut (sitede `--yz-kucuk`,
kartlarda 22 px) ve ikincil renkle (`--murekkep-2`) gösterilir. Reform modelleri tablosunda model adları (sütun başlıkları)
mürekkep rengindedir, köşedeki ölçüt hücresi ikincil renktedir.
Büyük harf dönüşümü, küçük büyük harf ve açık harf aralığı kullanılmaz (büyük başlıklardaki hafif daraltma hariç).

**Bölümler.** Ana içerikteki bölümler bir öncekinden ince bir çizgi (1 px, `--cizgi`), 64 px boşluk ve çizgiyle
başlık arasında 32 px ile ayrılır; ilk bölüm girişin hemen ardından gelir. Metin sayfalarında (Hakkında, Metodoloji)
dikey ritim daha sıktır: bölümler arası 32 px (önceki metinle ayırıcı çizgi arası), çizgiyle bölüm başlığı arası 24 px,
bölüm başlığı `--yz-bolum` boyutunda (24/32, 760 px altında 22/28) ve altı 12 px; alt bölüm başlıkları (h3) çizgisizdir,
gövde boyutundadır (18/28, 600), üstü 24 px, altı 12 px; paragraflar arası 16 px. Hikâye ve
veri sayfalarının ritmi bundan etkilenmez.

**Metin sayfası.** Hakkında ve Metodoloji aynı düzendedir (`web/temel.css`, `.metin-duzen`; dizin `web/metin.js`):
başlığın altında solda okuma metni, sağda "Bu sayfada" dizini. Okuma metni sola yaslıdır; sütunu 68ch genişliğindedir
(`--olcu-metin: 68ch`; 18 px Source Sans 3’te 608 px): satır başına yaklaşık 70–80 karakter. 1100 px ve üstünde dizin
sağ sütundadır (288 px, kabın sağ kenarında) ve kaydırdıkça yerinde durur: çubuğun 24 px altında; tek dosyanın
"Nasıl yaptık?"
sekmesinde sekmenin üst kenarından 24 px aşağıda (kaydırma konumu üst belgeden bildirilir). Dizin bölüm başlıklarına (h2;
Metodoloji’de alt bölümler h3, girintili) bağlantı verir ve okunan bölümü vurgular: bağlantılar ikincil renktedir, okunan
bölümünki mürekkep rengi ve solunda 2 px mürekkep çizgiyle (`aria-current`); kırmızı kullanılmaz. Dizinden seçilen bölüm,
okur kendisi kaydırana dek vurgulu kalır. 1100 px altında dizin başlığın hemen altında katlanabilir bir kutudur ("Bu
sayfada"): kapalı başlar, bir bağlantı seçilince kapanır. Dizin başlıklardan üretilir, elle yazılmaz; her bölüm
başlığının kimliği vardır (İngilizcede "en-" önekiyle). Reform modelleri sayfasında giriş metni metin sütunu
ölçüsündedir; karşılaştırma tablosu tam genişlikte kalır ve sayfada bölüm başlığı olmadığı için dizin yoktur.
Okuma metni dar ekranda da gövde boyutundadır (760 px altında küçülmez). Metodoloji’nin ilk paragrafı Hakkında’daki gibi
giriş paragrafıdır (`.giris`); hemen altında küçük, ikincil renkte tek satır son değişiklik tarihini (git kaydından;
işlenmemiş değişiklik varsa o gün) ve asıl metnin açık depodaki `METODOLOJI.md` olduğunu söyler. Okuma metnindeki alan ve
dosya adları (`code`) metinle aynı yazı tipindedir, küçük boyutta, çok küçük yatay iç boşlukla (0.12em, 15 px’te 2 px’in altında) ve 4 px köşeyle, çizgi renginden
açık bir zemin üzerinde (`.duz-yazi code`, `web/temel.css`). 24 karakterden kısa olup tire, eğik çizgi ya da boşluk taşıyan
kod satır sonunda bölünmez (`code.kisa`; sınıfı `veto_atlasi/metodoloji.py` verir, ör. `V-YYYY-AA-GG-n`); uzun dosya adı
ve yol satıra sığmazsa kırılır. `METODOLOJI_EN.md`’nin başındaki çeviri notu (`>` satırı) depodaki dosya içindir: üretici
`>` ile başlayan satırı sayfaya taşımaz, sayfada bu bilgi yalnızca girişin altındaki küçük satırda görünür.

**Hakkında (21 Ekim 2026, kullanıcı kararı).** Beş bölüm vardır: Ne topladık ve neden, Kaynaklar ve veriyi indirme,
Terimler, Bilinen sınırlar ve düzeltmeler, İletişim (kimlikler `ne-topladik`, `kaynaklar`, `terimler`, `sinirlar`,
`iletisim`; İngilizcede `en-` önekli). Sayım, tarih, konu ve doğrulama kuralları Hakkında’da tekrarlanmaz, tek cümleyle
Metodoloji’ye bağlanır. İndirme bölümü veri dosyalarına, veri sözlüğüne ve çevrimdışı sürüme bağlantı verir. Terimler
bölümü on terimi birer cümleyle tanımlar (`dl.terimler`): resmî veto, daimî üye, öneri, ret oyu, kısmi veto, ön soru
vetosu, kapalı oturum vetosu, veto girişimi tartışması, toplantı kaydı, referans tablo. İletişim bölümü lisansı, Zenodo
arşivini ve gizlilik notunu taşır: çerez ve ziyaretçi sayacı yoktur; tema ve dil seçimi ile internetsiz açılış için
kaydedilen sayfalar yalnızca okurun tarayıcısında durur.

**Kartlar (kalıcı kural).** Tam genişlikteki, yani bulunduğu sütunu dolduran hiçbir kart tek bir dar metin sütunu
taşımaz: kart ya iki sütuna bölünür ya da genişliği metin sütununa iner (`max-width: var(--olcu-metin)`, 68ch). Kart,
zemini `--yuzey` olan çerçeveli kutudur.

- İki sütun: Söz ve Kayıt satırları ve "Kitaptaki model" kartları (sütunlar 1,15 : 1,
  aralarında 2 px çizgi; modelde solda bölüm başlığı ve özet, sağda kitaptan alıntılar ve künyeleri alt alta; 760 px
  altında tek sütun, sağ sütun kesik çizginin altına iner), simülasyonun sonuç bloğu (iki sonuç yan yana; içteki sonuçlar
  çerçevesiz ve zeminsiz, aralarında 2 px çizgi; 760 px altında üst çizgiyle alt alta).
- Metin sütunu genişliği: Reform modellerinin 960 px ve altındaki ölçüt kutusu.
- Kuralın gerektirmediği kartlar: tablo ya da form taşıyan kartlar ve ızgarada yan yana duran kartlar genişliği
  içerikleriyle doldurur. 68ch’ten dar kartlar (dar ekranda bütün kartlar) metin sütunundan geniş olamaz.
- Kart yalnızca yan yana duran ya da seçilebilen öğeler içindir (20 Ekim 2026): öne çıkan kayıtlar, sonuç kartları, grup
  kartları, Söz ve Kayıt satırları, galeri kartları, tablolar. Tek başına duran bölümler (Vetolar’ın grafiği ve konular
  listesi, simülasyonun kayıt seçimi ve sınırlar notu, Söz ve Kayıt’ın içindekiler listesi, Hakkında’daki doğrulama sayıları)
  çerçevesiz ve zeminsizdir; ayrım boşluk ve ince çizgiyle yapılır. Açılır metinler ("Ayarlar", "Kitaptan", "Filtrele",
  tablo açıcılar) kart değildir; genişlikleri en fazla 640 px’tir.

`tests/test_tasarim.py` her sayfanın kartlarını bu çözümlere göre sınıflandırır; yeni bir kart sınıflandırılmadan test
geçmez. Tarayıcı taraması (12 Ekim 2026) iki dilde 390, 900, 960, 1280 ve 2560 px’te yapıldı.

**Hikâye.** `kaynaklar/kimlik/hikaye-taslak.html` düzeni bu ızgara ve ölçekle uygulanır: 760 px sütun (24 px iç
boşluk), ortalanmış; başlığın üstünde, taslaktaki üst yazının yerinde, atlasın çıkış noktası kaynaklı bir alıntı olarak
durur: başlık boyutunda (40/48, dar ekranda 32/40) Source Serif 4 600 alıntı, altında küçük boyutta ve ikincil renkte
künye (Cumhurbaşkanı Recep Tayyip Erdoğan · etkinlik · tarih · sayfa); alıntı ile başlık arası 48 px (dar ekranda 32 px).
İki dilde de 2019 hitabından: Türkçede Türkçe kitapçıktaki “Dünya 5’ten Büyüktür.”, İngilizcede İngilizce kitapçıktaki
"The world is bigger than five!" (kaynakta italik ve tırnaksız; tırnak eklenmez). Alıntı, alıntı bankasındaki metnin içinden
birebir alınır.
Başlık ve büyük sayılar gösterge boyutunda; Türkçe başlık 960 px ve üstünde tek satırdır ve gerekirse sütunun sağına taşar
(96 px’te 776 px, sütun içi 712 px), İngilizce başlık iki satırdır; büyük sayının alt yazısı küçük boyutta, ikincil renkte ve italiktir ve sayının ne olduğunu
söyler; adım numarası başlık boyutunda, soru başlığı gövde boyutunda (600); solda sabit ilerleme rayı (760 px altında
gizli): gelecek adım içi boş halka (2 px ikincil renk), geçilen adım ikincil renkte dolu nokta, okunan adım mürekkep renginde
dolu ve büyük nokta; ayrım iki temada da renk tonuna değil biçime dayanır. Metindeki sayılar, yazıyla yazılanlar ve ekleri dâhil (on beş, yirmi yedisi, on beşinde, 1946’dan), veriden
hesaplanır; nitel ifadeler (tamamı, yarısından fazlası, neredeyse tamamı) verinin değerleriyle testte sınanır. Adımlar kaydırınca en fazla 300 ms’de belirir ve bir kez görünen adım bir daha
solmaz; gözlem eşiği 0’dır, hızlı kaydırmada üzerinden geçilen adımlar da görünür sayılır. Hareket azaltma
tercihinde animasyon yoktur.
1. adımın koltuk diyagramı: on beş koltuk tek sırada (8 px ara; 760 px altında beşerli üç sıra, ilk sıra daimî üyeler).
Daimî koltuk mürekkep, içinde sol üstte 8 px kırmızı kare (veto yetkisi) ve altında üyenin kısa kodu (CN, FR, RU, UK, US;
Şart’ın 23. maddesindeki sıra, kodlar simülasyondakilerle aynı; küçük boyut, 600, zemin renginde); kodların açılımı
diyagramın altında küçük boyutta. Bayrak kullanılmaz: beş bayrağın beşinde de kırmızı vardır (kırmızı kuralı).

**Hikâye, yedi adım (21 Ekim 2026, kullanıcı kararı).** Yedi adımın metni, görselleri, alıntıları ve bağlantıları 21 Ekim
2026’da yayımlanan hâlindedir; bir adımın içeriği ancak yeni bir kullanıcı kararıyla değişir. Sitenin yazım kuralları
adımlarda da uygulanır: kıvrık kesme ve kurum adlarına gelen ekler (bölüm 2, "Kesme ve tırnak"), şapkalı yazım, satır sonu
bağları ve "-member" birleşiği ("Satır sonu"), künye ("Künye"), paragrafın son satırı. Terim kuralları ("öneri" ve "evet
oyu"; "Noktalama ve ses", "Kayıt notu biçimi") adım metinlerine uygulanmaz: 2., 4. ve 7. adım "karar" der, 4. adım "lehte oy
kullandı" der. Bu istisna yalnız yedi adımın alt yazısı ve paragrafı içindir; girişte, kapanışta, meta açıklamada ve paylaşım
görselinin metninde terim "öneri"dir. `tests/test_hikaye.py` ve `tests/test_yazim.py` istisnayı adım adım sınırlar.

- Adım başlıkları soru ya da kısa ad biçimindedir ("Kaç karar düştü?", "Tek ülke, bütün Konsey").
- Her adımda bir alıntı vardır (sırasıyla 2019, 2023, 2024 ve 2026 hitapları, 2023 hitabının ikinci alıntısı, 2022 hitabı,
  kitabın Giriş’i); girişte 2019, kapanışta 2025 hitabı. Adımın altındaki bağlantının adı "Ayrıntı" / "Details"tir, 7. adımda
  "Sayımı kendiniz yapın" / "Run the count yourself". Hedefler: Metodoloji, Vetolar, Söz ve Kayıt’ın konuları (`#h-konu`),
  galerisi (`#h-galeri`) ve zaman çizelgesi (`#h-cizelge`), Kim temsil ediliyor?, Ya veto olmasaydı?.
- Görseller büyük sayıyı yinelemez, ona bir bilgi ekler. 1. adımda on beş koltuk. 2. adımda her ret oyu bir kare; ızgara her
  genişlikte 23 sütundur, kapalı oturum vetoları içi boş, kesik çizgili karedir. 3. adımda üye çubukları (Sovyetler Birliği
  ve Rusya aynı çubukta, kendi renkleriyle). 4. adımda on beş oy noktası (ret noktası dolu kırmızı) ve sonuç satırı. 5. adımda
  Asya-Pasifik grubunun nüfus ve koltuk payı çubukları, Afrika’nın daimî koltuk çubuğu ("0 / 5") ve küçük harita. 6. adımda
  Nisan 2022’den bu yana kullanılan her veto bir kare; Genel Kurulda görüşülenler mürekkep renginde, kareler gruplanmaz. 7.
  adımda veto olmasaydı kabul edilecek kararların çubuğu (264 / 266) ve kitap alıntısı.
- Ekran okuyucu metni görseli cümleyle söyler: "322 ret oyu, her kare bir oy. Kesik çizgili iki kare, oy dağılımı kayıtlı
  olmayan kapalı oturum vetoları."; "22 vetonun 22 tanesi Genel Kurulda görüşüldü, her kare bir veto."
- Üç istisna (21 Ekim 2026, kullanıcı kararı). 6. adımın alt yazısı ayı da söyler: "veto, Nisan 2022’den bu yana Genel
  Kurulda görüşüldü" / "vetoes debated in the General Assembly since April 2022" (ay ve yıl `GK_BAS`’tan). 5. adımın ikinci
  cümlesi Afrika grubunun payını söyler: "Aynı dönemde Afrika grubunun BM üyesi ülkelerin nüfusundaki payı iki katına
  çıktı." / "… has doubled." (kat veriden: 2023 payının 1963 payına oranı, yuvarlanmış). 7. adımın kitap alıntısı iki dilde
  aynı kısa parçadır: tıkanıklığın nedenine ilişkin ara söz atlama işaretiyle (…) çıkarılır (`KISA`, `KISA_EN`); her parça
  kaynakta birebir ve sırasıyla geçer, künyede yalnız bölüm adı vardır.

Alıntıların ve adım paragraflarının son satırında tek sözcük kalmaz (`text-wrap: pretty`, son iki sözcük arasında bölünmez
boşluk). Raydaki bir adıma tıklamak adresi `#adim-N` yapar. Yazdırmada bütün adımlar görünür, ray gizlenir, renkler basılır.

**Söz ve Kayıt, zaman çizelgesi.** Tarih gövde boyutunda (600, mürekkep); kaydırırken görünür alanın ortasındaki olay yüzey
zemini ve dolu noktayla işaretlenir (yazı boyutu değişmez). Listenin üstündeki zaman şeridi olayları zaman ölçeğinde gösterir
(veto kırmızı nokta, kitap ve karar mürekkep halka; aynı yere düşenler üst üste, en az 24 px aralık); şeritte seçilen olay
görünür alanın ortasına kayar ve odak olaya geçer (klavyede tek sekme durağı, oklar, Home ve End). Şerit yalnızca en az
761 px genişlik ve 820 px yükseklikteki ekranda üst çubuğun altında sabit kalır, daha alçak ekranda sayfayla kayar. Etkin
olayın tarihi ve adı lejantın altında, şeridin tam genişliğinde kendi satırındadır; satırın yeri baştan ayrılır, olay
seçilince alttaki liste kaymaz (dar ekranda yalnızca şerit etkinken görünür). Yalnız uzun gündem adı üç noktayla kısalır;
belge kodu ve veto eden üye aynı parçada durur ve kesilmez; 760 px altında ipucu iki satırdır (üstte
tarih, altta metin) ve lejant iki satırlık yer ayırır. Her olayın tarihi kalıcı bağlantısıdır (`#olay-YYYY-AA-GG`); adresteki olay açılışta
ortaya gelir. Hareket azaltma tercihinde kaydırma anlıktır, geçiş yoktur.

**Kim temsil ediliyor?, harita.** Tablolardan önce. Renk dört adımlı bir açıklık sırasıdır, kategorik renk değildir: öteki
üyeler `--bos`, seçilen grubun üyeleri `--h-grup` (`#9AA3B2`; koyu kâğıtta `#5F6673`, seçilmiş koltuktan ayrışsın diye),
seçilmiş koltuk `--murekkep-2`, daimî koltuk `--murekkep` (koltuk çubuğuyla aynı); komşu adımlar arasında OKLab ΔE ≥ 20
(`tests/test_harita.py`). BM üyesi olmayan alanlar boştur (zemin rengi; kenarı `--murekkep-2`, %50 opak, 0,75 px). Kırmızı ve yeşil yoktur. Grup değişince renkler
0,4 s’de geçer; ülke listesi haritanın erişilebilir karşılığıdır. Yakınlaştırma harita ve veriyi değiştirmez, yalnızca görünümü
(viewBox) büyütür: en çok 8 kat; sol altta +, − ve "Tüm dünya" düğmeleri (32 px); çift tıklama ve çift dokunma tıklanan yeri
ortaya getirip iki kat büyütür; yakınken sürükleme ve iki parmak; Ctrl + kaydırma (dokunmatik yüzeyde iki parmak). Düz kaydırma
sayfayı kaydırır. Geçiş 0,3 s, hareket azaltma tercihinde anlık; küçük devlet noktaları her ölçekte ekranda 3,5 px.
Ülke arama (tarayıcının öneri listesiyle; büyük-küçük harf ve aksan duyarsız) ve ülke kartı: tıklanan ya da aranan ülkenin
grubu, BM’ye kabul tarihi, nüfusu ve payı, bütçe payı (resmî üç ondalık), barış gücü personeli, İİT üyeliği ve Konsey durumu;
aranan ülkeye yakınlaşılır, seçili ülke 2 px mürekkep çizgiyle; dokunmatikte ipucu yerine kart açılır. Nüfus daireleri
(aç/kapa): daire alanı 2023 nüfusuyla orantılı, ekranda sabit boyda (en büyüğü 16–40 px yarıçap); daireli görünümde kara
nötr, renk dairededir. BM üyesi olmayan alanlar boş kalır ama adlıdır: ipucunda
BM’nin kullandığı adı (Türkiye’nin tanıdığı devletler Dışişleri Bakanlığının kullandığı adla: Kuzey Kıbrıs Türk
Cumhuriyeti, Kosova, Filistin, Vatikan), altında durumu; bağlı olunan devlet ve anlaşmazlıklar
yazılmaz (kullanıcı kararı, 19 Ekim 2026); arama bu alanları da bulur. BM istatistiklerinin ayrı saydığı bölgeler (Hong
Kong, Makao, Fransa’nın deniz aşırı bölgeleri, Karayip Hollandası) üyenin renginde, ipucunda kendi adı ve nüfusuyla
("Réunion · Fransa toprağı; nüfusu BM istatistiklerinde ayrı sayılır"); üyenin kartında ayrıca listelenir (kullanıcı kararı:
"nüfus sayımları ayrı ayrı, özgün isimleriyle"). Görünüm adreste saklanır (`#grup=…&ulke=…&balon=1&gorunum=x,y,kat`; varsayılanlar yazılmaz) ve
"Bağlantıyı kopyala" ile paylaşılır (dokunmatikte paylaşım menüsü, öbürlerinde panoya kopyalama).
Barış gücü personeli BM Barış ve Güvenlik Veri Merkezinin aylık katkı verisidir (şu an 31 Temmuz 2026;
peacekeeping.un.org’daki aylık PDF 28 Şubat 2026’dan sonra güncellenmedi). Veri yenilenince tarih sayfada, Metodoloji
2.9’da, `kaynaklar/KAYNAKLAR.md`’de ve Temsil kartlarının alt bilgisinde birlikte değişir. Negatif farklarda eksi
işareti kullanılır (bölüm 2, Yüzde).

**Hikâye, 5. adımın küçük haritası.** Temsil haritasıyla aynı çizim: Asya-Pasifik `--murekkep-2`, Afrika `--m-afr` (`#9AA3B2`;
koyu kâğıtta `#5F6673`), öteki üyeler `--bos`, üye olmayanlar boş; altında iki grubun adı. Harita verisi adım yaklaşınca
yüklenir; ilk sayfa hafif kalır.

**Düğmeler.** İki tür vardır; tanım `web/temel.css`’tedir (`.dugme`, `.dugme.ikincil`, `.dugme.kucuk`) ve bütün sayfalarda
aynıdır (Hikâye’de "Bütün kayıtlar", simülasyonda "Sayımı yeniden başlat" ve "Rastgele kayıt"). Birincil: dolu mürekkep zemin
(`--murekkep`), kâğıt rengi yazı (`--zemin`), Source Sans 3 600 gövde boyutu, 48 px yükseklik, 24 px yatay iç boşluk, 6 px köşe.
İkincil: açık zemin (`--yuzey`), mürekkep yazı, 1 px çizgi rengi çerçeve, aynı ölçüler. Küçük kopya (simülasyonun yapışkan
şeridi): 40 px, küçük boyut, 16 px yatay iç boşluk. Simge solda, yazı rengiyle (`currentColor`); kırmızı kullanılmaz. Pasif
durumda (ör. sayım sürerken) soluk (opaklık 0,45) ve `aria-disabled`: düğme odaklanabilir kalır, tıklama yok sayılır, odak
kaybolmaz. Odak halkası mürekkep, 2 px. Hareket azaltma tercihinde sayım animasyonsuzdur; düğme sonucu anında yeniler.
Küçük denetimlerin dokunma alanı en az 40 px’tir (simülasyonun gezinme ve ülke düğmeleri, "Temizle", açılır kutu
başlıkları; üst çubuğun düğmeleri için bölüm 3).

**Köşeler ve oklar (20 Ekim 2026).** Düğmelerin 6 px köşesi bütün denetimlerde aynıdır: üye ve grup seçim düğmeleri,
simülasyonun gezinme ve ülke düğmeleri, etiketler, ülke arama kutusu, üst çubuktaki dil, tema ve menü düğmeleri. Hap biçimi
(tam yuvarlak uçlar) kullanılmaz. Bağlantı metninde ok işareti (→, ↓) yoktur; bağlantı alt çizgisiyle tanınır. Ok yalnızca
yön bildiren düğmelerde ("← Önceki", "Sonraki →") ve Hikâye 4. adımın sonuç satırında ("14 evet, 1 hayır → düştü") kalır.
Ya veto olmasaydı?’da adım göstergesi yoktur; bölüm başlıkları numarasızdır ("Kaydı seçin"). `tests/test_tasarim.py` denetler.

**Noktalama ve ses (20 Ekim 2026).** Orta nokta (·) yalnızca künyede kullanılır; cümlelerde, sayaçlarda ve etiketlerde
virgül ("13 evet, 1 hayır, 1 çekimser", "60 öneri, 60 oy"). Arayüz metninde cümle başına en çok bir noktalı virgül;
Metodoloji yöntem metni olarak bu kuralın dışındadır. "Etiket: içerik" kalıbı yalnızca liste başlıklarında kalır
("Toplantı kayıtları: …"); cümleler etiketle değil özneyle başlar ("67 üye devlet ve 3 gözlemci konuştu", "Veto eden ABD
söz aldı"). Parantez içi sözlük yoktur ("evet (lehte)" değil "evet"); terim "öneri"dir, giriş cümlesinde "karar taslağı" (Hikâye’nin
yedi adımı bu terim kuralının dışındadır; bölüm 2, "Hikâye, yedi adım").
Öne çıkan kayıt başlıkları iki noktayla açılmaz ("Gazze: ateşkes taslağı" değil "Gazze’de ateşkes taslağı").
Hakkında ve sayfa notlarında anlatıcı "biz"dir, atlas kendinden üçüncü kişiyle söz etmez; Metodoloji edilgen kalır.
Şapkalı yazım tek biçimdir: daimî, resmî, dâhil. Metodoloji’nin paragrafları kalın etiketle açılmaz. Bu bölümün kuralları
açık depodaki Markdown belgelerine (README, METODOLOJI, KAYNAKLAR) de uygulanır; Metodoloji’nin başında son değişiklik
tarihi yazılır (git kaydından).
Tarihler yazıyla (10 Ekim 2026), ISO biçimi okuma metninde kullanılmaz; SHA-256 özeti okuma metninde değil
`kaynaklar/KAYNAKLAR.md`’dedir. Açılır başlıklar (`summary`) tarayıcı üçgeni olmadan, altı çizili bağlantı gibidir
(`web/temel.css`); açık kutunun başlığında alt çizgi kalkar (Ya veto olmasaydı?). Tablo açıcının adı tek sözcüktür:
"Tablo". Soru başlıklı okuma kutusu kullanılmaz: grafik açıklaması tek cümledir, etkileşim ve klavye notları yalnızca ekran okuyucuya gider, oran gibi okuma
kuralları ilgili bölümün açıklamasında tek cümledir. Öne çıkan kayıtlar kart ızgarası değil iki sütunlu listedir (seçili
kayıt solda 2 px çizgi). Kayıt ayrıntısındaki "Mutabakat" satırı veri dosyasındaki kısa kodu okura cümle olarak yazar
("Oy dağılımı toplantı kaydından eklendi (S/PV.10130)."). Sievers ve Daws’ın Tablo 4’ü sitede "referans tablo"dur;
tek bir satırı "referans tablo (Tablo 4, #N)" diye anılır.

**Kayıt notu biçimi.** Kayıt notlarında çalışma günlüğü dili yer almaz: indirme tarihi, iç dosya adları ve yerel yollar,
erişim sorunları, okura iş bırakan cümleler ("doğrulanmalı") ve süreç cümleleri ("eşleştirildi", "bağlandı", "esas
alındı") yoktur. Not etiketle açılmaz ("Oy dağılımı: …" değil) ve panelde başka satırda duran sayıyı, belge simgesini ve
sayfayı yinelemez. İç tablo adı (scprocedure), ISO tarih ve "Tarih farkı" satırı kullanılmaz; tarih yazıyla ve bir kez
verilir. Yer paragrafla gösterilir ("par. 54"), "PDF s." yazılmaz. Türkçe notta alıntı çift tırnaklıdır, aralıklarda yarım
çizgi (–) kullanılır, saat yerine "akşam", "sabaha karşı" yazılır, sıra sayıları yazıyladır ("üçüncüsü") ve her not
noktayla biter. Oy sayımı paneldeki terimlerle yazılır ("11 evet, 2 hayır, 2 çekimser"; İngilizcede "11 in favour,
2 against, 2 abstaining"); sayıdan sonra "lehte" ya da "aleyhte" gelmez. Üyenin oyu "hayır oyu verdi", "evet oyu verdi" diye yazılır ("aleyhte oy
verdi", "lehte oy verdi" yazılmaz); paylaşım kartlarında da böyledir. Hikâye 4. adımının "lehte oy kullandı" ifadesi bu
kuralın tek istisnasıdır. Notlarda da yazım şapkalıdır (daimî, resmî,
dâhil). Birçok kayda uyan yöntem notu kayıtlarda tekrarlanmaz, Metodoloji’de bir kez yazılır.

**Kesme ve tırnak (21 Ekim 2026).** Görünen metinde kesme işareti kıvrıktır (’): Türkiye’nin, 1946’dan, Council’s,
members’. Kural sözlüklere, meta açıklamalara, veriye (gündem adları, kayıt notları, düzeltme açıklamaları, Temsil
notları), CSV metinlerine ve Markdown belgelerine uygulanır; sayı ekleri de böyle yazılır (`${yil}’${ek}`). Düz kesme (')
yalnızca kodda, kimliklerde, adreslerde, dosya adlarında ve kaynaktan eşleştirme için olduğu gibi saklanan özgün
adlarda kalır (ör. WPP ve BM listelerindeki `Côte d'Ivoire`). Alıntı bankasındaki alıntılar kaynaktaki gibidir. Alıntı
tırnağı “ ”dir. Alıntı dış çift tırnak içinde gösterilince içindeki çift tırnak tek tırnak olur (“… ‘Dünya 5’ten
Büyüktür.’”). Dönüşümü gösteren kod yapar (Vetolar’da ve Ya veto olmasaydı?’da `icTirnak`, paylaşım kartlarında
`scripts/08_paylasim_kartlari.py`); kaynaktaki alıntı metni değişmez. Alıntıyı dış tırnaksız blok olarak gösteren yerde
(Hikâye, Söz ve Kayıt) iç tırnak kaynaktaki gibi kalır.

Kurum, kuruluş ve kurul adlarına gelen ekler kesmeyle ayrılmaz (TDK; 21 Ekim 2026, kullanıcı kararı): Güvenlik Konseyinde,
Konseyin, Konseyde, Genel Kurulda, Genel Kurulun, BM Genel Kurulunda, Afrika Grubunun, Dışişleri Bakanlığının, Veri
Merkezinin, Dag Hammarskjöld Kütüphanesinin, Afrika Birliğinin. Kesme şu adlarda kalır: kısaltmalar (BM’nin, İİT’nin,
WPP’nin), ülke ve devlet adları (Türkiye’nin, Rusya Federasyonu’nun), kişi adları (Erdoğan’ın), yer adları (Gazze’de), dönem
adları (Soğuk Savaş’ın), sayılar (1946’dan), sayfa, belge, bölüm ve kitap adları (Söz ve Kayıt’ın, Ezulwini Uzlaşısı’nı,
Şart’ın, 2. Bölüm’de) ve makam adı (Genel Sekreter’in).
Alıntı metinleri kaynaktaki gibi kalır. Kural sözlüklere, meta açıklamalara, veriye, CSV metinlerine, paylaşım kartlarına
ve Markdown belgelerine uygulanır; `tests/test_yazim.py` Türkçe görünen metinde kesmeli kurum biçimini arar.

**Yüzde.** Türkçede yüzde işareti sayının önüne gelir (%58, %18,3), İngilizcede arkasına (58%, 18.3%); sayı ile
işaret arasında boşluk yoktur. Sayfalarda, kartlarda ve testlerde aynıdır; `tests/test_yazim.py` denetler. Negatif
sayılarda eksi işareti kısa çizgi değil U+2212’dir (−1,4).

**Satır sonu.** Birlikte okunan parçalar satır sonunda ayrılmaz; sözlükteki metin değişmez, sayfa betiği yazarken bağlar.
Tarihte gün, ay ve yıl bölünmez boşlukla (U+00A0) birleşir; yıl ve madde aralıklarında yarım çizginin iki yanına sözcük
birleştirici (U+2060) girer (1963–2023, 8 (g)–(i)); sayı ile ardındaki ad bölünmez boşlukla bağlanır (12 devlet, 12 states);
"Madde 27/3", "Article 27 (3)" ve sayı ile "-member" birleşiği ("20-member", "eleven-member", "fifty-four-member";
Hikâye’de `bitisik()`) tek parçadır. Paragraf göndermesinde kısaltma ile sayı, sayı ile ardındaki
madde harfi bölünmez boşlukla bağlanır ("par. 5 (b)", "paras. 5 (b)", "A/59/L.67 (b)", "Ezulwini C (e) 2–3"; Ya veto
olmasaydı?’da `kirilmaz()`; aynı işlev eşik çiftinde noktalı virgülden sonraki boşluğu da bağlar: "(9/15; 7/11)").
Not ve açıklama metinlerinde de "s." ve "p." numarasından ayrılmaz ("A/76/PV.69, s. 20"; Söz ve Kayıt’ta bölünmez boşluk
sözlükte yazılıdır). Vetolar’ın durum satırında sayı ile ardındaki sözcüğü sayfa betiği bağlar (`sayiBagla`: "53 öneri",
"3 of them").
Oy kodu ardındaki kapanış paranteziyle birlikte bölünmez ("12-3-0)"). Hikâye’de künye tarihini `tarihUzun` bağlar.
Metodoloji’de üretici (`veto_atlasi/metodoloji.py`, `_satir_bagla`) tarihleri, aralıkları (U+2060), kısaltma ya da
gönderme ile sayıyı (par., para., s., p., pp., No., Kural, Rule, Madde, Article, Tablo, Table), sayı ile ardındaki adı
(bağlaç ve edatlar hariç) ve sayı ile madde harfini bağlar; kod parçalarına, başlıklara ve `.md` kaynaklarına dokunmaz.
Hakkında’da aynı bağlamayı sayfa betiği (`satirBagla`) görünen metinde yapar; sabit metin değişmez.

**Künye.** Alıntı künyesi Hikâye’de, Söz ve Kayıt’ta ve paylaşım kartlarında aynı sıra ve ayraçladır:
"Cumhurbaşkanı Recep Tayyip Erdoğan · BM 74. Genel Kurulu hitabı · 24 Eylül 2019 · s. 6"; kitap alıntısında
"Cumhurbaşkanı Recep Tayyip Erdoğan · Daha Adil Bir Dünya Mümkün · Giriş". İngilizcede aynı yapı, resmî İngilizce
metnin kaynağıyla ("President Recep Tayyip Erdoğan · Address to the 74th Session of the UN General Assembly · 24 September
2019 · p. 6"). İngilizce metin BM toplantı kaydından geliyorsa sayfadan önce belge simgesi yazılır ("… · 24 September
2019 · A/74/PV.3, p. 22"); iki sayfaya yayılan alıntıda "pp." yazılır. Kitap alıntısında İngilizce baskı ve bölümü yazılır,
sayfa numarası yazılmaz ("President Recep Tayyip Erdoğan · A Fairer World is Possible · Introduction"). Resmî
İngilizcesi olmayan alıntıda künye Türkçe kaynağı gösterir; kitap adı ve bölüm İngilizce baskıdaki gibi yazılır
(A Fairer World is Possible · Introduction; Part II: A United Nations Reform) ve alıntının altında "Unofficial translation
by Veto Atlas" etiketli çeviri durur. "s.", "p." ve "pp." numarasından, tarihte gün, ay ve yıl birbirinden ayrılmaz
(bölünmez boşluk); sayfa göndermesi de tarihten ayrılmaz (aradaki ayracın iki yanında bölünmez boşluk; Hikâye, Söz ve
Kayıt). Söz ve Kayıt’ta künye satırı yalnız parça sınırında bölünür: her parça kendi kutusundadır (`.kunye .kp`,
`inline-block`), orta nokta önceki parçayla aynı satırda kalır; en çok 12 harflik son parça ("Giriş", "Introduction") önceki
parçayla aynı kutuda durur, alt satırda tek başına kalmaz. Hikâye’de künye düz metin olarak akar; parça kutusu orada 390 px’te
İngilizce künyeyi bir satır uzatır. Paylaşım kartlarında ad alıntının altında,
kalan kısım alt bilgide aynı sıra ve ayraçla tek satırda durur. Simülasyondaki "Kitabın girişinden" satırı ve Reform modellerindeki
hücre altı belge satırı künye değildir.

**Kitabın adı (14 Ekim 2026, kullanıcı kararı).** Türkçe sayfalarda “Daha Adil Bir Dünya Mümkün”, bölümler "Giriş" ve
"2. Bölüm". İngilizce sayfalarda kitap İngilizce baskının adıyla anılır: “A Fairer World is Possible”. Her sayfada ilk
geçişte Türkçe özgün adı parantez içinde ve `lang="tr"` ile verilir. Meta açıklamada `lang` yazılamadığı için orada yalnız
parantez kullanılır. Bölümler İngilizce sayfalarda her yerde "Introduction" ve "Part II"dir (İngilizce baskıda "Part II:
A United Nations Reform"). Söz ve Kayıt’taki model bölümünün künyesi İngilizcede: "Recep Tayyip Erdoğan, *A Fairer World is
Possible: A Proposed Model for a United Nations Reform*, Turkuvaz Kitap, 2021; Turkish original: *Daha Adil Bir Dünya
Mümkün*". Alt başlık künye sayfasından (PDF s. 4) alındı. Lisans dosyasının (`LICENSE-DATA`) İngilizce bölümü yalnız
İngilizcedir: kitap orada “A Fairer World is Possible” ve “its Turkish original” diye anılır, Türkçe adı geçmez
(21 Ekim 2026).

**Dil işareti.** İngilizce sayfalardaki Türkçe ifadeler (alıntılar, bölüm adları, belge ve başlık adları) `lang="tr"`
taşır; Metodoloji’nin Markdown kaynağında `[metin]{lang=tr}` yazılır. Türkçe sayfalardaki İngilizce adlar (kitap ve yayın
adları) `lang="en"` taşır (Hakkında’da `<cite lang="en">`).

**İlk ekranda tek fikir.** Çubuğun altında yalnızca başlık, bir cümle ve ilk görsel; okuma notu varsa tek cümledir ve
ilk görselin altındadır. Betikle dolan sayfa, içerik hazır olana kadar görünmez (Ya veto olmasaydı?: `html.hazir`);
yüklenirken düzen kaymaz.

**Okuma kolaylığı.**

- Grafik açıklaması tek cümledir; etkileşim ve klavye notları görünmez, yalnızca ekran okuyucuya gider
  (`aria-describedby`; Vetolar).
- Aynı not iki yerde tekrarlanmaz: iki panelin ortak notu panellerin altında bir kez verilir (Ya veto olmasaydı?).
- Ya veto olmasaydı?: paneller oyları sayar; sonuç panellerin altında tek bir "Sonuç" bloğundadır
  (`kaynaklar/kimlik/sonuc-taslak.html`): başlıkta kaydın tarihi ve belge numarası; iki sonuç kartı yan yana (sistem adı ve
  kural özeti, büyük sonuç sözcüğü, tek cümle neden; ayar notu önerilen sistem kartında tek satır); altında fark cümlesi,
  birincil ve ikincil düğme. Mobilde kartlar alt alta. "Sınırlar" notu kutusuz iki cümledir, panellerin altında;
  sayım sırası notu Metodoloji 2.10’dadır. Yapışkan şerit aynı renklerle iki sonucu ve küçük "Yeniden say" düğmesini taşır; yalnızca sonuç kartları
  ekran dışındayken görünür. 760 px altında düğme şeritte yer almaz, şerit tek satırdır.
- Varsayıma dayanan seçenekler (karar eşiği, üye sayısı) varsayılan olarak kapalı "Ayarlar" kutusundadır; kutudaki tek
  cümle kitabın 20 üyeli Konsey önerdiğini ama karar eşiğini yazmadığını, eşiğin ve sayımdaki üye sayısının varsayım
  olduğunu söyler. Varsayılandan farklı bir ayar seçildiğinde, kutu kapalıyken de
  önerilen sistemin sonuç kartında tek satırlık bir not (ör. "üçte iki eşiği, 20 üyeli Konsey ile sayıldı") görünür (Ya veto
  olmasaydı?).
- Söz ve Kayıt’ta girişin altında bölümlere bağlantı veren bir "İçindekiler" listesi bulunur (kutu değil, üstte ve
  altta çizgi); metin sayfalarında
  (Hakkında, Metodoloji) bunun yerine "Bu sayfada" dizini vardır (bkz. Metin sayfası). Tek dosya sürümünde sayfa içi
  bağlantılar sayfanın kendi çerçevesinde kalır.
- Söz ve Kayıt satırlarının ve "Kitaptaki model" kartlarının üstünde bir sütun başlığı satırı vardır (Söz / Kayıt;
  Unsur / Kitaptan): ikincil renk, küçük boyut, 600, alt çizgili; liste kaydırılırken üst çubuğun altında yapışkan kalır.
  Hücrelerde etiket yoktur. 760 px altında satırlar tek sütuna indiğinde başlık satırı görünmez (ekran okuyucuya açık
  kalır); Söz ve Kayıt satırlarında kayıt bölümünün başında küçük "Kayıt" etiketi görünür. Model kartlarında etiket
  gerekmez: alıntıların künyesi kitabı gösterir. Sütunlar ekran okuyucu için tablo rolleriyle (table, row, columnheader,
  cell) işaretlidir; başlık satırı satırlarla aynı tablodadır.
- Sayfa başlığı (h1) üst çubuktaki sekme adıyla aynıdır (Vetolar, Söz ve Kayıt, Kim temsil ediliyor?, Reform modelleri, Ya
  veto olmasaydı?); "Nasıl yaptık?" sekmesinin iki sayfası kendi adını taşır (Hakkında, Metodoloji). Hikâye’nin başlığı
  "Yedi adımda veto"dur. Giriş cümlesi sayfanın konusunu söyler, sayfayı tarif etmez ("Temsil endeksinde Asya-Pasifik
  Grubunun …").
- Metodoloji’de bölümler sayıyla numaralanır (1, 2, 2.1, 2.2 …); alt bölümler "Bu sayfada" dizininde üst bölümün altında
  girintili, sayfada çizgisiz alt başlıktır (h3).
- Grafiğin işaretleri (kapalı oturum vetosu, Cumhurbaşkanı Erdoğan’ın Genel Kurul hitabı) üye lejantından ayrı,
  kendi satırında açıklanır (Vetolar). Üye lejantı, Temsil’deki grup seçimi ve simülasyondaki veto eden ülke seçimi
  çerçevesiz sekme satırıdır: seçili öğe 2 px mürekkep alt çizgili ve 600; seçim varken ötekiler soluk (20 Ekim 2026).
  Temsil’in İngilizce sekmeleri BM grup adını "Group" sözcüğü olmadan verir (African, Asia-Pacific, Eastern European, Latin
  American and Caribbean, Western European and Others).
- Karşılaştırma tablosu açık durur: geniş ekranda tablo, 960 px ve altında ölçüt ölçüt alt alta (Reform modelleri);
  961–1180 px arasında hücre iç boşluğu 12 px, ölçüt sütunu 144 px. Altı ölçüt vardır; ilk satır taslağı kimin sunduğunu
  ("Kim sundu?"), veto satırından sonraki satır karar için gereken oyu gösterir.
- Vetolar’da kayıt türü "Genel Kurulda görüşülenler" seçilince (`?tur=genel-kurul`) listenin üstünde başlıklı bir tablo
  çıkar: her Genel Kurul tartışması bir satırdır (veto tarihi, gündem, veto eden, tartışma tarihi ve türü, konuşan üye
  devlet, veto edenin söz alıp almadığı, tutanak); gündem kaydı açar. Aynı tartışmada (aynı tarihler ve tutanaklar)
  görüşülen vetolar o satırda alt alta durur: veto tarihi, gündem ve veto eden her veto için ayrı, tartışma hücreleri
  hepsini kapsar. 521 px ve üstünde tablo kendi kabında (`role="region"`, odaklanabilir) durur; sığmadığında yatay kayar
  ve kaydırılacak içerik olan kenarda 48 px’lik solma görünür. 520 px ve altında, öteki blok tablolar gibi, her tartışma
  bir bloktur (21 Ekim 2026, kullanıcı kararı): başta tartışma tarihi (600) ve türü, altında her veto (veto tarihi, gündem,
  veto eden), sonra konuşan üye devlet, söz ve tutanak. Değerlerin solunda sütun adı durur (10em sütun); yatay kayma yoktur.
  Sütun başlıkları ekran okuyucuya açık kalır; her tartışma ayrı bir `tbody`’dir, satır ve hücreler `role` taşır.
- Tablo notları tablonun kaydırma kabının dışında, altında durur (Söz ve Kayıt, Ya veto olmasaydı?); yana kaydırınca not
  yerinde kalır. 520 px ve altında Söz ve Kayıt’ın hitaplar arası ve Gazze tabloları, simülasyonun özet tablosu, Temsil’in
  nüfus tablosu ve Vetolar’ın Genel Kurul tablosu satır satır bloklara iner: satırın ilk hücresi başlık olur, her değerin yanında sütun adı yazar (uzun
  sütun adının kısası: Gazze tablosunda "Oy" / "Vote"; tam ad başlıkta ekran okuyucuya açık); masaüstü düzeni değişmez.
  Gazze tablosunda veto eden üyeler lejanttaki gibi 12 px arayla dizilir; virgül adın yanında kalır.
  Temsil’in harita altındaki ülke listesi blok olmaz: 520 px ve altında ülke adı ve sayı sütunu başlıkları satır kırar,
  hücre iç boşluğu dikeyde 8 px, yatayda 4 px’tir (sütun arası 8 px); ilk sütunun solunda ve son sütunun sağında boşluk
  yoktur. Liste 390 px’te iki dilde, bütün görünümlerde kutuya sığar.
- Aleyhte oy sayısı veto eden daimî üye sayısından büyükse oy satırının altında tek cümle öteki hayır oylarının daimî
  olmayan üyelerin olduğunu ve veto sayılmadığını söyler (Vetolar). Öteki hayır oyu tekse cümle tekildir ("Öteki hayır oyu
  daimî olmayan bir üyenindir; veto sayılmaz.").
- İngilizce sayılı cümleler 1 için tekildir (Ya veto olmasaydı?: "at least 1 vote in favour is needed", "In 1 record").
- Vetolar’da arama bir konunun yer adıyla ("Gazze") ya da adındaki bir sözcükle ("İsrail", "Israel") eşleşir ve
  sonuçların hepsi o konuya bağlıysa durum satırı konuyu ve ikincil olarak bağlı kayıt sayısını söyler. Konunun tam adı
  aranır ve ikincil bağ yoksa ("Ukraine") düz sayım yazar.

**Paylaşılabilir adresler.** Görünüm adrese yazılır (`history.replaceState`; varsayılanlar yazılmaz, `?lang=en` korunur),
açılışta ve geri tuşunda okunur:

- Vetolar: `konu`, `uye`, `donem`, `tur`, `q`, `yil` ve açık kayıt `kayit` (`?kayit=V-…`; eski `#k-…` adresi de kaydı açar).
  Açık kaydın altında iki bağlantı vardır: "Bu kaydın bağlantısı" (panoya kopyalar, "Kopyalandı" ekran okuyucuya da
  söylenir) ve "Bu kayıtta hata bildirin" (e-posta, konu satırında kayıt kimliği).
- Hikâye: `#adim-N`. 6. adımın bağlantısı Söz ve Kayıt’ın zaman çizelgesine gider (`vizyon.html#h-cizelge`).
- Söz ve Kayıt: `#olay-YYYY-AA-GG`, alıntılar `#alinti-<kimlik>`, kitaptaki model `#h-model`.
- Ya veto olmasaydı?: `?kayit=V-…`.
- Kim temsil ediliyor?: `#grup=…&ulke=…&balon=1&gorunum=x,y,kat`.

**Yöntem yalnızca "Nasıl yaptık?"ta (kalıcı kural).** Yöntem ve kaynak açıklamaları "Nasıl yaptık?" sekmesindeki
Hakkında ve Metodoloji sayfalarındadır; başka sayfalarda yöntem açıklaması eklenmez. Diğer sayfalarda kaynak dosyası
adı, SHA-256, indirme listesi, "sayılar veri setinden hesaplanır" türü notlar, alt bilgide kaynak listesi ya da
tanımlar bölümü yer almaz. Sayfalarda kalanlar: ekrandaki bir sayıyı ya da işareti okumak için gereken kısa notlar
(tek cümlelik grafik açıklamaları; simülasyonda "Sınırlar" notu), alıntı künyeleri ve kayıtların belge
bağlantıları. Alt bilgide son vetonun ve verinin güncellendiği tarih (Hikâye, Vetolar: "Son veto 17 Eylül 2026’da, veri 20 Ekim
2026’da güncellendi.") ve her sayfada alt bilgi notu bulunur. `tests/test_okunurluk.py` denetler.

## 3. Logo ve işaret (logo paketi v3)

Logo ve işaret dosyaları logo paketi v3’tendir (13 Ekim 2026; v3 v2’den yalnızca Android ana ekran ikonunda ve manifestte
ayrılır). Dosyalar vektördür (yazılar yola çevrilmiş), boşluksuz kırpılmıştır ve sitenin renklerini kullanır: mürekkep
`#13213A`, ret kırmızısı `#A4262C`, ikincil `#5A6578`; koyu zemin sürümlerinde (`-koyu`) `#EDE8E0`, `#E05A52`, `#AEB8C4`.
Kaynak `kaynaklar/kimlik/paket/`’tir (paketin kendisi): sitedeki logo ve işaret dosyaları `paket/svg/`’dekilerle, sekme ve
uygulama simgeleri `paket/web/`’dekilerle baytı baytına aynıdır (`tests/test_kimlik.py`).

- Ortak üst çubuk (`web/cubuk.js`, bütün sayfalar ve tek dosya sürümü): solda asıl işaret (`isaret.svg`, koyu kâğıtta
  `isaret-koyu.svg`) 40 px yükseklikte ve yanında canlı logo yazısı "Veto Atlası" (20 Ekim; ölçüler "Keskinlik"te); ikisi
  birlikte `logo-cubuk-b.svg`’nin görünümünü ve 183 px’lik genişliğini verir, hikâyeye bağlanır; çubuk 76 px (alt çizgi iç gölgeyle
  çizilir, yüksekliğe eklenmez). Sağda sayfa bağlantıları (Hikâye · Vetolar · Söz ve Kayıt · Kim temsil ediliyor? ·
  Reform modelleri · Ya veto olmasaydı? · Nasıl yaptık?; aralarında 12 px), en sağda TR/EN ve tema düğmesi. Sekme sırası
  Hikâye’nin anlatım sırasıdır (21 Ekim 2026, kullanıcı kararı); tek dosyanın sekmeleri, site haritası ve internetsiz
  kopya listesi (`veto_atlasi/cevrimdisi.py`, `SAYFALAR`) aynı sıradadır. Dil, tema ve menü düğmeleri masaüstünde 40 px
  yüksekliktedir (dokunma hedefi), yatay iç boşluk 8 px; aralarında 8 px, grubun solunda ek pay yoktur. Çubuk
  yapışkandır ve %92 saydam zemin üzerinde bulanıklık kullanır (taslaktaki gibi); sayfa içi bağlantılar 84 px kaydırma
  payıyla çubuğun altına iner. Bağlantılar tek satıra sığmadığında (betik ölçer; dile ve genişliğe göre) "Menü"
  düğmesine toplanır. Betik iki şeyi ölçer: çubuk içeriğinin kaydırma genişliğini ve dil ile tema düğmelerinin sağ kenarının
  çubuk içeriğinin sağ kenarını (iç boşluk hariç) aşıp aşmadığını; İngilizce "Dark" düğmesi kaydırma genişliğini büyütmeden
  kenar boşluğuna taşabiliyordu. 1100–1440 px’te TR ve EN çubuk taşmaz; 520 px ve altında asıl işaret 34 px yükseklikte (`isaret.svg`, koyu kâğıtta `isaret-koyu.svg`) ve
  yanında logo yazısı aynı oranla 23,2 px (harf aralığı 0,17 px, işaretle arası 12 px); 380 px altında yazı 20,8 px, 340 px
  altında yalnızca işaret. Telefonda (520 px ve altı) dil ve menü düğmeleri 34 px yüksekliktedir, yatay iç boşluk 8 px
  (logo yazısı sığsın diye; WCAG 2.2 AA en az 24 px ister); tema düğmesi yalnızca simgedir (34 × 34 px; adı
  `aria-label`’da). Çubuk 64 px, kaydırma payı 72 px. Logo yazısının telefonda da görünmesi 21 Ekim 2026 kullanıcı
  kararıdır; 360–430 px’te TR ve EN çubuk taşmadan sığar. Telefonlar 2–3 kat piksel yoğunluğuyla çizdiği için işaret ve yazı bu boyutta nettir.
- İçeriğe atlama bağlantısı: çubuğun ilk odak durağı "İçeriğe geç" / "Skip to content" bağlantısıdır (`.c-atla`). Yalnızca
  odaklanınca çubuğun solunda ikincil düğme görünümünde (48 px) belirir ve görünen dilin ana içeriğine (`main`; Vetolar’da
  sayfa kabı) odağı taşır; adres değişmez. Tek dosyada yoktur. Tek dosyanın çubuğunda bunun yerine kısa not durur:
  "Çevrimdışı sürüm" / "Offline version" (uzun hâli `title`’da: "Çevrimdışı sürüm. Bütün sayfalar bu dosyada."; 760 px
  altında gizli).
- Keskinlik (20 Ekim): çubuk logosu tek bir SVG değildir. `logo-cubuk-b.svg`’deki yazı yola çevrilmiş olduğundan %100 ölçekte
  (1 kat piksel yoğunluğu) tarayıcı onu gri tonlu yumuşatmayla çiziyor, yanındaki menü yazıları ise hinting ve ClearType (renkli
  alt piksel) netliğinde çıkıyordu; logo yazısı bulanık, 5 px’e düşen halka kareleri lekeli görünüyordu (Windows, Chrome, ekran
  görüntüsüyle doğrulandı; %150 ve üstünde sorun yok). Yazı bu yüzden canlı metin oldu: `Veto Atlası Logo` kesimi
  (`web/fonts/veto-atlasi-logo.woff2`: Source Serif 4 Semibold, optik boy 20, yani logo paketinin yazıyı yola çevirdiği kesim;
  yalnızca "Veto Atlası"nın 10 glifi, hinting’li, 4 kB), `logo-cubuk-b.svg`’nin 40 px’e ölçeklenmiş ölçüleriyle: yazı
  52/76,19 × 40 = 27,3 px, harf aralığı 0,2 px, işaretle arası 14 px, taban çizgisi işaretin üstünden 28,4 px (40 px satır
  kutusunda 1 px aşağı); Chromium’da 4 kat yoğunlukta ölçüldü, yazının mürekkep kutusu SVG’dekiyle 0,25 px içinde aynıdır.
  Yazının rengi `--murekkep` (koyu kâğıtta kendiliğinden açılır); yazı tipi yüklenene kadar yedek gösterilmez
  (`font-display: block`). `tests/test_tasarim.py` logo yazısı kurallarını yazı ölçeği taramasının dışında tutar. Yazının
  sınıf adı `c-yazi`’dir: reklam engelleyicilerin ortak listesi EasyList eski `c-ad` sınıfını genel bir kuralla (`##.c-ad`)
  gizlediği için 20–21 Ekim’de engelleyicili masaüstü tarayıcılarda logo yazısı görünmedi. Sınıf ve kimlik adlarında `ad`,
  `ads`, `banner`, `sponsor` gibi parçalar kullanılmaz (`tests/test_kimlik.py`). Halkanın 1 kat
  yoğunlukta ~5 px’lik kareleri çizimin sınırıdır; küçük boya özel bir işaret çizimi (piksele oturan kareler) ayrı bir karardır,
  yapılmadı. `logo-cubuk-b.svg` ve koyu sürümü sitede kullanılmaz, kimlik dosyası olarak `web/` altında ve pakette durur
  (bayt bayt aynı). Eski not (13 Ekim): logo 183 px genişlikte tam piksele oturuyordu; Edge’de 1265 ve 1280 px pencerede
  çizilenler 1 px kaydırmayla birebir aynıydı.
- Sayfaların içinde logo kullanılmaz; üst çubuktaki logo yeterlidir. Sloganlı tam logo (`logo-yatay-a.svg`, koyu
  kâğıtta `logo-yatay-a-koyu.svg`) kimlik dosyası olarak `web/` altında durur; sayfalarda ve tek dosya sürümünde
  yer almaz. Slogan ("Dünya 5’ten büyüktür" / "The world is bigger than five") sayfaların alt bilgisinde
  tekrarlanmaz; atlasın çıkış noktası hikâyenin giriş alıntısında ve Hakkında sayfasının girişinde yazılıdır. Sayfa
  başlığı `h1` olarak kalır.
- İşaret: 32 px ve üstünde (telefonda her boyutta) `isaret.svg` (çubuk, kartlar, önizleme); 32 px’in altında
  `isaret-kucuk.svg`. İkisi de aynı 15 kareden oluşur; küçük sürümde kareler biraz küçük, aralar biraz geniştir. Eski
  küçük işaretin iri kareleri üst üste binip kalın, dişli bir halka oluşturuyordu; bu çizim kaldırıldı.
  `isaret-kucuk.svg` ve `isaret-kucuk-koyu.svg` `web/` altında durur, sitede kullanılmaz.
- Sekme ve uygulama simgeleri lacivert zeminli settir (kaynağı `kaynaklar/kimlik/paket/web/`, sitede aynı adlarla):
  `favicon.ico` (16 + 32 + 48 px), `favicon.svg`, `apple-touch-icon.png` (180 px, opak zemin), `icon-192.png` ve
  `icon-512.png`, maskable olarak ayrı çizilmiş `icon-maskable-192.png` ve `icon-maskable-512.png` (logo paketi v3); hepsi
  `site.webmanifest`’te. Android (Samsung dahil) maskable görselin yalnızca ortadaki üçte ikisini (72/108) gösterip kendi
  şekline kırpar; işaret merkezden en çok 0,315 × genişlik uzaktadır, o alanın içinde kalır (13 Ekim’de ölçüldü; test
  denetler). Aynı görsel hem normal hem maskable ikon olarak kullanılmaz: eski sitede `ikon-512.png` ikisi için de
  tanımlıydı, halkanın kenarı ve kırmızı kare kesiliyordu. Manifestte `id` ve `start_url` `/hikaye`dir (ana ekrandan açılınca
  hikâye). Ana ekrana eklenmiş kısayollar ikonlarını kendiliğinden güncellemez; simge değişince eski kısayol silinip site
  yeniden eklenir (Chrome menüsünde "Uygulamayı yükle" görünürse o seçilir). `<head>` satırları:

  ```html
  <link rel="icon" href="favicon.ico?v=2" sizes="32x32">
  <link rel="icon" href="favicon.svg?v=2" type="image/svg+xml">
  <link rel="apple-touch-icon" href="apple-touch-icon.png?v=2">
  <link rel="manifest" href="site.webmanifest">
  <meta name="theme-color" content="#FBF8F1">
  ```

  ICO yalnızca 32x32 yedektir; eski `sizes="any"` Chrome’un SVG yerine pikselli ICO’yu seçmesine yol açıyordu. `?v=2`
  eski simgelerin tarayıcı önbelleğinden düşmesi içindir; simge yeniden değişirse sayı artırılır. Yollar sitedeki öteki
  bağlantılar gibi göreli yazılır (`favicon.ico`, `/favicon.ico` değil); paketin örneği
  (`kaynaklar/kimlik/paket/web/head-etiketleri.html`) kökten yazılmıştır ve paylaşım satırları da içerir. Eski simgeler
  (`ikon-192/512.png`, `isaret-180/192/512.png`, `ikon-maskable-*.png`) kullanılmaz. Tek dosya sürümü aynı simgeleri
  gömer.
- Paylaşım görseli: sayfaların `og:image`’ı `onizleme.png`’dir (veri grafiği; bölüm 6). Ya veto olmasaydı? ve Söz ve Kayıt
  kendi önizlemesini kullanır (`onizleme-simulasyon.png`, `onizleme-vizyon.png`; ikisi de `web/` kökünde). Paketin logolu
  paylaşım görseli `og-image.png` (1200 × 630) yalnızca pakette durur (`paket/web/`), sitede yoktur.
- Tek renk: `paket/svg/isaret-tek-renk.svg` ve `paket/svg/tek-renk/` (siyah ve beyaz sürümler). Kırmızı kare başka renge
  çevrilmez ve yeri değişmez.
- En küçük boyut (paket v2): çubuk logosu 40 px yükseklik; sloganlı yatay logo 240 px, sloganlı dikey logo 160 px
  genişlik; işaret 32 px’in altında `isaret-kucuk.svg`.
- Boşluk payı: işaretin etrafında en az bir kare genişliği; logo esnetilmez, döndürülmez; gölge, degrade ve 3B efekt
  kullanılmaz.
- Kartların sağ alt köşesinde `isaret.svg`: eski dosyadaki gibi 44 × 44 px kutu, çizim içinde ortalanmış 34 px yükseklikte
  (31,4 × 34 px; viewBox’a eşit pay eklenir). Kutu aynı kaldığı için alt bilgi satırı değişmez; 13 Ekim’de 44 kart canlıdakiyle
  yalnızca işaretin 32 × 34 px’lik alanında farklıydı. Adın yanında süs olduğu için `aria-hidden`. Paylaşım önizlemelerinde
  sol üstte 40 px yükseklikte çubuk logosu (`logo-cubuk-b.svg`, yazı işaretli; sol üst köşesi 89, 74 px):
  `scripts/06_onizleme_gorseli.py` dosyadaki yolları çizer, harflerin iç boşluklarını açık bırakır, kenarları yumuşatır.
  Logo ya da önizleme değişince eski ve yeni görsel piksel piksel karşılaştırılır; fark yalnızca değişen bölgede olur.
- Görünür boyutlar (çizimin kendisi; eski dosyalarda çevresinde boşluk vardı): çubuk logosu 183 × 40 px (eski 184 × 40),
  kart işareti 31 × 34 px (eski 31 × 34), önizleme logosu 183 × 40 px; telefon çubuğundaki işaret 31 × 34 px
  (eski küçük işaret 29 × 33).
- Kimlik klasörü (13 Ekim’de düzenlendi): `KILAVUZ.md`, tasarım referansları (`hikaye-taslak.html`, `sonuc-taslak.html`)
  ve `paket/`: logo paketi v3’ün `svg/` (tek renk sürümleriyle), `web/`, `sosyal/`, `kaynak/` (üretim betiği `uret.py`,
  yazı tipleri ve lisansları), `KULLANIM.md` ve `onizleme.html`’i. Paketin PNG’leri, baskı dosyaları (EPS ve PDF; depoya
  PDF girmez) ve `pano.png`’si depoda yoktur; `kaynak/uret.py` bunları pakette yeniden üretir (üretilenler commit edilmez),
  tamamı paketin zip’indedir. Eski paketin 45 dosyası kaldırıldı; git geçmişinde durur.

## 4. İlkeler

- **Veri süsten önce gelir.** Her görsel bir sayıya karşılık gelir; süs amaçlı şekil, doku ve
  arka plan görseli kullanılmaz. Hareket yalnızca anlamı taşıdığında ve hareket azaltma tercihine
  uyarak kullanılır.
- **Felaket görseli kullanılmaz.** Savaş, yıkım, yas ve mağduriyet fotoğrafı ya da çizimi yoktur;
  anlatım kayıt, oy ve sayıyla yapılır.
- **Değerlendirme dili yoktur.** Sayılar ve kaynaklar verilir; karşılaştırmalı ("tek", "ilk",
  "yalnızca o") iddialar yalnızca imzalı bir Sunuş metninde yer alabilir (sitede şu an Sunuş yok).
- **Kaynak her yerde.** Her alıntı künyesiyle, her kayıt belgeleriyle birlikte görünür; kart ve hikâye dâhil.
  Sayıların kaynakları ve yöntem "Nasıl yaptık?" sekmesinde (Hakkında, Metodoloji) bir arada verilir; sayfalarda
  tekrarlanmaz.

## 5. Tasarım referansı: `hikaye-taslak.html`

`kaynaklar/kimlik/hikaye-taslak.html` hikâye sayfasının (ve ortak üst çubuğun) ölçü, boşluk ve tipografi
kararlarının referansıdır; sitenin parçası değildir ve yayımlanmaz. Taslaktaki yollar yereldir ve depoda
karşılıkları yoktur, bu yüzden dosya doğrudan açıldığında yazı tipleri ve logo yüklenmez:

- `@font-face` yolları: `SourceSerif4-Regular.otf`, `SourceSerif4-Semibold.otf`, `SourceSans3-Regular.otf`,
  `SourceSans3-Semibold.otf` (taslakla aynı klasörde beklenen OTF dosyaları). Sitede aynı aileler
  `web/fonts/` altındaki woff2 dosyalarıyla (`web/fonts/fonts.css`) kullanılır.
- Logo yolu: `cikti/logo-yatay-a.svg`; sitedeki karşılığı `web/logo-yatay-a.svg`.

Taslaktaki sayılar ve metinler örnektir; sitede sayılar veri setinden hesaplanır, metinler `web/hikaye.html`
sözlüğündedir.

## 6. Yayın öğeleri

**Yayın adresi.** `https://vetoatlas.com` (vetoatlas.org bu adrese yönlendirilir). Her sayfa `og:url`, mutlak
`og:image` (`https://vetoatlas.com/onizleme.png`; Ya veto olmasaydı? ve Söz ve Kayıt’ta kendi önizlemesi), `og:image:alt`
ve `twitter:image:alt`, `canonical` ve `hreflang` (tr, en = `?lang=en`, x-default) taşır;
İngilizce görünümde `web/cubuk.js` canonical ve `og:url` adresine `?lang=en` ekler. Giriş sayfasının
(`web/index.html`) canonical adresi hikâyedir. Tek dosyada sayfa çerçeveleri canonical ve hreflang taşımaz.
Paylaşım kartlarının alt bilgisi: "Veto Atlası · vetoatlas.com" / "Veto Atlas · vetoatlas.com"; solda kaynak satırı
("DHL veto listesi ve S/PV kayıtları, 17 Eylül 2026"). Sol üst etiket yalnızca alıntı kartlarında ("Söz ve Kayıt"); sayı
kartlarında etiket yoktur (20 Ekim 2026).

**Paylaşım kartları (21 Ekim 2026, kullanıcı kararı).** Kartlarda üst bant yoktur; üst boşluk 48 px, kimliği alt bilgideki
işaret ve çizgi taşır. Oylar sitedeki gibi karedir (16 px, aralarında 6 px, ret karesi sonda ve kırmızı); daire
kullanılmaz. Konular kartında gri iz konunun bütün ret oylarıdır, ucunda ikincil renkte toplamı yazar ("/ 53"). Kart cümlesi
tek bilgi söyler; tarih ve kaynak cümlede değil alt bilgidedir, ikinci bilgi varsa görsel notundadır (kart 02 ve 03).
Künye dışında orta nokta kullanılmaz. Temsil kartlarının (09–11) alt bilgisi yalnız kartta gösterilen ölçülerin kaynaklarını
sayar (Asya-Pasifik: WPP 2024, Konsey 2026; Afrika: barış gücü verisinin ayı, Konsey 2026; P5: WPP 2024, bütçe ölçeği
2025–2027, Konsey 2026). Afrika kartındaki barış gücü çubuğunun etiketi verinin ayını söyler ("Barış gücü personeli payı,
Temmuz 2026") ve rengi Temsil sayfasındaki personel rengidir (`--g-personel`).

**Önizleme görseli.** Sözcük yoktur, yalnızca sayı ve yıl (iki dilde aynı): sol üstte çubuk logosu, sağ üstte 96 px kayıt
sayısı ve 22 px dönem (1946–2026), birim grafiğin çentiklerinin altında onyıllar (18 px, ikincil renk), altta çizgi ve
adres. Sayfaya özel önizlemeler (Ya veto olmasaydı?, Söz ve Kayıt) `scripts/08_paylasim_kartlari.py` ile aynı düzende
üretilir; her sayfanın `og:image:alt` metni kendi görselini anlatır. Söz ve Kayıt önizlemesinde sağ üstte yalnız "22 / 22"
vardır. 22 kare iki sırada (11 + 11) durur, veto girişimi tartışmalarının 15 küçük karesi altta tek sıradadır. Görünen
kareler simülasyon önizlemesiyle aynı yükseklikte başlar ve aynı sol ve sağ kenarda durur; grafik büyük sayı ile alt çizgi
arasını doldurur.

**Önizleme alt metni.** `og:image:alt` ve `twitter:image:alt` sayfanın statik başlığında iki dillidir ("Türkçe / English");
Hikâye, Vetolar, Söz ve Kayıt, Kim temsil ediliyor?, Reform modelleri ve Metodoloji’de sayfa betiği açılışta görünen dile
göre sözlükteki metni yazar (Hikâye’de `gorselAlt`, sayısı veri setinden; Metodoloji’de `veto_atlasi/metodoloji.py`, öteki
sayfalarda `onizlemeAlt`); Hakkında ve Ya veto olmasaydı?’da statik metin kalır. Ortak önizleme için metin: "Veto Atlası: 1946’dan 2026’ya Güvenlik
Konseyinde vetoyla düşen 266 öneri; her kare bir ret oyu, yıllara göre." / "Veto Atlas: 266 proposals blocked by the
veto in the Security Council, 1946–2026; each square is one negative vote, by year." Söz ve Kayıt ve Ya veto olmasaydı?
kendi görsellerini anlatır (22 vetonun hepsi ve 15 küçük kare; 266 önerinin 264’ü ve kesikli iki kare).

**Alt bilgi notu.** Her sayfanın altında tek satır: "Beta sürümü. Hata bildirmek için iletisim@vetoatlas.com adresine
yazın." (EN "Beta version. To report an error, write to …"). `web/cubuk.js` kurar: sayfanın kendi alt bilgisi varsa (Hikâye,
Vetolar) ona eklenir, yoksa sayfa kabının sonunda ince çizgili bir alt bilgi oluşturulur; tek dosyada her çerçeve kendi
notunu taşır.

**İnternetsiz çalışma.** `web/cevrimdisi.js` (service worker; `veto_atlasi/cevrimdisi.py` üretir, 04 ve 11 yeniler)
sekiz sayfayı, 404 sayfasını ve kullandıkları dosyaları (betikler, stiller, veri, yazı tipleri, çubuk logoları, uygulama ikonları; yaklaşık
1,1 MB) ilk açılışta kaydeder. Önce ağ: internet varken her istek sunucudan gelir, site ziyaretçisi için bir şey değişmez;
ağ 4 saniyede yanıt vermezse ya da internet yoksa kayıtlı kopya sunulur, kaydı olmayan sayfa adresinde 404 kopyası açılır. Sürüm kaydedilen dosyaların içerik özetidir; biri değişince yeni kopya kaydedilir,
eskisi silinir. Paylaşım kartları, indirme dosyaları (`web/veri/`) ve tek dosya kaydedilmez. `web/cubuk.js` yalnızca güvenli
bağlamda (https) kaydeder; tek dosya ve dosya olarak açılış kaydetmez, veri tasarrufu açıksa (`navigator.connection.saveData`)
kayıt yapılmaz. Yalnızca site içi isteklere karışır, dış istek yoktur.

**Çevrimdışı sürüm.** Sitenin tamamı tek HTML dosyası olarak da vardır (`veto-atlasi-tek-dosya.html`,
`scripts/10_tek_dosya.py`); Hakkında’nın indirme bölümünden bağlıdır (İngilizcede `?lang=en`). Çerçevelerdeki göreli
bağlantılar (`LICENSE-DATA.txt`, `veri/`) yayın adresine yazılır.

**Önbellek ve başlıklar (`web/_headers`).** Yazı tipleri bir yıl değişmez sayılır (`immutable`), PNG ve SVG bir hafta
önbellekte kalır, HTML ve veri her açılışta doğrulanır. Yazı tipi dosyası değişirse dosya adına sürüm eklenir; `fonts.css`
ve internetsiz kopya listesi birlikte yenilenir. Her yanıtta `X-Content-Type-Options: nosniff`, `Referrer-Policy:
strict-origin-when-cross-origin` ve kamera, mikrofon ve konumu kapatan `Permissions-Policy` vardır. Paylaşım kartları ve
tek dosya `X-Robots-Tag: noindex` taşır; `robots.txt` onları engellemez.

**Veri sözlüğü.** Açık verinin her sütunu `kaynaklar/veri_sozlugu.csv`’de bir kez, iki dilde açıklanır; boş değerin anlamı
da iki dildedir (`bos_anlami`, `bos_anlami_en`), tip kısa koddur. `scripts/04_web_verisi.py`
sözlüğü `web/veri/veri_sozlugu.csv` olarak yazar, sütunlarını CSV başlıklarıyla birebir denetler ve iki XLSX dosyasına
sözlük sayfası ekler; şemada (`schema/veto_kaydi.schema.json`) her alanın açıklaması vardır. Hakkında’nın indirme bölümü
sözlüğe bağlantı verir.

**Sunuş kutusu (sitede yok).** Hikâyede başlık ve özetten sonra doğrudan 1. adım gelir. İleride bir Sunuş eklenirse
kutu `web/hikaye.html` içinde `<div class="giris">` ile `<div id="adimlar">` arasına (ikisi de tek `main` içinde) girer; kapalıyken tek satır
(solda başlık, sağda imza ve açma oku), 48 px. Çerçeve iç gölgeyle çizildiği için kart kuralında "metin" sınıfındadır
(`tests/test_tasarim.py`, `KARTLAR`). Metni ve imzası yayımlayan tarafından yazılır; sözlüğe `sunus.baslik`,
`sunus.imza`, `sunus.metin` anahtarlarıyla iki dilde eklenir.

İşaretleme:

```html
  <details class="sunus">
    <summary><h2 id="h-sunus" data-t="sunus.baslik"></h2><p class="imza" data-t="sunus.imza"></p></summary>
    <p class="bos" data-t="sunus.metin"></p>
  </details>
```

Stil (hareket azaltma tercihinde `.sunus summary::after` geçişi kapatılır):

```css
/* Sunuş: başlığın altında, ilk adımın önünde; kapalıyken tek satır (solda başlık, sağda imza ve açma oku), en fazla 48 px */
.sunus { background: var(--yuzey); box-shadow: inset 0 0 0 1px var(--cizgi); border-radius: 6px; margin: 0 0 16px; }
.sunus summary { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 16px; min-height: 48px; padding: 0 16px; }
.sunus summary::-webkit-details-marker { display: none; }
.sunus summary::after { content: ""; flex: none; width: 8px; height: 8px; margin: -4px 4px 0 0; border-right: 2px solid var(--murekkep); border-bottom: 2px solid var(--murekkep); transform: rotate(45deg); transition: transform .2s; }
.sunus[open] summary::after { transform: rotate(-135deg); margin-top: 4px; }
.sunus summary:focus-visible { outline: 2px solid var(--murekkep); outline-offset: -2px; border-radius: 6px; }
.sunus h2 { font-family: var(--serif); font-weight: 600; font-size: var(--yz-govde); line-height: var(--sa-govde); margin: 0; flex: none; }
.sunus .imza { margin: 0 0 0 auto; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: var(--yz-kucuk); line-height: var(--sa-kucuk); }
.sunus .imza, .sunus .bos { color: var(--murekkep-2); font-style: italic; }
.sunus .bos { margin: 0; padding: 4px 16px 16px; }
```
