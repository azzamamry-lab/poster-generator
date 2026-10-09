# -*- coding: utf-8 -*-
"""
Poster "Jumat Berkah di Masjidil Haram" - versi baru (dibuat dari nol).

Semua teks & warna bisa diubah dari blok KONTEN di bawah.
Jalankan: python buat_poster_jumat.py
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display


def arab(teks):
    """Siapkan teks Arab supaya benar: huruf bersambung + urutan kanan->kiri.

    Tanpa ini, PIL menggambar huruf Arab terpisah dan terbalik.
    """
    try:
        return get_display(arabic_reshaper.reshape(teks))
    except Exception:
        return teks

# ============================================================
# KONTEN  (ubah di sini kalau perlu)
# ============================================================
JUDUL_1 = "JUMAT BERKAH"
JUDUL_2 = "DI MASJIDIL HARAM"
SUBJUDUL = "Berbagi di Tanah Suci, raih keberkahan berlipat ganda."

HADIS_1 = "Masjidil Haram memiliki keutamaan yang sangat agung."
HADIS_2_AWAL = "Rasulullah "
HADIS_2_ARAB = "\u0635\u0644\u0649 \u0627\u0644\u0644\u0647 \u0639\u0644\u064a\u0647 \u0648\u0633\u0644\u0645"
HADIS_2_AKHIR = " bersabda:"
HADIS_KUTIP = (
    "\u201cShalat di Masjidil Haram lebih utama daripada\n"
    "100.000 shalat di masjid lainnya.\u201d"
)
HADIS_SUMBER = "(HR. Ahmad & Ibnu Majah)"
AJAKAN = (
    "Mari manfaatkan kesempatan berada di Tanah Suci\n"
    "dengan memperbanyak ibadah, doa, dan berbagi kepada sesama."
)

NOMINAL_1 = "HANYA 10 RIYAL / PAX"
NOMINAL_2 = "Rp50.000 / PAX"
TITIP = (
    "Titip sedekah Anda di Tanah Suci.\n"
    "Semoga menjadi amal yang diterima dan penuh keberkahan."
)

KONTAK_1 = "0858 4267 7096"
KONTAK_2 = "+20 11 02301172"

# Rekening
REKENING = [
    ("BSI", "7167851252"),
    ("Bank Jago Syariah", "509515222864"),
    ("Bank Mandiri", "1380029700130"),
]
ATAS_NAMA = "a.n. YUSUF BURHANI"

# ============================================================
# WARNA
# ============================================================
NAVY = (17, 51, 40)          # hijau tua (judul)
HIJAU = (27, 94, 62)         # hijau utama
HIJAU_MUDA = (232, 244, 236)  # latar kotak hijau muda
EMAS = (198, 154, 42)        # aksen emas
EMAS_MUDA = (247, 240, 220)  # latar kotak hadis
PUTIH = (255, 255, 255)
KREM = (250, 248, 243)       # latar poster
ABU = (108, 117, 125)        # teks abu

# --- Path dibuat relatif terhadap lokasi script, supaya portabel ---
AKAR = Path(__file__).resolve().parent.parent   # naik dari scripts/ ke akar repo
FOTO = AKAR / "aset" / "kabah.jpg"
FONT_AMIRI = AKAR / "aset" / "fonts" / "Amiri-Regular.ttf"
OUT = AKAR / "hasil"
OUT.mkdir(exist_ok=True)


def _cari_font(kandidat):
    """Cari font pertama yang ada (lintas OS)."""
    for f in kandidat:
        try:
            if Path(f).exists():
                return f
        except Exception:
            continue
    return None


_FONT_TEBAL = _cari_font([
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
])
_FONT_BIASA = _cari_font([
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
])

# Kanvas: 1080x1920 (rasio 9:16, pas untuk WA/IG story)
import sys
UKURAN = {
    "story": (1080, 1920),   # WA/IG story
    "feed":  (1080, 1350),   # IG/FB feed (4:5)
}
PILIH = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in UKURAN else "story"
W, H = UKURAN[PILIH]


def font(ukuran, tebal=False):
    """Ambil font; kalau tidak ada, pakai default."""
    jalur = _FONT_TEBAL if tebal else _FONT_BIASA
    if jalur:
        try:
            return ImageFont.truetype(jalur, ukuran)
        except Exception:
            pass
    return ImageFont.load_default()


def tengah(d, teks, y, f, warna, lebar=W):
    """Tulis teks di tengah horizontal."""
    bbox = d.textbbox((0, 0), teks, font=f)
    w = bbox[2] - bbox[0]
    d.text(((lebar - w) / 2, y), teks, font=f, fill=warna)
    return bbox[3] - bbox[1]


def tengah_banyak(d, baris_list, y, f, warna, jarak=10):
    for b in baris_list:
        h = tengah(d, b, y, f, warna)
        y += h + jarak
    return y


# ============================================================
# 1. LATAR: foto Ka'bah di atas, area putih di bawah
# ============================================================
poster = Image.new("RGB", (W, H), KREM)
d = ImageDraw.Draw(poster)

# --- foto Ka'bah (bagian atas) ---
tinggi_foto = 780 if PILIH == "story" else 620
foto = Image.open(FOTO).convert("RGB")
rasio = max(W / foto.size[0], tinggi_foto / foto.size[1])
foto = foto.resize((int(foto.size[0] * rasio), int(foto.size[1] * rasio)), Image.LANCZOS)
kiri = (foto.size[0] - W) // 2
atas = (foto.size[1] - tinggi_foto) // 2
foto = foto.crop((kiri, atas, kiri + W, atas + tinggi_foto))
poster.paste(foto, (0, 0))

# gradasi gelap di bawah foto supaya tulisan judul terbaca
lapis = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dl = ImageDraw.Draw(lapis)
for y in range(tinggi_foto):
    t = y / tinggi_foto
    # makin ke bawah makin gelap
    alpha = int(200 * max(0, (t - 0.35) / 0.65) ** 1.5)
    dl.line([(0, y), (W, y)], fill=(6, 32, 22, alpha))
poster = Image.alpha_composite(poster.convert("RGBA"), lapis).convert("RGB")

# gradasi putih halus di perbatasan foto -> area teks
lapis2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d2 = ImageDraw.Draw(lapis2)
y_awal = tinggi_foto - 120
for y in range(120):
    a = int(255 * (y / 120) ** 1.2)
    d2.line([(0, y_awal + y), (W, y_awal + y)], fill=KREM + (a,))
poster = Image.alpha_composite(poster.convert("RGBA"), lapis2).convert("RGB")

d = ImageDraw.Draw(poster)

# ============================================================
# 2. JUDUL di atas foto
# ============================================================
f_judul = font(86, True)
f_judul2 = font(56, True)
f_sub = font(27)

y = 448 if PILIH == "story" else 318
tengah(d, JUDUL_1, y, f_judul, PUTIH)
y += 104
tengah(d, JUDUL_2, y, f_judul2, (240, 205, 110))
y += 78
tengah(d, SUBJUDUL, y, f_sub, (226, 232, 228))

# garis aksen emas
garis_y = y + 44
d.rectangle([(W // 2 - 90, garis_y), (W // 2 + 90, garis_y + 4)], fill=(240, 205, 110))

# ============================================================
# 3. KARTU KEUTAMAAN MASJIDIL HARAM
# ============================================================
x0, x1 = 78, W - 78
if PILIH == "story":
    ky, kh = 830, 430
else:
    ky, kh = 618, 400

# kartu putih dengan bayangan
bay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
db = ImageDraw.Draw(bay)
db.rounded_rectangle([x0 + 5, ky + 8, x1 + 5, ky + kh + 8], radius=26, fill=(20, 40, 30, 45))
bay = bay.filter(ImageFilter.GaussianBlur(11))
poster = Image.alpha_composite(poster.convert("RGBA"), bay).convert("RGB")
d = ImageDraw.Draw(poster)

d.rounded_rectangle([x0, ky, x1, ky + kh], radius=26, fill=PUTIH,
                    outline=(224, 232, 226), width=2)

# label kecil
f_label = font(23, True)
lbl = "KEUTAMAAN MASJIDIL HARAM"
bbox = d.textbbox((0, 0), lbl, font=f_label)
lw = bbox[2] - bbox[0]
lx = (W - lw) / 2
d.rounded_rectangle([lx - 22, ky + 30, lx + lw + 22, ky + 74], radius=22, fill=HIJAU_MUDA)
d.text((lx, ky + 40), lbl, font=f_label, fill=HIJAU)

# teks hadis pembuka
f_t = font(25)
yy = ky + 100
tengah(d, HADIS_1, yy, f_t, (60, 72, 66))
yy += 38

# baris campuran: Indonesia + Arab (Arab perlu font & urutan khusus)
try:
    f_arab = ImageFont.truetype(FONT_AMIRI, 30)
except Exception:
    f_arab = font(27)
teks_arab = arab(HADIS_2_ARAB)
w1 = d.textlength(HADIS_2_AWAL, font=f_t)
w2 = d.textlength(teks_arab, font=f_arab)
w3 = d.textlength(HADIS_2_AKHIR, font=f_t)
x_awal = (W - (w1 + w2 + w3)) / 2
d.text((x_awal, yy), HADIS_2_AWAL, font=f_t, fill=(60, 72, 66))
d.text((x_awal + w1, yy - 6), teks_arab, font=f_arab, fill=(27, 94, 62))
d.text((x_awal + w1 + w2, yy), HADIS_2_AKHIR, font=f_t, fill=(60, 72, 66))
yy += 38

# kotak kutipan
qy = yy + 12
d.rounded_rectangle([x0 + 34, qy, x1 - 34, qy + 132], radius=16, fill=EMAS_MUDA)
f_q = font(28, True)
d.text((W / 2, qy + 28), "\u201c", font=font(52, True), fill=EMAS, anchor="mm")
yy2 = qy + 46
for baris in HADIS_KUTIP.split("\n"):
    tengah(d, baris, yy2 - 20, f_q, (120, 88, 20))
    yy2 += 36
tengah(d, HADIS_SUMBER, qy + 100, font(20), (150, 125, 70))

# ajakan
yy3 = qy + 156
for baris in AJAKAN.split("\n"):
    tengah(d, baris, yy3, f_t, (60, 72, 66))
    yy3 += 36

# ============================================================
# 4. KOTAK NOMINAL
# ============================================================
SISA = H
ny = 1300 if PILIH == "story" else 972
nh = 130 if PILIH == "story" else 112
d.rounded_rectangle([x0, ny, x1, ny + nh], radius=22, fill=HIJAU_MUDA,
                    outline=(190, 220, 200), width=2)
f_nom = font(34, True)
d.text((W / 2, ny + 38), NOMINAL_1, font=f_nom, fill=HIJAU, anchor="mm")
f_nom2 = font(40, True)
d.text((W / 2, ny + 88), NOMINAL_2, font=f_nom2, fill=EMAS, anchor="mm")

# kalimat titip sedekah
f_tit = font(24)
yyt = ny + nh + 22
for baris in TITIP.split("\n"):
    tengah(d, baris, yyt, f_tit, (70, 82, 76))
    yyt += 34

# ============================================================
# 5. KARTU REKENING (transfer)
# ============================================================
ry = 1560 if PILIH == "story" else 1106
TINGGI_REK = 210 if PILIH == "story" else 178
d.rounded_rectangle([x0, ry, x1, ry + TINGGI_REK], radius=22, fill=PUTIH,
                    outline=(208, 224, 212), width=2)
d.rounded_rectangle([x0, ry, x1, ry + 46], radius=22, fill=HIJAU)
d.rectangle([x0, ry + 30, x1, ry + 46], fill=HIJAU)
f_rt = font(23, True)
d.text((W / 2, ry + 23), "TRANSFER DONASI", font=f_rt, fill=PUTIH, anchor="mm")

f_bank = font(22, True)
f_norek = font(26, True)
yy2 = ry + 62
for i, (bank, norek) in enumerate(REKENING):
    d.text((x0 + 30, yy2), bank, font=f_bank, fill=ABU)
    bb = d.textbbox((0, 0), norek, font=f_norek)
    d.text((x1 - 30 - (bb[2] - bb[0]), yy2 - 3), norek, font=f_norek, fill=HIJAU)
    yy2 += 40 if PILIH == "story" else 34
    if i < len(REKENING) - 1:
        d.line([(x0 + 30, yy2 - 9), (x1 - 30, yy2 - 9)], fill=(236, 242, 238), width=1)

f_an = font(21, True)
d.text((W / 2, yy2 + 2), ATAS_NAMA, font=f_an, fill=(120, 90, 25), anchor="mm")

# ============================================================
# 6. KONTAK di paling bawah
# ============================================================
f_info = font(20, True)
f_kontak = font(25, True)
by = ry + (232 if PILIH == "story" else 186)
d.text((W / 2, by), "INFO & KONFIRMASI", font=f_info, fill=ABU, anchor="mm")
d.text((W / 2, by + 38), f"{KONTAK_1}   \u2022   {KONTAK_2}",
       font=f_kontak, fill=HIJAU, anchor="mm")

nama = f"poster_jumat_berkah_{PILIH}"
poster.save(OUT / f"{nama}.png", optimize=True)
poster.save(OUT / f"{nama}.jpg", quality=94, optimize=True)
print(f"OK -> {OUT / (nama + '.png')}")
print(f"   ukuran: {poster.size[0]}x{poster.size[1]}")
