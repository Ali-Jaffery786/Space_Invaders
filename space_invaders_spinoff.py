import pygame
import time
import random
from os.path import join
pygame.font.init()

pygame.display.set_caption('Space Invaders')
FONT = pygame.font.SysFont('Pixel Emulator', 25)
END_SCREEN = pygame.font.SysFont('Pixel Emulator', 75)
WIDTH, HEIGHT = 1000, 700
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

class Player(pygame.sprite.Sprite):

    def __init__(self, groups, starSprite):
        super().__init__(groups)
        self.image = pygame.image.load(join('img', 'player.png')).convert_alpha()
        self.rect = self.image.get_rect(center = (WIDTH/2, HEIGHT-self.image.get_height()/2))
        self.direction = pygame.Vector2()
        self.speed = 300
        self.group = groups
        self.lives = 3
        self.starSprite = starSprite

        # star cooldown logic.
        self.can_shoot = True
        self.star_shoot_time = 0
        self.cooldown_duration = 300
        self.last_frame_keys = []
    
    def update(self, dt):

        keys = pygame.key.get_pressed()
        # Movement
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        if self.rect.right <= WIDTH and self.rect.left >= 0:
            self.rect.center += self.direction * self.speed * dt
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
        elif self.rect.left < 0:
            self.rect.left = 0
        # Firing
        if keys[pygame.K_w] and self.can_shoot and not self.last_frame_keys[pygame.K_w]:
            #fire a star !!!
            Star(self.rect.midtop, (self.group, self.starSprite))
            self.can_shoot = False
            self.star_shoot_time = pygame.time.get_ticks()
        self.last_frame_keys = keys
        self.star_timer()
        
    def star_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.star_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

class Star(pygame.sprite.Sprite):

    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('img', 'star.png')).convert()
        self.rect = self.image.get_rect(midbottom = pos)
        self.direction = pygame.math.Vector2(0, -1)
        self.speed = 500

    def update(self, dt):
        self.rect.center += self.speed * dt * self.direction
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    
    def __init__(self, groups, x ,y):
        super().__init__(groups)
        self.image = pygame.image.load(join('img', 'enemy.png')).convert_alpha()
        self.rect = self.image.get_rect(center = (x, y))

    def update(self, dt):
        pass

class Laser(pygame.sprite.Sprite):

    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('img', 'laser.png')).convert()
        self.rect = self.image.get_rect(midtop = (pos))
        self.direction = pygame.math.Vector2(0, 1)
        self.speed = 500

    def update(self, dt):
        self.rect.center += self.speed * dt * self.direction
        if self.rect.top > HEIGHT:
            self.kill()

def draw(all_sprites, lives):
    WINDOW.fill('Black')
    lives_text = FONT.render(f"Lives: {lives}", 0, 'white')
    WINDOW.blit(lives_text, (10, 10))
    all_sprites.draw(WINDOW)
    pygame.display.update()
    

def main():
    # Group Definitions
    all_sprites = pygame.sprite.Group()
    enemy_sprites = pygame.sprite.Group()
    star_sprites = pygame.sprite.Group()
    laser_sprites = pygame.sprite.Group()
    # Sprite instantiations
    player = Player(all_sprites, star_sprites)
    enemy_xpos = [(WIDTH/10*x)-(WIDTH/10)/2 for x in range(1, 11)]
    enemy_ypos = [75, 150, 225, 300, 375]
    enemies = [Enemy((all_sprites, enemy_sprites), enemy_xpos[i], enemy_ypos[j]) for j in range(5)
               for i in range(10)]
    
    laser_event = pygame.event.custom_type()
    pygame.time.set_timer(laser_event, 1000)
    lasers = []
    clock = pygame.time.Clock()

    run = True
    # Game loop
    while run:
        dt = clock.tick(144) / 1000
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                run = False
                break

            # Randomize laser firing
            if event.type == laser_event:
                if len(enemies) < 8:
                    laser_count = random.randint(1, len(enemies))
                else:
                    laser_count = random.randint(1, 8)
                for _ in range(laser_count):
                    chosen_enemy = random.randint(0, len(enemies)-1)
                    chosen_enemy_pos = enemies[chosen_enemy].rect.midbottom
                    lasers.append(Laser(chosen_enemy_pos, (all_sprites, laser_sprites)))
                freq = random.randint(100, 4000)
                pygame.time.set_timer(laser_event, freq)

        #Kill enemies when hit
        star_enemy_collisions = pygame.sprite.groupcollide(star_sprites, enemy_sprites, True,
                                                           True)
        # Remove enemies from the enemy list for laser logic
        for stars, hit_enemies in star_enemy_collisions.items():
            for enemy in hit_enemies:
                enemies.remove(enemy)

        #Decrease lives when hit
        laser_player_collision = pygame.sprite.spritecollideany(player, laser_sprites)
        if laser_player_collision:
            laser_player_collision.kill()
            if player.lives == 0:
                run = False
                game_over = END_SCREEN.render("GAME OVER", 0, 'red')
                WINDOW.blit(game_over, (WIDTH/2 - game_over.get_width()/2,
                                        HEIGHT/2 - game_over.get_height()/2))
                pygame.display.update()
                pygame.time.delay(3000)
            player.lives -= 1

        # Winner screen
        if not enemy_sprites.sprites():
            winner = END_SCREEN.render("YOU WIN!", 0, 'white')
            WINDOW.blit(winner, (WIDTH/2 - winner.get_width()/2, HEIGHT/2 - winner.get_height()/2))
            pygame.display.update()
            pygame.time.delay(5000)

        all_sprites.update(dt)
        draw(all_sprites, player.lives)

# OLD CODE
# PLAYER_WIDTH = 40
# PLAYER_HEIGHT = 60
# PLAYER_SURF = pygame.image.load(join('img', 'player.png')).convert_alpha()
# PLAYER_RECT = PLAYER_SURF.get_rect(center = (0, 0))
# PLAYER_VEL = 500

# ENEMY_WIDTH = 80
# ENEMY_HEIGHT = 50

# PROJ_WIDTH = 10
# PROJ_HEIGHT = 20
# PROJ_VEL = 10
# FIRE_COOLDOWN = 500

# def draw(player, enemies, elapsed_time, player_projs, enemy_projs, lives):
#     time_text = FONT.render(f'Time: {round(elapsed_time)}s', 0, 'white')
#     lives_text = FONT.render(f'Lives: {lives}', 0, 'white')
#     WINDOW.fill('Black')
#     WINDOW.blit(time_text, (10, 10))
#     WINDOW.blit(lives_text, (10, HEIGHT - 30))
#     for player_proj in player_projs:
#         pygame.draw.rect(WINDOW, 'blue', player_proj)
#     for enemy_proj in enemy_projs:
#         pygame.draw.rect(WINDOW, 'white', enemy_proj)
#     for enemy in enemies:
#         pygame.draw.rect(WINDOW, 'red', enemy)
#     pygame.draw.rect(WINDOW, 'green', player)
#     pygame.display.update()
    
    
    
# def main():
#     run: bool = True
#     player = Player()
#     player = pygame.Rect(500, HEIGHT-PLAYER_HEIGHT-25,
#                          PLAYER_WIDTH, PLAYER_HEIGHT)
#     player_direction = pygame.math.Vector2()
#     player_projs = []
#     last_fired_time = 0
#     lives = 3
#     hit = False
    
#     enemies = []
#     enemy_y = 50
#     for x in range(4):
#         enemy_x = 40
#         for y in range(8):
#             enemy = pygame.Rect(enemy_x, enemy_y, ENEMY_WIDTH, ENEMY_HEIGHT)
#             enemies.append(enemy)
#             enemy_x += ENEMY_WIDTH + 40
#         enemy_y += ENEMY_HEIGHT + 40

#     enemy_projs = []
#     enemy_proj_increment = 2
#     enemy_proj_counter = 0

    
#     clock = pygame.time.Clock()
#     start_time = time.time()
#     elapsed_time = 0

#     while run:
#         dt = clock.tick() / 1000
#         enemy_proj_counter += dt
#         elapsed_time = time.time() - start_time

#         if enemy_proj_counter > enemy_proj_increment and len(enemies) >= 0:
#             for _ in range(4):
#                 whichEnemy = random.randint(0, len(enemies)-1)
#                 chosen_enemy = enemies[whichEnemy]
#                 enemy_proj = pygame.Rect(chosen_enemy.x + chosen_enemy.width/2 - PROJ_WIDTH/2,
#                                          chosen_enemy.y, PROJ_WIDTH, PROJ_HEIGHT)
#                 enemy_projs.append(enemy_proj)
#             enemy_proj_counter = 0

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False
#                 break

#             if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
#                 proj_x = player.x + player.width/2 - PROJ_WIDTH/2
#                 player_proj = pygame.Rect(proj_x, player.y, PROJ_WIDTH, PROJ_HEIGHT)
#                 player_projs.append(player_proj)
        
#         keys = pygame.key.get_pressed()
#         player_direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        
#         player.center += player_direction * PLAYER_VEL * dt

#         for player_proj in player_projs[:]:
#             player_proj.y -= PROJ_VEL
#             if player_proj.y + player_proj.height <= 0:
#                 player_projs.remove(player_proj)

#         for enemy_proj in enemy_projs[:]:
#             enemy_proj.y += PROJ_VEL
#             if enemy_proj.y >= HEIGHT:
#                 enemy_projs.remove(enemy_proj)
#             elif enemy_proj.y + enemy_proj.height >= player.height and enemy_proj.colliderect(player):
#                 enemy_projs.remove(enemy_proj)
#                 hit = True

#         if hit:
#             lives -= 1
#             if lives == 0:
#                 draw(player, enemies, elapsed_time, player_projs, enemy_projs, lives)
#                 lost_text = FONT.render('YOU LOST', 0, 'white')
#                 WINDOW.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2,
#                                     HEIGHT/2 - lost_text.get_height()/2))
#                 pygame.display.update()
#                 pygame.time.delay(4000)
#                 break
#             hit = False
#         draw(player, enemies, elapsed_time, player_projs, enemy_projs, lives)

#     pygame.quit()

if __name__ == '__main__':
    main()