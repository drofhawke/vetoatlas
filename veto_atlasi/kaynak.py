"""
Ham kaynak dosyalarının arşivlenmesi ve özetlenmesi.

İlke: Ham dosya, sunucudan gelen baytların birebir kopyasıdır. Metin moduna
çevrilmez (Windows'ta satır sonları bozulur), var olan bir dosyanın üzerine
asla yazılmaz. SHA-256 özeti her zaman diskteki dosyanın baytlarından hesaplanır;
böylece 01, 03 ve 04 aynı dosya için aynı değeri gösterir.
"""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path


def dosya_sha256(yol: Path) -> str:
    return hashlib.sha256(Path(yol).read_bytes()).hexdigest()


def ham_kaydet(icerik: bytes, klasor: Path, gun: date, onek: str = "veto_dhl") -> Path:
    """
    Baytları <klasor>/<onek>_<gun>.html olarak yazar ve yolu döndürür.
    Aynı adda dosya varsa: içerik birebir aynıysa yeniden yazmaz, o dosyayı döndürür;
    farklıysa _2, _3 ... ekiyle yeni dosya açar. Mevcut dosyaya asla dokunmaz.
    """
    klasor.mkdir(parents=True, exist_ok=True)
    yol = klasor / f"{onek}_{gun.isoformat()}.html"
    n = 2
    while yol.exists():
        if yol.read_bytes() == icerik:
            return yol
        yol = klasor / f"{onek}_{gun.isoformat()}_{n}.html"
        n += 1
    with open(yol, "xb") as f:  # "x": dosya varsa hata verir, üzerine yazmaz
        f.write(icerik)
    return yol


def ham_html_oku(yol: Path) -> str:
    """Ham dosyayı bayt olarak okuyup UTF-8 çözer. Satır sonlarına dokunmaz."""
    return Path(yol).read_bytes().decode("utf-8")


def kaynak_dogrula(kok: Path, meta: dict, yoksa_kayitli: bool = False) -> tuple[Path | None, str]:
    """
    İşlenmiş verinin meta bilgisindeki ham dosyayı bulur, özetini diskten yeniden
    hesaplar ve kayıtlı özetle karşılaştırır. Tutmazsa ValueError fırlatır.
    Ham dosya yoksa (açık depoda ham dosyalar yoktur; künyesi data/raw/KAYNAK.md'de):
    yoksa_kayitli=True ise kayıtlı özet döner (yol None), değilse ValueError.
    Dosya varsa özet her durumda doğrulanır.
    """
    yol = kok / meta["kaynak_dosya"]
    if not yol.exists():
        if yoksa_kayitli:
            return None, meta["kaynak_sha256"]
        raise ValueError(f"Ham kaynak dosyası bulunamadı: {meta['kaynak_dosya']}")
    sha = dosya_sha256(yol)
    if sha != meta.get("kaynak_sha256"):
        raise ValueError(
            f"SHA-256 tutmuyor: {meta['kaynak_dosya']} diskte {sha}, "
            f"işlenmiş veride {meta.get('kaynak_sha256')}. 01'i yeniden çalıştır."
        )
    return yol, sha
