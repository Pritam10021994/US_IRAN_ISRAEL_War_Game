"""
Procedural art engine — every sprite drawn with pygame shapes.
No external image files needed.
"""
import pygame
import math
import random
from constants import *


def draw_gradient_rect(surf, rect, c1, c2, vertical=True):
    """Draw a vertical or horizontal gradient rectangle."""
    x, y, w, h = rect
    for i in range(h if vertical else w):
        t = i / max(h if vertical else w, 1)
        r = int(c1[0] + (c2[0]-c1[0])*t)
        g = int(c1[1] + (c2[1]-c1[1])*t)
        b = int(c1[2] + (c2[2]-c1[2])*t)
        if vertical:
            pygame.draw.line(surf, (r,g,b), (x, y+i), (x+w, y+i))
        else:
            pygame.draw.line(surf, (r,g,b), (x+i, y), (x+i, y+h))


# ─── BACKGROUNDS ─────────────────────────────────────────────
def draw_sky_gulf(surf, W, H):
    """Persian Gulf — dusk sky, calm water."""
    draw_gradient_rect(surf, (0,0,W,H//2), (20,30,80), (220,120,50))
    draw_gradient_rect(surf, (0,H//2,W,H//2), (20,80,160), (10,40,100))
    # Stars
    random.seed(42)
    for _ in range(80):
        sx, sy = random.randint(0,W), random.randint(0,H//3)
        pygame.draw.circle(surf, (255,255,200,180), (sx,sy), random.randint(1,2))
    # Sun
    pygame.draw.circle(surf, (255,200,80), (W//2, H//3), 55)
    pygame.draw.circle(surf, (255,230,120), (W//2, H//3), 40)
    # Water reflections
    for i in range(20):
        rx = random.randint(0,W)
        ry = H//2 + random.randint(0, H//4)
        pygame.draw.ellipse(surf, (255,160,60,80), (rx, ry, random.randint(30,100), 4))

def draw_sky_desert(surf, W, H):
    """Desert — harsh midday sun."""
    draw_gradient_rect(surf, (0,0,W,H//2), (80,140,220), (220,200,150))
    draw_gradient_rect(surf, (0,H//2,W,H//4), (210,180,110), (180,150,80))
    # Dunes
    for i in range(6):
        dx = i * W//5 - 50
        pts = [(dx-80,H), (dx+60,H//2+80), (dx+200,H)]
        pygame.draw.polygon(surf, (210,180,100), pts)
        pygame.draw.polygon(surf, (230,200,120), [(dx,H//2+120),(dx+60,H//2+80),(dx+120,H//2+120)])
    pygame.draw.circle(surf, (255,240,80), (W-120, 100), 60)

def draw_sky_city(surf, W, H):
    """City — night skyline."""
    draw_gradient_rect(surf, (0,0,W,H), (5,5,20), (15,20,60))
    # Stars
    random.seed(7)
    for _ in range(120):
        pygame.draw.circle(surf, (255,255,255), (random.randint(0,W), random.randint(0,H//2)), 1)
    # Moon
    pygame.draw.circle(surf, (230,230,200), (W-160, 90), 40)
    pygame.draw.circle(surf, (10,10,40), (W-145, 82), 36)
    # Buildings
    bldg_colors = [(30,35,60),(25,30,55),(35,40,65),(20,25,50)]
    random.seed(13)
    for i in range(18):
        bw = random.randint(40,90)
        bh = random.randint(80,300)
        bx = i * 70 + random.randint(-10,10)
        by = H - bh
        pygame.draw.rect(surf, random.choice(bldg_colors), (bx, by, bw, bh))
        # Windows
        for wy in range(by+10, H-10, 20):
            for wx in range(bx+8, bx+bw-8, 15):
                if random.random() > 0.35:
                    pygame.draw.rect(surf, (255,220,100,180), (wx, wy, 8, 10))

def draw_background(surf, bg_type):
    W, H = surf.get_size()
    if bg_type == "gulf":
        draw_sky_gulf(surf, W, H)
    elif bg_type == "desert":
        draw_sky_desert(surf, W, H)
    else:
        draw_sky_city(surf, W, H)


# ─── GROUND ──────────────────────────────────────────────────
def draw_ground(surf, ground_rects, bg_type):
    W, H = surf.get_size()
    if bg_type in ("gulf", "city"):
        ground_c1, ground_c2 = (50,120,40), (35,85,20)
    else:
        ground_c1, ground_c2 = (200,170,90), (160,130,60)
    
    for rect in ground_rects:
        rx, ry, rw, rh = rect
        if bg_type == "gulf":
            # Water at sea level
            if ry > H - 160:
                pygame.draw.rect(surf, (20,80,160), rect)
                # Waves
                for wx in range(rx, rx+rw, 30):
                    pygame.draw.arc(surf, (60,140,210), (wx, ry+5, 30, 10), 0, math.pi, 2)
            else:
                draw_gradient_rect(surf, rect, ground_c1, ground_c2)
                pygame.draw.line(surf, (80,160,60), (rx,ry), (rx+rw, ry), 3)
        else:
            draw_gradient_rect(surf, rect, ground_c1, ground_c2)
            pygame.draw.line(surf, (100,170,70), (rx,ry), (rx+rw, ry), 3)


# ─── CHARACTERS (Leaders) ────────────────────────────────────
def draw_trump(surf, x, y, size=1.0, angry=False):
    """Draw Donald Trump — blonde hair, red tie, suit."""
    s = size
    # Body — dark suit
    body_pts = [(x-25*s, y), (x+25*s, y), (x+30*s, y+70*s), (x-30*s, y+70*s)]
    pygame.draw.polygon(surf, (30,30,80), body_pts)
    # White shirt
    pygame.draw.polygon(surf, WHITE, [(x-8*s,y+5*s),(x+8*s,y+5*s),(x+5*s,y+60*s),(x-5*s,y+60*s)])
    # Red tie
    pygame.draw.polygon(surf, (200,20,20), [(x-5*s,y+10*s),(x+5*s,y+10*s),(x+3*s,y+55*s),(x,y+65*s),(x-3*s,y+55*s)])
    # Head
    pygame.draw.ellipse(surf, (255,210,170), (x-22*s, y-55*s, 44*s, 55*s))
    # Hair — famous golden swoosh
    hair_pts = [(x-22*s,y-35*s),(x-25*s,y-55*s),(x-10*s,y-65*s),(x+22*s,y-60*s),(x+25*s,y-45*s),(x+15*s,y-38*s)]
    pygame.draw.polygon(surf, (240,210,100), hair_pts)
    pygame.draw.polygon(surf, (220,180,60), [(x-8*s,y-50*s),(x+20*s,y-60*s),(x+20*s,y-45*s),(x,y-42*s)])
    # Eyes
    eye_y = y - 38*s
    pygame.draw.ellipse(surf, (30,30,30), (x-12*s, eye_y, 10*s, 8*s))
    pygame.draw.ellipse(surf, (30,30,30), (x+2*s, eye_y, 10*s, 8*s))
    pygame.draw.circle(surf, WHITE, (int(x-8*s), int(eye_y+2*s)), int(3*s))
    pygame.draw.circle(surf, WHITE, (int(x+6*s), int(eye_y+2*s)), int(3*s))
    if angry:
        pygame.draw.line(surf, (80,40,10), (x-12*s,eye_y-3*s),(x-2*s,eye_y), 3)
        pygame.draw.line(surf, (80,40,10), (x+2*s,eye_y),(x+12*s,eye_y-3*s), 3)
    # Mouth — pursed/O shape
    mouth_y = y - 22*s
    pygame.draw.ellipse(surf, (180,80,80), (x-8*s, mouth_y, 16*s, 9*s))
    pygame.draw.ellipse(surf, (220,100,100), (x-5*s, mouth_y+2*s, 10*s, 5*s))
    # Ears
    pygame.draw.ellipse(surf, (240,190,160), (x-27*s, y-40*s, 8*s, 12*s))
    pygame.draw.ellipse(surf, (240,190,160), (x+19*s, y-40*s, 8*s, 12*s))
    # Arms
    pygame.draw.line(surf, (30,30,80), (int(x-25*s),int(y+10*s)), (int(x-45*s),int(y+50*s)), int(14*s))
    pygame.draw.line(surf, (30,30,80), (int(x+25*s),int(y+10*s)), (int(x+45*s),int(y+50*s)), int(14*s))
    # Hands
    pygame.draw.circle(surf, (255,210,170), (int(x-45*s), int(y+50*s)), int(10*s))
    pygame.draw.circle(surf, (255,210,170), (int(x+45*s), int(y+50*s)), int(10*s))
    # Legs
    pygame.draw.rect(surf, (20,20,70), (int(x-22*s), int(y+60*s), int(18*s), int(30*s)))
    pygame.draw.rect(surf, (20,20,70), (int(x+4*s), int(y+60*s), int(18*s), int(30*s)))
    # Shoes
    pygame.draw.ellipse(surf, (10,10,10), (int(x-25*s), int(y+82*s), int(22*s), int(10*s)))
    pygame.draw.ellipse(surf, (10,10,10), (int(x+2*s), int(y+82*s), int(22*s), int(10*s)))

def draw_netanyahu(surf, x, y, size=1.0, angry=False):
    """Draw Netanyahu — bald, dark suit, Israeli flag pin."""
    s = size
    # Body — navy suit
    body_pts = [(x-25*s,y),(x+25*s,y),(x+30*s,y+70*s),(x-30*s,y+70*s)]
    pygame.draw.polygon(surf, (20,30,100), body_pts)
    # White shirt
    pygame.draw.polygon(surf, WHITE, [(x-8*s,y+5*s),(x+8*s,y+5*s),(x+5*s,y+60*s),(x-5*s,y+60*s)])
    # Blue tie
    pygame.draw.polygon(surf, (30,60,200), [(x-5*s,y+10*s),(x+5*s,y+10*s),(x+3*s,y+50*s),(x,y+60*s),(x-3*s,y+50*s)])
    # Head — bald
    pygame.draw.ellipse(surf, (220,180,150), (x-22*s, y-55*s, 44*s, 55*s))
    # Bald shine
    pygame.draw.ellipse(surf, (240,205,180), (x-10*s, y-55*s, 20*s, 15*s))
    # Remaining hair sides (gray)
    pygame.draw.arc(surf, (140,130,130), (x-24*s, y-40*s, 10*s, 20*s), math.pi/2, math.pi*3/2, int(5*s))
    pygame.draw.arc(surf, (140,130,130), (x+14*s, y-40*s, 10*s, 20*s), -math.pi/2, math.pi/2, int(5*s))
    # Eyebrows
    pygame.draw.line(surf, (80,60,40), (int(x-14*s), int(y-35*s)), (int(x-2*s), int(y-32*s)), int(3*s))
    pygame.draw.line(surf, (80,60,40), (int(x+2*s), int(y-32*s)), (int(x+14*s), int(y-35*s)), int(3*s))
    # Eyes
    eye_y = y - 28*s
    pygame.draw.ellipse(surf, (50,40,30), (x-13*s, eye_y, 10*s, 8*s))
    pygame.draw.ellipse(surf, (50,40,30), (x+3*s, eye_y, 10*s, 8*s))
    pygame.draw.circle(surf, WHITE, (int(x-9*s), int(eye_y+3*s)), int(2*s))
    pygame.draw.circle(surf, WHITE, (int(x+7*s), int(eye_y+3*s)), int(2*s))
    # Nose prominent
    pygame.draw.polygon(surf, (200,160,130), [(x-3*s,y-22*s),(x+3*s,y-22*s),(x+5*s,y-12*s),(x-5*s,y-12*s)])
    # Mouth
    mouth_y = y - 10*s
    pygame.draw.line(surf, (140,80,60), (int(x-8*s),int(mouth_y)), (int(x+8*s),int(mouth_y)), int(3*s))
    if angry:
        pygame.draw.line(surf, (140,80,60), (int(x-8*s),int(mouth_y)), (int(x),int(mouth_y+5*s)), int(3*s))
    # Arms
    pygame.draw.line(surf, (20,30,100), (int(x-25*s),int(y+10*s)), (int(x-45*s),int(y+50*s)), int(14*s))
    pygame.draw.line(surf, (20,30,100), (int(x+25*s),int(y+10*s)), (int(x+45*s),int(y+50*s)), int(14*s))
    pygame.draw.circle(surf, (220,180,150), (int(x-45*s), int(y+50*s)), int(10*s))
    pygame.draw.circle(surf, (220,180,150), (int(x+45*s), int(y+50*s)), int(10*s))
    # Legs
    pygame.draw.rect(surf, (15,25,90), (int(x-22*s), int(y+60*s), int(18*s), int(30*s)))
    pygame.draw.rect(surf, (15,25,90), (int(x+4*s), int(y+60*s), int(18*s), int(30*s)))
    pygame.draw.ellipse(surf, (10,10,10), (int(x-25*s), int(y+82*s), int(22*s), int(10*s)))
    pygame.draw.ellipse(surf, (10,10,10), (int(x+2*s), int(y+82*s), int(22*s), int(10*s)))

def draw_khamenei(surf, x, y, size=1.0, angry=False):
    """Draw Khamenei — turban, robes, glasses, beard."""
    s = size
    # Robe — black
    body_pts = [(x-30*s,y),(x+30*s,y),(x+35*s,y+80*s),(x-35*s,y+80*s)]
    pygame.draw.polygon(surf, (20,20,20), body_pts)
    # Inner robe
    pygame.draw.polygon(surf, (40,40,40), [(x-12*s,y+5*s),(x+12*s,y+5*s),(x+8*s,y+70*s),(x-8*s,y+70*s)])
    # Head / face
    pygame.draw.ellipse(surf, (200,165,130), (x-22*s, y-50*s, 44*s, 52*s))
    # Black turban
    turban_pts = [(x-25*s,y-38*s),(x-28*s,y-55*s),(x-15*s,y-68*s),(x,y-72*s),(x+15*s,y-68*s),(x+28*s,y-55*s),(x+25*s,y-38*s)]
    pygame.draw.polygon(surf, (10,10,10), turban_pts)
    # Turban wrap lines
    pygame.draw.arc(surf, (30,30,30), (x-28*s,y-70*s,56*s,35*s), 0, math.pi, int(3*s))
    # Eyebrows
    pygame.draw.line(surf, (30,20,10), (int(x-16*s),int(y-30*s)),(int(x-3*s),int(y-27*s)), int(3*s))
    pygame.draw.line(surf, (30,20,10), (int(x+3*s),int(y-27*s)),(int(x+16*s),int(y-30*s)), int(3*s))
    # Glasses
    pygame.draw.rect(surf, (20,20,20), (x-18*s, y-26*s, 14*s, 11*s), int(2*s))
    pygame.draw.rect(surf, (20,20,20), (x+4*s, y-26*s, 14*s, 11*s), int(2*s))
    pygame.draw.line(surf, (20,20,20), (int(x-4*s),int(y-21*s)),(int(x+4*s),int(y-21*s)), int(2*s))
    # Eyes behind glasses
    pygame.draw.circle(surf, (50,40,30), (int(x-11*s),int(y-21*s)), int(3*s))
    pygame.draw.circle(surf, (50,40,30), (int(x+11*s),int(y-21*s)), int(3*s))
    # Nose
    pygame.draw.ellipse(surf, (180,145,110), (x-4*s, y-15*s, 8*s, 10*s))
    # Beard — full black
    beard_pts = [(x-20*s,y-12*s),(x+20*s,y-12*s),(x+25*s,y+10*s),(x+15*s,y+18*s),(x,y+22*s),(x-15*s,y+18*s),(x-25*s,y+10*s)]
    pygame.draw.polygon(surf, (15,12,10), beard_pts)
    # Gray streaks in beard
    for bx_off, by_off in [(-8,5),(0,12),(8,5)]:
        pygame.draw.line(surf, (100,100,100),(int(x+bx_off*s),int(y-5*s)),(int(x+bx_off*s*0.7),int(y+18*s)),int(2*s))
    # Mustache
    pygame.draw.ellipse(surf, (20,15,10), (x-12*s, y-14*s, 24*s, 6*s))
    # Arms in robes
    pygame.draw.line(surf, (20,20,20),(int(x-30*s),int(y+10*s)),(int(x-50*s),int(y+55*s)),int(16*s))
    pygame.draw.line(surf, (20,20,20),(int(x+30*s),int(y+10*s)),(int(x+50*s),int(y+55*s)),int(16*s))
    pygame.draw.ellipse(surf, (200,165,130),(x-57*s,y+47*s,16*s,16*s))
    pygame.draw.ellipse(surf, (200,165,130),(x+41*s,y+47*s,16*s,16*s))
    # Legs
    pygame.draw.rect(surf, (15,15,15),(int(x-20*s),int(y+70*s),int(17*s),int(25*s)))
    pygame.draw.rect(surf, (15,15,15),(int(x+3*s),int(y+70*s),int(17*s),int(25*s)))
    pygame.draw.ellipse(surf, (30,20,10),(int(x-23*s),int(y+87*s),int(22*s),int(10*s)))
    pygame.draw.ellipse(surf, (30,20,10),(int(x+1*s),int(y+87*s),int(22*s),int(10*s)))

LEADER_DRAW = {
    TEAM_US: draw_trump,
    TEAM_IL: draw_netanyahu,
    TEAM_IR: draw_khamenei,
}


# ─── SOLDIERS ────────────────────────────────────────────────
def draw_soldier(surf, x, y, team, size=0.6):
    s = size
    color = TEAM_COLORS[team]
    skin = (210,170,120)
    # Helmet
    pygame.draw.ellipse(surf, (50,70,50), (x-12*s, y-28*s, 24*s, 16*s))
    pygame.draw.rect(surf, (50,70,50), (x-14*s, y-16*s, 28*s, 5*s))
    # Head
    pygame.draw.ellipse(surf, skin, (x-10*s, y-20*s, 20*s, 20*s))
    # Body
    pygame.draw.rect(surf, color, (x-12*s, y, 24*s, 22*s))
    # Arms
    pygame.draw.line(surf, color, (int(x-12*s),int(y+5*s)),(int(x-22*s),int(y+18*s)),int(6*s))
    pygame.draw.line(surf, color, (int(x+12*s),int(y+5*s)),(int(x+22*s),int(y+18*s)),int(6*s))
    # Rifle
    pygame.draw.rect(surf, DARK_GRAY, (x+14*s, y+10*s, 20*s, 5*s))
    pygame.draw.rect(surf, (50,40,30), (x+32*s, y+10*s, 3*s, 5*s))
    # Legs
    pygame.draw.rect(surf, (40,55,40), (x-10*s, y+22*s, 9*s, 18*s))
    pygame.draw.rect(surf, (40,55,40), (x+1*s, y+22*s, 9*s, 18*s))
    # Boots
    pygame.draw.ellipse(surf, (20,15,10), (x-12*s, y+35*s, 14*s, 8*s))
    pygame.draw.ellipse(surf, (20,15,10), (x-1*s, y+35*s, 14*s, 8*s))


# ─── VEHICLES ────────────────────────────────────────────────
def draw_tank(surf, x, y, team, flip=False):
    color = TEAM_COLORS[team]
    dark = tuple(max(0,c-40) for c in color)
    # Body
    pygame.draw.rect(surf, color, (x-45, y-18, 90, 30))
    pygame.draw.polygon(surf, dark, [(x-50,y-18),(x-35,y-32),(x+35,y-32),(x+50,y-18)])
    # Turret
    pygame.draw.ellipse(surf, dark, (x-20, y-40, 40, 22))
    # Barrel
    barrel_dir = -1 if flip else 1
    pygame.draw.rect(surf, (40,40,40), (x, y-35, barrel_dir*55, 8))
    # Wheels
    for wx in range(-40, 50, 18):
        pygame.draw.circle(surf, (30,30,30), (x+wx, y+15), 14)
        pygame.draw.circle(surf, (60,60,60), (x+wx, y+15), 8)
    # Track
    pygame.draw.rect(surf, (30,20,10), (x-50, y+4, 100, 8))
    # Star/insignia
    pygame.draw.circle(surf, WHITE, (x, y-26), 6)
    pygame.draw.polygon(surf, (200,180,30), [(x,y-32),(x+4,y-22),(x-4,y-22)])

def draw_warship(surf, x, y, team):
    color = TEAM_COLORS[team]
    gray = (100,110,120)
    # Hull
    pts = [(x-100,y),(x+100,y),(x+90,y+35),(x-90,y+35)]
    pygame.draw.polygon(surf, gray, pts)
    pygame.draw.polygon(surf, (80,90,100), [(x-100,y),(x+100,y),(x+80,y+15),(x-80,y+15)])
    # Superstructure
    pygame.draw.rect(surf, (90,100,110), (x-30, y-50, 60, 55))
    pygame.draw.rect(surf, (70,80,90), (x-15, y-75, 30, 30))
    # Radar
    pygame.draw.circle(surf, color, (x, y-75), 10)
    pygame.draw.line(surf, (200,200,200), (x,y-75),(x+20,y-65),2)
    # Gun turrets
    pygame.draw.rect(surf, (60,70,80), (x-80, y-15, 30, 18))
    pygame.draw.rect(surf, (40,40,40), (x-65, y-15, 5, -20))
    pygame.draw.rect(surf, (60,70,80), (x+50, y-15, 30, 18))
    pygame.draw.rect(surf, (40,40,40), (x+60, y-15, 5, -20))
    # Wake / water line
    pygame.draw.ellipse(surf, (100,160,220), (x-110, y+30, 220, 15))

def draw_frigate(surf, x, y, team):
    color = TEAM_COLORS[team]
    # Smaller warship
    pts = [(x-60,y),(x+60,y),(x+50,y+25),(x-50,y+25)]
    pygame.draw.polygon(surf, (90,100,115), pts)
    pygame.draw.rect(surf, (80,90,105), (x-20, y-35, 40, 38))
    pygame.draw.rect(surf, (60,70,85), (x-10, y-50, 20, 20))
    pygame.draw.rect(surf, (40,40,40), (x-40, y-10, 5, -25))
    pygame.draw.rect(surf, (40,40,40), (x+35, y-10, 5, -25))
    pygame.draw.ellipse(surf, (80,140,200), (x-65, y+20, 130, 10))

def draw_fighter_jet(surf, x, y, team, flip=False):
    color = TEAM_COLORS[team]
    # Fuselage
    if flip:
        pts = [(x+60,y),(x-20,y-8),(x-60,y),(x-20,y+8)]
    else:
        pts = [(x-60,y),(x+20,y-8),(x+60,y),(x+20,y+8)]
    pygame.draw.polygon(surf, (150,155,165), pts)
    # Wings
    wing_dir = -1 if flip else 1
    pygame.draw.polygon(surf, color, [(x,y),(x,y-3),(x+wing_dir*25,y-20),(x+wing_dir*10,y)])
    pygame.draw.polygon(surf, color, [(x,y),(x,y+3),(x+wing_dir*25,y+20),(x+wing_dir*10,y)])
    # Tail
    pygame.draw.polygon(surf, (130,135,145), [(x-wing_dir*50,y),(x-wing_dir*50,y-4),(x-wing_dir*35,y-14),(x-wing_dir*35,y)])
    # Cockpit
    pygame.draw.ellipse(surf, (100,200,255,180), (x-10*wing_dir+wing_dir*30, y-8, 20, 16))
    # Engine glow
    glow_x = x - wing_dir*55
    pygame.draw.circle(surf, ORANGE, (int(glow_x), int(y)), 7)
    pygame.draw.circle(surf, YELLOW, (int(glow_x), int(y)), 4)
    # Missiles under wings
    pygame.draw.rect(surf, (80,80,80), (x+wing_dir*15, y+12, wing_dir*20, 4))
    pygame.draw.rect(surf, (80,80,80), (x+wing_dir*15, y-16, wing_dir*20, 4))

def draw_bomber(surf, x, y, team):
    color = TEAM_COLORS[team]
    # Wide fuselage
    pygame.draw.ellipse(surf, (120,125,135), (x-50, y-10, 100, 20))
    # Broad swept wings
    pygame.draw.polygon(surf, (100,105,115), [(x-50,y),(x,y-5),(x+50,y),(x+30,y+8),(x-30,y+8)])
    pygame.draw.polygon(surf, color, [(x-50,y),(x,y-3),(x+50,y),(x+60,y+25),(x-60,y+25)])
    # Tail
    pygame.draw.polygon(surf, (100,105,115), [(x-50,y),(x-50,y-5),(x-30,y-20),(x-30,y)])
    # Cockpit
    pygame.draw.ellipse(surf, (80,180,240), (x+20, y-8, 30, 16))
    # Bomb bay
    for bx in range(-20, 25, 15):
        pygame.draw.ellipse(surf, (60,60,70), (x+bx-4, y+8, 8, 12))
    # Engine pods
    for ex in [-25, 5]:
        pygame.draw.ellipse(surf, (80,85,95), (x+ex, y+6, 20, 10))
        pygame.draw.circle(surf, ORANGE, (x+ex, y+11), 5)

def draw_drone(surf, x, y, team):
    color = TEAM_COLORS[team]
    # Body
    pygame.draw.ellipse(surf, (80,85,95), (x-18,y-6,36,12))
    # Wings X shape
    pygame.draw.line(surf, color, (x-25,y-10),(x+25,y+10), 6)
    pygame.draw.line(surf, color, (x-25,y+10),(x+25,y-10), 6)
    # Rotors
    for rx,ry in [(x-22,y-8),(x+22,y-8),(x-22,y+8),(x+22,y+8)]:
        pygame.draw.circle(surf, (40,40,40), (rx,ry), 10, 2)
        pygame.draw.ellipse(surf, (200,200,200,150), (rx-12,ry-3,24,6))
    # Camera
    pygame.draw.circle(surf, (20,20,20), (x,y+5), 5)
    pygame.draw.circle(surf, LIGHT_BLUE, (x,y+5), 3)
    # Payload
    pygame.draw.rect(surf, (50,50,60), (x-6,y+8,12,8))


# ─── PROJECTILES ─────────────────────────────────────────────
def draw_missile(surf, x, y, angle_deg, team):
    color = TEAM_COLORS[team]
    angle = math.radians(angle_deg)
    length = 28
    dx = math.cos(angle)*length
    dy = -math.sin(angle)*length
    # Trail
    for i in range(1,6):
        t = i/6
        tc = (int(255*(1-t)), int(100*(1-t)), 0)
        pygame.draw.circle(surf, tc, (int(x-dx*t), int(y+dy*t)), int(5*(1-t))+1)
    # Body
    pygame.draw.line(surf, (180,185,200), (int(x),int(y)),(int(x+dx),int(y-dy)),7)
    # Nose
    pygame.draw.circle(surf, RED, (int(x+dx),int(y-dy)), 5)
    # Fins
    fin_perp_x = -math.sin(angle)*6
    fin_perp_y = -math.cos(angle)*6
    pygame.draw.line(surf, color,(int(x),int(y)),(int(x+fin_perp_x),int(y+fin_perp_y)),3)
    pygame.draw.line(surf, color,(int(x),int(y)),(int(x-fin_perp_x),int(y-fin_perp_y)),3)

def draw_bomb_proj(surf, x, y):
    # Teardrop bomb
    pygame.draw.ellipse(surf, (50,50,60), (x-8, y-12, 16, 20))
    pygame.draw.polygon(surf, (50,50,60), [(x-4,y-12),(x+4,y-12),(x,y-20)])
    pygame.draw.circle(surf, YELLOW, (x, y+4), 4)

def draw_rocket_proj(surf, x, y, angle_deg, team):
    color = TEAM_COLORS[team]
    angle = math.radians(angle_deg)
    dx = math.cos(angle)*22
    dy = math.sin(angle)*22
    for i in range(1,5):
        t = i/5
        pygame.draw.circle(surf, (255,int(100*(1-t)),0), (int(x-dx*t),int(y+dy*t)), int(4*(1-t))+1)
    pygame.draw.line(surf, color,(int(x),int(y)),(int(x+dx),int(y-dy)),8)
    pygame.draw.circle(surf, ORANGE, (int(x+dx),int(y-dy)),5)

def draw_torpedo_proj(surf, x, y):
    pygame.draw.ellipse(surf, (60,70,80),(x-16,y-5,32,10))
    pygame.draw.polygon(surf, (80,90,100),[(x-16,y-5),(x-16,y+5),(x-24,y)])
    pygame.draw.circle(surf, YELLOW,(x+14,y),5)


# ─── EXPLOSIONS ──────────────────────────────────────────────
def draw_explosion(surf, x, y, frame, max_frames=30):
    """Multi-layered explosion animation."""
    t = frame / max_frames
    if t > 1: return
    
    # Shockwave ring
    r_shock = int(t * 120)
    alpha = int(255 * (1 - t))
    shock_surf = pygame.Surface((r_shock*2+4, r_shock*2+4), pygame.SRCALPHA)
    pygame.draw.circle(shock_surf, (255,200,100, max(0,alpha//2)), (r_shock+2,r_shock+2), r_shock, 3)
    surf.blit(shock_surf, (x-r_shock-2, y-r_shock-2))
    
    # Core fireball
    r_fire = int(80 * math.sin(t * math.pi))
    fire_col = (255, int(200*(1-t**2)), 0)
    if r_fire > 0:
        pygame.draw.circle(surf, fire_col, (x,y), r_fire)
        pygame.draw.circle(surf, (255,255,200), (x,y), r_fire//2)
    
    # Flying debris
    random.seed(frame * 7)
    for _ in range(12):
        angle = random.uniform(0, 2*math.pi)
        dist = random.uniform(20, 90) * t
        dx = math.cos(angle)*dist
        dy = math.sin(angle)*dist
        size = random.randint(2,7)
        dcolor = random.choice([(200,80,20),(80,80,80),(255,150,0),(40,40,40)])
        pygame.draw.circle(surf, dcolor, (int(x+dx),int(y+dy)), size)
    
    # Smoke puffs
    for i in range(5):
        angle = random.uniform(0, 2*math.pi)
        dist = random.uniform(40, 100) * t
        sr = int(15 + dist*0.3)
        sx = x + math.cos(angle)*dist
        sy = y + math.sin(angle)*dist - t*60
        smoke_col = (int(150+50*(1-t)),)*3
        pygame.draw.circle(surf, smoke_col, (int(sx),int(sy)), sr)

def draw_smoke_trail(surf, points):
    for i, (px,py) in enumerate(points):
        t = i/max(len(points),1)
        r = int(3+t*8)
        alpha = int(120*(1-t))
        s = pygame.Surface((r*2,r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (180,180,180,alpha),(r,r),r)
        surf.blit(s,(px-r,py-r))


# ─── UI ELEMENTS ─────────────────────────────────────────────
def draw_flag(surf, x, y, team, w=40, h=25):
    colors = TEAM_FLAGS[team]
    if team == TEAM_US:
        # Red and white stripes
        stripe_h = h // 7
        for i in range(7):
            c = RED if i % 2 == 0 else WHITE
            pygame.draw.rect(surf, c, (x, y + i*stripe_h, w, stripe_h))
        # Blue canton
        pygame.draw.rect(surf, BLUE, (x, y, w//2, h//2))
        # Stars (simplified)
        for sy in range(3):
            for sx in range(4):
                pygame.draw.circle(surf, WHITE, (x+4+sx*5, y+4+sy*5), 1)
    elif team == TEAM_IL:
        pygame.draw.rect(surf, WHITE, (x,y,w,h))
        pygame.draw.rect(surf, BLUE, (x, y+3, w, 5))
        pygame.draw.rect(surf, BLUE, (x, y+h-8, w, 5))
        # Star of David
        cx,cy = x+w//2, y+h//2
        pygame.draw.polygon(surf, BLUE, [(cx,cy-7),(cx+6,cy+3),(cx-6,cy+3)])
        pygame.draw.polygon(surf, BLUE, [(cx,cy+7),(cx+6,cy-3),(cx-6,cy-3)])
    else:  # Iran
        stripe_h = h // 3
        pygame.draw.rect(surf, GREEN, (x, y, w, stripe_h))
        pygame.draw.rect(surf, WHITE, (x, y+stripe_h, w, stripe_h))
        pygame.draw.rect(surf, RED, (x, y+stripe_h*2, w, stripe_h))
        # Sword emblem
        cx,cy = x+w//2, y+h//2
        pygame.draw.line(surf, RED, (cx,cy-8),(cx,cy+8),2)
        pygame.draw.ellipse(surf, RED, (cx-4,cy-3,8,6),1)

def draw_slingshot(surf, x, y):
    """Draw a slingshot / launch frame."""
    # Posts
    pygame.draw.line(surf, (80,50,20),(x,y),(x-25,y-70),10)
    pygame.draw.line(surf, (80,50,20),(x,y),(x+25,y-70),10)
    # Fork tips
    pygame.draw.circle(surf, (60,35,10),(x-25,y-70),8)
    pygame.draw.circle(surf, (60,35,10),(x+25,y-70),8)
    # Rubber bands when not stretched
    pygame.draw.line(surf, (40,20,5),(x-25,y-70),(x,y-55),3)
    pygame.draw.line(surf, (40,20,5),(x+25,y-70),(x,y-55),3)

def draw_power_arc(surf, sx, sy, vx, vy):
    """Draw the trajectory prediction arc."""
    grav = GRAVITY
    px, py = sx, sy
    pvx, pvy = vx, vy
    for _ in range(60):
        pvy += grav
        px += pvx
        py += pvy
        if py > SCREEN_H: break
        if _ % 4 == 0:
            alpha = max(0, 200 - _*3)
            pygame.draw.circle(surf, (255,255,100,alpha), (int(px),int(py)), 3)

def draw_health_bar(surf, x, y, hp, max_hp, w=60, h=8, label=""):
    pct = max(0, hp/max_hp)
    bar_col = GREEN if pct > 0.5 else YELLOW if pct > 0.25 else RED
    pygame.draw.rect(surf, (40,40,40),(x-2,y-2,w+4,h+4))
    pygame.draw.rect(surf, bar_col,(x,y,int(w*pct),h))
    pygame.draw.rect(surf, WHITE,(x,y,w,h),1)

def draw_hud(surf, font_sm, font_med, team_a, team_b, score_a, score_b,
             hp_a, hp_b, curr_turn, level_name, weapon_name, round_num):
    W, H = surf.get_size()
    # Top bar BG
    hud = pygame.Surface((W, 70), pygame.SRCALPHA)
    hud.fill((0,0,0,180))
    surf.blit(hud,(0,0))

    # Team A info
    draw_flag(surf, 12, 10, team_a, 48, 30)
    name_a = LEADER_NAMES[team_a]
    t = font_med.render(name_a, True, WHITE)
    surf.blit(t,(70,10))
    draw_health_bar(surf,70,35,hp_a,100,120,12)
    t = font_sm.render(f"Score: {score_a}", True, YELLOW)
    surf.blit(t,(70,52))

    # Team B info
    draw_flag(surf, W-60, 10, team_b, 48, 30)
    name_b = LEADER_NAMES[team_b]
    t = font_med.render(name_b, True, WHITE)
    surf.blit(t,(W-70-t.get_width(),10))
    draw_health_bar(surf,W-195,35,hp_b,100,120,12)
    t = font_sm.render(f"Score: {score_b}", True, YELLOW)
    surf.blit(t,(W-70-t.get_width(),52))

    # Center
    ln = font_med.render(level_name, True, GOLD)
    surf.blit(ln,(W//2-ln.get_width()//2,8))
    rn = font_sm.render(f"Round {round_num}  |  {weapon_name}", True, LIGHT_BLUE)
    surf.blit(rn,(W//2-rn.get_width()//2,34))
    turn = font_med.render(f"{'YOUR' if curr_turn==team_a else 'ENEMY'} TURN", True,
                           GREEN if curr_turn==team_a else RED)
    surf.blit(turn,(W//2-turn.get_width()//2,52))
