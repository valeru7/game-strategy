import pygame
import random

WIDTH, HEIGHT = 800, 600
ROAD_WIDTH = WIDTH // 3
SPEED = 5
BULLET_SPEED = 10
LIVES = 10
MONEY = 100
ENEMY_DETERMINATION = 3500  # Начальная решимость врага
sabotage_cost = 100  # Начальная цена саботажа
new_button_cost = 10  # Начальная цена кнопки Казарма
shoot_delay = 300  # Начальная задержка между выстрелами
initial_spawn_rate = 30  # Начальная частота спауна врагов
rollback_cost = 50  # Начальная цена кнопки "Откат"

# Цвета
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
# Настройка звука
pygame.mixer.init()


# Настройка экрана
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enemy Run Game")

# Загрузка музыки
pygame.mixer.music.load("Sound_17248.mp3")
pygame.mixer.music.play(-1)  # -1 для зацикливания музыки

# Шрифт для отображения жизней и денег
font = pygame.font.Font(None, 36)

# Загрузка изображений
background_image = pygame.transform.scale(pygame.image.load("1.png"), (800, 600))
enemy_image = pygame.image.load("sprite1.png")
enemy_image = pygame.transform.scale(enemy_image, (50, 50))
bullet_image = pygame.transform.scale(pygame.image.load("sprite2.png"), (50, 55))  # Увеличение изображения пули

class Enemy:
    def __init__(self, road):
        self.x = road * ROAD_WIDTH + (ROAD_WIDTH - 50) // 2
        self.y = 0

    def move(self):
        self.y += SPEED

    def draw(self):
        screen.blit(enemy_image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 50, 50)

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        self.y -= BULLET_SPEED

    def draw(self):
        screen.blit(bullet_image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 20, 10)  # Обновление размеров для коллизии

class Button:
    def __init__(self, text, x, y, width, height, cost):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.cost = cost

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)  # Рисуем кнопку
        text_surface = font.render(f"{self.text} (Цена: {self.cost})", True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)  # Рисуем текст на кнопке

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)  # Проверяем, нажата ли кнопка

def main():
    global LIVES, MONEY, ENEMY_DETERMINATION, sabotage_cost, shoot_delay, spawn_rate, rollback_cost
    clock = pygame.time.Clock()
    enemies = []
    bullets = []
    spawn_timer = 0
    last_shot_time = 0  # Время последнего выстрела
    spawn_rate = initial_spawn_rate  # Устанавливаем начальную частоту спауна

    # Создаем кнопки
    sabotage_button = Button("Саботаж", WIDTH // 2 - 50, HEIGHT - 100, 150, 50, sabotage_cost)
    new_button = Button("Казарма", ROAD_WIDTH // 2 - 75, HEIGHT - 100, 150, 50, new_button_cost)  # Цена кнопки Казарма равна 10
    rollback_button = Button("Откат", ROAD_WIDTH * 2 + 50, HEIGHT - 100, 150, 50, rollback_cost)  # Кнопка "Откат"

    running = True
    while running:
        screen.blit(background_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левый клик мыши
                    if sabotage_button.is_clicked(event.pos):
                        if MONEY >= sabotage_button.cost:  # Проверяем, достаточно ли денег
                            ENEMY_DETERMINATION -= 1000  # Уменьшаем решимость врага
                            MONEY -= sabotage_button.cost  # Уменьшаем деньги
                            print(f"Саботаж! Решимость врага упала на 1000, деньги уменьшены на {sabotage_button.cost}.")
                            sabotage_button.cost = int(sabotage_button.cost * 1.5)  # Увеличиваем цену саботажа на 50%
                        else:
                            print("Недостаточно денег для саботажа!")

                    if new_button.is_clicked(event.pos):
                        if MONEY >= new_button.cost:  # Проверяем, достаточно ли денег для кнопки Казарма
                            MONEY -= new_button.cost
                            print("Казарма нажата!")
                            new_button.cost = int(new_button.cost * 1.5)  # Увеличиваем цену на 50%
                            global shoot_delay  # Указываем, что мы будем использовать глобальную переменную
                            shoot_delay = max(10, shoot_delay - 9)  # Уменьшаем задержку на 9 мс, минимум 10 мс
                        else:
                            print("Недостаточно денег для кнопки Казарма!")

                    if rollback_button.is_clicked(event.pos):
                        if MONEY >= rollback_button.cost:  # Проверяем, достаточно ли денег для кнопки "Откат"
                            spawn_rate = initial_spawn_rate  # Возвращаем спаун врагов к начальной частоте
                            MONEY -= rollback_button.cost  # Уменьшаем деньги
                            rollback_button.cost = int(rollback_button.cost * 1.5)  # Увеличиваем цену на 50%
                            print("Спаун врагов возвращён к начальному значению!")
                        else:
                            print("Недостаточно денег для кнопки Откат!")

        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()  # Текущее время в миллисекундах

        if keys[pygame.K_a] and current_time - last_shot_time > shoot_delay:
            shoot_bullet(0, bullets)
            last_shot_time = current_time
        if keys[pygame.K_s] and current_time - last_shot_time > shoot_delay:
            shoot_bullet(1, bullets)
            last_shot_time = current_time
        if keys[pygame.K_d] and current_time - last_shot_time > shoot_delay:
            shoot_bullet(2, bullets)
            last_shot_time = current_time

        spawn_timer += 1
        if spawn_timer > spawn_rate:
            road = random.randint(0, 2)
            enemies.append(Enemy(road))
            spawn_timer = 0
            # Увеличиваем частоту спауна врагов каждые 1000 мс
            if current_time // 1000 % 10 == 0:  # Каждые 10 секунд
                spawn_rate = max(10, spawn_rate - 2)  # Увеличиваем скорость спауна

        for enemy in enemies[:]:
            enemy.move()
            if enemy.y > HEIGHT:
                enemies.remove(enemy)
                LIVES -= 1
                MONEY -= 5
            enemy.draw()

        for bullet in bullets[:]:
            bullet.move()
            if bullet.y < 0:
                bullets.remove(bullet)
                MONEY += 3
            else:
                bullet.draw()
                for enemy in enemies[:]:
                    if bullet.get_rect().colliderect(enemy.get_rect()):
                        bullets.remove(bullet)
                        enemies.remove(enemy)
                        MONEY += 4  # Увеличиваем монеты за убийство врага до 4
                        ENEMY_DETERMINATION -= 1  # Уменьшаем решимость врага
                        break

        # Отображаем жизни, деньги и решимость врага
        lives_text = font.render(f"Lives: {LIVES}", True, GREEN)
        money_text = font.render(f"Money: {MONEY}", True, YELLOW)
        determination_text = font.render(f"Решимость врага: {ENEMY_DETERMINATION}", True, RED)
        screen.blit(lives_text, (10, 10))
        screen.blit(money_text, (10, 50))
        screen.blit(determination_text, (10, 90))

        # Проверка на победу
        if ENEMY_DETERMINATION <= 0:
            print("Вы победили!")
            running = False

        # Рисуем кнопки
        sabotage_button.draw()
        new_button.draw()
        rollback_button.draw()  # Рисуем кнопку "Откат"

        if LIVES <= 0:
            running = False
            print("Game Over!")

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def shoot_bullet(road, bullets):
    global MONEY
    if MONEY > 0:
        bullets.append(Bullet(road * ROAD_WIDTH + (ROAD_WIDTH - 20) // 2, HEIGHT - 50))  # Увеличение позиции пули
        MONEY -= 1