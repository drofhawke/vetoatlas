# Metodoloji

Sitedeki her sayı bu sayfadaki kurallara dayanmaktadır. Bir kuralın değişmesi hâlinde değişiklik,
tarihiyle birlikte bu sayfaya işlenir.

## 1. Kategoriler

Veri setinde yalnızca resmî vetolar vardır.

Resmî veto, bir daimî üyenin aksi hâlde gerekli oyu almış bir karar taslağına ret oyu
vermesidir. Ana kaynak Dag Hammarskjöld Kütüphanesi veto listesidir (1946–2004 dönemi
BM belgesi A/58/47, Ek III’e dayanır).

Veto tehdidi nedeniyle oylamaya sunulmayan ya da yumuşatılan taslaklar henüz eklenmemiştir.
Eklenmeleri hâlinde ayrı tutulur ve veto sayısına katılmaz.

Konseyin 1994’te Ruanda’da olduğu gibi bir kriz karşısında karar almadığı durumlar da veto sayılmaz.

## 2. Sayım kuralları

“Veto sayısı” iki biçimde hesaplanır ve her yerde ikisi birlikte verilir.
Taslak bazında sayım, veto nedeniyle kabul edilemeyen karar taslaklarının sayısıdır. Oy bazında
sayım, kullanılan ret oylarının sayısıdır; bir taslağı iki üye veto ettiyse 2
sayılır. Genel Sekreter seçimi için kapalı oturumda kullanılan 2 veto öneri sayısına girer, ret oyu
sayısına girmez; bu nedenle ret oyu toplamı 324 değil 322’dir. Konsey büyüklüğü: 1963 Şart değişikliğinin yürürlüğe girdiği 31 Ağustos 1965’e kadar
on bir üye ve yedi olumlu oy kuralı; sonrasında on beş üye ve dokuz oy. 31 Ağustos 1965 ile
1965 sonu arasında veto kullanılmadığı için veri seti 1966 öncesi kayıtları on bir üyeli Konseye
sayar (“on dörde karşı bir” galerisinde “ona karşı bir”, simülasyon sayfasında eşik 7). “On dörde karşı bir” sayımı,
lehte oy sayısı Konseyin üye sayısından bir eksik olan önerileri alır; bir üyenin oylamaya katılmadığı
3 kayıt (30 Kasım 1950, 26 Temmuz 1973, 23 Haziran 1976) bu sayıya girmez. Kaynakta yıldızla işaretli, paragraf veya değişiklik önergesine yönelik
vetolar ayrıca işaretlenir.

SSCB vetoları Rusya Federasyonu’nun halefi olduğu koltuğa aittir ancak ayrı
kodlanır. 25 Ekim 1971 öncesi “Çin” vetoları Çin Cumhuriyeti’ne (Tayvan) aittir ve
Çin Halk Cumhuriyeti’ne yazılmaz.

### 2.1. Taslak kaynağı, kısmi ve ön soru vetoları

1946–1953 arasındaki vetoların bir kısmında karar taslağı ayrı bir S/ belgesi olarak
yayımlanmamıştır; öneri doğrudan toplantıda sunulmuş ve toplantı kaydında yer
almıştır. Bu kayıtlar eksik veri sayılmaz, `taslak_kaynagi: toplanti_kaydi`
olarak işaretlenir.

Kaynakta yıldız işareti iki farklı anlamda kullanılır. Çoğunlukla paragraf veya
değişiklik önergesine yönelik kısmi vetoyu gösterir. Kapalı oturumlarda (ör. Genel
Sekreter seçimi) ise veto eden üyenin resmî bildiride yer almadığını, kaynak
tarafından atfedildiğini gösterir. Bu ikisi ayrı alanlarda tutulur.

Kısmi veto, taslağın bütünü yerine bir değişiklik önergesine ya da taslağın bir bölümüne
(paragraf, cümle, kelime) yapılan ayrı oylamada kullanılan ret oyudur. Kaynaktaki yıldız,
“oral amendment” kaydı ve `duzeltmeler.csv` “kismi” sütunu bu işareti koyar. Açık veride işaret
`kismi_veto_suphesi` sütunundadır; `True` kısmi vetoyu gösterir. 31 kısmi vetonun 16’sı 13 Aralık
1955’teki üyelik oylamasından gelmektedir. Bunların 14’ünde Konsey, Brezilya ve Yeni Zelanda’nın S/3502
taslağının ikinci giriş paragrafındaki ülke adlarını tek tek oylamıştır; 13 kelime SSCB’nin,
“Mongolian People’s Republic” ise Çin Cumhuriyeti’nin ret oyuyla kabul edilememiştir (S/PV.704, par. 54 ve 57–72).
Tanım, bir taslağın ayrı ayrı oylanan kelime ve paragraflarını da kapsar; bu, A/58/47 Annex III’ün
II. kısmının (“Paragraphs of draft resolutions or amendments thereto not adopted owing to the
negative vote of a permanent member”) kapsamıyla uyumludur: o kısım da bu oylamaları
“Preambular para. 2 (the word ...)” olarak verir. 13 Aralık 1955’teki 16 kaydın hepsi (14 kelime
oylaması ve Çin’in S/3506 değişiklik önergesinin iki parçası) kısmi vetodur; kelime oylamalarının
taslak bağlantısı S/3502, önerge oylamalarınınki S/3502 ve S/3506’dır.

“Ön soru” vetoları, bir konunun usul meselesi sayılıp sayılmayacağına dair
oylamada kullanılan vetolardır (çifte veto). Usul kararlarında veto
bulunmadığından, daimî üyenin önce bu ön soruyu veto etmesi esas meseleyi de
vetoya açar. Bu kayıtlar ayrıca işaretlenir.

Aynı gün, aynı gündem maddesinde ve aynı içerikle birden fazla görünen satırlar
kaynak tarafından ayrı vetolar olarak listelenmiştir. Silinmez, toplantı kaydından
doğrulanarak ayrıştırılır.

### 2.2. Kaynak mutabakatı

Ana veri kaynağı DHL veto listesidir; belge numaraları ve bağlantılar oradan gelir.
Sayımın doğruluğu, Konsey prosedürü üzerine standart başvuru eseri olan Sievers ve
Daws’ın *The Procedure of the UN Security Council* çalışmasının veto tablosuyla
(scprocedure.org, Tablo 4) satır satır karşılaştırılarak sağlanır.

İki kaynak arasındaki her fark `kaynaklar/duzeltmeler.csv` dosyasında gerekçesiyle
kayıtlıdır ve kodun içine hiçbir düzeltme gömülü değildir. Eklenen ya da değiştirilen
her kayıt `duzeltme` alanında hangi referans satırına dayandığını taşır.

Mutabakat sonucunda DHL listesinde eksik olan 18 öneri tespit edilmiştir: 13 Aralık
1955’teki 16 veto (SSCB’nin 15 üyelik ve değişiklik vetosu ile Çin Cumhuriyeti’nin
Moğolistan vetosu), 10 Eylül 1972’deki Çin-SSCB ortak değişiklik vetosu ve 24 Şubat
2025’te tek satırda birleştirilmiş iki ayrı Rus vetosu. Ayrıca 26 Haziran 1946’da
Fransa’nın SSCB ile birlikte kullandığı bir ret oyu DHL’de yer almamaktadır.

13 Aralık 1955 ve 10 Eylül 1972 vetoları toplantı kayıtlarından (S/PV.704 ve
S/PV.1662) doğrulanmıştır. Oy dağılımları ve veto eden üyeler referans
tabloyla aynıdır. Referans tablonun aynı gün içindeki sırası toplantıdakinden farklıdır:
Moğolistan vetosu toplantıdaki 16 vetonun 3.’südür (tabloda #76, günün son satırı); 1972’deki
değişiklik vetosu aynı toplantıdaki ABD vetosundan önce oylanmıştır (tabloda #118 ABD, #119
değişiklik). Tablo gün içi sırayı hangi kurala göre verdiğini belirtmediği için bu bir hata
sayılmaz. Kayıt kimlikleri 2.3’teki Kural 2 gereği değiştirilmez; toplantıdaki sıra notlarda yazılıdır.

DHL listesi 1946–2004 verisini A/58/47 Annex III’ten aldığını belirtmektedir. Bu 17 veto o ekin Part II
bölümünde (paragraf ve değişiklik önergesi vetoları) vardır ve liste aynı bölümdeki başka
satırları içerir; dolayısıyla yokluk bir kapsam farkı değil, eksikliktir ve hata bildirimine
alınmıştır (`kaynaklar/KAYNAKLAR.md`, “DHL listesinin kapsamı”).

İki kaynağın tarihleri yedi vetoda farklıdır. Bu farklar silinmez. Oylama günü toplantı
kaydından belirlenir ve doğru tarihi hangi kaynak veriyorsa kayıtta o kullanılır; diğer
kaynağın tarihi notlarda kalır. Referans kaynağın kendi iç tutarsızlıkları
(`kaynaklar/KAYNAKLAR.md`) da aynı şekilde belgelenir.

Genel oy dağılımı (lehte-aleyhte-çekimser) referans tablodan alınır. Aynı gün aynı
gündemde birden fazla veto olduğunda eşleştirme ülke adı, gündem ya da kaynaktaki
dipnotla yapılır ve gerekçesi kayda yazılır. Bu yollarla eşleştirilemeyenler toplantı
kaydından elle eşleştirilene kadar boş bırakılır; tahmin edilmez.

Referans tablonun kapsamı 18 Eylül 2025’teki vetoda biter. Bu tarihten sonraki vetolar
BM birincil kaynaklarından eklenir ve doğrulanır: karar taslağı (S/…), toplantı kaydı
(S/PV.…) ve BM basın bülteni. Veto eden üyeler, oy dağılımı ve gündem maddesi toplantı
kaydındaki oylama bölümünden alınır. DHL listesinde yer alıp oy dağılımı bulunmayan
vetolara (7 Nisan 2026, S/2026/273) oy bu yolla eklenir. Kanonik DHL dosyasında
bulunmayan vetolar (17 Eylül 2026, S/2026/740) da aynı kaynaklarla kayda girer. Bu satırlar
`duzeltmeler.csv` dosyasında `kaynak_url`, `oy` ve `taslak` sütunlarıyla, gerekçede
toplantı kaydının sayfa numarasıyla birlikte tutulur. Mutabakatta referans toplamlarına
“kapsam sonrası” olarak eklenirler. Doğrulanamayan bir ayrıntı (ör. açılamayan bir basın
bülteni) gerekçeye açıkça yazılır.

İki kaynağın ayrıştığı ya da tek başına yetmediği
kayıtlar ilgili toplantı kaydının (S/PV) kendisinden doğrulanır. Kayıtlar undocs.org
üzerinden BM belge sisteminin PDF’leri olarak açılır. Eski yıllarda Resmî Kayıtlar sürümü
(S/PV.NNNN(OR)) kullanılır; metin katmanı olmayan taranmış sayfalar görüntüden okunur.
Oy dağılımı, kayıttaki lehte, aleyhte ve çekimser ülke listelerinden sayılır. Oylama günü,
toplantının açılış ve kapanış saatlerinden, verilen aralardan ve konuşmalardaki zaman
ifadelerinden (“dün sabah”, “yarın, 7 Eylül”) çıkarılır. Toplantı gece yarısını geçmişse
oylamanın hangi gün yapıldığı bu işaretlerle ayrılır ve not edilir. Kayıt kimliği
(V-<DHL tarihi>-n) tarih düzeltilse de değişmez. DHL’de birbirinin aynısı olan satırlar,
toplantıdaki oylama sırasına göre bağlanır. Her sonuç `duzeltmeler.csv` dosyasında toplantı
kaydı ve PDF sayfa numarasıyla (`oy_esle`, `tarih_dogrula`) tutulur. Referans tabloyla
çelişen değerlerde toplantı kaydı esas alınır ve çelişki kayda yazılır. Kayda
ulaşılamazsa ya da kayıt kesin sonuç vermiyorsa tahmin yapılmaz: kayıt nedeniyle birlikte
“doğrulanamadı” olarak bırakılır ve arayüzde “Doğrulanıyor” etiketi kalır. CAPTCHA ya da
bot doğrulaması gibi erişim engelleri aşılmaz.

Toplantı kaydında paragraf numarası varsa birincil atıf paragraf numarasıdır;
PDF sayfası yanında parantez içinde kalır (“S/PV.704, par. 54 (PDF s. 13)”). Paragraf numarası
olmayan kayıtlarda PDF sayfası kullanılır; basılı sayfa PDF sayfasından farklıysa fark yazılır.
Kayıt notlarındaki sayfa numaraları PDF sayfasıdır. S/PV.704 ve S/PV.1662’de basılı sayfa PDF sayfasından
2 eksiktir.
Belge sisteminde bulunmayan ya da otomatik erişimi engellenen belgelerin künyesi, indirme adresi ve
SHA-256 özeti `kaynaklar/KAYNAKLAR.md` dosyasındadır (“Yerel belgeler”); belgelerin kendisi depoya girmez.

Yapay zekâ çıktısı kaynak sayılmaz. Bir dil modelinin ürettiği özet, çeviri,
transkript ya da liste, kaynağın kendisi yerine kullanılmaz ve depoya kaynak olarak konmaz. Her
bilgi belgenin kendisinden (toplantı kaydı, karar taslağı, resmî liste) alınır ve o belgeye
atıfla yazılır.

Belge bağlantıları arayüzde ve açık veride belge kodlarından kurulur
(`https://undocs.org/<kod>`); DHL sayfasındaki bağlantılar kullanılmaz, çünkü beşi bozuktur
(`kaynaklar/hata_bildirimi.md`, DHL iletisi). Ham bağlantılar `data/processed/` altında kaynaktaki
hâliyle durur. Belge kodlarının ve bağlantıların biçimi `tests/test_belge_kodlari.py` ile denetlenir;
bağlantılara istek atılmaz.

### 2.3. Tarih ve kimlik kuralları

Kural 1. Vetonun tarihi, oylamanın fiilen yapıldığı takvim günüdür. Gece yarısını
geçen toplantılarda bu gün, toplantı kaydının başlığındaki tarihten (toplantının başladığı
günden) farklı olabilir. Örnekler: 3/4 Aralık 1960, 20/21 Şubat 1961, 22/23 Ağustos 1968.
İki tarih de kayıtta tutulur. Oylama günü `tarih` alanındadır. Kaynağın verdiği tarih
`tarih_ham` alanında, referans tablonunki `referans_tarih` alanında durur. Toplantı
kaydının başlık tarihi ve oylama gününün nasıl belirlendiği notlarda ve
`toplanti_dogrulamasi` alanında, sayfa numarasıyla yazılıdır.

Kural 2. Kayıt kimlikleri sabit anahtarlardır ve tarih bilgisi taşımaz. Kimlik
(`V-YYYY-AA-GG-n`) kayıt ilk oluşturulduğunda DHL tarihinden ve günün sırasından üretilir.
İçindeki tarih parçası yalnızca bu ilk anı gösterir; tarih olarak okunmaz, tarih yalnızca
`tarih` alanından alınır. Bir kaydın tarihi sonradan düzeltilirse kimliği değişmez.
Örneğin V-1950-09-05-1 kaydının tarihi 6 Eylül 1950’dir. Düzeltme dosyaları, konu düzeltmeleri ve
dış bağlantılar kimliğe dayandığı için kimliği değiştirmek bu bağları koparırdı.

### 2.4. Konu sınıflandırması ve Türkçe başlıklar

Her veto 15 konudan tam olarak birine ana konu olarak atanır: Filistin ve Arap-İsrail
meselesi; Lübnan; Suriye; Diğer Ortadoğu ve Kuzey Afrika; Kıbrıs; Ukrayna; Diğer Avrupa;
Güney Afrika, Namibya ve Rodezya; Diğer Afrika; Latin Amerika ve Karayipler; Asya;
Silahsızlanma ve askerî gerilimler; Üyelik başvuruları; Genel Sekreter seçimi; Tematik konular.

Atama iki katmanlıdır. `kaynaklar/gundem_sozlugu.csv`, veri setindeki 136 benzersiz gündem
başlığının her biri için sadık bir Türkçe çeviri, konu ve bölge verir. Çeviriye yorum
katılmaz; tarih, gönderen ve belge numarası olduğu gibi aktarılır. Başlık tek başına yetmediğinde
konu kayıt bazında `kaynaklar/konu_duzeltmeleri.csv` dosyasından gelir. Örneğin genel
“The situation in the Middle East” başlığı altındaki vetolar Lübnan, Suriye ya da Filistin
olabilir. Bu dosyadaki her satırın gerekçesi, scprocedure Tablo 4’te o vetoya verilen konudur.
Tablonun kapsamı dışındaki vetolarda gerekçe, taslağın konusu ve toplantı kaydıdır.

Bir veto birden fazla konuya değiyorsa ana konu dışındakiler `ikincil_konular` alanına yazılır.
Örnekler: 2024 Filistin üyelik vetosu ve 1956 Süveyş vetoları için Filistin, 1958 Lübnan-Ürdün
şikâyeti için Diğer Ortadoğu. İkincil konu kaydı filtrelemede o konuya da bağlar, ama hiçbir
sayıma girmez. Konu toplamları yalnızca ana konuyu sayar ve her zaman 266 öneriye tamamlanır.
Arayüzde ikincil bağlar ayrı bir notla gösterilir.

Sözlükte bulunmayan yeni bir başlık geldiğinde veri hattı uyarı verir ve kaydın konusunu
“Sınıflandırılmadı” yapar; tahminle konu atanmaz. Sözlük satırı eklenene kadar kayıt bu
etiketle görünür.

### 2.5. Genel Kurul tartışmaları (A/RES/76/262)

26 Nisan 2022’de kabul edilen A/RES/76/262 uyarınca Genel Kurul Başkanı, her vetodan sonraki
10 iş günü içinde bir tartışma toplar. Genel Kurul aynı konuda olağanüstü özel oturumda
toplanıyorsa ayrı bir tartışma yapılmaz. Güvenlik Konseyi ise her veto için bir özel rapor
sunar. Bu tarihten önceki vetolar bu bölümün kapsamı dışındadır; arayüzde Genel Kurul bölümü
gösterilmez.

A/RES/76/262, Genel Kurulun 26 Nisan 2022’deki 69. genel kurul toplantısında oylama yapılmadan
kabul edilmiştir (A/76/PV.69, s. 8). Karara göre veto kullanan daimî üye ya da üyelere konuşmacı
listesinde öncelik tanınır; Güvenlik Konseyi tartışmadan en az 72 saat önce Genel Kurula özel
rapor sunmaya davet edilir; Genel Kurulun gündemine “Use of the veto” (vetonun kullanılması)
maddesi eklenmiştir (par. 1–4). Taslağın 57 sunucusu bulunmakta olup kabul toplantısında 27 delegasyon daha
sunucu olmuştur; Timor-Leste iki listede de yer aldığından toplam sunucu sayısı 83’tür (A/76/L.52;
A/76/PV.69, s. 7–8). Daimî üyelerden ABD ilk sunucular arasında, Fransa ve Birleşik Krallık sonradan
sunucu olanlar arasındadır; Çin ve Rusya Federasyonu iki listede de yer almaz. Türkiye ilk sunucular
arasındadır (belgede “Turkey”) ve temsilcisi kabulden sonraki açıklamasında Türkiye’nin iki yıl önceki
başlangıcından bu yana girişimin çekirdek grubunda yer aldığını ifade etmiştir (A/76/PV.69, s. 20). Sayfa
numaraları belgelerin PDF sayfalarıdır.

Tartışmalar `kaynaklar/genel_kurul_tartismalari.csv` dosyasında, vetolardan ayrı tutulur. Bir
tartışma birden çok vetoyu, bir veto da birden çok tartışmayı kapsayabilir. Konseyin özel
raporları `kaynaklar/ozel_raporlar.csv` dosyasındadır. İki tür tartışma vardır:
`veto_girisimi` (“Use of the veto” gündem maddesi altındaki tartışma) ve
`olaganustu_ozel_oturum` (ES-10, ES-11). Olağanüstü özel oturumlarda konuşmacı sayısı
tutulmaz; yalnızca toplantı kayıtları ve kabul edilen kararlar yazılır.

Her toplantı kaydı için üç değerden biri kullanılır. `resmi`: BM belge
sisteminde yayımlanmış tutanak (A/…/PV.…). `gayriresmi_transkript`: tutanak yayımlanmamış ama
BM’nin otomatik konuşma tanıma transkripti (transcripts.un.org) var. `yayimlanmadi`: ikisi de
yok. Gayriresmî transkriptten alınan her bilgi `gayriresmi_alanlar` sütununda ayrıca
işaretlenir. Bekleyen kayıtlar `scripts/05_bekleyen_kayitlar.py` ile denetlenir; yayımlanan
kayıt elle işlenir ve gerekiyorsa sayım tutanaktan yeniden yapılır.

Her tartışmanın tarihi ve gündemi bir resmî kaynaktan doğrulanır: tutanak ya da
BM Günlüğü (journal.un.org). Günlük, toplantının ilgili vetoyla bağlantılı gündemi
görüştüğünü gösteriyorsa (gündem maddesi, özel rapor ya da oturumu yeniden toplayan mektup)
kayıt `dogrulandi` olur ve dayanak `dogrulama_kaynagi` sütununa yazılır.

Konuşmacılar yalnızca veto girişimi tartışmalarında şöyle sayılır:
- Yalnızca veto gündem maddesinin konuşmaları sayılır. Aynı toplantıda görüşülen başka
  maddeler ve tartışmanın devam toplantıları, tutanaktaki gündem maddesi başlıklarına göre
  ayrılır.
- Her delegasyon bir kez sayılır. Başkan ve Sekretarya sayılmaz.
- Grup adına konuşan delegasyon tek konuşmacı sayılır. Grup adına konuştuğu
  `grup_adina_konusanlar` sütununda, grubun adıyla işaretlenir. Grup işareti iki kaynaktan
  gelir: BM Günlüğü’nün “on behalf of” notu ve konuşmacının tutanaktaki kendi beyanı (“… adına
  konuşuyorum”). Başka bir delegasyonun grup konuşmasına katılmak ya da onu desteklemek,
  kendi ülkesi adına konuşmak ve “bütün üye devletler adına” gibi genel ifadeler grup sayılmaz.
- Gözlemciler (Avrupa Birliği, Filistin Devleti, Malta Egemen Tarikatı vb.) üye devletlerden
  ayrı sütunda sayılır.
- Cevap hakkı kullanımları açıklamalardan ayrı tutulur.
- `veto_eden_konustu`, veto eden her ülke için ayrı tutulur; çifte vetolarda iki ülke de
  yazılır. Değerler: `aciklama`, `yalnizca_cevap_hakki`, `hayir`.
- Kaynak: tutanağı yayımlanmış tartışmalarda sayım tutanaktan yapılır, BM Günlüğü özetiyle
  karşılaştırılır. Tutanağı yayımlanmamış tartışmalarda sayım BM Günlüğü özetinden yapılır;
  `konusmaci_kaynagi` bunu gösterir. Başkanlık ofisinin yayımladığı tartışma özetleri çapraz
  kontrol için kullanılır. Tutmayan her sayı `capraz_kontrol` sütununa yazılır.
- Kontrol ölçütü: 6 Mart 2025 tartışmasında (A/79/PV.60) açıklama yapan 35 delegasyon (34
  üye devlet ve Avrupa Birliği). Bu sayı Başkanlık özetiyle aynıdır.

### 2.6. İngilizce sürüm ve çeviriler

Notlar, düzeltme açıklamaları ve konu gerekçeleri Türkçe yazılır; asıl metin Türkçedir.
Her birinin İngilizce karşılığı yanında tutulur: `kaynaklar/duzeltmeler.csv` dosyasında
`aciklama_en`, `kaynaklar/konu_duzeltmeleri.csv` dosyasında `gerekce_en`, ayrıştırıcının
ürettiği sabit notlar için `kaynaklar/notlar_en.csv`. Konu adlarının karşılıkları
`kaynaklar/konular_en.csv` dosyasındadır. Çeviriler sadıktır: belge kodları, sayfa ve paragraf
numaraları, tarihlerdeki sayılar ve özel adlar değiştirilmez. Özgün İngilizce metni doğrulanmamış
bir ifade Türkçede tırnak içinde verildiyse, İngilizcede uydurma bir alıntı yaratmamak için
tırnaksız aktarılır. Bir notun İngilizcesi eksikse `04_web_verisi.py` uyarı verir ve arayüzün
İngilizce sürümü o notun Türkçe asıl metnini gösterir. İngilizce sürümde gündem başlıkları
BM’deki özgün hâliyle verilir; Türkçe sürümde çevirinin altında özgün başlık da görünür. Bu belgenin İngilizcesi `METODOLOJI_EN.md` dosyasındadır;
`web/metodoloji.html` sayfası `04_web_verisi.py` her çalıştığında ikisinden üretilir.

### 2.7. Alıntı bankası ve Söz ve Kayıt sayfası

`kaynaklar/alintilar.csv`, Cumhurbaşkanı Recep Tayyip Erdoğan’ın 2019 ve 2022–2026 BM Genel Kurulu
hitaplarından ve “Daha Adil Bir Dünya Mümkün” kitabından alıntıları tutar. Kaynaklar depoda değildir;
künyeleri ve SHA-256 değerleri `kaynaklar/KAYNAKLAR.md` dosyasındadır. Alıntılar PDF metin
katmanından kesilir ve her biri, boşluklar normalize edilerek, belirtilen sayfada kelimesi
kelimesine aranır. Hitaplarda basılı sayfa ve PDF sayfası birlikte tutulur. Kitap alıntılarında iki dilde de
sayfa numarası yazılmaz, atıf bölüm başlığıyla yapılır. Kitabın Türkçe PDF’inde zaten basılı sayfa
numarası yoktur. Doğrulanamayan alıntıda `04_web_verisi.py` durur. Bir alıntı atlama işaretiyle (…) kısaltıldığında,
işaretin ayırdığı her parça kaynakta ayrı ayrı ve kelimesi kelimesine aranır; parçalar kaynaktaki sırasıyla ve
aynı pasajdan gelmelidir. Alıntı bankasında tam metin kalır; kısaltılmış biçim yalnızca hikâyede kullanılır
(giriş alıntısı ve 7. adım). Hikâyenin giriş alıntısı 2019 hitabındandır: Türkçede Türkçe kitapçıktaki
“Dünya 5’ten Büyüktür.”, İngilizcede İngilizce kitapçıktaki “The world is bigger than five!” cümlesi.

İngilizce sayfalarda alıntının resmî İngilizce metni kullanılır. Resmî İngilizce metin
Türkçe metinle aynı kurala bağlıdır: kendi kaynağında, belirtilen sayfada kelimesi kelimesine aranır,
doğrulanamazsa `04_web_verisi.py` durur ve testler (`tests/test_alintilar.py`) kaynağı yerelde olan her
İngilizce metni kaynağına karşı denetler. Kaynaklar şunlardır:
- 2022–2026 hitapları: derlemenin İngilizce bölümü.
- 2019 hitabı: İletişim Başkanlığının İngilizce kitapçığı. Kitapçık konuşmanın hazırlanmış metnidir. Kürsüde
  eklenen ve kitapçıkta bulunmayan pasajın (2019-2) İngilizcesi BM’nin İngilizce toplantı kaydından
  (A/74/PV.3) alınır. Konuşma Türkçe yapılmış olup kayıttaki İngilizce, delegasyonun verdiği tercümedir.
- Kitap: İngilizce baskı *A Fairer World is Possible* (Turkuvaz Kitap, 2021), İngilizce bölüm başlığıyla. İngilizce baskının PDF’i bir taramadır ve metin katmanı OCR’dır. Bu yüzden
  alıntıların geçtiği sayfalar sayfa görüntüsüyle karşılaştırılmıştır. OCR’ın görüntüden farklı okuduğu tek yer
  (s. 32’de kısa tire) görüntüdeki gibi düzeltilerek aranır (`kaynaklar/KAYNAKLAR.md`).

Resmî İngilizcesi bulunamayan alıntıda İngilizce sayfada Türkçe özgün metin kalır ve altına “Unofficial
translation by Veto Atlas” etiketli bir çeviri eklenir. Bu çeviri bir kaynağa karşı doğrulanmaz. Bugün bütün
alıntıların resmî İngilizcesi bulunmaktadır.

Söz ve Kayıt sayfası (`web/vizyon.html`) her alıntının yanına veri setinden hesaplanan bir karşılık koymaktadır. Sayılar sayfa
açılırken hesaplanır; alıntı ile sayı arasında neden-sonuç ilişkisi kurulmaz. “Ekim 2023 sonrası
Gazze ile ilgili vetolar”, oylama günü 7 Ekim 2023 ya da sonrası olan ve taslak metninde “Gaza”
sözcüğü geçen vetolardır (`kaynaklar/gazze_taslaklari.md`).
Bu listedeki 22 Aralık 2023 vetosu taslağın kendisine değil, ona verilen sözlü değişiklik önergesine
yöneliktir; `veto_hedefi` sütunu bunu gösterir ve veri betiği `04_web_verisi.py` bu işareti kayıttaki “oral amendment” notuyla
karşılaştırır. “Kitaptaki model” bölümünde alıntılar kısa tutulur; her unsurun geri kalanı özetlenir.

Bölge dağılımı, gündem sözlüğündeki bölge alanını kullanır: Ortadoğu ve Kuzey Afrika, Avrupa,
Afrika, Asya ve Pasifik, Latin Amerika ve Karayipler ve Küresel. “Küresel”, belirli bir bölgeye
bağlanmayan gündemlerdir (genel üyelik başvuruları, silahsızlanma, Genel Sekreter’in atanması,
tematik konular). Bölge gündem başlığına göre atanır; konu sınıflandırmasından bağımsızdır.
Veto girişimi tartışmalarındaki delegasyon sayıları 2.5’teki sayım kurallarıyla yapılmış sayılardır
(üye devletler ve gözlemciler birlikte; cevap hakkı hariç).

### 2.8. Reform modelleri

Reform modelleri sayfası (`web/reform.html`), Güvenlik Konseyi reformu için dört modeli aynı altı ölçütle
yan yana sunmaktadır: modeli kimin sunduğu, toplam üye sayısı, yeni daimî üye, vetonun kimde olduğu, karar için gereken
oy ve Genel Kurul ile ilişki. Modeller
Ezulwini Uzlaşısı (Ext/EX.CL/2 (VII); A/59/L.67), G4 (A/59/L.64), Uzlaşı için Birlik (A/59/L.68) ve
“Daha Adil Bir Dünya Mümkün” kitabıdır; belgelerin tarih sırasıyla verilir. Karşılaştırma birincil
belgelerden aktarılır (`kaynaklar/reform_modelleri.csv`): her hücre belgenin kendi hükmünü özetler ve
altında dayanak paragrafı yazılır. Kitaptan tırnak içinde verilen her ifade, alıntı bankasındaki
doğrulanmış bir alıntıda birebir geçer. Bunu otomatik bir test denetler. Kitap alıntıları iki dilde de bölüm
başlığıyla künyelenir; tablodaki dayanak da bölüm başlığıdır. Sayfa modeller hakkında değerlendirme cümlesi kurmaz.

### 2.9. Temsil endeksi

`web/temsil.html`, BM bölgesel grupları için beş payı yan yana göstermektedir; hesap `scripts/09_temsil.py`,
girdiler `kaynaklar/temsil/*.csv`, çıktı `data/processed/temsil.json`. Veto veri setine hiçbir şey
eklenmez; bileşik puan ya da sıralama yoktur.

- Birim BM bölgesel gruplarıdır (DGACM listesi, 10 Ekim 2026). Türkiye iki grupta listelenir ve
  seçimlerde yalnızca WEOG sayılır; ABD hiçbir grubun üyesi değildir ve seçimlerde WEOG sayılır. Her ikisi
  WEOG’da sayılır ve notlanır. Coğrafi bölgeler (M49) kullanılmaz; koltuk dağılımı seçim birimine dayanır.
- Nüfus verisi WPP 2024’ün 1 Ocak tahminidir, bin kişi; yıllar 2023 (son tahmin yılı) ve 1963 (A/RES/1991 (XVIII)
  yılı). 1945 için WPP serisi yoktur; hesaplanmaz. 2023 payı 193 üyenin toplamı içindedir (BM üyesi
  olmayan ülke ve alanlar, ör. Filistin, Tayvan, Kosova, Batı Sahra ve Porto Riko, paydaya girmez). Kıbrıs: WPP’nin
  verisi adanın tamamını kapsar (“Refers to the whole country”); Kuzey Kıbrıs Türk Cumhuriyeti’nin nüfusu (KKTC İstatistik
  Kurumu, Nüfus Projeksiyonları 2019–2023, 11 Kasım 2024; 2022 yıl sonu projeksiyonu 462.747, WPP’nin 1 Ocak 2023 tahminiyle
  aynı an) çıkarılır, KKTC BM üyesi olmadığı için paydaya girmez. Bu, verideki tek BM dışı nüfus kaynağıdır; değerler
  `kaynaklar/temsil/kktc_nufus.csv` dosyasındadır. 1963 değerleri değişmez. 1963 payı, 1963 sonundaki 113 üyenin o tarihteki ülkeleriyle
  hesaplanır: dağılan devletler ardıl ülkelerin serileri toplanarak (SSCB 13 cumhuriyet, Ukrayna ve Beyaz
  Rusya ayrı üye; Yugoslavya 7 seri; Çekoslovakya 2), 1963’te büyük olan devletler o tarihteki sınırlarıyla
  (Pakistan + Bangladeş, Malezya + Singapur, Etiyopya + Eritre, Sudan + Güney Sudan); Çin koltuğu Çin
  Cumhuriyeti’ndeyken nüfus “China” + “China, Taiwan Province of China” toplamıdır. Her ardıl kuralı
  JSON’da notlanır; hiçbir seri iki kez sayılmaz. Bunu otomatik bir test denetler.
- Üye payı grup üye sayısı / 193. Bütçe payı 2025–2027 olağan bütçe ölçeği yüzdelerinin toplamı
  / 100 (A/RES/79/249; Katkılar Komitesi Excel’i). Personel payı barış gücü üniformalı personel
  (asker, polis, uzman, karargâh subayı), 31 Temmuz 2026 ülke toplamları / genel toplam.
- Daimî koltuk payı = daimî / 5; toplam koltuk payı = (daimî + seçilmiş) / 15, mevcut dönem
  (BM Konsey üyeleri sayfası, 2026). Seçilmiş koltuk dağılımı A/RES/1991 (XVIII) A par. 3 (Afrika ve
  Asya 5, Doğu Avrupa 1, Latin Amerika 2, Batı Avrupa ve diğerleri 2); Afrika 3 / Asya-Pasifik 2 ayrımı
  mevcut uygulamadır. Her gösterge için koltuk/gösterge oranı = toplam koltuk payı / gösterge payı; oran 1 ise
  grubun koltuk payı gösterge payına eşittir, 1’den büyükse koltuk payı daha yüksek, küçükse daha düşüktür.
- Kümeler beş daimî üye ve İİT üyeleridir (57 üyeden Filistin BM üyesi değildir; 56 üye). İİT 1969’da
  kurulduğundan 1963 değeri bugünkü üyelerden o tarihte BM üyesi olanların 1963 sınırlarıyla toplamıdır.
- Kaynaklar: nüfus: United Nations, Department of Economic and Social Affairs, Population Division (2024),
  World Population Prospects 2024, Online Edition, `WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx`, lisans
  CC BY 3.0 IGO; üye devletler ve kabul tarihleri: un.org/en/about-us/member-states; bölgesel gruplar: DGACM,
  Regional groups of Member States, un.org/dgacm/en/content/regional-groups; bütçe ölçeği: Committee on
  Contributions, `Scale of Assessments for RB 1946-2027.xlsx` (A/RES/79/249, 24 Aralık 2024); barış gücü: UN Peace
  and Security Data Hub, Latest Uniformed Personnel Contribution By Country (DPO-UCLATEST), 31 Temmuz 2026,
  psdata.un.org (peacekeeping.un.org’daki aylık sıralama PDF’i 28 Şubat 2026’dan sonra güncellenmemiştir; veri
  merkezinin 28 Şubat 2026 değerleri o PDF’le ülke ülke aynıdır); İİT üyeleri: oic-oci.org/en/members (57 üye); Konsey üyeleri: UN
  Security Council, Current Members, main.un.org/securitycouncil/en/content/current-members; seçilmiş koltuk
  dağılımı: A/RES/1991 (XVIII), 17 Aralık 1963. Barış gücü verisine erişim 21 Ekim 2026, ötekilere 10 Ekim 2026; künyeler ve SHA-256 değerleri
  `kaynaklar/KAYNAKLAR.md` dosyasındadır.
- Sayfanın başındaki harita, seçilen bölgesel grubun üyelerini ve Güvenlik Konseyindeki koltuklarını
  (2026) gösterir; aynı bilgi haritanın altındaki ülke listesindedir. Sınırlar Natural Earth 1:50m 5.1.2’den (kamu
  malı), Equal Earth izdüşümüyle; hesap `scripts/13_harita.py`. 193 üyenin her biri kendi ülkesiyle eşlenir; BM üyesi
  olmayan ülke ve alanlar (Batı Sahra, Kuzey Kıbrıs Türk Cumhuriyeti, Tayvan, Kosova, Filistin ve bağımlı topraklar)
  boş çizilir.
  Natural Earth’ün varsayılan çizimi fiilî durumdur; tartışmalı alanlar `kaynaklar/temsil/harita_kurallari.csv`’deki
  kurallarla çizilir: Kırım Ukrayna’nın (A/RES/68/262), Golan Suriye’nin (S/RES/497 (1981)) parçası olarak; Batı
  Sahra’nın tamamı BM üyesi olmayan alan olarak (BM’nin kendi kendini yönetmeyen topraklar listesi); Somaliland
  Somali’nin parçası olarak; Natural Earth’te ayrı alan olan Åland Finlandiya’nın; BM’nin ülke ve alan listesinde (M49)
  ayrı alan olmayan Ashmore ve Cartier Adaları ile WPP 2024’te Avustralya’nın verisine dâhil Christmas, Cocos (Keeling) ve
  Norfolk adaları Avustralya’nın parçası olarak. Haritadaki nüfuslar BM istatistiklerindeki ayrı sayımları izler (WPP 2024
  notları): Çin’in verisi Hong Kong ve Makao’yu, Fransa’nınki Fransız Guyanası, Guadeloupe, Martinique, Mayotte ve
  Réunion’u, Hollanda’nınki Bonaire, Sint Eustatius ve Saba’yı kapsamaz. Bu bölgeler üyenin renginde ama kendi adı ve
  nüfusuyla gösterilir, nüfusları üyeye eklenmez (`kaynaklar/temsil/ayri_sayilan_bolgeler.csv`). Kıbrıs’ın nüfusundan
  KKTC’ninki çıkarılmıştır (yukarıdaki nüfus maddesi); KKTC’nin ipucunda bu sayı görünür. BM üyesi olmayan
  alanların üzerine gelince adı ve durumu (üye değil, gözlemci devlet, kendi kendini yönetmeyen toprak) gösterilir; adlar
  BM’nin kullandığı biçimdedir (WPP 2024; WPP’de yoksa M49); Türkiye’nin tanıdığı devletler (Kuzey Kıbrıs Türk Cumhuriyeti,
  Kosova, Filistin, Vatikan) T.C. Dışişleri Bakanlığının kullandığı adla yazılır (Bakanlığın temsilcilik listesi). Bağlı olunan
  devlet ve anlaşmazlıklar yazılmaz; iki üye arasında tartışmalı Siachen Buzulu adsızdır
  (`kaynaklar/temsil/uye_olmayan_alanlar.csv`). Nüfus balonlarında dairenin alanı ülkenin 2023 nüfusuyla (WPP 2024) orantılıdır. Harita BM üyeliğini gösterir; sınırların ve adların gösterimi bir egemenlik görüşü
  bildirmez.
- Sayfada yalnızca paylar verilir; karşılaştırma ya da değerlendirme cümlesi kurulmaz.

### 2.10. “Ya veto olmasaydı?” sayfası

`web/simulasyon.html` bir veto kaydının kayıtlı oylarını iki sistemde saymaktadır; hiçbir oy değiştirilmez,
eklenmez ya da tahmin edilmez. Yalnızca veri setindeki kayıtlar seçilebilir; varsayımsal bir öneri girilemez ve
sayfa hiçbir modeli tercih etmez. Kitaptaki 20 üyeli Konsey seçildiğinde hesap yine yalnızca kayıtlı oylara
dayanır ve seçili eşiğin oranı korunur: 15 üyede 9 olan mevcut çoğunluk kuralı 20 üyede 12, üçte iki 14,
salt çoğunluk 11 oydur. Kayıtlı olumlu oylar bu eşiği tek başına karşılıyorsa sonuç “kabul edilirdi”dir;
karşılamıyorsa sonuç “kayıtta olmayan üyelere bağlı” olarak verilir ve kayıtta olmayan 5 (1966 öncesinde 9)
üyeden en az kaçının olumlu oy kullanması gerektiği yazılır. Bu üyelerin oyu tahmin edilmez; tamamı olumlu oy
kullansa da eşiğe ulaşılamayan kayıt “çoğunluk yok, kabul edilmezdi” sayılır. Toplu görünümdeki sayılar sayfa açılırken veri setinden
hesaplanır. Diğer modellerle karşılaştırma kutusu 2.8’deki belgelerin hükümlerini kullanır; her birinin dayanak
paragrafı kutuda yazılıdır.

Toplu görünümde eşikler 11 üyeli Konseyde 7, 8 ve 6, 15 üyeli Konseyde 9, 10 ve 8’dir (mevcut çoğunluk
kuralı, üçte iki, salt çoğunluk). Oyların panellerdeki sayım sırası bir gösterimdir; toplantı kayıtlarında üye
bazlı oylama sırası yoktur. BM Şartı’nın 108. maddesine göre Şart değişiklikleri, Genel Kurul üyelerinin üçte
ikisinin oyuyla kabul edilip beş daimî üye dâhil üyelerin üçte ikisi tarafından onaylandığında yürürlüğe girer;
sayfa bu süreç hakkında bir varsayım yapmaz.

## 3. Nedensellik dili

Bir vetonun sonraki olaylara yol açtığı ileri sürülmez. Kayıt ve sayı yan yana verilir.

## 4. Kapsam ve seçim

Veri seti kaynaktaki bütün vetoları içerir; veto eden ülkeye ya da konuya göre seçim yapılmaz.

## 5. Veto eden tarafın gerekçesi

Veto eden üyenin açıklaması toplantı kaydındadır ve her kayıt o belgeye bağlanır. 26 Nisan 2022’den
sonraki vetolarda Genel Kurul tartışmasının kayıtları da bağlanır.

## 6. Tekrarlanabilirlik

Her veri sürümünde indirilen kaynağın adresi, indirme tarihi ve SHA-256 özeti kayıtlıdır
(`kaynaklar/KAYNAKLAR.md`). Ham kopya açık depoda yoktur; aynı adresten indirilip özetle
karşılaştırılabilir. Ayrıştırma kodu açıktır; herkes aynı kaynaktan aynı sonucu üretebilir.
Hata bildirimleri kabul edilir. Veri düzeltmeleri gerekçesiyle `kaynaklar/duzeltmeler.csv`
dosyasına yazılır; değişikliklerin tamamı açık deponun geçmişinde görülür.

## 7. Sonraki aşama

Seçilen vetolar için vaka analizleri ve insani veriler (kayıp, göç, yardım erişimi) henüz eklenmemiştir.
Eklendiklerinde her vakanın seçim ölçütü yazılır; insani veriler yalnızca BM ajanslarının ve tanınmış
bağımsız kurumların yayımladığı rakamlardan alınır.
