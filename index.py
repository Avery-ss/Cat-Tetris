import pygame
from copy import deepcopy
from random import choice, randrange

W,H = 10,18
TILE = 45
GAME_RES = W * TILE,H * TILE
RES = 850, 850

pygame.init()
sc = pygame.display.set_mode(RES)
game_sc = pygame.Surface(GAME_RES)
clock = pygame.time.Clock()
fps = 60

grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

figure_pos = [[(-1,0),(-2,0),(0,0),(1,0)],
              [(0,-1),(-1,-1),(-1,0),(0,0)],
              [(-1,0),(-1,1),(0,0),(0,-1)],
              [(0,0),(-1,0),(0,1),(-1,-1)],
              [(0,0),(0,-1),(0,1),(-1,-1)],
              [(0,0),(0,-1),(0,1),(1,-1)],
              [(0,0),(0,-1),(0,1),(-1,0)]]

figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figure_pos]
figure_rect = pygame.Rect(0,0,TILE - 2, TILE - 2)

field = [[0 for i in range(W)] for j in range (H)]
anim_count, anim_speed, anim_limit = 0, 60, 2000

bg = pygame.image.load(('bg.png')).convert()
game_bg = pygame.image.load(('bg2.jpeg')).convert()

COLORS = [
    (242, 242, 228),  (240, 238, 222),  
    (238, 235, 218),  (250, 230, 222),  
    (248, 228, 220),  (252, 235, 225), 
    (232, 212, 192),  (225, 205, 185),
    (218, 198, 178),  (228, 200, 190), 
    (220, 192, 182), (215, 188, 175),  
    (185, 155, 135), (175, 145, 125),  
    (165, 135, 115),  (178, 142, 132),  
    (168, 132, 122),  (158, 125, 115),  
    (120, 85, 70),   (115, 80, 75),  
    (110, 90, 80),  (125, 90, 75),  
    (118, 85, 80),  (130, 95, 85),  
    (108, 88, 78),  (135, 100, 85), 
    (122, 90, 85),   (128, 95, 80)  
]
get_color = lambda: choice(COLORS)

COLOR_TEXT_DARK = (40, 35, 30)      # для основного текста
COLOR_TEXT_LIGHT = (80, 65, 55)     # для светлого текста
COLOR_TEXT_BRIGHT = (180, 160, 140) # для акцентов
COLOR_FRAME = (50, 40, 30)          # для рамок
COLOR_BORDER = (35, 25, 20)         # для обводки блоков

main_font = pygame.font.Font('font.otf', 85)
font = pygame.font.Font('font.otf', 35)
font2 = pygame.font.SysFont('arial', 20, bold=True)
title_tetris = main_font.render("TETRIS", True, COLOR_TEXT_DARK)
title_score = font.render("БАЛЛЫ", True, COLOR_TEXT_DARK)
title_record = font.render("РЕКОРД", True, COLOR_TEXT_DARK)
title_next = font2.render("следующая фигура:", True, COLOR_TEXT_BRIGHT)

figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

#подсчет баллов
score, lines = 0, 0
scores = {0:0,
          1:100,
          2:300,
          3:700,
          4:1500}

particles = []  # список для хранения частиц(при удалении строки)
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = randrange(-4, 5)   # скорость по X (-4 до 4)
        self.vy = randrange(-8, -2)  # скорость по Y (вверх, от -8 до -2)
        self.size = randrange(4, 12)  # размер частицы
        self.life = 30  # жизнь в кадрах
        self.angle = randrange(0, 360)  # для вращения
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # гравитация
        self.life -= 1
        self.angle += 5  # вращение
        
    def draw(self, surface):
        if self.life > 0:
            # Цвет затухает с жизнью
            alpha = min(255, self.life * 8)
            # Создаём поверхность с прозрачностью
            particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            color_with_alpha = (*self.color, min(255, alpha))
            pygame.draw.rect(particle_surface, color_with_alpha, (0, 0, self.size, self.size))
            # Поворачиваем частицу
            rotated = pygame.transform.rotate(particle_surface, self.angle)
            surface.blit(rotated, (self.x, self.y))

#проверка границ поля
def check_borders():
    for i in range(4):
        if figure[i].x < 0 or figure[i].x > W - 1:
            return False
        elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
            return False
    return True

#получение рекорда из файла
def get_record():
    try:
        with open('record.txt') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record.txt','w') as f:
            f.write('0')

#установка нового рекорда
def set_record(record, score):
    rec = max(int(record),score)
    with open('record.txt','w') as f:
        f.write(str(rec))

#отрисовка блока с тенями и т.п
def draw_block(surface, color, x, y): 
    rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, (35, 25, 20), rect, 2)
    pygame.draw.line(surface, (min(255, color[0] + 40), 
                               min(255, color[1] + 40), 
                               min(255, color[2] + 40)),
                     (x * TILE + 2, y * TILE + 2),
                     (x * TILE + TILE - 3, y * TILE + 2), 2)
    pygame.draw.line(surface, (min(255, color[0] + 40), 
                               min(255, color[1] + 40), 
                               min(255, color[2] + 40)),
                     (x * TILE + 2, y * TILE + 2),
                     (x * TILE + 2, y * TILE + TILE - 3), 2)
    pygame.draw.line(surface, (max(0, color[0] - 40), 
                               max(0, color[1] - 40), 
                               max(0, color[2] - 40)),
                     (x * TILE + 2, y * TILE + TILE - 3),
                     (x * TILE + TILE - 3, y * TILE + TILE - 3), 2)
    pygame.draw.line(surface, (max(0, color[0] - 40), 
                               max(0, color[1] - 40), 
                               max(0, color[2] - 40)),
                     (x * TILE + TILE - 3, y * TILE + 2),
                     (x * TILE + TILE - 3, y * TILE + TILE - 3), 2)
#начальный экран   
start_screen = True
while start_screen:
    sc.blit(bg, (0, 0))
    sc.blit(game_sc, (20, 20))
    game_sc.blit(game_bg, (0, 0))
    
    # Показываем превью фигур
    for y, row in enumerate(field):
        for x, col in enumerate(row):
            if col:
                draw_block(game_sc, col, x, y)
    
    for i in range(4):
        draw_block(game_sc, color, figure[i].x, figure[i].y)
    
    sc.blit(title_score, (525, 400))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (575, 450))
    sc.blit(title_record, (670, 400))
    sc.blit(font.render(str(get_record()), True, pygame.Color('white')), (700, 450))
    
    title_text = main_font.render("TETRIS", True, (50, 40, 30))
    sc.blit(title_text, (525, 150))
    
    start_text = font.render("Нажми SPACE для старта", True, (50, 40, 30))
    sc.blit(start_text, (60, 400))
    
    controls_text1 = font2.render("← →  - движение", True, (50, 40, 30))
    controls_text2 = font2.render("↑    - поворот", True, (50, 40, 30))
    controls_text3 = font2.render("↓    - быстрое падение", True, (50, 40, 30))
    controls_text4 = font2.render("R    - начать сначала", True, (50, 40, 30))
    sc.blit(controls_text1, (165, 550))
    sc.blit(controls_text2, (165, 600))
    sc.blit(controls_text3, (165, 650))
    sc.blit(controls_text4, (165, 700))
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                start_screen = False
            if event.key == pygame.K_r:
                # рестарт на стартовом экране
                field = [[0 for i in range(W)] for j in range(H)]
                score, lines = 0, 0
                anim_count, anim_speed, anim_limit = 0, 60, 2000
                figure, color = deepcopy(choice(figures)), get_color()
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                particles.clear()
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    exit()
    
    clock.tick(fps)

#экран поражения
def show_game_over_screen(score, record):
    game_over = True
    
    # Затемнение фона
    overlay = pygame.Surface(RES)
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    
    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return 'restart'
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    exit()
                if event.key == pygame.K_SPACE:
                    return 'restart'
    
        sc.blit(bg, (0, 0))
        sc.blit(game_sc, (20, 20))
        sc.blit(overlay, (0, 0))
        
        # Рамка Game Over
        game_over_rect = pygame.Rect(RES[0]//2 - 250, RES[1]//2 - 150, 500, 350)
        pygame.draw.rect(sc, (40, 35, 30), game_over_rect)
        pygame.draw.rect(sc, (80, 70, 60), game_over_rect, 3)
        
        game_over_font = pygame.font.Font('font.otf', 72)
        game_over_text = game_over_font.render("GAME OVER", True, (220, 180, 140))
        sc.blit(game_over_text, (RES[0]//2 - game_over_text.get_width()//2, RES[1]//2 - 100))
        
        # Результаты
        result_font = pygame.font.Font('font.otf', 36)
        score_text = result_font.render(f"СЧЁТ: {score}", True, (255, 255, 255))
        sc.blit(score_text, (RES[0]//2 - score_text.get_width()//2, RES[1]//2 - 20))
        
        # Рекорд
        if score > int(record):
            record_text = result_font.render(f"НОВЫЙ РЕКОРД!", True, (255, 215, 0))
        else:
            record_text = result_font.render(f"РЕКОРД: {record}", True, (200, 200, 200))
        sc.blit(record_text, (RES[0]//2 - record_text.get_width()//2, RES[1]//2 + 30))
        
        # Подсказки
        hint_font = pygame.font.Font('font.otf', 24)
        restart_text = hint_font.render("Нажми R или SPACE для новой игры", True, (150, 140, 130))
        sc.blit(restart_text, (RES[0]//2 - restart_text.get_width()//2, RES[1]//2 + 100))
        
        quit_text = hint_font.render("Нажми Q или ESC для выхода", True, (150, 140, 130))
        sc.blit(quit_text, (RES[0]//2 - quit_text.get_width()//2, RES[1]//2 + 140))
        
        pygame.display.flip()
        clock.tick(fps)

paused = False
while True:
    record = get_record()
    dx, rotate = 0, False
    sc.blit(bg,(0,0))
    sc.blit(game_sc,(20,20))
    game_sc.blit(game_bg,(0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            if event.key == pygame.K_RIGHT:
                dx = 1
            if event.key == pygame.K_DOWN:
                anim_limit = 100
            if event.key == pygame.K_UP:
                rotate = True
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_r:  # рестарт
                paused = False
                field = [[0 for i in range(W)] for j in range(H)]
                score, lines = 0, 0
                anim_count,anim_speed, anim_limit = 0, 60, 2000
                figure, color = deepcopy(choice(figures)), get_color()
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                particles.clear()
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    exit()
    
    if paused:
        game_sc.blit(game_bg, (0, 0))
        
        for i_rect in grid:
            pygame.draw.rect(game_sc, (40, 60, 40), i_rect, 1)
        
        for y, row in enumerate(field):
            for x, col in enumerate(row):
                if col:
                    draw_block(game_sc, col, x, y)
        
        for i in range(4):
            draw_block(game_sc, color, figure[i].x, figure[i].y)
        
        sc.blit(bg, (0, 0))
        sc.blit(game_sc, (20, 20))
        
        frame_rect = pygame.Rect(550, 120, 240, 220)
        pygame.draw.rect(sc, (30, 25, 20), frame_rect)
        pygame.draw.rect(sc, (80, 70, 60), frame_rect, 3)
        pygame.draw.rect(sc, (50, 40, 30), frame_rect, 1)
        
        for block in next_figure:
            block_surface = pygame.Surface((TILE, TILE))
            draw_block(block_surface, next_color, 0, 0)  
            sc.blit(block_surface, (block.x * TILE + offset_x, block.y * TILE + offset_y))
        
        sc.blit(title_tetris, (520, 20))
        sc.blit(title_score, (525, 400))
        sc.blit(font.render(str(score), True, pygame.Color('white')), (575, 450))
        sc.blit(title_record, (670, 400))
        sc.blit(font.render(str(record), True, pygame.Color('white')), (700, 450))
        sc.blit(title_next, (565, 130))
        
        pause_text = main_font.render("ПАУЗА", True, (50, 40, 30))
        sc.blit(pause_text, (125, 400))
        
        pygame.display.flip()
        clock.tick(fps)
        continue

    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break

    #движение вниз    
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)

        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_limit = 2000
                break

    #поворот
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x -x
            figure[i].y = center.y +y
            if not check_borders():
                figure = deepcopy(figure_old)
                break
     
    # удаление строк        
    row = H - 1
    rows_cleared = 0
    while row >= 0:
        if all(field[row]):  # строка полностью заполнена
            # Создаём частицы для каждого блока в строке
            for x in range(W):
                if field[row][x]:
                    for _ in range(4):
                        particles.append(Particle(
                            x * TILE + randrange(0, TILE),
                            row * TILE + randrange(0, TILE),
                            field[row][x]
                        ))
            
            # Удаляем строку (сдвигаем все вышестоящие строки вниз)
            for r in range(row, 0, -1):
                field[r] = field[r-1][:]
            field[0] = [0] * W
            
            rows_cleared += 1
            # Не уменьшаем row — проверяем ту же позицию снова
        else:
            row -= 1  # переходим к следующей строке

    # Начисляем очки один раз за все удалённые строки
    if rows_cleared > 0:
        score += scores[rows_cleared]
        anim_speed = min(300, anim_speed + rows_cleared * 3)
        lines += rows_cleared

    [pygame.draw.rect(game_sc,(40,60,40),i_rect,1) for i_rect in grid] #отрисовка сетки
    
    for i in range(4): #фигура
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        draw_block(game_sc, color, figure[i].x, figure[i].y)

    for particle in particles[:]:
        particle.update()
        particle.draw(game_sc)
        if particle.life <= 0:
            particles.remove(particle)

    for y, row in enumerate(field): #отрисовка
        for x, col in enumerate(row):
            if col:
                draw_block(game_sc, col, x, y)

    # Рамка для след. фигуры
    frame_rect = pygame.Rect(550, 120, 240, 220)
    pygame.draw.rect(sc, (30, 25, 20), frame_rect)
    pygame.draw.rect(sc, (80, 70, 60), frame_rect, 3)
    pygame.draw.rect(sc, (50, 40, 30), frame_rect, 1)
    # Центрирование фигуры внутри рамки
    min_x = min(block.x for block in next_figure)
    max_x = max(block.x for block in next_figure)
    min_y = min(block.y for block in next_figure)
    max_y = max(block.y for block in next_figure)
    fig_width = (max_x - min_x + 1) * TILE
    fig_height = (max_y - min_y + 1) * TILE
    # Смещение для центрирования
    offset_x = 550 + (240 - fig_width) // 2 - min_x * TILE
    offset_y = 120 + (240 - fig_height) // 2 - min_y * TILE

    # След. фигура с центрированием
    for block in next_figure:
        block_surface = pygame.Surface((TILE, TILE))
        draw_block(block_surface, next_color, 0, 0)  
        sc.blit(block_surface, (block.x * TILE + offset_x, block.y * TILE + offset_y))

    sc.blit(title_tetris, (520, 20))
    sc.blit(title_score, (525, 400))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (575, 450))
    sc.blit(title_record, (670, 400))
    sc.blit(font.render(str(get_record()), True, pygame.Color('white')), (700, 450))
    sc.blit(title_next,(565,130))

    game_over_flag = False
    for i in range(W):
        if field[0][i]:
            set_record(record, score)
            
            result = show_game_over_screen(score, record)
            
            if result == 'restart':
                # Перезапуск игры
                field = [[0 for i in range(W)] for j in range(H)]
                anim_count, anim_speed, anim_limit = 0, 60, 2000
                score, lines = 0, 0
                figure, color = deepcopy(choice(figures)), get_color()
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                paused = False
                game_over_flag = True
                continue
            break

    if game_over_flag:
        continue

    pygame.display.flip()
    clock.tick(fps)
