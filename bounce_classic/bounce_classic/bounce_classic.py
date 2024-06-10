import pygame
import sys

# Inisialisasi Pygame
pygame.init()

# Konstanta
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BALL_RADIUS = 20
FINISH_LINE_X = 2500  # Level lebih besar dari layar
SPEED = 10
JUMP_STRENGTH = 15
GRAVITY = 1
SPIKE_WIDTH = 30
SPIKE_HEIGHT = 50
BOX_WIDTH = 50
BOX_HEIGHT = 50
MARGIN = SCREEN_WIDTH // 2  # Margin untuk kamera

# Warna
WHITE = (85, 218, 254)
RED = (240, 53, 9)
BLACK = (0, 0, 0)

# Set up layar
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bounce Classic")

# Memuat gambar dan menskalakan
ball_image = pygame.image.load('ball.png')
ball_image = pygame.transform.scale(ball_image, (BALL_RADIUS * 2, BALL_RADIUS * 2))

spike_image = pygame.image.load('spike.png')
spike_image = pygame.transform.scale(spike_image, (SPIKE_WIDTH, SPIKE_HEIGHT))

box_image = pygame.image.load('box.png')
box_image = pygame.transform.scale(box_image, (BOX_WIDTH, BOX_HEIGHT))

finish_image = pygame.image.load('finish.png')  # Gambar tanda finish
finish_image = pygame.transform.scale(finish_image, (BOX_WIDTH, BOX_HEIGHT * 2))

# Kelas Bola
class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BALL_RADIUS
        self.image = ball_image
        self.original_image = ball_image
        self.speed = SPEED
        self.jump_strength = JUMP_STRENGTH
        self.velocity_y = 0
        self.is_jumping = False
        self.angle = 0
    
    def move(self, direction):
        if direction == 'left' and self.x - self.radius > 0:  # Membatasi gerakan ke kiri
            self.x -= self.speed
            self.angle += self.speed  # Rotasi ke kiri
        elif direction == 'right' and self.x + self.radius < FINISH_LINE_X + BOX_WIDTH:  # Membatasi gerakan ke kanan
            self.x += self.speed
            self.angle -= self.speed  # Rotasi ke kanan

        # Memeriksa tabrakan horizontal dengan kotak
        for box in boxes:
            if self.y + self.radius > box[1] and self.y - self.radius < box[1] + BOX_HEIGHT:
                if self.x + self.radius > box[0] and self.x - self.radius < box[0] + BOX_WIDTH:
                    if direction == 'left':
                        self.x = box[0] + BOX_WIDTH + self.radius
                    elif direction == 'right':
                        self.x = box[0] - self.radius
    
    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = -self.jump_strength
    
    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.y += self.velocity_y

        # Memeriksa tabrakan vertikal dengan kotak
        for box in boxes:
            if self.x + self.radius > box[0] and self.x - self.radius < box[0] + BOX_WIDTH:
                if self.y + self.radius > box[1] and self.y - self.radius < box[1] + BOX_HEIGHT:
                    if self.velocity_y > 0:  # Jatuh di atas kotak
                        self.y = box[1] - self.radius
                        self.is_jumping = False
                        self.velocity_y = 0
                    elif self.velocity_y < 0:  # Tabrakan dari bawah kotak
                        self.y = box[1] + BOX_HEIGHT + self.radius
                        self.velocity_y = 1  # Mengurangi efek gravitasi untuk melompat kembali
    
    def draw(self, screen, camera_x):
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        rect = rotated_image.get_rect(center=(self.x - camera_x, self.y))
        screen.blit(rotated_image, rect.topleft)

# Kelas Spike
class Spike:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = spike_image
    
    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.x - camera_x, self.y - self.image.get_height()))

# Fungsi untuk memeriksa tabrakan
def check_collision(ball, spike):
    if ball.x + ball.radius > spike.x and ball.x - ball.radius < spike.x + spike.image.get_width():
        if ball.y + ball.radius > spike.y - spike.image.get_height():
            return True
    return False

# Fungsi untuk memeriksa tabrakan dengan finish
def check_finish_collision(ball, finish):
    if ball.x + ball.radius > finish[0] and ball.x - ball.radius < finish[0] + BOX_WIDTH:
        if ball.y + ball.radius > finish[1] and ball.y - ball.radius < finish[1] + (BOX_HEIGHT * 2):
            return True
    return False

# Fungsi untuk mereset game
def reset_game():
    global ball, spikes, game_over, message, camera_x, boxes, finish
    ball = Ball(50, SCREEN_HEIGHT - BALL_RADIUS - BOX_HEIGHT)
    spikes = [Spike(x, y) for x, y in spike_positions]
    game_over = False
    message = ""
    camera_x = 0
    
    # Inisialisasi kotak alas dan kotak atap, serta kotak pembatas kiri dan kanan
    boxes = []
    for i in range(-BOX_WIDTH, FINISH_LINE_X + BOX_WIDTH * 3, BOX_WIDTH):  # Mulai dari -BOX_WIDTH untuk menutupi sisi kiri, dan geser tembok kanan ke kanan 1 kotak
        boxes.append((i, SCREEN_HEIGHT - BOX_HEIGHT))  # Kotak alas
        boxes.append((i, 0))  # Kotak atap
    
    for j in range(0, SCREEN_HEIGHT, BOX_HEIGHT):  # Pembatas kiri dan kanan
        boxes.append((-BOX_WIDTH, j))  # Pembatas kiri
        boxes.append((FINISH_LINE_X + BOX_WIDTH, j))  # Pembatas kanan
    
    # Tambahkan kotak di posisi tertentu
    for x, y in box_positions:
        boxes.append((x, y))
    
    # Inisialisasi tanda finish di atas kotak terakhir
    finish = (FINISH_LINE_X, SCREEN_HEIGHT - BOX_HEIGHT * 3)  # Posisi tanda finish

# Daftar posisi untuk kotak tambahan
box_positions = [
    (300, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    (350, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    (350, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    
    (400, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    (400, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (400, SCREEN_HEIGHT - BOX_HEIGHT * 4),

    (450, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    (450, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (450, SCREEN_HEIGHT - BOX_HEIGHT * 4),

    (600, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    (600, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (600, SCREEN_HEIGHT - BOX_HEIGHT * 4),

    (650, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    (650, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (650, SCREEN_HEIGHT - BOX_HEIGHT * 4),

    (700, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    (700, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    
    (750, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    
    (900, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    
    (950, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (950, SCREEN_HEIGHT - BOX_HEIGHT * 4),
    
    (1000, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (1000, SCREEN_HEIGHT - BOX_HEIGHT * 4),
    (1000, SCREEN_HEIGHT - BOX_HEIGHT * 5),
    
    (1050, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (1050, SCREEN_HEIGHT - BOX_HEIGHT * 4),
    (1050, SCREEN_HEIGHT - BOX_HEIGHT * 5),
    
    (1100, SCREEN_HEIGHT - BOX_HEIGHT * 4),
    (1100, SCREEN_HEIGHT - BOX_HEIGHT * 5),
    
    (1150, SCREEN_HEIGHT - BOX_HEIGHT * 5),
    
    (1400, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (1450, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (1500, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (1550, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (1600, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (1650, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (1400, SCREEN_HEIGHT - BOX_HEIGHT * 5),
    (1450, SCREEN_HEIGHT - BOX_HEIGHT * 5),
    (1500, SCREEN_HEIGHT - BOX_HEIGHT * 5),
    (1550, SCREEN_HEIGHT - BOX_HEIGHT * 5),
    (1600, SCREEN_HEIGHT - BOX_HEIGHT * 5),
    (1650, SCREEN_HEIGHT - BOX_HEIGHT * 5),
    (1700, SCREEN_HEIGHT - BOX_HEIGHT * 5),
    
    (1750, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    
    (1400, SCREEN_HEIGHT - BOX_HEIGHT * 7),
    (1450, SCREEN_HEIGHT - BOX_HEIGHT * 7),
    (1500, SCREEN_HEIGHT - BOX_HEIGHT * 7),
    (1550, SCREEN_HEIGHT - BOX_HEIGHT * 7),
    (1600, SCREEN_HEIGHT - BOX_HEIGHT * 7),
    (1650, SCREEN_HEIGHT - BOX_HEIGHT * 7),
    
    (1400, SCREEN_HEIGHT - BOX_HEIGHT * 9),
    (1450, SCREEN_HEIGHT - BOX_HEIGHT * 9),
    (1500, SCREEN_HEIGHT - BOX_HEIGHT * 9),
    (1550, SCREEN_HEIGHT - BOX_HEIGHT * 9),
    (1600, SCREEN_HEIGHT - BOX_HEIGHT * 9),
    (1650, SCREEN_HEIGHT - BOX_HEIGHT * 9),
    (1700, SCREEN_HEIGHT - BOX_HEIGHT * 9),
    
    (1750, SCREEN_HEIGHT - BOX_HEIGHT * 3),
    (1750, SCREEN_HEIGHT - BOX_HEIGHT * 4),
    (1750, SCREEN_HEIGHT - BOX_HEIGHT * 5),
    (1750, SCREEN_HEIGHT - BOX_HEIGHT * 6),
    (1750, SCREEN_HEIGHT - BOX_HEIGHT * 7),
    (1750, SCREEN_HEIGHT - BOX_HEIGHT * 8),
    (1750, SCREEN_HEIGHT - BOX_HEIGHT * 9),
    
    (1900, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    (2000, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    (2100, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    (2200, SCREEN_HEIGHT - BOX_HEIGHT * 2),
    (2300, SCREEN_HEIGHT - BOX_HEIGHT * 2),
]

# Daftar posisi untuk spike tambahan
spike_positions = [
    (550, SCREEN_HEIGHT - BOX_HEIGHT),
    (1200, SCREEN_HEIGHT - BOX_HEIGHT),
    (1250, SCREEN_HEIGHT - BOX_HEIGHT),
    (1300, SCREEN_HEIGHT - BOX_HEIGHT),
    (1950, SCREEN_HEIGHT - BOX_HEIGHT),
    (2050, SCREEN_HEIGHT - BOX_HEIGHT),
    (2150, SCREEN_HEIGHT - BOX_HEIGHT),
    (2250, SCREEN_HEIGHT - BOX_HEIGHT),
    (2350, SCREEN_HEIGHT - BOX_HEIGHT),
    # (1750, SCREEN_HEIGHT - BOX_HEIGHT),
    # (850, SCREEN_HEIGHT - BOX_HEIGHT),
    # (1250, SCREEN_HEIGHT - BOX_HEIGHT)
]

# Inisialisasi objek dan status game
reset_game()

# Main game loop
running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    
    if not game_over:
        if keys[pygame.K_LEFT]:
            ball.move('left')
        if keys[pygame.K_RIGHT]:
            ball.move('right')
        if keys[pygame.K_UP]:
            ball.jump()
        
        ball.apply_gravity()
        
        # Update posisi kamera untuk mengikuti bola
        camera_x = ball.x - SCREEN_WIDTH // 2
        
        camera_x = max(camera_x, -BOX_WIDTH)  # Batas kiri kamera dengan margin        
        camera_x = min(camera_x, FINISH_LINE_X - SCREEN_WIDTH + (BOX_WIDTH * 2))  # Batas kanan kamera dengan margin
        
        # Menggambar kotak alas dan kotak atap, serta pembatas kiri dan kanan
        for box in boxes:
            screen.blit(box_image, (box[0] - camera_x, box[1]))
        
        # Menggambar tanda finish
        screen.blit(finish_image, (finish[0] - camera_x, finish[1]))
        
        ball.draw(screen, camera_x)
        
        for spike in spikes:
            spike.draw(screen, camera_x)
            if check_collision(ball, spike):
                message = "Game Over! Press SPACE to Restart"
                game_over = True
        
        # Cek apakah bola mencapai kotak finish
        if check_finish_collision(ball, finish):
            message = "You Win! Press SPACE to Restart"
            game_over = True
    else:
        if keys[pygame.K_SPACE]:
            reset_game()

    if message:
        font = pygame.font.Font(None, 36)
        text = font.render(message, True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(text, text_rect)
    
    pygame.display.flip()
    pygame.time.Clock().tick(30)

pygame.quit()
sys.exit()

        
