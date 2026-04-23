"""Constants and game configuration."""
import pygame

# Screen
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
GRAVITY = 0.35

# Colors
SKY_TOP    = (10,  20,  60)
SKY_MID    = (30,  60, 130)
SKY_BOT    = (180, 120, 60)
SUN_COLOR  = (255, 230, 80)
GROUND_TOP = (80, 140, 50)
GROUND_MID = (60, 110, 35)
GROUND_BOT = (40,  80, 20)
SAND       = (210, 180, 100)
WATER      = (30, 100, 200)
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
RED        = (220,  40,  40)
ORANGE     = (255, 140,   0)
YELLOW     = (255, 220,   0)
GOLD       = (255, 200,   0)
BLUE       = (30,  80, 200)
GREEN      = (50, 180,  50)
GRAY       = (130, 130, 130)
DARK_GRAY  = (60,  60,  60)
BROWN      = (120,  70,  30)
LIGHT_BLUE = (100, 180, 255)
PINK       = (255, 180, 180)
PURPLE     = (140,  60, 200)
SMOKE_COL  = (180, 180, 180, 120)

# Teams
TEAM_US    = "usa"
TEAM_IL    = "israel"
TEAM_IR    = "iran"

TEAM_COLORS = {
    TEAM_US: (60, 100, 200),
    TEAM_IL: (30, 100, 220),
    TEAM_IR: (0, 140, 60),
}

TEAM_FLAGS = {
    TEAM_US: (RED, WHITE, BLUE),
    TEAM_IL: (WHITE, BLUE, BLUE),
    TEAM_IR: (GREEN, WHITE, RED),
}

LEADER_NAMES = {
    TEAM_US: "Donald Trump",
    TEAM_IL: "Netanyahu",
    TEAM_IR: "Khamenei",
}

# Weapon types
W_MISSILE  = "missile"
W_TANK     = "tank_shell"
W_DRONE    = "drone"
W_BOMB     = "bomb"
W_ROCKET   = "rocket"
W_TORPEDO  = "torpedo"

WEAPON_DATA = {
    W_MISSILE:  {"name": "Cruise Missile", "damage": 80,  "blast": 90,  "speed": 8,   "icon": "🚀"},
    W_TANK:     {"name": "Tank Shell",     "damage": 60,  "blast": 70,  "speed": 12,  "icon": "💣"},
    W_DRONE:    {"name": "Armed Drone",    "damage": 50,  "blast": 60,  "speed": 5,   "icon": "🛸"},
    W_BOMB:     {"name": "Air Bomb",       "damage": 100, "blast": 120, "speed": 6,   "icon": "💥"},
    W_ROCKET:   {"name": "Rocket",         "damage": 70,  "blast": 80,  "speed": 10,  "icon": "🔥"},
    W_TORPEDO:  {"name": "Torpedo",        "damage": 90,  "blast": 100, "speed": 7,   "icon": "⚡"},
}

# Levels
LEVELS = [
    {
        "name":    "Persian Gulf Standoff",
        "bg":      "gulf",
        "team_a":  TEAM_US,
        "team_b":  TEAM_IR,
        "desc":    "US vs Iran — Control the Gulf!",
    },
    {
        "name":    "Desert Storm",
        "bg":      "desert",
        "team_a":  TEAM_IL,
        "team_b":  TEAM_IR,
        "desc":    "Israel vs Iran — Middle East showdown!",
    },
    {
        "name":    "Final Reckoning",
        "bg":      "city",
        "team_a":  TEAM_US,
        "team_b":  TEAM_IL,
        "desc":    "Allied Nations — Joint Strike Mission!",
    },
]

# Physics zones
SLING_X    = 200
SLING_Y    = 480
MAX_POWER  = 22
ANGLE_MIN  = -80
ANGLE_MAX  = 80
