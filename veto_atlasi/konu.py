"""
Konu sınıflandırması ve Türkçe gündem başlıkları.

İki kaynak dosya kullanılır, ikisi de kaynaklar/ altında ve gerekçeli:
  gundem_sozlugu.csv    -> her özgün gündem başlığı için Türkçe çeviri, konu ve bölge
  konu_duzeltmeleri.csv -> başlığın tek başına yetmediği kayıtlar için kayıt bazında konu
                           ve ikincil konular (gerekçe: scprocedure Tablo 4'teki konu)

Sayımlarda yalnızca ana konu (konu_kategorisi) kullanılır; ikincil konular filtrelemede
kaydı ilgili konuya da bağlar ama hiçbir toplama girmez.
"""

from __future__ import annotations

import csv
from pathlib import Path

KONULAR = [
    "Filistin ve Arap-İsrail meselesi",
    "Lübnan",
    "Suriye",
    "Diğer Ortadoğu ve Kuzey Afrika",
    "Kıbrıs",
    "Ukrayna",
    "Diğer Avrupa",
    "Güney Afrika, Namibya ve Rodezya",
    "Diğer Afrika",
    "Latin Amerika ve Karayipler",
    "Asya",
    "Silahsızlanma ve askerî gerilimler",
    "Üyelik başvuruları",
    "Genel Sekreter seçimi",
    "Tematik konular",
]
SINIFLANDIRILMADI = "Sınıflandırılmadı"

BOLGELER = [
    "Ortadoğu ve Kuzey Afrika",
    "Avrupa",
    "Afrika",
    "Asya ve Pasifik",
    "Latin Amerika ve Karayipler",
    "Küresel",
]


def _oku(yol: Path) -> list[dict]:
    with open(yol, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _liste(s: str | None) -> list[str]:
    return [p.strip() for p in (s or "").split(";") if p.strip()]


def sozluk_oku(yol: Path) -> dict[str, dict]:
    """gundem_orijinal -> {gundem_tr, konu, bolge}. Geçersiz konu/bölge ya da mükerrer başlık hata verir."""
    sozluk: dict[str, dict] = {}
    for i, s in enumerate(_oku(yol), start=2):
        if s["gundem_orijinal"] in sozluk:
            raise ValueError(f"{yol.name} satır {i}: başlık iki kez geçiyor: {s['gundem_orijinal']}")
        if s["konu"] not in KONULAR:
            raise ValueError(f"{yol.name} satır {i}: bilinmeyen konu '{s['konu']}'")
        if s["bolge"] not in BOLGELER:
            raise ValueError(f"{yol.name} satır {i}: bilinmeyen bölge '{s['bolge']}'")
        if not s["gundem_tr"].strip():
            raise ValueError(f"{yol.name} satır {i}: Türkçe başlık boş")
        sozluk[s["gundem_orijinal"]] = {"gundem_tr": s["gundem_tr"], "konu": s["konu"], "bolge": s["bolge"]}
    return sozluk


def duzeltmeleri_oku(yol: Path) -> dict[str, dict]:
    """kayıt id -> {konu, ikincil_konular, gerekce, gerekce_en}."""
    duz: dict[str, dict] = {}
    for i, s in enumerate(_oku(yol), start=2):
        ikincil = _liste(s["ikincil_konular"])
        for k in [s["konu"], *ikincil]:
            if k not in KONULAR:
                raise ValueError(f"{yol.name} satır {i}: bilinmeyen konu '{k}'")
        if s["konu"] in ikincil:
            raise ValueError(f"{yol.name} satır {i}: ana konu ikincil konularda da var")
        if s["id"] in duz:
            raise ValueError(f"{yol.name} satır {i}: kayıt iki kez geçiyor: {s['id']}")
        if not s["gerekce"].strip():
            raise ValueError(f"{yol.name} satır {i}: gerekçe boş")
        duz[s["id"]] = {"konu": s["konu"], "ikincil_konular": ikincil, "gerekce": s["gerekce"],
                        "gerekce_en": (s.get("gerekce_en") or "").strip()}
    return duz


def siniflandir(kayitlar: list[dict], sozluk: dict[str, dict], duzeltmeler: dict[str, dict]) -> list[str]:
    """
    Kayıtlara gundem_tr, konu_kategorisi, bolge ve ikincil_konular alanlarını yazar.
    Sözlükte olmayan başlık "Sınıflandırılmadı" olur. Döndürür: uyarı listesi.
    """
    uyarilar: list[str] = []
    bilinmeyen: dict[str, list[str]] = {}
    for k in kayitlar:
        s = sozluk.get(k["gundem_maddesi"])
        if s is None:
            bilinmeyen.setdefault(k["gundem_maddesi"], []).append(k["id"])
            k.update(gundem_tr=None, konu_kategorisi=SINIFLANDIRILMADI, bolge=None, ikincil_konular=[])
        else:
            k.update(gundem_tr=s["gundem_tr"], konu_kategorisi=s["konu"], bolge=s["bolge"], ikincil_konular=[])
        d = duzeltmeler.get(k["id"])
        if d:
            k["konu_kategorisi"] = d["konu"]
            k["ikincil_konular"] = list(d["ikincil_konular"])
    for baslik, idler in bilinmeyen.items():
        uyarilar.append(f"Sözlükte olmayan gündem başlığı ({', '.join(idler)}): \"{baslik}\" -> {SINIFLANDIRILMADI}")
    mevcut = {k["id"] for k in kayitlar}
    for i in duzeltmeler:
        if i not in mevcut:
            uyarilar.append(f"konu_duzeltmeleri.csv'deki kayıt veri setinde yok: {i}")
    return uyarilar


def konu_dagilimi(kayitlar: list[dict]) -> dict[str, dict]:
    """Konu -> {oneri, oy, ikincil}. Öneri ve oy yalnızca ana konuyu sayar; oy kapalı oturumları dışarıda bırakır."""
    d = {k: {"oneri": 0, "oy": 0, "ikincil": 0} for k in KONULAR}
    for k in kayitlar:
        d.setdefault(k["konu_kategorisi"], {"oneri": 0, "oy": 0, "ikincil": 0})
        d[k["konu_kategorisi"]]["oneri"] += 1
        if not k.get("atif_belirsiz"):
            d[k["konu_kategorisi"]]["oy"] += len(k["veto_eden_uyeler"])
        for ik in k.get("ikincil_konular", []):
            d[ik]["ikincil"] += 1
    return d
