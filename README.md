# Veto Atlası

Veto Atlası, BM Güvenlik Konseyinde 1946’dan bu yana kullanılan vetoları kaynaklarıyla
toplar: sekiz sayfalık site (vetoatlas.com), açık veri ve üretim betikleri. Veto tehdidiyle
masaya gelmeyen taslaklar ve Konseyin eylemsizlik vakaları henüz veri setinde yok.

> **Bu depo yayın kopyasıdır; çalışma geçmişi özeldir.** Sürüm 1.0.0 (beta), https://vetoatlas.com.
> Depoda olmayanlar: ham kaynak kopyaları (`data/raw/`; adres, indirme zamanı, bayt ve SHA-256
> `data/raw/KAYNAK.md`'de, yeniden indirme `01` ile), scprocedure Tablo 4 referans tablosu (`03` bu yüzden
> burada çalışmaz; çıktısı `data/processed/vetolar_mutabik.*`), yerel belgeler ve çalışma metinleri (künyeleri
> `kaynaklar/KAYNAKLAR.md`'de; belgeler `07` ile indirilir). Ham dosya yoksa `04` kayıtlı özetle çalışır;
> ham dosyayı ya da yerel belgeleri isteyen testler atlanır.

## English

Veto Atlas collects the vetoes cast in the UN Security Council since 1946, with their sources:
266 proposals and 322 negative votes. The site is at https://vetoatlas.com, in Turkish and English.
The open data is in `web/veri/` as CSV, XLSX and JSON. The code is under MIT, the data under
CC BY 4.0 (`LICENSE-DATA`). See `CITATION.cff` to cite it. If you find an error, write to
iletisim@vetoatlas.com with the record ID and the document you rely on.

## Kurulum

Python 3.12 ile denendi. Proje klasöründe bir terminal açın (VS Code’da Ctrl+`) ve sırayla çalıştırın:

```
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS, Linux
pip install -r requirements.txt
python -m pytest tests -q
python scripts/01_veto_listesini_cek.py
python scripts/02_dogrula.py
python scripts/03_mutabakat.py
python scripts/04_web_verisi.py
python scripts/05_bekleyen_kayitlar.py   # isteğe bağlı: yayımlanmayı bekleyen GK tutanakları
python scripts/06_onizleme_gorseli.py    # paylaşım önizleme görseli (web/onizleme.png)
```

Yazı tiplerini yeniden üretmek için (14): `pip install fonttools brotli ttfautohint-py`, sonra
`python scripts/14_yazi_tipleri.py`.

Son komuttan sonra `web/index.html` dosyasına çift tıklayarak siteyi açabilirsiniz: giriş sayfası hikâyedir
(`web/hikaye.html`), atlasın kendisi `web/vetolar.html`.
Sunucu gerekmez; veri `web/veri.js` dosyasına gömülüdür.

`01` betiği kaynağı indirir, ham kopyasını `data/raw/` altına tarihli olarak arşivler ve
`data/processed/vetolar.json` ile `vetolar.csv` dosyalarını üretir. Ayrıştırılamayan her
satır `data/review/inceleme.csv` dosyasına düşer; hiçbir satır sessizce atılmaz.

Yayımlanan veri `web/veri/` altındadır (266 kayıt). `data/processed/vetolar.*` DHL listesinin ayrıştırılmış
hâlidir (247 satır), `vetolar_mutabik.*` Tablo 4 ile mutabakattan sonraki ara çıktıdır.

## Klasör yapısı

```
README.md                      Bu dosya
LICENSE, LICENSE-DATA          Kod (MIT) ve veri (CC BY 4.0) lisansları; LICENSE-DATA’nın sitedeki kopyası web/LICENSE-DATA.txt
CITATION.cff                   Atıf bilgisi
METODOLOJI.md                  Tanımlar, sayım kuralları, sınırlar (asıl metin)
METODOLOJI_EN.md               İngilizce çevirisi; 04 ikisinden web/metodoloji.html üretir
requirements.txt               Python bağımlılıkları (14 için gerekenler yukarıda)
wrangler.jsonc                 Cloudflare yayını: web/ statik varlık olarak, bulunamayan adreste web/404.html

veto_atlasi/parser.py          Ayrıştırma mantığı (tek doğruluk kaynağı)
veto_atlasi/kaynak.py          Ham dosyayı bayt bayt arşivleme ve SHA-256 doğrulama
veto_atlasi/konu.py            Konu sınıflandırması ve Türkçe başlıklar
veto_atlasi/genel_kurul.py     Genel Kurul tartışmaları (A/RES/76/262) ve Konsey özel raporları
veto_atlasi/alinti.py          Alıntı bankasının kaynaklara karşı doğrulanması
veto_atlasi/metodoloji.py      METODOLOJI.md ve METODOLOJI_EN.md’den web/metodoloji.html
veto_atlasi/excel.py           Açık veri CSV’lerinin Excel kopyası (web/veri/*.xlsx)
veto_atlasi/tek_dosya.py       Tek dosyalık çevrimdışı sürüm
veto_atlasi/cevrimdisi.py      İnternetsiz çalışma (web/cevrimdisi.js)
veto_atlasi/yazi_tipleri.py    Yazı tiplerinin kesilmesi ve hinting

scripts/01_veto_listesini_cek.py   İndir + arşivle + ayrıştır
scripts/02_dogrula.py              Şema, mükerrer ve sayım kontrolleri
scripts/03_mutabakat.py            Referans kaynakla mutabakat + oy dağılımı
scripts/04_web_verisi.py           Konu, Genel Kurul tartışmaları + mutabık veriden web/veri.js, web/veri/ ve web/metodoloji.html
scripts/05_bekleyen_kayitlar.py    Resmî tutanağı bekleyen GK toplantılarını belge sisteminde arar (veriyi değiştirmez)
scripts/06_onizleme_gorseli.py     web/veri.js’ten paylaşım önizleme görseli (Open Graph) üretir
scripts/07_belgeleri_indir.py      Yerel belgeleri KAYNAKLAR.md tablosundan indirir, özetini doğrular
scripts/08_paylasim_kartlari.py    Veri setinden ve alıntı bankasından iki dilli paylaşım kartları (web/kartlar/,
                                   HTML + PNG; PNG için makinedeki Edge/Chrome başsız modda); katalog kaynaklar/kart_katalogu.md
scripts/09_temsil.py               Temsil endeksi: BM bölgesel grupları, P5 ve İİT için nüfus, üye, bütçe, barış gücü ve
                                   koltuk payları (kaynaklar/temsil/*.csv -> data/processed/temsil.json, web/temsil_veri.js;
                                   --girdi ham kaynaklardan CSV üretir)
scripts/10_tek_dosya.py            Tek dosyalık çevrimdışı sürüm: sekiz sayfa yedi sekmede, veri ve yazı tipleri gömülü
                                   (web/veto-atlasi-tek-dosya.html; 04 de üretir)
scripts/11_cevrimdisi.py           İnternetsiz çalışma: web/cevrimdisi.js (service worker; 04 de üretir)
scripts/12_site_haritasi.py        Site haritası: web/sitemap.xml (sayfalar TR/EN ve açık veri; lastmod git kaydından)
scripts/13_harita.py               Temsil haritası: Natural Earth 5.1.2 sınırlarından web/harita_veri.js (Equal Earth; kurallar
                                   kaynaklar/temsil/harita_kurallari.csv, adlar ulke_adlari.csv ve uye_olmayan_alanlar.csv;
                                   --indir Natural Earth dosyalarını indirir)
scripts/14_yazi_tipleri.py         Yazı tiplerini keser ve hinting ekler (web/fonts/README.md)

web/index.html                 Giriş: hikâyeye yönlendirir (yedek: yerel açılış; sunucuda kökü web/_redirects yönlendirir)
web/hikaye.html                Yedi adımlı anlatı (sayılar veri setinden canlı)
web/vetolar.html               Atlas: grafik, filtreler ve kayıtlar (tek dosya, kütüphanesiz)
web/vizyon.html                Söz ve Kayıt: alıntılar ve veri setinden hesaplanan karşılıkları
web/reform.html                Reform modelleri: dört Güvenlik Konseyi reform modeli aynı altı ölçütle
web/simulasyon.html            Ya veto olmasaydı?
web/temsil.html                Kim temsil ediliyor?
web/hakkinda.html              Hakkında: yöntemin sade özeti, bilinen sınırlar, iletişim, lisans ve Zenodo arşivi
web/metodoloji.html            Metodoloji (04 üretir, elle düzenlenmez)
web/404.html                   Bulunamayan adres sayfası (iki dilli, arama motorlarına kapalı)
web/veto-atlasi-tek-dosya.html Tek dosyalık çevrimdışı sürüm (10 ve 04 üretir)
web/cubuk.js, temel.css        Ortak üst çubuk, alt bilgi notu, dil ve tema; ortak yazı ve ızgara kuralları
web/metin.js                   Metin sayfalarının (Hakkında, Metodoloji) "Bu sayfada" dizini
web/suzgec.js                  Ya veto olmasaydı? sayfasının birbirine bağlı filtreleri
web/veri.js                    Sayfalara gömülü veri (04 üretir)
web/temsil_veri.js             Temsil endeksi verisi (09 üretir)
web/harita_veri.js             Temsil haritası (13 üretir)
web/cevrimdisi.js              İnternetsiz çalışma (service worker; elle düzenlenmez, 11 ve 04 üretir)
web/veri/                      İndirilebilir veri (vetolar.csv/xlsx/json, genel_kurul_tartismalari.csv/xlsx); 04 üretir
web/veri/veri_sozlugu.csv      Açık veri sütunlarının sözlüğü (tip, boş değerin anlamı, TR ve EN açıklama); 04,
                               kaynaklar/veri_sozlugu.csv’den kopyalar ve XLSX’lere "sozluk" sayfası olarak ekler
web/kartlar/                   Paylaşım kartları (HTML + PNG; 08 üretir)
web/fonts/                     Gömülü yazı tipleri ve OFL lisansları (üçüncü taraf istek yok)
web/_redirects                 Sunucu yönlendirmesi: / -> /hikaye (302, sorgu korunur; Workers statik varlıkları)
web/_headers                   Sunucu başlıkları: .txt ve açık veri CSV’leri charset=utf-8; kartlar ve tek dosya
                               dizine eklenmez (X-Robots-Tag: noindex)
web/robots.txt, sitemap.xml    Arama motorları: bütün site taranabilir; site haritası (12 üretir)

kaynaklar/                     Referans tablo, gerekçeli düzeltmeler, kaynak notları (KAYNAKLAR.md),
                               gündem sözlüğü (gundem_sozlugu.csv), konu düzeltmeleri,
                               genel_kurul_tartismalari.csv, ozel_raporlar.csv
kaynaklar/alintilar.csv        Alıntı bankası; doğrulaması kaynaklar/alintilar_dogrulama.csv (veto_atlasi/alinti.py)
kaynaklar/temsil/              Temsil endeksi girdileri, harita kuralları ve ülke adları
kaynaklar/kimlik/              Tasarım kılavuzu (KILAVUZ.md) ve logo paketi
kaynaklar/.belgeler/           Yerel belgeler (toplantı kaydı PDF’leri; harita, ad ve KKTC nüfusu kaynakları); depoya girmez, künye ve SHA-256
                               KAYNAKLAR.md’de, indirme: scripts/07_belgeleri_indir.py
data/raw | processed | review  Ham kaynak, işlenmiş veri, elle kontrol listesi
schema/veto_kaydi.schema.json  Her kaydın uyması gereken yapı
tests/                         Birim testleri ve veri seti değişmezleri
```

## Lisans ve atıf

Kod MIT lisansıyla (`LICENSE`), atlasın veri derlemesi CC BY 4.0 lisansıyla (`LICENSE-DATA`) yayımlanır. Alıntılar,
üçüncü taraf veriler ve yazı tipleri kendi lisans ve koşullarına tabidir. Tam liste `LICENSE-DATA`’dadır (sitedeki
kopyası `web/LICENSE-DATA.txt`, ikisi aynı tutulur). Yayın adresi: https://vetoatlas.com

Atıf örneği: Yıldız, Nuh Mehmet. Veto Atlası. Sürüm 1.0.0, 2026. https://doi.org/10.5281/zenodo.23326362
(ayrıntılar `CITATION.cff`’te).

## Hata bildirimi

Veride ya da metinde bir yanlış görürseniz iletisim@vetoatlas.com adresine yazın. Kaydın kimliğini
(ör. V-1980-01-11-1) ve dayandığınız belgeyi ekleyin.
