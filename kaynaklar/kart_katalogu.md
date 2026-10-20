# Paylaşım kartları kataloğu

Kartlar `scripts/08_paylasim_kartlari.py` ile `web/kartlar/` altına üretilir: 11 kart × 2 dil (TR, EN)
× 2 boyut (1200×630, 1080×1080), HTML ve PNG. Her sayı veri setinden (`web/veri.js`) ya da temsil
endeksinden (`data/processed/temsil.json`, kart 09–11), her alıntı
alıntı bankasından (`kaynaklar/alintilar.csv`, kelimesi kelimesine doğrulanmış) gelir; kartta elle
yazılmış sayı yoktur. `web/kartlar/kartlar.json` kartların dayandığı veri setinin SHA-256'sını
taşır; veri değişince 04 betiği kartların yenilenmesi gerektiğini bildirir ve `tests/test_kartlar.py`
sayıları yeniden hesaplayıp karşılaştırır. Kartlarda ve bu katalogda değerlendirme içeren dil
kullanılmaz; sayılar ve kaynaklar verilir. Kartın metni en fazla iki cümledir: ana cümle düz, ihtiyat
(kapsam dışı kayıtlar, sayım kuralı) ikinci cümlede. Sayı kartlarının sağ yarısında (kare sürümde
sayının altında) kartın verisini gösteren sade bir görsel vardır; ana grafiğin diliyle çizilir (kare
= bir kayıt, kesikli çerçeve = kapalı oturum, üye renkleri ana sayfadakiyle aynı). Alıntı kartlarında
görsel yoktur. Alt bilgi tek satırdır: solda kısa kaynak ve veri tarihi, sağda atlasın adı ve yayın
adresi için yer tutucu; yayın adresi belli olunca betikteki `yer` metni doldurulur.

Aşağıdaki sayılar 20 Ekim 2026 tarihli veri setine (son kayıt 17 Eylül 2026) aittir.

## kart-01-vetosuz — 264 / 266
- **Kart metni:** Veto ile düşen 266 önerinin 264'ü, veto olmasaydı kayıtlı oylarla kabul edilmiş
  olurdu. Oy dağılımı kayıtlı olmayan 2 kapalı oturum vetosu hariç.
- **Görsel:** 266 kare (19 × 14); 264 dolu, 2 kesikli çerçeveli boş (kapalı oturum).
- **Dayanak:** Veri setindeki 266 kaydın oy dağılımları (kaynak: scprocedure Tablo 4 ve toplantı
  kayıtları, `METODOLOJI.md` 2.2).
- **Hesap:** Kapalı oturum vetoları (2) dışarıda; kalan 264 kayıtta lehte oy sayısı, kaydın
  tarihindeki çoğunluk eşiğiyle (15 üyede 9, 1966 öncesi 11 üyede 7) karşılaştırılır. 264'ünde lehte
  oy eşiğe ulaşır. Kayıtlı oyların değişmeyeceği varsayılır; veto tehdidiyle oylanmayan taslaklar
  kapsam dışıdır (`web/simulasyon.html`, "Sınırlar").
- **Paylaşım cümlesi (TR):** Veto ile düşen 266 önerinin oy dağılımı kayıtlı 264'ü, veto olmasaydı
  kayıtlı oylarla kabul edilmiş olurdu.
- **Paylaşım cümlesi (EN):** Of the 266 vetoed proposals, 264 with a recorded vote breakdown would
  have been adopted on the recorded votes in a Council without a veto.

## kart-02-tek-ret — 55
- **Kart metni:** 55 öneri, Konsey'in öbür bütün üyeleri lehte oy verirken tek bir ret oyuyla düştü.
  27'si 11 üyeli Konsey'de (1966 öncesi) oylandı.
- **Görsel:** 15 nokta; 14 lehte renginde, 1 vurgu renginde (ret). Küçük not: 1966 öncesi 11 üyeli
  Konsey'de ona karşı bir, 27 öneri.
- **Dayanak:** Oy dağılımları (lehte = Konsey büyüklüğü − 1, aleyhte = 1).
- **Hesap:** `lehte + 1 == konsey_buyuklugu` ve `aleyhte == 1` olan kayıtlar; Konsey büyüklüğü
  1966 öncesi 11, sonrası 15. Ana sayfadaki özet cümlesi ve vizyon sayfasındaki "On dörde karşı
  bir" galerisi aynı kuralı kullanır.
- **Paylaşım cümlesi (TR):** 55 öneri, Konsey'in öbür bütün üyeleri lehte oy verirken tek bir ret
  oyuyla düştü.
- **Paylaşım cümlesi (EN):** 55 proposals failed on a single negative vote while every other member
  of the Council voted in favour.

## kart-03-genel-kurul — 22 / 22
- **Kart metni:** Nisan 2022'den bu yana veto ile düşen 22 önerinin 22'si Genel Kurul'da görüşüldü.
  Veto eden ülke 15 veto girişimi tartışmasının 15'inde söz aldı.
- **Görsel:** 22 kare (2 × 11, hepsi dolu); altında 15 küçük vurgu renkli kare ve "15 / 15
  tartışmada veto eden söz aldı" notu.
- **Dayanak:** `kaynaklar/genel_kurul_tartismalari.csv` (toplantı kayıtları A/…/PV ve BM Günlüğü;
  `METODOLOJI.md` 2.5). Görüşmeler 15 veto girişimi tartışması ve 6 olağanüstü özel oturum
  toplantısında yapıldı; söz alma sayımı yalnızca veto girişimi tartışmalarını kapsar.
- **Hesap:** Tarihi 2022-04-26 ve sonrası olan kayıtlar; `gk.durum == "yapildi"` olanlar; veto
  girişimi tartışmalarında `veto_eden_konustu` alanı her veto eden üye için "hayir" olmayanlar.
  Üç tartışmada (2025-10-01, 2026-04-16, 2026-10-01) sayım tutanak yerine BM Günlüğü'nden.
- **Paylaşım cümlesi (TR):** Nisan 2022'den bu yana her veto Genel Kurul'da görüşüldü; veto eden
  ülke 15 tartışmanın 15'inde kürsüye çıktı.
- **Paylaşım cümlesi (EN):** Every veto since April 2022 has been debated in the General Assembly;
  the vetoing country took the floor in all 15 veto initiative debates.

## kart-04-besi-de — 322
- **Kart metni:** 1946'dan bu yana 322 ret oyu; beş daimî üyenin hepsi veto kullandı. Kapalı
  oturumdaki 2 veto üye toplamına girmez.
- **Görsel:** Üye başına yatay çubuk, üye renkleriyle ve sayısıyla: Sovyetler Birliği 114, Rusya
  Federasyonu 43, ABD 94, Birleşik Krallık 30, Fransa 18, Çin 23.
- **Dayanak:** Veri setindeki `veto_eden_uyeler` alanı; kapalı oturumdaki 2 veto üye toplamına
  girmez (`METODOLOJI.md` 2). SSCB ve Rusya Federasyonu ayrı kodlanır; 1971 öncesi "Çin" vetosu
  Çin Cumhuriyeti'ne aittir (1 veto, 13 Aralık 1955).
- **Hesap:** Kapalı oturum dışı kayıtlarda üye başına ret oyu sayısı; çubuk uzunluğu en yüksek
  üyeye (114) göre orantılıdır.
- **Paylaşım cümlesi (TR):** 1946'dan bu yana 322 ret oyu: beş daimî üyenin hepsi veto kullandı.
- **Paylaşım cümlesi (EN):** 322 negative votes since 1946: all five permanent members have used the
  veto.

## kart-05-konular — 4 konu
- **Kart metni:** Dört konuda en çok ret oyu kullanan üyeler: Filistin – ABD 42 · Suriye – Rusya
  Federasyonu 18 · Güney Afrika – Birleşik Krallık 24 · Üyelik başvuruları – Sovyetler Birliği 51.
  Yalnızca kaydın ana konusu sayılır.
- **Görsel:** Dört kısa çubuk, üye renginde; arkasındaki açık çubuk konudaki toplam ret oyunu
  gösterir (Filistin ve Arap-İsrail meselesi 53, Suriye 28, Güney Afrika, Namibya ve Rodezya 54,
  Üyelik başvuruları 60).
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
- **Metin (EN):** "I have been saying for years that we cannot afford to place humanity's fate into
  the hands of a small group of nations. Today, in your presence, I say again: The world is bigger than
  five!" (İletişim Başkanlığı'nın İngilizce kitapçığı, s. 6).
- **Kaynak:** BM 74. Genel Kurulu konuşması, 24 Eylül 2019; Türkçe ve İngilizce kitapçık s. 6.
  `kaynaklar/alintilar.csv` 2019-1.
- **Paylaşım cümlesi (TR):** 24 Eylül 2019 Genel Kurul konuşmasından, s. 6.
- **Paylaşım cümlesi (EN):** From the address to the 74th Session of the General Assembly, 24
  September 2019, p. 6.

## kart-09-asya-pasifik — %57,8
- **Kart metni:** Asya-Pasifik Grubu'nun 54 üyesi BM üyeleri nüfusunun %57,8'ini oluşturuyor; Güvenlik
  Konseyi'nin 15 koltuğundan 3'ü (%20,0) bu grupta, bunun 1'i daimî. Nüfus 2023 tahmini (WPP 2024),
  koltuklar mevcut dönem (2026).
- **Dayanak:** `data/processed/temsil.json` (ASP): nüfus payı 2023, koltuk (1 daimî + 2 seçilmiş) / 15
  (`METODOLOJI.md` 2.9; girdiler `kaynaklar/temsil/`).
- **Hesap:** `scripts/09_temsil.py`; kart sayıları `temsil_sayilari()` ile JSON'dan okunur, test aynı
  alanları karşılaştırır.
- **Görsel:** İki yatay çubuk yan yana: nüfus payı (lehte rengi) ve koltuk payı (vurgu rengi), yüzdeyle.
- **Paylaşım cümlesi (TR):** Asya-Pasifik Grubu: BM üyeleri nüfusunun %57,8'i, Konsey koltuklarının %20'si
  (1 daimî).
- **Paylaşım cümlesi (EN):** Asia-Pacific Group: 57.8% of the population of UN Member States, 20% of
  Council seats (1 permanent).

## kart-10-afrika — 0 / 5
- **Kart metni:** Afrika Grubu'nun 54 üyesi barış gücü üniformalı personelinin %39,1'ini sağlıyor ve
  olağan bütçe ölçeğinin %1,1'ini ödüyor; Konsey'de 3 seçilmiş koltuğu (%20,0) var, daimî koltuğu yok.
  Personel 28 Şubat 2026, ölçek 2025–2027, nüfus 2023.
- **Dayanak:** `temsil.json` (AFR): personel payı (28 Şubat 2026 sıralaması, üniformalı personel: asker,
  polis, uzman, karargâh subayı), bütçe payı (2025–2027 ölçeği), koltuk 0 daimî + 3 seçilmiş.
- **Hesap:** `scripts/09_temsil.py`; büyük sayı daimî koltuk / 5.
- **Görsel:** Nüfus payı (%18,3) ve koltuk payı (%20,0) çubukları yan yana.
- **Paylaşım cümlesi (TR):** Afrika Grubu: 54 üye, barış gücü personelinin %39'u, bütçe ölçeğinin %1'i,
  daimî koltuk 0.
- **Paylaşım cümlesi (EN):** African Group: 54 members, 39% of peacekeeping personnel, 1% of the budget
  scale, 0 permanent seats.

## kart-11-p5 — 5 / 5
- **Kart metni:** Beş daimî üye BM üyeleri nüfusunun %25,6'sını oluşturuyor, olağan bütçe ölçeğinin
  %51,9'unu ödüyor ve 15 koltuğun 5'ini (%33,3) tutuyor; daimî koltukların tamamı bu beş üyede. Nüfus
  2023 tahmini (WPP 2024), ölçek 2025–2027.
- **Dayanak:** `temsil.json` (P5 kümesi): nüfus payı 2023 (193 üyenin toplamında), bütçe payı, koltuk
  5 daimî / 15.
- **Hesap:** `scripts/09_temsil.py`; test P5 nüfus payını elle yazılmış beş nüfusla doğrular
  (`tests/test_temsil.py`).
- **Görsel:** Nüfus payı (%25,6) ve koltuk payı (%33,3) çubukları yan yana.
- **Paylaşım cümlesi (TR):** Beş daimî üye: nüfusun %25,6'sı, bütçe ölçeğinin %52'si, koltukların %33'ü,
  daimî koltukların tamamı.
- **Paylaşım cümlesi (EN):** Five permanent members: 25.6% of the population, 52% of the budget scale, 33%
  of the seats, all permanent seats.
