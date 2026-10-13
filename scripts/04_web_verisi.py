"""
Adım 4: Mutabık veri setinden arayüzün okuyacağı web/veri.js dosyasını üretir.

    python scripts/04_web_verisi.py

Veri bir .js dosyasına gömülür; böylece web/index.html (hikâye) çift tıklanarak,
sunucu kurmadan tarayıcıda açılabilir.

Konu sınıflandırması ve Türkçe başlıklar burada eklenir:
  kaynaklar/gundem_sozlugu.csv    -> başlık bazında Türkçe çeviri, konu, bölge
  kaynaklar/konu_duzeltmeleri.csv -> kayıt bazında konu ve ikincil konular
Sözlükte olmayan bir başlık gelirse uyarı verilir ve kaydın konusu "Sınıflandırılmadı" olur.

Genel Kurul tartışmaları (A/RES/76/262) da burada eklenir:
  kaynaklar/genel_kurul_tartismalari.csv, kaynaklar/ozel_raporlar.csv

Açık veri (her çalıştırmada yeniden yazılır; SHA-256 değerleri veri.js'e girer):
  web/veri/vetolar.json, web/veri/vetolar.csv, web/veri/genel_kurul_tartismalari.csv
"""
import copy
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

from veto_atlasi.genel_kurul import genel_kurul_ekle, raporlari_oku, tartismalari_oku  # noqa: E402
from veto_atlasi.kaynak import kaynak_dogrula  # noqa: E402
from veto_atlasi import alinti, metodoloji, tek_dosya  # noqa: E402
from veto_atlasi.konu import (  # noqa: E402
    KONULAR, SINIFLANDIRILMADI, duzeltmeleri_oku, konu_dagilimi, siniflandir, sozluk_oku,
)

REF_SON_TARIH = "2025-09-18"
KONULAR_EN = KOK / "kaynaklar/konular_en.csv"


def konular_en_oku() -> dict[str, str]:
    with open(KONULAR_EN, encoding="utf-8", newline="") as f:
        harita = {s["konu"]: s["konu_en"] for s in csv.DictReader(f)}
    eksik = set(KONULAR + [SINIFLANDIRILMADI]) - set(harita)
    if eksik:
        raise ValueError(f"konular_en.csv'de İngilizce karşılığı olmayan konu: {sorted(eksik)}")
    return harita


def belge_url(kod: str) -> str:
    return "https://undocs.org/" + re.sub(r"\s+", "", kod)


def undocs(kod: str) -> str:
    return "https://undocs.org/" + kod


def gk_web(t: dict) -> dict:
    """Bir Genel Kurul tartışmasının arayüzde gösterilecek hâli."""
    return {
        "id": t["id"], "tur": t["tur"], "oturum": t["oturum"], "gundem": t["gundem_maddesi"], "tarihler": t["tarihler"],
        "kayitlar": [{"kod": r["kod"], "url": undocs(r["kod"]), "durum": r["durum"]} for r in t["toplanti_kayitlari"]],
        "kararlar": [{"kod": r, "url": undocs(r)} for r in t["kabul_edilen_kararlar"]],
        "konusmacilar": t["konusmacilar"],
        "dogrulama": t["dogrulama"], "dogrulamaKaynagi": t["dogrulama_kaynagi"],
    }


def ceviri_eksikleri(kayitlar: list[dict], konu_duzeltmeleri: dict, duzeltme_satirlari: list[dict]) -> list[str]:
    """Türkçe asıl metinlerin İngilizce karşılığı eksikse uyarı listesi döndürür."""
    uyarilar = []
    for i, s in enumerate(duzeltme_satirlari, start=2):
        if not (s.get("aciklama_en") or "").strip():
            uyarilar.append(f"duzeltmeler.csv satır {i}: açıklamanın İngilizcesi (aciklama_en) eksik")
    for kid, d in konu_duzeltmeleri.items():
        if not d.get("gerekce_en"):
            uyarilar.append(f"konu_duzeltmeleri.csv {kid}: gerekçenin İngilizcesi (gerekce_en) eksik")
    for k in kayitlar:
        en = k.get("notlar_en") or []
        for j, n in enumerate(k.get("notlar") or []):
            if j >= len(en) or not en[j]:
                uyarilar.append(f"{k['id']}: notun İngilizcesi eksik: {n[:70]}")
        if k.get("duzeltme") and not k.get("duzeltme_en"):
            uyarilar.append(f"{k['id']}: mutabakat açıklamasının İngilizcesi eksik")
    return uyarilar


def gazze_oku(kayitlar: list[dict]) -> list[dict]:
    """
    Ekim 2023 sonrası Gazze ile ilgili vetolar (seçim kuralı: kaynaklar/gazze_taslaklari.md).
    Döndürür: [{id, hedef}]; hedef "taslak" ya da "sozlu_degisiklik" (veto taslağa verilen sözlü
    değişiklik önergesine yönelik; böyle bir kayıt veri setinde kısmi veto olarak işaretli olmalı).
    """
    idx = {k["id"]: k for k in kayitlar}
    with open(KOK / "kaynaklar/gazze_taslaklari.csv", encoding="utf-8", newline="") as f:
        satirlar = list(csv.DictReader(f))
    for s in satirlar:
        k = idx.get(s["id"])
        if not k or s["taslak"] not in k["taslak_belgeler"] or s["toplanti"] not in k["toplanti_kayitlari"]:
            raise ValueError(f"gazze_taslaklari.csv: {s['id']} veri setiyle uyuşmuyor")
        if k["tarih"] < "2023-10-07" or int(s["gazze_gecis"]) < 1:
            raise ValueError(f"gazze_taslaklari.csv: {s['id']} seçim kuralına uymuyor")
        if s["veto_hedefi"] not in {"taslak", "sozlu_degisiklik"} or (s["veto_hedefi"] == "sozlu_degisiklik") != bool(
                k.get("kismi_veto_suphesi") and any("oral amendment" in n for n in k.get("notlar_en") or [])):
            raise ValueError(f"gazze_taslaklari.csv: {s['id']} veto_hedefi veri setindeki notla uyuşmuyor")
    return [{"id": s["id"], "hedef": s["veto_hedefi"]} for s in satirlar]


def reform_oku() -> list[dict]:
    """Reform modelleri karşılaştırması (birincil belgeler, kaynaklar/KAYNAKLAR.md)."""
    with open(KOK / "kaynaklar/reform_modelleri.csv", encoding="utf-8", newline="") as f:
        satirlar = list(csv.DictReader(f))
    olcutler = {"toplam", "yeni_daimi", "veto", "genel_kurul"}
    for model in {s["model"] for s in satirlar}:
        if {s["olcut"] for s in satirlar if s["model"] == model} != olcutler:
            raise ValueError(f"reform_modelleri.csv: {model} için ölçütler eksik")
    return satirlar


def paket_olustur(veri: dict, sozluk: dict, duzeltmeler: dict, sema: dict, sha: str,
                  tartismalar: list | None = None, raporlar: dict | None = None) -> tuple[dict, list[str], list[dict]]:
    """Döndürür: (veri.js paketi, uyarılar, sınıflandırılmış kayıtlar). Şemaya uymayan kayıt ValueError verir."""
    if tartismalar is None:
        tartismalar = tartismalari_oku(KOK / "kaynaklar/genel_kurul_tartismalari.csv")
    if raporlar is None:
        raporlar = raporlari_oku(KOK / "kaynaklar/ozel_raporlar.csv")
    kayitlar = copy.deepcopy(veri["kayitlar"])
    uyarilar = siniflandir(kayitlar, sozluk, duzeltmeler)
    uyarilar += genel_kurul_ekle(kayitlar, tartismalar, raporlar)
    with open(KOK / "kaynaklar/duzeltmeler.csv", encoding="utf-8", newline="") as f:
        uyarilar += ceviri_eksikleri(kayitlar, duzeltmeler, list(csv.DictReader(f)))
    tartisma_idx = {t["id"]: t for t in tartismalar}

    dogrulayici = Draft202012Validator(sema)
    hatalar = [f"{k['id']}: {h.message}" for k in kayitlar for h in dogrulayici.iter_errors(k)]
    if hatalar:
        raise ValueError("Şemaya uymayan kayıt:\n  " + "\n  ".join(hatalar))

    cikti = []
    for k in kayitlar:
        belgeler = []
        for kod in list(dict.fromkeys(k["taslak_belgeler"] + k["toplanti_kayitlari"])):
            belgeler.append({"kod": kod, "url": belge_url(kod),
                             "tur": "toplanti" if kod.upper().startswith("S/PV") else "taslak"})

        # Toplantı kaydıyla doğrulanan alanlar etiketten çıkar; doğrulanamayanlar nedeniyle birlikte kalır.
        td = k.get("toplanti_dogrulamasi") or {}
        # Her doğrulama mesajı ve not iki dilde (tr, en); Türkçe asıl metindir.
        notlar = k.get("notlar") or []
        notlar_en = (k.get("notlar_en") or []) + [None] * len(notlar)
        en_karsiligi = dict(zip(notlar, notlar_en))
        dogrulama = []
        tarih_d = td.get("tarih")
        if k.get("referans_tarih") and not (tarih_d and tarih_d["durum"] == "dogrulandi"):
            dogrulama.append({
                "tr": f"Tarih iki kaynakta farklı: DHL {k['tarih']}, referans tablo {k['referans_tarih']}. "
                      + (tarih_d["aciklama"] if tarih_d else "Oylama günü toplantı kaydından doğrulanacak."),
                "en": f"The two sources give different dates: DHL {k['tarih']}, reference table {k['referans_tarih']}. "
                      + ((en_karsiligi.get(tarih_d["aciklama"]) or tarih_d["aciklama"]) if tarih_d
                         else "The voting day is to be verified from the meeting record."),
            })
        if not k.get("oy_dagilimi") and not k.get("atif_belirsiz"):
            if k["tarih"] > REF_SON_TARIH:
                dogrulama.append({"tr": "Oy dağılımı henüz eklenmedi; referans tablo Eylül 2025'e kadar uzanıyor.",
                                  "en": "Vote breakdown not yet added; the reference table runs to September 2025."})
            else:
                dogrulama.append({"tr": "Aynı gün birden fazla veto var; oy dağılımı toplantı kaydından eşleştirilecek.",
                                  "en": "Several vetoes on the same day; the vote breakdown is to be matched from the meeting record."})
        if (k.get("oy_dagilimi") or {}).get("not"):
            dogrulama.append({"tr": "Referans tablodaki oy toplamı 15'i aşıyor; doğru dağılım toplantı kaydından teyit edilecek.",
                              "en": "The vote total in the reference table exceeds 15; the breakdown is to be confirmed from the meeting record."})
        if (k.get("duzeltme") or "").startswith("üye eklendi") and "uye" not in td:
            dogrulama.append({"tr": "Eklenen ret oyunun aynı gündeki hangi oylamaya ait olduğu toplantı kaydından doğrulanacak.",
                              "en": "Which vote on that day the added negative vote belongs to is to be verified from the meeting record."})

        # Doğrulama kaynağı: aynı toplantı kaydı ve sayfaya dayanan alanlar tek satırda
        kaynaklar: dict[tuple, list[str]] = {}
        for alan in ("tarih", "oy", "uye"):
            v = td.get(alan)
            if v and v["durum"] == "dogrulandi":
                kaynaklar.setdefault((v["toplanti"], v["sayfa"], v.get("paragraf") or "", v["kaynak_url"]), []).append(alan)
        dogrulama_kaynagi = [
            {"alanlar": adlar, "toplanti": toplanti, "sayfa": sayfa, "paragraf": paragraf or None, "url": url}
            for (toplanti, sayfa, paragraf, url), adlar in kaynaklar.items()
        ]

        gk = k["genel_kurul"]
        gk_cikti = None if gk["durum"] == "kapsam_disi" else {
            "durum": gk["durum"],
            "ozelRapor": {"kod": gk["ozel_rapor"], "url": undocs(gk["ozel_rapor"])} if gk["ozel_rapor"] else None,
            "tartismalar": [gk_web(tartisma_idx[i]) for i in gk["tartismalar"]],
        }

        gundem = k["gundem_maddesi"]
        cikti.append({
            "id": k["id"],
            "tarih": k["tarih"],
            "gundem": gundem,
            "gundemTr": k["gundem_tr"],
            "konu": k["konu_kategorisi"],
            "ikincil": k["ikincil_konular"],
            "bolge": k["bolge"],
            "uyeler": k["veto_eden_uyeler"],
            "oy": k.get("oy_dagilimi"),
            "belgeler": belgeler,
            # Doğrulama mesajında zaten geçen not (ör. "doğrulanamadı" gerekçesi) ikinci kez gösterilmez
            "notlar": [{"tr": n, "en": e} for n, e in zip(notlar, notlar_en)
                       if not any(n in m["tr"] for m in dogrulama)],
            "duzeltme": k.get("duzeltme"),
            "duzeltmeEn": k.get("duzeltme_en"),
            "dogrulama": dogrulama,
            "dogrulamaKaynagi": dogrulama_kaynagi,
            "kapali": bool(k.get("atif_belirsiz")),
            "kismi": bool(k.get("kismi_veto_suphesi")),
            "onSoru": bool(k.get("on_soru_vetosu")),
            "uyelik": bool(re.search(r"membership|admission of new members", gundem, re.I)),
            "gk": gk_cikti,
        })

    meta = veri["meta"]
    siniflanmamis = any(k["konu"] == SINIFLANDIRILMADI for k in cikti)
    paket = {
        "meta": {
            "kaynak_dosya": meta.get("kaynak_dosya"),
            "kaynak_url": kaynak_kaydi().get("Adres"), "kaynak_indirme": kaynak_kaydi().get("İndirme zamanı"),
            "kaynak_sha256": sha,
            "mutabakat_zamani": meta.get("mutabakat_zamani"),
            "kayit_sayisi": len(cikti),
            "konular": KONULAR + ([SINIFLANDIRILMADI] if siniflanmamis else []),
            "konularEn": konular_en_oku(),
        },
        "kayitlar": cikti,
    }
    return paket, uyarilar, kayitlar


ACIK_VERI = KOK / "web" / "veri"
CSV_ALANLARI = ["id", "tarih", "tarih_ham", "referans_tarih", "gundem_maddesi", "gundem_tr", "konu_kategorisi",
                "ikincil_konular", "bolge", "veto_eden_uyeler", "kapali_oturum", "oy_lehte", "oy_aleyhte", "oy_cekimser",
                "taslak_belgeler", "toplanti_kayitlari", "kismi_veto_suphesi", "on_soru_vetosu", "taslak_kaynagi",
                "toplanti_dogrulamasi", "genel_kurul_durum", "ozel_rapor", "genel_kurul_tartismalari", "duzeltme", "duzeltme_en", "notlar", "notlar_en"]


def csv_satiri(k: dict) -> dict:
    oy = k.get("oy_dagilimi") or {}
    td = k.get("toplanti_dogrulamasi") or {}
    gk = k.get("genel_kurul") or {}
    return {
        "id": k["id"], "tarih": k["tarih"], "tarih_ham": k["tarih_ham"], "referans_tarih": k.get("referans_tarih") or "",
        "gundem_maddesi": k["gundem_maddesi"], "gundem_tr": k.get("gundem_tr") or "",
        "konu_kategorisi": k.get("konu_kategorisi") or "", "ikincil_konular": "; ".join(k.get("ikincil_konular") or []),
        "bolge": k.get("bolge") or "", "veto_eden_uyeler": "; ".join(k["veto_eden_uyeler"]),
        "kapali_oturum": k.get("atif_belirsiz", False),
        "oy_lehte": oy.get("lehte", ""), "oy_aleyhte": oy.get("aleyhte", ""), "oy_cekimser": oy.get("cekimser", ""),
        "taslak_belgeler": "; ".join(k["taslak_belgeler"]), "toplanti_kayitlari": "; ".join(k["toplanti_kayitlari"]),
        "kismi_veto_suphesi": k.get("kismi_veto_suphesi", False), "on_soru_vetosu": k.get("on_soru_vetosu", False),
        "taslak_kaynagi": k.get("taslak_kaynagi") or "",
        "toplanti_dogrulamasi": "; ".join(f"{a}: {v['durum']} ({v['toplanti']}" + (f", par. {v['paragraf']}" if v.get("paragraf") else "")
                                         + (f", s. {v['sayfa']}" if v.get("sayfa") else "") + ")"
                                         for a, v in td.items()),
        "genel_kurul_durum": gk.get("durum") or "", "ozel_rapor": gk.get("ozel_rapor") or "",
        "genel_kurul_tartismalari": "; ".join(gk.get("tartismalar") or []),
        "duzeltme": k.get("duzeltme") or "", "duzeltme_en": k.get("duzeltme_en") or "",
        "notlar": " | ".join(k.get("notlar") or []), "notlar_en": " | ".join(e or "" for e in k.get("notlar_en") or []),
    }


def acik_kayit(k: dict) -> dict:
    """
    Açık veri kaydı. belge_linkleri DHL sayfasındaki bağlantılar yerine belge kodlarından kurulur:
    DHL'deki beş bağlantı bozuk (kaynaklar/hata_bildirimi.md, DHL iletisi). Ham bağlantılar
    data/processed/ altında kaynaktaki hâliyle durur.
    """
    k = dict(k)
    k["belge_linkleri"] = [belge_url(kod) for kod in dict.fromkeys(k["taslak_belgeler"] + k["toplanti_kayitlari"])]
    return k


def kaynak_kaydi() -> dict:
    """data/raw/KAYNAK.md tablosu: Adres, İndirme zamanı, SHA-256 (Hakkında sayfasındaki kaynak maddesi için)."""
    s = (KOK / "data/raw/KAYNAK.md").read_text(encoding="utf-8")
    return {m[1].strip(): m[2].strip().strip("`") for m in re.finditer(r"^\| ([^|]+) \| ([^|]+) \|$", s, re.M)}


def acik_veri_yaz(kayitlar: list[dict], meta: dict) -> list[dict]:
    """web/veri/ altına indirilebilir dosyaları yazar; her biri için boyut ve SHA-256 döndürür."""
    ACIK_VERI.mkdir(parents=True, exist_ok=True)
    surum = (meta.get("mutabakat_zamani") or "")[:10]
    icerik = {
        "vetolar.json": json.dumps({
            "meta": {"ad": "Veto Atlası veri seti", "veri_surumu": surum, "kayit_sayisi": len(kayitlar),
                     "kaynak_dosya": meta.get("kaynak_dosya"), "kaynak_sha256": meta.get("kaynak_sha256"),
                     "sema": "schema/veto_kaydi.schema.json"},
            "kayitlar": [acik_kayit(k) for k in sorted(kayitlar, key=lambda k: (k["tarih"], k["id"]))],
        }, ensure_ascii=False, indent=1).encode("utf-8"),
        "genel_kurul_tartismalari.csv": (KOK / "kaynaklar/genel_kurul_tartismalari.csv").read_bytes(),
    }
    tampon = io.StringIO()
    w = csv.DictWriter(tampon, fieldnames=CSV_ALANLARI, lineterminator="\n")
    w.writeheader()
    for k in sorted(kayitlar, key=lambda k: (k["tarih"], k["id"])):
        w.writerow(csv_satiri(k))
    icerik["vetolar.csv"] = ("\ufeff" + tampon.getvalue()).encode("utf-8")  # BOM: Excel Türkçe karakterleri doğru açsın
    dosyalar = []
    for ad in ("vetolar.csv", "vetolar.json", "genel_kurul_tartismalari.csv"):
        (ACIK_VERI / ad).write_bytes(icerik[ad])
        dosyalar.append({"dosya": f"veri/{ad}", "bayt": len(icerik[ad]), "sha256": hashlib.sha256(icerik[ad]).hexdigest()})
    return dosyalar


def istatistik(kayitlar: list[dict]) -> dict:
    """Hakkında sayfası için: toplantı kaydından doğrulanan kayıtlar ve kaynaklarda bulunan hatalar."""
    dogrulanan = sum(1 for k in kayitlar if any(v["durum"] == "dogrulandi" for v in (k.get("toplanti_dogrulamasi") or {}).values()))
    dogrulanamayan = sum(1 for k in kayitlar if any(v["durum"] == "dogrulanamadi" for v in (k.get("toplanti_dogrulamasi") or {}).values()))
    # Hata sayıları kaynaklar/hata_bildirimi.md tablolarından (1. bölüm DHL, 2. bölüm scprocedure)
    bolum, hatalar = None, {"dhl": 0, "scprocedure": 0}
    for satir in (KOK / "kaynaklar/hata_bildirimi.md").read_text(encoding="utf-8").splitlines():
        if satir.startswith("## 1."):
            bolum = "dhl"
        elif satir.startswith("## 2."):
            bolum = "scprocedure"
        elif satir.startswith("## "):
            bolum = None  # 3. bölüm (gönderim kaydı) sayılmaz; bozuk bağlantı tablosunun satırları simgeyle başlar, sayılmaz
        elif bolum and re.match(r"^\| ?\d", satir):
            hatalar[bolum] += 1
    return {"toplanti_kaydindan_dogrulanan": dogrulanan, "dogrulanamayan": dogrulanamayan, "kaynak_hatalari": hatalar}


def main():
    veri = json.loads((KOK / "data/processed/vetolar_mutabik.json").read_text(encoding="utf-8"))
    try:
        yol, sha = kaynak_dogrula(KOK, veri["meta"], yoksa_kayitli=True)
        if yol is None:
            print("Not: ham dosya yerelde yok; kayıtlı özet kullanıldı (künye: data/raw/KAYNAK.md)")
        paket, uyarilar, kayitlar = paket_olustur(
            veri,
            sozluk_oku(KOK / "kaynaklar/gundem_sozlugu.csv"),
            duzeltmeleri_oku(KOK / "kaynaklar/konu_duzeltmeleri.csv"),
            json.loads((KOK / "schema/veto_kaydi.schema.json").read_text(encoding="utf-8")),
            sha,
        )
    except ValueError as e:
        sys.exit(f"HATA: {e}")

    paket["meta"]["veri_surumu"] = (veri["meta"].get("mutabakat_zamani") or "")[:10]
    paket["meta"]["indirmeler"] = acik_veri_yaz(kayitlar, paket["meta"])
    paket["meta"]["istatistik"] = istatistik(kayitlar)
    # Alıntı bankası: metinde (ya da doğrulama kaydında) bulunmayan hiçbir alıntı sisteme giremez
    alintilar, alinti_hatalari, yontem = alinti.dogrula(KOK)
    if alinti_hatalari:
        sys.exit("HATA: alıntı doğrulanamadı:\n  " + "\n  ".join(alinti_hatalari))
    paket["alintilar"] = alintilar
    try:
        paket["gazze"] = gazze_oku(kayitlar)
        paket["reformModelleri"] = reform_oku()
    except ValueError as e:
        sys.exit(f"HATA: {e}")
    hedef = KOK / "web" / "veri.js"
    hedef.parent.mkdir(exist_ok=True)
    hedef.write_text("window.VETO_VERISI = " + json.dumps(paket, ensure_ascii=False) + ";\n", encoding="utf-8")

    print(f"Kaynak  : {veri['meta']['kaynak_dosya']}")
    print(f"SHA-256 : {sha}\n")
    print("Konu (yalnızca ana konu sayılır)        Öneri  Oy  İkincil")
    for konu, d in konu_dagilimi(kayitlar).items():
        print(f"  {konu:38} {d['oneri']:5} {d['oy']:4} {d['ikincil'] or '':>7}")
    for u in uyarilar:
        print(f"UYARI: {u}")
    print(f"\n{len(paket['kayitlar'])} kayıt -> {hedef.relative_to(KOK)}")
    for f in paket["meta"]["indirmeler"]:
        print(f"Açık veri: web/{f['dosya']}  {f['bayt']} bayt  SHA-256 {f['sha256'][:16]}…")
    # METODOLOJI.md ve çevirisinden iki dilli metodoloji sayfası
    sayfa, md_uyarilari = metodoloji.yaz(KOK)
    for u in md_uyarilari:
        print(f"UYARI: {u}")
    print(f"Metodoloji: {sayfa.relative_to(KOK)}")
    print(f"Alıntılar: {len(alintilar)} alıntı, doğrulama {yontem}")
    # Tek dosyalık inceleme sürümü (altı sayfa, veri ve yazı tipleri gömülü)
    tek = tek_dosya.uret(KOK)
    print(f"Tek dosya: {tek.relative_to(KOK)} ({tek.stat().st_size / 1e6:.2f} MB)")
    # Paylaşım kartları veri setinin belirli bir sürümüne dayanır; veri değiştiyse yeniden üretilmeli
    kart_manifesti = KOK / "web/kartlar/kartlar.json"
    if kart_manifesti.exists():
        if json.loads(kart_manifesti.read_text(encoding="utf-8")).get("kaynak_sha256") != sha:
            print("UYARI: web/kartlar/ eski veri setine dayanıyor; python scripts/08_paylasim_kartlari.py ile yeniden üretin.")
    else:
        print("Not: paylaşım kartları yok (python scripts/08_paylasim_kartlari.py).")
    print("Tarayıcıda açmak için: web/index.html (hikâye) ya da web/vetolar.html (atlas) dosyasına çift tıkla.")


if __name__ == "__main__":
    main()
