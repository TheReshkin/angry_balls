import pygame
import sys
import math
import random

# Инициализация Pygame
pygame.init()

# Установка размеров окна
WIDTH, HEIGHT = 500, 400

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


# Создание класса для интерактивного объекта
class Ball(pygame.sprite.Sprite):
    def __init__(self, color, radius, position, speed, enemy):
        super().__init__()
        self.color = color
        self.radius = radius
        self.position = pygame.math.Vector2(position)
        self.speed = speed  # Скорость передвижения
        self.max_speed = speed  # Максимальная скорость
        self.direction = pygame.math.Vector2(random.uniform(-1, 1),
                                             random.uniform(-1, 1)).normalize()  # Случайное направление
        self.tick_counter = 0  # Счетчик тиков
        self.max_ticks = 30  # Максимальное количество тиков перед сменой направления
        self.health = 100  # Здоровье
        self.enemy = enemy  # Враг

        # Создание прямоугольника для шара
        self.image = pygame.Surface((radius * 2, radius * 2))
        self.image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=position)

    def update(self):
        # Изменение положения шара с учетом скорости и направления
        self.position += self.direction * self.speed

        # Проверка на столкновение с границами окна
        if self.position.x - self.radius < 0 or self.position.x + self.radius > WIDTH:
            self.direction.x *= -1
        if self.position.y - self.radius < 0 or self.position.y + self.radius > HEIGHT:
            self.direction.y *= -1

        # Проверка на максимальную скорость
        if self.speed > self.max_speed:
            self.speed = self.max_speed

        # Изменение направления через определенное количество тиков
        self.tick_counter += 1
        if self.tick_counter >= self.max_ticks:
            self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
            self.tick_counter = 0

        # Попытка избежать попадания в углы
        if self.position.x - self.radius < 50 and self.position.y - self.radius < 50:
            self.direction = pygame.math.Vector2(1, 1).normalize()
        elif self.position.x + self.radius > WIDTH - 50 and self.position.y - self.radius < 50:
            self.direction = pygame.math.Vector2(-1, 1).normalize()
        elif self.position.x - self.radius < 50 and self.position.y + self.radius > HEIGHT - 50:
            self.direction = pygame.math.Vector2(1, -1).normalize()
        elif self.position.x + self.radius > WIDTH - 50 and self.position.y + self.radius > HEIGHT - 50:
            self.direction = pygame.math.Vector2(-1, -1).normalize()

        # Обновление позиции прямоугольника
        self.rect.center = self.position

        # # Периодическое выстреливание снарядов во врага
        # if random.random() < 0.01:  # Вероятность выстрела
        #     direction_to_enemy = (self.enemy.position - self.position).normalize()
        #     bullet = Bullet(self.color, 5, self.position, 8, direction_to_enemy)
        #     bullets.add(bullet)
        #     all_sprites.add(bullet)

    def draw_health(self, screen):
        # Отображение индикатора здоровья в левом верхнем углу окна
        font = pygame.font.SysFont(None, 24)
        health_text = font.render("Health: " + str(self.health), True, self.color)
        if self.color == RED:
            screen.blit(health_text, (10, 40))  # Отображение здоровья красного шара ниже
        else:
            screen.blit(health_text, (10, 10))  # Отображение здоровья зеленого шара выше


class Ball_AI(Ball):
    def __init__(self, color, radius, position, speed, enemy):
        super().__init__(color, radius, position, speed, enemy)

    def update(self):
        super().update()
        # Управление поведением зеленого шара
        if self.color == GREEN:
            # Если здоровье зеленого шара меньше 50, отправить запрос на помощь красному шару
            if self.health < 50:
                self.move_towards_enemy()
            # Иначе, если зеленый шар находится ближе к красному шару, чем к центру окна, двигаться в сторону красного шара
            elif self.distance_to_enemy() < self.distance_to_center():
                self.move_towards_enemy()
            # Иначе, если зеленый шар находится далеко от красного шара и ближе к центру окна, двигаться к центру окна
            else:
                if random.random() < 0.1:
                    self.move_to_center()
        # Случайное движение в любом направлении
        else:
            self.move_randomly()

    # Вспомогательные методы для класса Ball

    def move_towards_enemy(self):
        direction_to_enemy = (self.enemy.position - self.position).normalize()
        self.direction = direction_to_enemy

    def move_to_center(self):
        center = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        direction_to_center = (center - self.position).normalize()
        self.direction = direction_to_center

    def move_randomly(self):
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

    def distance_to_enemy(self):
        return self.position.distance_to(self.enemy.position)

    def distance_to_center(self):
        center = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        return self.position.distance_to(center)

    def draw_health(self, screen):
        # Отображение индикатора здоровья в левом верхнем углу окна
        font = pygame.font.SysFont(None, 24)
        health_text = font.render("Health: " + str(self.health), True, self.color)
        if self.color == RED:
            screen.blit(health_text, (10, 40))  # Отображение здоровья красного шара ниже
        else:
            screen.blit(health_text, (10, 10))  # Отображение здоровья зеленого шара выше


class Bullet(pygame.sprite.Sprite):
    def __init__(self, color, radius, position, speed, direction, shooter):
        super().__init__()
        self.color = color
        self.radius = radius
        self.position = pygame.math.Vector2(position)
        self.speed = min(speed, 5 * max_ball_speed)  # Ограничение скорости снаряда
        self.direction = direction
        self.rect = pygame.Rect(position[0], position[1], radius * 2, radius * 2)
        self.shooter = shooter
        # Создаем изображение для звездочки
        self.image = pygame.Surface((radius * 2, radius * 2))
        self.image.set_colorkey((0, 0, 0))
        pygame.draw.polygon(self.image, self.color, [(self.radius, 0), (self.radius * 2, self.radius * 2 // 3),
                                                     (self.radius * 3 // 2, self.radius * 2),
                                                     (self.radius // 2, self.radius * 2),
                                                     (0, self.radius * 2 // 3)])

    def update(self):
        # Перемещение снаряда в заданном направлении с учетом скорости
        self.position += self.direction * self.speed
        self.rect.center = self.position


# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Window")

clock = pygame.time.Clock()  # Создание объекта Clock для управления частотой кадров


def new_obj():
    # Создание объектов
    red_ball = Ball(RED, 20, (WIDTH // 4, HEIGHT // 4), 5, None)  # Первый шар, его враг пока не определен
    green_ball = Ball_AI(GREEN, 20, (WIDTH * 3 // 4, HEIGHT * 3 // 4), 5,
                         red_ball)  # Второй шар, его враг - красный шар
    red_ball.enemy = green_ball  # Определение врага для красного шара
    balls = pygame.sprite.Group([red_ball, green_ball])

    bullets = pygame.sprite.Group()

    # Создание группы спрайтов
    all_sprites = pygame.sprite.Group()
    all_sprites.add(balls)
    return all_sprites, bullets, balls


def draw_stats(screen, death):
    font = pygame.font.SysFont(None, 24)

    # Рассчитываем высоту текста для каждой строки
    font_height = font.get_height()

    # Устанавливаем начальную позицию для текста в левом нижнем углу
    x = 20  # Отступ от левого края
    y = screen.get_height() - font_height * len(death) - 10  # Отступ от нижнего края

    # Отображение количества смертей для каждого цвета шара
    for color, count in death.items():
        death_text = font.render(f"{color}: {count}", True, (122, 122, 122))
        screen.blit(death_text, (x, y))
        y += font_height  # Перемещаем следующий текст на следующую строку

all_sprites, bullets, balls = new_obj()
max_ball_speed = 5  # Максимальная скорость шаров

death = {'Green': 0, 'Red': 0}
# Главный игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Обновление состояния спрайтов
    all_sprites.update()
    # Создание новых пуль
    for ball in balls:
        if random.random() < 0.01:  # Вероятность выстрела
            direction_to_enemy = (ball.enemy.position - ball.position).normalize()
            bullet = Bullet(ball.color, 5, ball.position, 8, direction_to_enemy, ball)
            bullets.add(bullet)
            all_sprites.add(bullet)
        if ball.health <= 0:
            color = 'Green' if ball.color == (0, 255, 0) else 'Red'
            death[color] += 1
            draw_stats(screen, death)
            print(death)
            all_sprites, bullets, balls = new_obj()

    # Проверка столкновений между шарами и снарядами и уменьшение здоровья при попадании
    for bullet in bullets:
        for ball in balls:
            if pygame.sprite.collide_circle(bullet, ball) and ball != bullet.shooter:
                ball.health -= 10
                # bullets.remove(bullet)
                # bullet.kill()

    # Очистка экрана
    screen.fill(WHITE)

    # Отрисовка спрайтов и индикаторов здоровья
    for ball in balls:
        ball.draw_health(screen)
    all_sprites.draw(screen)

    # Отображение
    pygame.display.flip()

    clock.tick(1000)  # Установка частоты кадров на 30 FPS

# Завершение работы Pygame
pygame.quit()
sys.exit()
