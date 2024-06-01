"""
Ce jeu qui s'intitule "2hu ~ Highly Unresponsive to Prayers", ce qui se traduit de l'anglais en 
"2hnr ~ Hautement non-responsif aux prières", reprend les principes d'un jeu arcade authentique
où le joueur s'incarne en vaisseau spacial. Il doit se battre à l'aide de ses armements contre 
de nombreux ennemis (aliens et aéronefs ennemis) qui se déplacent rapidement et de manière 
aléatoire, ainsi qu'un boss final qui l'attend en fin de partie. Pour jouer, il suffit d'utiliser
les touches W,A,S,D ou les flèches du clavier pour se déplacer horizontalement et verticalement 
sur le plan de jeu et d'appuyer sur la touche espace pour tirer sur les ennemis. Un score est 
également affiché enhaut de la page. On espère que vous profiterez de notre travail et vous 
souhaitons bonne chance!
"""
from random import randint, choice
import pyxel


type Tile = tuple[int, int]

TRANSPARENCY: int = 5

ENEMIES: list[Tile] = [(x * 16, y * 16 + 8) for x in range(4) for y in range(2, 4)]
BOSSES: list[Tile] = [(x * 16, 24) for x in range(4)]
BOSS_BULLETS: list[Tile] = [(8 + 8*x, 88) for x in range(4)]
POWERUPS: list[Tile] = [(8 + 8*x, 80) for x in range(5)] + [(56, 80)]

DEATH_ANIMATION: list[Tile] = [(x, 104) for x in range(0, 65, 16)] + [(0, 120), (16, 120)]
BOSS_ANIMATION: list[Tile] = [(32, 120), (48, 120)] + [(x, 136) for x in range(0, 65, 16)]

# Movement Functions
def linear_movement(x, y, dx, dy, *args) -> tuple[int, int]:
    return x + dx, y + dy

def sinus_side_movement(x, y, dx, dy, start, *args) -> tuple[int, int]:
    return x + dx, int(pyxel.sin((x + dx) * 2) * 64) + start
    
def sinus_down_movement(x, y, dx, dy, start, *args) -> tuple[int, int]:
    return int(pyxel.sin((y + dy) * 2) * 64) + start, y + dy

def boss_sinus_movement(x, dx) -> tuple[int, int]:
    y = int(pyxel.sin((x + dx)) * 64)
    if y < 32:
        y = - (y - 32) + 32
    return x + dx, y

MOVEMENTS: list = [linear_movement, sinus_side_movement, sinus_down_movement]

class Bullets:
    def __init__(self):
        self.bullets: dict[Tile, Tile] = {}

    def add_bullet(self, x, y, bx, by):
        self.bullets[(x + 4, y)] = (bx, by)

    def collision(self, x, y, deltax, deltay):
        for dx in range(deltax):
            for dy in range(deltay):
                positions = {(x + dx + i * 8, y + dy + j * 8) 
                            for i in range(2) for j in range(2)}
                for position in positions:
                    if position in self.bullets:
                        del self.bullets[position]
                        return True

    def update(self):
        new_dict: dict[Tile, Tile] = {}
        for key, value in self.bullets.items():
            if key[1] - 5 > 32:
                new_dict[(key[0], key[1] - 5)] = value
        self.bullets = new_dict
    
    def draw(self):
        for key, value in self.bullets.items():
            x, y = key
            sprite_x, sprite_y = value
            pyxel.blt(x, y, 0, sprite_x, sprite_y, 8, 8, TRANSPARENCY)

class Player:
    def __init__(self):
        self.x: int = 120
        self.y: int = 240
        self.lives: int = 3
        self.iframes: int = 0
        self.death_frame: int = 0

    def update(self, bullets):
        if self.lives < 1:
            self.death_frame += 1
            return

        self.iframes = max(0, self.iframes - 1)

        movement = 2 if pyxel.btn(pyxel.KEY_SHIFT) else 4

        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.x = max(self.x - movement, 0)
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.x = min(self.x + movement, 240)
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
            self.y = max(self.y - movement, 32)
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S):
            self.y = min(self.y + movement, 240)
        if (pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_Z)) and pyxel.frame_count % 3 == 0:
            bullets.add_bullet(self.x, self.y, 40, 72)

    def draw(self):
        for n_life in range(self.lives):
            pyxel.blt(n_life*8, 0, 0, 0, 136, 16, 16, TRANSPARENCY)
        if self.lives < 1:
            sprite_x, sprite_y = DEATH_ANIMATION[min(self.death_frame//4, 6)]
            pyxel.blt(self.x, self.y, 0, sprite_x, sprite_y, 16, 16, TRANSPARENCY)
            return
        if not (self.iframes and (pyxel.frame_count % 4 == 0 or pyxel.frame_count % 4 == 1)):
            pyxel.blt(self.x, self.y, 0, 0, 8, 16, 16, TRANSPARENCY)

class Enemy:
    def __init__(self):
        self.tx, self.ty = choice(ENEMIES)
        self.lives: int = 5
        self.movement = choice(MOVEMENTS)
        if self.movement == linear_movement:
            if randint(0, 1):
                self.x, self.y = randint(0, 240), 56
            else:
                self.x, self.y = 0, randint(56, 112)
        
            self.dx, self.dy = randint(1, 2), randint(1, 2)
            self.start = 0
        elif self.movement == sinus_side_movement:
            self.start = randint(92, 184)
            self.x, self.y = self.start, 0
            self.dx, self.dy = randint(1, 2), randint(1, 2)
        else:
            self.start = randint(56, 184)
            self.x, self.y = 0, self.start
            self.dx, self.dy = randint(1, 2), randint(1, 2)
        
    
    def update(self, player, bullets) -> int:
        if self.x > 240 or self.x < 0:
            self.dx = -self.dx
        
        if self.y > 240 or self.y < 32:
            self.dy = -self.dy
        
        self.x, self.y = self.movement(self.x, self.y, self.dx, self.dy, self.start)

        if (
            self.x + 5 < player.x + 10
            and self.x + 10 > player.x + 5
            and self.y + 5 < player.y + 10
            and self.y + 10 > player.y + 5
            and not player.iframes
        ):
            player.lives -= 1
            player.iframes = 90

        if bullets.collision(self.x + 5, self.y + 5, 6, 6):
            self.lives -= 1
        
    
    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.tx, self.ty, 16, 16, TRANSPARENCY)


class BossBullet:
    def __init__(self, tx, ty, x, y, dx, dy):
        self.tx, self.ty = tx, ty
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.alive: bool = True

    def update(self, player):
        self.x += self.dx
        self.y += self.dy
        if (
            self.x < player.x + 10
            and self.x + 8 > player.x + 5
            and self.y < player.y + 10
            and self.y + 8 > player.y + 5
            and not player.iframes
        ):
            player.lives -= 1
            player.iframes = 90
        
        if self.x > 256 or self.x < -7 or self.y > 256 or self.y < 24:
            self.alive = False
        
    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.tx, self.ty, 8, 8, TRANSPARENCY)


class Boss:
    def __init__(self):
        num = randint(0, 3)
        self.animation = 0
        self.sprite_x, self.sprite_y = BOSSES[num]
        self.bullet_x, self.bullet_y = BOSS_BULLETS[num]
        self.x, self.y = 120, 64
        self.lives: int = 50
        self.live: bool = True
        self.hit: bool = False
        self.bullets: set[BossBullet] = set()
        self.dx: int = 2
        

    def update(self, player, bullets):
        if self.animation < len(BOSS_ANIMATION):
            return

        if self.x > 240 or self.x < 0:
            self.dx = -self.dx

        if (
            self.x + 5 < player.x + 10
            and self.x + 10 > player.x + 5
            and self.y + 5 < player.y + 10
            and self.y + 10 > player.y + 5
            and not player.iframes
        ):
            player.lives -= 1
            player.iframes = 90
        
        if bullets.collision(self.x, self.y, 16, 16):
            self.lives -= 1
            self.hit = True

        self.x, self.y = boss_sinus_movement(self.x, self.dx)
        
        new_bullets = set()
        for bullet in self.bullets:
            bullet.update(player)
            if bullet.alive:
                new_bullets.add(bullet)
        self.bullets = new_bullets

        if self.lives < 0:
            if self.bullets == set():
                self.live = False
            return

        if pyxel.frame_count % 20 == 0:
            for dx in range(-1, 2):
                for dy  in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    self.bullets.add(BossBullet(
                        self.bullet_x, self.bullet_y,
                        self.x + 4, self.y + 4,
                        dx, dy
                        ))

    def draw(self):
        if self.animation < len(BOSS_ANIMATION):
            sprite_x, sprite_y = BOSS_ANIMATION[self.animation]
            pyxel.blt(120, 64, 0, sprite_x, sprite_y, 16, 16, TRANSPARENCY)
            if pyxel.frame_count % 6 == 0:
                self.animation += 1
            return
        
        for bullet in self.bullets:
            bullet.draw()
        
        if self.lives < 0:
            return

        if self.hit == True:
            self.hit = False
            return
            
        pyxel.blt(self.x, self.y, 0, self.sprite_x, self.sprite_y, 16, -16, TRANSPARENCY)
    

class Enemies:
    def __init__(self):
        self.enemies: set[Enemy] = {Enemy() for _ in range(4)}

    def add_enemy(self):
        self.enemies.add(Enemy())

    def update(self, player, bullets, boss):
        score = 0
        new_enemies: set[Enemy] = set()
        for enemy in self.enemies:
            enemy.update(player, bullets)
            if enemy.lives > 0:
                new_enemies.add(enemy)
            else:
                score += 200
        
        self.enemies = new_enemies
        
        if pyxel.frame_count % 90 == 0:
            self.add_enemy()
        
        return score

    def draw(self):
        for enemy in self.enemies:
            enemy.draw()
        

class App:
    def __init__(self):
        pyxel.init(256, 256, "2hu ~ Highly Unresponsive to Prayers")
        pyxel.load("1.pyxres")

        self.player = Player()
        self.enemies = Enemies()
        self.bullets = Bullets()
        self.boss = None
        self.score: int = 0

        pyxel.run(self.update, self.draw)
    
    def update(self):
        if self.player.death_frame == 40:
            return
        self.bullets.update()
        self.player.update(self.bullets)
        self.score += self.enemies.update(self.player, self.bullets, self.boss)
        if self.score != 0 and self.score % 3000 == 0 and self.boss is None:
            self.boss = Boss()
        if self.boss is not None:
            self.boss.update(self.player, self.bullets)
            if self.boss.live == False:
                self.score += 10_000
                self.boss = None
    
    def draw(self):
        pyxel.bltm(0, 0, 0, 0, 0, 256, 256)
        if self.player.death_frame == 40:
            pyxel.text(120, 120, "Game Over", 0)
            pyxel.text(120, 128, f"Score: {self.score}", 0)
            return
        self.bullets.draw()
        self.enemies.draw()
        self.player.draw()
        if self.boss is not None:
            self.boss.draw()
        pyxel.text(16, 16, str(self.score), 0)


if __name__ == "__main__":
    App()