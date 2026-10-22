"""
Adım 3: DHL veri setini scprocedure Tablo 4 ile mutabık hale getirir.

    python scripts/03_mutabakat.py

Ne yapar:
  1. Düzeltme öncesi iki kaynak arasındaki farkları tarih bazında raporlar.
  2. kaynaklar/duzeltmeler.csv içindeki gerekçeli düzeltmeleri uygular.
     (Hiçbir düzeltme kodun içine gömülü değildir; hepsi o dosyada, gerekçesiyle.)
     kaynak_url / oy / taslak sütunları doluysa (toplantı kaydı ya da referans kapsamı sonrası
     BM birincil kaynakları) onlar kullanılır; boşsa satır scprocedure Tablo 4'e dayanır.
     tarih_dogrula satırları oylama gününü toplantı kaydından sabitler; boş tarih
     "doğrulanamadı" demektir ve nedeni gerekçede yazar.
  3. Eşleşebilen kayıtlara genel oy dağılımını (lehte-aleyhte-çekimser) ekler.
  4. Düzeltme sonrası toplamları referansla karşılaştırır.

Notlar ve mutabakat açıklamaları Türkçe yazılır (asıl metin); her birinin İngilizcesi yanında
tutulur (notlar_en, duzeltme_en). Kaynaklar: duzeltmeler.csv "aciklama_en" sütunu ve ayrıştırıcının
sabit notları için kaynaklar/notlar_en.csv. Karşılığı olmayan not için notlar_en'de null kalır;
04 betiği bunu uyarı olarak bildirir.

Çıktılar:
  data/processed/vetolar_mutabik.json / .csv
  data/review/oy_eslesmeyen.csv   -> oy dağılımı elle eşleştirilecek kayıtlar
"""
import copy
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

from veto_atlasi.kaynak import kaynak_dogrula  # noqa: E402

REF_URL = "https://www.scprocedure.org/_files/ugd/54a569_8c1ef1fee8ca4d6ab09b7fb516b55a22.pdf"
REF_SON_TARIH = "2025-09-18"  # Tablo 4 sürümünün kapsadığı son veto
# scprocedure Tablo 4 referans tablosu açık depoda dağıtılmaz (künyesi kaynaklar/KAYNAKLAR.md)
REFERANS = KOK / "kaynaklar/scprocedure_tablo4.csv"
# Ayrıştırıcının tarih aralığı notu (veto_atlasi/parser.py); oylama günü doğrulanınca kayıttan çıkar
TARIH_ARALIGI_NOTU = "DHL listesi bu oylamanın tarihini bir aralık olarak veriyor"


def oku_csv(yol):
    with open(yol, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def oy_ayir(s):
    if not s:
        return None
    l, a, c = (int(x) for x in s.split("-"))
    d = {"lehte": l, "aleyhte": a, "cekimser": c}
    if l + a + c > 15:
        d["not"] = "Kaynakta oy toplamı 15'i aşıyor; toplantı kaydından doğrulanacak."
    return d


def uye_anahtari(k):
    return ("BELIRSIZ",) if k.get("atif_belirsiz") else tuple(sorted(k["veto_eden_uyeler"]))


def main():
    if not REFERANS.exists():
        sys.exit("HATA: referans tablo depoda yok: kaynaklar/scprocedure_tablo4.csv (scprocedure Tablo 4, açık depoda "
                 "dağıtılmaz; künyesi kaynaklar/KAYNAKLAR.md). 03 bu tablo olmadan çalışmaz; mutabık veri "
                 "data/processed/vetolar_mutabik.json ve .csv dosyalarındadır.")
    veri = json.loads((KOK / "data/processed/vetolar.json").read_text(encoding="utf-8"))
    try:
        yol, sha = kaynak_dogrula(KOK, veri["meta"], yoksa_kayitli=True)
    except ValueError as e:
        sys.exit(f"HATA: {e}")
    if yol is None:
        print("Not     : ham dosya yerelde yok; kayıtlı özet kullanıldı (künye: data/raw/KAYNAK.md)")
    print(f"Kaynak  : {veri['meta']['kaynak_dosya']}")
    print(f"SHA-256 : {sha}\n")
    kayitlar = veri["kayitlar"]
    ref = oku_csv(REFERANS)
    duz = oku_csv(KOK / "kaynaklar/duzeltmeler.csv")
    for r in ref:
        r["uyeler"] = tuple(sorted(r["veto_eden_uyeler"].split(";")))

    # ---------- 1. Düzeltme öncesi fark raporu ----------
    rg, bg = defaultdict(list), defaultdict(list)
    for r in ref:
        rg[r["tarih"]].append(r)
    for k in kayitlar:
        if k["tarih"] <= REF_SON_TARIH:
            bg[k["tarih"]].append(k)
    farkli = [t for t in sorted(set(rg) | set(bg))
              if Counter(r["uyeler"] for r in rg[t]) != Counter(uye_anahtari(k) for k in bg[t])]
    print(f"Düzeltme öncesi farklı tarih sayısı: {len(farkli)}")

    # ---------- 2. Düzeltmeleri uygula ----------
    mutabik = copy.deepcopy(kayitlar)
    idx = {k["id"]: k for k in mutabik}
    sabit_en = {r["not"]: r["not_en"] for r in oku_csv(KOK / "kaynaklar/notlar_en.csv")}
    for k in mutabik:
        k.setdefault("duzeltme", None)
        k.setdefault("duzeltme_en", None)
        k.setdefault("referans_tarih", None)
        k.setdefault("toplanti_dogrulamasi", {})
        k["notlar_en"] = [sabit_en.get(n) for n in k["notlar"]]

    def not_ekle(k, tr, en):
        """Türkçe notu ve İngilizce karşılığını (yoksa None) aynı sırada ekler."""
        k["notlar"].append(tr)
        k["notlar_en"].append(en)

    def ing(d, sablon):
        """aciklama_en doluysa İngilizce şablonu doldurur, değilse None döner."""
        en = (d.get("aciklama_en") or "").strip()
        return sablon.format(en) if en else None

    def duzeltme_yaz(k, tr, en):
        k["duzeltme"], k["duzeltme_en"] = tr, en
    ref_no = {r["no"]: r for r in ref}

    def dogrulama_isle(k, alan, d, durum="dogrulandi"):
        k["toplanti_dogrulamasi"][alan] = {"durum": durum, "toplanti": d["toplanti"], "aciklama": d["aciklama"]}
        if durum == "dogrulandi":
            k["toplanti_dogrulamasi"][alan].update(sayfa=d["sayfa"], kaynak_url=d["kaynak_url"])
            # Toplantı kaydında paragraf numarası varsa birincil atıf odur; PDF sayfası yanında kalır
            if d.get("paragraf"):
                k["toplanti_dogrulamasi"][alan]["paragraf"] = d["paragraf"]

    eklenen = 0
    acik_eslesme = {}  # kayıt id -> scprocedure no (gerekçesi duzeltmeler.csv'de)
    dogrudan_oy = {}   # kayıt id -> "L-A-Ç" (BM birincil kaynağından, duzeltmeler.csv "oy" sütunu)
    for d in duz:
        tur = d["tur"]
        taslak, birincil = d.get("taslak") or "", d.get("kaynak_url") or ""
        if tur == "ekle":
            n = sum(1 for k in mutabik if k["tarih"] == d["tarih"]) + 1
            mutabik.append({
                "id": f"V-{d['tarih']}-{n}", "tarih": d["tarih"], "tarih_ham": d["tarih"],
                "tarih_aralik_mi": False, "taslak_belgeler": [t for t in taslak.split(";") if t],  # "taslak;önerge" olabilir
                "toplanti_kayitlari": [d["toplanti"]],
                "gundem_maddesi": d["konu"], "veto_eden_uyeler": d["uyeler"].split(";"),
                "kategori": "resmi_veto",
                # Kısmi veto: değişiklik önergesi ya da taslağın bir bölümüne (paragraf, kelime) ayrı oylama ("kismi" sütunu)
                "kismi_veto_suphesi": "amendment" in d["konu"].lower() or d.get("kismi") == "evet",
                # Taslak belgesi yoksa öneri toplantıda sözlü sunulmuştur (erken dönem)
                "taslak_kaynagi": "belge" if taslak else "toplanti_kaydi",
                "on_soru_vetosu": False, "atif_belirsiz": False,
                "notlar": [d["aciklama"]], "notlar_en": [ing(d, "{}")], "kaynak_url": birincil or REF_URL,
                "belge_linkleri": [birincil] if birincil else [],
                "bolge": None, "konu_kategorisi": None, "oy_dagilimi": None,
                "ga_tartisma_belgesi": None, "baglam_ozeti": None, "vaka_analizi_var": False,
                "duzeltme": (f"eklendi: scprocedure #{d['scprocedure_no']}" if d["scprocedure_no"]
                             else f"eklendi: BM birincil kaynağı ({d['toplanti']})"),
                "duzeltme_en": (f"added: scprocedure #{d['scprocedure_no']}" if d["scprocedure_no"]
                                else f"added: UN primary source ({d['toplanti']})"),
                "referans_tarih": None, "toplanti_dogrulamasi": {},
            })
            idx[mutabik[-1]["id"]] = mutabik[-1]
            if d.get("oy"):
                dogrudan_oy[mutabik[-1]["id"]] = d["oy"]
                dogrulama_isle(mutabik[-1], "oy", d)
                # Toplantı kaydı oylamada aleyhte oy verenleri sayar; ret oyu veren üyeler aynı sayfadan doğrulanır
                dogrulama_isle(mutabik[-1], "uye", d)
            else:
                acik_eslesme[mutabik[-1]["id"]] = d["scprocedure_no"]
            eklenen += 1
        elif tur == "uye_ekle":
            k = idx[d["hedef"]]
            k["veto_eden_uyeler"].append(d["uyeler"])
            not_ekle(k, d["aciklama"], ing(d, "{}"))
            duzeltme_yaz(k, f"üye eklendi ({d['uyeler']}): scprocedure #{d['scprocedure_no']}",
                         f"member added ({d['uyeler']}): scprocedure #{d['scprocedure_no']}")
            if d.get("toplanti"):
                k["duzeltme"] += f", {d['toplanti']} ile doğrulandı"
                k["duzeltme_en"] += f", verified with {d['toplanti']}"
                dogrulama_isle(k, "uye", d)
        elif tur == "bol":
            k = idx[d["hedef"]]
            taslaklar = k["taslak_belgeler"]
            k["taslak_belgeler"] = taslaklar[:1]
            duzeltme_yaz(k, f"ikiye bölündü: scprocedure #{d['scprocedure_no']}",
                         f"split in two: scprocedure #{d['scprocedure_no']}")
            not_ekle(k, d["aciklama"], ing(d, "{}"))
            yeni = copy.deepcopy(k)
            n = sum(1 for x in mutabik if x["tarih"] == k["tarih"]) + 1
            yeni["id"] = f"V-{k['tarih']}-{n}"
            yeni["taslak_belgeler"] = taslaklar[1:2]
            mutabik.append(yeni)
            idx[yeni["id"]] = yeni
            eklenen += 1
        elif tur == "oy_esle":
            k = idx[d["hedef"]]
            if taslak and taslak not in k["taslak_belgeler"]:  # oy_esle: tek taslak
                sys.exit(f"oy_esle {d['hedef']}: {taslak} bu kaydın taslakları arasında yok {k['taslak_belgeler']}")
            if d.get("oy"):
                dogrudan_oy[d["hedef"]] = d["oy"]
                # Okur notu yalnızca panelde olmayanı söyler (aleyhte ve çekimser kalanlar, oylanan bölüm);
                # oy sayısı, belge ve sayfa panelin "Genel oy" ve "Doğrulama kaynağı" satırlarındadır.
                not_ekle(k, d["aciklama"], ing(d, "{}"))
                no = d["scprocedure_no"]
                if no and ref_no[no]["oy_lehte_aleyhte_cekimser"] != d["oy"]:
                    ref_oy = ref_no[no]["oy_lehte_aleyhte_cekimser"]
                    not_ekle(k, f"Referans tablo oyu {ref_oy} veriyor; biz toplantı kaydındaki {d['oy']} sonucunu aldık "
                                f"(Tablo 4, #{no}).",
                             f"The reference table gives {ref_oy}; we follow the meeting record, which gives {d['oy']} "
                             f"(Table 4, #{no}).")
                if not k["duzeltme"]:
                    duzeltme_yaz(k, f"oy eklendi: toplantı kaydı ({d['toplanti']})",
                                 f"vote added: meeting record ({d['toplanti']})")
                dogrulama_isle(k, "oy", d)
            else:
                acik_eslesme[d["hedef"]] = d["scprocedure_no"]
                # Okur notunda iç ad yok: referans tablo numarası "(Tablo 4, #N)" olarak, açıklama numarayı zaten veriyorsa eksiz
                ek = "" if f"#{d['scprocedure_no']}" in d["aciklama"] else f" (Tablo 4, #{d['scprocedure_no']})"
                ek_en = "" if f"#{d['scprocedure_no']}" in (d.get("aciklama_en") or "") else f" (Table 4, #{d['scprocedure_no']})"
                not_ekle(k, f"{d['aciklama']}{ek}.", ing(d, f"{{}}{ek_en}."))
        elif tur == "tarih_farki":
            # Okur notu yok: tarih farkını tarih_dogrula satırının açıklaması tek notta anlatır
            # (aciklama sütunu burada yalnızca kayıt içindir).
            k = idx[d["hedef"]]
            k["referans_tarih"] = d["tarih"]
        elif tur == "tarih_dogrula":
            k = idx[d["hedef"]]
            if not d["tarih"]:
                not_ekle(k, d["aciklama"], ing(d, "{}"))
                dogrulama_isle(k, "tarih", d, "dogrulanamadi")
                continue
            # Kimlik (V-<DHL tarihi>-n) değişmez; yalnızca oylama günü düzeltilir. İki kaynağın tarihini ve
            # doğru günü açıklama sütunu yazıyla, tek notta verir (ISO tarih okur notuna yazılmaz).
            k["tarih"] = d["tarih"]
            kalan = [(n, e) for n, e in zip(k["notlar"], k["notlar_en"]) if not n.startswith(TARIH_ARALIGI_NOTU)]
            k["notlar"], k["notlar_en"] = [n for n, _ in kalan], [e for _, e in kalan]
            not_ekle(k, d["aciklama"], ing(d, "{}"))
            dogrulama_isle(k, "tarih", d)
        else:
            sys.exit(f"Bilinmeyen düzeltme türü: {tur}")

    # ---------- 3. Oy dağılımı eşleştirme ----------
    def esles_tarih(k):
        return k.get("referans_tarih") or k["tarih"]

    mg = defaultdict(list)
    for k in mutabik:
        mg[esles_tarih(k)].append(k)
    for k in mutabik:
        if k["id"] in dogrudan_oy:
            k["oy_dagilimi"] = oy_ayir(dogrudan_oy[k["id"]])
        elif k["id"] in acik_eslesme:
            k["oy_dagilimi"] = oy_ayir(ref_no[acik_eslesme[k["id"]]]["oy_lehte_aleyhte_cekimser"])
    eslesmeyen = []
    for t, grup in mg.items():
        refs = rg.get(t, [])
        if not refs:
            continue
        for k in grup:
            if k["oy_dagilimi"]:
                continue
            adaylar = [r for r in refs if r["uyeler"] == uye_anahtari(k)]
            oylar = {r["oy_lehte_aleyhte_cekimser"] for r in adaylar}
            if len(oylar) == 1 and adaylar[0]["oy_lehte_aleyhte_cekimser"]:
                k["oy_dagilimi"] = oy_ayir(adaylar[0]["oy_lehte_aleyhte_cekimser"])
            elif len(oylar) > 1:
                eslesmeyen.append({"id": k["id"], "gundem": k["gundem_maddesi"],
                                   "aday_oylar": " / ".join(sorted(oylar)),
                                   "scprocedure_no": ";".join(r["no"] for r in adaylar)})

    mutabik.sort(key=lambda k: (k["tarih"], k["id"]), reverse=True)

    # ---------- 4. Toplam kontrolü ----------
    ref_uye = Counter(u for r in ref for u in r["uyeler"] if u != "BELIRSIZ")
    sonrasi = [k for k in mutabik if k["tarih"] > REF_SON_TARIH]
    for k in sonrasi:
        ref_uye.update(k["veto_eden_uyeler"])
    biz_uye = Counter(u for k in mutabik if not k.get("atif_belirsiz") for u in k["veto_eden_uyeler"])

    print(f"Uygulanan düzeltme: {len(duz)} satır  (eklenen kayıt: {eklenen})")
    print(f"\nÖneri sayısı   : biz {len(mutabik)} | referans {len(ref) + len(sonrasi)}")
    print(f"Veto oyu       : biz {sum(biz_uye.values())} | referans {sum(ref_uye.values())}")
    print("\nÜye      Biz   Referans")
    tamam = len(mutabik) == len(ref) + len(sonrasi)
    for u in ["SSCB", "RUS", "USA", "GBR", "FRA", "CHN"]:
        isaret = "" if biz_uye[u] == ref_uye[u] else "  <-- FARK"
        tamam &= not isaret
        print(f"  {u:6} {biz_uye[u]:5} {ref_uye[u]:8}{isaret}")
    print(f"\nKapalı oturum (üye toplamı dışında): {sum(1 for k in mutabik if k.get('atif_belirsiz'))}")
    print(f"Oy dağılımı eklenen kayıt         : {sum(1 for k in mutabik if k['oy_dagilimi'])}/{len(mutabik)}")
    print(f"Oy dağılımı elle eşleşecek        : {len(eslesmeyen)} -> data/review/oy_eslesmeyen.csv")
    tarih_d = Counter(k["toplanti_dogrulamasi"].get("tarih", {}).get("durum", "bekliyor")
                      for k in mutabik if k.get("referans_tarih"))
    print(f"İki kaynakta tarihi farklı kayıt  : {sum(tarih_d.values())} "
          f"(toplantı kaydıyla doğrulanan {tarih_d['dogrulandi']}, doğrulanamayan {tarih_d['dogrulanamadi']}, "
          f"bekleyen {tarih_d['bekliyor']})")
    print(f"Toplantı kaydıyla doğrulanan oy   : {sum(1 for k in mutabik if 'oy' in k['toplanti_dogrulamasi'])}")
    print(f"\nSonuç: {'MUTABIK' if tamam else 'FARK VAR'}")

    meta = dict(veri["meta"])
    meta.update({"referans": REF_URL, "duzeltme_sayisi": len(duz), "kayit_sayisi": len(mutabik),
                 "mutabakat_zamani": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    (KOK / "data/processed/vetolar_mutabik.json").write_text(
        json.dumps({"meta": meta, "kayitlar": mutabik}, ensure_ascii=False, indent=2), encoding="utf-8")

    with open(KOK / "data/processed/vetolar_mutabik.csv", "w", newline="", encoding="utf-8-sig") as f:
        alanlar = ["id", "tarih", "referans_tarih", "taslak_belgeler", "toplanti_kayitlari",
                   "gundem_maddesi", "veto_eden_uyeler", "oy_dagilimi", "atif_belirsiz",
                   "kismi_veto_suphesi", "on_soru_vetosu", "duzeltme", "notlar"]
        w = csv.DictWriter(f, fieldnames=alanlar)
        w.writeheader()
        for k in mutabik:
            satir = {}
            for a in alanlar:
                v = k.get(a)
                if isinstance(v, list):
                    v = "; ".join(v)
                elif isinstance(v, dict):
                    v = f"{v['lehte']}-{v['aleyhte']}-{v['cekimser']}"
                satir[a] = v
            w.writerow(satir)

    with open(KOK / "data/review/oy_eslesmeyen.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["id", "gundem", "aday_oylar", "scprocedure_no"])
        w.writeheader()
        w.writerows(eslesmeyen)

    sys.exit(0 if tamam else 1)


if __name__ == "__main__":
    main()
