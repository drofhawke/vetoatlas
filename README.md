# Veto Atlası (BM Veto ve Kilitlenme Atlası)

BM Güvenlik Konseyi'nde 1946'dan bugüne kullanılan vetoları, veto tehdidiyle masaya
gelmeyen taslakları ve Konsey'in eylemsizlik vakalarını kaynaklı, doğrulanabilir ve
indirilebilir bir veri setinde toplayan interaktif platform.

> **Bu depo yayın kopyasıdır; çalışma geçmişi özeldir.** Sürüm 1.0.0 (beta), https://vetoatlas.com.
> Depoda olmayanlar: ham kaynak kopyaları (`data/raw/`; adres, indirme zamanı, bayt ve SHA-256
> `data/raw/KAYNAK.md`'de, yeniden indirme `01` ile), scprocedure Tablo 4 referans tablosu (`03` bu yüzden
> burada çalışmaz; çıktısı `data/processed/vetolar_mutabik.*`), yerel belgeler ve çalışma metinleri (künyeleri
> `kaynaklar/KAYNAKLAR.md`'de; belgeler `07` ile indirilir). Ham dosya yoksa `04` kayıtlı özetle çalışır;
> ham dosyayı ya da yerel belgeleri isteyen testler atlanır.

**Aşama 1 (bu sürüm): Veri temeli.** Arayüz, veri seti sağlamlaşmadan yazılmaz.

## Kurulum (Windows, VS Code)

VS Code'da proje klasörünü açın, terminali açın (Ctrl+`) ve sırayla çalıştırın:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest tests -q
python scripts/01_veto_listesini_cek.py
python scripts/02_dogrula.py
python scripts/03_mutabakat.py
python scripts/04_web_verisi.py
python scripts/05_bekleyen_kayitlar.py   # isteğe bağlı: yayımlanmayı bekleyen GK tutanakları
python scripts/06_onizleme_gorseli.py    # paylaşım önizleme görseli (web/onizleme.png)
```

Son komuttan sonra `web/index.html` dosyasına çift tıklayarak siteyi açabilirsiniz: giriş sayfası hikâyedir
(`web/hikaye.html`), atlasın kendisi `web/vetolar.html`.
Sunucu gerekmez; veri `web/veri.js` dosyasına gömülüdür.

`01` betiği kaynağı indirir, ham kopyasını `data/raw/` altına tarihli olarak arşivler ve
`data/processed/vetolar.json` ile `vetolar.csv` dosyalarını üretir. Ayrıştırılamayan her
satır `data/review/inceleme.csv` dosyasına düşer; hiçbir satır sessizce atılmaz.

## Klasör yapısı

```
veto_atlasi/parser.py          Ayrıştırma mantığı (tek doğruluk kaynağı)
veto_atlasi/kaynak.py          Ham dosyayı bayt bayt arşivleme ve SHA-256 doğrulama
veto_atlasi/konu.py            Konu sınıflandırması ve Türkçe başlıklar
scripts/01_veto_listesini_cek.py   İndir + arşivle + ayrıştır
scripts/02_dogrula.py          Şema, mükerrer ve sayım kontrolleri
scripts/03_mutabakat.py        Referans kaynakla mutabakat + oy dağılımı
web/index.html                 Giriş: hikâyeye yönlendirir (yedek: yerel açılış; sunucuda kökü web/_redirects yönlendirir)
web/hikaye.html                Yedi adımlı anlatı (sayılar veri setinden canlı)
web/vetolar.html               Atlas: grafik, filtreler ve kayıtlar (tek dosya, kütüphanesiz)
web/hakkinda.html              Hakkında: yöntemin sade özeti, bilinen sınırlar, iletişim, lisans ve Zenodo arşivi
web/veri/                      İndirilebilir veri (vetolar.csv/xlsx/json, genel_kurul_tartismalari.csv/xlsx); 04 üretir
scripts/04_web_verisi.py       Konu, Genel Kurul tartışmaları + mutabık veriden web/veri.js üretir
scripts/05_bekleyen_kayitlar.py  Resmî tutanağı bekleyen GK toplantılarını belge sisteminde arar (veriyi değiştirmez)
scripts/06_onizleme_gorseli.py   web/veri.js'ten paylaşım önizleme görseli (Open Graph) üretir
veto_atlasi/genel_kurul.py     Genel Kurul tartışmaları (A/RES/76/262) ve Konsey özel raporları
kaynaklar/                     Referans tablo, gerekçeli düzeltmeler, kaynak notları,
                               gündem sözlüğü (gundem_sozlugu.csv), konu düzeltmeleri,
                               genel_kurul_tartismalari.csv, ozel_raporlar.csv
kaynaklar/.belgeler/           Yerel belgeler (toplantı kaydı PDF'leri); depoya girmez, künye ve SHA-256
                               KAYNAKLAR.md'de, indirme: scripts/07_belgeleri_indir.py
scripts/07_belgeleri_indir.py  Yerel belgeleri KAYNAKLAR.md tablosundan indirir, özetini doğrular
scripts/08_paylasim_kartlari.py  Veri setinden ve alıntı bankasından iki dilli paylaşım kartları (web/kartlar/,
                               HTML + PNG; PNG için makinedeki Edge/Chrome başsız modda); katalog kaynaklar/kart_katalogu.md
scripts/09_temsil.py             Temsil endeksi: BM bölgesel grupları, P5 ve İİT için nüfus, üye, bütçe, barış gücü ve
                                 koltuk payları (kaynaklar/temsil/*.csv -> data/processed/temsil.json, web/temsil_veri.js;
                                 --girdi ham kaynaklardan CSV üretir)
scripts/10_tek_dosya.py          Tek dosyalık inceleme sürümü: sekiz sayfa yedi sekmede, veri ve yazı tipleri gömülü
                                 (web/veto-atlasi-tek-dosya.html; 04 de üretir)
scripts/11_cevrimdisi.py         İnternetsiz çalışma: web/cevrimdisi.js (service worker; 04 de üretir)
scripts/12_site_haritasi.py      Site haritası: web/sitemap.xml (sayfalar TR/EN ve açık veri; lastmod git kaydından)
schema/veto_kaydi.schema.json  Her kaydın uyması gereken yapı
tests/                         Birim testleri ve veri seti değişmezleri
data/raw | processed | review  Ham kaynak, işlenmiş veri, elle kontrol listesi
METODOLOJI.md                  Tanımlar, sayım kuralları, sınırlar (asıl metin)
METODOLOJI_EN.md               İngilizce çevirisi; 04 ikisinden web/metodoloji.html üretir
kaynaklar/alintilar.csv        Alıntı bankası; doğrulaması kaynaklar/alintilar_dogrulama.csv (veto_atlasi/alinti.py)
web/vizyon.html                Söz ve Kayıt: alıntılar ve veri setinden hesaplanan karşılıkları
web/reform.html                Reform modelleri: dört Güvenlik Konseyi reform modeli aynı dört ölçütle
web/fonts/                     Gömülü yazı tipleri ve OFL lisansları (üçüncü taraf istek yok)
web/404.html                   Bulunamayan adres sayfası (iki dilli, arama motorlarına kapalı)
web/_redirects                 Sunucu yönlendirmesi: / -> /hikaye (302, sorgu korunur; Workers statik varlıkları)
web/_headers                   Sunucu başlıkları: .txt ve açık veri CSV'leri charset=utf-8
web/robots.txt, sitemap.xml    Arama motorları: kartlar ve tek dosya taranmaz; site haritası (12 üretir)
web/cevrimdisi.js              İnternetsiz çalışma (service worker; elle düzenlenmez, 11 ve 04 üretir)
wrangler.jsonc                 Cloudflare yayını: web/ statik varlık olarak, bulunamayan adreste web/404.html
```

## Lisans ve atıf

Kod MIT lisansıyla (`LICENSE`), atlasın veri derlemesi CC BY 4.0 lisansıyla (`LICENSE-DATA`) yayımlanır. Alıntılar,
WPP 2024 nüfus verisi, Sievers ve Daws tablosundan alınan oy dağılımları ve yazı tipleri kendi lisans ve koşullarına
tabidir (`LICENSE-DATA`; sitedeki kopyası `web/LICENSE-DATA.txt`, ikisi aynı tutulur). Atıf bilgisi: `CITATION.cff`. Yayın adresi: https://vetoatlas.com

## Yol haritası

1. Resmi veto veri seti (DHL listesi), doğrulama ve scprocedure ile mutabakat  ✓
   Tarih farkları ve oy eşleşmeleri toplantı kayıtlarından doğrulandı ✓
2. Oy dağılımlarının ve belge bağlantılarının UN Digital Library'den eklenmesi
3. 2022 sonrası Genel Kurul veto tartışmalarının (A/RES/76/262) bağlanması ✓
4. Gizli veto ve eylemsizlik kategorileri için ayrı, kaynaklı veri setleri
5. Vaka analizleri (seçim ölçütü METODOLOJI.md'de)
6. İnteraktif arayüz: ilk ekran (zaman çizelgesi + kayıt listesi) ✓, Türkçe başlıklar ve
   konulara göre görünüm ✓, sonra EN ve AR
