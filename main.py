import random
import pygame as pg   
import pygame_menu



pg.init()

SCREEN_WIDTH = 900 
SCREEN_HEIGHT = 550

CHARACTER_WIDTH = 300 
CHARACTER_HEIGHT = 375

FPS = 60

font = pg.font.Font(None, 40)

def load_image(file, width, height):
    image = pg.image.load(file).convert_alpha()
    image = pg.transform.scale(image, (width, height))
    return image

def text_render(text):
    return font.render(str(text), True, "black")


class Enemy(pg.sprite.Sprite):
    def __init__(self, folder):
        super().__init__()
        self.folder = folder
        self.load_animations()

        self.hp = 200

        self.image = self.idle_animation_left[0]
        self.current_image = 0
        self.current_animation = self.idle_animation_left

        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)

        self.timer = pg.time.get_ticks()
        self.interval = 300
        self.side = "left"
        self.animation_mode = True

        self.magic_balls = pg.sprite.Group()

        self.attack_mode = False
        self.attack_interval = 500

        self.move_interval = 800
        self.move_duration = 0
        self.direction = 0
        self.move_timer = pg.time.get_ticks()
        
        self.charge_power = 0 


    def load_animations(self):
        self.idle_animation_right = [load_image(f"images/{self.folder}/idle{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
                                     for i in range(1,4)]
        
        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

        self.move_animation_right = [load_image(f"images/{self.folder}/move{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)
                                     for i in range(1,5)]
        
        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

        self.attack = [load_image(f"images/{self.folder}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack.append(pg.transform.flip(self.attack[0], True, False))

    def update(self, player):
        self.handle_attack_mode(player)
        self.handle_movement()
        self.handle_animation()


    def handle_attack_mode(self, player):
        
        if not self.attack_mode:
            attack_probability =1 

            if player.charge_mode:
                attack_probability += 2

            if random.randint(1,100) <= attack_probability:
                self.attack_mode = True
                self.charge_power = random.randint(1,100)

                if player.rect.centerx < self.rect.centerx:
                    self.side = "left"
                else:
                    self.side = "right"
                self.animation_mode = False
                self.image = self.attack[self.side!="right"]
            
        if self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.attack_interval:
                self.attack_mode = False
                self.timer = pg.time.get_ticks()

    
    def handle_movement(self):
        if self.attack_mode:
            return
        
        now = pg.time.get_ticks()
        
        if now - self.move_timer < self.move_duration:
            self.animation_mode = True
            self.rect.x += self.direction
            self.current_animation = self.move_animation_left if self.direction == -1 else self.move_animation_right
        else:
            if random.randint(1,100) == 1 and now - self.move_timer > self.move_interval:
                self.move_timer = pg.time.get_ticks()
                self.move_duration = random.randint(400, 1500)
                self.direction = random.choice([-1,1])
            else:
                self.animation_mode = True
                self.current_animation = self.idle_animation_left if self.side == "left" else self.idle_animation_right
        
        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
        elif self.rect.left <= 0:
            self.rect.left = 0 
        
    
        



    def handle_animation(self):
        if self.animation_mode and not self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.interval:
                self.current_image += 1
                if self.current_image >= len(self.current_animation):
                    self.current_image = 0
                self.image = self.current_animation[self.current_image]
                self.timer = pg.time.get_ticks()
        
        if self.attack_mode and self.charge_power > 0: 
            ball_position = self.rect.topright if self.side == "right" else self.rect.topleft
            self.magic_balls.add(MagicBall(ball_position, self.side, self.charge_power, self.folder))
            self.charge_power = 0 
            self.image = self.attack[self.side != "right"]
            self.timer = pg.time.get_ticks()


# Sozdadim class personagha igroka
class Player(pg.sprite.Sprite):
    def __init__(self, folder = "fire wizard", first_player = True):
        super().__init__()

        self.folder = folder

        self.load_animations()

        if first_player:
            self.coord = (100, SCREEN_HEIGHT // 2)
            self.current_animation = self.idle_animation_right
            self.side = "right"
            self.key_right = pg.K_d
            self.key_left = pg.K_a
            self.key_down = pg.K_s
            self.key_charge = pg.K_SPACE
        else:
            self.coord = (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)
            self.current_animation = self.idle_animation_left
            self.side = "left"
            self.key_right = pg.K_RIGHT
            self.key_left = pg.K_LEFT
            self.key_down = pg.K_DOWN
            self.key_charge = pg.K_RCTRL

        self.image = self.current_animation[0]
        self.current_image = 0
        self.current_animation = self.idle_animation_right
        self.rect = self.image.get_rect()
        self.rect.center = self.coord

        self.timer = pg.time.get_ticks()
        self.interval = 300 
        self.animation_mode = True

        self.charge_power = 0
        self.charge_indicator = pg.Surface((self.charge_power, 10))
        self.charge_indicator.fill("red")

        self.hp = 200


        self.charge_mode = False
        self.magic_balls = pg.sprite.Group()

        self.attack_mode = False
        self.attack_interval = 500


    
    
    
    def load_animations(self):

        self.idle_animation_right = []
        for i in range(1, 4):
            self.idle_animation_right.append(load_image(f"images/{self.folder}/idle{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT))

        self.idle_animation_left = []
        for image in self.idle_animation_right:
            self.idle_animation_left.append(pg.transform.flip(image, True, False))

        # Animatciya dwisgeniia vpravo
        self.move_animation_right = []
        for i in range(1,4):
            self.move_animation_right.append(load_image(f"images/{self.folder}/move{i}.png", CHARACTER_WIDTH, CHARACTER_HEIGHT))

        # Animatciya dwisgeniia vlevo
        self.move_animation_left = []
        for image in self.move_animation_right:
            self.move_animation_left.append(pg.transform.flip(image, True, False))


        # Prisidaniyia
        self.down = [load_image(f"images/{self.folder}/down.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.down.append(pg.transform.flip(self.down[0], True, False))

        #Podgotovka k atacke
        self.charge = [load_image(f"images/{self.folder}/charge.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.charge.append(pg.transform.flip(self.charge[0], True, False))

        #Atacka
        self.attack = [load_image(f"images/{self.folder}/attack.png", CHARACTER_WIDTH, CHARACTER_HEIGHT)]
        self.attack.append(pg.transform.flip(self.attack[0], True, False))

    
    
    
    def update(self, player=None):    
        direction = 0 

        keys = pg.key.get_pressed()

        if keys[self.key_left]:
            direction = -1
            self.side = "left"
        elif keys[self.key_right]:
            direction = 1
            self.side = "right"

        #dvishenie
        self.handle_movement(direction, keys)
            
        #animatsiya perschonaga
        self.handle_animation()


        # reghim atttacki i vozvracheniia v iskhodnuiyu positziu
        self.handle_attack_mode()


    def handle_attack_mode(self):
        if self.attack_mode:
            if pg.time.get_ticks() - self.timer > self.attack_interval:
                self.attack_mode = False
                self.timer = pg.time.get_ticks()



    def handle_movement(self, direction, keys):
        if self.attack_mode:
            return

        
        if direction != 0 :
            self.animation_mode = True
            self.charge_mode = False
            self.rect.x += direction
            # Smeniaem animaciyu
            self.current_animation = self.move_animation_left if direction == -1 else self.move_animation_right

        elif keys[self.key_down]:
            self.animation_mode = False
            self.charge_mode = False
            self.image = self.down[self.side != "right"]

        elif keys[self.key_charge]:
            self.animation_mode = False
            self.charge_mode = True
            self.image = self.charge[self.side != "right"]
        
        
        else:
            self.animation_mode = True
            self.charge_mode = False
            self.current_animation = self.idle_animation_left if self.side == "left" else self.idle_animation_right
        
        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        elif self.rect.left <= 0:
            self.rect.left = 0



    def handle_animation(self):
        if not self.charge_mode and self.charge_power > 0:
            self.attack_mode = True

        if self.animation_mode and not self.attack_mode: 
            if pg.time.get_ticks() - self.timer > self.interval:
                #pereckluchaem animaciyu na sleduyushiy cadr
                self.current_image += 1 
                if self.current_image >= len(self.current_animation):
                    self.current_image = 0
                self.image = self.current_animation[self.current_image]
                self.timer = pg.time.get_ticks()

        if self.charge_mode:
            self.charge_power += 1
            self.charge_indicator = pg.Surface((self.charge_power, 10))
            self.charge_indicator.fill("red")
            if self.charge_power == 100:
                self.attack_mode = True

        if self.attack_mode and self.charge_power > 0:
            fireball_position = self.rect.topright if self.side == "right" else self.rect.topleft
            #sozdaiom fireball
            self.magic_balls.add(MagicBall(fireball_position, self.side, self.charge_power, self.folder))

            self.charge_power = 0 
            self.charge_mode = False
            self.image = self.attack[self.side != "right"]
            self.timer = pg.time.get_ticks()



class MagicBall(pg.sprite.Sprite):
    def __init__(self, coord, side, power, folder):
        super().__init__()

        self.side = side
        self.power = power / 2
        self.image = load_image(f"images/{folder}/magicball.png", 200, 150)
        if self.side == "right":
            self.image = pg.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()

        self.rect.center = coord[0], coord[1] + 120
    
    
    def update(self):
        if self.side == "right":
            self.rect.x += 4

            if self.rect.left >=  SCREEN_WIDTH:
                self.kill()

        else:
            self.rect.x -= 4
            if self.rect.right <= 0:
                self.kill()
        



class Game:

    def __init__(self, mode, wizards):

        self.mode = mode
        
        # Cosdanie okna
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Битва магов")

        self.background = load_image("images/background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        self.foreground = load_image("images/foreground.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        if mode == "one player":
            self.player = Player()
            self.enemy = Enemy(folder=wizards[0])

        elif mode == "two players": 
            self.player = Player(folder=wizards[0])
            self.enemy = Player(folder=wizards[1], first_player = False)
        
        self.clock = pg.time.Clock()
        
        self.is_running = True
        self.win = None



        self.clock = pg.time.Clock()
        self.run()

    def run(self):
        while True:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)
    
    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            
            if event.type == pg.KEYDOWN and self.win is not None:
                quit()
    
    def update(self):
        if self.win is None:
            self.enemy.update(player=self.player)
            self.player.update()

        self.player.magic_balls.update()
        self.enemy.magic_balls.update()

        if self.mode == "one player" or self.enemy.image not in self.enemy.down:
            hits = pg.sprite.spritecollide(self.enemy, self.player.magic_balls, True, pg.sprite.collide_rect_ratio(0.3))
            for hit in hits:
                self.enemy.hp -= hit.power
        
        
        

        #popadanie v igroka
        if self.player.image not in self.player.down:
            hits = pg.sprite.spritecollide(self.player, self.enemy.magic_balls, True, 
                                           pg.sprite.collide_rect_ratio(0.3))

            for hit in hits:
                self.player.hp -= hit.power

        # proverka pobedui igroka
        if self.player.hp < 0:
            self.win = self.enemy
        if self.enemy.hp < 0:
            self.win = self.player

    
    
    def draw(self):
        # Otrisovka inerfaica
        self.screen.blit(self.background, (0, 0))

        # Otrisovka personashey
        self.screen.blit(self.player.image, self.player.rect)

        # Otrisovka enemy
        self.screen.blit(self.enemy.image, self.enemy.rect)

        if self.player.charge_mode:
            self.screen.blit(self.player.charge_indicator,(self.player.rect.left +120, self.player.rect.top))
        if self.mode == "two players":
            if self.enemy.charge_mode:
                self.screen.blit(self.enemy.charge_indicator, (self.enemy.rect.left +120, self.enemy.rect.top))



        # Magicball
        self.player.magic_balls.draw(self.screen)
        self.enemy.magic_balls.draw(self.screen )

        #otrisovka polosok zdorovia
        pg.draw.rect(self.screen, 'green', (10,10, self.player.hp, 20))
        pg.draw.rect(self.screen, 'black', (10,10,100*2,20), 2)
        
        pg.draw.rect(self.screen, 'green', (SCREEN_WIDTH - 210, 10, self.enemy.hp, 20))
        pg.draw.rect(self.screen, 'black' , (SCREEN_WIDTH - 210, 10, 100 *2, 20), 2)

        # peredniy plan
        self.screen.blit(self.foreground, (0, 0))

        #who won message
        if self.win == self.player:
            text = text_render(f"Выйграл маг слева! {self.player.folder}")
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
        
        if self.win == self.enemy:
            text = text_render(f"Выйграл маг справа! {self.enemy.folder}")
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
        

        
        
        pg.display.flip()

#Game menu
class Menu:
    def __init__(self):
        self.surface = pg.display.set_mode((900, 550))
        self.menu = pygame_menu.Menu(
            height = 550,
            width = 900,
            theme = pygame_menu.themes.THEME_BLUE,
            title = "Битва Магов"
        )

        self.menu.add.label(title="Режим на одного")
        self.menu.add.selector('Противник: ', [('Маг молний', 1), ('Монах земли',2), ("Случайный", 3)], onchange=self.select_enemy)
        self.menu.add.button("Играть", self.start_one_player_game)

        self.menu.add.label(title="Режим на двоих")
        self.menu.add.selector("Левый игрок:", [('Маг Молний', 1), ("Монах земли", 2), ("Маг огня", 3)], onchange=self.set_left_player)
        self.menu.add.selector("Правый игрок:", [('Маг Молний', 1), ("Монах земли", 2), ("Маг огня", 3)], onchange=self.set_right_player)
        self.menu.add.button("Играть", self.start_two_player_game)

        self.enemies = ["lightning wizard", "earth monk"]
        self.enemy = self.enemies[0]

        self.players = ["lightning wizard", "earth monk", "fire wizard"]
        self.left_player = self.players[1]
        self.right_player =self.players[0]
        
        
        self.run()

    def set_left_player(self,selected, value):
        self.left_player = self.players[value - 1]
        print("Левый игрок", self.left_player)
    
    def set_right_player(self,selected, value):
        self.right_player = self.players[value - 1]
        print("Правый игрок", self.right_player)

    
    
    
    def select_enemy(self,selected, value):
        if value in (1,2):
            self.enemy = self.enemies[value-1]
        else:
            self.enemy = random.choice(self.enemies)
        
        
    


    def start_one_player_game(self):
        
        Game("one player", [self.enemy])
    
    def start_two_player_game(self):
        Game("two players", [self.left_player, self.right_player])        

    def run(self):
        self.menu.mainloop(self.surface)


# Tochka vkhoda v programmu
if __name__ == "__main__":
    Menu()



        
    


