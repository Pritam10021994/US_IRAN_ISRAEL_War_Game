"""
Procedural sound engine.
Generates all game sounds via numpy + pygame without any audio files.
Falls back silently if numpy unavailable.
"""
import pygame
import math
import random

_sounds = {}

def _make_wave(samples, rate=44100):
    """Convert float array to pygame Sound."""
    try:
        import numpy as np
        arr = np.array(samples, dtype=np.float32)
        arr = np.clip(arr, -1.0, 1.0)
        arr_16 = (arr * 32767).astype(np.int16)
        stereo = np.column_stack([arr_16, arr_16])
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        return None

def _sine(freq, dur, rate=44100, vol=0.5, fade_out=True):
    n = int(dur * rate)
    samples = []
    for i in range(n):
        t = i / rate
        val = vol * math.sin(2 * math.pi * freq * t)
        if fade_out:
            val *= max(0, 1 - i/n)
        samples.append(val)
    return samples

def _noise(dur, rate=44100, vol=0.3):
    n = int(dur * rate)
    return [vol * (random.random()*2-1) * max(0,1-i/n) for i in range(n)]

def _explosion_wave(dur=0.8, rate=44100):
    n = int(dur * rate)
    s = []
    for i in range(n):
        t = i/n
        # Low boom + noise
        boom = 0.6 * math.sin(2*math.pi*60*t*(1-t)) * (1-t)**0.5
        noise = 0.4 * (random.random()*2-1) * (1-t)**2
        s.append(boom + noise)
    return s

def _missile_wave(dur=0.4, rate=44100):
    n = int(dur*rate)
    s = []
    for i in range(n):
        t = i/n
        freq = 400 + 300*t
        val = 0.3 * math.sin(2*math.pi*freq*t) + 0.2*(random.random()*2-1)
        val *= (1-t*0.3)
        s.append(val)
    return s

def _launch_wave(dur=0.5, rate=44100):
    n = int(dur*rate)
    s = []
    for i in range(n):
        t = i/n
        freq = 200 + 500*t
        val = 0.4 * math.sin(2*math.pi*freq*t) * (1-t*0.5)
        s.append(val)
    return s

def _victory_wave(dur=1.2, rate=44100):
    notes = [523, 659, 784, 1047]  # C E G C
    n = int(dur*rate)
    note_len = n // len(notes)
    s = []
    for ni, freq in enumerate(notes):
        for i in range(note_len):
            t = i / note_len
            val = 0.4 * math.sin(2*math.pi*freq*(i/rate)) * (1-t*0.5)
            s.append(val)
    return s

def _menu_music(dur=3.0, rate=44100):
    """Simple marching tune."""
    melody = [392,392,392,330,392,523,392,330,262,262,262,330,392,523]
    n = int(dur*rate)
    beat = n // len(melody)
    s = []
    for freq in melody:
        for i in range(beat):
            t = i/beat
            val = 0.15 * math.sin(2*math.pi*freq*(i/rate)) * (0.9 if t < 0.7 else 1-t*2)
            # Drum beat at start of each note
            if i < 800:
                val += 0.1 * (random.random()*2-1) * (1-i/800)
            s.append(val)
    return s

def init_sounds():
    """Initialize all sounds. Returns True if audio works."""
    if not pygame.mixer.get_init():
        return False
    try:
        _sounds['explosion'] = _make_wave(_explosion_wave())
        _sounds['missile']   = _make_wave(_missile_wave())
        _sounds['launch']    = _make_wave(_launch_wave())
        _sounds['victory']   = _make_wave(_victory_wave())
        _sounds['menu']      = _make_wave(_menu_music())
        _sounds['hit']       = _make_wave(_noise(0.3, vol=0.5))
        return True
    except Exception:
        return False

def play(name, loops=0):
    snd = _sounds.get(name)
    if snd:
        try:
            snd.play(loops=loops)
        except Exception:
            pass

def stop(name):
    snd = _sounds.get(name)
    if snd:
        try:
            snd.stop()
        except Exception:
            pass
