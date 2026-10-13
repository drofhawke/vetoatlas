# Veto Atlası – tasarım kılavuzu

Bu kılavuz `KULLANIM.md`'yi temel alır ve sitenin, kartların ve tek dosya sürümünün paylaştığı
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
| `--bos` | `#EDE7DA` | `#2E2A24` | Boş ve seçili alan, çubuk arka planı |
| `--oy-lehte` | `#9AA3B2` | `#8B94A3` | Nötr kare ve "evet (lehte)" oyu |
| `--oy-aleyhte` | `#13213A` | `#EDE8E0` | "Hayır (aleyhte)" oyu |
| `--oy-cekimser` | `#D9D3C7` | `#4A463F` | Çekimser oy |
| `--vurgu` | `#A4262C` | `#E05A52` | **Yalnızca ret oyu ve veto** |
| `--kabul` | `#2D6A4F` | `#6FBF8E` | **Yalnızca simülasyon sonucu "Kabul edilirdi"** |

Üye renkleri (açık tema; koyu temada açık tonları): Sovyetler Birliği `#7E2F3C`, Rusya Federasyonu
`#C2666F`, ABD `#24507F`, Birleşik Krallık `#2F7A6E`, Fransa `#A8782A`, Çin `#5E4E9A`.

**Tema.** Site her zaman kâğıt (açık) temada açılır; işletim sisteminin koyu tema tercihi dikkate
alınmaz (`prefers-color-scheme` kullanılmaz). Koyu kâğıt yalnızca üst çubuktaki "Koyu" düğmesiyle seçilir
(`:root[data-theme="dark"]`) ve tarayıcıda hatırlanır (`localStorage`, erişilemezse kâğıt kalır).
`tests/test_kimlik.py` varsayılanın kâğıt olduğunu denetler.

**Kırmızı kuralı.** `--vurgu` yalnızca ret oyunu ve vetoyu gösterir: birim grafikteki ret kareleri,
galerideki ve kartlardaki "bir hayır" noktası, hikâyedeki beş daimî koltuğun içindeki küçük kare (koltuk mürekkep), simülasyonda
ret oyu ve mevcut sistemde vetoyla düşen sonuç ("Düştü"), logodaki kırmızı kare. Bağlantı, düğme, odak halkası, etiket, sekme çizgisi, alıntı çizgisi,
seçilmiş koltuk ve hitap işaretleri mürekkep ya da ikincil renktedir. Yeni bir kırmızı kullanım
eklenmeden önce bu kurala göre gerekçelendirilir.

**Yeşil kuralı.** `--kabul` (kâğıtta `#2D6A4F`, koyu kâğıtta `#6FBF8E`) yalnızca simülasyon sonucundaki "Kabul edilirdi"
içindir (sonuç kartı ve yapışkan şerit); başka hiçbir yerde kullanılmaz. Karşıtlık: `#2D6A4F` kâğıt zeminde 6,03:1, beyaz
yüzeyde 6,39:1; `#6FBF8E` koyu kâğıtta 7,87:1, koyu yüzeyde 7,00:1. "Yeni üyelerin oyuna bağlı" ikincil renktedir; önerilen
sistemde çoğunluk olmadan düşme veto olmadığı için mürekkep rengindedir. Kırmızı kuralı değişmez. Yapışkan şeridin zemini kâğıt
rengidir: koyu temada `#E05A52` koyu yüzeyde 4,23:1'e iner, koyu kâğıtta 4,76:1'dir.

**Karşıtlık.** Metin için en az 4,5:1 (büyük metin 3:1), grafik öğeler için 3:1 hedeflenir;
`tests/test_kimlik.py` palet çiftlerini hesaplar, tarayıcı denetimi (`scratchpad/erisim.py`) sayfada
ölçer. Nötr kare rengi (`#9AA3B2`) fildişi zemin üzerinde 3:1'in altındadır; karelerin yanında
her zaman sayı ve metin bulunur, renk tek başına anlam taşımaz.

## 2. Yazı, ızgara ve hizalama (`web/temel.css`)

Her sayfa `web/temel.css` dosyasını kendi stilinden önce yükler; tek dosya sürümü gömer.
`tests/test_tasarim.py` bütün stil kaynaklarını bu kurallara göre tarar; hesaplanmış değerler (her öğenin
boşluğu, yazı boyutu, satır yüksekliği ve ailesi) tarayıcıda ayrıca ölçülür.

**İki yazı tipi.** Source Serif 4 (başlıklar, okuma metni, büyük sayılar; 600) ve Source Sans 3 (arayüz,
etiket, tablo, kod ve özet değerleri). Yazı tipleri yerel dosyalardır (`web/fonts/`, SIL OFL 1.1); dış istek yoktur.
Source Sans 3'ün 400 ağırlıklı italik kesimi (latin ve latin-ext) hikâyede büyük sayının alt yazısı
içindir; italik metin bu kesimle gösterilir, tarayıcı yapay italik üretmez.

**Dört yazı boyutu** (boyut / satır yüksekliği; ikisi de 4 px ızgarasında):

| Belirteç | Masaüstü | 760 px ve altı | Kullanım |
|---|---|---|---|
| `--yz-kucuk` | 15 / 24 | 15 / 24 | Etiket, künye, açıklama, tablo, çubuk bağlantıları, grafik yazıları |
| `--yz-govde` | 18 / 28 | 18 / 28 | Okuma metni, ara başlıklar (h2, h3; 600), form alanları, sonuç şeridi |
| `--yz-baslik` | 40 / 48 | 32 / 40 | Sayfa başlığı (h1), hikâyede adım numarası, simülasyonda sonuç, büyük sayılar (kartlarda) |
| `--yz-gosterge` | 96 / 96 | 56 / 56 | Hikâyenin başlığı ve büyük sayıları |

**4 px ızgarası.** Bütün boşluk ve hizalamalar 4 px'in katıdır ve şu basamaklardan seçilir:
4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 (`--b1` … `--b24`). Bileşen içi 4–12, bileşenler arası ve paragraflar
16–24, alt bölüm 32, bölüm 48–64. Sayfa üstü 48 px (dar ekranda 32 px), giriş ile ilk bölüm arası 48 px.
Çubuk 76 px (dar ekranda 64 px), üstündeki beta şeridi 32 px; çizgileri iç gölgeyle çizilir, yüksekliğe eklenmez.
Kenar boşluğu 24 px (dar ekranda 16 px); okuma metninin satırı en fazla 640 px (`--olcu`), metin sayfalarında 68ch
(`--olcu-metin`; satır başına yaklaşık 70–80 karakter).

**Hizalama (kalıcı kural).** Bütün metin sola yaslıdır; iki yana yaslama ve heceleme hiçbir genişlikte kullanılmaz.
`web/temel.css` metni sola yaslar ve hecelemeyi kapatır (`text-align: left; hyphens: none`). Gerekçe: iki yana yaslı
satırlarda kelime aralıkları açılıyordu ve Edge 155 Türkçe ve İngilizce heceleme yapmıyordu (11 Ekim 2026 ölçümü: en
geniş kelime aralığı normal boşluğun 3 katını 390 px'te satırların %25'inde, 1280 px'te %11'inde aşıyordu). Sağa
yaslama yalnızca tablolardaki sayılar ve sayaçlar içindir (basamaklar alt alta gelir; `tabular-nums`).
`tests/test_tasarim.py` bu kuralı bütün stil kaynaklarında denetler.

**Etiketler.** Etiketler (Söz ve Kayıt'ın sütun başlıkları, "Kitapta: …" bölüm künyesi,
paylaşım kartlarının üst etiketi gibi) cümle düzeninde yazılır; etiket oldukları küçük boyut (sitede `--yz-kucuk`,
kartlarda 22 px) ve ikincil renkle (`--murekkep-2`) gösterilir.
Büyük harf dönüşümü, küçük büyük harf ve açık harf aralığı kullanılmaz (büyük başlıklardaki hafif daraltma hariç).

**Bölümler.** Ana içerikteki bölümler bir öncekinden ince bir çizgi (1 px, `--cizgi`), 64 px boşluk ve çizgiyle
başlık arasında 32 px ile ayrılır; ilk bölüm girişin hemen ardından gelir. Metin sayfalarında (Hakkında, Metodoloji)
dikey ritim daha sıktır: bölümler arası 32 px (önceki metinle ayırıcı çizgi arası), çizgiyle bölüm başlığı arası 24 px,
başlığın altı 12 px; alt bölüm başlıkları (h3) çizgisizdir, üstü 24 px, altı 12 px; paragraflar arası 16 px. Hikâye ve
veri sayfalarının ritmi bundan etkilenmez.

**Metin sayfası.** Hakkında ve Metodoloji aynı düzendedir (`web/temel.css`, `.metin-duzen`; dizin `web/metin.js`):
başlığın altında solda okuma metni, sağda "Bu sayfada" dizini. Okuma metni sola yaslıdır; sütunu 68ch genişliğindedir
(`--olcu-metin: 68ch`; 18 px Source Sans 3'te 608 px): satır başına yaklaşık 70–80 karakter. 1100 px ve üstünde dizin
sağ sütundadır (288 px, kabın sağ kenarında) ve kaydırdıkça yerinde durur: çubuğun 24 px altında; tek dosyanın
"Nasıl yaptık?"
sekmesinde sekmenin üst kenarından 24 px aşağıda (kaydırma konumu üst belgeden bildirilir). Dizin bölüm başlıklarına (h2;
Metodoloji'de alt bölümler h3, girintili) bağlantı verir ve okunan bölümü vurgular: bağlantılar ikincil renktedir, okunan
bölümünki mürekkep rengi ve solunda 2 px mürekkep çizgiyle (`aria-current`); kırmızı kullanılmaz. Dizinden seçilen bölüm,
okur kendisi kaydırana dek vurgulu kalır. 1100 px altında dizin başlığın hemen altında katlanabilir bir kutudur ("Bu
sayfada"): kapalı başlar, bir bağlantı seçilince kapanır. Dizin başlıklardan üretilir, elle yazılmaz; her bölüm
başlığının kimliği vardır (İngilizcede "en-" önekiyle). Reform modelleri sayfasında giriş metni ve "Nasıl okunur?"
kutusu aynı ölçüdedir; karşılaştırma tablosu tam genişlikte kalır ve sayfada bölüm başlığı olmadığı için dizin yoktur.

**Kartlar (kalıcı kural).** Tam genişlikteki, yani bulunduğu sütunu dolduran hiçbir kart tek bir dar metin sütunu
taşımaz: kart ya iki sütuna bölünür ya da genişliği metin sütununa iner (`max-width: var(--olcu-metin)`, 68ch). Kart,
zemini `--yuzey` olan çerçeveli kutudur.

- İki sütun: Söz ve Kayıt satırları ve "Kitaptaki model" kartları (sütunlar 1,15 : 1,
  aralarında 2 px çizgi; modelde solda bölüm başlığı ve özet, sağda kitaptan alıntılar ve künyeleri alt alta; 760 px
  altında tek sütun, sağ sütun kesik çizginin altına iner), simülasyonun iki sonuç kartı, Söz ve Kayıt'ın içindekiler
  kutusu (iki sütunlu liste).
- Metin sütunu genişliği: Ya veto olmasaydı? "Sınırlar", Reform modellerinin 960 px ve altındaki ölçüt kutusu, Vetolar
  kayıtlarındaki "Veto girişimi (A/RES/76/262) hakkında" kutusu.
- Kuralın gerektirmediği kartlar: tablo, grafik ya da form taşıyan kartlar ve ızgarada yan yana duran kartlar genişliği
  içerikleriyle doldurur; metin sütununun içindeki kartlar (Hakkında) kurala
  uyar. 68ch'ten dar kartlar (dar ekranda bütün kartlar) metin sütunundan geniş olamaz.
- Zemini ve çerçevesi olmayan açılır metinler ("Nasıl okunur?", "Nasıl hesaplanıyor?") kart değildir; genişlikleri en
  fazla 640 px'tir.

`tests/test_tasarim.py` her sayfanın kartlarını bu çözümlere göre sınıflandırır; yeni bir kart sınıflandırılmadan test
geçmez. Tarayıcı taraması (12 Ekim 2026) iki dilde 390, 900, 960, 1280 ve 2560 px'te yapıldı.

**Hikâye.** `kaynaklar/kimlik/hikaye-taslak.html` düzeni bu ızgara ve ölçekle uygulanır: 760 px sütun (24 px iç
boşluk), ortalanmış; başlığın üstünde, taslaktaki üst yazının yerinde, atlasın çıkış noktası kaynaklı bir alıntı olarak
durur: başlık boyutunda (40/48, dar ekranda 32/40) Source Serif 4 600 alıntı, altında küçük boyutta ve ikincil renkte
künye (Cumhurbaşkanı Recep Tayyip Erdoğan · tarih · etkinlik · sayfa); alıntı ile başlık arası 48 px (dar ekranda 32 px).
Türkçede 2019 hitabından “Dünya 5’ten Büyüktür.”; 2019 kitapçığında İngilizce metin olmadığı için İngilizcede 2023
hitabının İngilizce metninden “The world is bigger than five.” Alıntı, alıntı bankasındaki metnin içinden birebir alınır.
Başlık ve büyük sayılar gösterge boyutunda; Türkçe başlık 960 px ve üstünde tek satırdır ve gerekirse sütunun sağına taşar
(96 px'te 776 px, sütun içi 712 px), İngilizce başlık iki satırdır; büyük sayının alt yazısı küçük boyutta, ikincil renkte ve italiktir ve sayının ne olduğunu
söyler; adım numarası başlık boyutunda, soru başlığı gövde boyutunda (600); solda sabit ilerleme rayı (760 px altında
gizli). Metindeki sayılar, yazıyla yazılanlar ve ekleri dâhil (on beş, yirmi yedisi, on beşinde, 1946'dan), veriden
hesaplanır; nitel ifadeler (tamamı, yarısından fazlası, neredeyse tamamı) verinin değerleriyle testte sınanır. Adımlar kaydırınca en fazla 300 ms'de belirir ve bir kez görünen adım bir daha
solmaz; gözlem eşiği 0'dır, hızlı kaydırmada üzerinden geçilen adımlar da görünür sayılır. Hareket azaltma
tercihinde animasyon yoktur.

**Düğmeler.** İki tür vardır; tanım `web/temel.css`'tedir (`.dugme`, `.dugme.ikincil`, `.dugme.kucuk`) ve bütün sayfalarda
aynıdır (Hikâye'de "Veriyi keşfet", simülasyonda "Sayımı yeniden başlat" ve "Rastgele kayıt"). Birincil: dolu mürekkep zemin
(`--murekkep`), kâğıt rengi yazı (`--zemin`), Source Sans 3 600 gövde boyutu, 48 px yükseklik, 24 px yatay iç boşluk, 6 px köşe.
İkincil: açık zemin (`--yuzey`), mürekkep yazı, 1 px çizgi rengi çerçeve, aynı ölçüler. Küçük kopya (simülasyonun yapışkan
şeridi): 40 px, küçük boyut, 16 px yatay iç boşluk. Simge solda, yazı rengiyle (`currentColor`); kırmızı kullanılmaz. Pasif
durumda (ör. sayım sürerken) soluk (opaklık 0,45) ve `aria-disabled`: düğme odaklanabilir kalır, tıklama yok sayılır, odak
kaybolmaz. Odak halkası mürekkep, 2 px. Hareket azaltma tercihinde sayım animasyonsuzdur; düğme sonucu anında yeniler.

**Yüzde.** Türkçede yüzde işareti sayının önüne gelir (%58, %18,3), İngilizcede arkasına (58%, 18.3%); sayı ile
işaret arasında boşluk yoktur. Sayfalarda, kartlarda ve testlerde aynıdır; `tests/test_yazim.py` denetler.

**Künye.** Alıntı künyesi Hikâye'de, Söz ve Kayıt'ta ve paylaşım kartlarında aynı sıra ve ayraçladır:
"Cumhurbaşkanı Recep Tayyip Erdoğan · BM 74. Genel Kurulu konuşması · 24 Eylül 2019 · s. 6"; kitap alıntısında
"Cumhurbaşkanı Recep Tayyip Erdoğan · Daha Adil Bir Dünya Mümkün · Giriş". İngilizcede aynı yapı ("President Recep
Tayyip Erdoğan · Address to the 74th Session of the UN General Assembly · 24 September 2019 · p. 6"); bölüm adı
İngilizceye aktarılır (Introduction; Chapter 2: … (Reform of the United Nations)), Türkçe kalan parçalar (kitap adı, bölüm
başlığı) `lang="tr"` ile işaretlenir. "s." ve "p." numarasından ayrılmaz. Paylaşım kartlarında ad alıntının altında,
kalan kısım alt bilgide aynı sıra ve ayraçla durur. Simülasyondaki "Kitapta: …" etiketi ve Reform modellerindeki
"Dayanak" satırı künye değildir.

**Dil işareti.** İngilizce sayfalardaki Türkçe ifadeler (alıntılar, bölüm adları, belge ve başlık adları) `lang="tr"`
taşır; Metodoloji'nin Markdown kaynağında `[metin]{lang=tr}` yazılır.

**İlk ekranda tek fikir.** Çubuğun altında yalnızca başlık, bir cümle ve ilk görsel; okuma notları
"Nasıl okunur?" ya da "Nasıl hesaplanıyor?" açılır kutusunda ya da ilk görselin altında.

**Okuma kolaylığı.**

- Grafik açıklaması tek cümledir; okuma ve etkileşim notları hemen altındaki "Nasıl okunur?" kutusundadır
  (Vetolar).
- Aynı not iki yerde tekrarlanmaz: iki panelin ortak notu panellerin altında bir kez verilir (Ya veto olmasaydı?).
- Ya veto olmasaydı?: paneller oyları sayar; sonuç panellerin altında tek bir "Sonuç" bloğundadır
  (`kaynaklar/kimlik/sonuc-taslak.html`): başlıkta kaydın tarihi ve belge numarası; iki sonuç kartı yan yana (sistem adı ve
  kural özeti, büyük sonuç sözcüğü, tek cümle neden; ayar notu önerilen sistem kartında tek satır); altında fark cümlesi,
  birincil ve ikincil düğme, en altta küçük yazıyla sayım sırası notu. Mobilde kartlar alt alta. "Sınırlar" kutusu açık ve
  ayrıdır, katlanmaz. Yapışkan şerit aynı renklerle iki sonucu ve küçük "Yeniden say" düğmesini taşır; yalnızca sonuç kartları
  ekran dışındayken görünür.
- Varsayıma dayanan seçenekler (karar eşiği, üye sayısı) varsayılan olarak kapalı "Ayarlar" kutusundadır; kutuda tek
  bir cümle kitabın bunları belirtmediğini söyler. Varsayılandan farklı bir ayar seçildiğinde, kutu kapalıyken de
  önerilen sistemin sonuç kartında tek satırlık bir not (ör. "Ayar: üçte iki eşiği, 20 üyeli Konsey") görünür (Ya veto
  olmasaydı?).
- Söz ve Kayıt'ta girişin altında bölümlere bağlantı veren bir "İçindekiler" kutusu bulunur; metin sayfalarında
  (Hakkında, Metodoloji) bunun yerine "Bu sayfada" dizini vardır (bkz. Metin sayfası). Tek dosya sürümünde sayfa içi
  bağlantılar sayfanın kendi çerçevesinde kalır.
- Söz ve Kayıt satırlarının ve "Kitaptaki model" kartlarının üstünde bir sütun başlığı satırı vardır (Söz / Kayıt;
  Unsur / Kitaptan): ikincil renk, küçük boyut, 600, alt çizgili; liste kaydırılırken üst çubuğun altında yapışkan kalır.
  Hücrelerde etiket yoktur. 760 px altında satırlar tek sütuna indiğinde başlık satırı görünmez (ekran okuyucuya açık
  kalır); Söz ve Kayıt satırlarında kayıt bölümünün başında küçük "Kayıt" etiketi görünür. Model kartlarında etiket
  gerekmez: alıntıların künyesi kitabı gösterir. Sütunlar ekran okuyucu için tablo rolleriyle (table, row, columnheader,
  cell) işaretlidir; başlık satırı satırlarla aynı tablodadır.
- Sayfa başlığı (h1) üst çubuktaki sekme adıyla aynıdır (Vetolar, Söz ve Kayıt, Reform modelleri, Ya veto olmasaydı?, Kim
  temsil ediliyor?, Hakkında, Metodoloji); Hikâye'nin başlığı "Yedi adımda veto"dur. Eski başlıklar giriş cümlesinde yaşar
  ("Güvenlik Konseyi reformu için dört model…", "Temsil endeksi, …").
- Metodoloji'de bölümler sayıyla numaralanır (1, 2, 2.1, 2.2 …); alt bölümler "Bu sayfada" dizininde üst bölümün altında
  girintili, sayfada çizgisiz alt başlıktır (h3).
- Grafiğin işaretleri (kapalı oturum vetosu, Cumhurbaşkanı Erdoğan'ın Genel Kurul hitabı) üye düğmelerinden ayrı,
  kendi satırında açıklanır (Vetolar).
- Karşılaştırma tablosu açık durur: geniş ekranda tablo, 960 px ve altında ölçüt ölçüt alt alta (Reform modelleri).

**Yöntem yalnızca "Nasıl yaptık?"ta (kalıcı kural).** Yöntem ve kaynak açıklamaları "Nasıl yaptık?" sekmesindeki
Hakkında ve Metodoloji sayfalarındadır; başka sayfalarda yöntem açıklaması eklenmez. Diğer sayfalarda kaynak dosyası
adı, SHA-256, indirme listesi, "sayılar veri setinden hesaplanır" türü notlar, alt bilgide kaynak listesi ya da
tanımlar bölümü yer almaz. Sayfalarda kalanlar: ekrandaki bir sayıyı ya da işareti okumak için gereken kısa notlar
("Nasıl okunur?" kutuları; simülasyonda "Nasıl hesaplanıyor?" ve "Sınırlar"), alıntı künyeleri ve kayıtların belge
bağlantıları. Alt bilgide yalnızca veri tarihi bulunur (Hikâye, Vetolar). `tests/test_okunurluk.py` denetler.

## 3. Logo ve işaret (`KULLANIM.md`)

- Ortak üst çubuk (`web/cubuk.js`, bütün sayfalar ve tek dosya sürümü): solda slogansız çubuk logosu
  `logo-cubuk-b.svg` (koyu kâğıtta `logo-cubuk-b-koyu.svg`), 52 px yükseklik, hikâyeye bağlanır; çubuk 76 px
  (alt çizgi iç gölgeyle çizilir, yüksekliğe eklenmez). Sağda sayfa bağlantıları (Hikâye · Vetolar · Söz ve Kayıt ·
  Reform modelleri · Ya veto olmasaydı? · Kim temsil ediliyor? · Nasıl yaptık?; aralarında 12 px), en sağda TR/EN
  ve tema düğmesi. Çubuk yapışkandır ve %92 saydam zemin
  üzerinde bulanıklık kullanır (taslaktaki gibi); sayfa içi bağlantılar 84 px kaydırma payıyla çubuğun altına iner.
  Bağlantılar tek satıra sığmadığında (betik ölçer; dile ve genişliğe göre) "Menü" düğmesine toplanır;
  520 px ve altında logo yerine işaret 40 px (`isaret-kucuk.svg`, koyu kâğıtta `isaret-kucuk-koyu.svg`),
  çubuk 64 px, kaydırma payı 72 px.
- Sayfaların içinde logo kullanılmaz; üst çubuktaki logo yeterlidir. Sloganlı tam logo (`logo-yatay-a.svg`, koyu
  kâğıtta `logo-yatay-a-koyu.svg`) kimlik dosyası olarak `web/` altında durur; sayfalarda ve tek dosya sürümünde
  yer almaz. Slogan ("Dünya 5'ten büyüktür" / "The world is bigger than five") sayfaların alt bilgisinde
  tekrarlanmaz; atlasın çıkış noktası hikâyenin giriş alıntısında ve Hakkında sayfasının girişinde yazılıdır. Sayfa
  başlığı `h1` olarak kalır.
- İşaret: 64 px ve üstünde `isaret.svg` (kartlar, önizleme), 48 px ve altında `isaret-kucuk.svg` (dar ekranda çubuk).
- Sekme ve uygulama simgeleri kâğıt zeminli settir (`kaynaklar/kimlik/favicon/`, favicon-kagit; kullanım notu oradaki
  `KULLANIM.md`): `favicon.ico` (16 + 32 + 48 px), `favicon.svg`, `apple-touch-icon.png` (180 px), `ikon-192.png` ve
  `ikon-512.png` (`site.webmanifest`; maskable olarak da aynı dosyalar). Zeminli simge koyu ve açık sekme çubuklarında aynı
  netlikte görünür; eski zeminsiz simgeler (`isaret-180/192/512.png`, `ikon-maskable-*.png`) kullanılmaz. `<head>` satırları
  oradaki `KULLANIM.md`'dekilerdir, sitedeki öteki bağlantılar gibi göreli yolla (`favicon.ico`, `/favicon.ico` değil). Tek
  dosya sürümü aynı simgeleri gömer.
- Tek renk: `isaret-tek-renk.svg`. Kırmızı kare başka renge çevrilmez. `isaret-kucuk-koyu.svg`,
  `isaret-kucuk.svg`'nin `logo-yatay-a-koyu.svg` renkleriyle (`#EEF1F5`, `#E34A50`) yazılmış koyu zemin sürümüdür.
- En küçük boyut: işaret 16 px, yatay logo 140 px genişlik.
- Boşluk payı: işaretin etrafında en az bir kare genişliği; logo gölge, degrade ve 3B efektsiz.
- Logo dosyalarının renkleri (`#1F2A37`, `#B3272D`, `#F7F3EC`) kimlik dosyalarında sabittir; site paleti
  (`#13213A`, `#A4262C`, `#FBF8F1`) aynı ailedendir ve logo yeniden boyanmaz.
- Kartların sağ alt köşesinde `isaret.svg` (44 px); paylaşım önizlemesinde (`onizleme.png`) sol üstte
  halka işareti.

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
`og:image` (`https://vetoatlas.com/onizleme.png`), `canonical` ve `hreflang` (tr, en = `?lang=en`, x-default) taşır;
İngilizce görünümde `web/cubuk.js` canonical ve `og:url` adresine `?lang=en` ekler. Giriş sayfasının
(`web/index.html`) canonical adresi hikâyedir. Tek dosyada sayfa çerçeveleri canonical ve hreflang taşımaz.
Paylaşım kartlarının alt bilgisi: "Veto Atlası · vetoatlas.com" / "Veto Atlas · vetoatlas.com".

**Beta şeridi.** Her sayfanın üstünde, çubuğun önünde ince bir şerit: "Beta sürümü · Hata bildirin:
iletisim@vetoatlas.com" (EN "Beta · Report an error: …"). `web/cubuk.js` kurar (tek dosyada üst belgede);
yüzey zemini, alt çizgisi iç gölgeyle, küçük yazı, 4 px dikey boşlukla 32 px. Yapışkan değildir, sayfayla kayar;
yazdırılmaz.

**Sunuş kutusu (kaldırıldı).** Hikâyede başlık ve özetten sonra doğrudan 1. adım gelir. İleride bir Sunuş eklenirse
kutu `web/hikaye.html` içinde `<header class="giris">` ile `<p class="asagi">` arasına girer; kapalıyken tek satır
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
