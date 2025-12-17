import pygame
import sys
import math
import random

pygame.init()

LEBAR = 800
TINGGI = 600
layar = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption("BRIO.KUMAN - Jalan Raya Malam")
clock = pygame.time.Clock()
FPS = 60

# ============================================================
# LOAD KARAKTER (PAJERO / BRIO)
# ============================================================
FILENAME = 'pajeroo.png'
try:
    gambar_asli = pygame.image.load(FILENAME).convert_alpha()
except Exception:
    print("pajeroo.png tidak ada → pakai placeholder")
    gambar_asli = pygame.Surface((141, 200), pygame.SRCALPHA)
    pygame.draw.rect(gambar_asli, (50, 50, 70), (0, 0, 141, 200))
    pygame.draw.rect(gambar_asli, (200, 200, 200), (15, 15, 111, 170), 6)
    pygame.draw.circle(gambar_asli, (255, 220, 0), (70, 50), 30)

UKURAN_X = 141
UKURAN_Y = 200
gambar_asli = pygame.transform.scale(gambar_asli, (UKURAN_X, UKURAN_Y))

# ============================================================
# LOAD KUMAN
# ============================================================
UKURAN_KUMAN = 80
try:
    kuman_img = pygame.image.load('kuman.png').convert_alpha()
    kuman_img = pygame.transform.scale(kuman_img, (UKURAN_KUMAN, UKURAN_KUMAN))
except Exception:
    print("kuman.png tidak ada → pakai placeholder kuning")
    kuman_img = pygame.Surface((UKURAN_KUMAN, UKURAN_KUMAN), pygame.SRCALPHA)
    points = [(40, 0), (60, 30), (50, 80), (30, 80), (20, 30)]
    pygame.draw.polygon(kuman_img, (255, 220, 0), points)
    pygame.draw.polygon(kuman_img, (255, 255, 150), points, 5)
    pygame.draw.circle(kuman_img, (255, 255, 255, 180), (40, 40), 20)

# ============================================================
# VARIABEL GAME
# ============================================================
pos_x = LEBAR // 2 - UKURAN_X // 2
pos_y = TINGGI - UKURAN_Y - 50
KECEPATAN = 7
arah = 1
waktu = 0.0
bounce = 0.0
trail = []
trail_surface = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)

# Animasi jalan
road_offset = 0.0
road_speed = 8.0

# Area jalan untuk spawn kuman (hanya muncul di jalan)
AREA_JALAN_MIN = 210
AREA_JALAN_MAX = TINGGI - 120

# List kuman
kuman_list = []
for _ in range(12):
    kuman_list.append({
        "x": random.randint(100, LEBAR - 100),
        "y": random.randint(AREA_JALAN_MIN, AREA_JALAN_MAX),
        "aktif": True
    })

# Bintang pre-render surface
stars_surf = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)

# ============================================================
# DETEKSI TABRAKAN
# ============================================================
def cek_tabrakan():
    hero_rect = pygame.Rect(int(pos_x + 30), int(pos_y + 30), int(UKURAN_X - 60), int(UKURAN_Y - 60))
    for k in kuman_list:
        if not k["aktif"]:
            continue
        kuman_rect = pygame.Rect(int(k["x"] - UKURAN_KUMAN // 2), int(k["y"] - UKURAN_KUMAN // 2),
                                 UKURAN_KUMAN, UKURAN_KUMAN)
        if hero_rect.colliderect(kuman_rect):
            k["aktif"] = False

# ============================================================
# BACKGROUND JALAN RAYA MALAM
# ============================================================
def gambar_jalan_raya():
    global road_offset, road_speed
    road_offset += road_speed
    # keep road_offset bounded to avoid super besar number
    if road_offset > 1000000:
        road_offset = road_offset % 1000

    # Langit malam
    layar.fill((5, 10, 30))

    # Bintang berkedip - gambar ke stars_surf (SRCALPHA)
    stars_surf.fill((0, 0, 0, 0))
    for i in range(80):
        x = int((i * 137 + road_offset * 2) % (LEBAR + 200) - 100)
        y = int((i * 73) % 300 + 20)
        alpha = int(100 + 155 * math.sin(pygame.time.get_ticks() * 0.002 + i))
        alpha = max(0, min(255, alpha))
        pygame.draw.circle(stars_surf, (255, 255, 200, alpha), (x, y), 1)
    layar.blit(stars_surf, (0, 0))

    # Aspal jalan
    pygame.draw.rect(layar, (30, 30, 35), (0, 150, LEBAR, TINGGI - 150))

    # Garis tengah putus-putus (bergerak)
    for i in range(-50, LEBAR + 100, 120):
        x = int((i + road_offset * 4) % (LEBAR + 200) - 100)
        pygame.draw.rect(layar, (255, 255, 100), (x, TINGGI // 2 - 10, 80, 12))

    # Garis pinggir kuning (atas dan bawah)
    pygame.draw.line(layar, (255, 200, 0), (0, 160), (LEBAR, 160), 8)
    pygame.draw.line(layar, (255, 200, 0), (0, TINGGI - 20), (LEBAR, TINGGI - 20), 8)

    # Marka samping putih
    for i in range(-100, LEBAR + 200, 80):
        x = int((i + road_offset * 2) % (LEBAR + 300) - 150)
        pygame.draw.rect(layar, (255, 255, 255), (x, 170, 60, 8))
        pygame.draw.rect(layar, (255, 255, 255), (x, TINGGI - 30, 60, 8))

    # Lampu jalan kiri-kanan
    for i in range(15):
        x = int((i * 200 - road_offset * 3) % (LEBAR + 400) - 200)
        if i % 2 == 0:
            pygame.draw.line(layar, (100, 100, 120), (x, 160), (x, 80), 6)
            pygame.draw.circle(layar, (255, 230, 150), (x, 80), 20)
        else:
            xp = x + LEBAR
            pygame.draw.line(layar, (100, 100, 120), (xp, 160), (xp, 80), 6)
            pygame.draw.circle(layar, (255, 230, 150), (xp, 80), 20)

    # Efek speed lines (buram)
    for i in range(20):
        x = int((i * 100 - road_offset * 10) % (LEBAR + 300) - 150)
        y = 150 + i * 25
        alpha = max(0, min(255, 60 + i * 8))
        s = pygame.Surface((120, 4), pygame.SRCALPHA)
        s.fill((255, 255, 255, alpha))
        layar.blit(s, (x, y))

# ============================================================
# FONT
# ============================================================
font_title = pygame.font.SysFont("Impact", 52, bold=True)
font_score = pygame.font.SysFont("Arial", 32, bold=True)

# ============================================================
# MAIN LOOP
# ============================================================
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        dx = -KECEPATAN
        arah = -1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx = KECEPATAN
        arah = 1
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dy = -KECEPATAN
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy = KECEPATAN

    pos_x = max(50, min(pos_x + dx, LEBAR - UKURAN_X - 50))
    pos_y = max(150, min(pos_y + dy, TINGGI - UKURAN_Y - 20))

    bergerak = (dx != 0 or dy != 0)
    if bergerak:
        waktu += 0.4
        bounce = math.sin(waktu) * 18
        road_speed = 8.0 + abs(dx) * 0.8
        if len(trail) == 0 or math.hypot(trail[-1][0] - (pos_x + UKURAN_X // 2),
                                         trail[-1][1] - (pos_y + UKURAN_Y // 2)) > 25:
            trail.append([pos_x + UKURAN_X // 2, pos_y + UKURAN_Y // 2, 255])
    else:
        bounce *= 0.9
        road_speed = 8.0

    # Update trail alpha and cleanup
    for t in trail[:]:
        t[2] -= 12
        if t[2] <= 0:
            trail.remove(t)

    # collision detection
    cek_tabrakan()

    # Respawn kuman kalau habis (tetap di area jalan)
    if all(not k["aktif"] for k in kuman_list):
        for k in kuman_list:
            k["x"] = random.randint(100, LEBAR - 100)
            k["y"] = random.randint(AREA_JALAN_MIN, AREA_JALAN_MAX)
            k["aktif"] = True

    # Gambar background
    gambar_jalan_raya()

    # Gambar semua kuman (hanya di jalan karena spawn di area jalan)
    for k in kuman_list:
        if k["aktif"]:
            layar.blit(kuman_img, (int(k["x"] - UKURAN_KUMAN // 2), int(k["y"] - UKURAN_KUMAN // 2)))

    # Gambar karakter dengan bounce (pastikan orientasi)
    karakter = gambar_asli if arah == 1 else pygame.transform.flip(gambar_asli, True, False)
    layar.blit(karakter, (int(pos_x), int(pos_y + bounce)))

    # Teks judul
    shadow = font_title.render("BRIO.KUMAN", True, (180, 0, 0))
    title = font_title.render("BRIO.KUMAN", True, (255, 230, 100))
    layar.blit(shadow, (202, 12))
    layar.blit(title, (200, 10))

    # Score
    sisa = sum(1 for k in kuman_list if k["aktif"])
    score = font_score.render(f"KUMAN: {sisa}", True, (255, 255, 150))
    layar.blit(score, (LEBAR - 220, 10))

    pygame.display.flip()
    clock.tick(FPS)
