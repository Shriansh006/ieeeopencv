import cv2
import pygame
import sys
import random


nose_cascade = cv2.CascadeClassifier('nose.xml')
if nose_cascade.empty():
    print("Cascade failed to load.")
    sys.exit()

cap = cv2.VideoCapture(0)

pygame.init()
WIDTH, HEIGHT = 640, 480
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Nose Bird")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)


bird_x = 100
bird_radius = 20
gravity = 0.25
jump_strength = -6
flap_threshold = 15 

bird_y = HEIGHT * 3 // 4
bird_velocity = 0
walls = []
wall_width = 60
gap_height = 160
wall_speed = 4
wall_interval = 2700
last_wall_time = pygame.time.get_ticks()
prev_nose_y = None
game_over = False


def create_wall():
    gap_y = random.randint(100, HEIGHT - 100 - gap_height)
    top = pygame.Rect(WIDTH, 0, wall_width, gap_y)
    bottom = pygame.Rect(WIDTH, gap_y + gap_height, wall_width, HEIGHT)
    return (top, bottom)

def draw_webcam_background(frame):
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.flip(frame, 1)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.rotate(frame, -90)
    frame = pygame.transform.flip(frame, True, False)
    win.blit(frame, (0, 0))


def draw_bird():
    pygame.draw.circle(win, (255, 255, 0), (bird_x, int(bird_y)), bird_radius)


def draw_walls():
    for top, bottom in walls:
        pygame.draw.rect(win, (0, 255, 0), top)
        pygame.draw.rect(win, (0, 255, 0), bottom)


def check_collision():
    bird_rect = pygame.Rect(bird_x - bird_radius, int(bird_y - bird_radius), bird_radius * 2, bird_radius * 2)
    for top, bottom in walls:
        if bird_rect.colliderect(top) or bird_rect.colliderect(bottom):
            return True
    if bird_y < 0 or bird_y > HEIGHT:
        return True
    return False


def reset_game():
    global bird_y, bird_velocity, walls, last_wall_time, game_over
    bird_y = HEIGHT * 1 // 2
    bird_velocity = 0
    walls = []
    last_wall_time = pygame.time.get_ticks()
    game_over = False


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()

    
    ret, frame = cap.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    noses = nose_cascade.detectMultiScale(gray, 1.3, 5)
    flap_now = False

    if len(noses) > 0:
        (x, y, w, h) = noses[0]
        nose_y = y + h // 2

        
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        if prev_nose_y is not None:
            diff = prev_nose_y - nose_y
            print(f"Nose Y movement: {diff}")  
            if diff > flap_threshold:
                flap_now = True
                print("FLAP!")  

        prev_nose_y = nose_y

    if game_over and flap_now:
        reset_game()

    if not game_over:
        if flap_now:
            bird_velocity = jump_strength

        bird_velocity += gravity
        bird_y += bird_velocity

       
        current_time = pygame.time.get_ticks()
        if current_time - last_wall_time > wall_interval:
            walls.append(create_wall())
            last_wall_time = current_time

       
        for i in range(len(walls)):
            walls[i] = (walls[i][0].move(-wall_speed, 0), walls[i][1].move(-wall_speed, 0))

        
        walls = [pair for pair in walls if pair[0].right > 0]

        if check_collision():
            game_over = True

   
    draw_webcam_background(frame)
    draw_bird()
    draw_walls()

    if game_over:
        over_text = font.render("Game Over - Flap to Restart", True, (255, 0, 0))
        win.blit(over_text, (WIDTH // 2 - 160, HEIGHT // 2 - 20))

    pygame.display.update()
    clock.tick(30)
