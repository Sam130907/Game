import os
import sys
import random
import math

import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicalEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.menu import show_title_screen, show_pause_menu

class Game:
    def __init__(self): 
        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((960, 720))
        self.display = pygame.Surface((400, 310), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((400, 310))
        self.display_3 = pygame.Surface((400, 310))

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]

        self.assets = {
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'stone' : load_images('tiles/stone'),
            'sand' : load_images('tiles/sand'),
            'sand_decor' : load_images('tiles/sand_decor'),
            'ice' : load_images('tiles/ice'),
            'ice_decor' : load_images('tiles/ice_decor'),
            'grass_decor' : load_images('tiles/grass_decor'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'dungeon' : load_images('tiles/dungeon'),
            'dungeon_decor' : load_images('tiles/dungeon_decor'),
            'enemy/idle' : Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run' : Animation(load_images('entities/enemy/run'), img_dur=6),
            'player/idle' : Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run' : Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump' : Animation(load_images('entities/player/jump')),
            'player/slide' : Animation(load_images('entities/player/slide')),
            'player/wall_slide' : Animation(load_images('entities/player/wall_slide')),
            'particle/leaf' : Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle' : Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun' : load_image('gun.png'),
            'projectile' : load_image('projectile.png'),
            'tutorial_text' : load_images('tiles/tutorial_text'),
            'finish_decor' : load_images('tiles/finish_decor'),
        }

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)
        
        self.level = 0

        self.screenshake = 0 

        self.load_level(6)
        self.transition = 0

        show_title_screen(self)

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('grass_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:

                bx, by = spawner['pos']
                n = getattr(self, 'enemies_per_spawner', 5)
                cols = min(10, max(1, int(math.sqrt(n))))  
                spacing_x = 14
                spacing_y = 18
                start_x = bx - (cols - 1) * spacing_x / 2
                start_y = by    
                for i in range(n):
                    r = i // cols
                    c = i % cols
                    x = start_x + c * spacing_x + random.uniform(-2, 2)
                    y = start_y + r * spacing_y + random.uniform(-2, 2)
                    self.enemies.append(Enemy(self, (x, y), (8, 15)))
        
        self.projectiles = []
        self.particles = []
        self.sparks = []

        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30

    def run(self):
        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets['background'], (0, 0))

            self.screenshake = max(0, self.screenshake - 1)

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) -1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition +=1

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.load_level(self.level)

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 20
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 20
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            self.clouds.update()
            self.clouds.render(self.display_2, offset=render_scroll)

            self.tilemap.render(self.display, offset=render_scroll)

            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] +=1
                img = self.assets['projectile']
                if projectile[1] > 0:  
                    img = pygame.transform.flip(img, True, False)
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.screenshake = max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame= random.randint(0, 7)))

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (1, 0), (0, -1), (0 ,1)]:
                self.display_2.blit(display_sillhouette, offset)

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.jump()
                    if event.key == pygame.K_x:
                        self.player.dash()
                    if event.key == pygame.K_e:
                        self.player.attack()
                    if event.key == pygame.K_p:
                        show_pause_menu(self)
                    if event.key == pygame.K_g and self.level == 6:  # Check if final level
                        # Show end game message
                        title_font = pygame.font.SysFont(None, 64)
                        credit_font = pygame.font.SysFont(None, 36)
                        
                        # Create text surfaces
                        thank_you = title_font.render("Thank you for playing", True, (255, 255, 255))
                        credits = credit_font.render("Game made by Sam", True, (255, 255, 255))
                        
                        # Animation for text dropping from top (not as far down)
                        start_y = -100
                        end_y = 80  # Reduced from screen.get_height() // 3
                        credit_y = self.screen.get_height() - 80  # Fixed bottom position
                        
                        for i in range(60):  # 1 second animation
                            # Calculate current text position
                            current_y = start_y + (end_y - start_y) * (i / 60)
                            
                            # Let the game update normally
                            if not self.dead:
                                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                            for enemy in self.enemies.copy():
                                kill = enemy.update(self.tilemap, (0, 0))
                                if kill:
                                    self.enemies.remove(enemy)
                            
                            # Normal game rendering
                            self.display.fill((0, 0, 0, 0))
                            self.display_2.blit(self.assets['background'], (0, 0))
                            self.clouds.update()
                            self.clouds.render(self.display_2, offset=render_scroll)
                            self.tilemap.render(self.display, offset=render_scroll)
                            
                            for enemy in self.enemies.copy():
                                enemy.render(self.display, offset=render_scroll)
                            self.player.render(self.display, offset=render_scroll)
                            
                            for particle in self.particles:
                                particle.render(self.display, offset=render_scroll)
                            for spark in self.sparks:
                                spark.render(self.display, offset=render_scroll)
                            
                            self.display_2.blit(self.display, (0, 0))
                            scaled = pygame.transform.scale(self.display_2, self.screen.get_size())
                            self.screen.blit(scaled, (0, 0))
                            
                            # Draw text with drop shadow
                            shadow_offset = 2
                            thank_x = (self.screen.get_width() - thank_you.get_width()) // 2
                            credit_x = (self.screen.get_width() - credits.get_width()) // 2
                            
                            # Draw shadows
                            self.screen.blit(thank_you, (thank_x + shadow_offset, current_y + shadow_offset))
                            self.screen.blit(credits, (credit_x + shadow_offset, credit_y + shadow_offset))
                            
                            # Draw text
                            self.screen.blit(thank_you, (thank_x, current_y))
                            self.screen.blit(credits, (credit_x, credit_y))
                            
                            pygame.display.flip()
                            self.clock.tick(60)
                        
                        # Keep showing text for 3 seconds while game continues
                        start_time = pygame.time.get_ticks()
                        while pygame.time.get_ticks() - start_time < 3000:
                            # Let the game update normally
                            if not self.dead:
                                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                            for enemy in self.enemies.copy():
                                kill = enemy.update(self.tilemap, (0, 0))
                                if kill:
                                    self.enemies.remove(enemy)
                            
                            # Normal game rendering
                            self.display.fill((0, 0, 0, 0))
                            self.display_2.blit(self.assets['background'], (0, 0))
                            self.clouds.update()
                            self.clouds.render(self.display_2, offset=render_scroll)
                            self.tilemap.render(self.display, offset=render_scroll)
                            
                            for enemy in self.enemies.copy():
                                enemy.render(self.display, offset=render_scroll)
                            self.player.render(self.display, offset=render_scroll)
                            
                            for particle in self.particles:
                                particle.render(self.display, offset=render_scroll)
                            for spark in self.sparks:
                                spark.render(self.display, offset=render_scroll)
                            
                            self.display_2.blit(self.display, (0, 0))
                            scaled = pygame.transform.scale(self.display_2, self.screen.get_size())
                            self.screen.blit(scaled, (0, 0))
                            
                            # Keep showing text at final positions
                            self.screen.blit(thank_you, (thank_x + shadow_offset, end_y + shadow_offset))
                            self.screen.blit(credits, (credit_x + shadow_offset, credit_y + shadow_offset))
                            self.screen.blit(thank_you, (thank_x, end_y))
                            self.screen.blit(credits, (credit_x, credit_y))
                            
                            pygame.display.flip()
                            self.clock.tick(60)

                        # sync movement to actual keyboard state after unpausing
                        keys = pygame.key.get_pressed()
                        self.movement[0] = bool(keys[pygame.K_LEFT])
                        self.movement[1] = bool(keys[pygame.K_RIGHT])
                        if not self.movement[0] and not self.movement[1]:
                            if hasattr(self.player, 'vel'):
                                try:
                                    if isinstance(self.player.vel, list):
                                        self.player.vel[0] = 0
                                    elif isinstance(self.player.vel, tuple):
                                        self.player.vel = (0,) + tuple(self.player.vel[1:])
                                except Exception:
                                    pass
                            if hasattr(self.player, 'vx'):
                                try:
                                    self.player.vx = 0
                                except Exception:
                                    pass


                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False

                        if not self.movement[1]:
                            if hasattr(self.player, 'vel'):
                                try:
                                    if isinstance(self.player.vel, list):
                                        self.player.vel[0] = 0
                                    elif isinstance(self.player.vel, tuple):
                                        self.player.vel = (0,) + tuple(self.player.vel[1:])
                                except Exception:
                                    pass
                            if hasattr(self.player, 'vx'):
                                try:
                                    self.player.vx = 0
                                except Exception:
                                    pass
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                        if not self.movement[0]:
                            if hasattr(self.player, 'vel'):
                                try:
                                    if isinstance(self.player.vel, list):
                                        self.player.vel[0] = 0
                                    elif isinstance(self.player.vel, tuple):
                                        self.player.vel = (0,) + tuple(self.player.vel[1:])
                                except Exception:
                                    pass
                            if hasattr(self.player, 'vx'):
                                try:
                                    self.player.vx = 0
                                except Exception:
                                    pass

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            self.display_2.blit(self.display, (0, 0))

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)

Game().run()