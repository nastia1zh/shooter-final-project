# підключаємо потрібні нам бібліотеки
from pygame import *
from random import randint
from time import time as timer

# фонова музика
mixer.init()
mixer.music.load("space.mp3")
mixer.music.play()
fire_sound = mixer.Sound("fire.ogg")

# шрифти і написи
font.init()
font1 = font.SysFont('Arial', 80)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))
font2 = font.SysFont('Arial', 36)

# картинки, які ми використовуємо
img_back = "font.gif" # фон гри
img_hero = "hero.png" # герой
img_enemy = "ufo.gif" # ворог
img_bullet = "bullet.png" # фаєрбол
img_ast = "ghost.png" # перешкода (привид)

lost = 0 # пропущено ворогів
score = 0 # збито ворогів
life = 3 # кількість життя
goal = 10
max_lost = 15 # програли, якщо пропустили таку кількість ворогів

# клас-бтько для інших спрайтів
class GameSprite(sprite.Sprite):
    # конструктор класу
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)

        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed

        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    # метод, який добавляє героя на екран
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# клас головного героя
class Player(GameSprite):
    # метод для управління спрайтом стрілками клавіатури
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
    # метод "вистріл"
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

# клас спрайта-ворога
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        # зникає, якщо дійде до краю екрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost = lost + 1

# клас фаєрбола
class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

# створюємо вікно
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))

# створюємо спрайти
bullets = sprite.Group()

ship = Player(img_hero, 5, 400, 80, 100, 10)

monsters = sprite.Group()
for i in range(1, 6):
    monster = Enemy(img_enemy, randint (80, win_width-80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)

asteroids = sprite.Group()
for i in range(3):
    asteroid = Enemy(img_ast, randint (80, win_width-80), -40, 80, 50, randint(1, 7))
    asteroids.add(asteroid)

finish = False
run = True
rel_time = False # змінна-перемикач з логічними значеннями, що відповідає питанням "Чи йде перезарядка?"
num_fire = 0 # півдрахунок кількості скоєних пострілів

# ігровий цикл:
while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        # подія натиску на пробіл - спрайт стріляє
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                    if num_fire < 5 and rel_time == False:
                        num_fire = num_fire + 1
                        fire_sound.play()
                        ship.fire()
                    if num_fire  >= 5 and rel_time == False : 
                        last_time = timer() 
                        rel_time = True 

    if not finish:
        window.blit(background,(0,0))
        
        # рух спрайтів
        ship.update()
        monsters.update()
        asteroids.update()
        bullets.update()
        
        # оновлюємо їх у новому місці
        ship.reset()
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)

    if rel_time == True:
       now_time = timer()
       # встановлюємо час перезарядки 3 секунди
       if now_time - last_time < 3:
           reload = font2.render('Wait, reload...', 1, (150, 0, 0))
           window.blit(reload, (260, 460))
       else:
           num_fire = 0   
           rel_time = False 

    # коли фаєрбол торкається ворога 
    collides = sprite.groupcollide(monsters, bullets, True, True)
    for c in collides:
        score = score + 1
        monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
        monsters.add(monster)
    
    # коли герой торкається ворога, привида
    if sprite.spritecollide(ship, monsters, False) or sprite.spritecollide(ship, asteroids, False):
        sprite.spritecollide(ship, monsters, True)
        sprite.spritecollide(ship, asteroids, True)
        life = life - 1
    
    if life == 0 or lost >= max_lost:
        finish = True
        window.blit(lose, (200, 200))

    if score >= goal:
        finish = True
        window.blit(win, (200, 200))
    
    # пишемо текст на екрані
    text = font2.render("Рахунок: " + str(score), 1, (255, 255, 255))
    window.blit(text, (10, 20))

    text_lose = font2.render("Пропущено: " + str(lost), 1, (255, 255, 255))
    window.blit(text_lose, (10, 50))

    if life == 3:
        life_color = (0, 150, 0)
    if life == 2:
        life_color = (150, 150, 0)
    if life == 1:
        life_color = (150, 0, 0)

    text_life = font1.render(str(life), 1, life_color)
    window.blit(text_life, (650, 10))

    display.update()

    time.delay(50)
