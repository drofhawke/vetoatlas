"""
Genel Kurulun vetolardan sonra yaptığı tartışmalar (A/RES/76/262, 26 Nisan 2022).

İki kaynak dosya, ikisi de kaynaklar/ altında:
  genel_kurul_tartismalari.csv -> her tartışma bir satır (veto girişimi tartışması ya da
                                  olağanüstü özel oturum); bir tartışma birden fazla vetoyu,
                                  bir veto birden fazla tartışmayı kapsayabilir
  ozel_raporlar.csv            -> her veto için Güvenlik Konseyinin özel raporu

Kurallar METODOLOJI.md 2.5'te.
"""

from __future__ import annotations

import csv
from pathlib import Path

KAPSAM_BASLANGICI = "2022-04-26"
TURLER = {"veto_girisimi", "olaganustu_ozel_oturum"}
KAYIT_DURUMLARI = {"resmi", "gayriresmi_transkript", "yayimlanmadi"}
KONUSTU = {"aciklama", "yalnizca_cevap_hakki", "hayir"}
DOGRULAMA = {"dogrulandi", "olasi"}
SAYI_ALANLARI = ("aciklama_uye_devlet", "aciklama_gozlemci", "grup_adina_konusan", "cevap_hakki")


def _liste(s: str | None) -> list[str]:
    return [p.strip() for p in (s or "").split(";") if p.strip()]


def tartismalari_oku(yol: Path) -> list[dict]:
    with open(yol, encoding="utf-8", newline="") as f:
        satirlar = list(csv.DictReader(f))
    tartismalar = []
    for i, s in enumerate(satirlar, start=2):
        hata = lambda m: ValueError(f"{yol.name} satır {i} ({s['tartisma_id']}): {m}")  # noqa: E731
        if s["tur"] not in TURLER:
            raise hata(f"bilinmeyen tür '{s['tur']}'")
        kayitlar, durumlar = _liste(s["toplanti_kayitlari"]), _liste(s["kayit_durumlari"])
        if len(kayitlar) != len(durumlar) or not kayitlar:
            raise hata("toplantı kayıtları ile kayıt durumları eşleşmiyor")
        if set(durumlar) - KAYIT_DURUMLARI:
            raise hata(f"bilinmeyen kayıt durumu {set(durumlar) - KAYIT_DURUMLARI}")
        if s["dogrulama"] not in DOGRULAMA or not s["dogrulama_kaynagi"].strip():
            raise hata("doğrulama ve kaynağı zorunlu")
        t = {
            "id": s["tartisma_id"], "tur": s["tur"], "oturum": s["oturum"], "gundem_maddesi": s["gundem_maddesi"],
            "tarihler": _liste(s["tarihler"]),
            "toplanti_kayitlari": [{"kod": k, "durum": d} for k, d in zip(kayitlar, durumlar)],
            "veto_idleri": _liste(s["veto_idleri"]),
            "kabul_edilen_kararlar": _liste(s["kabul_edilen_kararlar"]),
            "dogrulama": s["dogrulama"], "dogrulama_kaynagi": s["dogrulama_kaynagi"],
            "capraz_kontrol": s.get("capraz_kontrol") or "",
            "konusmacilar": None,
        }
        if s["tur"] == "veto_girisimi":
            # Konuşmacı sayıları yalnızca veto girişimi tartışmalarında tutulur
            if any(s[a] == "" for a in SAYI_ALANLARI):
                raise hata("veto girişimi tartışmasında konuşmacı sayıları eksik")
            eden = {}
            for p in _liste(s["veto_eden_konustu"]):
                uye, durum = p.split(":")
                if durum not in KONUSTU:
                    raise hata(f"bilinmeyen veto_eden_konustu değeri '{durum}'")
                eden[uye] = durum
            gruplar = _liste(s["grup_adina_konusanlar"])
            if int(s["grup_adina_konusan"]) != len(gruplar):
                raise hata("grup adına konuşan sayısı listeyle tutmuyor")
            t["konusmacilar"] = {
                "aciklama_uye_devlet": int(s["aciklama_uye_devlet"]),
                "aciklama_gozlemci": int(s["aciklama_gozlemci"]), "gozlemciler": _liste(s["gozlemciler"]),
                "grup_adina_konusan": len(gruplar), "grup_adina_konusanlar": gruplar,
                "cevap_hakki": int(s["cevap_hakki"]), "cevap_hakki_kullananlar": _liste(s["cevap_hakki_kullananlar"]),
                "veto_eden_konustu": eden, "kaynak": s["konusmaci_kaynagi"],
                "gayriresmi_alanlar": _liste(s["gayriresmi_alanlar"]),
            }
            if t["konusmacilar"]["kaynak"] not in ("toplanti_kaydi", "bm_gunlugu", "gayriresmi_transkript"):
                raise hata("bilinmeyen konuşmacı kaynağı")
        elif any(s[a] for a in SAYI_ALANLARI) or s["veto_eden_konustu"]:
            raise hata("olağanüstü özel oturumda konuşmacı sayısı tutulmaz")
        tartismalar.append(t)
    return tartismalar


def raporlari_oku(yol: Path) -> dict[str, str]:
    with open(yol, encoding="utf-8", newline="") as f:
        return {s["veto_id"]: s["ozel_rapor"] for s in csv.DictReader(f)}


def genel_kurul_ekle(kayitlar: list[dict], tartismalar: list[dict], raporlar: dict[str, str]) -> list[str]:
    """Her kayda genel_kurul alanını yazar. Döndürür: uyarılar."""
    uyarilar = []
    mevcut = {k["id"]: k for k in kayitlar}
    for t in tartismalar:
        for v in t["veto_idleri"]:
            if v not in mevcut:
                uyarilar.append(f"{t['id']}: veri setinde olmayan veto {v}")
            elif t["konusmacilar"]:
                eksik = set(mevcut[v]["veto_eden_uyeler"]) - set(t["konusmacilar"]["veto_eden_konustu"])
                if eksik:
                    uyarilar.append(f"{t['id']}: veto eden {sorted(eksik)} için veto_eden_konustu yok")
    for v in raporlar:
        if v not in mevcut:
            uyarilar.append(f"ozel_raporlar.csv: veri setinde olmayan veto {v}")
    for k in kayitlar:
        if k["tarih"] < KAPSAM_BASLANGICI:
            k["genel_kurul"] = {"durum": "kapsam_disi", "ozel_rapor": None, "tartismalar": []}
            continue
        ilgili = [t["id"] for t in tartismalar if k["id"] in t["veto_idleri"]]
        k["genel_kurul"] = {"durum": "yapildi" if ilgili else "bekleniyor",
                            "ozel_rapor": raporlar.get(k["id"]), "tartismalar": ilgili}
        if not ilgili:
            uyarilar.append(f"{k['id']}: 76/262 kapsamında ama Genel Kurul tartışması kayıtlı değil")
        if not raporlar.get(k["id"]):
            uyarilar.append(f"{k['id']}: özel rapor kayıtlı değil")
    return uyarilar


def bekleyen_kayitlar(tartismalar: list[dict]) -> list[tuple[str, str, str]]:
    """Resmî kaydı henüz yayımlanmamış toplantılar: (tartışma, kayıt, durum)."""
    return [(t["id"], r["kod"], r["durum"]) for t in tartismalar for r in t["toplanti_kayitlari"] if r["durum"] != "resmi"]
