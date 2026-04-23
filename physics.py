"""
Physics engine and game entities.
Projectiles, targets, particles, AI.
"""
import pygame
import math
import random
from constants import *
from art import (draw_missile, draw_bomb_proj, draw_rocket_proj, draw_torpedo_proj,
                 draw_explosion, draw_smoke_trail)


class Particle:
    def __init__(self, x, y, vx, vy, color, radius=4, life=40):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.radius = radius
        self.life = life
        self.max_life = life

    def update(self):
        self.vy += GRAVITY * 0.5
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.life -= 1

    def draw(self, surf):
        t = self.life / self.max_life
        r = max(1, int(self.radius * t))
        alpha = int(255 * t)
        s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
        c = (*self.color[:3], alpha)
        pygame.draw.circle(s, c, (r+1,r+1), r)
        surf.blit(s, (int(self.x)-r-1, int(self.y)-r-1))


class Explosion:
    def __init__(self, x, y, radius):
        self.x, self.y = x, y
        self.radius = radius
        self.frame = 0
        self.max_frames = 35
        self.done = False

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.done = True

    def draw(self, surf):
        draw_explosion(surf, self.x, self.y, self.frame, self.max_frames)


class Projectile:
    def __init__(self, x, y, vx, vy, weapon_type, team, blast_r):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.weapon = weapon_type
        self.team = team
        self.blast_r = blast_r
        self.damage = WEAPON_DATA[weapon_type]["damage"]
        self.active = True
        self.trail = []
        self.trail_max = 18
        self.lifetime = 0
        self.max_lifetime = 400
        # Drone/guided properties
        self.is_guided = (weapon_type == W_DRONE)
        self.target = None

    def set_target(self, tx, ty):
        self.target = (tx, ty)

    def update(self, ground_rects, W, H):
        if not self.active:
            return

        # Drone homing logic
        if self.is_guided and self.target:
            tx, ty = self.target
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)
            if dist > 5:
                desired_vx = dx/dist * 5
                desired_vy = dy/dist * 5
                self.vx += (desired_vx - self.vx) * 0.04
                self.vy += (desired_vy - self.vy) * 0.04
        else:
            self.vy += GRAVITY

        # Record trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > self.trail_max:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy
        self.lifetime += 1

        # Out of bounds
        if self.x < -50 or self.x > W+50 or self.y > H+50 or self.lifetime > self.max_lifetime:
            self.active = False
            return

        # Ground collision
        for rect in ground_rects:
            rx, ry, rw, rh = rect
            if rx <= self.x <= rx+rw and ry <= self.y <= ry+rh:
                self.active = False
                return

    def angle_deg(self):
        return math.degrees(math.atan2(-self.vy, self.vx))

    def draw(self, surf):
        if not self.active:
            return
        draw_smoke_trail(surf, self.trail)
        x, y = int(self.x), int(self.y)
        if self.weapon in (W_MISSILE, W_ROCKET):
            draw_missile(surf, x, y, self.angle_deg(), self.team)
        elif self.weapon == W_BOMB:
            draw_bomb_proj(surf, x, y)
        elif self.weapon == W_TORPEDO:
            draw_torpedo_proj(surf, x, y)
        elif self.weapon == W_DRONE:
            from art import draw_drone
            draw_drone(surf, x, y, self.team)
        elif self.weapon == W_TANK:
            draw_rocket_proj(surf, x, y, self.angle_deg(), self.team)


class Target:
    """A target box/structure on the enemy side."""
    def __init__(self, x, y, w, h, hp, team, kind="block"):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.hp = hp
        self.max_hp = hp
        self.team = team
        self.kind = kind
        self.alive = True
        self.wobble = 0
        self.debris = []

    def check_hit(self, proj_x, proj_y, blast_r):
        cx = self.x + self.w//2
        cy = self.y + self.h//2
        dist = math.hypot(proj_x-cx, proj_y-cy)
        return dist < blast_r + max(self.w, self.h)//2

    def take_damage(self, dmg, proj_x, proj_y):
        self.hp -= dmg
        self.wobble = 12
        # Create debris
        cx = self.x + self.w//2
        cy = self.y + self.h//2
        for _ in range(8):
            vx = random.uniform(-4, 4)
            vy = random.uniform(-6, -1)
            c = random.choice([(180,100,60),(150,80,40),(200,200,200),(80,80,80)])
            self.debris.append(Particle(cx, cy, vx, vy, c, random.randint(3,8), 50))
        if self.hp <= 0:
            self.alive = False
            self.hp = 0

    def update(self):
        if self.wobble > 0:
            self.wobble -= 1
        for p in self.debris[:]:
            p.update()
            if p.life <= 0:
                self.debris.remove(p)

    def draw(self, surf, font_sm):
        if not self.alive:
            for p in self.debris:
                p.draw(surf)
            return

        dx = math.sin(self.wobble * 0.8) * min(self.wobble, 6) if self.wobble else 0
        rx = int(self.x + dx)

        col = TEAM_COLORS[self.team]
        dark = tuple(max(0,c-50) for c in col)

        if self.kind == "block":
            pygame.draw.rect(surf, col, (rx, self.y, self.w, self.h))
            pygame.draw.rect(surf, dark, (rx, self.y, self.w, self.h), 3)
            # Battle damage texture
            if self.hp < self.max_hp * 0.7:
                for i in range(3):
                    lx = rx + random.randint(5, self.w-5)
                    pygame.draw.line(surf, (40,30,20),(lx,self.y+5),(lx-8,self.y+self.h-5),2)

        elif self.kind == "bunker":
            pts = [(rx,self.y+self.h),(rx+self.w,self.y+self.h),
                   (rx+self.w-10,self.y+10),(rx+10,self.y+10)]
            pygame.draw.polygon(surf, col, pts)
            pygame.draw.polygon(surf, dark, pts, 3)
            pygame.draw.rect(surf, dark, (rx+self.w//2-8, self.y+5, 16, 20))

        elif self.kind == "tower":
            pygame.draw.rect(surf, col, (rx+self.w//4, self.y, self.w//2, self.h))
            pygame.draw.rect(surf, dark, (rx, self.y, self.w, self.h//4))
            for bx in [rx+5, rx+self.w-12]:
                pygame.draw.rect(surf, dark, (bx, self.y-10, 7, 15))

        # Flag on top
        if self.kind in ("tower","bunker"):
            from art import draw_flag
            draw_flag(surf, rx+self.w//2-10, self.y-30, self.team, 20, 13)

        # HP bar
        from art import draw_health_bar
        draw_health_bar(surf, rx, self.y-16, self.hp, self.max_hp, self.w, 7)

        for p in self.debris:
            p.draw(surf)


class AI:
    """Simple AI for the enemy turn."""
    def __init__(self, team, difficulty=1):
        self.team = team
        self.difficulty = difficulty
        self.think_timer = 90  # frames to "think"
        self.thinking = True

    def reset(self):
        self.think_timer = 80 + random.randint(0, 40)
        self.thinking = True

    def compute_shot(self, sx, sy, targets):
        """Compute angle and power to hit a target."""
        if not targets:
            return 45, 15

        # Pick a target
        tgt = random.choice(targets)
        tx = tgt.x + tgt.w // 2
        ty = tgt.y + tgt.h // 2

        # Rough ballistic solution
        dx = tx - sx
        dy = sy - ty
        g = GRAVITY

        # Try several powers and find best angle
        best = (45, 15)
        best_dist = float('inf')

        for power in range(8, MAX_POWER+1, 2):
            vx0 = power * math.cos(math.radians(45))
            vy0 = power * math.sin(math.radians(45))
            # Time to reach tx: tx = sx + vx0*t → t = dx/vx0
            if abs(vx0) < 0.1:
                continue
            t_hit = dx / vx0
            if t_hit < 0:
                continue
            pred_y = sy - vy0*t_hit + 0.5*g*t_hit**2
            dist = abs(pred_y - ty)
            # Add noise based on difficulty
            noise = random.uniform(-30, 30) * (2 - self.difficulty)
            if dist + noise < best_dist:
                best_dist = dist + noise
                # Solve for angle more precisely
                for angle_deg in range(10, 80, 5):
                    angle = math.radians(angle_deg)
                    vx = power * math.cos(angle)
                    vy = power * math.sin(angle)
                    if abs(vx) < 0.1:
                        continue
                    t = dx / vx
                    if t < 0:
                        continue
                    py = sy - vy*t + 0.5*g*t**2
                    d = abs(py - ty)
                    if d < best_dist:
                        best_dist = d
                        best = (angle_deg, power)

        # Add accuracy noise
        angle, power = best
        angle += random.uniform(-12, 12) * (2 - self.difficulty * 0.5)
        power += random.uniform(-3, 3)
        power = max(5, min(MAX_POWER, power))
        return angle, power

    def update(self):
        if self.thinking and self.think_timer > 0:
            self.think_timer -= 1
        if self.think_timer <= 0:
            self.thinking = False
