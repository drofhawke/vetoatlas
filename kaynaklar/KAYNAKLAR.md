# Referans kaynaklar

## Ham DHL dosyası

**Kanonik kaynak:** `data/raw/veto_dhl_2026-10-10.html` (73.235 bayt), SHA-256
`b92d1fe1db9abe42dd8d864c3c88ea6a0fc8074dba39f596f4b544b93e147083`.
https://www.un.org/Depts/dhl/resguide/scact_veto_table_en.htm adresinden 10 Ekim 2026'da
indirilmiştir. Sunucudan gelen baytlar çözülmeden ve satır sonları değiştirilmeden yazılmıştır.
01, 03 ve 04 betikleri özeti bu dosyanın diskteki baytlarından hesaplar; üçü de aynı değeri
gösterir, değer tutmazsa 03 ve 04 durur.

**Internet Archive kopyası:**
https://web.archive.org/web/20260912160946/https://www.un.org/depts/dhl/resguide/scact_veto_table_en.htm
Bu kopyanın ham baytları kanonik dosyayla aynıdır (SHA-256 `b92d1fe1…7083`, 10 Ekim 2026'da
karşılaştırıldı). 10 Ekim'de yeni bir kayıt alınamadı, çünkü un.org arşivin tarayıcısını 403 ile
engelledi. Ayrıntılar `data/raw/KAYNAK.md` dosyasındadır.

`data/raw/veto_dhl_2026-10-09.html` silinmemiştir ama kanonik değildir. 01 betiğinin önceki
sürümü sayfayı metne çevirip Python'un metin moduyla yazıyordu. Windows bu modda her `\n`
karakterini `\r\n`'ye çevirir. Sunucu satırları zaten `\r\n` ile gönderdiği için 1.524 satır
sonunun her biri diske `\r\r\n` olarak geçti. Dosya bu yüzden 1.524 bayt uzundur ve SHA-256
değeri (`2b47731b…ef38`) sunucunun gönderdiği içeriği temsil etmez. İçerik olarak aynıdır:
fazladan `\r` karakterleri atıldığında 10 Ekim indirmesiyle bayt bayt örtüşür, özeti de
`b92d1fe1…` olur. Ayrıştırıcı iki dosyadan aynı 247 kaydı çıkarır. O günkü işlenmiş verideki
özet de bu doğru değerdi, çünkü eski betik özeti diske yazmadan önce bellekteki metinden
hesaplıyordu. Yani kayıtlı özet diskteki dosyayı tutmuyordu. Kanonik olmamasının nedeni budur.
Ham kopyanın işi, sunucudan geleni değiştirmeden saklamak ve herkesin özeti dosyadan yeniden
hesaplayıp doğrulayabilmesini sağlamaktır; bu dosya o sınamayı geçemez. Betiğin yeni sürümü
(`veto_atlasi/kaynak.py`) baytları olduğu gibi yazar ve var olan bir ham dosyanın üzerine asla
yazmaz. `.gitattributes` da git'in `data/raw/` altındaki satır sonlarına dokunmasını engeller.

## Referans tablo

**scprocedure_tablo4.csv** — Sievers & Daws, *The Procedure of the UN Security Council*,
Tablo 4: "Vetoes of draft resolutions and proposed amendments cast in formal Security
Council meetings, 1946 to present", 18 Eylül 2025 sürümü.
https://www.scprocedure.org/_files/ugd/54a569_8c1ef1fee8ca4d6ab09b7fb516b55a22.pdf

PDF'ten elle aktarılmıştır (öneri no, tarih, veto eden üyeler, genel oy). Aktarımın
doğruluğu, kaynağın kendi üye toplamlarıyla (SSCB 114, Rusya 41, ABD 94, İngiltere 30,
Fransa 18, Çin 21; 2 kapalı oturum vetosu üye toplamı dışında) birebir tutturularak
kontrol edilmiştir.

Kaynakta tespit edilen ve toplantı kaydından doğrulanan hatalar (ayrıntı ve sayfa
numaraları `duzeltmeler.csv`'de):
- No 198: tarih "17 Sept. 1995" yazılmış. S/PV.3538'e göre oylama 17 Mayıs 1995'te
  yapılmış, DHL doğru.
- No 224 (8 Temmuz 2015): oy 11-1-4 yazılmış (toplam 16). S/PV.7481'e göre 10-1-4.
- No 243 (13 Aralık 2021): oy 13-2-1 yazılmış (toplam 16). S/PV.8926'ya göre 12-2-1.
- No 43 (13 Aralık 1949): oy 8-2-1 yazılmış. S/PV.456'ya göre S/1431'in ilk bölümü 9-2-0
  ile düşmüş, Arjantin bu oylamada lehte. Aynı günün öbür vetosu (No 44) 8-2-1.
- No 96-97 (20 Şubat 1961): tarih toplantının başladığı gün. S/PV.942'ye göre iki veto da
  gece yarısından sonra, 21 Şubat'ta.

DHL'de doğrulanan hatalar:
- 5 Eylül 1950 (No 45): S/PV.496'nın basılı başlığı "5 Eylül 1950" diyor, ama kaydın
  içeriği toplantının 6 Eylül'de yapıldığını gösteriyor. DHL basılı başlığı izlemiş.
- 3 Aralık 1960 (No 94) ve 22 Ağustos 1968 (No 109): DHL toplantının başladığı günü veriyor.
  İki toplantı da gece yarısını geçmiş ve oylamalar ertesi gün (4 Aralık, 23 Ağustos)
  yapılmış.
- 26 Haziran 1946: Fransa'nın ret oyu DHL'de hiç yok. S/PV.49'a göre bu oy ön soru
  oylamasına (No 4) ait.

11-13 Ocak 1980 (No 145): DHL toplantının iki gününü aralık olarak veriyor; bu bir hata değil.
S/PV.2191'e göre toplantı 11 Ocak'ta oylama yapılmadan ara verdi, S/13735 13 Ocak'taki ikinci
oturumda 10-2-2 ile düştü. Referans tablonun tarihi doğru. Belge yerel belgeler tablosunda (aşağıya bakın).

## Yerel belgeler (depoya girmez)

Toplantı kayıtları ve öbür BM belgelerinin PDF'leri `kaynaklar/.belgeler/` altında yalnızca yerelde
tutulur (`.gitignore`). Depoda künyeleri, indirme adresleri ve SHA-256 değerleri durur;
`scripts/07_belgeleri_indir.py` belgeleri bu tablodan indirir ve özetlerini doğrular (özeti
tutmayan indirme saklanmaz). Otomatik erişimi engellenen adres için betik durumu bildirir; belge
tarayıcıyla elle indirilip klasöre konur, erişim engeli aşılmaz. İndirme adresleri dosyaların
indirme kaydından (Windows Zone.Identifier) ya da indiren komuttan alındı.

| Dosya | Künye | İndirme adresi | Sayfa | Bayt | SHA-256 |
|---|---|---|---|---|---|
| `S_PV.704.pdf` | Güvenlik Konseyi 704. toplantı kaydı, 13 Aralık 1955 (S/PV.704), İngilizce ve Fransızca, Resmî Kayıtlar baskısı. Taranmış; metin katmanı OCR ve hatalı, yalnızca oylamaların yerini bulmak için kullanıldı, bulgular sayfa görüntülerinden okundu. Basılı sayfa = PDF sayfası − 2. Dayanak olduğu kayıtlar: 13 Aralık 1955'teki 16 veto (`duzeltmeler.csv`). Elle indirildi (10 Ekim 2026); aynı adres betikle de aynı özeti veriyor. | https://documents.un.org/doc/undoc/gen/n56/090/32/pdf/n5609032.pdf | 24 | 2758833 | `a1324a62702f399a40bd8a952aafe581c49121dca554c038d21c217a69d7cdf6` |
| `S_PV.1662.pdf` | Güvenlik Konseyi 1662. toplantı kaydı, 10 Eylül 1972 (S/PV.1662), İngilizce. Taranmış; metin katmanı OCR, bulgular sayfa görüntülerinden okundu. Basılı sayfa = PDF sayfası − 2. Dayanak olduğu kayıt: 10 Eylül 1972 Çin–SSCB değişiklik vetosu (`duzeltmeler.csv`). Elle indirildi (10 Ekim 2026). | https://documents.un.org/doc/undoc/gen/n75/821/91/pdf/n7582191.pdf | 22 | 3369638 | `c03dfb154c41c11149967b4c09804bee6a8d2bc4385edb0281ff5fee8646c29c` |
| `S_PV.2191_Add.1.pdf` | Güvenlik Konseyi 2191. toplantı kaydı ve Add.1, 11 ve 13 Ocak 1980 (S/PV.2191 and Add.1), İngilizce. documents.un.org'da bulunmadığı için BM Dijital Kütüphanesi'nden elle indirildi (10 Ekim 2026; kayıt sayfası https://digitallibrary.un.org/record/549704). Dijital Kütüphane otomatik isteğe boş yanıt (202) veriyor; betik bunu bildirir. Taranmış; metin katmanı güvenilir değil, bulgular sayfa görüntülerinden okundu. Basılı sayfa = PDF sayfası − 2. Dayanak olduğu kayıt: V-1980-01-11-1. | https://digitallibrary.un.org/nanna/record/549704/files/S_PV.2191ANDAdd.1--S_PV.2191--S_PV.2191_Add.1-EN.pdf | 19 | 2851748 | `dde22974f924d2591cfec51bb4233792e4654f2ec6ba2d6e898d309df72884c0` |
| `A_58_47.pdf` | Genel Kurul, 58. oturum, Ek No. 47 (A/58/47): Güvenlik Konseyi'nde adil temsil ve üye sayısının artırılması konulu açık uçlu çalışma grubunun raporu, 2004. Annex III "Negative votes of permanent members at public meetings of the Security Council": Part I karar taslakları, Part II "Paragraphs of draft resolutions or amendments thereto not adopted owing to the negative vote of a permanent member". DHL veto listesi 1946–2004 verisinin kaynağı olarak bu eki gösterir. Betikle indirildi (10 Ekim 2026). | https://documents.un.org/api/symbol/access?s=A/58/47(SUPP)&l=en&t=pdf | 38 | 166799 | `61b7c1f6d88d4adf3fd76065f972ede8d78bdb916299ed1cc8d18eded63fc607` |
| `WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx` | BM Dünya Nüfus Beklentileri 2024 (WPP 2024), demografik göstergeler, kompakt dosya (POP/DB/WPP/Rev.2024/GEN/F01/Rev.1); sayfalar "Estimates" (1950–2023), "Medium variant", "NOTES". Lisans CC BY 3.0 IGO; atıf (dosyadaki metin): "United Nations, Department of Economic and Social Affairs, Population Division (2024). World Population Prospects 2024, Online Edition." Kullanılan sütun: "Total Population, as of 1 January (thousands)", yıllar 1963 ve 2023. Erişim 10 Ekim 2026. | https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/EXCEL_FILES/1_General/WPP2024_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT.xlsx | – | 26142942 | `98e34d9b65b53858cd08a57a566e45050b08093ad85ba5714fe6fbd78055ae6d` |
| `Scale_of_Assessments_for_RB_1946-2027.xlsx` | Katkılar Komitesi, "United Nations Scale of assessments for the Regular budget 1946-2027" (Excel); 2025–2027 sütunu A/RES/79/249 (24 Aralık 2024) ölçeğidir, toplam 100. Erişim 10 Ekim 2026. A/RES/79/249 PDF'inden pdftotext ile okuma sütun kaydırdığı için (ör. Türkiye 0,018 görünür, doğru değer 0,685) Excel esas alındı. | https://www.un.org/en/ga/contributions/Scale%20of%20Assessments%20for%20RB%201946-2027.xlsx | – | 78130 | `737d0d78b0225ad10c3f42328799fe28842634ac0d697eba5e023cb2e1edbbd8` |
| `02_country_ranking_95_february_2026.pdf` | BM Barış Gücü, "Uniformed Personnel Contributing Countries by Ranking: Experts on Mission, Formed Police Units, Individual Police, Staff Officer, and Troops, As of: 28/02/2026" (aylık rapor 95); 119 ülke, genel toplam 47 298. Sayfa https://peacekeeping.un.org/en/troop-and-police-contributors (dosya adresi sayfa betiğinden). Erişim 10 Ekim 2026. | https://peacekeeping.un.org/sites/default/files/2026-03/02_country_ranking_95_february_2026.pdf | 4 | 189126 | `f5896fe44e71a204fa4e37f05de482c898e158d523e3dc4d7e6c0146d0cc9e3a` |
| `A_74_PV.3.pdf` | Genel Kurul, 74. oturum, 3. genel kurul toplantısının kaydı, 24 Eylül 2019 (A/74/PV.3), İngilizce, Resmî Kayıtlar. Cumhurbaşkanı Erdoğan'ın konuşması s. 19–24; kayıttaki not: "spoke in Turkish; English interpretation provided by the delegation". Metin katmanı dijitaldir (taranmamış). Sayfa numarası = PDF sayfası ("22/60"). Dayanak olduğu kayıt: alıntı 2019-2'nin İngilizcesi (2019 İngilizce kitapçığında bu pasaj yok). Betikle indirildi (14 Ekim 2026, 08:14 UTC). | https://documents.un.org/api/symbol/access?s=A/74/PV.3&l=en&t=pdf | 60 | 969653 | `6be031612fdcc26dc8f49904bf83cb7ee8841b53bbb6bfeeba635c72d13836ce` |
| `A_RES_1991_XVIII.pdf` | Genel Kurul kararı 1991 (XVIII) A ve B, 17 Aralık 1963: Güvenlik Konseyi ve Ekonomik ve Sosyal Konsey'de adil temsil; A par. 3: on seçilmiş üyenin dağılımı (Afrika ve Asya 5, Doğu Avrupa 1, Latin Amerika 2, Batı Avrupa ve diğerleri 2). Taranmış, OCR metin katmanı. | https://documents.un.org/api/symbol/access?s=A/RES/1991(XVIII)&l=en&t=pdf | 2 | 158586 | `245d9b915f14104fed7109f5f7b5a1eff3654e186cdde35ab6a95418e97a0aef` |

**DHL listesinin kapsamı.** DHL veto listesi, 1946–2004 verisini A/58/47 Annex III'ten aldığını
yazar ve yıldızlı satırlar için "most are veto of paragraphs or amendments" der. Liste, Annex III
Part II'deki paragraf ve değişiklik önergesi vetolarının birçoğunu içerir (ör. 24 Kasım 1961 ve
21 Şubat 1961'de ikişer satır, 14 Aralık 1955, 13 Aralık 1949'da iki satır, 25 Ağustos 1947,
26 Temmuz 1985). Part II'deki 13 Aralık 1955 satırlarının 16'sı ve 10 Eylül 1972 S/10786 2 (a)
satırı ise listede yok. Kapsam dışı bırakma kuralı belirtilmediği ve aynı türden satırlar listede
bulunduğu için bu, kapsam farkı değil eksikliktir (`hata_bildirimi.md`, DHL iletisi, 8. madde).
Öte yandan 29 Eylül 1972 S/10805/Rev.1'in iki paragraf vetosu (Part II) DHL'de tek satırda
"(as amended)" olarak görünür; liste Part II'yi bütünüyle aktarmaz.

Aynı denetim DHL Araştırma Rehberi'ndeki güncel listede (Liste B) de yapıldı: adres
https://research.un.org/en/docs/sc/quick/veto, tablo kaynağı
https://ydsftksff8.execute-api.us-east-1.amazonaws.com/dev/render_meeting_veto/sc_veto_list/EN,
erişim 10 Ekim 2026 15:15 UTC, kopya `data/raw/veto_dhl_rehber_2026-10-10.html` (254 satır).
Listede "13 December 1955" tarihli satır yok (Aralık 1955 için yalnızca 14 ve 15 Aralık var);
"10 September 1972" için tek satır var, S/10784 (ABD); S/10786, S/3502, S/3506 ve S/PV.704
hiç geçmiyor. 17 vetonun 17'si bu listede de yok; 8. madde iki liste için geçerli.

**Referans tablonun gün içi sırası.** scprocedure Tablo 4 ters kronolojiktir; aynı gün içindeki
satırların hangi kurala göre sıralandığını belirtmez. 13 Aralık 1955 ve 10 Eylül 1972'de tablonun
sırası toplantıdaki oylama sırasından farklıdır (Moğolistan vetosu #76, toplantıda 16 vetonun
3.'sü; #119 değişiklik vetosu #118 ABD vetosundan önce oylandı). Tablo kronolojik sıra iddia
etmediği için bu bir hata sayılmaz; fark yalnızca kayıt notlarında yazılıdır.

## Temsil endeksi girdileri (`kaynaklar/temsil/`, `scripts/09_temsil.py`)

Girdi CSV'leri `python scripts/09_temsil.py --girdi` ile aşağıdaki kaynaklardan üretilir; ham HTML kopyaları
`data/raw/temsil/` altındadır (erişim 10 Ekim 2026). Büyük dosyalar yukarıdaki "Yerel belgeler" tablosundadır.
un.org sayfaları BM kullanım koşullarına tabidir (https://www.un.org/en/about-us/terms-of-use); İİT sayfası
kullanım koşulu belirtmez. Veri setine (vetolar) hiçbir şey eklenmez; çıktı `data/processed/temsil.json`.

| Girdi | Kaynak | Adres | Erişim | Lisans / koşul | Ham kopya (SHA-256) |
|---|---|---|---|---|---|
| `nufus_wpp2024.csv` | WPP 2024, 1 Ocak nüfusu (bin), 1963 ve 2023, 237 ülke/alan, ISO3 ile | yukarıdaki Excel | 2026-10-10 | CC BY 3.0 IGO; atıf: "United Nations, Department of Economic and Social Affairs, Population Division (2024). World Population Prospects 2024, Online Edition." | `98e34d9b…` (Excel) |
| `kktc_nufus.csv` | Kuzey Kıbrıs Türk Cumhuriyeti nüfusu, 2022 yıl sonu projeksiyonu (462.747); Kıbrıs'ın WPP nüfusundan çıkarılır (WPP'nin Kıbrıs verisi adanın tamamını kapsar). KKTC İstatistik Kurumu, "Kamuoyu Bilgilendirme: Nüfus Projeksiyonları", 11 Kasım 2024 (2019–2022 serisi bu yayında düzeltildi) | https://istatistik.gov.ct.tr/Portals/39/Proj_yayin_11_Kasim_2024_1.pdf | 2026-10-19 | kaynağın koşulları | `kaynaklar/.belgeler/kktc/Proj_yayin_11_Kasim_2024_1.pdf` (216084 bayt) `60a359b7aa17459300a780b80fe7463ef686a94283d240d79fd05f2a25a55f97` |
| `uye_devletler.csv` | BM üye devletleri ve kabul tarihleri (193) | https://www.un.org/en/about-us/member-states | 2026-10-10 | BM kullanım koşulları | `uye_devletler_2026-10-10.html` `ee2f0f2faa59256bc6651778eb9f940a1a24d6d0aed9624697473e17fca52163` |
| `bolgesel_gruplar.csv` | DGACM, Regional groups of Member States (Afrika 54, Asya-Pasifik 55, Doğu Avrupa 23, GRULAC 33, WEOG 29; Türkiye iki listede) | https://www.un.org/dgacm/en/content/regional-groups | 2026-10-10 | BM kullanım koşulları | `bolgesel_gruplar_2026-10-10.html` `b431e7cf508847e60d8ccce954f9c936c681947a964144256447dc7ac49408c4` |
| `iit_uyeleri.csv` | İslam İşbirliği Teşkilatı üye devletleri (57, üyelik yılıyla); sayfa JavaScript'le dolduğu için tarayıcıda işlenmiş kopya | https://www.oic-oci.org/en/members | 2026-10-10 | belirtilmemiş | `iit_uyeler_2026-10-10.html` `66a7d8f69922a756114ff3e4a96bae3c4181e1bb4d53b00eac4c2bc6298f9e1a` |
| `butce_olcegi_2025_2027.csv` | Olağan bütçe katkı ölçeği 2025–2027 (A/RES/79/249) | yukarıdaki Excel | 2026-10-10 | BM kullanım koşulları | `737d0d78…` (Excel) |
| `baris_gucu_2026-02.csv` | Üniformalı personel, ülke sıralaması, 28 Şubat 2026 | yukarıdaki PDF | 2026-10-10 | BM kullanım koşulları | `f5896fe4…` (PDF) |
| `gk_uyeleri_2026.csv` | Güvenlik Konseyi mevcut üyeleri (5 daimî; seçilmiş: Bahreyn, Kolombiya, Kongo DC, Letonya, Liberya 2027; Danimarka, Yunanistan, Pakistan, Panama, Somali 2026) | https://main.un.org/securitycouncil/en/content/current-members | 2026-10-10 | BM kullanım koşulları | `gk_uyeler_2026-10-10.html` `9a7b20e88ab64610f0c0e63803417a17794fce244a5275ec95a54a72cc949caa` |

Seçilmiş koltuk dağılımının dayanağı A/RES/1991 (XVIII) A par. 3 (yukarıdaki tablo) ve mevcut dönem
üyeliğidir (Afrika 3, Asya-Pasifik 2, Doğu Avrupa 1, GRULAC 2, WEOG 2). Madde 23 ve 27 değişikliği
31 Ağustos 1965'te yürürlüğe girdi (BM Şart değişiklikleri sayfası: https://www.un.org/en/node/125739).
Bütçe ölçeği PDF'ini (A/RES/79/249) pdftotext ile okumak sütunları kaydırdığından Excel esas alındı.
Barış gücü sayfası yalnızca PDF sunar; dosya adı her ay değişir, adres sayfa betiğinden alınır.

### Temsil haritası (`scripts/13_harita.py`, `web/harita_veri.js`)

Sınırlar Natural Earth 1:50m Cultural Vectors 5.1.2'den (kamu malı; https://www.naturalearthdata.com/about/terms-of-use/).
Dosyalar depoya girmez; `python scripts/13_harita.py --indir` aşağıdaki adreslerden `kaynaklar/.belgeler/natural_earth/`
altına indirir ve özetlerini doğrular. Natural Earth'ün varsayılan çizimi fiilî durumdur; tartışmalı alanların ataması
`kaynaklar/temsil/harita_kurallari.csv`'de gerekçesiyle. Ülke adları `kaynaklar/temsil/ulke_adlari.csv`'de: Unicode CLDR 48
(Node.js 24, ICU 78.3) Türkçe ve İngilizce bölge adları, site adlandırmasına göre düzeltilmiş (ör. ABD, Rusya Federasyonu,
Kongo Demokratik Cumhuriyeti; İngilizcede "&" yerine "and"). BM üyesi olmayan alanların adları
`kaynaklar/temsil/uye_olmayan_alanlar.csv`'de: BM'nin kullandığı ad (WPP 2024 dosyasındaki ad, yoksa aşağıdaki M49
sayfasındaki ad); Türkiye'nin tanıdığı devletler (Kuzey Kıbrıs Türk Cumhuriyeti, Kosova, Filistin, Vatikan) T.C. Dışişleri
Bakanlığı'nın temsilcilik listesindeki adla. Tanıma dayanağı Bakanlığın kendi kaynakları: Lefkoşa, Priştine ve Vatikan
büyükelçilikleri, Kudüs Başkonsolosluğu; Filistin sayfasında "Filistin Devleti'ni ilk gün tanıyan ülkeler arasında", Vatikan
sayfasında "11 Nisan 1960 tarihinde diplomatik ilişkiler kurulmuştur". Erişim 19 Ekim 2026.

| Dosya | İndirme adresi | Bayt | SHA-256 |
|---|---|---|---|
| `ne_50m_admin_0_countries.geojson` | https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_50m_admin_0_countries.geojson | 3083490 | `3e458fc036ad0a66411f2c1e6cac49c5d7bfb81cb1123bc513b22511a2b7fdeb` |
| `m49_overview_2026-10-19.html` (`kaynaklar/.belgeler/m49/`) | https://unstats.un.org/unsd/methodology/m49/overview/ (BM İstatistik Bölümü, ülke ve alan kodları; WPP'de bulunmayan üye olmayan alanların BM adları) | 1721575 | `b9048114f6e7f2abda83bf03d4263c9d7cd1bd7230e3d0461025ee7839a7a1fb` |
| `temsilcilikler.tr_2026-10-19.js` (`kaynaklar/.belgeler/disisleri/`) | https://www.mfa.gov.tr/site_media/assets/content/temsilcilikler/temsilcilikler.tr.js (T.C. Dışişleri Bakanlığı, temsilcilik listesi, Türkçe adlar) | 86330 | `b3896d8e62fc7b96f325f690bfe3e3c7ceb7f4e4c8989aaa2c9152cee79a448b` |
| `temsilcilikler.en_2026-10-19.js` (`kaynaklar/.belgeler/disisleri/`) | https://www.mfa.gov.tr/site_media/assets/content/temsilcilikler/temsilcilikler.en.js (aynı liste, İngilizce adlar) | 86682 | `1706b8091d941be0fb32d15bf9c5b573277ef3b830c06af2c4bcc6cfdb236b5e` |
| `turkiye-filistin-siyasi-iliskileri_2026-10-19.html` (`kaynaklar/.belgeler/disisleri/`) | https://www.mfa.gov.tr/turkiye-filistin-siyasi-iliskileri.tr.mfa | 31871 | `e51a2a2c6f695f809f4bc1a9d80e0f5213c82c6b7a29371e246750ffd71a7427` |
| `turkiye-vatikan-siyasi-iliskileri_2026-10-19.html` (`kaynaklar/.belgeler/disisleri/`) | https://www.mfa.gov.tr/turkiye-vatikan-siyasi-iliskileri.tr.mfa | 30265 | `817a46af44951a677865e08087d3aa13cfe371f0723336bfa13fdc62d101f076` |
| `ne_50m_admin_0_breakaway_disputed_areas.geojson` | https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_50m_admin_0_breakaway_disputed_areas.geojson | 147141 | `e91f0f9518b24355ceec6668f4df874d6f39db7d0bc9ec22d9b14429bfb6be01` |


## Çalışma metinleri (depoya girmez)

Alıntı bankası ve model sayfası için kullanılan metinler `kaynaklar/calisma_metinleri/` altında
yalnızca yerelde tutulur (`.gitignore`). Depoda künyeleri, indirme adresleri ve SHA-256 değerleri
durur; aynı dosyayı indiren herkes özetle karşılaştırarak aynı metni kullandığını doğrulayabilir.
Alıntı testleri bu dosyalar yerelde varsa çalışır, yoksa atlanır (`tests/conftest.py`).
İndirme adresleri dosyaların indirme kaydından (Windows Zone.Identifier) alındı. İlk üç dosyanın
adreslerine otomatik istek atılmadı. 2019 İngilizce kitapçığının adresinden 14 Ekim 2026'da dosya
yeniden indirildi; aynı özeti veriyor.

| Dosya | Künye | İndirme adresi | Bayt | SHA-256 |
|---|---|---|---|---|
| `Birlesmis_milletler_konuşması2019.pdf` | Türkiye Cumhuriyeti Cumhurbaşkanı Recep Tayyip Erdoğan, *Birleşmiş Milletler 74. Genel Kurulu Konuşması*, 24 Eylül 2019, New York. Cumhurbaşkanlığı İletişim Başkanlığı yayını, 36 sayfa. | https://yayinlar.iletisim.gov.tr/uploads/Birlesmis_milletler_konu%C5%9Fmas%C4%B1.pdf (yayın sayfası: https://yayinlar.iletisim.gov.tr/detay/cumhurbaskani-recep-tayyip-erdoganin-birlesmis-milletler-74-genel-kurulu-konusmasi) | 984189 | `7560e5dae69d5794beb9b365ecde136688b5c894239c4dac30c163b5025f21f8` |
| `BM2026-2022-web.pdf` | *Cumhurbaşkanı Recep Tayyip Erdoğan'ın BM Genel Kurulu Hitapları (2022-2026)* / *President Recep Tayyip Erdoğan's Addresses at the UN General Assembly (2022–2026)*, Türkçe, İngilizce ve Arapça. Cumhurbaşkanlığı İletişim Başkanlığı Yayınları, 1. baskı, Eylül 2026, ISBN 978-625-8937-23-7, 292 sayfa. | https://yayinlar.iletisim.gov.tr/uploads/BM2026-2022-web.pdf (yayın sayfası: https://yayinlar.iletisim.gov.tr/detay/cumhurbaskanimiz-recep-tayyip-erdoganin-bm-genel-kurulu-hitaplari) | 78253223 | `95a411fc27a712d09a4e67037ad87e5c93117813b9468907b7752ad42df732ed` |
| `DahaAdilBirDünyaMümkün.pdf` | Recep Tayyip Erdoğan, *Daha Adil Bir Dünya Mümkün: Birleşmiş Milletler Reformu İçin Bir Model Önerisi*, Turkuvaz Kitap, 1. baskı, Eylül 2021, ISBN 978-625-7548-08-3, 132 sayfa. Hakları Turkuvaz Medya Grubu'na aittir. | Resmî indirme adresi yok; yerel kopya bir paylaşım sitesinden (pdfkitapoku.org, Yandex Disk) indirildi. PDF basılı baskının sayfa numaralarını içermez: alıntılara sayfa numarası yazılmaz, atıf yalnızca bölüm başlığıyla yapılır. | 1375541 | `8cc02a625387f855980f2c960e53fffb9a9ec2a9c0a0ac7e7f9856046c9aac9e` |
| `Birlesmis_Milletler_EN_2019.pdf` | President of the Republic of Turkey Recep Tayyip Erdoğan's *Address to the 74th Session of the United Nations General Assembly*, 24 September 2019, New York. Cumhurbaşkanlığı İletişim Başkanlığı yayını; Türkçe kitapçıkla aynı yayın sayfasındaki İngilizce sürüm, 24 sayfa. Konuşmanın hazırlanmış metnidir: kürsüde eklenen bazı cümleler (ör. alıntı 2019-2) bu kitapçıkta yoktur. Erişim 14 Ekim 2026. | https://yayinlar.iletisim.gov.tr/uploads/Birles%CC%A7mis%CC%A7_Milletler_EN.pdf (yayın sayfası: https://yayinlar.iletisim.gov.tr/detay/cumhurbaskani-recep-tayyip-erdoganin-birlesmis-milletler-74-genel-kurulu-konusmasi) | 953956 | `3da12fb7d63c00fca759a2a33c0016e39e2590262593bc9c63882f76047a174c` |
| `A_Fairer_World_is_Possible_EN.pdf` | Recep Tayyip Erdoğan, *A Fairer World is Possible: A Proposed Model for a United Nations Reform*, çeviren Doğan Eşkinat, Turkuvaz Kitap, 1. baskı (First Printing), Eylül 2021, ISBN 978-625-7548-19-9. Hakları Turkuvaz Haberleşme ve Yayıncılık A.Ş.'ye aittir. *Daha Adil Bir Dünya Mümkün*'ün İngilizce baskısı. Künye, PDF s. 4'teki künye sayfasının görüntüsünden okundu. | Resmî indirme adresi yok; yerel kopya basılı baskının Internet Archive taramasıdır (https://archive.org/details/isbn_9786257548199, 2022) ve bir paylaşım sitesinden indirildi (https://dokumen.pub/download/a-fairer-world-is-possible-a-proposed-model-for-a-united-nations-reform-1nbsped-9786257548199.html). Taranmıştır, metin katmanı OCR'dır: alıntılar sayfa görüntüleriyle karşılaştırıldı (aşağıda "OCR düzeltmesi"). 220 PDF sayfası; basılı sayfa = PDF sayfası − 2. | 8789570 | `a6e6f0ef6feb74ac947a7d46b666a6be6c26c035ccf39f010ec81d1524bdcb53` |

**Sayfa numaraları.** Alıntı bankasında (`kaynaklar/alintilar.csv`) basılı sayfa ve PDF sayfası
birlikte tutulur. 2019 kitapçığında basılı sayfa = PDF sayfası − 2 (kapak ve iç kapak
numarasız). 2022–2026 derlemesinde basılı sayfa = PDF sayfası − 1. Bu fark, Türkçe ve İngilizce
bölümlerin numaralı 206 sayfasının tamamında sayfa başlığındaki numarayla doğrulandı; istisna
yok. Kitap PDF'i basılı baskının sayfa numaralarını içermez; kitap alıntılarının Türkçesinde sayfa numarası
yazılmaz, atıf bölüm başlığıyla yapılır. 2019 İngilizce kitapçığında da basılı sayfa = PDF sayfası − 2
(numaralı 15 sayfanın, basılı s. 5–19, hepsinde tutuyor). İngilizce kitapta basılı sayfa = PDF
sayfası − 2. Sayfa numarası metin katmanında 164 sayfada okunuyor; 162'sinde fark tutuyor. İki istisna OCR'ın yanlış
okumasıdır, ikisi de görüntüden okundu: PDF s. 139'da basılı "137" "iL37", PDF s. 155'te basılı "153" "133" olarak
okunuyor. A/74/PV.3'te sayfa numarası PDF sayfasıdır ("22/60").

**İngilizce metinler.** Resmî İngilizce metin şu sırayla aranır: kaynağın resmî İngilizce sürümü
(2022–2026 derlemesinin İngilizce bölümü, 2019 İngilizce kitapçığı, kitabın İngilizce baskısı); orada
yoksa BM'nin İngilizce toplantı kaydı. Alıntı 2019-2'nin İngilizcesi 2019 İngilizce kitapçığında yok
(kitapçık konuşmanın hazırlanmış metnidir; Türkçe kitapçık kürsüde söyleneni verir); İngilizcesi
A/74/PV.3'ten alındı (s. 22; kayıtta "spoke in Turkish; English interpretation provided by the
delegation"). Kitap alıntılarının İngilizcesi İngilizce baskıdan, basılı sayfa numarası ve İngilizce bölüm
başlığıyla (Introduction; Part II: A United Nations Reform) alındı. Kitap-7 iki sayfaya yayılır (s. 184–185).
Alıntının başı birinci sayfanın gövdesinin tam sonunda, devamı ikinci sayfanın gövdesinin tam başında aranır. Gövde,
sayfa başlığı ve sayfa numarası çıkarılmış metindir. pdftotext'in iki uygulaması sayfa kenarını farklı verir: xpdf
(Git Bash ile gelir) hecelenmiş sözcüğü ve numarayı ayrı satırlarda verir, Poppler (PowerShell'de varsayılan) numarayı
sözcüğe yapıştırır ("Secu184"). Bu yüzden doğrulama ikisiyle de sınandı. Resmî
İngilizcesi bulunamayan alıntıda Türkçe özgün metin kalır ve altına "Unofficial translation by Veto Atlas"
etiketli çeviri eklenir (`ceviri_en`); şu an böyle bir alıntı yok.

**OCR düzeltmesi.** İngilizce kitabın metin katmanı OCR'dır. Alıntıların geçtiği yedi sayfa
(PDF s. 33, 34, 139, 140, 182, 186, 187) sayfa görüntüsüyle karşılaştırıldı. Tek fark PDF s. 34'te (basılı 32):
basılı sayfadaki boşluklu kısa tireyi (–) OCR uzun tire (—) okuyor. Doğrulama bu yeri görüntüdeki gibi düzeltip
arar (`veto_atlasi/alinti.py`, `OCR_DUZELTMELERI`). Düzeltme sayfada tam bir kez geçmezse doğrulama durur.
Bunun dışında metin katmanına dokunulmaz.

**Dizgi sorunu.** Derlemenin 2025 Türkçe bölümünün son sayfasında (PDF s. 50, basılı 49) metin
katmanında konuşmanın son satırlarına önsözün metni karışıyor. Sayfa görüntüsünde yalnızca
konuşma var. Bu sayfadan alınan alıntı, karışmanın başladığı yerden önce bitiyor; sayfa
görüntüsüyle karşılaştırıldı (`tests/test_alintilar.py`).

**Alıntı doğrulaması.** Her alıntı, kaynağın metin katmanında belirtilen sayfada kelimesi
kelimesine geçmelidir (boşluk, satır sonu ve satır sonu hecelemesi normalize edilir).
Türkçe metin Türkçe kaynakta, İngilizce metin İngilizce kaynakta ayrı ayrı aranır.
Doğrulama sonucu `kaynaklar/alintilar_dogrulama.csv` dosyasına alıntı metinlerinin ve kaynakların
SHA-256 özetleriyle yazılır. Kaynak yerelde yoksa 04 betiği o kaynaktan gelen metni bu kayda göre kabul
eder; kayıtta olmayan ya da metni değişmiş alıntı sisteme giremez. BM belgesi olan kaynak (A/74/PV.3)
"Yerel belgeler" tablosundadır ve `scripts/07_belgeleri_indir.py` ile indirilir.

## Güvenlik Konseyi reform modelleri (vizyon sayfası karşılaştırma tablosu)

`kaynaklar/reform_modelleri.csv` birincil belgelerden doğrudan aktarıldı (10 Ekim 2026'da indirildi;
dosyalar depoda değil, özetleri burada). Her hücrenin dayanağı (paragraf) dosyada yazılıdır.

| Model | Belge | Kaynak | Bayt | SHA-256 |
|---|---|---|---|---|
| G4 | A/59/L.64 (6 Temmuz 2005) | https://documents.un.org/api/symbol/access?s=A/59/L.64&l=en&t=pdf | 35998 | `63f9ed024b40b89a474efb318ab7059829e315d38c6021ee0a263fe51c2041b5` |
| Uzlaşı için Birlik | A/59/L.68 (21 Temmuz 2005) | https://documents.un.org/api/symbol/access?s=A/59/L.68&l=en&t=pdf | 124388 | `eaabf4409f1c73d91ba5433efe6db89d93e89bf3698e6473afd5e46c497e76f4` |
| Afrika Birliği taslağı | A/59/L.67 (18 Temmuz 2005) | https://documents.un.org/api/symbol/access?s=A/59/L.67&l=en&t=pdf | 28884 | `babc98c4d5f44a2ef4ef4f79679048b4e30d8253daf60a0412353c7611c47149` |
| Ezulwini Uzlaşısı | Ext/EX.CL/2 (VII), Afrika Birliği Yürütme Konseyi 7. Olağanüstü Oturumu, 7-8 Mart 2005 | https://old.centerforunreform.org/sites/default/files/Ezulwini%20Consensus.pdf | 167134 | `becbc792e1135b3fb2a312f15745a93cb033debb642053dd85d479a48e2978d0` |

Ezulwini Uzlaşısı'nın BM'deki kopyası (un.org/en/africa/osaa) 403 döndürdü; engel aşılmadı.
Afrika Birliği'nin kendi belge arşivinde metnin kendisi bulunamadı. Kullanılan kopya, Center for
UN Reform Education'ın yayımladığı, Afrika Birliği antetli ve belge numaralı (Ext/EX.CL/2 (VII))
8 sayfalık metindir.

## Referans kapsamı sonrası (BM birincil kaynakları)

18 Eylül 2025 sonrasındaki vetolar toplantı kayıtlarından doğrulanır. Erişim tarihi
10 Ekim 2026. Belgeler https://documents.un.org üzerinden indirilmiştir.
- 7 Nisan 2026: S/2026/273, S/PV.10130 (oylama s. 4). Basın bülteni SC/16330 press.un.org
  CAPTCHA istediği için açılamadı.
- 17 Eylül 2026: S/2026/740, S/PV.10224 (oylama s. 4), basın bülteni SC/16455
  (https://press.un.org/en/2026/sc16455.doc.htm). Kanonik ham dosyada (DHL'nin statik sayfası)
  yok; DHL araştırma rehberindeki güncel listede (research.un.org, 23 Eylül 2026 güncellemesi) var.

**DHL'nin iki listesi.** Statik sayfa (scact_veto_table_en.htm) ile araştırma rehberindeki
güncel liste (https://research.un.org/en/docs/sc/quick/veto) 10 Ekim 2026'da karşılaştırıldı.
Güncel listede 251 kayıt, statik sayfada 247 kayıt var. Güncel listenin fazlası 17 Eylül 2026
vetosu ile üç tarih aralığının iki satıra bölünmesinden geliyor: 3/4 Aralık 1960, 7/9 Ocak 1980 ve
11/13 Ocak 1980. Bu bölünme aynı vetoyu iki kez saydırır; 1960 için S/PV.911'de tek oylama var.
Kanonik kaynak bu yüzden şimdilik statik sayfa olarak kalıyor.

**Genel toplamlar için:** scprocedure.org "Overview of vetoes cast from 1946 to present", 7 Nisan 2026.

Doğrulanan hatalar için kaynak sahiplerine gönderilecek bildirim taslağı:
`kaynaklar/hata_bildirimi.md` (henüz gönderilmedi).
