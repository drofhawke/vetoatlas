# Paylaşım kartları kataloğu

Kartlar `scripts/08_paylasim_kartlari.py` ile `web/kartlar/` altına üretilir: 11 kart × 2 dil (TR, EN)
× 2 boyut (1200×630, 1080×1080), HTML ve PNG. Her sayı veri setinden (`web/veri.js`) ya da temsil
endeksinden (`data/processed/temsil.json`, kart 09–11), her alıntı
alıntı bankasından (`kaynaklar/alintilar.csv`, kelimesi kelimesine doğrulanmış) gelir; kartta elle
yazılmış sayı yoktur. `web/kartlar/kartlar.json` kartların dayandığı veri setinin SHA-256'sını
taşır; veri değişince 04 betiği kartların yenilenmesi gerektiğini bildirir ve `tests/test_kartlar.py`
sayıları yeniden hesaplayıp karşılaştırır. Kartlarda ve bu katalogda değerlendirme içeren dil
kullanılmaz; sayılar ve kaynaklar verilir. Kartın metni en fazla iki cümledir: ana cümle düz, ihtiyat
(kapsam dışı kayıtlar, sayım kuralı) ikinci cümlede. Kart 02 ve 03'te ikinci bilgi cümlede değil,
görselin altındaki notta durur; aynı bilgi kartta iki kez geçmez. Tarih ve kaynak alt bilgidedir,
cümlede değil. Pay paydaya eşitse metin "tamamı" der ("22 önerinin tamamı"). Sayı kartlarının sağ yarısında (kare sürümde
sayının altında) kartın verisini gösteren sade bir görsel vardır; ana grafiğin diliyle çizilir (kare
= bir kayıt, kesikli çerçeve = kapalı oturum, üye renkleri ana sayfadakiyle aynı). Alıntı kartlarında
görsel yoktur. Kartta üst bant yoktur (üst boşluk 48 px); kimlik alt bilgideki işaret ve çizgidir. Alt
bilgi tek satırdır: solda kısa kaynak ve veri tarihi, sağda atlasın adı ve vetoatlas.com.

Aynı betik iki sayfaya özel, sözcüksüz paylaşım önizlemesi yazar: `web/onizleme-simulasyon.png`
(kart-01'in kare ızgarası, 264 / 266) ve `web/onizleme-vizyon.png` (kart-03'ün kareleri, 22 / 22).
Çerçeveleri `web/onizleme.png` ile aynıdır (06 betiği): sol üstte çubuk logosu, sağ üstte büyük sayı,
altta çizgi ve vetoatlas.com. İki önizlemede görünen kareler aynı yükseklikte başlar ve aynı sol ve sağ
kenarda durur. Söz ve Kayıt önizlemesinde 22 kare iki sırada (11 + 11) durur, 15 küçük kare altta tek sıradadır;
grafik büyük sayı ile alt çizgi arasındaki alanı doldurur. Görselde açıklamasız sayı yoktur (Söz ve Kayıt'ın
15 küçük karesini sayfanın `og:image:alt` metni anlatır).

Aşağıdaki sayılar 20 Ekim 2026 tarihli veri setine (son kayıt 17 Eylül 2026) aittir.

## kart-01-vetosuz — 264 / 266
- **Kart metni:** Veto nedeniyle kabul edilemeyen 266 önerinin 264'ü, veto olmasaydı kayıtlı oylarla
  kabul edilmiş olacaktı. Kalan 2 veto kapalı oturumda kullanılmış olup oy dağılımları kayıtlı değildir.
- **Görsel:** 266 kare (19 × 14); 264 dolu, 2 kesikli çerçeveli boş (kapalı oturum).
- **Dayanak:** Veri setindeki 266 kaydın oy dağılımları (kaynak: scprocedure Tablo 4 ve toplantı
  kayıtları, `METODOLOJI.md` 2.2).
- **Hesap:** Kapalı oturum vetoları (2) dışarıda; kalan 264 kayıtta lehte oy sayısı, kaydın
  tarihindeki çoğunluk eşiğiyle (15 üyede 9, 1966 öncesi 11 üyede 7) karşılaştırılır. 264'ünde lehte
  oy eşiğe ulaşır. Kayıtlı oyların değişmeyeceği varsayılır; veto tehdidiyle oylanmayan taslaklar
  kapsam dışıdır (`web/simulasyon.html`, "Sınırlar").
- **Paylaşım cümlesi (TR):** Veto nedeniyle kabul edilemeyen 266 önerinin oy dağılımı kayıtlı 264'ü, veto
  olmasaydı kayıtlı oylarla kabul edilmiş olacaktı.
- **Paylaşım cümlesi (EN):** Of the 266 proposals not adopted owing to a veto, 264 with a recorded vote
  breakdown would have been adopted on the recorded votes in a Council without a veto.

## kart-02-tek-ret — 55
- **Kart metni:** 55 öneri, Konseyin diğer bütün üyeleri olumlu oy kullanmış olmasına rağmen tek bir ret
  oyu nedeniyle kabul edilememiştir.
- **Görsel:** 15 kare (16 px, 6 px ara; sitedeki oy kareleri gibi); 14 lehte renginde, 1 vurgu
  renginde (ret). Altında not: Bunların 27'si 1966'dan önce, Konsey 11 üyeliyken ona karşı bir oyla
  kabul edilememiştir.
- **Dayanak:** Oy dağılımları (lehte = Konsey büyüklüğü − 1, aleyhte = 1).
- **Hesap:** `lehte + 1 == konsey_buyuklugu` ve `aleyhte == 1` olan kayıtlar; Konsey büyüklüğü
  1966 öncesi 11, sonrası 15. Ana sayfadaki özet cümlesi ve vizyon sayfasındaki "On dörde karşı
  bir" galerisi aynı kuralı kullanır.
- **Paylaşım cümlesi (TR):** 55 öneri, Konseyin diğer bütün üyeleri olumlu oy kullanmış olmasına rağmen
  tek bir ret oyu nedeniyle kabul edilememiştir.
- **Paylaşım cümlesi (EN):** 55 proposals were not adopted on a single negative vote, although every
  other member of the Council voted in favour.

## kart-03-genel-kurul — 22 / 22
- **Kart metni:** Nisan 2022'den bu yana veto nedeniyle kabul edilemeyen 22 önerinin tamamı Genel Kurulda
  görüşülmüştür.
- **Görsel:** 22 kare (2 × 11, hepsi dolu); altında 15 küçük mürekkep renkli kare ve not: Vetoyu
  kullanan ülke 15 tartışmanın tamamında söz almıştır.
- **Dayanak:** `kaynaklar/genel_kurul_tartismalari.csv` (toplantı kayıtları A/…/PV ve BM Günlüğü;
  `METODOLOJI.md` 2.5). Görüşmeler 15 veto girişimi tartışması ve 6 olağanüstü özel oturum
  toplantısında yapıldı; söz alma sayımı yalnızca veto girişimi tartışmalarını kapsar.
- **Hesap:** Tarihi 2022-04-26 ve sonrası olan kayıtlar; `gk.durum == "yapildi"` olanlar; veto
  girişimi tartışmalarında `veto_eden_konustu` alanı her veto eden üye için "hayir" olmayanlar.
  Üç tartışmada (2025-10-01, 2026-04-16, 2026-10-01) sayım tutanak yerine BM Günlüğü'nden.
- **Paylaşım cümlesi (TR):** Nisan 2022'den bu yana her veto Genel Kurulda görüşülmüştür; vetoyu
  kullanan ülke 15 tartışmanın tamamında söz almıştır.
- **Paylaşım cümlesi (EN):** Every veto since April 2022 has been debated in the General Assembly;
  the vetoing country spoke in all 15 veto initiative debates.

## kart-04-besi-de — 322
- **Kart metni:** 1946'dan bu yana 322 ret oyu kullanılmış olup beş daimî üyenin tamamı vetoya
  başvurmuştur. Kapalı oturumdaki 2 veto üye toplamlarına dâhil değildir.
- **Görsel:** Üye başına yatay çubuk, üye renkleriyle ve sayısıyla: Sovyetler Birliği 114, Rusya
  Federasyonu 43, ABD 94, Birleşik Krallık 30, Fransa 18, Çin 23.
- **Dayanak:** Veri setindeki `veto_eden_uyeler` alanı; kapalı oturumdaki 2 veto üye toplamına
  girmez (`METODOLOJI.md` 2). SSCB ve Rusya Federasyonu ayrı kodlanır; 1971 öncesi "Çin" vetosu
  Çin Cumhuriyeti'ne aittir (1 veto, 13 Aralık 1955).
- **Hesap:** Kapalı oturum dışı kayıtlarda üye başına ret oyu sayısı; çubuk uzunluğu en yüksek
  üyeye (114) göre orantılıdır.
- **Paylaşım cümlesi (TR):** 1946'dan bu yana 322 ret oyu: beş daimî üyenin tamamı vetoya başvurmuştur.
- **Paylaşım cümlesi (EN):** 322 negative votes since 1946: all five permanent members have used the
  veto.

## kart-05-konular — 4 konu
- **Kart metni:** Dört konuda en çok ret oyu kullanan üye, konudaki bütün ret oylarıyla birlikte
  gösterilmektedir. Sayımda yalnızca kaydın ana konusu esas alınmaktadır.
- **Görsel:** Dört kısa çubuk, üye renginde ve sayısıyla (Filistin – ABD 42, Suriye – Rusya
  Federasyonu 18, Güney Afrika – Birleşik Krallık 24, Üyelik başvuruları – Sovyetler Birliği 51);
  arkasındaki açık çubuk konudaki bütün ret oylarıdır ve ucunda ikincil renkte yazar (/ 53, / 28,
  / 54, / 60).
- **Dayanak:** Konu sınıflandırması `kaynaklar/gundem_sozlugu.csv` ve `konu_duzeltmeleri.csv`
  (yalnızca ana konu sayılır, `METODOLOJI.md` 2.4).
- **Hesap:** Her konu için kapalı oturum dışı kayıtlarda üye başına ret oyu; en yüksek olan.
- **Paylaşım cümlesi (TR):** Filistin'de ABD, Suriye'de Rusya, Güney Afrika'da Birleşik Krallık,
  üyelik başvurularında Sovyetler Birliği: konuya göre en çok ret oyu kullanan üyeler.
- **Paylaşım cümlesi (EN):** The United States on Palestine, Russia on Syria, the United Kingdom on
  South Africa, the Soviet Union on membership applications: the members with the most negative
  votes by topic.

## kart-06-alinti-2026 — alıntı
- **Metin (TR):** "190'dan fazla ülkenin iradesinin 5 ülkenin keyfine bağlı olduğu bir yapı, kabul
  edelim ki, ne âdildir, ne de güveni tam manasıyla tesis edebilir."
- **Metin (EN):** derlemenin İngilizce bölümünden (çevrilmedi).
- **Kaynak:** BM 81. Genel Kurulu hitabı, 22 Eylül 2026; derleme s. 16 (TR), s. 116 (EN).
  `kaynaklar/alintilar.csv` 2026-1; doğrulama `kaynaklar/alintilar_dogrulama.csv`.
- **Paylaşım cümlesi (TR):** 22 Eylül 2026 Genel Kurul hitabından, s. 16.
- **Paylaşım cümlesi (EN):** From the address to the 81st Session of the General Assembly, 22
  September 2026, p. 116.

## kart-07-alinti-2025 — alıntı
- **Metin (TR):** "Görevimiz sistemi terk etmek değil; onarmak, yeniden işler hale getirmektir."
- **Metin (EN):** derlemenin İngilizce bölümünden.
- **Kaynak:** BM 80. Genel Kurulu hitabı, 23 Eylül 2025; derleme s. 49 (TR), s. 151 (EN).
  `kaynaklar/alintilar.csv` 2025-1.
- **Paylaşım cümlesi (TR):** 23 Eylül 2025 Genel Kurul hitabından, s. 49.
- **Paylaşım cümlesi (EN):** From the address to the 80th Session of the General Assembly, 23
  September 2025, p. 151.

## kart-08-alinti-2019 — alıntı
- **Metin (TR):** "Bu kürsüden yıllardır insanlığın kaderinin sınırlı sayıdaki ülkenin ihtiyarına
  bırakılamayacağını söylüyorum. Burada sizlerin huzurunda tekrar ediyorum; "Dünya 5'ten
  Büyüktür.""
- **Kartta:** alıntının içindeki çift tırnak tek tırnak olur (‘Dünya 5’ten Büyüktür.’); kaynak metin değişmez.
- **Metin (EN):** "I have been saying for years that we cannot afford to place humanity's fate into
  the hands of a small group of nations. Today, in your presence, I say again: The world is bigger than
  five!" (İletişim Başkanlığının İngilizce kitapçığı, s. 6).
- **Kaynak:** BM 74. Genel Kurulu konuşması, 24 Eylül 2019; Türkçe ve İngilizce kitapçık s. 6.
  `kaynaklar/alintilar.csv` 2019-1.
- **Paylaşım cümlesi (TR):** 24 Eylül 2019 Genel Kurul konuşmasından, s. 6.
- **Paylaşım cümlesi (EN):** From the address to the 74th Session of the General Assembly, 24
  September 2019, p. 6.

## kart-09-asya-pasifik — %57,8
- **Kart metni:** Asya-Pasifik Grubunun 54 üyesi, BM üyesi devletlerin nüfusunun %57,8'ini oluşturmaktadır;
  Güvenlik Konseyinin 15 koltuğundan 3'ü (%20,0) bu gruba ait olup bunların 1'i daimî koltuktur.
- **Alt bilgi:** WPP 2024, Konsey 2026. Kart 09–11'in alt bilgisi yalnız kartta gösterilen ölçülerin kaynağını sayar.
- **Dayanak:** `data/processed/temsil.json` (ASP): nüfus payı 2023, koltuk (1 daimî + 2 seçilmiş) / 15
  (`METODOLOJI.md` 2.9; girdiler `kaynaklar/temsil/`).
- **Hesap:** `scripts/09_temsil.py`; kart sayıları `temsil_sayilari()` ile JSON'dan okunur, test aynı
  alanları karşılaştırır.
- **Görsel:** İki yatay çubuk alt alta: nüfus payı (lehte rengi) ve koltuk payı (mürekkep rengi),
  yüzdeyle; koltuk etiketi "Koltuk payı, 1 daimî ve 2 seçilmiş".
- **Paylaşım cümlesi (TR):** Asya-Pasifik Grubu: BM üyeleri nüfusunun %57,8'i, Konsey koltuklarının %20'si
  (1 daimî).
- **Paylaşım cümlesi (EN):** Asia-Pacific Group: 57.8% of the population of UN Member States, 20% of
  Council seats (1 permanent).

## kart-10-afrika — 0 / 5
- **Kart metni:** Afrika Grubunun 54 üyesi, barış gücü üniformalı personelinin %37,9'unu sağlamaktadır.
  Grubun Konseyde 3 seçilmiş koltuğu bulunmakta, daimî koltuğu bulunmamaktadır.
- **Dayanak:** `temsil.json` (AFR): personel payı (31 Temmuz 2026 sıralaması, üniformalı personel: asker,
  polis, uzman, karargâh subayı), bütçe payı (2025–2027 ölçeği), koltuk 0 daimî + 3 seçilmiş.
- **Hesap:** `scripts/09_temsil.py`; büyük sayı daimî koltuk / 5.
- **Alt bilgi:** Barış gücü Temmuz 2026, Konsey 2026.
- **Görsel:** Barış gücü personeli payı (%37,9) ve koltuk payı (%20,0) çubukları alt alta; çubuklar
  cümledeki ölçüyü gösterir. Personel etiketi tarihlidir ("Barış gücü personeli payı, Temmuz 2026"), çubuğu
  Kim temsil ediliyor? sayfasındaki barış gücü rengindedir (#5E4E9A).
- **Paylaşım cümlesi (TR):** Afrika Grubu: 54 üye, barış gücü personelinin %38'i, bütçe ölçeğinin %1'i,
  daimî koltuk 0.
- **Paylaşım cümlesi (EN):** African Group: 54 members, 38% of peacekeeping personnel, 1% of the budget
  scale, 0 permanent seats.

## kart-11-p5 — 5 / 5
- **Kart metni:** Beş daimî üye, BM üyesi devletlerin nüfusunun %25,6'sını oluşturmakta, olağan bütçenin
  %51,9'unu karşılamakta ve Konseyin 15 koltuğundan 5'ini elinde bulundurmaktadır.
- **Dayanak:** `temsil.json` (P5 kümesi): nüfus payı 2023 (193 üyenin toplamında), bütçe payı, koltuk
  5 daimî / 15.
- **Hesap:** `scripts/09_temsil.py`; test P5 nüfus payını elle yazılmış beş nüfusla doğrular
  (`tests/test_temsil.py`).
- **Alt bilgi:** WPP 2024, bütçe ölçeği 2025–2027, Konsey 2026.
- **Görsel:** Nüfus payı (%25,6) ve koltuk payı (%33,3) çubukları alt alta.
- **Paylaşım cümlesi (TR):** Beş daimî üye: nüfusun %25,6'sı, bütçe ölçeğinin %52'si, koltukların %33'ü,
  daimî koltukların tamamı.
- **Paylaşım cümlesi (EN):** Five permanent members: 25.6% of the population, 52% of the budget scale, 33%
  of the seats, all permanent seats.
