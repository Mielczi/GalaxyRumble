import pygame
from random import randint
from abc import ABC, abstractmethod

pygame.init()
resolution = (1280, 720)
window = pygame.display.set_mode(resolution)
pygame.display.set_caption('GalaxyRumble')


# --- WŁASNY WYJĄTEK ---
class AmmoError(Exception):
    def __init__(self, message="BRAK AMUNICJI!"):
        super().__init__(message)


# --- STRATEGIA: STRZELANIE ---
class ShootingStrategy(ABC):
    @abstractmethod
    def shoot(self, player):
        pass


class SingleShot(ShootingStrategy):
    def shoot(self, player):
        return [Bullet(player.x_cord + player.width // 2, player.y_cord)]


class DoubleShot(ShootingStrategy):
    def shoot(self, player):
        return [
            Bullet(player.x_cord + 10, player.y_cord),
            Bullet(player.x_cord + player.width - 10, player.y_cord)
        ]

# --- KOMPOZYT I KOMENDA ---
class Ammo:
    def __init__(self, max_ammo):
        self._max_ammo = max_ammo
        self._current_ammo = max_ammo

    @property
    def current_ammo(self):
        return self._current_ammo

    @property
    def max_ammo(self):
        return self._max_ammo

    def use(self):
        if self._current_ammo <= 0:
            raise AmmoError
        self._current_ammo -= 1

    def reload(self):
        self._current_ammo = self._max_ammo

    def add_ammo(self, amount):
        self._current_ammo = min(self._current_ammo + amount, self._max_ammo)


# --- DRUGI KONTRUKTOR ---
class AmmoBox:
    def __init__(self, x_cord, y_cord, ammo_value=5):
        self.x_cord = x_cord
        self.y_cord = y_cord
        self.image = pygame.image.load('bullet.png')
        self.hitbox = pygame.Rect(x_cord, y_cord, self.image.get_width(), self.image.get_height())
        self.ammo_value = ammo_value

    @classmethod
    def random_box(cls):
        return cls(randint(50, 1230), randint(50, 670))

    def draw(self, window):
        window.blit(self.image, (self.x_cord, self.y_cord))

    def tick(self):
        self.hitbox.topleft = (self.x_cord, self.y_cord)


class Medkit:
    def __init__(self, x_cord, y_cord):
        self.x_cord = x_cord
        self.y_cord = y_cord
        self.image = pygame.image.load('apteczka.png')
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.width, self.height)

    @classmethod
    def random_medkit(cls):
        x = randint(50, 1230)
        y = randint(50, 670)
        return cls(x, y)

    def tick(self):
        self.hitbox.topleft = (self.x_cord, self.y_cord)

    def draw(self):
        window.blit(self.image, (self.x_cord, self.y_cord))


class Enemy:
    def __init__(self, image_path, speed, health):
        self.x_cord = randint(0, 1280)
        self.y_cord = randint(-200, -50)
        self.image = pygame.image.load(image_path)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.width, self.height)
        self.speed = speed
        self.health = health

    def tick(self):
        self.y_cord += self.speed
        self.hitbox.topleft = (self.x_cord, self.y_cord)

    def draw(self):
        window.blit(self.image, (self.x_cord, self.y_cord))

        max_health = 3
        health_bar_width = self.width
        health_bar_height = 5

        pygame.draw.rect(window, (255, 0, 0), (self.x_cord, self.y_cord - 10, health_bar_width, health_bar_height))

        current_health_width = health_bar_width * (self.health / max_health)
        pygame.draw.rect(window, (0, 255, 0), (self.x_cord, self.y_cord - 10, current_health_width, health_bar_height))


class TankEnemy(Enemy):
    def __init__(self):
        super().__init__('wrogi_statek_3.xcf', 2, 3)

    def tick(self):
        self.y_cord += self.speed
        self.x_cord += randint(-15, 15)
        self.hitbox.topleft = (self.x_cord, self.y_cord)


class FastEnemy(Enemy):
    def __init__(self):
        super().__init__('wrogi_statek_2.xcf', 7, 1)

    def tick(self):
        self.y_cord += self.speed
        self.x_cord += randint(-10, 10)
        self.hitbox.topleft = (self.x_cord, self.y_cord)


class ClassicEnemy(Enemy):
    def __init__(self):
        super().__init__('wrogi_statek_1.xcf', 5, 2)

    def tick(self):
        self.y_cord += self.speed
        self.x_cord += randint(-20, 20)
        self.hitbox.topleft = (self.x_cord, self.y_cord)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x_cord = 600
        self.y_cord = 600
        self.image = pygame.image.load('statek3.xcf')
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.speed = 10
        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.width, self.height)
        self.health = 3
        self.ammo = Ammo(30)
        self.shooting_strategy = SingleShot()

    def tick(self, keys):
        if keys[pygame.K_UP]:
            self.y_cord -= self.speed
        if keys[pygame.K_LEFT]:
            self.x_cord -= self.speed
        if keys[pygame.K_DOWN]:
            self.y_cord += self.speed
        if keys[pygame.K_RIGHT]:
            self.x_cord += self.speed

        self.hitbox.topleft = (self.x_cord, self.y_cord)
        self.hitbox.clamp_ip(window.get_rect())
        self.x_cord, self.y_cord = self.hitbox.topleft

    def draw(self):
        window.blit(self.image, (self.x_cord, self.y_cord))
        ammo_text = pygame.font.SysFont('arial', 30).render(f'Amunicja: {self.ammo.current_ammo}', True, (255, 255, 255))
        window.blit(ammo_text, (10, 170))

    def shoot(self):
        if self.ammo.current_ammo <= 0:
            raise AmmoError()
        self.ammo.use()
        return self.shooting_strategy.shoot(self)

    def switch_strategy(self):
        if isinstance(self.shooting_strategy, SingleShot):
            self.shooting_strategy = DoubleShot()
        else:
            self.shooting_strategy = SingleShot()

    def collect_ammo_box(self, ammo_box):
        if self.hitbox.colliderect(ammo_box.hitbox):
            self.ammo.add_ammo(ammo_box.ammo_value)
            return True
        return False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x_cord, y_cord):
        super().__init__()
        self.image = pygame.image.load("pocisk.xcf")
        self.rect = self.image.get_rect(center=(x_cord, y_cord))
        self.speed = 15

    def tick(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

    def update(self):
        self.tick()

    def draw(self):
        window.blit(self.image, self.rect.topleft)


class Coin:
    def __init__(self, x_cord, y_cord):
        self.x_cord = x_cord
        self.y_cord = y_cord
        self.image = pygame.image.load('moneta.xcf')
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.width, self.height)

    def tick(self):
        self.hitbox.topleft = (self.x_cord, self.y_cord)

    def draw(self):
        window.blit(self.image, (self.x_cord, self.y_cord))

    @staticmethod
    def random_position():
        return randint(0, 1280), randint(0, 720)


class Meteor:
    def __init__(self):
        self.x_cord = randint(0, 1280)
        self.y_cord = randint(-200, -50)
        self.image = pygame.image.load('meteor.xcf')
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.width, self.height)
        self.speed = 10

    def tick(self):
        self.y_cord += self.speed
        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.width, self.height)

    def draw(self):
        window.blit(self.image, (self.x_cord, self.y_cord))


class Background:
    def __init__(self):
        self.image = pygame.image.load('long_screen1.jpg')
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.y1_cord = 0
        self.y2_cord = -self.height

    def tick(self, player):
        self.y1_cord += 7
        self.y2_cord += 7

        if self.y1_cord >= resolution[1]:
            self.y1_cord = self.y2_cord - self.height
        if self.y2_cord >= resolution[1]:
            self.y2_cord = self.y1_cord - self.height

    def draw(self):
        window.blit(self.image, (0, self.y1_cord))
        window.blit(self.image, (0, self.y2_cord))


def spawn_enemy():
    enemy_types = [TankEnemy, FastEnemy, ClassicEnemy]
    return enemy_types[randint(0, 2)]()


class Button:
    def __init__(self, x_cord, y_cord):
        self.x_cord = x_cord
        self.y_cord = y_cord
        self.button_image = pygame.image.load('play_button.png')
        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.button_image.get_width(), self.button_image.get_height())

    def tick(self):
        if self.hitbox.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                return True

    def draw(self, window):
        window.blit(self.button_image, (self.x_cord, self.y_cord))


def loading_screen():
    run = True
    loading_screen_image = pygame.image.load('loading_screen.jpg')
    play_button = Button(385, 532)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        window.blit(loading_screen_image, (0, 0))
        play_button.draw(window)

        if play_button.tick():
            run = False

        pygame.display.update()


def hardcore():
    run = True
    game_over = False
    game_over_image = pygame.image.load('game_over.png')
    player = Player()
    bullets = pygame.sprite.Group()
    background = Background()
    clock = 0
    coin_clock = 0
    coin_count = 0
    enemy_clock = 0
    medkit_clock = 0
    ammo_clock = 0

    points = 0
    coins = []
    meteors = []
    enemies = []
    medkits = []
    ammo_boxes = []
    font = pygame.font.SysFont('arial', 30)

    while run:
        delta_time = pygame.time.Clock().tick(60) / 1000
        clock += delta_time
        coin_clock += delta_time
        enemy_clock += delta_time
        medkit_clock += delta_time
        ammo_clock += delta_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    try:
                        new_bullets = player.shoot()
                        bullets.add(*new_bullets)
                    except AmmoError as e:
                        print(e)
        if game_over:
            window.blit(game_over_image, (0, 0))
            restart_text = font.render('Press R to Restart', True, (255, 255, 255))
            window.blit(restart_text, (resolution[0] // 2 - 100, resolution[1] // 2 + 50))
            pygame.display.update()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                hardcore()
            continue

        keys = pygame.key.get_pressed()
        player.tick(keys)
        bullets.update()

        if ammo_clock >= 10:  # co 10 sekund
            ammo_clock = 0
            if len(ammo_boxes) < 2:  # maksymalnie 2 pudełka na ekranie
                ammo_boxes.append(AmmoBox.random_box())

        if coin_clock >= 6:
            coin_clock = 0
            x, y = Coin.random_position()
            coins.append(Coin(x, y))

        if medkit_clock >= 15:
            medkit_clock = 0
            medkits.append(Medkit.random_medkit())

        if enemy_clock >= 5:
            enemy_clock = 0
            enemy = spawn_enemy()
            if enemy:
                enemies.append(enemy)

        if clock >= 3:
            clock = 0
            meteors.append(Meteor())

        for coin in coins:
            coin.tick()

        for medkit in list(medkits):
            if player.hitbox.colliderect(medkit.hitbox):
                player.health = 3
                medkits.remove(medkit)

        for meteor in list(meteors):
            if player.hitbox.colliderect(meteor.hitbox):
                player.health -= 1
                meteors.remove(meteor)
                if player.health <= 0:
                    game_over = True

        for enemy in list(enemies):
            if player.hitbox.colliderect(enemy.hitbox):
                game_over = True

        for enemy in list(enemies):
            enemy.tick()

        background.tick(player)

        for coin in list(coins):
            if player.hitbox.colliderect(coin.hitbox):
                coins.remove(coin)
                coin_count += 1
                if coin_count == 3:
                    points += 1
                    coin_count = 0

        background.draw()

        score_image = font.render(f'Punkty: {points}', True, (255, 255, 255))
        health_image = font.render(f'Zdrowie: {player.health}', True, (255, 0, 0))
        coin_image = font.render(f'Monety: {coin_count}/3', True, (255, 255, 0))
        enemy_count_text = font.render(f'Wrogowie: {len(enemies)}', True, (255, 255, 255))

        window.blit(score_image, (10, 10))
        window.blit(health_image, (10, 50))
        window.blit(coin_image, (10, 90))
        window.blit(enemy_count_text, (10, 130))

        player.draw()

        for enemy in enemies:
            enemy.draw()

        for bullet in list(bullets):
            for meteor in list(meteors):
                if bullet.rect.colliderect(meteor.hitbox):
                    bullet.kill()
                    meteors.remove(meteor)
                    points += 1
                    break

            for enemy in list(enemies):
                if bullet.rect.colliderect(enemy.hitbox):
                    bullet.kill()
                    enemy.health -= 1
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        points += 5
                    break

            bullet.draw()

            for box in ammo_boxes:
                if player.collect_ammo_box(box):
                    ammo_boxes.remove(box)
                    ammo_boxes.append(AmmoBox.random_box())

        for box in ammo_boxes:
            box.draw(window)
            box.tick()

        for coin in coins:
            coin.draw()

        for meteor in meteors:
            meteor.draw()
            meteor.tick()

        for medkit in medkits:
            medkit.draw()

        pygame.display.update()


if __name__ == '__main__':
    loading_screen()
    hardcore()
