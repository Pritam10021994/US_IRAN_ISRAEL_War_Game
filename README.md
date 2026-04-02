# ⚔️ War of Pride & Honor ⚔️

**An Angry-Birds style artillery war game featuring Donald Trump, Netanyahu & Khamenei**

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install pygame numpy

# 2. Run the game
python main.py
```

---

## 🎮 How to Play

### Controls
| Action | Control |
|--------|---------|
| Aim | Click & hold near the slingshot, drag to aim |
| Fire | Release mouse button |
| Switch weapon | Keys **1–6** or **Mouse Wheel** |
| Restart level | **R** |
| Back to menu | **ESC** |
| Next level | **N** |

### Objective
- **Destroy all enemy structures** to win the round
- Pull further back = more power
- Angle determines trajectory
- Enemy AI takes turns firing back!

---

## 🗺️ Levels

| Level | Setting | Match |
|-------|---------|-------|
| 1 | Persian Gulf (Dusk) | 🇺🇸 USA vs 🇮🇷 Iran |
| 2 | Desert Storm | 🇮🇱 Israel vs 🇮🇷 Iran |
| 3 | City at Night | 🇺🇸 USA vs 🇮🇱 Israel |

---

## ⚔️ Weapons

| # | Weapon | Damage | Blast Radius |
|---|--------|--------|-------------|
| 1 | 🚀 Cruise Missile | 80 | 90 |
| 2 | 💣 Tank Shell | 60 | 70 |
| 3 | 🛸 Armed Drone | 50 | 60 (guided!) |
| 4 | 💥 Air Bomb | 100 | 120 |
| 5 | 🔥 Rocket | 70 | 80 |
| 6 | ⚡ Torpedo | 90 | 100 |

> **Tip:** The Drone (🛸) is **guided** — it homes in on the nearest target!

---

## 🏗️ Architecture

```
war_of_pride_honor/
├── main.py          # Entry point
├── game.py          # Main game class, screens, game loop
├── physics.py       # Projectiles, targets, AI, particles
├── art.py           # All procedural drawing (no image files needed)
├── sounds_engine.py # Procedural audio generation
├── constants.py     # Game configuration
└── requirements.txt
```

All graphics are **procedurally generated** — no external assets needed!
Sounds are **synthesized** via numpy waveforms.

---

## 🖥️ System Requirements

- Python 3.8+
- pygame 2.1+
- numpy 1.21+ (for audio synthesis; game still works without it)
- 1280×720 screen or larger (resizable window)

---

## 🎯 Tips & Strategy

1. **Aim low** for targets on the ground platform
2. **High arc** (45°+) for targets hidden behind structures  
3. **Drone** auto-tracks enemies — great when you can't aim precisely
4. **Air Bomb** has the biggest blast — great for cluster targets
5. **Enemy AI** gets smarter in later levels — move fast!

---

*Built entirely in Python with Pygame — all graphics & sounds procedurally generated*
"# US_IRAN_ISRAEL_War_Game" 
