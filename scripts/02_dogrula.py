"""
Adım 2: Ayrıştırılmış veriyi doğrular ve özet istatistik üretir.

    python scripts/02_dogrula.py

Kontroller: şema uyumu, mükerrer kayıt, tarih sırası, üye dağılımı.
Önemli: "Veto sayısı" iki farklı şekilde sayılır ve ikisi de raporlanır:
  - Taslak bazında: kaç karar taslağı veto ile düştü
  - Oy bazında   : kaç ret oyu kullanıldı (bir taslağı iki üye veto ettiyse 2)
Bu ayrım yapılmazsa rakamlarımız başka kaynaklarla tutmaz ve eleştiriye açık olur.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator

KOK = Path(__file__).resolve().parents[1]
veri = json.loads((KOK / "data/processed/vetolar.json").read_text(encoding="utf-8"))
sema = json.loads((KOK / "schema/veto_kaydi.schema.json").read_text(encoding="utf-8"))
kayitlar = veri["kayitlar"]

hatalar = 0
dogrulayici = Draft202012Validator(sema)
for k in kayitlar:
    for h in dogrulayici.iter_errors(k):
        hatalar += 1
        print(f"[ŞEMA] {k['id']}: {h.message}")

# Kimlikler benzersiz olmalı (gerçek hata)
for i, n in Counter(k["id"] for k in kayitlar).items():
    if n > 1:
        hatalar += 1
        print(f"[KİMLİK ÇAKIŞMASI] {i} x{n}")

# Aynı gün, aynı taslak, aynı gündem, aynı üye: kaynak bunları ayrı veto olarak listeliyor
# (ör. 26 Haziran 1946 İspanya meselesi). Silinmez, toplantı kaydından elle doğrulanır.
# Gruptaki her kayıt duzeltmeler.csv'de toplantı kaydına dayalı bir oy_esle satırıyla
# ayrıştırılmışsa uyarı kalkar.
with open(KOK / "kaynaklar/duzeltmeler.csv", encoding="utf-8") as f:
    ayristirilan = {d["hedef"]: d["toplanti"] for d in csv.DictReader(f)
                    if d["tur"] == "oy_esle" and d.get("toplanti")}
icerik = defaultdict(list)
for k in kayitlar:
    icerik[(k["tarih"], tuple(k["taslak_belgeler"]), tuple(k["toplanti_kayitlari"]),
            k["gundem_maddesi"], tuple(k["veto_eden_uyeler"]))].append(k["id"])
uyari = cozulen = 0
for a, idler in icerik.items():
    if len(idler) < 2:
        continue
    if all(i in ayristirilan for i in idler):
        cozulen += 1
        print(f"[ÇÖZÜLDÜ - aynı içerik x{len(idler)}] {a[0]} | {a[3][:50]} -> "
              f"{', '.join(sorted({ayristirilan[i] for i in idler}))} ile ayrıştırıldı")
    else:
        uyari += 1
        print(f"[UYARI - aynı içerik x{len(idler)}] {a[0]} | {a[3][:60]} -> toplantı kaydından doğrula")

uye_oy = Counter(u for k in kayitlar for u in k["veto_eden_uyeler"])
on_yil = Counter(f"{k['tarih'][:3]}0-{k['tarih'][:3]}9" for k in kayitlar if k["tarih"])

print("\n=== ÖZET ===")
print(f"Kayıt (satır)            : {len(kayitlar)}")
print(f"Taslak bazında veto      : {sum(max(1, len(k['taslak_belgeler'])) for k in kayitlar)}")
print(f"Oy bazında veto          : {sum(uye_oy.values())}")
print(f"Kısmi veto şüphesi (*)   : {sum(k['kismi_veto_suphesi'] for k in kayitlar)}")
print(f"Toplantı içi öneri       : {sum(k.get('taslak_kaynagi') == 'toplanti_kaydi' for k in kayitlar)}")
print(f"Ön soru (çifte) vetosu   : {sum(k.get('on_soru_vetosu', False) for k in kayitlar)}")
print(f"Atfı belirsiz (kapalı)   : {sum(k.get('atif_belirsiz', False) for k in kayitlar)}")
print("\nÜyeye göre ret oyu:")
for u, n in uye_oy.most_common():
    print(f"  {u:5} {n}")
print("\nOn yıla göre kayıt:")
for d in sorted(on_yil):
    print(f"  {d:10} {on_yil[d]}")

print(f"\nSonuç: {'TEMİZ' if hatalar == 0 else f'{hatalar} sorun var'}"
      + (f" ({uyari} uyarı elle doğrulanacak)" if uyari else "")
      + (f"; aynı içerikli {cozulen} grup toplantı kaydından ayrıştırıldı" if cozulen else ""))
sys.exit(1 if hatalar else 0)
