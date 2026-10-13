# Ham kaynak: DHL Güvenlik Konseyi veto listesi

| Alan | Değer |
|---|---|
| Adres | https://www.un.org/Depts/dhl/resguide/scact_veto_table_en.htm |
| Kanonik dosya | `data/raw/veto_dhl_2026-10-10.html` |
| İndirme zamanı | 2026-10-10T07:58:45+00:00 |
| Boyut | 73.235 bayt |
| SHA-256 | `b92d1fe1db9abe42dd8d864c3c88ea6a0fc8074dba39f596f4b544b93e147083` |
| Internet Archive kopyası | https://web.archive.org/web/20260912160946/https://www.un.org/depts/dhl/resguide/scact_veto_table_en.htm |
| Arşiv kopyasının ham baytları | https://web.archive.org/web/20260912160946id_/https://www.un.org/depts/dhl/resguide/scact_veto_table_en.htm |

**Arşiv kopyası.** 10 Ekim 2026'da sayfa Internet Archive'a kaydettirilmek istendi; Save Page Now
"The target server blocks access … (HTTP status=403)" yanıtını verdi, yani un.org arşivin
tarayıcısını o gün engelledi. Engel aşılmadı. Arşivde daha önce alınmış kopyalar vardır.
12 Eylül 2026 kopyasının ham baytları (`id_` adresi) 10 Ekim 2026'da indirildi: 73.235 bayt,
SHA-256 `b92d1fe1…7083`, kanonik dosyayla bayt bayt aynı. Arşivin dizinine (CDX) göre
17 Ağustos 2026 ile 16 Eylül 2026 arasındaki bütün kopyaların içerik özeti de aynıdır
(SHA-1 base32 `2VVXOS2SAUOS5TJ2XRVU7WBKFPABZRKO`; kanonik dosyanın SHA-1'i de bu değeri verir).
Arşiv adresinde `depts` küçük harfle geçer; sunucu iki yazımı da aynı sayfaya götürür.

Bu dosyayı herkes kendi indirdiği kopyayla karşılaştırabilir:
`sha256sum veto_dhl_2026-10-10.html`.

`veto_dhl_2026-10-09.html` kanonik değildir; nedeni `kaynaklar/KAYNAKLAR.md` dosyasında yazılıdır.

## Araştırma rehberindeki liste (B)

DHL Araştırma Rehberi'ndeki güncel veto listesi (https://research.un.org/en/docs/sc/quick/veto)
sayfaya bir iframe ile yüklenir; tablonun kendisi şu adresten gelir:
https://ydsftksff8.execute-api.us-east-1.amazonaws.com/dev/render_meeting_veto/sc_veto_list/EN
Kopya: `data/raw/veto_dhl_rehber_2026-10-10.html`, 10 Ekim 2026 15:15 UTC, 199.733 bayt,
SHA-256 `73a298a56a0c1caf8d32177dc8f95f2d2ebdc6d1af6cea254834b3cd56e166b3`. Bu liste canlı
üretildiği için kopyanın özeti ileride alınacak kopyalarla aynı olmayabilir.
