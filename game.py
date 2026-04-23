"""
Main Game class — handles all screens and the core game loop.
"""
import pygame
import math
import random
import sys
from constants import *
from art import *
from physics import Projectile, Target, Explosion, Particle, AI
import sounds_engine as sfx


class Screen:
    MENU    = "menu"
    PLAYING = "playing"
    WIN     = "win"
    LOSE    = "lose"
    LEVEL_SELECT = "level_select"
    HOW_TO  = "how_to"


class WarGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock  = clock
        self.W, self.H = screen.get_size()

        # Fonts
        try:
            self.font_big  = pygame.font.SysFont("Impact", 72)
            self.font_med  = pygame.font.SysFont("Impact", 36)
            self.font_sm   = pygame.font.SysFont("Arial", 22)
            self.font_xs   = pygame.font.SysFont("Arial", 16)
        except Exception:
            self.font_big  = pygame.font.Font(None, 80)
            self.font_med  = pygame.font.Font(None, 42)
            self.font_sm   = pygame.font.Font(None, 28)
            self.font_xs   = pygame.font.Font(None, 20)

        self.audio_ok = sfx.init_sounds()
        self.state    = Screen.MENU
        self.current_level_idx = 0
        self.score_a  = 0
        self.score_b  = 0

        # Pre-render static BGs
        self._cached_bgs = {}
        for lvl in LEVELS:
            bg = pygame.Surface((self.W, self.H))
            draw_background(bg, lvl["bg"])
            self._cached_bgs[lvl["bg"]] = bg

        self._init_level(0)
        self._menu_timer = 0

    # ─── LEVEL SETUP ──────────────────────────────────────────
    def _init_level(self, idx):
        self.current_level_idx = idx
        lvl = LEVELS[idx]
        self.bg_type  = lvl["bg"]
        self.team_a   = lvl["team_a"]
        self.team_b   = lvl["team_b"]
        self.level_name = lvl["name"]
        self.level_desc = lvl["desc"]

        self.W, self.H = self.screen.get_size()
        GH = self.H  # ground height reference

        # Ground platforms (x,y,w,h)
        self.ground = [
            (0,           GH-60,  self.W,       60),   # main floor
            (100,         GH-160, 200,           100),  # left platform
            (self.W-300,  GH-160, 200,           100),  # right platform
            (self.W//2-80,GH-220, 160,           60),   # center mid
        ]

        # Slingshot position (player launches from here)
        self.sling_x = 180
        self.sling_y = GH - 60

        # Game state
        self.hp_a = 100
        self.hp_b = 100
        self.round_num = 1
        self.current_turn = self.team_a  # player is always team_a
        self.projectiles  = []
        self.explosions   = []
        self.particles    = []

        # Weapons list for player
        self.weapons_list = [W_MISSILE, W_TANK, W_DRONE, W_BOMB, W_ROCKET, W_TORPEDO]
        self.weapon_idx   = 0

        # Aiming
        self.aiming  = False
        self.angle   = 45.0
        self.power   = 14.0
        self.mouse_down = False
        self.drag_start = None
        self.fired   = False
        self.waiting_impact = False

        # AI
        self.ai = AI(self.team_b, difficulty=1 + idx * 0.3)
        self.ai.reset()
        self.ai_shot_queued = False
        self.ai_angle = 45.0
        self.ai_power = 14.0

        # Targets
        self._build_targets()

        # Vehicles & soldiers (decorative + functional)
        self._build_army()

        # Messages
        self.messages = []  # [(text, color, timer)]
        self.hit_flash = 0

        # Camera shake
        self.shake = 0
        self.shake_x = 0
        self.shake_y = 0

        if self.audio_ok:
            sfx.play('menu', loops=-1)

    def _build_targets(self):
        """Place destructible targets on the enemy side."""
        GH = self.H
        enemy_start = self.W - 500
        self.targets = []
        configs = [
            # (x_offset, y_offset_from_floor, w, h, hp, kind)
            (0,   110, 60,  110, 80,  "bunker"),
            (80,  60,  50,  60,  60,  "block"),
            (140, 90,  40,  90,  50,  "tower"),
            (200, 60,  55,  60,  70,  "block"),
            (270, 120, 70,  120, 90,  "bunker"),
            (350, 80,  45,  80,  55,  "block"),
            (410, 100, 60,  100, 65,  "tower"),
        ]
        for xoff, h, w, ph, hp, kind in configs:
            tx = enemy_start + xoff
            ty = GH - 60 - h
            t = Target(tx, ty, w, ph, hp, self.team_b, kind)
            self.targets.append(t)

        # Add some on platforms
        t = Target(self.W-260, GH-160-80, 50, 80, 60, self.team_b, "block")
        self.targets.append(t)
        t = Target(self.W//2-60, GH-220-70, 40, 70, 50, self.team_b, "tower")
        self.targets.append(t)

    def _build_army(self):
        """Decorative vehicles and soldiers."""
        GH = self.H
        self.army_a = []  # player side
        self.army_b = []  # enemy side

        # Player side vehicles
        self.army_a.append(("tank",   170, GH-62, self.team_a, False))
        self.army_a.append(("frigate",120, GH-45, self.team_a, False))
        self.army_a.append(("jet",    300, GH-140, self.team_a, False))

        # Enemy side
        self.army_b.append(("tank",   self.W-200, GH-62, self.team_b, True))
        self.army_b.append(("warship",self.W-350, GH-42, self.team_b, True))
        self.army_b.append(("drone",  self.W-280, GH-180, self.team_b, True))
        self.army_b.append(("bomber", self.W//2,  GH-250, self.team_b, True))

        # Soldiers
        self.soldiers_a = [(120+i*25, GH-62, self.team_a) for i in range(4)]
        self.soldiers_b = [(self.W-180+i*20, GH-62, self.team_b) for i in range(4)]

    # ─── MAIN LOOP ────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    if self.state == Screen.PLAYING:
                        self.state = Screen.MENU
                    else:
                        running = False
                elif e.type == pygame.VIDEORESIZE:
                    self.W, self.H = e.w, e.h
                    self.screen = pygame.display.set_mode((self.W,self.H), pygame.RESIZABLE)

            if self.state == Screen.MENU:
                self._run_menu(events)
            elif self.state == Screen.LEVEL_SELECT:
                self._run_level_select(events)
            elif self.state == Screen.HOW_TO:
                self._run_howto(events)
            elif self.state == Screen.PLAYING:
                self._run_game(events)
            elif self.state in (Screen.WIN, Screen.LOSE):
                self._run_end(events)

            pygame.display.flip()
            self.clock.tick(FPS)

    # ─── MENU ─────────────────────────────────────────────────
    def _run_menu(self, events):
        self._menu_timer += 1
        W, H = self.W, self.H

        # Animated background
        bg = self._cached_bgs[LEVELS[0]["bg"]].copy()
        self.screen.blit(bg, (0,0))

        # Darken
        overlay = pygame.Surface((W,H), pygame.SRCALPHA)
        overlay.fill((0,0,20,160))
        self.screen.blit(overlay,(0,0))

        # Draw leaders floating
        t = self._menu_timer
        for i, (team, draw_fn) in enumerate([
            (TEAM_US, draw_trump),
            (TEAM_IL, draw_netanyahu),
            (TEAM_IR, draw_khamenei),
        ]):
            bx = W//4 * (i+1) - W//8 + (i-1)*60
            by = H//2 + int(math.sin(t*0.04 + i*2)*15)
            sz = 1.2
            draw_fn(self.screen, bx, by, sz, angry=(t//30)%2==0)
            # Name tag
            nt = self.font_sm.render(LEADER_NAMES[team], True, GOLD)
            self.screen.blit(nt,(bx-nt.get_width()//2, by+100))

        # Title
        title_shadow = self.font_big.render("WAR OF PRIDE & HONOR", True, (20,20,50))
        title = self.font_big.render("WAR OF PRIDE & HONOR", True, GOLD)
        tx = W//2 - title.get_width()//2
        ty = 60 + int(math.sin(t*0.03)*5)
        self.screen.blit(title_shadow,(tx+3,ty+3))
        self.screen.blit(title,(tx,ty))

        # Subtitle
        sub = self.font_med.render("⚔  An Artillery Strategy Game  ⚔", True, LIGHT_BLUE)
        self.screen.blit(sub,(W//2-sub.get_width()//2, 145))

        # Buttons
        buttons = [
            ("▶  PLAY",         Screen.LEVEL_SELECT, GREEN),
            ("?  HOW TO PLAY",  Screen.HOW_TO,       LIGHT_BLUE),
            ("✕  QUIT",         "quit",              RED),
        ]
        for i, (label, action, col) in enumerate(buttons):
            bw, bh = 320, 58
            bx = W//2 - bw//2
            by = H - 260 + i*75
            mx,my = pygame.mouse.get_pos()
            hover = bx <= mx <= bx+bw and by <= my <= by+bh
            pulse = int(math.sin(t*0.1)*10) if hover else 0
            bg_col = tuple(min(255,c+40) for c in col) if hover else tuple(max(0,c-40) for c in col)
            pygame.draw.rect(self.screen, bg_col, (bx-pulse//2, by-pulse//4, bw+pulse, bh+pulse//2), border_radius=12)
            pygame.draw.rect(self.screen, col, (bx-pulse//2, by-pulse//4, bw+pulse, bh+pulse//2), 3, border_radius=12)
            bt = self.font_med.render(label, True, WHITE)
            self.screen.blit(bt,(bx+bw//2-bt.get_width()//2, by+bh//2-bt.get_height()//2))

            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and hover:
                    if action == "quit":
                        pygame.quit(); sys.exit()
                    elif action == Screen.LEVEL_SELECT:
                        sfx.stop('menu')
                        self.state = Screen.LEVEL_SELECT
                    else:
                        self.state = action

        # Credits
        cr = self.font_xs.render("© War of Pride & Honor — Built with Python & Pygame", True, GRAY)
        self.screen.blit(cr,(W//2-cr.get_width()//2, H-30))

    # ─── LEVEL SELECT ─────────────────────────────────────────
    def _run_level_select(self, events):
        W, H = self.W, self.H
        self.screen.fill((10,15,40))

        title = self.font_big.render("SELECT MISSION", True, GOLD)
        self.screen.blit(title,(W//2-title.get_width()//2, 30))

        for i, lvl in enumerate(LEVELS):
            bw, bh = 700, 110
            bx = W//2 - bw//2
            by = 140 + i*130
            ta = lvl["team_a"]
            tb = lvl["team_b"]
            col_a = TEAM_COLORS[ta]
            col_b = TEAM_COLORS[tb]

            mx,my = pygame.mouse.get_pos()
            hover = bx<=mx<=bx+bw and by<=my<=by+bh
            bg_alpha = 200 if hover else 140
            panel = pygame.Surface((bw,bh), pygame.SRCALPHA)
            panel.fill((30,30,60,bg_alpha))
            self.screen.blit(panel,(bx,by))
            pygame.draw.rect(self.screen, GOLD if hover else GRAY, (bx,by,bw,bh),2,border_radius=8)

            # Flags
            draw_flag(self.screen, bx+20, by+35, ta, 50, 32)
            draw_flag(self.screen, bx+bw-70, by+35, tb, 50, 32)

            # VS
            vs = self.font_med.render("VS", True, RED)
            self.screen.blit(vs,(bx+bw//2-vs.get_width()//2, by+35))

            # Names
            ln = self.font_med.render(lvl["name"], True, WHITE)
            self.screen.blit(ln,(bx+bw//2-ln.get_width()//2, by+8))
            ld = self.font_sm.render(lvl["desc"], True, LIGHT_BLUE)
            self.screen.blit(ld,(bx+bw//2-ld.get_width()//2, by+78))

            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and hover:
                    self._init_level(i)
                    self.state = Screen.PLAYING

        back = self.font_med.render("◀ BACK", True, WHITE)
        bx = W//2 - back.get_width()//2
        by = H - 70
        mx,my = pygame.mouse.get_pos()
        hover = bx<=mx<=bx+back.get_width() and by<=my<=by+back.get_height()
        self.screen.blit(back,(bx,by))
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and hover:
                self.state = Screen.MENU

    # ─── HOW TO PLAY ──────────────────────────────────────────
    def _run_howto(self, events):
        W, H = self.W, self.H
        self.screen.fill((5,10,30))
        title = self.font_big.render("HOW TO PLAY", True, GOLD)
        self.screen.blit(title,(W//2-title.get_width()//2,30))
        
        lines = [
            ("CONTROLS", GOLD),
            ("🖱  Click & Drag on slingshot to aim",  WHITE),
            ("   Pull back further = MORE POWER",     LIGHT_BLUE),
            ("   Release to FIRE!",                   GREEN),
            ("",None),
            ("WEAPONS", GOLD),
            ("1-6  Switch weapon before firing",      WHITE),
            ("Mouse Wheel  Cycle weapons",            WHITE),
            ("",None),
            ("OBJECTIVE", GOLD),
            ("Destroy all enemy structures to win!", WHITE),
            ("Each hit reduces enemy HP",            WHITE),
            ("You have unlimited ammo!",             LIGHT_BLUE),
            ("",None),
            ("WEAPONS LIST", GOLD),
        ]
        for wk, wd in WEAPON_DATA.items():
            lines.append((f"  {wd['icon']}  {wd['name']} — Damage: {wd['damage']}  Blast: {wd['blast']}", WHITE))

        y = 110
        for txt, col in lines:
            if col is None:
                y += 10; continue
            t = self.font_sm.render(txt, True, col)
            self.screen.blit(t,(W//2-t.get_width()//2,y))
            y += 32

        back = self.font_med.render("◀ BACK", True, WHITE)
        self.screen.blit(back,(W//2-back.get_width()//2, H-60))
        mx,my = pygame.mouse.get_pos()
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                self.state = Screen.MENU

    # ─── GAME LOOP ────────────────────────────────────────────
    def _run_game(self, events):
        self.W, self.H = self.screen.get_size()
        W, H = self.W, self.H

        # Handle shake
        if self.shake > 0:
            self.shake -= 1
            self.shake_x = random.randint(-self.shake, self.shake)
            self.shake_y = random.randint(-self.shake, self.shake)
        else:
            self.shake_x = self.shake_y = 0

        self._handle_input(events)
        self._update()
        self._draw()

    def _handle_input(self, events):
        mx, my = pygame.mouse.get_pos()

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.current_turn == self.team_a and not self.waiting_impact:
                    # Check if near slingshot
                    sx, sy = self.sling_x, self.sling_y - 60
                    dist = math.hypot(mx-sx, my-sy)
                    if dist < 70:
                        self.mouse_down = True
                        self.drag_start = (mx, my)
                        self.aiming = True

            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                if self.mouse_down and self.aiming and not self.waiting_impact:
                    self._fire_player(mx, my)
                self.mouse_down = False
                self.aiming = False

            elif e.type == pygame.MOUSEWHEEL:
                self.weapon_idx = (self.weapon_idx + e.y) % len(self.weapons_list)

            elif e.type == pygame.KEYDOWN:
                key = e.key
                if pygame.K_1 <= key <= pygame.K_6:
                    self.weapon_idx = min(key - pygame.K_1, len(self.weapons_list)-1)
                elif key == pygame.K_r:
                    self._init_level(self.current_level_idx)
                elif key == pygame.K_n:  # next level
                    next_idx = (self.current_level_idx + 1) % len(LEVELS)
                    self._init_level(next_idx)

        # Aiming calculation
        if self.mouse_down and self.drag_start:
            dx = self.drag_start[0] - mx
            dy = self.drag_start[1] - my
            self.power = min(math.hypot(dx, dy) * 0.22, MAX_POWER)
            self.angle = math.degrees(math.atan2(-dy, dx))
            self.angle = max(-60, min(80, self.angle))

    def _fire_player(self, mx, my):
        if self.drag_start is None:
            return
        dx = self.drag_start[0] - mx
        dy = self.drag_start[1] - my
        power = min(math.hypot(dx,dy)*0.22, MAX_POWER)
        if power < 1:
            return
        angle = math.atan2(-dy, dx)
        vx = power * math.cos(angle)
        vy = -power * math.sin(angle)

        wtype = self.weapons_list[self.weapon_idx]
        blast = WEAPON_DATA[wtype]["blast"]
        p = Projectile(self.sling_x, self.sling_y-65, vx, vy, wtype, self.team_a, blast)

        # Drone targets nearest enemy
        if wtype == W_DRONE and self.targets:
            alive = [t for t in self.targets if t.alive]
            if alive:
                tgt = random.choice(alive)
                p.set_target(tgt.x+tgt.w//2, tgt.y+tgt.h//2)

        self.projectiles.append(p)
        self.fired = True
        self.waiting_impact = True
        self.aiming = False
        sfx.play('launch')

    def _fire_ai(self):
        wtype = random.choice(self.weapons_list)
        blast = WEAPON_DATA[wtype]["blast"]
        angle_r = math.radians(self.ai_angle)
        power = self.ai_power
        # AI fires from right side, toward left
        sx = self.W - 150
        sy = self.H - 120
        vx = -power * math.cos(angle_r)
        vy = -power * math.sin(angle_r)
        p = Projectile(sx, sy, vx, vy, wtype, self.team_b, blast)
        # Rough targeting
        alive_a_targets = [t for t in self.targets if t.alive and t.team == self.team_b]
        # Fire at sling area roughly
        p.set_target(self.sling_x, self.sling_y) if wtype == W_DRONE else None
        self.projectiles.append(p)
        self.waiting_impact = True
        sfx.play('launch')

    def _update(self):
        W, H = self.W, self.H

        # AI turn logic
        if self.current_turn == self.team_b and not self.waiting_impact:
            self.ai.update()
            if not self.ai.thinking:
                alive_targets = [t for t in self.targets if t.alive and t.team == self.team_a] if hasattr(self,'targets') else []
                sx = W-150; sy = H-120
                self.ai_angle, self.ai_power = self.ai.compute_shot(sx, sy, alive_targets)
                self._fire_ai()
                self.ai.reset()

        # Update projectiles
        any_active = False
        for p in self.projectiles:
            if p.active:
                p.update(self.ground, W, H)
                any_active = True

            if not p.active and not hasattr(p, '_exploded'):
                p._exploded = True
                self._trigger_explosion(p)

        # Check if all projectiles done
        all_done = not any_active or all(not p.active for p in self.projectiles)
        if self.waiting_impact and all_done and self.projectiles:
            self.waiting_impact = False
            self.fired = False
            # Switch turns
            if self.current_turn == self.team_a:
                self.current_turn = self.team_b
                self.ai.reset()
            else:
                self.current_turn = self.team_a
            self.round_num += 1
            self.projectiles = [p for p in self.projectiles if p.active]

        # Update explosions
        for ex in self.explosions[:]:
            ex.update()
            if ex.done:
                self.explosions.remove(ex)

        # Update particles
        for pt in self.particles[:]:
            pt.update()
            if pt.life <= 0:
                self.particles.remove(pt)

        # Update targets
        for t in self.targets:
            t.update()

        # Messages
        for m in self.messages[:]:
            m[2] -= 1
            if m[2] <= 0:
                self.messages.remove(m)

        # Check win/lose
        alive = [t for t in self.targets if t.alive]
        if not alive or self.hp_b <= 0:
            self.score_a += 1
            self.state = Screen.WIN
        if self.hp_a <= 0:
            self.state = Screen.LOSE

    def _trigger_explosion(self, proj):
        x, y = int(proj.x), int(proj.y)
        blast = proj.blast_r
        dmg = proj.damage
        ex = Explosion(x, y, blast)
        self.explosions.append(ex)
        self.shake = min(20, blast//5)
        sfx.play('explosion')

        # Damage nearby targets
        for tgt in self.targets:
            if tgt.alive and tgt.check_hit(x, y, blast):
                actual_dmg = int(dmg * random.uniform(0.7, 1.3))
                tgt.take_damage(actual_dmg, x, y)
                self.hp_b = max(0, self.hp_b - actual_dmg//4)
                sfx.play('hit')
                self.messages.append([f"-{actual_dmg} HP!", RED, 90])

        # Damage player HP if AI hit close to sling
        if proj.team == self.team_b:
            dist = math.hypot(x - self.sling_x, y - (self.sling_y-60))
            if dist < blast + 60:
                hit = int(dmg * random.uniform(0.5, 1.0))
                self.hp_a = max(0, self.hp_a - hit)
                self.messages.append([f"BASE HIT: -{hit} HP", ORANGE, 100])

        # Spawn particles
        for _ in range(20):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(2, 8)
            vx = math.cos(angle)*speed
            vy = math.sin(angle)*speed - 4
            col = random.choice([ORANGE, RED, YELLOW, (80,80,80)])
            self.particles.append(
                Particle(x+random.randint(-20,20), y+random.randint(-20,20),
                         vx, vy, col, random.randint(3,9), random.randint(30,60))
            )

    def _draw(self):
        W, H = self.W, self.H
        sx, sy = self.shake_x, self.shake_y

        # Background
        bg = self._cached_bgs.get(self.bg_type)
        if bg:
            self.screen.blit(bg, (sx, sy))
        else:
            self.screen.fill((20,30,80))

        # Ground
        draw_ground(self.screen, [(x+sx,y+sy,w,h) for x,y,w,h in self.ground], self.bg_type)

        # Army vehicles
        for kind, ax, ay, team, flip in self.army_a + self.army_b:
            ax2,ay2 = ax+sx, ay+sy
            if kind == "tank":
                draw_tank(self.screen, ax2, ay2, team, flip)
            elif kind == "warship":
                draw_warship(self.screen, ax2, ay2, team)
            elif kind == "frigate":
                draw_frigate(self.screen, ax2, ay2, team)
            elif kind == "jet":
                draw_fighter_jet(self.screen, ax2, ay2, team, flip)
            elif kind == "bomber":
                draw_bomber(self.screen, ax2, ay2, team)
            elif kind == "drone":
                draw_drone(self.screen, ax2, ay2, team)

        # Soldiers
        for (solx, soly, team) in self.soldiers_a + self.soldiers_b:
            draw_soldier(self.screen, solx+sx, soly+sy, team, 0.65)

        # Slingshot
        draw_slingshot(self.screen, self.sling_x+sx, self.sling_y+sy)

        # Leaders (larger, stationed behind lines)
        draw_trump(self.screen, 80+sx, self.sling_y-5+sy, 0.85) if self.team_a == TEAM_US else None
        draw_netanyahu(self.screen, 80+sx, self.sling_y-5+sy, 0.85) if self.team_a == TEAM_IL else None
        draw_khamenei(self.screen, 80+sx, self.sling_y-5+sy, 0.85) if self.team_a == TEAM_IR else None

        draw_trump(self.screen, W-100+sx, self.sling_y-5+sy, 0.85) if self.team_b == TEAM_US else None
        draw_netanyahu(self.screen, W-100+sx, self.sling_y-5+sy, 0.85) if self.team_b == TEAM_IL else None
        draw_khamenei(self.screen, W-100+sx, self.sling_y-5+sy, 0.85) if self.team_b == TEAM_IR else None

        # Targets
        for tgt in self.targets:
            tgt.x_disp = tgt.x + sx
            tgt.y_disp = tgt.y + sy
            # Draw at offset
            orig_x, orig_y = tgt.x, tgt.y
            tgt.x += sx; tgt.y += sy
            tgt.draw(self.screen, self.font_xs)
            tgt.x, tgt.y = orig_x, orig_y

        # Particles
        for pt in self.particles:
            pt.draw(self.screen)

        # Explosions
        for ex in self.explosions:
            ex.draw(self.screen)

        # Projectiles
        for p in self.projectiles:
            p.draw(self.screen)

        # Aiming UI
        if self.aiming and self.current_turn == self.team_a:
            mx,my = pygame.mouse.get_pos()
            if self.drag_start:
                dx = self.drag_start[0]-mx
                dy = self.drag_start[1]-my
                power = min(math.hypot(dx,dy)*0.22, MAX_POWER)
                angle = math.atan2(-dy, dx)
                vx = power*math.cos(angle)
                vy = -power*math.sin(angle)
                draw_power_arc(self.screen, self.sling_x, self.sling_y-65, vx, vy)

                # Rubber band
                pygame.draw.line(self.screen, (80,40,10),
                                 (self.sling_x-25, self.sling_y-70), (mx, my), 3)
                pygame.draw.line(self.screen, (80,40,10),
                                 (self.sling_x+25, self.sling_y-70), (mx, my), 3)

                # Power indicator
                pw_pct = power / MAX_POWER
                pw_col = GREEN if pw_pct < 0.5 else YELLOW if pw_pct < 0.8 else RED
                pw_txt = self.font_sm.render(f"Power: {int(pw_pct*100)}%", True, pw_col)
                self.screen.blit(pw_txt,(mx+15,my-20))

        # Weapon selector bar
        self._draw_weapon_bar()

        # HUD
        draw_hud(self.screen, self.font_xs, self.font_sm,
                 self.team_a, self.team_b,
                 self.score_a, self.score_b,
                 self.hp_a, self.hp_b,
                 self.current_turn,
                 self.level_name,
                 WEAPON_DATA[self.weapons_list[self.weapon_idx]]["name"],
                 self.round_num)

        # Messages
        for i, (txt, col, timer) in enumerate(self.messages):
            alpha = min(255, timer*4)
            ms = self.font_med.render(txt, True, col)
            self.screen.blit(ms, (W//2-ms.get_width()//2, H//2-60-i*45))

        # Controls hint
        if self.round_num == 1 and self.current_turn == self.team_a:
            hint = self.font_xs.render("Click & drag on slingshot to aim  |  1-6 switch weapon  |  R=restart  |  ESC=menu", True, LIGHT_BLUE)
            self.screen.blit(hint,(W//2-hint.get_width()//2, H-28))

        # AI thinking indicator
        if self.current_turn == self.team_b and self.ai.thinking:
            ai_txt = self.font_med.render(f"⚠  {LEADER_NAMES[self.team_b]} is targeting you...", True, RED)
            self.screen.blit(ai_txt,(W//2-ai_txt.get_width()//2, H//2+80))

    def _draw_weapon_bar(self):
        W, H = self.W, self.H
        nw = len(self.weapons_list)
        bar_w = nw * 80 + 20
        bx = W//2 - bar_w//2
        by = H - 70

        bg = pygame.Surface((bar_w, 60), pygame.SRCALPHA)
        bg.fill((0,0,0,160))
        self.screen.blit(bg,(bx,by))

        for i, wk in enumerate(self.weapons_list):
            wd = WEAPON_DATA[wk]
            wx = bx + 10 + i*80
            wy = by + 5
            sel = (i == self.weapon_idx)
            col = GOLD if sel else GRAY
            pygame.draw.rect(self.screen, col, (wx,wy,70,50), 2+(2 if sel else 0), border_radius=6)
            if sel:
                bg2 = pygame.Surface((70,50), pygame.SRCALPHA)
                bg2.fill((255,200,0,40))
                self.screen.blit(bg2,(wx,wy))

            ic = self.font_med.render(wd["icon"],True,WHITE)
            self.screen.blit(ic,(wx+35-ic.get_width()//2,wy+2))
            nm = self.font_xs.render(str(i+1),True,col)
            self.screen.blit(nm,(wx+3,wy+36))

    # ─── END SCREEN ───────────────────────────────────────────
    def _run_end(self, events):
        W, H = self.W, self.H
        win = (self.state == Screen.WIN)

        self.screen.fill((5,5,20))
        overlay = pygame.Surface((W,H), pygame.SRCALPHA)
        overlay.fill((0,0,0,120))
        self.screen.blit(overlay,(0,0))

        if win:
            title_txt = "VICTORY!"
            title_col = GOLD
            msg_txt = f"{LEADER_NAMES[self.team_a]}'s forces are victorious!"
            sfx.play('victory') if not hasattr(self,'_played_end') else None
        else:
            title_txt = "DEFEATED"
            title_col = RED
            msg_txt = f"{LEADER_NAMES[self.team_b]} crushes your forces!"
        self._played_end = True

        # Fireworks if win
        if win:
            for _ in range(5):
                fx = random.randint(0,W)
                fy = random.randint(0,H//2)
                fc = (random.randint(150,255),random.randint(150,255),random.randint(0,200))
                for fa in range(0,360,30):
                    fv = random.uniform(2,8)
                    fx2 = fx + math.cos(math.radians(fa))*random.randint(20,80)
                    fy2 = fy + math.sin(math.radians(fa))*random.randint(20,80)
                    pygame.draw.line(self.screen, fc,(fx,fy),(int(fx2),int(fy2)),2)

        title = self.font_big.render(title_txt, True, title_col)
        self.screen.blit(title,(W//2-title.get_width()//2,H//3-50))
        msg = self.font_med.render(msg_txt, True, WHITE)
        self.screen.blit(msg,(W//2-msg.get_width()//2,H//3+60))

        score = self.font_med.render(f"Score: {self.score_a}  Losses: {self.score_b}", True, LIGHT_BLUE)
        self.screen.blit(score,(W//2-score.get_width()//2,H//3+110))

        buttons = [
            ("▶ NEXT MISSION" if win else "↻ RETRY",  "next" if win else "retry", GREEN if win else YELLOW),
            ("⌂ MAIN MENU",  "menu", LIGHT_BLUE),
        ]
        for i,(label,action,col) in enumerate(buttons):
            bw,bh = 300,55
            bx = W//2-bw//2
            by = H//2+80+i*75
            mx,my = pygame.mouse.get_pos()
            hover = bx<=mx<=bx+bw and by<=my<=by+bh
            c2 = tuple(min(255,c+50) for c in col) if hover else col
            pygame.draw.rect(self.screen,c2,(bx,by,bw,bh),border_radius=10)
            pygame.draw.rect(self.screen,WHITE,(bx,by,bw,bh),2,border_radius=10)
            bt = self.font_med.render(label,True,BLACK if hover else WHITE)
            self.screen.blit(bt,(bx+bw//2-bt.get_width()//2,by+bh//2-bt.get_height()//2))
            for e in events:
                if e.type==pygame.MOUSEBUTTONDOWN and hover:
                    delattr(self,'_played_end') if hasattr(self,'_played_end') else None
                    if action=="next":
                        next_idx=(self.current_level_idx+1)%len(LEVELS)
                        self._init_level(next_idx)
                        self.state=Screen.PLAYING
                    elif action=="retry":
                        self._init_level(self.current_level_idx)
                        self.state=Screen.PLAYING
                    else:
                        self.state=Screen.MENU
