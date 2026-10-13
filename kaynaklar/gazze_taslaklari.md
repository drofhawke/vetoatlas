# Ekim 2023 sonrası Gazze ile ilgili vetolar: seçim kuralı

`gazze_taslaklari.csv` listesi şu kuralla üretildi (10 Ekim 2026):

1. Aday: oylama günü 7 Ekim 2023 ya da sonrası olan bütün vetolar (17 kayıt).
2. Her adayın karar taslağı BM belge sisteminden (documents.un.org, İngilizce) indirildi ve
   metin katmanında "Gaza" sözcüğü sayıldı. Sözcük geçen taslaklar listeye girdi; sayı
   `gazze_gecis` sütunundadır.
3. Sonuç: 9 veto. Hepsinin gündemi "The situation in the Middle East, including the Palestinian
   question". Aynı dönemdeki öbür vetoların taslaklarında "Gaza" geçmiyor; bunlar arasında
   18 Nisan 2024 Filistin üyelik başvurusu taslağı (S/2024/312) da var.
4. 22 Aralık 2023 vetosu taslağın kendisine değil, S/2023/1029'a toplantıda sözlü olarak önerilen
   değişikliğe yöneliktir (S/PV.9520 s. 4-5). DHL listesi bunu "oral amendment" olarak gösterir.
   `veto_hedefi` sütunu bu kayıtta `sozlu_degisiklik`, ötekilerde `taslak` değerini taşır; 04 bu
   işareti veri setindeki kısmi veto işareti ve "oral amendment" notuyla karşılaştırır.

Bu dosya `scripts/04_web_verisi.py` tarafından okunur; listede veri setinde olmayan bir kimlik
ya da kayıttakinden farklı bir taslak varsa 04 durur.
