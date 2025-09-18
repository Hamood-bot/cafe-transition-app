import os
import time
import math
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageSequence
import pygame
import calendar
from datetime import datetime
from tkinter import font as tkfont
import random
import json

# ---------------- Configuration ----------------
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
OUTSIDE_GIF = os.path.join(ASSETS_DIR, 'outside.gif')
INSIDE_GIF  = os.path.join(ASSETS_DIR, 'original.gif')
FOCUSED_GIF = os.path.join(ASSETS_DIR, 'focused.gif')  # scene shown after selecting Focused mood
FIREPLACE_GIF = os.path.join(ASSETS_DIR, 'fireplace.gif')  # cozy fireplace scene
COFFEE_GIF = os.path.join(ASSETS_DIR, 'coffee.gif')  # cozy coffee brewing scene
BELL_SOUND  = os.path.join(ASSETS_DIR, 'bell.wav')  # notification bell sound
RING_SOUND = os.path.join(ASSETS_DIR, 'ring.mp3')  # coffee completion sound
COFFEE_SOUND = os.path.join(ASSETS_DIR, 'coffee.mp3')  # coffee brewing sound
LEAF_IMAGE  = os.path.join(ASSETS_DIR, 'leaf.png')  # user-supplied leaf sprite (prefer small like 16x16 or 24x24)
RAIN_SOUND  = os.path.join(ASSETS_DIR, 'rain.wav')  # soft looping ambience (optional)
FIREPLACE_SOUND = os.path.join(ASSETS_DIR, 'fire.mp3')  # cozy fireplace crackling (optional)
HOVER_SOUND = os.path.join(ASSETS_DIR, 'hover.mp3') # menu hover blip (optional)
TYPING_SOUND = os.path.join(ASSETS_DIR, 'typing.mp3')  # short subtle key tap (optional)
PAGEFLIP_SOUND = os.path.join(ASSETS_DIR, 'pageflip.mp3')  # page flip sound for notebook
MUSIC_DEFAULT = os.path.join(ASSETS_DIR, 'music.mp3')  # default background music (looped)
MUSIC_VOLUME = 0.35
TORN_SOUND = os.path.join(ASSETS_DIR, 'tear.wav')      # optional paper tear sfx

# ------------- Display / Scaling Configuration -------------
# SCALE_MODE:
#   'fixed'  -> always use FIXED_SCALE
#   'auto'   -> pick the largest integer scale that fits within MAX_DISPLAY_* bounds
#   'none'   -> no enlargement (scale = 1)
SCALE_MODE = 'auto'
FIXED_SCALE = 4
MAX_DISPLAY_WIDTH = 800
MAX_DISPLAY_HEIGHT = 600
# RESIZE/FRAME FIT MODE:
#   'letterbox' -> preserve aspect, pad with bars (old behavior)
#   'fill'      -> cover: scale up preserving aspect then center-crop to base size (no bars)
#   'stretch'   -> simple resize to target size (can distort)
RESIZE_MODE = 'fill'

FPS_LIMIT = 120
CROSSFADE_FRAMES = 30  # Duration of fade transition (frames)
TEAR_DURATION_FRAMES = 50  # frames for torn page transition
USE_TORN_TRANSITION = False
TEAR_EDGE_SEGMENTS = 18    # how many horizontal jitter points across width
TEAR_WOBBLE_Y = 24         # vertical random wobble amplitude of edge
TEAR_DEBRIS_COUNT = 22     # small paper debris particles spawned along edge
TEAR_BG_SHADE = (245,242,233,255)  # paper color for revealed edge fringe
TEAR_FRINGE_THICKNESS = 14 # thickness of fringe highlight mask
LOOP = True

# Door hotspot (x1, y1, x2, y2) in original GIF pixel coordinates - enlarged for easier clicking
DOOR_HITBOX = (20, 20, 120, 120)  # Much larger door hitbox from left to right
CLICK_ANYWHERE_OUTSIDE = True  # If True, any click while outside starts transition
SHOW_DOOR_DEBUG = False        # If True, draws red door hotspot rectangle
SHOW_FOCUSED_DEBUG = False     # If True, draws book/calendar hitboxes in focused scene
SHOW_COORDS = True             # If True, displays logical cursor coordinates top-left
CURSOR_MODE = 'leaf'           # 'leaf' or 'crosshair' for precision aiming
USE_LEAF_CURSOR = True         # Enable custom leaf cursor instead of system pointer
LEAF_SCALE = 1                 # Optional extra scale on the leaf image (logical before canvas scale)
LEAF_OFFSET = (-12, -12)       # Pixel offset (logical) to adjust anchor (e.g., (-8,-8) to center)
LEAF_LOCK_TO_SCREEN = True     # If True, leaf cursor will NOT be multiplied by scene scale (stays system-cursor sized)
LEAF_TARGET_SCREEN_SIZE = None # e.g., (24,24) to force size in screen pixels when locked; None to keep source size
LEAF_AUTO_SHRINK = True        # If True and no explicit target size, very large leaf images are downscaled automatically
LEAF_AUTO_MAX = 48             # Maximum width/height (screen px) after auto shrink when locked
ENABLE_RAIN_AMBIENCE = True    # Loop rain ambience if rain.wav present
RAIN_VOLUME = 0.08            # 0.0 - 1.0
# Notebook configuration (bigger, pixel aesthetic)
NOTEBOOK_WIDTH = 640
NOTEBOOK_HEIGHT = 480
PIXEL_FONT_CANDIDATES = [
    "Press Start 2P",  # common retro Google font (if installed)
    "Pixel Operator",
    "Perfect DOS VGA 437",
    "Terminal",
    "Fixedsys",
    "Courier New"  # fallback
]
PIXEL_FONT_SIZE = 12
PIXEL_FONT_HEADER_SIZE = 14


# Mood menu configuration
ENABLE_MOOD_MENU = True
MOOD_MENU_TITLE = "What are you feeling today?"  # displayed title
MOOD_MENU_ITEMS = [
    ("Cozy", "warm & calm"),
    ("Focused", "sharp mindset"),

    ("Creative", "let it flow")
]

# Cozy submenu configuration
COZY_SUBMENU_ITEMS = [
    ("Meditate", "find inner peace"),
    ("Phone", "tea timer challenge"),
    ("Fireplace", "cozy crackling sounds"),
    ("Coffee", "brew & sip")
]

# Focused submenu configuration
FOCUSED_SUBMENU_ITEMS = [
    ("Study Zone", "focus & concentrate"),
    ("To-Do List", "organize your tasks")
]

# Creative submenu configuration  
CREATIVE_SUBMENU_ITEMS = [
    ("Edit Code", "open source code editor"),
    ("Mood Menu", "return to main menu")
]

# Phone game configuration
PHONE_IMAGE = os.path.join(ASSETS_DIR, 'phone.png')
PHONE_GAME_WIDTH = 160   # Game area width (matches phone screen width exactly)
PHONE_GAME_HEIGHT = 265  # Game area height (extended to better fill phone screen)
PHONE_GAME_SCALE = 1.0   # Overall game scale multiplier
PHONE_GAME_OFFSET_X = 20 # Horizontal offset from phone left edge (aligned with screen)
PHONE_GAME_OFFSET_Y = 37 # Vertical offset from phone top edge (centered with taller game area)

# Tea Timer Challenge configuration
TEA_TIMER_DURATION = 5.0  # Timer duration in seconds
TEA_PERFECT_START = 0.3   # Perfect zone starts at 30% of timer
TEA_PERFECT_END = 0.5     # Perfect zone ends at 50% of timer

# Ping pong game settings
PONG_BALL_SIZE = 3       # Ball size
PONG_PADDLE_WIDTH = 6    # Paddle width
PONG_PADDLE_HEIGHT = 25  # Paddle height
PONG_PADDLE_SPEED = 4    # Paddle movement speed (increased from 2 for faster movement)
PONG_BALL_SPEED = 2      # Ball movement speed

# Meditation timer configuration
MEDITATION_DURATION = 60  # 1 minute in seconds
BREATHING_CYCLE_DURATION = 8  # 4 seconds inhale + 4 seconds exhale
MEDITATION_BG_COLOR = "#1a1a2e"
MEDITATION_TEXT_COLOR = "#eee2dc"
MEDITATION_ACCENT_COLOR = "#f4a261"

# Coffee scene configuration
COFFEE_BG_COLOR = "#3e2723"  # Rich coffee brown
COFFEE_TEXT_COLOR = "#d7ccc8"  # Light coffee cream
COFFEE_ACCENT_COLOR = "#8d6e63"  # Medium coffee brown
COFFEE_STEAM_COLOR = "#ffffff"  # White steam
COFFEE_BEAN_COLOR = "#5d4037"  # Dark coffee bean
COFFEE_CUP_COLOR = "#f5f5dc"  # Beige cup color

MOOD_MENU_WIDTH = 300       # widened panel to avoid text overflow with bigger icons
MOOD_MENU_ITEM_HEIGHT = 32  # taller rows for more separation
MOOD_MENU_PADDING = 10
MOOD_MENU_TITLE_HEIGHT = 28
MOOD_MENU_DESC_OFFSET = 14  # adjust for new taller rows
MOOD_MENU_BG = "#0b0b0f"
MOOD_MENU_BORDER = "#d0cbb8"
MOOD_MENU_HOVER_BG = "#2e2a23"
MOOD_MENU_TEXT_COLOR = "#d8d0c0"
MOOD_MENU_HOVER_TEXT = "#fff9e6"
MOOD_MENU_ACCENT = "#c29552"  # left bar accent
MOOD_MENU_ANIM_SPEED = 0.12   # slide-in speed (fraction per frame)
MOOD_MENU_FONT = ("Courier New", 12, "bold")
MOOD_MENU_DESC_FONT = ("Courier New", 9, "normal")
MOOD_BADGE_FONT = ("Courier New", 10, "bold")
USE_BLOCKY_FONT = True  # enable custom blocky font rendering for menu/badge later
HOVER_VOLUME = 0.35        # hover sound volume

# Icon configuration for mood menu
MOOD_ICON_SIZE = 24          # logical pixels (will be scaled by scene scale) - enlarged
MOOD_ICON_TEXT_GAP = 6       # gap between icon and text
MOOD_ICON_DRAW_SCALE = 1.3   # extra scale factor applied only when rendering (visual boost)
MOOD_MENU_ICON_MAP = {       # map item label -> icon filename in assets (optional)
    "Cozy": "icon_cozy.png",
    "Focused": "icon_focused.png",
    "Melancholic": "icon_melancholic.png",
    "Creative": "icon_creative.png",
}

# Focused scene interactive element hitboxes (logical GIF coordinates)
# Placeholder values; user will provide final positions.
BOOK_HITBOX = (492, 680, 532, 720)       # approx centered on (512,700) size 40x40
CALENDAR_HITBOX = (1050, 130, 1090, 170) # approx centered on (1070,150) size 40x40

# Enlarged interactive hitboxes (recomputed centrally) – override originals for better accessibility
def _expand_centered(box, new_size):
    """Utility for internal constant computation: expand a (x1,y1,x2,y2) box to new_size x new_size keeping center."""
    x1,y1,x2,y2 = box
    cx = (x1 + x2)//2
    cy = (y1 + y2)//2
    half = new_size//2
    return (cx-half, cy-half, cx+half, cy+half)

def _expand_rightward(box, new_size, right_bias=1.5):
    """Expand hitbox with extra extension to the right for easier clicking."""
    x1,y1,x2,y2 = box
    cx = (x1 + x2)//2
    cy = (y1 + y2)//2
    half = new_size//2
    
    # Calculate left and right extensions with bias toward right
    left_extend = int(half / right_bias)
    right_extend = new_size - left_extend
    
    return (cx-left_extend, cy-half, cx+right_extend, cy+half)

def _expand_horizontal(box, width, height):
    """Expand hitbox horizontally (left to right) with specified width and height."""
    x1,y1,x2,y2 = box
    cx = (x1 + x2)//2
    cy = (y1 + y2)//2
    half_width = width//2
    half_height = height//2
    
    return (cx-half_width, cy-half_height, cx+half_width, cy+half_height)

ENLARGED_INTERACTIVE_SIZE = 300  # logical pixels (square) - made even bigger for easier clicking
HORIZONTAL_WIDTH = 400  # Even wider horizontal coverage
HORIZONTAL_HEIGHT = 150  # Reasonable height coverage
BOOK_HORIZONTAL_WIDTH = 600  # Extra wide horizontal coverage specifically for book
BOOK_HORIZONTAL_HEIGHT = 200  # Taller coverage for book area
BOOK_HITBOX = _expand_horizontal(BOOK_HITBOX, BOOK_HORIZONTAL_WIDTH, BOOK_HORIZONTAL_HEIGHT)
CALENDAR_HITBOX = _expand_horizontal(CALENDAR_HITBOX, HORIZONTAL_WIDTH, HORIZONTAL_HEIGHT)

# Hover highlight styling
FOCUSED_HOVER_OUTLINE = '#ffd27f'
FOCUSED_HOVER_OUTLINE_WIDTH = 3

# Typing sound throttle (seconds)
TYPING_SOUND_COOLDOWN = 0.5

# Blocky font configuration
BLOCKY_FONT_SIZE = 8  # base size for blocky characters
BLOCKY_FONT_SCALE = 1  # additional scale multiplier
BLOCKY_FONT_SPACING = 1  # extra spacing between characters

# Notebook persistence
NOTEBOOK_SAVE_FILE = os.path.join(ASSETS_DIR, 'notebook_data.json')

# iPod configuration
IPOD_WIDTH = 200
IPOD_HEIGHT = 280
IPOD_BG_COLOR = "#f0f0f0"
IPOD_SCREEN_COLOR = "#000000"
IPOD_TEXT_COLOR = "#ffffff"
IPOD_ACCENT_COLOR = "#0080ff"

# ------------------------------------------------

class AnimatedGif:
    def __init__(self, path: str):
        self.path = path
        self.frames = []  # list of (PIL.Image, duration_ms)
        self.width = 0
        self.height = 0
        self.total_duration = 0
        self.valid = False
        self._load()

    def _load(self):
        if not os.path.isfile(self.path):
            return
        try:
            im = Image.open(self.path)
            self.width, self.height = im.size
            for frame in ImageSequence.Iterator(im):
                duration = frame.info.get('duration', 100)  # default 100ms
                self.frames.append((frame.convert('RGBA'), duration))
                self.total_duration += duration
            if not self.frames:
                # fallback single frame
                self.frames.append((im.convert('RGBA'), 100))
                self.total_duration = 100
            self.valid = True
        except Exception as e:
            print(f"[ERR] Failed to load GIF {self.path}: {e}")

    def get_frame(self, elapsed_ms: int):
        if not self.frames:
            return None
        if LOOP:
            elapsed_ms = elapsed_ms % self.total_duration
        acc = 0
        for img, dur in self.frames:
            acc += dur
            if elapsed_ms < acc:
                return img
        return self.frames[-1][0]

class SceneManager:
    STATE_OUTSIDE = 'outside'
    STATE_FADING  = 'fading'
    STATE_INSIDE  = 'inside'
    STATE_FADING_TO_FOCUSED = 'fading_to_focused'
    STATE_FADING_TO_FIREPLACE = 'fading_to_fireplace'
    STATE_FADING_FROM_FIREPLACE = 'fading_from_fireplace'
    STATE_FADING_TO_COFFEE = 'fading_to_coffee'
    STATE_FADING_FROM_COFFEE = 'fading_from_coffee'
    STATE_FOCUSED = 'focused'
    STATE_TEARING = 'tearing'
    STATE_FIREPLACE = 'fireplace'
    STATE_COFFEE = 'coffee'

    def __init__(self, app):
        self.app = app
        self.state = self.STATE_OUTSIDE
        self.start_time = time.time()
        self.fade_counter = 0
        self.fade_done_callback = None

    def update(self, dt):
        if self.state == self.STATE_FADING:
            self.fade_counter += 1
            if self.fade_counter >= CROSSFADE_FRAMES:
                self.state = self.STATE_INSIDE
        elif self.state == self.STATE_FADING_TO_FOCUSED:
            self.fade_counter += 1
            if self.fade_counter >= CROSSFADE_FRAMES:
                self.state = self.STATE_FOCUSED
        elif self.state == self.STATE_FADING_TO_FIREPLACE:
            self.fade_counter += 1
            if self.fade_counter >= CROSSFADE_FRAMES:
                self.state = self.STATE_FIREPLACE
        elif self.state == self.STATE_FADING_FROM_FIREPLACE:
            self.fade_counter += 1
            if self.fade_counter >= CROSSFADE_FRAMES:
                self.state = self.STATE_INSIDE
        elif self.state == self.STATE_FADING_TO_COFFEE:
            self.fade_counter += 1
            if self.fade_counter >= CROSSFADE_FRAMES:
                self.state = self.STATE_COFFEE
        elif self.state == self.STATE_FADING_FROM_COFFEE:
            self.fade_counter += 1
            if self.fade_counter >= CROSSFADE_FRAMES:
                self.state = self.STATE_INSIDE
        elif self.state == self.STATE_TEARING:
            self.fade_counter += 1
            if self.fade_counter >= TEAR_DURATION_FRAMES:
                # finish tearing -> focused
                self.state = self.STATE_FOCUSED

    def trigger_fade(self):
        if self.state == self.STATE_OUTSIDE:
            self.state = self.STATE_FADING
            self.fade_counter = 0
            self.app.play_bell()

    def trigger_fade_to_focused(self):
        # Allow triggering from INSIDE only (ignore if already fading or focused)
        if self.state not in (self.STATE_INSIDE,):
            print(f"[DEBUG] trigger_fade_to_focused ignored; state={self.state}")
            return
        print('[DEBUG] trigger_fade_to_focused start')
        if USE_TORN_TRANSITION:
            self.state = self.STATE_TEARING
            self.fade_counter = 0
            self.app.start_torn_transition()
        else:
            self.state = self.STATE_FADING_TO_FOCUSED
            self.fade_counter = 0

    def trigger_fade_to_fireplace(self):
        # Allow triggering from INSIDE only (ignore if already fading or in fireplace)
        if self.state not in (self.STATE_INSIDE,):
            print(f"[DEBUG] trigger_fade_to_fireplace ignored; state={self.state}")
            return
        print('[DEBUG] trigger_fade_to_fireplace start')
        self.state = self.STATE_FADING_TO_FIREPLACE
        self.fade_counter = 0
    
    def trigger_fade_from_fireplace(self):
        # Allow triggering from FIREPLACE only
        if self.state not in (self.STATE_FIREPLACE,):
            print(f"[DEBUG] trigger_fade_from_fireplace ignored; state={self.state}")
            return
        print('[DEBUG] trigger_fade_from_fireplace start')
        self.state = self.STATE_FADING_FROM_FIREPLACE
        self.fade_counter = 0

    def trigger_fade_to_coffee(self):
        # Allow triggering from INSIDE only (ignore if already fading or in coffee scene)
        if self.state not in (self.STATE_INSIDE,):
            print(f"[DEBUG] trigger_fade_to_coffee ignored; state={self.state}")
            return
        print('[DEBUG] trigger_fade_to_coffee start')
        self.state = self.STATE_FADING_TO_COFFEE
        self.fade_counter = 0
    
    def trigger_fade_from_coffee(self):
        # Allow triggering from COFFEE only
        if self.state not in (self.STATE_COFFEE,):
            print(f"[DEBUG] trigger_fade_from_coffee ignored; state={self.state}")
            return
        print('[DEBUG] trigger_fade_from_coffee start')
        self.state = self.STATE_FADING_FROM_COFFEE
        self.fade_counter = 0

class TeaTimerGame:
    """Tea Timer Challenge - hit the key at the perfect moment for ideal tea"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.wins = 0  # Track consecutive wins for difficulty scaling
        self.reset_game()
        
    def reset_game(self):
        """Reset the tea timer game to initial state"""
        self.timer_elapsed = 0.0
        # Base timer gets faster with wins - much more aggressive
        base_time = max(1.5, TEA_TIMER_DURATION - (self.wins * 0.4))
        self.timer_total = base_time
        self.game_state = "running"  # "running", "success", "weak", "bitter", "waiting"
        self.result_message = ""
        self.result_timer = 0.0
        
        # Perfect zone gets much smaller with wins - down to 1% at high levels
        zone_size = max(0.01, 0.2 - (self.wins * 0.025))  # Starts at 20%, shrinks by 2.5% per win, min 1%
        zone_center = 0.4  # Keep zone centered at 40%
        self.perfect_zone_start = zone_center - zone_size/2
        self.perfect_zone_end = zone_center + zone_size/2
        
    def update(self, dt):
        """Update the tea timer game state"""
        if self.game_state == "running":
            self.timer_elapsed += dt
            
            # Check if timer has run out (bitter tea)
            if self.timer_elapsed >= self.timer_total:
                self.game_state = "bitter"
                self.result_message = "Too Late! Bitter Tea"
                self.result_timer = 2.0
                self.wins = 0  # Reset win streak on failure
                
        elif self.game_state in ["success", "weak", "bitter"]:
            self.result_timer -= dt
            if self.result_timer <= 0:
                self.game_state = "waiting"
                self.result_timer = 1.0
                
        elif self.game_state == "waiting":
            self.result_timer -= dt
            if self.result_timer <= 0:
                self.reset_game()
    
    def handle_key_press(self):
        """Handle player key press during tea timing"""
        if self.game_state != "running":
            return
            
        progress = self.timer_elapsed / self.timer_total
        
        if progress < self.perfect_zone_start:
            # Too early - sweet tea
            self.game_state = "weak"
            self.result_message = "Too Early! Tea Too Sweet"
            self.result_timer = 2.0
            self.wins = 0  # Reset win streak on failure
        elif progress <= self.perfect_zone_end:
            # Perfect timing - ideal tea
            self.game_state = "success"
            self.wins += 1
            difficulty_msg = f" (Win #{self.wins})" if self.wins > 1 else ""
            self.result_message = f"Perfect! Ideal Tea{difficulty_msg}"
            self.result_timer = 2.0
        else:
            # Too late but not completely - strong tea
            self.game_state = "bitter"
            self.result_message = "Too Late! Bitter Tea"
            self.result_timer = 2.0
            self.wins = 0  # Reset win streak on failure
    
    def get_timer_progress(self):
        """Get current timer progress (0.0 to 1.0)"""
        return min(self.timer_elapsed / self.timer_total, 1.0)
    
    def is_in_perfect_zone(self):
        """Check if current progress is in perfect zone"""
        progress = self.get_timer_progress()
        return self.perfect_zone_start <= progress <= self.perfect_zone_end
    
    def get_difficulty_info(self):
        """Get current difficulty information"""
        zone_size = (self.perfect_zone_end - self.perfect_zone_start) * 100
        return f"Speed: {self.timer_total:.1f}s | Zone: {zone_size:.0f}% | Wins: {self.wins}"

class PingPongGame:
    def __init__(self, width=120, height=200, ball_speed=2, paddle_speed=3):
        self.width = width
        self.height = height
        self.ball_speed = ball_speed
        self.paddle_speed = paddle_speed
        self.reset_game()
        
    def reset_game(self):
        # Ball
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx = self.ball_speed
        self.ball_dy = self.ball_speed
        self.ball_size = PONG_BALL_SIZE
        
        # Paddles
        self.paddle_width = PONG_PADDLE_WIDTH
        self.paddle_height = PONG_PADDLE_HEIGHT
        
        # Player paddle (left)
        self.player_y = self.height // 2 - self.paddle_height // 2
        
        # AI paddle (right)
        self.ai_y = self.height // 2 - self.paddle_height // 2
        
        # Score
        self.player_score = 0
        self.ai_score = 0
        
    def update(self):
        # Move ball
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Ball collision with top/bottom
        if self.ball_y <= 0 or self.ball_y >= self.height - self.ball_size:
            self.ball_dy = -self.ball_dy
            
        # Ball collision with paddles
        # Player paddle
        if (self.ball_x <= self.paddle_width and 
            self.player_y <= self.ball_y <= self.player_y + self.paddle_height):
            self.ball_dx = abs(self.ball_dx)
            
        # AI paddle
        if (self.ball_x >= self.width - self.paddle_width - self.ball_size and
            self.ai_y <= self.ball_y <= self.ai_y + self.paddle_height):
            self.ball_dx = -abs(self.ball_dx)
            
        # Scoring
        if self.ball_x < 0:
            self.ai_score += 1
            self.reset_ball()
        elif self.ball_x > self.width:
            self.player_score += 1
            self.reset_ball()
            
        # Simple AI
        ai_center = self.ai_y + self.paddle_height // 2
        if ai_center < self.ball_y - 10:
            self.ai_y += self.paddle_speed
        elif ai_center > self.ball_y + 10:
            self.ai_y -= self.paddle_speed
            
        # Keep AI paddle in bounds
        self.ai_y = max(0, min(self.height - self.paddle_height, self.ai_y))
        
    def reset_ball(self):
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx = self.ball_speed if self.ball_dx > 0 else -self.ball_speed
        self.ball_dy = self.ball_speed if self.ball_dy > 0 else -self.ball_speed
        
    def move_player_up(self):
        self.player_y = max(0, self.player_y - self.paddle_speed)
        
    def move_player_down(self):
        self.player_y = min(self.height - self.paddle_height, self.player_y + self.paddle_speed)

class MeditationTimer:
    def __init__(self):
        self.duration = MEDITATION_DURATION
        self.time_remaining = self.duration
        self.breathing_phase = "inhale"  # "inhale" or "exhale"
        self.breathing_timer = 0
        self.is_active = False
        self.breathing_cycle_time = BREATHING_CYCLE_DURATION / 2  # 4 seconds each phase
        
    def start(self):
        self.is_active = True
        self.time_remaining = self.duration
        self.breathing_timer = 0
        self.breathing_phase = "inhale"
        
    def stop(self):
        self.is_active = False
        
    def update(self, dt):
        if not self.is_active:
            return
            
        # Update main timer
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.is_active = False
            return
            
        # Update breathing cycle
        self.breathing_timer += dt
        if self.breathing_timer >= self.breathing_cycle_time:
            self.breathing_timer = 0
            self.breathing_phase = "exhale" if self.breathing_phase == "inhale" else "inhale"
            
    def get_time_display(self):
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        return f"{minutes:02d}:{seconds:02d}"
        
    def get_breathing_instruction(self):
        if self.breathing_phase == "inhale":
            return "Breathe In..."
        else:
            return "Breathe Out..."
            
    def get_breathing_progress(self):
        # Returns 0.0 to 1.0 for visual breathing circle
        return self.breathing_timer / self.breathing_cycle_time

class CafeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Cafe Transition Prototype")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.resizable(False, False)  # Prevent maximizing and resizing
        # Determine pixel-font to use once (lazy selection)
        self.pixel_font_family = self._choose_pixel_font()

        # Load assets
        self.outside = AnimatedGif(OUTSIDE_GIF)
        self.inside  = AnimatedGif(INSIDE_GIF)
        self.focused_scene = AnimatedGif(FOCUSED_GIF)
        self.fireplace = AnimatedGif(FIREPLACE_GIF)
        self.coffee = AnimatedGif(COFFEE_GIF)
        # Fallback: if specified INSIDE_GIF path didn't load but a generic 'inside.gif' exists, use it
        alt_inside_path = os.path.join(ASSETS_DIR, 'inside.gif')
        if not self.inside.valid and os.path.isfile(alt_inside_path):
            print('[INFO] Falling back to inside.gif (configured INSIDE_GIF missing or invalid)')
            self.inside = AnimatedGif(alt_inside_path)
        # Determine logical (base) size: use max so both GIFs fit without cropping
        base_w_candidates = [w for w in (self.outside.width, self.inside.width) if w]
        base_h_candidates = [h for h in (self.outside.height, self.inside.height) if h]
        self.width = max(base_w_candidates) if base_w_candidates else 128
        self.height = max(base_h_candidates) if base_h_candidates else 96

        self.scale = self.compute_scale()

        self.canvas = tk.Canvas(root, width=self.width*self.scale, height=self.height*self.scale, bg="#000", highlightthickness=0)
        self.canvas.pack()

        # Custom cursor state
        self.leaf_img_original = None
        self.leaf_img_scaled = None
        self.cursor_x = 0
        self.cursor_y = 0
        self.current_logical_xy = (0, 0)
        if USE_LEAF_CURSOR:
            self.load_leaf_cursor()
            # Hide system cursor over canvas
            try:
                self.canvas.configure(cursor="none")
            except Exception:
                pass

        # Pygame mixer for bell
        self.rain_channel = None
        self.fireplace_channel = None
        self.coffee_channel = None
        self.bell_loaded = False
        self.rain_loaded = False
        self.fireplace_loaded = False
        self.coffee_loaded = False
        self.fireplace_playing = False
        self.music_channel = None
        self.music_loaded = False
        self.current_music_path = None
        self.cozy_music_button = None
        # Torn transition data
        self.tear_points = []  # list of (x,y) across width
        self.tear_debris = []  # list of particles {x,y,vx,vy,life}
        self.tear_cached_mask = None
        try:
            pygame.mixer.init()
            if os.path.isfile(BELL_SOUND):
                self.bell_loaded = True
            if ENABLE_RAIN_AMBIENCE and os.path.isfile(RAIN_SOUND):
                try:
                    self.rain_sound = pygame.mixer.Sound(RAIN_SOUND)
                    self.rain_sound.set_volume(RAIN_VOLUME)
                    # Play on its own channel looping (-1)
                    self.rain_channel = self.rain_sound.play(loops=-1)
                    self.rain_loaded = True
                except Exception as re:
                    print("[WARN] Could not play rain ambience:", re)
            
            # Load fireplace sound but don't play it yet
            if os.path.isfile(FIREPLACE_SOUND):
                try:
                    self.fireplace_sound = pygame.mixer.Sound(FIREPLACE_SOUND)
                    self.fireplace_sound.set_volume(0.95)  # Moderate volume for fireplace
                    self.fireplace_loaded = True
                except Exception as fe:
                    print("[WARN] Could not load fireplace sound:", fe)
            
            # Load coffee brewing sound but don't play it yet
            if os.path.isfile(COFFEE_SOUND):
                try:
                    self.coffee_sound = pygame.mixer.Sound(COFFEE_SOUND)
                    self.coffee_sound.set_volume(1.0)  # Maximum volume for coffee brewing
                    self.coffee_loaded = True
                except Exception as ce:
                    print("[WARN] Could not load coffee sound:", ce)
        except Exception as e:
            print("[WARN] Pygame mixer init failed:", e)

        self.scene = SceneManager(self)
        self.last_time = time.time()
        self.elapsed_outside_ms = 0
        self.elapsed_inside_ms = 0
        self.elapsed_focused_ms = 0
        self._frame_refs = []  # keep references to PhotoImage

        # Mood menu state
        self.menu_active = False
        self.menu_boxes = []  # list of (item_index, (x1,y1,x2,y2)) in logical coords
        self.menu_hover_index = -1
        self.menu_selected_index = -1
        self.menu_anim_progress = 0.0  # 0 -> 1 slide in
        
        # Cozy submenu state
        self.cozy_submenu_active = False
        self.cozy_submenu_boxes = []
        self.cozy_submenu_hover_index = -1
        self.cozy_submenu_selected = ""
        
        # Focused submenu state
        self.focused_submenu_active = False
        self.focused_submenu_boxes = []
        self.focused_submenu_hover_index = -1
        self.focused_submenu_selected = ""
        
        # Creative submenu state
        self.creative_submenu_active = False
        self.creative_submenu_boxes = []
        self.creative_submenu_hover_index = -1
        self.creative_submenu_selected = ""
        
        # Phone game state
        self.phone_game_active = False
        self.phone_image = None
        self.tea_timer_game = None
        
        # Key state tracking for smooth phone game controls
        self.keys_pressed = set()
        
        # Meditation state
        self.meditation_active = False
        self.meditation_timer = None
        
        # Coffee scene state
        self.coffee_scene_active = False
        self.coffee_brewing = False
        self.coffee_brew_timer = 0
        self.coffee_channel = None
        self.coffee_reading_visible = True  # Show reading initially, hide after click
        self.current_coffee_reading = ""  # Store the current coffee reading
        
        # To-do list state
        self.todo_list_active = False
        self.todo_items = []
        self.todo_selected_index = 0
        
        # Calendar events state
        self.calendar_events = {}  # Format: {"YYYY-MM-DD": [{"title": "Event", "time": "10:00", "description": ""}]}
        self.load_calendar_events()
        
        self.hover_sound_loaded = False
        self.typing_sound_loaded = False
        self.last_typing_sound_time = 0.0
        # Mood icons (logical sized PIL images, converted on draw via _to_menu_icon_photo)
        self.mood_icons = {}  # label -> PIL.Image (RGBA) resized to MOOD_ICON_SIZE
        if ENABLE_MOOD_MENU and os.path.isfile(HOVER_SOUND):
            try:
                self.hover_sound = pygame.mixer.Sound(HOVER_SOUND)
                self.hover_sound.set_volume(HOVER_VOLUME)
                self.hover_sound_loaded = True
            except Exception as e:
                print("[WARN] Could not load hover sound:", e)
        # Load typing sound if present
        if os.path.isfile(TYPING_SOUND):
            try:
                self.typing_sound = pygame.mixer.Sound(TYPING_SOUND)
                self.typing_sound.set_volume(0.8)
                self.typing_sound_loaded = True
            except Exception as e:
                print('[WARN] Could not load typing sound:', e)
        # Load page flip sound if present
        self.pageflip_sound_loaded = False
        if os.path.isfile(PAGEFLIP_SOUND):
            try:
                self.pageflip_sound = pygame.mixer.Sound(PAGEFLIP_SOUND)
                self.pageflip_sound.set_volume(0.7)
                self.pageflip_sound_loaded = True
            except Exception as e:
                print('[WARN] Could not load page flip sound:', e)
        # load music default
        if os.path.isfile(MUSIC_DEFAULT):
            try:
                self.background_music = pygame.mixer.Sound(MUSIC_DEFAULT)
                self.background_music.set_volume(MUSIC_VOLUME)
                self.music_channel = self.background_music.play(loops=-1)
                self.music_loaded = True
                self.current_music_path = MUSIC_DEFAULT
            except Exception as e:
                print('[WARN] Could not play default music:', e)
        # tear sound
        self.tear_sound = None
        if os.path.isfile(TORN_SOUND):
            try:
                self.tear_sound = pygame.mixer.Sound(TORN_SOUND)
                self.tear_sound.set_volume(0.6)
            except Exception:
                self.tear_sound = None

        if ENABLE_MOOD_MENU:
            self.load_mood_icons()
            
        # Load phone image if present
        if os.path.isfile(PHONE_IMAGE):
            try:
                self.phone_image = Image.open(PHONE_IMAGE).convert('RGBA')
            except Exception as e:
                print(f"[WARN] Could not load phone image: {e}")

        self.canvas.bind("<Button-1>", self.on_click)
        if USE_LEAF_CURSOR:
            self.canvas.bind("<Motion>", self.on_mouse_move)
        # Key bindings for menu navigation
        self.root.bind('<Up>', self.on_key)
        self.root.bind('<Down>', self.on_key)
        self.root.bind('<Return>', self.on_key)
        self.root.bind('<Escape>', self.on_key)
        # Add W/S bindings for to-do list navigation
        self.root.bind('<w>', self.on_key)
        self.root.bind('<s>', self.on_key)
        
        # Key press/release tracking for smooth movement
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        self.root.focus_set()  # Enable key events
        
        self.loop()

    def on_click(self, event):
        # If cozy submenu active, handle submenu clicks
        if self.cozy_submenu_active:
            lx = event.x // self.scale
            ly = event.y // self.scale
            for idx, (x1,y1,x2,y2) in self.cozy_submenu_boxes:
                if x1 <= lx <= x2 and y1 <= ly <= y2:
                    label, _ = COZY_SUBMENU_ITEMS[idx]
                    self.cozy_submenu_selected = label
                    self.cozy_submenu_active = False
                    
                    if label == "Phone":
                        self.start_phone_game()
                    elif label == "Meditate":
                        self.start_meditation()
                    elif label == "Fireplace":
                        self.toggle_fireplace()
                    elif label == "Coffee":
                        self.start_coffee_scene()
                    return
                    
        # If creative submenu active, handle submenu clicks
        if self.creative_submenu_active:
            lx = event.x // self.scale
            ly = event.y // self.scale
            for idx, (x1,y1,x2,y2) in self.creative_submenu_boxes:
                if x1 <= lx <= x2 and y1 <= ly <= y2:
                    label, _ = CREATIVE_SUBMENU_ITEMS[idx]
                    self.creative_submenu_selected = label
                    self.creative_submenu_active = False
                    
                    if label == "Edit Code":
                        self.open_code_editor()
                    elif label == "Notebook":
                        self.open_note_window()
                    elif label == "Mood Menu":
                        self.menu_active = True
                    return
                    
        # If focused submenu active, handle submenu clicks  
        if self.focused_submenu_active:
            lx = event.x // self.scale
            ly = event.y // self.scale
            for idx, (x1,y1,x2,y2) in self.focused_submenu_boxes:
                if x1 <= lx <= x2 and y1 <= ly <= y2:
                    label, _ = FOCUSED_SUBMENU_ITEMS[idx]
                    self.focused_submenu_selected = label
                    self.focused_submenu_active = False
                    
                    if label == "Study Zone":
                        self.scene.trigger_fade_to_focused()  # Go to focused scene for study zone
                    elif label == "To-Do List":
                        self.start_todo_list()  # New to-do list function
                    return
        
        # If todo list active, handle button clicks
        if self.todo_list_active and hasattr(self, 'todo_button_boxes'):
            lx = event.x // self.scale
            ly = event.y // self.scale
            for idx, (x1,y1,x2,y2) in enumerate(self.todo_button_boxes):
                if x1 <= lx <= x2 and y1 <= ly <= y2:
                    button_names = ["Add New", "Edit", "Delete", "Toggle"]
                    button_name = button_names[idx]
                    
                    if button_name == "Add New":
                        if not self.todo_editing:
                            self.todo_input_mode = True
                            self.todo_input_text = ""
                    elif button_name == "Edit":
                        if not self.todo_input_mode and self.todo_items and self.todo_selected_index < len(self.todo_items):
                            self.todo_editing = True
                            self.todo_edit_text = self.todo_items[self.todo_selected_index]['text']
                    elif button_name == "Delete":
                        if not self.todo_editing and not self.todo_input_mode and self.todo_items and self.todo_selected_index < len(self.todo_items):
                            del self.todo_items[self.todo_selected_index]
                            if self.todo_selected_index >= len(self.todo_items) and self.todo_items:
                                self.todo_selected_index = len(self.todo_items) - 1
                            elif not self.todo_items:
                                self.todo_selected_index = 0
                            self.save_todo_items()
                    elif button_name == "Toggle":
                        if not self.todo_editing and not self.todo_input_mode and self.todo_items and self.todo_selected_index < len(self.todo_items):
                            current = self.todo_items[self.todo_selected_index]
                            current['completed'] = not current.get('completed', False)
                            self.save_todo_items()
                    return
                    
        # If menu active, interpret click as selection attempt
        if self.menu_active:
            lx = event.x // self.scale
            ly = event.y // self.scale
            for idx, (x1,y1,x2,y2) in self.menu_boxes:
                if x1 <= lx <= x2 and y1 <= ly <= y2:
                    self.menu_selected_index = idx
                    # For now simply close menu after selection
                    self.menu_active = False
                    # If Cozy mood chosen, show submenu; if Focused, start transition
                    label, _ = MOOD_MENU_ITEMS[idx]
                    if label == 'Cozy':
                        print('[DEBUG] Cozy selected - showing submenu')
                        self.activate_cozy_submenu()
                    elif label == 'Creative':
                        print('[DEBUG] Creative selected - showing submenu')
                        self.activate_creative_submenu()
                    elif label == 'Focused':
                        print('[DEBUG] Focused selected - showing submenu')
                        self.activate_focused_submenu()
                    return
              
        # Focused scene interactive clicks
        if self.scene.state == SceneManager.STATE_FOCUSED:
            lx = event.x // self.scale
            ly = event.y // self.scale
            if self._point_in_box(lx, ly, BOOK_HITBOX):
                self.open_note_window()
                return
            if self._point_in_box(lx, ly, CALENDAR_HITBOX):
                self.open_calendar_window()
                return
                
        # Coffee scene interactive clicks
        if self.scene.state == SceneManager.STATE_COFFEE:
            # Click anywhere to hide the coffee reading
            self.coffee_reading_visible = False
            return
            
        # Cozy music change button click
        if self.cozy_music_button and self.scene.state == SceneManager.STATE_INSIDE:
            # Music button works regardless of mood selection
            bx1, by1, bx2, by2 = self.cozy_music_button
            if bx1 <= event.x <= bx2 and by1 <= event.y <= by2:
                self.pick_new_music()
                return
        if self.scene.state == SceneManager.STATE_OUTSIDE:
            if CLICK_ANYWHERE_OUTSIDE:
                self.scene.trigger_fade()
                return
            # Fallback to hitbox logic if flag disabled
            lx = event.x // self.scale
            ly = event.y // self.scale
            x1, y1, x2, y2 = DOOR_HITBOX
            if x1 <= lx <= x2 and y1 <= ly <= y2:
                self.scene.trigger_fade()

    def play_bell(self):
        if self.bell_loaded:
            try:
                pygame.mixer.Sound(BELL_SOUND).play()
            except Exception as e:
                print("[WARN] Bell play failed:", e)

    def play_ring(self):
        try:
            pygame.mixer.Sound(RING_SOUND).play()
        except Exception as e:
            print("[WARN] Ring play failed:", e)

    def loop(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        self.scene.update(dt)
        self.update_animation_time(dt)
        
        # Update phone game if active
        if self.phone_game_active and self.tea_timer_game:
            # Update tea timer game
            self.tea_timer_game.update(dt)
            
        # Update meditation timer if active
        if self.meditation_active and self.meditation_timer:
            self.meditation_timer.update(dt)
            if not self.meditation_timer.is_active:
                # Timer finished
                self.meditation_active = False
                
        # Update coffee brewing timer if brewing
        if self.coffee_brewing:
            self.coffee_brew_timer += dt
            print(f"[DEBUG] Coffee brewing: {self.coffee_brew_timer:.1f}/5.0 seconds")
            # Coffee finishes brewing after 5 seconds
            if self.coffee_brew_timer >= 5.0:
                print("[DEBUG] Coffee brewing finished!")
                self.coffee_brewing = False
                # Stop coffee sound
                if self.coffee_channel:
                    self.coffee_channel.stop()
                    self.coffee_channel = None
                # Play ring and transition to coffee scene
                self.play_ring()
                self.coffee_scene_active = True
                self.coffee_reading_visible = True  # Reset reading visibility for new session
                self.current_coffee_reading = self.get_random_coffee_reading()  # Generate new reading
                self.scene.trigger_fade_to_coffee()
                
        self.draw()

        # Aim for FPS limit
        delay = int(1000 / FPS_LIMIT)
        self.root.after(delay, self.loop)

    def update_animation_time(self, dt):
        # Advance elapsed times (ms)
        self.elapsed_outside_ms += int(dt * 1000)
        self.elapsed_inside_ms += int(dt * 1000)
        self.elapsed_focused_ms += int(dt * 1000)

    def draw(self):
        if hasattr(self.scene, 'state'):
            if self.scene.state in (SceneManager.STATE_FADING_TO_FOCUSED, SceneManager.STATE_FADING, SceneManager.STATE_TEARING):
                print(f"[DEBUG] draw state={self.scene.state} fade_counter={self.scene.fade_counter}")
        self.canvas.delete("all")
        self._frame_refs.clear()

        # Determine frames for each scene state
        frame_out = None
        frame_in = None
        frame_focus = None
        frame_fireplace = None
        frame_coffee = None
        if self.scene.state in (SceneManager.STATE_OUTSIDE, SceneManager.STATE_FADING):
            frame_out = self.outside.get_frame(self.elapsed_outside_ms) if self.outside.valid else self.placeholder_frame("OUTSIDE")
        if self.scene.state in (SceneManager.STATE_INSIDE, SceneManager.STATE_FADING, SceneManager.STATE_FADING_TO_FOCUSED, SceneManager.STATE_FADING_TO_FIREPLACE, SceneManager.STATE_FADING_FROM_FIREPLACE, SceneManager.STATE_FADING_TO_COFFEE, SceneManager.STATE_FADING_FROM_COFFEE):
            frame_in = self.inside.get_frame(self.elapsed_inside_ms) if self.inside.valid else None
        if self.scene.state in (SceneManager.STATE_FOCUSED, SceneManager.STATE_FADING_TO_FOCUSED):
            frame_focus = self.focused_scene.get_frame(self.elapsed_focused_ms) if self.focused_scene.valid else None
        if self.scene.state in (SceneManager.STATE_FIREPLACE, SceneManager.STATE_FADING_TO_FIREPLACE, SceneManager.STATE_FADING_FROM_FIREPLACE):
            frame_fireplace = self.fireplace.get_frame(self.elapsed_inside_ms) if self.fireplace.valid else None
        if self.scene.state in (SceneManager.STATE_COFFEE, SceneManager.STATE_FADING_TO_COFFEE, SceneManager.STATE_FADING_FROM_COFFEE):
            frame_coffee = self.coffee.get_frame(self.elapsed_inside_ms) if self.coffee.valid else self.placeholder_frame("COFFEE", COFFEE_BG_COLOR)

        if frame_out is not None:
            frame_out = self._standardize_frame(frame_out)
        if frame_in is not None:
            frame_in = self._standardize_frame(frame_in)
        if frame_focus is not None:
            frame_focus = self._standardize_frame(frame_focus)
        if frame_fireplace is not None:
            frame_fireplace = self._standardize_frame(frame_fireplace)
        if frame_coffee is not None:
            frame_coffee = self._standardize_frame(frame_coffee)

        # Blend logic across transitions
        if self.scene.state == SceneManager.STATE_FADING and frame_out and frame_in:
            alpha = self.scene.fade_counter / max(1, CROSSFADE_FRAMES)
            blended = Image.blend(frame_out, frame_in, alpha)
            disp = self._to_photo(blended)
        elif self.scene.state == SceneManager.STATE_FADING_TO_FOCUSED:
            # Provide fallback placeholder focus frame if missing
            if frame_in is None:
                frame_in = self.placeholder_frame('INSIDE')
            if frame_focus is None:
                frame_focus = self._focused_placeholder_from(frame_in)
            alpha = self.scene.fade_counter / max(1, CROSSFADE_FRAMES)
            blended = Image.blend(frame_in, frame_focus, alpha)
            disp = self._to_photo(blended)
        elif self.scene.state == SceneManager.STATE_FADING_TO_FIREPLACE:
            # Provide fallback placeholder fireplace frame if missing
            if frame_in is None:
                frame_in = self.placeholder_frame('INSIDE')
            if frame_fireplace is None:
                frame_fireplace = self.placeholder_frame('FIREPLACE')
            alpha = self.scene.fade_counter / max(1, CROSSFADE_FRAMES)
            blended = Image.blend(frame_in, frame_fireplace, alpha)
            disp = self._to_photo(blended)
        elif self.scene.state == SceneManager.STATE_FADING_FROM_FIREPLACE:
            # Fade from fireplace back to inside
            if frame_fireplace is None:
                frame_fireplace = self.placeholder_frame('FIREPLACE')
            if frame_in is None:
                frame_in = self.placeholder_frame('INSIDE')
            alpha = self.scene.fade_counter / max(1, CROSSFADE_FRAMES)
            blended = Image.blend(frame_fireplace, frame_in, alpha)
            disp = self._to_photo(blended)
        elif self.scene.state == SceneManager.STATE_FADING_TO_COFFEE:
            # Fade from inside to coffee scene
            if frame_coffee is None:
                frame_coffee = self.placeholder_frame('COFFEE', COFFEE_BG_COLOR)
            if frame_in is None:
                frame_in = self.placeholder_frame('INSIDE')
            alpha = self.scene.fade_counter / max(1, CROSSFADE_FRAMES)
            blended = Image.blend(frame_in, frame_coffee, alpha)
            disp = self._to_photo(blended)
        elif self.scene.state == SceneManager.STATE_FADING_FROM_COFFEE:
            # Fade from coffee scene back to inside
            if frame_coffee is None:
                frame_coffee = self.placeholder_frame('COFFEE', COFFEE_BG_COLOR)
            if frame_in is None:
                frame_in = self.placeholder_frame('INSIDE')
            alpha = self.scene.fade_counter / max(1, CROSSFADE_FRAMES)
            blended = Image.blend(frame_coffee, frame_in, alpha)
            disp = self._to_photo(blended)
        elif self.scene.state == SceneManager.STATE_TEARING:
            # Render tearing effect (with placeholder if needed)
            if frame_in is None:
                frame_in = self.placeholder_frame('INSIDE')
            if frame_focus is None:
                frame_focus = self._focused_placeholder_from(frame_in)
            progress = self.scene.fade_counter / max(1, TEAR_DURATION_FRAMES)
            tear_img = self.render_torn_transition(frame_in, frame_focus, progress)
            disp = self._to_photo(tear_img)
        else:
            # choose highest priority frame by current state
            if self.scene.state == SceneManager.STATE_COFFEE and frame_coffee is not None:
                base = frame_coffee
            elif self.scene.state == SceneManager.STATE_FIREPLACE and frame_fireplace is not None:
                base = frame_fireplace
            elif self.scene.state == SceneManager.STATE_FOCUSED and frame_focus is not None:
                base = frame_focus
            elif self.scene.state in (SceneManager.STATE_INSIDE, SceneManager.STATE_FADING_TO_FOCUSED) and frame_in is not None:
                base = frame_in
            else:
                base = frame_out
            disp = self._to_photo(base)
        self.canvas.create_image(0, 0, anchor="nw", image=disp)
        self._frame_refs.append(disp)

        # Draw coffee scene overlay when in coffee mode
        if self.scene.state == SceneManager.STATE_COFFEE:
            self.draw_coffee_scene()

        # (Optional) debug hotspot (disabled by default)
        if SHOW_DOOR_DEBUG and self.scene.state == SceneManager.STATE_OUTSIDE:
            x1,y1,x2,y2 = DOOR_HITBOX
            self.canvas.create_rectangle(x1*self.scale, y1*self.scale, x2*self.scale, y2*self.scale, outline="#ff0000")

        if not self.outside.valid:
            self.canvas.create_text(10, 10, anchor="nw", fill="#fff", text="Add outside.gif", font=("Courier New", 10, "bold"))
        if not self.inside.valid:
            self.canvas.create_text(10, 26, anchor="nw", fill="#fff", text="Add inside.gif", font=("Courier New", 10, "bold"))
        if self.scene.state in (SceneManager.STATE_FOCUSED, SceneManager.STATE_FADING_TO_FOCUSED, SceneManager.STATE_TEARING) and not self.focused_scene.valid:
            self.canvas.create_text(10, 42, anchor="nw", fill="#fff", text="(focused placeholder)", font=("Courier New", 10, "bold"))

        # Focused debug overlays
        if SHOW_FOCUSED_DEBUG and self.scene.state == SceneManager.STATE_FOCUSED:
            self._draw_hitbox(BOOK_HITBOX, '#00ff00')
            self._draw_hitbox(CALENDAR_HITBOX, '#00bfff')

        # Activate menu first time we are inside
        if ENABLE_MOOD_MENU and self.scene.state == SceneManager.STATE_INSIDE and not self.menu_active and self.menu_selected_index == -1:
            self.activate_mood_menu()

        # Show coffee brewing message when brewing
        if self.coffee_brewing:
            # Animated dots (cycle through 1, 2, 3 dots)
            dot_cycle = int(self.coffee_brew_timer * 2) % 3 + 1
            dots = "." * dot_cycle
            brewing_text = f"Making coffee{dots}"
            
            if USE_BLOCKY_FONT:
                text_width = self._get_blocky_text_width(brewing_text)
                text_x = (self.width - text_width) // 2
                text_y = self.height // 2 - 10
                self._draw_blocky_text(text_x, text_y, brewing_text, "#d7ccc8")
            else:
                px = self.scale
                self.canvas.create_text((self.width//2)*px, (self.height//2)*px,
                                      text=brewing_text, 
                                      fill="#d7ccc8", 
                                      font=("Courier New", 72, "bold"))

        if self.menu_active:
            # advance animation progress
            if self.menu_anim_progress < 1.0:
                self.menu_anim_progress = min(1.0, self.menu_anim_progress + MOOD_MENU_ANIM_SPEED)
            self.draw_mood_menu()
            # Also draw music button when menu is active if a mood was previously selected
            if self.menu_selected_index != -1:
                self.draw_cozy_music_button()
        elif self.cozy_submenu_active:
            self.draw_cozy_submenu()
        elif self.focused_submenu_active:
            self.draw_focused_submenu()
        elif self.creative_submenu_active:
            self.draw_creative_submenu()
        elif self.menu_selected_index != -1:
            self.draw_selection_badge()
            self.draw_cozy_music_button()
            
        # Draw phone game overlay
        if self.phone_game_active:
            self.draw_phone_game()
            
        # Draw meditation overlay
        if self.meditation_active:
            self.draw_meditation()
            
        # Draw to-do list in focused scene
        if self.todo_list_active:
            self.draw_todo_list_overlay()

        # Hover highlight for focused interactive zones
        if self.scene.state == SceneManager.STATE_FOCUSED:
            lx, ly = self.current_logical_xy
            hover_box = None
            if self._point_in_box(lx, ly, BOOK_HITBOX):
                hover_box = BOOK_HITBOX
            elif self._point_in_box(lx, ly, CALENDAR_HITBOX):
                hover_box = CALENDAR_HITBOX
            if hover_box:
                self._draw_focus_hover(hover_box)

        # Draw custom cursor / crosshair last
        if CURSOR_MODE == 'leaf' and USE_LEAF_CURSOR and self.leaf_img_scaled is not None:
            if LEAF_LOCK_TO_SCREEN:
                dx = self.cursor_x
                dy = self.cursor_y
            else:
                dx = (self.cursor_x + LEAF_OFFSET[0]) * self.scale
                dy = (self.cursor_y + LEAF_OFFSET[1]) * self.scale
            if LEAF_LOCK_TO_SCREEN:
                dx += LEAF_OFFSET[0]
                dy += LEAF_OFFSET[1]
            leaf_photo = self.leaf_img_scaled
            self.canvas.create_image(dx, dy, anchor="nw", image=leaf_photo)
            self._frame_refs.append(leaf_photo)
        elif CURSOR_MODE == 'crosshair':
            # precision crosshair in contrasting colors
            cx = self.cursor_x if LEAF_LOCK_TO_SCREEN else (self.cursor_x * self.scale)
            cy = self.cursor_y if LEAF_LOCK_TO_SCREEN else (self.cursor_y * self.scale)
            size = 10
            self.canvas.create_line(cx - size, cy, cx + size, cy, fill="#fffbcc")
            self.canvas.create_line(cx, cy - size, cx, cy + size, fill="#fffbcc")
            self.canvas.create_rectangle(cx-2, cy-2, cx+2, cy+2, outline="#ff2", fill="#ff2")

        # Coordinate overlay
        if SHOW_COORDS:
            lx, ly = self.current_logical_xy
            self.canvas.create_text(4, 4, anchor='nw', text=f"{lx},{ly}", fill='#ffaa44', font=("Courier New", 10, 'bold'))

    # -------- Torn Transition --------
    def start_torn_transition(self):
        # Generate jittered edge points across width
        w, h = self.width, self.height
        self.tear_points = []
        for i in range(TEAR_EDGE_SEGMENTS+1):
            x = int(i * w / TEAR_EDGE_SEGMENTS)
            jitter = random.randint(-TEAR_WOBBLE_Y, TEAR_WOBBLE_Y)
            y = int(h * 0.15 + (h*0.7 * (i/TEAR_EDGE_SEGMENTS))) + jitter
            self.tear_points.append((x, y))
        # Debris
        self.tear_debris = []
        for _ in range(TEAR_DEBRIS_COUNT):
            px = random.randint(0, w)
            py = random.randint(0, h)
            vx = random.uniform(-1.5,1.5)
            vy = random.uniform(-2.5,-0.5)
            life = random.uniform(0.4,1.2)
            self.tear_debris.append({'x':px,'y':py,'vx':vx,'vy':vy,'life':life,'age':0})
        if self.tear_sound:
            try:
                self.tear_sound.play()
            except Exception:
                pass

    def render_torn_transition(self, img_in, img_focus, progress: float):
        # progress 0..1: reveal from top-left to bottom-right masked by tear polygon
        w, h = self.width, self.height
        base_in = img_in.copy()
        reveal = img_focus.copy()
        # Build a vertical split proportion based on progress (simulate paper peel)
        # Determine path along tear points, then offset horizontally
        mask = Image.new('L', (w,h), 0)
        import math
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        # compute dynamic x offset of edge (pulling to right)
        pull = int(progress * w * 0.95)
        # build polygon: edge -> bottom-right corner -> top-right corner
        poly = []
        for (x,y) in self.tear_points:
            poly.append((min(w-1, x + pull), y))
        poly.append((w-1,h-1))
        poly.append((w-1,0))
        draw.polygon(poly, fill=255)
        # composite reveal over base
        comp = Image.composite(reveal, base_in, mask)
        # fringe highlight (paper edge)
        from PIL import ImageFilter
        edge_mask = mask.filter(ImageFilter.BoxBlur(2))
        edge_img = Image.new('RGBA',(w,h),(0,0,0,0))
        edge_draw = ImageDraw.Draw(edge_img)
        # draw jagged edge along points
        scaled = []
        for (x,y) in self.tear_points:
            scaled.append((min(w-1, x + pull), y))
        for i in range(len(scaled)-1):
            x1,y1 = scaled[i]
            x2,y2 = scaled[i+1]
            edge_draw.line((x1,y1,x2,y2), fill=(255,255,255,180), width=2)
        comp.alpha_composite(edge_img)
        return comp

    # -------- Background Music --------
    def pick_new_music(self):
        path = filedialog.askopenfilename(title='Select music file', filetypes=[('Audio','*.mp3 *.wav *.ogg')])
        if not path:
            return
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(MUSIC_VOLUME)
            if self.music_channel:
                self.music_channel.stop()
            self.music_channel = snd.play(loops=-1)
            self.current_music_path = path
        except Exception as e:
            messagebox.showerror('Music Error', f'Could not play file:\n{e}')

    def draw_cozy_music_button(self):
        # Always show the music button when in the inside scene
        if self.scene.state != SceneManager.STATE_INSIDE:
            self.cozy_music_button = None
            return
        
        # Show music button always when inside, regardless of mood selection
        # draw top-right small button
        w = self.width * self.scale
        pad = 6
        bw, bh = 120, 28
        x1 = w - bw - pad
        y1 = pad
        x2 = x1 + bw
        y2 = y1 + bh
        self.canvas.create_rectangle(x1, y1, x2, y2, fill='#22201b', outline='#c29552', width=2)
        self.canvas.create_text((x1+x2)//2, (y1+y2)//2, text='Change Music', fill='#ffd9a3', font=('Courier New', 10, 'bold'))
        self.cozy_music_button = (x1, y1, x2, y2)

    def _to_photo(self, pil_img):
        if pil_img is None:
            pil_img = self.placeholder_frame("MISSING")
        if self.scale != 1:
            pil_img = pil_img.resize((self.width*self.scale, self.height*self.scale), Image.NEAREST)
        return ImageTk.PhotoImage(pil_img)

    def _standardize_frame(self, frame_img: Image.Image) -> Image.Image:
        """Return a frame exactly (self.width, self.height) using RESIZE_MODE."""
        target_w, target_h = self.width, self.height
        if frame_img.size == (target_w, target_h):
            return frame_img
        fw, fh = frame_img.size
        if RESIZE_MODE == 'stretch':
            return frame_img.resize((target_w, target_h), Image.NEAREST)
        if RESIZE_MODE == 'letterbox':
            # scale to fit inside (no crop) then pad
            scale_ratio = min(target_w / fw, target_h / fh)
            new_w = max(1, int(fw * scale_ratio))
            new_h = max(1, int(fh * scale_ratio))
            resized = frame_img.resize((new_w, new_h), Image.NEAREST)
            canvas = Image.new('RGBA', (target_w, target_h), (0,0,0,255))
            ox = (target_w - new_w)//2
            oy = (target_h - new_h)//2
            canvas.paste(resized, (ox, oy))
            return canvas
        # fill (cover): scale to cover entire target then center crop
        scale_ratio = max(target_w / fw, target_h / fh)
        new_w = max(1, int(fw * scale_ratio))
        new_h = max(1, int(fh * scale_ratio))
        resized = frame_img.resize((new_w, new_h), Image.NEAREST)
        # center crop
        left = (new_w - target_w)//2
        top = (new_h - target_h)//2
        right = left + target_w
        bottom = top + target_h
        return resized.crop((left, top, right, bottom))

    def compute_scale(self) -> int:
        if SCALE_MODE == 'none':
            return 1
        if SCALE_MODE == 'fixed':
            return max(1, int(FIXED_SCALE))
        if SCALE_MODE == 'auto':
            # largest integer scale that keeps within max display bounds
            for s in range(8, 0, -1):  # try downwards
                if self.width * s <= MAX_DISPLAY_WIDTH and self.height * s <= MAX_DISPLAY_HEIGHT:
                    return s
            return 1
        # fallback
        return 1

    def placeholder_frame(self, label: str):
        img = Image.new('RGBA', (self.width, self.height), (20,20,20,255))
        return img

    def _focused_placeholder_from(self, base_img: Image.Image):
        """Generate a visually distinct placeholder for focused scene when focused.gif missing."""
        try:
            img = base_img.copy().convert('RGBA')
        except Exception:
            img = self.placeholder_frame('FOCUSED')
        px = img.load()
        w,h = img.size
        for y in range(h):
            for x in range(w):
                r,g,b,a = px[x,y]
                avg = (r+g+b)//3
                # bluish desaturated tint to differentiate
                r = int((avg*0.55) + 8)
                g = int((avg*0.6) + 12)
                b = int((avg*0.9) + 50)
                dx = (x - w/2)/(w/2)
                dy = (y - h/2)/(h/2)
                dist = (dx*dx + dy*dy)**0.5
                if dist > 0.65:
                    fade = min(1.0, (dist-0.65)/0.5)
                    dim = 1 - fade*0.55
                    r = int(r*dim)
                    g = int(g*dim)
                    b = int(b*dim)
                px[x,y] = (r,g,b,a)
        return img

    # -------- Leaf Cursor Helpers --------
    def load_leaf_cursor(self):
        if not os.path.isfile(LEAF_IMAGE):
            return
        try:
            img = Image.open(LEAF_IMAGE).convert('RGBA')
            # optional logical scaling of leaf itself before canvas scaling
            if LEAF_SCALE != 1:
                w, h = img.size
                img = img.resize((max(1,int(w*LEAF_SCALE)), max(1,int(h*LEAF_SCALE))), Image.NEAREST)
            # Auto shrink huge source before storing as original to conserve memory
            if LEAF_LOCK_TO_SCREEN and LEAF_AUTO_SHRINK and LEAF_TARGET_SCREEN_SIZE is None:
                w, h = img.size
                if w > LEAF_AUTO_MAX or h > LEAF_AUTO_MAX:
                    ratio = min(LEAF_AUTO_MAX / w, LEAF_AUTO_MAX / h)
                    new_w = max(1, int(w * ratio))
                    new_h = max(1, int(h * ratio))
                    img = img.resize((new_w, new_h), Image.NEAREST)
            self.leaf_img_original = img
            # create PhotoImage after applying canvas scale so it remains crisp
            self.refresh_leaf_scaled()
        except Exception as e:
            print(f"[WARN] Failed to load leaf cursor image: {e}")

    def refresh_leaf_scaled(self):
        if self.leaf_img_original is None:
            return
        img = self.leaf_img_original
        if LEAF_LOCK_TO_SCREEN:
            # Do not multiply by scene scale; optionally force a target size
            if LEAF_TARGET_SCREEN_SIZE:
                tw, th = LEAF_TARGET_SCREEN_SIZE
                img = img.resize((tw, th), Image.NEAREST)
            elif LEAF_AUTO_SHRINK:
                # secondary guard if original was swapped later
                w, h = img.size
                if w > LEAF_AUTO_MAX or h > LEAF_AUTO_MAX:
                    ratio = min(LEAF_AUTO_MAX / w, LEAF_AUTO_MAX / h)
                    img = img.resize((max(1,int(w*ratio)), max(1,int(h*ratio))), Image.NEAREST)
        else:
            if self.scale != 1:
                w, h = img.size
                img = img.resize((w*self.scale, h*self.scale), Image.NEAREST)
        self.leaf_img_scaled = ImageTk.PhotoImage(img)

    def on_mouse_move(self, event):
        # event.x / event.y are in display (scaled) coords
        if LEAF_LOCK_TO_SCREEN:
            # Keep raw display coordinates for direct placement
            self.cursor_x = event.x
            self.cursor_y = event.y
        else:
            self.cursor_x = event.x // self.scale
            self.cursor_y = event.y // self.scale
        # Always store logical coords for debug overlay
        self.current_logical_xy = (event.x // self.scale, event.y // self.scale)
        
        # Hover detection for cozy submenu
        if self.cozy_submenu_active:
            lx = event.x // self.scale
            ly = event.y // self.scale
            new_hover = -1
            for idx, (x1,y1,x2,y2) in self.cozy_submenu_boxes:
                if x1 <= lx <= x2 and y1 <= ly <= y2:
                    new_hover = idx
                    break
            if new_hover != self.cozy_submenu_hover_index:
                self.cozy_submenu_hover_index = new_hover
                if new_hover != -1 and self.hover_sound_loaded:
                    try:
                        self.hover_sound.play()
                    except Exception:
                        pass
            return
            
        # Hover detection for creative submenu
        if self.creative_submenu_active:
            lx = event.x // self.scale
            ly = event.y // self.scale
            new_hover = -1
            for idx, (x1,y1,x2,y2) in self.creative_submenu_boxes:
                if x1 <= lx <= x2 and y1 <= ly <= y2:
                    new_hover = idx
                    break
            if new_hover != self.creative_submenu_hover_index:
                self.creative_submenu_hover_index = new_hover
                if new_hover != -1 and self.hover_sound_loaded:
                    try:
                        self.hover_sound.play()
                    except Exception:
                        pass
            return
            
        # Hover detection for focused submenu
        if self.focused_submenu_active:
            lx = event.x // self.scale
            ly = event.y // self.scale
            new_hover = -1
            for idx, (x1,y1,x2,y2) in self.focused_submenu_boxes:
                if x1 <= lx <= x2 and y1 <= ly <= y2:
                    new_hover = idx
                    break
            if new_hover != self.focused_submenu_hover_index:
                self.focused_submenu_hover_index = new_hover
                if new_hover != -1 and self.hover_sound_loaded:
                    try:
                        self.hover_sound.play()
                    except Exception:
                        pass
            return
        
        # Hover detection for todo list buttons
        if self.todo_list_active and hasattr(self, 'todo_button_boxes'):
            lx = event.x // self.scale
            ly = event.y // self.scale
            new_hover = -1
            for idx, (x1,y1,x2,y2) in enumerate(self.todo_button_boxes):
                if x1 <= lx <= x2 and y1 <= ly <= y2:
                    new_hover = idx
                    break
            if new_hover != self.todo_button_hover:
                self.todo_button_hover = new_hover
                if new_hover != -1 and self.hover_sound_loaded:
                    try:
                        self.hover_sound.play()
                    except Exception:
                        pass
            return
            
        # Hover detection for menu (use logical coordinates)
        if self.menu_active:
            lx = event.x // self.scale
            ly = event.y // self.scale
            new_hover = -1
            for idx, (x1,y1,x2,y2) in self.menu_boxes:
                if x1 <= lx <= x2 and y1 <= ly <= y2:
                    new_hover = idx
                    break
            if new_hover != self.menu_hover_index:
                self.menu_hover_index = new_hover
                if new_hover != -1 and self.hover_sound_loaded:
                    try:
                        self.hover_sound.play()
                    except Exception:
                        pass

    def on_close(self):
        try:
            if pygame.mixer.get_init():
                # Stop rain if playing
                if self.rain_channel:
                    try:
                        self.rain_channel.stop()
                    except Exception:
                        pass
                pygame.mixer.quit()
        except Exception:
            pass
        self.root.destroy()

    def on_key(self, event):
        # ESC during focus transition, focused state, fireplace transition, fireplace, coffee transition, or coffee - return to inside view and show menu
        if self.scene.state in (SceneManager.STATE_FADING_TO_FOCUSED, SceneManager.STATE_FOCUSED, SceneManager.STATE_TEARING, SceneManager.STATE_FADING_TO_FIREPLACE, SceneManager.STATE_FIREPLACE, SceneManager.STATE_FADING_FROM_FIREPLACE, SceneManager.STATE_FADING_TO_COFFEE, SceneManager.STATE_COFFEE, SceneManager.STATE_FADING_FROM_COFFEE):
            if event.keysym == 'Escape':
                # Handle fireplace exit with transition
                if self.scene.state in (SceneManager.STATE_FADING_TO_FIREPLACE, SceneManager.STATE_FIREPLACE):
                    if self.fireplace_playing:
                        if self.fireplace_channel:
                            self.fireplace_channel.stop()
                            self.fireplace_channel = None
                        self.fireplace_playing = False
                    # Use smooth transition back to inside scene
                    self.scene.trigger_fade_from_fireplace()
                # Handle coffee scene exit with transition
                elif self.scene.state in (SceneManager.STATE_FADING_TO_COFFEE, SceneManager.STATE_COFFEE):
                    self.coffee_scene_active = False
                    # Use smooth transition back to inside scene
                    self.scene.trigger_fade_from_coffee()
                else:
                    # For other states, immediate transition to inside
                    self.scene.state = SceneManager.STATE_INSIDE
                # Reactivate the menu when returning from focus mode, fireplace, or coffee
                self.activate_mood_menu()
                return
        
        # Coffee brewing controls - allow ESC to cancel brewing
        if self.coffee_brewing:
            if event.keysym == 'Escape':
                self.coffee_brewing = False
                if self.coffee_channel:
                    self.coffee_channel.stop()
                    self.coffee_channel = None
                return
        
        # Meditation controls
        if self.meditation_active:
            if event.keysym == 'Escape':
                self.meditation_active = False
                self.meditation_timer = None
                self.cozy_submenu_active = True  # Return to cozy submenu
                return
                
        # Phone game controls - Tea Timer Challenge
        if self.phone_game_active and self.tea_timer_game:
            if event.keysym == 'Escape':
                self.phone_game_active = False
                self.tea_timer_game = None
                self.cozy_submenu_active = True  # Return to cozy submenu
                return
            elif event.keysym == 'Return':
                # Only Enter key triggers tea timing attempt
                self.tea_timer_game.handle_key_press()
                return
                
        # To-do list controls
        if self.todo_list_active:
            if event.keysym == 'Escape':
                if self.todo_editing:
                    # Cancel editing
                    self.todo_editing = False
                    self.todo_edit_text = ""
                elif self.todo_input_mode:
                    # Cancel input mode
                    self.todo_input_mode = False
                    self.todo_input_text = ""
                else:
                    # Exit to-do list
                    self.save_todo_items()
                    self.todo_list_active = False
                    self.focused_submenu_active = True
                return
            elif event.keysym.lower() in ('w', 's'):
                if not self.todo_editing and not self.todo_input_mode and self.todo_items:
                    delta = -1 if event.keysym.lower() == 'w' else 1
                    self.todo_selected_index = (self.todo_selected_index + delta) % len(self.todo_items)
            elif event.keysym == 'space':
                if not self.todo_editing and not self.todo_input_mode and self.todo_items and self.todo_selected_index < len(self.todo_items):
                    # Toggle completion status
                    current = self.todo_items[self.todo_selected_index]
                    current['completed'] = not current.get('completed', False)
                    self.save_todo_items()
            elif event.keysym == 'Return':
                if self.todo_editing:
                    # Save edit
                    if self.todo_edit_text.strip() and self.todo_selected_index < len(self.todo_items):
                        self.todo_items[self.todo_selected_index]['text'] = self.todo_edit_text.strip()
                        self.save_todo_items()
                    self.todo_editing = False
                    self.todo_edit_text = ""
                elif self.todo_input_mode:
                    # Save new task
                    if self.todo_input_text.strip():
                        self.todo_items.append({"text": self.todo_input_text.strip(), "completed": False})
                        self.todo_selected_index = len(self.todo_items) - 1
                        self.save_todo_items()
                    self.todo_input_mode = False
                    self.todo_input_text = ""
                else:
                    # Start input mode for new task
                    self.todo_input_mode = True
                    self.todo_input_text = ""
            elif event.keysym == 'Delete':
                if not self.todo_editing and self.todo_items and self.todo_selected_index < len(self.todo_items):
                    # Remove selected item
                    del self.todo_items[self.todo_selected_index]
                    if self.todo_selected_index >= len(self.todo_items) and self.todo_items:
                        self.todo_selected_index = len(self.todo_items) - 1
                    elif not self.todo_items:
                        self.todo_selected_index = 0
                    self.save_todo_items()
            elif event.keysym == 'e':
                if not self.todo_editing and self.todo_items and self.todo_selected_index < len(self.todo_items):
                    # Start editing selected item
                    self.todo_editing = True
                    self.todo_edit_text = self.todo_items[self.todo_selected_index]['text']
            return
                
        # Cozy submenu navigation
        if self.cozy_submenu_active:
            if event.keysym in ('Up','Down'):
                if self.cozy_submenu_hover_index == -1:
                    self.cozy_submenu_hover_index = 0
                else:
                    delta = -1 if event.keysym == 'Up' else 1
                    total = len(COZY_SUBMENU_ITEMS)
                    self.cozy_submenu_hover_index = (self.cozy_submenu_hover_index + delta) % total
                if self.hover_sound_loaded:
                    try:
                        self.hover_sound.play()
                    except Exception:
                        pass
            elif event.keysym == 'Return':
                if self.cozy_submenu_hover_index != -1:
                    label, _ = COZY_SUBMENU_ITEMS[self.cozy_submenu_hover_index]
                    self.cozy_submenu_selected = label
                    self.cozy_submenu_active = False
                    if label == "Phone":
                        self.start_phone_game()
                    elif label == "Meditate":
                        self.start_meditation()
                    elif label == "Fireplace":
                        self.toggle_fireplace()
                    elif label == "Coffee":
                        self.start_coffee_scene()
                    elif label == "iPod":
                        self.start_ipod()
            elif event.keysym == 'Escape':
                self.cozy_submenu_active = False
                self.menu_active = True  # Go back to main menu
                # Stop fireplace sound when exiting cozy submenu
                if self.fireplace_playing:
                    if self.fireplace_channel:
                        self.fireplace_channel.stop()
                        self.fireplace_channel = None
                    self.fireplace_playing = False
            return
            
        # Creative submenu navigation
        if self.creative_submenu_active:
            if event.keysym in ('Up','Down'):
                if self.creative_submenu_hover_index == -1:
                    self.creative_submenu_hover_index = 0
                else:
                    delta = -1 if event.keysym == 'Up' else 1
                    total = len(CREATIVE_SUBMENU_ITEMS)
                    self.creative_submenu_hover_index = (self.creative_submenu_hover_index + delta) % total
                if self.hover_sound_loaded:
                    try:
                        self.hover_sound.play()
                    except Exception:
                        pass
            elif event.keysym == 'Return':
                if self.creative_submenu_hover_index != -1:
                    label, _ = CREATIVE_SUBMENU_ITEMS[self.creative_submenu_hover_index]
                    self.creative_submenu_selected = label
                    self.creative_submenu_active = False
                    if label == "Edit Code":
                        self.open_code_editor()
                    elif label == "Notebook":
                        self.open_note_window()
                    elif label == "Mood Menu":
                        self.menu_active = True
            elif event.keysym == 'Escape':
                self.creative_submenu_active = False
                self.menu_active = True  # Go back to main menu
            return
            
        # Focused submenu navigation
        if self.focused_submenu_active:
            if event.keysym in ('Up','Down'):
                if self.focused_submenu_hover_index == -1:
                    self.focused_submenu_hover_index = 0
                else:
                    delta = -1 if event.keysym == 'Up' else 1
                    total = len(FOCUSED_SUBMENU_ITEMS)
                    self.focused_submenu_hover_index = (self.focused_submenu_hover_index + delta) % total
                if self.hover_sound_loaded:
                    try:
                        self.hover_sound.play()
                    except Exception:
                        pass
            elif event.keysym == 'Return':
                if self.focused_submenu_hover_index != -1:
                    label, _ = FOCUSED_SUBMENU_ITEMS[self.focused_submenu_hover_index]
                    self.focused_submenu_selected = label
                    self.focused_submenu_active = False
                    if label == "Study Zone":
                        self.scene.trigger_fade_to_focused()  # Go to focused scene for study zone
                    elif label == "To-Do List":
                        self.start_todo_list()  # New to-do list function
            elif event.keysym == 'Escape':
                self.focused_submenu_active = False
                self.menu_active = True  # Go back to main menu
            return
            
        # Main menu navigation
        if not self.menu_active:
            return
        if event.keysym in ('Up','Down'):
            if self.menu_hover_index == -1:
                self.menu_hover_index = 0
            else:
                delta = -1 if event.keysym == 'Up' else 1
                total = len(MOOD_MENU_ITEMS)
                self.menu_hover_index = (self.menu_hover_index + delta) % total
            # sound on move
            if self.hover_sound_loaded:
                try:
                    self.hover_sound.play()
                except Exception:
                    pass
        elif event.keysym == 'Return':
            if self.menu_hover_index != -1:
                self.menu_selected_index = self.menu_hover_index
                self.menu_active = False
                # Handle selection
                try:
                    label, _ = MOOD_MENU_ITEMS[self.menu_selected_index]
                    if label == 'Cozy':
                        print('[DEBUG] Cozy selected - showing submenu')
                        self.activate_cozy_submenu()
                    elif label == 'Creative':
                        print('[DEBUG] Creative selected - showing submenu')
                        self.activate_creative_submenu()
                    elif label == 'Focused':
                        print('[DEBUG] Focused selected - showing submenu')
                        self.activate_focused_submenu()
                except Exception:
                    pass

    def on_key_press(self, event):
        """Handle key press events for continuous movement tracking"""
        self.keys_pressed.add(event.keysym)
        
        # Handle text input for todo editing and input modes
        if self.todo_list_active and (self.todo_editing or self.todo_input_mode):
            if event.keysym == 'BackSpace':
                if self.todo_editing and self.todo_edit_text:
                    self.todo_edit_text = self.todo_edit_text[:-1]
                elif self.todo_input_mode and self.todo_input_text:
                    self.todo_input_text = self.todo_input_text[:-1]
            elif len(event.char) == 1 and event.char.isprintable():
                # Add character to appropriate text
                if self.todo_editing:
                    self.todo_edit_text += event.char
                elif self.todo_input_mode:
                    self.todo_input_text += event.char
    
    def on_key_release(self, event):
        """Handle key release events for continuous movement tracking"""
        self.keys_pressed.discard(event.keysym)

    # -------- Mood Menu Helpers --------
    def activate_mood_menu(self):
        self.menu_active = True
        self.menu_anim_progress = 0.0
        self.build_menu_layout()

    def load_mood_icons(self):
        """Load or create placeholder icons for each mood label."""
        for label, _ in MOOD_MENU_ITEMS:
            filename = MOOD_MENU_ICON_MAP.get(label)
            img = None
            if filename:
                path = os.path.join(ASSETS_DIR, filename)
                if os.path.isfile(path):
                    try:
                        raw = Image.open(path).convert('RGBA')
                        if raw.size != (MOOD_ICON_SIZE, MOOD_ICON_SIZE):
                            raw = raw.resize((MOOD_ICON_SIZE, MOOD_ICON_SIZE), Image.NEAREST)
                        img = raw
                    except Exception as e:
                        print(f"[WARN] Failed loading icon for {label}: {e}")
            if img is None:
                # generate placeholder: colored box with first letter
                from random import Random
                r = Random(label)
                base_color = (r.randint(60,160), r.randint(60,160), r.randint(60,160), 255)
                placeholder = Image.new('RGBA', (MOOD_ICON_SIZE, MOOD_ICON_SIZE), base_color)
                # Draw letter manually (tiny 5x5 pixel font style) using simple blocks
                letter = label[0].upper()
                # crude bitmap mapping for a subset of capital letters (fallback to filled square)
                # We'll just carve a lighter pixel pattern
                lighter = (min(base_color[0]+60,255), min(base_color[1]+60,255), min(base_color[2]+60,255), 255)
                px = placeholder.load()
                # Simple pattern: border lighter + letter diagonal
                for y in range(MOOD_ICON_SIZE):
                    for x in range(MOOD_ICON_SIZE):
                        if x==0 or y==0 or x==MOOD_ICON_SIZE-1 or y==MOOD_ICON_SIZE-1:
                            px[x,y] = lighter
                # Add a diagonal stripe to hint a letter
                for d in range(MOOD_ICON_SIZE):
                    if 0 <= d < MOOD_ICON_SIZE:
                        px[d,d] = lighter
                img = placeholder
            self.mood_icons[label] = img

    def _to_menu_icon_photo(self, label):
        pil_img = self.mood_icons.get(label)
        if pil_img is None:
            return None
        # scale to display
        disp_img = pil_img
        base_px = MOOD_ICON_SIZE
        if MOOD_ICON_DRAW_SCALE != 1.0:
            # upscale logically first (nearest to keep pixels chunky)
            scaled_px = max(1, int(base_px * MOOD_ICON_DRAW_SCALE))
            disp_img = disp_img.resize((scaled_px, scaled_px), Image.NEAREST)
            base_px = scaled_px
        if self.scale != 1:
            disp_img = disp_img.resize((base_px*self.scale, base_px*self.scale), Image.NEAREST)
        return ImageTk.PhotoImage(disp_img)

    def build_menu_layout(self):
        self.menu_boxes.clear()
        panel_w = MOOD_MENU_WIDTH
        total_items = len(MOOD_MENU_ITEMS)
        panel_h = (MOOD_MENU_TITLE_HEIGHT + MOOD_MENU_PADDING +
                   total_items * MOOD_MENU_ITEM_HEIGHT + MOOD_MENU_PADDING)
        # center panel
        x1 = (self.width - panel_w)//2
        y1 = (self.height - panel_h)//2
        # store panel rect for drawing
        self.menu_panel_rect = (x1, y1, x1+panel_w, y1+panel_h)
        # item boxes (text baseline area)
        cur_y = y1 + MOOD_MENU_TITLE_HEIGHT
        for i, _ in enumerate(MOOD_MENU_ITEMS):
            item_y1 = cur_y + i * MOOD_MENU_ITEM_HEIGHT
            item_y2 = item_y1 + MOOD_MENU_ITEM_HEIGHT
            # Reserve space on left for icon square + gap
            left_text_x = x1 + MOOD_MENU_PADDING + MOOD_ICON_SIZE + MOOD_ICON_TEXT_GAP
            self.menu_boxes.append((i, (left_text_x, item_y1, x1+panel_w-MOOD_MENU_PADDING, item_y2)))
        # store icon anchor x position (square area start)
        self.menu_icon_x = x1 + MOOD_MENU_PADDING

    def draw_mood_menu(self):
        px = self.scale
        (x1,y1,x2,y2) = self.menu_panel_rect
        # Slide from slight upward offset (ease-out style using (1 - (1-p)^2))
        ease = 1 - (1 - self.menu_anim_progress)**2
        slide_offset = int((1 - ease) * 40)  # slide down distance
        y1s = y1 - slide_offset
        y2s = y2 - slide_offset
        self.canvas.create_rectangle(x1*px, y1s*px, x2*px, y2s*px, fill=MOOD_MENU_BG, outline=MOOD_MENU_BORDER, width=2)
        # Title
        if USE_BLOCKY_FONT:
            title_width = self._get_blocky_text_width(MOOD_MENU_TITLE)
            title_x = x1 + (MOOD_MENU_WIDTH - title_width) // 2
            self._draw_blocky_text(title_x, y1s + MOOD_MENU_PADDING, MOOD_MENU_TITLE, MOOD_MENU_TEXT_COLOR)
        else:
            self.canvas.create_text((x1+MOOD_MENU_WIDTH/2)*px, (y1s+MOOD_MENU_PADDING+4)*px, text=MOOD_MENU_TITLE, fill=MOOD_MENU_TEXT_COLOR, font=MOOD_MENU_FONT, anchor="n")
        # Items
        for idx, (ix1,iy1,ix2,iy2) in self.menu_boxes:
            # apply same vertical slide
            iy1s = iy1 - slide_offset
            iy2s = iy2 - slide_offset
            hovered = (idx == self.menu_hover_index)
            if hovered:
                # background
                self.canvas.create_rectangle(ix1*px, iy1s*px, ix2*px, iy2s*px, fill=MOOD_MENU_HOVER_BG, outline="")
                # left accent bar
                self.canvas.create_rectangle((ix1- (MOOD_ICON_SIZE + MOOD_ICON_TEXT_GAP) -4)*px, iy1s*px, (ix1- (MOOD_ICON_SIZE + MOOD_ICON_TEXT_GAP) -2)*px, iy2s*px, fill=MOOD_MENU_ACCENT, outline="")
            label, desc = MOOD_MENU_ITEMS[idx]
            text_color = MOOD_MENU_HOVER_TEXT if hovered else MOOD_MENU_TEXT_COLOR
            inner_w = (ix2 - ix1) - MOOD_MENU_PADDING  # single side padding since ix1 already accounts for left pad + icon
            # rough char capacity using monospace width ~7 px at scale 1 for font size 12
            max_label_chars = max(4, inner_w // 7)
            max_desc_chars = max(4, inner_w // 6)
            label_draw = self._truncate_text(label, max_label_chars)
            desc_draw = self._truncate_text(desc, max_desc_chars)
            # icon drawing
            icon_photo = self._to_menu_icon_photo(label)
            icon_box_y = iy1s + (MOOD_MENU_ITEM_HEIGHT - MOOD_ICON_SIZE)//2
            if icon_photo is not None:
                # If draw scale enlarged, center within original MOOD_ICON_SIZE square
                rendered_side = int(MOOD_ICON_SIZE * MOOD_ICON_DRAW_SCALE)
                offset = 0
                if rendered_side > MOOD_ICON_SIZE:
                    offset = (rendered_side - MOOD_ICON_SIZE)//2
                draw_x = self.menu_icon_x - offset
                draw_y = icon_box_y - offset
                self.canvas.create_image(draw_x*px, draw_y*px, anchor='nw', image=icon_photo)
                self._frame_refs.append(icon_photo)
            # left aligned text after icon
            text_x = ix1
            base_y = iy1s + 6
            if USE_BLOCKY_FONT:
                self._draw_blocky_text(text_x, base_y, label_draw, text_color)
                self._draw_blocky_text(text_x, base_y + MOOD_MENU_DESC_OFFSET, desc_draw, text_color)
            else:
                self.canvas.create_text(text_x*px, base_y*px, text=label_draw, fill=text_color, font=MOOD_MENU_FONT, anchor='nw')
                self.canvas.create_text(text_x*px, (base_y + MOOD_MENU_DESC_OFFSET)*px, text=desc_draw, fill=text_color, font=MOOD_MENU_DESC_FONT, anchor='nw')

    def draw_selection_badge(self):
        if self.menu_selected_index < 0 or self.menu_selected_index >= len(MOOD_MENU_ITEMS):
            return
        label, _ = MOOD_MENU_ITEMS[self.menu_selected_index]
        txt = f"Mood: {label}"
        px = self.scale
        pad = 6
        
        if USE_BLOCKY_FONT:
            # Calculate dimensions using blocky font
            w = self._get_blocky_text_width(txt) + pad*2
            h = 7 * BLOCKY_FONT_SCALE + pad*2
        else:
            # measure roughly: char * 7 pixels width (Courier assumption)
            w = len(txt) * 7 + pad*2
            h = 18
            
        x1 = self.width - w - 8
        y1 = 8
        x2 = x1 + w
        y2 = y1 + h
        self.canvas.create_rectangle(x1*px, y1*px, x2*px, y2*px, fill=MOOD_MENU_BG, outline=MOOD_MENU_ACCENT, width=1)
        
        if USE_BLOCKY_FONT:
            text_x = x1 + pad
            text_y = y1 + pad
            self._draw_blocky_text(text_x, text_y, txt, MOOD_MENU_ACCENT)
        else:
            self.canvas.create_text((x1 + w/2)*px, (y1 + h/2)*px, text=txt, fill=MOOD_MENU_ACCENT, font=MOOD_BADGE_FONT)

    # text helper
    def _truncate_text(self, text, max_chars):
        if len(text) <= max_chars:
            return text
        if max_chars <= 3:
            return text[:max_chars]
        return text[:max_chars-3] + '...'

    # -------- Focused Scene Helpers --------
    def _point_in_box(self, x, y, box):
        x1,y1,x2,y2 = box
        return x1 <= x <= x2 and y1 <= y <= y2

    def _draw_hitbox(self, box, color):
        x1,y1,x2,y2 = box
        px = self.scale
        self.canvas.create_rectangle(x1*px, y1*px, x2*px, y2*px, outline=color)

    def _draw_focus_hover(self, box):
        x1,y1,x2,y2 = box
        px = self.scale
        self.canvas.create_rectangle(x1*px, y1*px, x2*px, y2*px,
                                     outline=FOCUSED_HOVER_OUTLINE,
                                     width=FOCUSED_HOVER_OUTLINE_WIDTH)

    # -------- Blocky Font System --------
    def _blocky_font_char_bitmap(self, char):
        """Return a 5x7 bitmap for a blocky character. 1 = filled pixel, 0 = empty."""
        char = char.upper()
        bitmaps = {
            'A': [
                "01110",
                "10001",
                "10001",
                "11111",
                "10001",
                "10001",
                "00000"
            ],
            'B': [
                "11110",
                "10001",
                "11110",
                "11110",
                "10001",
                "11110",
                "00000"
            ],
            'C': [
                "01111",
                "10000",
                "10000",
                "10000",
                "10000",
                "01111",
                "00000"
            ],
            'D': [
                "11110",
                "10001",
                "10001",
                "10001",
                "10001",
                "11110",
                "00000"
            ],
            'E': [
                "11111",
                "10000",
                "11110",
                "10000",
                "10000",
                "11111",
                "00000"
            ],
            'F': [
                "11111",
                "10000",
                "11110",
                "10000",
                "10000",
                "10000",
                "00000"
            ],
            'G': [
                "01111",
                "10000",
                "10011",
                "10001",
                "10001",
                "01111",
                "00000"
            ],
            'H': [
                "10001",
                "10001",
                "11111",
                "10001",
                "10001",
                "10001",
                "00000"
            ],
            'I': [
                "11111",
                "00100",
                "00100",
                "00100",
                "00100",
                "11111",
                "00000"
            ],
            'J': [
                "11111",
                "00001",
                "00001",
                "00001",
                "10001",
                "01110",
                "00000"
            ],
            'K': [
                "10001",
                "10010",
                "11100",
                "10010",
                "10001",
                "10001",
                "00000"
            ],
            'L': [
                "10000",
                "10000",
                "10000",
                "10000",
                "10000",
                "11111",
                "00000"
            ],
            'M': [
                "10001",
                "11011",
                "10101",
                "10001",
                "10001",
                "10001",
                "00000"
            ],
            'N': [
                "10001",
                "11001",
                "10101",
                "10011",
                "10001",
                "10001",
                "00000"
            ],
            'O': [
                "01110",
                "10001",
                "10001",
                "10001",
                "10001",
                "01110",
                "00000"
            ],
            'P': [
                "11110",
                "10001",
                "11110",
                "10000",
                "10000",
                "10000",
                "00000"
            ],
            'Q': [
                "01110",
                "10001",
                "10001",
                "10101",
                "10010",
                "01101",
                "00000"
            ],
            'R': [
                "11110",
                "10001",
                "11110",
                "10010",
                "10001",
                "10001",
                "00000"
            ],
            'S': [
                "01111",
                "10000",
                "01110",
                "00001",
                "00001",
                "11110",
                "00000"
            ],
            'T': [
                "11111",
                "00100",
                "00100",
                "00100",
                "00100",
                "00100",
                "00000"
            ],
            'U': [
                "10001",
                "10001",
                "10001",
                "10001",
                "10001",
                "01110",
                "00000"
            ],
            'V': [
                "10001",
                "10001",
                "10001",
                "10001",
                "01010",
                "00100",
                "00000"
            ],
            'W': [
                "10001",
                "10001",
                "10001",
                "10101",
                "11011",
                "10001",
                "00000"
            ],
            'X': [
                "10001",
                "01010",
                "00100",
                "01010",
                "10001",
                "10001",
                "00000"
            ],
            'Y': [
                "10001",
                "01010",
                "00100",
                "00100",
                "00100",
                "00100",
                "00000"
            ],
            'Z': [
                "11111",
                "00010",
                "00100",
                "01000",
                "10000",
                "11111",
                "00000"
            ],
            ' ': [
                "00000",
                "00000",
                "00000",
                "00000",
                "00000",
                "00000",
                "00000"
            ],
            ':': [
                "00000",
                "00100",
                "00000",
                "00000",
                "00100",
                "00000",
                "00000"
            ],
            '.': [
                "00000",
                "00000",
                "00000",
                "00000",
                "00000",
                "00100",
                "00000"
            ],
            '0': [
                "01110",
                "10001",
                "10011",
                "10101",
                "11001",
                "01110",
                "00000"
            ],
            '1': [
                "00100",
                "01100",
                "00100",
                "00100",
                "00100",
                "01110",
                "00000"
            ],
            '2': [
                "01110",
                "10001",
                "00010",
                "00100",
                "01000",
                "11111",
                "00000"
            ],
            '3': [
                "01110",
                "10001",
                "00110",
                "00001",
                "10001",
                "01110",
                "00000"
            ],
            '4': [
                "00010",
                "00110",
                "01010",
                "11111",
                "00010",
                "00010",
                "00000"
            ],
            '5': [
                "11111",
                "10000",
                "11110",
                "00001",
                "10001",
                "01110",
                "00000"
            ],
            '6': [
                "01110",
                "10000",
                "11110",
                "10001",
                "10001",
                "01110",
                "00000"
            ],
            '7': [
                "11111",
                "00001",
                "00010",
                "00100",
                "01000",
                "01000",
                "00000"
            ],
            '8': [
                "01110",
                "10001",
                "01110",
                "10001",
                "10001",
                "01110",
                "00000"
            ],
            '9': [
                "01110",
                "10001",
                "01111",
                "00001",
                "00001",
                "01110",
                "00000"
            ]
        }
        return bitmaps.get(char, bitmaps[' '])  # fallback to space

    def _draw_blocky_text(self, x, y, text, color='#ffffff', bg_color=None):
        """Draw blocky pixel text at logical coordinates (x, y)."""
        if not USE_BLOCKY_FONT:
            return
        
        char_width = 5 * BLOCKY_FONT_SCALE + BLOCKY_FONT_SPACING
        char_height = 7 * BLOCKY_FONT_SCALE
        px = self.scale
        
        for i, char in enumerate(text):
            bitmap = self._blocky_font_char_bitmap(char)
            char_x = x + i * char_width
            
            # Draw background if specified
            if bg_color:
                self.canvas.create_rectangle(
                    char_x * px, y * px,
                    (char_x + 5 * BLOCKY_FONT_SCALE) * px,
                    (y + char_height) * px,
                    fill=bg_color, outline=""
                )
            
            # Draw character pixels
            for row_idx, row in enumerate(bitmap):
                for col_idx, pixel in enumerate(row):
                    if pixel == '1':
                        pixel_x = char_x + col_idx * BLOCKY_FONT_SCALE
                        pixel_y = y + row_idx * BLOCKY_FONT_SCALE
                        self.canvas.create_rectangle(
                            pixel_x * px, pixel_y * px,
                            (pixel_x + BLOCKY_FONT_SCALE) * px,
                            (pixel_y + BLOCKY_FONT_SCALE) * px,
                            fill=color, outline=""
                        )

    def _get_blocky_text_width(self, text):
        """Return the logical width of blocky text."""
        if not text:
            return 0
        char_width = 5 * BLOCKY_FONT_SCALE + BLOCKY_FONT_SPACING
        return len(text) * char_width - BLOCKY_FONT_SPACING  # remove last spacing

    # -------- Pixel Font Helper --------
    # -------- Cozy Submenu Methods --------
    def activate_cozy_submenu(self):
        self.cozy_submenu_active = True
        self.cozy_submenu_hover_index = -1
        self.build_cozy_submenu_layout()
        
    def build_cozy_submenu_layout(self):
        self.cozy_submenu_boxes.clear()
        panel_w = MOOD_MENU_WIDTH
        total_items = len(COZY_SUBMENU_ITEMS)
        panel_h = (MOOD_MENU_TITLE_HEIGHT + MOOD_MENU_PADDING +
                   total_items * MOOD_MENU_ITEM_HEIGHT + MOOD_MENU_PADDING)
        # center panel
        x1 = (self.width - panel_w)//2
        y1 = (self.height - panel_h)//2
        # store panel rect for drawing
        self.cozy_submenu_panel_rect = (x1, y1, x1+panel_w, y1+panel_h)
        # item boxes
        cur_y = y1 + MOOD_MENU_TITLE_HEIGHT
        for i, _ in enumerate(COZY_SUBMENU_ITEMS):
            item_y1 = cur_y + i * MOOD_MENU_ITEM_HEIGHT
            item_y2 = item_y1 + MOOD_MENU_ITEM_HEIGHT
            left_text_x = x1 + MOOD_MENU_PADDING
            self.cozy_submenu_boxes.append((i, (left_text_x, item_y1, x1+panel_w-MOOD_MENU_PADDING, item_y2)))
            
    def draw_cozy_submenu(self):
        px = self.scale
        (x1,y1,x2,y2) = self.cozy_submenu_panel_rect
        
        # Draw panel background
        self.canvas.create_rectangle(x1*px, y1*px, x2*px, y2*px, 
                                     fill=MOOD_MENU_BG, outline=MOOD_MENU_BORDER, width=2)
        
        # Title
        title_text = "Cozy Options"
        if USE_BLOCKY_FONT:
            title_width = self._get_blocky_text_width(title_text)
            title_x = x1 + (MOOD_MENU_WIDTH - title_width) // 2
            self._draw_blocky_text(title_x, y1 + MOOD_MENU_PADDING, title_text, MOOD_MENU_TEXT_COLOR)
        else:
            self.canvas.create_text((x1+MOOD_MENU_WIDTH/2)*px, (y1+MOOD_MENU_PADDING+4)*px, 
                                    text=title_text, fill=MOOD_MENU_TEXT_COLOR, font=MOOD_MENU_FONT, anchor="n")
        
        # Items
        for idx, (ix1,iy1,ix2,iy2) in self.cozy_submenu_boxes:
            hovered = (idx == self.cozy_submenu_hover_index)
            if hovered:
                self.canvas.create_rectangle(ix1*px, iy1*px, ix2*px, iy2*px, 
                                             fill=MOOD_MENU_HOVER_BG, outline="")
                self.canvas.create_rectangle((ix1-4)*px, iy1*px, (ix1-2)*px, iy2*px, 
                                             fill=MOOD_MENU_ACCENT, outline="")
            
            label, desc = COZY_SUBMENU_ITEMS[idx]
            text_color = MOOD_MENU_HOVER_TEXT if hovered else MOOD_MENU_TEXT_COLOR
            
            text_x = ix1
            base_y = iy1 + 6
            if USE_BLOCKY_FONT:
                self._draw_blocky_text(text_x, base_y, label, text_color)
                self._draw_blocky_text(text_x, base_y + MOOD_MENU_DESC_OFFSET, desc, text_color)
            else:
                self.canvas.create_text(text_x*px, base_y*px, text=label, 
                                        fill=text_color, font=MOOD_MENU_FONT, anchor='nw')
                self.canvas.create_text(text_x*px, (base_y + MOOD_MENU_DESC_OFFSET)*px, 
                                        text=desc, fill=text_color, font=MOOD_MENU_DESC_FONT, anchor='nw')
    
    # -------- Creative Submenu Methods --------
    def activate_creative_submenu(self):
        self.creative_submenu_active = True
        self.creative_submenu_hover_index = -1
        self.build_creative_submenu_layout()
        
    def build_creative_submenu_layout(self):
        """Build layout boxes for creative submenu items"""
        px = self.scale
        
        # Use same sizing and positioning as Cozy submenu
        center_x = self.width // 2
        center_y = self.height // 2
        
        menu_w = MOOD_MENU_WIDTH
        # Include title height in total menu height calculation
        menu_h = (MOOD_MENU_TITLE_HEIGHT + MOOD_MENU_PADDING +
                  len(CREATIVE_SUBMENU_ITEMS) * MOOD_MENU_ITEM_HEIGHT + MOOD_MENU_PADDING)
        
        x1 = center_x - menu_w // 2
        y1 = center_y - menu_h // 2
        
        self.creative_submenu_boxes = []
        
        for idx, (label, desc) in enumerate(CREATIVE_SUBMENU_ITEMS):
            item_y = y1 + MOOD_MENU_TITLE_HEIGHT + MOOD_MENU_PADDING + idx * MOOD_MENU_ITEM_HEIGHT
            item_h = MOOD_MENU_ITEM_HEIGHT - 4
            self.creative_submenu_boxes.append((idx, (x1 + MOOD_MENU_PADDING, item_y, x1 + menu_w - MOOD_MENU_PADDING, item_y + item_h)))
    
    def draw_creative_submenu(self):
        """Draw the creative submenu using same style as Cozy submenu"""
        px = self.scale
        
        # Background overlay
        self.canvas.create_rectangle(0, 0, self.width*px, self.height*px, 
                                   fill="#1a1a1a", stipple="gray50", outline="")
        
        # Use same sizing and positioning as Cozy submenu
        center_x = self.width // 2
        center_y = self.height // 2
        
        menu_w = MOOD_MENU_WIDTH
        # Include title height in total menu height calculation
        menu_h = (MOOD_MENU_TITLE_HEIGHT + MOOD_MENU_PADDING +
                  len(CREATIVE_SUBMENU_ITEMS) * MOOD_MENU_ITEM_HEIGHT + MOOD_MENU_PADDING)
        
        x1 = center_x - menu_w // 2
        y1 = center_y - menu_h // 2
        x2 = x1 + menu_w
        y2 = y1 + menu_h
        
        # Draw panel background using same colors as Cozy
        self.canvas.create_rectangle(x1*px, y1*px, x2*px, y2*px, 
                                     fill=MOOD_MENU_BG, outline=MOOD_MENU_BORDER, width=2)
        
        # Title
        title_text = "Creative Options"
        if USE_BLOCKY_FONT:
            title_width = self._get_blocky_text_width(title_text)
            title_x = x1 + (MOOD_MENU_WIDTH - title_width) // 2
            self._draw_blocky_text(title_x, y1 + MOOD_MENU_PADDING, title_text, MOOD_MENU_TEXT_COLOR)
        else:
            self.canvas.create_text((x1+MOOD_MENU_WIDTH/2)*px, (y1+MOOD_MENU_PADDING+4)*px, 
                                    text=title_text, fill=MOOD_MENU_TEXT_COLOR, font=MOOD_MENU_FONT, anchor="n")
        
        # Items
        for idx, (label, desc) in enumerate(CREATIVE_SUBMENU_ITEMS):
            item_y = y1 + MOOD_MENU_TITLE_HEIGHT + MOOD_MENU_PADDING + idx * MOOD_MENU_ITEM_HEIGHT
            
            hovered = (idx == self.creative_submenu_hover_index)
            if hovered:
                # Use same hover styling as Cozy menu
                ix1, iy1 = x1 + MOOD_MENU_PADDING, item_y
                ix2, iy2 = x2 - MOOD_MENU_PADDING, item_y + MOOD_MENU_ITEM_HEIGHT - 4
                
                self.canvas.create_rectangle(ix1*px, iy1*px, ix2*px, iy2*px, 
                                             fill=MOOD_MENU_HOVER_BG, outline="")
                self.canvas.create_rectangle((ix1-4)*px, iy1*px, (ix1-2)*px, iy2*px, 
                                             fill=MOOD_MENU_ACCENT, outline="")
            
            text_color = MOOD_MENU_HOVER_TEXT if hovered else MOOD_MENU_TEXT_COLOR
            
            text_x = x1 + MOOD_MENU_PADDING
            base_y = item_y + 6
            if USE_BLOCKY_FONT:
                self._draw_blocky_text(text_x, base_y, label, text_color)
                self._draw_blocky_text(text_x, base_y + MOOD_MENU_DESC_OFFSET, desc, text_color)
            else:
                self.canvas.create_text(text_x*px, base_y*px, text=label, 
                                        fill=text_color, font=MOOD_MENU_FONT, anchor='nw')
                self.canvas.create_text(text_x*px, (base_y + MOOD_MENU_DESC_OFFSET)*px, 
                                        text=desc, fill=text_color, font=MOOD_MENU_DESC_FONT, anchor='nw')
    
    def open_code_editor(self):
        """Open the source code file for editing"""
        try:
            import subprocess
            import sys
            
            # Get the current script path
            script_path = os.path.abspath(__file__)
            
            # Try to open with the default system editor
            if sys.platform.startswith('win'):
                # Windows - try notepad, then default
                try:
                    subprocess.run(['notepad.exe', script_path], check=True)
                except:
                    os.startfile(script_path)
            elif sys.platform.startswith('darwin'):
                # macOS
                subprocess.run(['open', '-t', script_path])
            else:
                # Linux
                editors = ['gedit', 'nano', 'vim', 'emacs']
                for editor in editors:
                    try:
                        subprocess.run([editor, script_path], check=True)
                        break
                    except FileNotFoundError:
                        continue
                        
        except Exception as e:
            print(f"[WARN] Could not open code editor: {e}")
            # Fallback - show file path
            messagebox.showinfo("Code Editor", f"Source code file:\n{os.path.abspath(__file__)}")
    
    # -------- Focused Submenu Methods --------
    def activate_focused_submenu(self):
        self.focused_submenu_active = True
        self.focused_submenu_hover_index = -1
        self.build_focused_submenu_layout()
        
    def build_focused_submenu_layout(self):
        self.focused_submenu_boxes.clear()
        panel_w = MOOD_MENU_WIDTH
        total_items = len(FOCUSED_SUBMENU_ITEMS)
        panel_h = (MOOD_MENU_TITLE_HEIGHT + MOOD_MENU_PADDING +
                   total_items * MOOD_MENU_ITEM_HEIGHT + MOOD_MENU_PADDING)
        # center panel
        x1 = (self.width - panel_w)//2
        y1 = (self.height - panel_h)//2
        # store panel rect for drawing
        self.focused_submenu_panel_rect = (x1, y1, x1+panel_w, y1+panel_h)
        # item boxes
        cur_y = y1 + MOOD_MENU_TITLE_HEIGHT
        for i, _ in enumerate(FOCUSED_SUBMENU_ITEMS):
            item_y1 = cur_y + i * MOOD_MENU_ITEM_HEIGHT
            item_y2 = item_y1 + MOOD_MENU_ITEM_HEIGHT
            left_text_x = x1 + MOOD_MENU_PADDING
            self.focused_submenu_boxes.append((i, (left_text_x, item_y1, x1+panel_w-MOOD_MENU_PADDING, item_y2)))
            
    def draw_focused_submenu(self):
        px = self.scale
        (x1,y1,x2,y2) = self.focused_submenu_panel_rect
        
        # Draw panel background
        self.canvas.create_rectangle(x1*px, y1*px, x2*px, y2*px, 
                                     fill=MOOD_MENU_BG, outline=MOOD_MENU_BORDER, width=2)
        
        # Title
        title_text = "Focused Options"
        if USE_BLOCKY_FONT:
            title_width = self._get_blocky_text_width(title_text)
            title_x = x1 + (MOOD_MENU_WIDTH - title_width) // 2
            self._draw_blocky_text(title_x, y1 + MOOD_MENU_PADDING, title_text, MOOD_MENU_TEXT_COLOR)
        else:
            self.canvas.create_text((x1+MOOD_MENU_WIDTH/2)*px, (y1+MOOD_MENU_PADDING+4)*px, 
                                    text=title_text, fill=MOOD_MENU_TEXT_COLOR, font=MOOD_MENU_FONT, anchor="n")
        
        # Items
        for idx, (ix1,iy1,ix2,iy2) in self.focused_submenu_boxes:
            if idx < len(FOCUSED_SUBMENU_ITEMS):
                label, desc = FOCUSED_SUBMENU_ITEMS[idx]
                hovered = (idx == self.focused_submenu_hover_index)
                if hovered:
                    self.canvas.create_rectangle(ix1*px, iy1*px, ix2*px, iy2*px, fill=MOOD_MENU_HOVER_BG, outline="")
                    # Draw left accent bar
                    self.canvas.create_rectangle((ix1-4)*px, iy1*px, (ix1-2)*px, iy2*px, fill=MOOD_MENU_ACCENT, outline="")
                text_color = MOOD_MENU_HOVER_TEXT if hovered else MOOD_MENU_TEXT_COLOR
                
                text_x = ix1
                base_y = iy1 + 6
                if USE_BLOCKY_FONT:
                    self._draw_blocky_text(text_x, base_y, label, text_color)
                    self._draw_blocky_text(text_x, base_y + MOOD_MENU_DESC_OFFSET, desc, text_color)
                else:
                    self.canvas.create_text(text_x*px, base_y*px, text=label, fill=text_color, font=MOOD_MENU_FONT, anchor='nw')
                    self.canvas.create_text(text_x*px, (base_y + MOOD_MENU_DESC_OFFSET)*px, text=desc, fill=text_color, font=MOOD_MENU_DESC_FONT, anchor='nw')
    
    # -------- Phone Game Methods --------
    def start_phone_game(self):
        if not self.phone_image:
            print("[WARN] Phone image not loaded, cannot start phone game")
            return
            
        self.phone_game_active = True
        # Use configurable game dimensions with scale factor
        game_w = int(PHONE_GAME_WIDTH * PHONE_GAME_SCALE)
        game_h = int(PHONE_GAME_HEIGHT * PHONE_GAME_SCALE)
        self.tea_timer_game = TeaTimerGame(game_w, game_h)
        
        # Ensure window has focus for key events
        self.root.focus_force()
        self.canvas.focus_set()  # Also set focus on canvas
        
    def draw_phone_game(self):
        if not self.phone_image or not self.tea_timer_game:
            return
            
        px = self.scale
        
        # Center phone on screen horizontally, move up by 1cm vertically
        phone_w, phone_h = self.phone_image.size
        phone_x = (self.width - phone_w) // 2
        phone_y = (self.height - phone_h) // 2 - 60  # Move up more (~2cm)
        
        # Draw phone image
        phone_photo = self._to_photo(self.phone_image)
        self.canvas.create_image(phone_x*px, phone_y*px, anchor="nw", image=phone_photo)
        self._frame_refs.append(phone_photo)
        
        # Game area positioning using configurable offsets
        game_offset_x = phone_x + int(PHONE_GAME_OFFSET_X * PHONE_GAME_SCALE)
        game_offset_y = phone_y + int(PHONE_GAME_OFFSET_Y * PHONE_GAME_SCALE)
        
        # Draw game area background
        game_w, game_h = self.tea_timer_game.width, self.tea_timer_game.height
        self.canvas.create_rectangle(game_offset_x*px, game_offset_y*px, 
                                     (game_offset_x + game_w)*px, (game_offset_y + game_h)*px,
                                     fill="#2a1810", outline="#8b4513", width=2)
        
        # Draw title
        title_y = game_offset_y + 15
        self.canvas.create_text((game_offset_x + game_w//2)*px, title_y*px,
                              text="TEA TIMER", fill="#f4e4c1", 
                              font=("Fixedsys", 9, "bold"))
        
        # Draw timer bar background
        bar_margin = 15
        bar_height = 25
        bar_y = title_y + 30
        bar_x_start = game_offset_x + bar_margin
        bar_x_end = game_offset_x + game_w - bar_margin
        bar_width = bar_x_end - bar_x_start
        
        # Timer bar background
        self.canvas.create_rectangle(bar_x_start*px, bar_y*px,
                                   bar_x_end*px, (bar_y + bar_height)*px,
                                   fill="#654321", outline="#8b4513", width=2)
        
        # Perfect zone indicator
        perfect_start_x = bar_x_start + int(bar_width * self.tea_timer_game.perfect_zone_start)
        perfect_end_x = bar_x_start + int(bar_width * self.tea_timer_game.perfect_zone_end)
        self.canvas.create_rectangle(perfect_start_x*px, bar_y*px,
                                   perfect_end_x*px, (bar_y + bar_height)*px,
                                   fill="#90EE90", outline="#228B22", width=1)
        
        # Current timer progress
        progress = self.tea_timer_game.get_timer_progress()
        current_x = bar_x_start + int(bar_width * progress)
        if progress > 0:
            # Timer progress bar
            color = "#90EE90" if self.tea_timer_game.is_in_perfect_zone() else "#DEB887"
            self.canvas.create_rectangle(bar_x_start*px, bar_y*px,
                                       current_x*px, (bar_y + bar_height)*px,
                                       fill=color, outline="")
        
        # Timer position indicator (moving line)
        if self.tea_timer_game.game_state == "running":
            self.canvas.create_line(current_x*px, bar_y*px,
                                  current_x*px, (bar_y + bar_height)*px,
                                  fill="red", width=3)
        
        # Instructions
        inst_y = bar_y + bar_height + 25
        if self.tea_timer_game.game_state == "running":
            self.canvas.create_text((game_offset_x + game_w//2)*px, inst_y*px,
                                  text="Press ENTER in", fill="#f4e4c1", 
                                  font=("Fixedsys", 7))
            self.canvas.create_text((game_offset_x + game_w//2)*px, (inst_y + 12)*px,
                                  text="GREEN ZONE", fill="#90EE90", 
                                  font=("Fixedsys", 7, "bold"))
        
        # Difficulty info
        diff_y = inst_y + 30
        difficulty_info = self.tea_timer_game.get_difficulty_info()
        # Split difficulty info into multiple lines if too long
        parts = difficulty_info.split(" | ")
        for i, part in enumerate(parts):
            self.canvas.create_text((game_offset_x + game_w//2)*px, (diff_y + i*10)*px,
                                  text=part, fill="#DEB887", 
                                  font=("Fixedsys", 6))
        
        # Result message
        if self.tea_timer_game.result_message:
            result_y = diff_y + len(parts)*10 + 15
            color = "#90EE90" if "Perfect" in self.tea_timer_game.result_message else "#FF6B6B"
            # Split long result messages
            message = self.tea_timer_game.result_message
            if len(message) > 15:
                words = message.split()
                line1 = " ".join(words[:2])
                line2 = " ".join(words[2:])
                self.canvas.create_text((game_offset_x + game_w//2)*px, result_y*px,
                                      text=line1, fill=color, 
                                      font=("Fixedsys", 8, "bold"))
                self.canvas.create_text((game_offset_x + game_w//2)*px, (result_y + 12)*px,
                                      text=line2, fill=color, 
                                      font=("Fixedsys", 8, "bold"))
            else:
                self.canvas.create_text((game_offset_x + game_w//2)*px, result_y*px,
                                      text=message, fill=color, 
                                      font=("Fixedsys", 8, "bold"))
        
        # Timer display
        time_left = max(0, self.tea_timer_game.timer_total - self.tea_timer_game.timer_elapsed)
        timer_y = game_offset_y + game_h - 30
        self.canvas.create_text((game_offset_x + game_w//2)*px, timer_y*px,
                              text=f"{time_left:.1f}s", fill="#f4e4c1", 
                              font=("Fixedsys", 7))
        
        # Exit instruction
        exit_y = game_offset_y + game_h - 15
        self.canvas.create_text((game_offset_x + game_w//2)*px, exit_y*px,
                              text="ESC=exit", fill="#888", 
                              font=("Fixedsys", 6))
    
    # -------- Meditation Methods --------
    def start_meditation(self):
        self.meditation_active = True
        self.meditation_timer = MeditationTimer()
        self.meditation_timer.start()
        
    def draw_meditation(self):
        if not self.meditation_timer:
            return
            
        px = self.scale
        
        # Dark overlay background
        overlay_alpha = 200
        overlay = Image.new('RGBA', (self.width, self.height), (26, 26, 46, overlay_alpha))
        overlay_photo = self._to_photo(overlay)
        self.canvas.create_image(0, 0, anchor="nw", image=overlay_photo)
        self._frame_refs.append(overlay_photo)
        
        # Central meditation panel
        panel_w = 300
        panel_h = 200
        panel_x = (self.width - panel_w) // 2
        panel_y = (self.height - panel_h) // 2
        
        # Panel background with gradient effect
        self.canvas.create_rectangle(panel_x*px, panel_y*px, 
                                     (panel_x + panel_w)*px, (panel_y + panel_h)*px,
                                     fill=MEDITATION_BG_COLOR, outline=MEDITATION_ACCENT_COLOR, width=3)
        
        # Inner glow effect
        for i in range(3):
            glow_alpha = 50 - i*15
            glow_color = f"#{int(244*0.3):02x}{int(162*0.3):02x}{int(97*0.3):02x}"
            self.canvas.create_rectangle((panel_x-i)*px, (panel_y-i)*px,
                                         (panel_x + panel_w + i)*px, (panel_y + panel_h + i)*px,
                                         outline=glow_color, width=1)
        
        # Timer display
        time_text = self.meditation_timer.get_time_display()
        timer_y = panel_y + 40
        if USE_BLOCKY_FONT:
            # Calculate proper character width for 2x scaled blocky font
            char_width = (5 * BLOCKY_FONT_SCALE + BLOCKY_FONT_SPACING) * 2  # 2x scale factor
            time_width = len(time_text) * char_width - BLOCKY_FONT_SPACING * 2  # Remove last spacing
            time_x = panel_x + (panel_w - time_width) // 2
            # Draw bigger blocky text by drawing multiple scaled characters
            for i, char in enumerate(time_text):
                char_x = time_x + i * char_width
                for row_idx, row in enumerate(self._blocky_font_char_bitmap(char)):
                    for col_idx, pixel in enumerate(row):
                        if pixel == '1':
                            # Draw 2x2 pixel blocks for bigger text
                            pixel_x = char_x + col_idx * BLOCKY_FONT_SCALE * 2
                            pixel_y = timer_y + row_idx * BLOCKY_FONT_SCALE * 2
                            self.canvas.create_rectangle(
                                pixel_x * px, pixel_y * px,
                                (pixel_x + BLOCKY_FONT_SCALE * 2) * px, 
                                (pixel_y + BLOCKY_FONT_SCALE * 2) * px,
                                fill=MEDITATION_ACCENT_COLOR, outline=""
                            )
        else:
            self.canvas.create_text((panel_x + panel_w//2)*px, timer_y*px, 
                                    text=time_text, fill=MEDITATION_ACCENT_COLOR,
                                    font=("Courier New", 24, "bold"), anchor="n")
        
        # Breathing instruction
        instruction = self.meditation_timer.get_breathing_instruction()
        instruction_y = panel_y + 90
        if USE_BLOCKY_FONT:
            inst_width = self._get_blocky_text_width(instruction)
            inst_x = panel_x + (panel_w - inst_width) // 2
            self._draw_blocky_text(inst_x, instruction_y, instruction, MEDITATION_TEXT_COLOR)
        else:
            self.canvas.create_text((panel_x + panel_w//2)*px, instruction_y*px,
                                    text=instruction, fill=MEDITATION_TEXT_COLOR,
                                    font=("Courier New", 16, "bold"), anchor="n")
        
        # Breathing circle visualization
        circle_center_x = panel_x + panel_w // 2
        circle_center_y = panel_y + 140
        base_radius = 20
        breathing_progress = self.meditation_timer.get_breathing_progress()
        
        # Animate circle size based on breathing phase
        if self.meditation_timer.breathing_phase == "inhale":
            radius = int(base_radius + breathing_progress * 15)
        else:
            radius = int(base_radius + 15 - breathing_progress * 15)
            
        # Outer breathing circle
        self.canvas.create_oval((circle_center_x - radius)*px, (circle_center_y - radius)*px,
                                (circle_center_x + radius)*px, (circle_center_y + radius)*px,
                                outline=MEDITATION_ACCENT_COLOR, width=3, fill="")
        
        # Inner steady circle
        inner_radius = base_radius // 2
        self.canvas.create_oval((circle_center_x - inner_radius)*px, (circle_center_y - inner_radius)*px,
                                (circle_center_x + inner_radius)*px, (circle_center_y + inner_radius)*px,
                                fill=MEDITATION_TEXT_COLOR, outline="")
        
        # Exit instruction
        exit_text = "Press ESC to exit meditation"
        exit_y = panel_y + panel_h - 20
        self.canvas.create_text((panel_x + panel_w//2)*px, exit_y*px,
                                text=exit_text, fill=MEDITATION_TEXT_COLOR,
                                font=("Courier New", 10), anchor="n")

    # -------- Coffee Scene Methods --------
    def start_coffee_scene(self):
        """Start the coffee brewing process."""
        self.coffee_brewing = True
        self.coffee_brew_timer = 0
        # Play coffee brewing sound
        if self.coffee_loaded:
            try:
                self.coffee_channel = self.coffee_sound.play(loops=0)  # Play once, no looping
            except Exception as e:
                print("[WARN] Could not play coffee sound:", e)
        
    def get_random_coffee_reading(self):
        """Generate a random reading from a curated set of short, fun quotes (not coffee-specific)."""
        quotes = [
            "Plot twist: it worked on the first try",
            "Low effort, high impact",
            "Shipping beats perfect",
            "Vibes immaculate, bugs negotiable",
            "Pixels over polish",
            "No meetings, just momentum",
            "Stay curious, stay scrappy",
            "Move fast, don't break your soul",
            "Silent grind, loud results",
            "Make it simple, make it weird",
            "Less talk, more ship",
            "Chaos, but curated",
            "Comfort zone: read-only",
            "Unmute your ideas",
            "Stay dangerous, be kind",
            "New tab, new chance",
            "Risk it for the biscuit",
            "Launch, then learn",
            "Perfect is postponed",
            "Iterate like you mean it",
            "Small wins, big waves",
            "Energy is a skill",
            "Do it scared",
            "We outside the comfort zone",
            "Delayed not denied",
            "Trust the plot",
            "You are the update",
            "Delete the doubt",
            "Tap in, lock in",
            "Let it be legendary",
            "Quietly iconic",
            "Build weird, stay soft",
            "Main character moment",
            "Dream in 8-bit",
            "Own the timeline",
            "Keep it playful",
            "Stay low, glow high",
            "Calm is a superpower",
            "Make it make sense",
            "Touch grass, write code",
            "Unsubscribe from drama",
            "Choose different",
            "Time is loud today",
            "You got this, obviously",
            "Certified vibe engineer",
            "Do less, but better",
            "Unbothered, hydrated",
            "Soft reset, hard focus",
            "New day, who dis",
            "Gold star energy",
            "Chaos, but optimized",
            "Blink and it's done",
            "High signal, low noise",
            "Stack wins, not tabs",
            "Speedrun the boring parts",
            "Make room for magic",
            "Edge case enthusiast",
            "Loading: better days",
            "Unstoppable but chill",
            "Go where the energy is",
            "Clean commits, clean mind",
            "Main quest: joy",
            "Side quests allowed",
            "Take up pixel space",
            "Beauty in the scuffed",
            "Grace over grind",
            "Good weird only",
            "Pause, then pounce",
            "Curiosity has Wi-Fi",
            "Make it inevitable",
            "Out of office, in the zone",
            "Focus is a flex",
            "Keyboard therapy session",
            "Don't overthink the fun",
            "Protect your peace",
            "Your pace is the meta",
            "Stay crispy, not burnt",
            "Mind like water",
            "Try, fail, learn, repeat",
            "Be the plot twist",
            "Start where you stand",
            "Done is gorgeous",
            "Leave room for wonder",
            "Future you says thanks",
            "Bet on your odd ideas",
            "Quiet hustle, loud life",
            "Nothing to prove",
            "Wild but respectful",
            "Let the nice things find you",
            "Naps are strategy",
            "Tap into cozy mode",
            "Soft launch your brilliance",
            "Refactor the vibe",
            "Shenanigans permitted",
            "Kindness scales",
            "Deadlines and lifelines",
            "Breathe like you mean it",
            "Light mode energy, dark mode focus",
            "New level unlocked",
            "Make it delightfully unnecessary",
            "Go make a tiny masterpiece",
            "Minimum viable joy",
            "Permission to be luminous",
            "Protect the weekend",
            "Aligned and unbothered",
            "Luck loves momentum",
            "Keep the bar weird",
            "Stay risky, stay kind",
            "Debug the mood",
            "Lag is temporary, style is forever",
            "Readme of your life: concise",
            "Trust your taste",
            "Underpromise, overvibe",
            "No one is you",
            "Signal > noise",
            "Make sparks, not smoke",
            "Commit messages write history",
            "Charge the fun meter",
            "Delight is a feature",
            "Whimsy approved",
            "Be the friendly anomaly",
            "Play like nobody's watching",
            "Infinite scroll of good ideas",
            "Bring your weird to work",
            "Curious, not furious",
            "Less doom, more bloom",
            "Quiet power, loud kindness",
            "Soft edges, sharp mind",
            "Ship the thing",
            "Chaos is a ladder... to learning",
            "Prototype the feeling",
            "Win the morning, coast the night",
            "Own your narrative",
            "Kind over cool",
            "Progress: now playing",
            "Give them easter eggs",
            "Write it like you mean it",
            "Bugs fear committed people",
            "You are allowed to take up space",
            "Make the small thing special",
            "Rest like it's part of the plan",
            "Momentum is magnetic",
            "Tiny steps, thunder results",
            "Refresh the vibe cache",
            "Be the calm in the chaos",
            "Chase clarity, not clout",
            "Smoother than your timeline",
            "Dream big, cache often",
            "Your weird is your superpower",
            "Quiet focus, bright future",
            "Upgrade your inner voice",
            "Run your own benchmark",
            "Don't borrow future stress",
            "We ship joy here",
            "Stay stubborn about your goals",
            "Make boredom productive",
            "Reduce, reuse, reimagine",
            "Collect moments, not tabs",
            "Less scroll, more soul",
            "Respect your rest",
            "Today: soft start, sharp finish",
            "Find the fun in the friction",
            "Keep learning out loud",
            "You're building a classic",
            "Every day is dev day",
            "Let curiosity lead",
            "Good ideas love quiet",
            "Make it feel inevitable",
            "Clarity over clever",
            "Practice makes patterns",
            "Confidence in draft mode",
            "Kindness is a force multiplier",
            "Your taste is a compass",
            "Stay human in the loop",
            "Protect your creative bandwidth",
            # Longer quotes to allow fuller, flowing readings
            "Some days are for quiet building: no fanfare, just you and the work, stacking tiny wins until momentum makes the announcement for you.",
            "If it looks effortless, it's because the effort was paid in advance—early mornings, kind patience, and a thousand little retries no one saw.",
            "You don't have to move fast; you just have to keep moving—curiosity will tow you across the boring parts and joy will meet you on the other side.",
            "When the plan gets noisy, listen for the signal: the small task you're avoiding that would make everything else easier or unnecessary.",
            "Make space for the thing you love to do badly—it's the sandbox where the brilliant version learns how to walk without pressure.",
            "You are allowed to take your time and still be incredible; speed is a metric, not a personality trait.",
            "Great work often looks like gentle work—clear boundaries, clean rest, and a focused hour repeated until it starts to look like magic.",
            "Your taste is not a burden; it's a compass. If something feels off, it probably is—pull the thread and trust what it reveals.",
            "Let it be fun again: reduce the surface area for friction, invite a little whimsy, and watch how quickly momentum forgives yesterday's stall.",
            "Sometimes the bravest move is a smaller scope—ship the kernel, learn, then let the next version become obvious.",
            "The best ideas show up dressed like jokes, hobbies, or detours; treat them kindly and they'll introduce you to something important.",
            "Don't make it harder than it needs to be—make it lighter than you expected, then carry it further than you thought you could.",
            "Be generous with your future self: leave notes, name things clearly, and commit messages like you're writing a short story they’ll enjoy rereading.",
            "Talent is surprisingly common; calm is not. Learn the quiet arts—attention, boundaries, recovery—and watch everything compound.",
            "You don't need permission to be excited about your own life. Build the small thing that makes you grin, then do it again tomorrow.",
            "There's a version of you beyond burnout that is playful, precise, and wildly effective—meet them by taking rest as seriously as ambition.",
            # Motivational punches (short)
            "Start before you feel ready",
            "Discipline is a love letter to your future self",
            "Your pace is still progress",
            "Tiny steps change big stories",
            "Consistency compounds quietly",
            "Focus turns minutes into momentum",
            "Be brave for ten seconds",
            "You can do hard things",
            "Show up, even small",
            "Future you is watching—impress them",
            "One page today, a chapter tomorrow",
            "Momentum starts with a single move",
            "Done is the door to better",
            "Practice makes patterns",
            "Direction beats speed",
            "Keep the promise you made to yourself",
            "Win the morning, win the day",
            "Hard now, easy later",
            "Little by little becomes a lot",
            "Turn pressure into presence",
            # Motivational longer entries
            "Courage isn’t the absence of fear; it’s the decision that the next step matters more than your comfort—take it, even if it’s small.",
            "What you repeat becomes who you are: keep the habits that make you proud and let the rest fall away without ceremony.",
            "You don’t need a perfect plan; you need a faithful rhythm—show up, adjust, repeat, and let consistency do its quiet magic.",
            "Doubt will always make a case; discipline doesn’t argue back—it just keeps moving, kindly and relentlessly.",
            "Greatness rarely looks glamorous up close—it looks like showing up on time, trying again, and being kinder than the situation requires.",
        ]
        
        import random
        return random.choice(quotes)

    def draw_coffee_scene(self):
        """Draw coffee scene with coffee reading fortune"""
        px = self.scale
        
        # Only show coffee reading if it's still visible
        if self.coffee_reading_visible:
            # Use the stored coffee reading for this session
            today_reading = self.current_coffee_reading
            
            # Reading text with dynamic wrap and font size for longer entries
            # Start higher up; adjust automatically based on number of lines
            base_y = self.height//2 - 80

            def wrap_words(text, max_chars):
                words = text.split()
                lines = []
                current = []
                for w in words:
                    current.append(w)
                    if len(' '.join(current)) > max_chars:
                        # move last word to next line
                        lines.append(' '.join(current[:-1]))
                        current = [w]
                if current:
                    lines.append(' '.join(current))
                return lines

            max_lines_allowed = 6
            chosen_font_size = 12
            chosen_lines = None
            # Try decreasing font size and increasing wrap width gently
            for fs in (12, 11, 10, 9, 8):
                # As font shrinks, allow a few more chars per line
                max_chars = 45 + (12 - fs) * 5  # 12->45, 11->50, 10->55, 9->60, 8->65
                candidate = wrap_words(today_reading, max_chars)
                if len(candidate) <= max_lines_allowed:
                    chosen_font_size = fs
                    chosen_lines = candidate
                    break
            if chosen_lines is None:
                # Still too long: hard cap lines and add ellipsis
                candidate = wrap_words(today_reading, 65)
                chosen_lines = candidate[:max_lines_allowed]
                if chosen_lines:
                    chosen_lines[-1] = chosen_lines[-1] + " ..."
                chosen_font_size = 8

            # Line spacing scales with font size (approx)
            line_spacing = 13 + chosen_font_size  # 25 at fs=12, 21 at fs=8
            reading_y = base_y

            for i, line in enumerate(chosen_lines):
                line_y = reading_y + (i * line_spacing)
                self.canvas.create_text((self.width//2)*px, line_y*px,
                                      text=line,
                                      fill="white",
                                      font=("Fixedsys", chosen_font_size, "normal"))
            
            # Decorative elements
            cup_y = reading_y + len(chosen_lines) * line_spacing + 30
            self.canvas.create_text((self.width//2)*px, cup_y*px,
                                  text="~ Today's Brew Brings Wisdom ~", 
                                  fill="white", 
                                  font=("Fixedsys", 10, "normal"))
            
            # Click instruction
            click_y = cup_y + 25
            self.canvas.create_text((self.width//2)*px, click_y*px,
                                  text="(Click anywhere to hide reading)", 
                                  fill="white", 
                                  font=("Fixedsys", 8, "normal"))
        
        # Instructions (always shown)
        instruction_y = self.height - 60
        self.canvas.create_text((self.width//2)*px, instruction_y*px,
                              text="Press ESC to return to the café", 
                              fill="white", 
                              font=("Fixedsys", 10, "normal"))

    # -------- To-Do List Methods --------
    def start_todo_list(self):
        """Start the simple to-do list overlay."""
        self.todo_list_active = True
        self.todo_selected_index = 0
        self.todo_editing = False
        self.todo_edit_text = ""
        
        # Button interaction state
        self.todo_button_hover = -1  # Which button is being hovered (-1 = none)
        self.todo_button_boxes = []  # Store button rectangles for hit detection
        
        # Input mode for adding new tasks
        self.todo_input_mode = False
        self.todo_input_text = ""
        
        # Load existing to-do items from file if available
        self.load_todo_items()
        
    def load_todo_items(self):
        """Load to-do items from persistent storage."""
        todo_save_file = os.path.join(ASSETS_DIR, 'todo_data.json')
        try:
            if os.path.exists(todo_save_file):
                with open(todo_save_file, 'r') as f:
                    data = json.load(f)
                    self.todo_items = data.get('items', [])
            else:
                # Default items for first run
                self.todo_items = [
                    {"text": "My first task", "completed": False},
                    {"text": "Another task", "completed": False},
                    {"text": "Completed task", "completed": True}
                ]
        except Exception as e:
            print(f"[WARN] Could not load to-do items: {e}")
            self.todo_items = [{"text": "Failed to load saved items", "completed": False, "details": ""}]
    
    def save_todo_items(self):
        """Save to-do items to persistent storage."""
        todo_save_file = os.path.join(ASSETS_DIR, 'todo_data.json')
        try:
            data = {'items': self.todo_items}
            with open(todo_save_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[WARN] Could not save to-do items: {e}")
    
    def add_todo_item(self, text):
        """Add a new to-do item."""
        if text.strip():
            new_item = {"text": text.strip(), "completed": False, "details": ""}
            self.todo_items.append(new_item)
            self.todo_selected_index = len(self.todo_items) - 1
            self.save_todo_items()
    
    def delete_todo_item(self, index):
        """Delete a to-do item by index."""
        if 0 <= index < len(self.todo_items):
            self.todo_items.pop(index)
            if self.todo_selected_index >= len(self.todo_items):
                self.todo_selected_index = max(0, len(self.todo_items) - 1)
            self.save_todo_items()
    
    def edit_todo_item(self, index, new_text):
        """Edit a to-do item's text."""
        if 0 <= index < len(self.todo_items) and new_text.strip():
            self.todo_items[index]["text"] = new_text.strip()
            self.save_todo_items()
    
    def edit_todo_details(self, index, new_details):
        """Edit a to-do item's details."""
        if 0 <= index < len(self.todo_items):
            self.todo_items[index]["details"] = new_details.strip()
            self.save_todo_items()
    
    def toggle_todo_completion(self, index):
        """Toggle a to-do item's completion status."""
        if 0 <= index < len(self.todo_items):
            self.todo_items[index]["completed"] = not self.todo_items[index]["completed"]
            self.save_todo_items()
    
    def load_calendar_events(self):
        """Load calendar events from persistent storage."""
        calendar_save_file = os.path.join(ASSETS_DIR, 'calendar_events.json')
        try:
            if os.path.exists(calendar_save_file):
                with open(calendar_save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.calendar_events = data.get('events', {})
            else:
                self.calendar_events = {}
        except Exception as e:
            print(f"[WARN] Failed to load calendar events: {e}")
            self.calendar_events = {}
    
    def save_calendar_events(self):
        """Save calendar events to persistent storage."""
        calendar_save_file = os.path.join(ASSETS_DIR, 'calendar_events.json')
        try:
            os.makedirs(ASSETS_DIR, exist_ok=True)
            data = {
                'events': self.calendar_events,
                'last_saved': datetime.now().isoformat()
            }
            with open(calendar_save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[WARN] Failed to save calendar events: {e}")
    
    def add_calendar_event(self, date_str, title, time="", description=""):
        """Add an event to a specific date."""
        if date_str not in self.calendar_events:
            self.calendar_events[date_str] = []
        
        event = {
            "title": title,
            "time": time,
            "description": description
        }
        self.calendar_events[date_str].append(event)
        self.save_calendar_events()
    
    def get_events_for_date(self, date_str):
        """Get all events for a specific date."""
        return self.calendar_events.get(date_str, [])
    
    def has_events_for_date(self, date_str):
        """Check if a date has any events."""
        return date_str in self.calendar_events and len(self.calendar_events[date_str]) > 0
    
    def draw_todo_list_overlay(self):
        """Draw simple menu-style to-do list overlay."""
        if not hasattr(self, 'todo_list_active') or not self.todo_list_active:
            return
            
        px = self.scale
        
        # Dark overlay background
        overlay_alpha = 200
        overlay = Image.new('RGBA', (self.width, self.height), (11, 11, 15, overlay_alpha))
        overlay_photo = self._to_photo(overlay)
        self.canvas.create_image(0, 0, anchor="nw", image=overlay_photo)
        self._frame_refs.append(overlay_photo)
        
        # Main panel - same style as other menus
        panel_w = 350
        panel_h = 450
        panel_x = (self.width - panel_w) // 2
        panel_y = (self.height - panel_h) // 2
        
        # Panel background - same as mood menu
        self.canvas.create_rectangle(panel_x*px, panel_y*px, 
                                     (panel_x + panel_w)*px, (panel_y + panel_h)*px,
                                     fill=MOOD_MENU_BG, outline=MOOD_MENU_BORDER, width=2)
        
        # Title
        title_text = "To-Do List"
        if USE_BLOCKY_FONT:
            title_width = self._get_blocky_text_width(title_text)
            title_x = panel_x + (panel_w - title_width) // 2
            self._draw_blocky_text(title_x, panel_y + 15, title_text, MOOD_MENU_TEXT_COLOR)
        else:
            self.canvas.create_text((panel_x + panel_w//2)*px, (panel_y + 20)*px,
                                    text=title_text, fill=MOOD_MENU_TEXT_COLOR,
                                    font=MOOD_MENU_FONT, anchor="n")
        
        # Task list area
        list_start_y = panel_y + 60
        max_visible = 8
        
        for i, item in enumerate(self.todo_items[:max_visible]):
            item_y = list_start_y + i * MOOD_MENU_ITEM_HEIGHT
            is_selected = (i == self.todo_selected_index)
            
            # Item background - same hover style as menus
            if is_selected:
                self.canvas.create_rectangle((panel_x + 10)*px, item_y*px,
                                             (panel_x + panel_w - 10)*px, (item_y + MOOD_MENU_ITEM_HEIGHT)*px,
                                             fill=MOOD_MENU_HOVER_BG, outline="")
                # Left accent bar
                self.canvas.create_rectangle((panel_x + 6)*px, item_y*px,
                                             (panel_x + 8)*px, (item_y + MOOD_MENU_ITEM_HEIGHT)*px,
                                             fill=MOOD_MENU_ACCENT, outline="")
            
            # Checkbox
            checkbox_x = panel_x + 20
            checkbox_y = item_y + 8
            checkbox_size = 12
            
            self.canvas.create_rectangle(checkbox_x*px, checkbox_y*px,
                                         (checkbox_x + checkbox_size)*px, (checkbox_y + checkbox_size)*px,
                                         outline=MOOD_MENU_TEXT_COLOR, width=1, fill="")
            
            if item.get('completed', False):
                # Checkmark
                self.canvas.create_line((checkbox_x + 2)*px, (checkbox_y + 6)*px,
                                        (checkbox_x + 5)*px, (checkbox_y + 9)*px,
                                        fill=MOOD_MENU_ACCENT, width=2)
                self.canvas.create_line((checkbox_x + 5)*px, (checkbox_y + 9)*px,
                                        (checkbox_x + 10)*px, (checkbox_y + 4)*px,
                                        fill=MOOD_MENU_ACCENT, width=2)
            
            # Task text
            text_x = checkbox_x + 20
            text_color = MOOD_MENU_HOVER_TEXT if is_selected else MOOD_MENU_TEXT_COLOR
            if item.get('completed', False):
                text_color = "#888888"
                
            # Show edit mode
            if is_selected and self.todo_editing:
                display_text = self.todo_edit_text + "_"
                text_color = MOOD_MENU_ACCENT
            else:
                display_text = item['text']
                if len(display_text) > 30:
                    display_text = display_text[:27] + "..."
            
            if USE_BLOCKY_FONT:
                self._draw_blocky_text(text_x, item_y + 8, display_text, text_color)
            else:
                self.canvas.create_text(text_x*px, (item_y + 12)*px,
                                        text=display_text, fill=text_color,
                                        font=MOOD_MENU_DESC_FONT, anchor="w")
        
        # Action buttons at bottom
        button_y = panel_y + panel_h - 80
        button_width = 80
        button_height = 25
        button_spacing = 10
        
        buttons = ["Add New", "Edit", "Delete", "Toggle"]
        total_width = len(buttons) * button_width + (len(buttons) - 1) * button_spacing
        start_x = panel_x + (panel_w - total_width) // 2
        
        # Clear button boxes for hit detection
        self.todo_button_boxes = []
        
        for i, button_text in enumerate(buttons):
            btn_x = start_x + i * (button_width + button_spacing)
            
            # Store button rectangle for hit detection
            self.todo_button_boxes.append((btn_x, button_y, btn_x + button_width, button_y + button_height))
            
            # Button background with hover effect
            is_hovered = (i == self.todo_button_hover)
            bg_color = MOOD_MENU_ACCENT if is_hovered else MOOD_MENU_HOVER_BG
            text_color = MOOD_MENU_BG if is_hovered else MOOD_MENU_TEXT_COLOR
            
            self.canvas.create_rectangle(btn_x*px, button_y*px,
                                         (btn_x + button_width)*px, (button_y + button_height)*px,
                                         fill=bg_color, outline=MOOD_MENU_BORDER, width=1)
            
            # Button text
            self.canvas.create_text((btn_x + button_width//2)*px, (button_y + button_height//2)*px,
                                    text=button_text, fill=text_color,
                                    font=("Courier New", 8), anchor="center")
        
        # Show input overlay if in input mode
        if self.todo_input_mode:
            input_y = panel_y + panel_h - 130
            self.canvas.create_rectangle((panel_x + 10)*px, input_y*px,
                                         (panel_x + panel_w - 10)*px, (input_y + 30)*px,
                                         fill="#1a1a2e", outline=MOOD_MENU_ACCENT, width=2)
            
            self.canvas.create_text((panel_x + 15)*px, (input_y + 15)*px,
                                   text=f"New task: {self.todo_input_text}_", fill=MOOD_MENU_TEXT_COLOR,
                                   font=("Courier New", 10), anchor="w")
        
        # Instructions
        inst_y = panel_y + panel_h - 40
        if self.todo_input_mode:
            instructions = "Type task name  ENTER Save  ESC Cancel"
        elif self.todo_editing:
            instructions = "Type new name  ENTER Save  ESC Cancel"
        else:
            instructions = "WS Navigate  Click buttons  E Edit  ESC Exit"
        self.canvas.create_text((panel_x + panel_w//2)*px, inst_y*px,
                                text=instructions, fill=MOOD_MENU_TEXT_COLOR,
                                font=("Courier New", 8), anchor="center")

    # -------- Fireplace Methods --------
    def toggle_fireplace(self):
        """Start or stop the fireplace sound and switch to fireplace scene with transition."""
        if not self.fireplace_loaded:
            print("[WARN] Fireplace sound not loaded")
            return
            
        if self.fireplace_playing:
            # Stop fireplace and return to inside scene with transition
            if self.fireplace_channel:
                self.fireplace_channel.stop()
                self.fireplace_channel = None
            self.fireplace_playing = False
            # Use proper fade transition back to inside scene
            self.scene.trigger_fade_from_fireplace()
            print("[INFO] Fireplace stopped, transitioning back to inside")
        else:
            # Start fireplace sound and trigger transition to fireplace scene
            try:
                self.fireplace_channel = self.fireplace_sound.play(loops=-1)
                self.fireplace_playing = True
                # Hide menus when transitioning to fireplace scene
                self.cozy_submenu_active = False
                self.menu_active = False
                # Trigger smooth transition to fireplace scene
                self.scene.trigger_fade_to_fireplace()
                print("[INFO] Fireplace started, transitioning to fireplace scene")
            except Exception as e:
                print(f"[WARN] Could not start fireplace: {e}")

    def _choose_pixel_font(self):
        try:
            available = set(tkfont.families())
            for fam in PIXEL_FONT_CANDIDATES:
                if fam in available:
                    return fam
        except Exception:
            pass
        return 'Courier New'
        
        # iPod dimensions and position (center of screen)
        ipod_w = IPOD_WIDTH
        ipod_h = IPOD_HEIGHT
        ipod_x = (self.width - ipod_w) // 2
        ipod_y = (self.height - ipod_h) // 2
        
        # iPod body background
        self.canvas.create_rectangle(ipod_x*px, ipod_y*px, 
                                   (ipod_x + ipod_w)*px, (ipod_y + ipod_h)*px,
                                   fill=IPOD_BG_COLOR, outline="black", width=2)
        
        # Screen area - improved margins and sizing
        screen_margin = 20  # Increased margin
        screen_x = ipod_x + screen_margin
        screen_y = ipod_y + screen_margin + 5  # Slight vertical offset
        screen_w = ipod_w - 2*screen_margin
        screen_h = (ipod_h//2) - screen_margin - 10  # More conservative height
        
        # Create clipping rectangle for screen content
        self.canvas.create_rectangle(screen_x*px, screen_y*px,
                                   (screen_x + screen_w)*px, (screen_y + screen_h)*px,
                                   fill=IPOD_SCREEN_COLOR, outline="black", width=1)
        
        # Current screen content - with proper bounds checking
        if self.ipod_player.current_screen == "main":
            self.draw_ipod_main_screen(screen_x, screen_y, screen_w, screen_h, px)
        elif self.ipod_player.current_screen == "playlist":
            self.draw_ipod_playlist_screen(screen_x, screen_y, screen_w, screen_h, px)
        
        # Control wheel area
        wheel_y = ipod_y + ipod_h//2 + 10
        wheel_size = 80
        wheel_x = ipod_x + (ipod_w - wheel_size)//2
        
        # Outer wheel
        self.canvas.create_oval(wheel_x*px, wheel_y*px,
                              (wheel_x + wheel_size)*px, (wheel_y + wheel_size)*px,
                              fill="#e0e0e0", outline="black", width=2)
        
        # Inner button
        button_size = 30
        button_x = wheel_x + (wheel_size - button_size)//2
        button_y = wheel_y + (wheel_size - button_size)//2
        
        self.canvas.create_oval(button_x*px, button_y*px,
                              (button_x + button_size)*px, (button_y + button_size)*px,
                              fill="white", outline="black")
        
        # Control labels
        self.canvas.create_text((wheel_x + wheel_size//2)*px, (wheel_y - 5)*px,
                              text="MENU", fill=IPOD_TEXT_COLOR, font=("Arial", 8), anchor="s")
        self.canvas.create_text((wheel_x + wheel_size + 5)*px, (wheel_y + wheel_size//2)*px,
                              text=">>", fill=IPOD_TEXT_COLOR, font=("Arial", 8), anchor="w")
        self.canvas.create_text((wheel_x + wheel_size//2)*px, (wheel_y + wheel_size + 5)*px,
                              text="PLAY", fill=IPOD_TEXT_COLOR, font=("Arial", 8), anchor="n")
        self.canvas.create_text((wheel_x - 5)*px, (wheel_y + wheel_size//2)*px,
                              text="<<", fill=IPOD_TEXT_COLOR, font=("Arial", 8), anchor="e")
        
        # Exit instruction
        exit_text = "Press ESC to close iPod"
        self.canvas.create_text((ipod_x + ipod_w//2)*px, (ipod_y + ipod_h + 20)*px,
                              text=exit_text, fill=IPOD_TEXT_COLOR,
                              font=("Arial", 10), anchor="n")
    
    def draw_ipod_main_screen(self, x, y, w, h, px):
        """Draw the main iPod screen"""
        # Title - ensure it fits within bounds
        title_y = y + 8
        if title_y > y + h - 10:  # Leave bottom margin
            return
            
        self.canvas.create_text((x + w//2)*px, title_y*px,
                              text="iPod", fill=IPOD_TEXT_COLOR,
                              font=("Arial", 10, "bold"), anchor="n")
        
        # Current song info
        song_y = y + 25
        if song_y < y + h - 15:
            current_song = self.ipod_player.get_current_song_name()
            if current_song != "No song selected":
                # Truncate based on screen width
                max_chars = max(15, w // 8)  # Estimate chars that fit
                if len(current_song) > max_chars:
                    current_song = current_song[:max_chars-3] + "..."
                    
            self.canvas.create_text((x + w//2)*px, song_y*px,
                                  text=f"♪ {current_song}", fill=IPOD_TEXT_COLOR,
                                  font=("Arial", 8), anchor="n")
        
        # Status
        status_y = y + 38
        if status_y < y + h - 10:
            status = "Playing" if self.ipod_player.is_playing else "Paused" if self.ipod_player.is_paused else "Stopped"
            self.canvas.create_text((x + w//2)*px, status_y*px,
                                  text=status, fill=IPOD_ACCENT_COLOR,
                                  font=("Arial", 7), anchor="n")
        
        # Menu options - only show if there's space
        options = ["Add Music Files", "Current Playlist", f"Vol: {int(self.ipod_player.volume*100)}%"]
        for i, option in enumerate(options):
            option_y = y + 55 + i*12
            if option_y > y + h - 8:  # Stop if we're running out of space
                break
            color = IPOD_ACCENT_COLOR if i == self.ipod_player.selected_index else IPOD_TEXT_COLOR
            self.canvas.create_text((x + 3)*px, option_y*px,
                                  text=f"• {option}", fill=color,
                                  font=("Arial", 7), anchor="nw")
    
    def draw_ipod_playlist_screen(self, x, y, w, h, px):
        """Draw the playlist screen"""
        self.canvas.create_text((x + w//2)*px, (y + 10)*px,
                              text="Playlist", fill=IPOD_TEXT_COLOR,
                              font=("Arial", 12, "bold"), anchor="n")
        
        if not self.ipod_player.playlist:
            self.canvas.create_text((x + w//2)*px, (y + h//2)*px,
                                  text="No songs in playlist", fill=IPOD_TEXT_COLOR,
                                  font=("Arial", 9), anchor="center")
            return
        
        # Show playlist items
        visible_items = 8
        start_idx = self.ipod_player.scroll_offset
        
        for i in range(visible_items):
            playlist_idx = start_idx + i
            if playlist_idx >= len(self.ipod_player.playlist):
                break
                
            song_path = self.ipod_player.playlist[playlist_idx]
            song_name = os.path.basename(song_path)
            
            # Truncate long names
            if len(song_name) > 20:
                song_name = song_name[:17] + "..."
            
            item_y = y + 25 + i*12
            is_current = playlist_idx == self.ipod_player.current_song_index
            is_selected = playlist_idx == (start_idx + self.ipod_player.selected_index)
            
            color = IPOD_ACCENT_COLOR if is_selected else IPOD_TEXT_COLOR
            prefix = "► " if is_current else "  "
            
            self.canvas.create_text((x + 5)*px, item_y*px,
                                  text=f"{prefix}{song_name}", fill=color,
                                  font=("Arial", 8), anchor="nw")
    
    def draw_ipod_browse_screen(self, x, y, w, h, px):
        """Draw the browse files screen"""
        self.canvas.create_text((x + w//2)*px, (y + 10)*px,
                              text="Browse Music", fill=IPOD_TEXT_COLOR,
                              font=("Arial", 12, "bold"), anchor="n")
        
        # Show current directory (truncated)
        current_dir = self.ipod_player.current_directory
        if len(current_dir) > 25:
            display_dir = "..." + current_dir[-22:]
        else:
            display_dir = current_dir
            
        self.canvas.create_text((x + w//2)*px, (y + 25)*px,
                              text=display_dir, fill=IPOD_TEXT_COLOR,
                              font=("Arial", 8), anchor="n")
        
        if not self.ipod_player.directory_contents:
            self.canvas.create_text((x + w//2)*px, (y + h//2)*px,
                                  text="No files found", fill=IPOD_TEXT_COLOR,
                                  font=("Arial", 9), anchor="center")
            return
        
        # Show directory contents
        visible_items = 6
        start_idx = self.ipod_player.browse_scroll_offset
        
        for i in range(visible_items):
            content_idx = start_idx + i
            if content_idx >= len(self.ipod_player.directory_contents):
                break
                
            item_name, item_type, item_path = self.ipod_player.directory_contents[content_idx]
            
            # Truncate long names
            display_name = item_name
            if len(display_name) > 18:
                display_name = display_name[:15] + "..."
            
            item_y = y + 40 + i*12
            is_selected = content_idx == (start_idx + self.ipod_player.selected_index)
            
            color = IPOD_ACCENT_COLOR if is_selected else IPOD_TEXT_COLOR
            
            # Icon based on type
            if item_type == "folder":
                icon = "📁 "
            elif item_type == "music":
                icon = "🎵 "
            else:
                icon = "  "
            
            self.canvas.create_text((x + 5)*px, item_y*px,
                                  text=f"{icon}{display_name}", fill=color,
                                  font=("Arial", 8), anchor="nw")
    def _choose_pixel_font(self):
        try:
            available = set(tkfont.families())
            for fam in PIXEL_FONT_CANDIDATES:
                if fam in available:
                    return fam
        except Exception:
            pass
        return 'Courier New'

    def open_note_window(self):
        if hasattr(self, 'note_win') and self.note_win and tk.Toplevel.winfo_exists(self.note_win):
            self.note_win.lift()
            return
        
        # Initialize notebook data if not exists
        if not hasattr(self, 'notebook_pages'):
            self.load_notebook_data()
        
        win = tk.Toplevel(self.root)
        win.title("� Café Journal")
        win.configure(bg="#2d251a")
        w, h = NOTEBOOK_WIDTH, NOTEBOOK_HEIGHT
        win.geometry(f"{w}x{h}")
        win.resizable(False, False)  # Fixed size for consistent layout
        
        # Add window icon styling
        try:
            win.iconbitmap(default=LEAF_IMAGE) if os.path.isfile(LEAF_IMAGE) else None
        except:
            pass
        
        # Main frame
        main_frame = tk.Frame(win, bg="#2d251a")
        main_frame.pack(fill='both', expand=True)
        
        # Canvas for warm café notebook aesthetic
        cv = tk.Canvas(main_frame, width=w, height=h-50, bg="#f4f1ea", highlightthickness=0)
        cv.pack(fill='both', expand=True)
        
        # --- Background parchment texture (simple procedural speckles) ---
        import random as _r
        for _ in range(140):
            sx = _r.randint(8, w-30)
            sy = _r.randint(8, h-90)
            radius = _r.randint(1, 2)
            shade = _r.randint(228, 240)
            color = f"#{shade:02x}{(shade-6):02x}{(shade-10):02x}"
            cv.create_oval(sx, sy, sx+radius, sy+radius, fill=color, outline="")
        
        # --- Subtle coffee ring stain ---
        ring_cx, ring_cy, ring_r = w-190, 120, 54
        for i in range(5):
            alpha_shift = 0x80 + i*8
            col = f"#{170+i*6:02x}{130+i*5:02x}{90+i*4:02x}"
            cv.create_oval(ring_cx-ring_r-i, ring_cy-ring_r-i, ring_cx+ring_r+i, ring_cy+ring_r+i,
                           outline=col, width=1)
        # inner gap erase effect
        cv.create_oval(ring_cx-ring_r+10, ring_cy-ring_r+10, ring_cx+ring_r-10, ring_cy+ring_r-10,
                       outline="", fill="#f4f1ea")
        
        # --- Page corner fold (top-right) ---
        fold_size = 46
        cv.create_polygon(w-4-fold_size, 4, w-4, 4, w-4, 4+fold_size, fill="#efe7dc", outline="#c8b8a0")
        cv.create_line(w-4-fold_size, 4, w-4, 4+fold_size, fill="#d6c7b4")
        cv.create_line(w-4-fold_size+3, 4, w-4, 4+fold_size-3, fill="#fffaf2")
        
        # Button frame at bottom with warm café styling
        btn_frame = tk.Frame(main_frame, bg="#8b7355", height=50, relief='flat', bd=0)
        btn_frame.pack(fill='x', side='bottom')
        btn_frame.pack_propagate(False)
        
        # Add subtle coffee-colored accent strip
        accent_strip = tk.Frame(btn_frame, bg="#d4a574", height=3)
        accent_strip.pack(fill='x', side='top')
        
        # Enhanced pixel notebook embellishments with warm café styling
        # Subtle outer shadow
        cv.create_rectangle(2, 2, w-2, h-52, fill="#e8e1d6", outline="")
        # Main warm borders
        cv.create_rectangle(4, 4, w-4, h-54, outline="#8b7355", width=3)
        cv.create_rectangle(0, 0, w, h-50, outline="#5d4e36", width=2)
        
        # Warm coffee-colored left margin (thicker) with stitched accent
        cv.create_line(88, 10, 88, h-60, fill="#d4a574", width=5)
        cv.create_line(93, 10, 93, h-60, fill="#b8894a", width=2)
        for ly in range(18, h-70, 26):
            cv.create_line(90, ly, 91, ly+8, fill="#8b7355", width=1)
        
        # Soft horizontal ruled lines (alternating warmth)
        for i, ly in enumerate(range(45, h-75, 24)):
            tone_a = "#ede3d6"
            tone_b = "#e5d8c8"
            base = tone_a if i % 2 == 0 else tone_b
            cv.create_line(20, ly, w-20, ly, fill=base, width=1)
        
        # Warm café-style punched holes
        hole_spacing = 36
        for idx, sy in enumerate(range(60, h-105, hole_spacing)):
            cv.create_oval(26, sy-2, 52, sy+24, fill="#d8cdb8", outline="")
            cv.create_oval(28, sy, 50, sy+22, fill="#f4f1ea", outline="#8b7355", width=3)
            cv.create_oval(32, sy+4, 46, sy+18, outline="#c29552", width=2)
            cv.create_oval(36, sy+8, 42, sy+14, fill="#f8f5ee", outline="#d4a574", width=1)
        
        # Warm right edge layered shadow
        for i in range(6):
            shade_val = 235 - i*8
            shade_color = f"#{shade_val:02x}{shade_val-5:02x}{shade_val-15:02x}"
            cv.create_rectangle(w-16+i, 16, w-15+i, h-65, fill=shade_color, outline="")
        
        # Enhanced top tab with café styling + brackets
        cv.create_rectangle(100, 16, w-50, 42, fill="#f8f5ee", outline="")
        cv.create_rectangle(100, 16, w-50, 18, fill="#fff9f0", outline="")
        cv.create_rectangle(100, 40, w-50, 42, fill="#e8ddd0", outline="")
        cv.create_rectangle(100, 16, 102, 42, fill="#fff9f0", outline="")
        cv.create_rectangle(w-52, 16, w-50, 42, fill="#ddd0c1", outline="")
        cv.create_rectangle(100, 16, w-50, 42, outline="#c29552", width=2)
        
        # Use blocky font for enhanced header with pixel brackets
        if USE_BLOCKY_FONT:
            header_text = "JOURNAL"
            deco_left = "["
            deco_right = "]"
            full_header = f"{deco_left}{header_text}{deco_right}"
            header_x = 100 + (w-50-100)//2 - self._get_blocky_text_width(full_header)//2
            self._draw_blocky_text_on_canvas(cv, header_x, 22, full_header, "#8b7355")
        else:
            cv.create_text((100+(w-50-100)/2), 29, text="[JOURNAL]", fill="#8b7355", 
                          font=("Courier New", 12, "bold"))
        
        # Watermark (coffee bean pixel cluster bottom-right)
        bean_base_x, bean_base_y = w-140, h-130
        for dx, dy, col in [
            (0,0,"#5a3a24"),(1,0,"#6b442a"),(2,0,"#6b442a"),(3,0,"#5a3a24"),
            (0,1,"#6b442a"),(1,1,"#835636"),(2,1,"#835636"),(3,1,"#6b442a"),
            (0,2,"#6b442a"),(1,2,"#835636"),(2,2,"#835636"),(3,2,"#6b442a"),
            (0,3,"#5a3a24"),(1,3,"#6b442a"),(2,3,"#6b442a"),(3,3,"#5a3a24")]:
            cv.create_rectangle(bean_base_x+dx, bean_base_y+dy, bean_base_x+dx+1, bean_base_y+dy+1, fill=col, outline="")
        
        # page number with café styling (unchanged logic)
        page_text = f"Page {self.current_page + 1}"
        if USE_BLOCKY_FONT:
            page_x = w - 80 - self._get_blocky_text_width(page_text)//2
            self._draw_blocky_text_on_canvas(cv, page_x, h-75, page_text, "#c29552")
        else:
            cv.create_text(w-65, h-75, text=page_text, fill="#c29552", 
                          font=("Courier New", 10, "bold"))
        
        # Enhanced text widget with warm café styling and character + word counter
        txt_bg = "#faf8f2"
        txt_fg = "#3d2f1f"
        txt = tk.Text(cv, wrap='word', bg=txt_bg, fg=txt_fg, insertbackground="#c29552", 
                     relief='flat', font=(self.pixel_font_family, PIXEL_FONT_SIZE),
                     selectbackground="#d4a574", selectforeground="#ffffff",
                     padx=12, pady=12, spacing1=2, spacing2=1, spacing3=2,
                     highlightthickness=0)
        txt.place(x=108, y=52, width=w-150, height=h-155)
        cv.create_rectangle(106, 50, w-40, h-100, fill="#e8ddd0", outline="")
        cv.create_rectangle(107, 51, w-41, h-101, outline="#c29552", width=2)
        
        # Counters frame
        counters_frame = tk.Frame(cv, bg="#f4f1ea")
        counters_frame.place(x=20, y=h-110)
        char_count_label = tk.Label(counters_frame, text="Chars: 0", bg="#f4f1ea", fg="#8b7355", font=("Courier New", 9, "bold"))
        char_count_label.pack(anchor='w')
        word_count_label = tk.Label(counters_frame, text="Words: 0", bg="#f4f1ea", fg="#8b7355", font=("Courier New", 9, "bold"))
        word_count_label.pack(anchor='w')
        
        # Load current page content and update counters
        if self.current_page < len(self.notebook_pages):
            txt.delete('1.0', 'end')
            txt.insert('1.0', self.notebook_pages[self.current_page])
            content = self.notebook_pages[self.current_page]
            char_count_label.config(text=f"Chars: {len(content)}")
            word_count_label.config(text=f"Words: {len(content.split()) if content.strip() else 0}")
        
        def save_page(event=None):
            content = txt.get('1.0', 'end-1c')
            if self.current_page < len(self.notebook_pages):
                self.notebook_pages[self.current_page] = content
                self.save_notebook_data()
            char_count = len(content)
            word_count = len(content.split()) if content.strip() else 0
            char_count_label.config(text=f"Chars: {char_count}")
            word_count_label.config(text=f"Words: {word_count}")
        
        txt.bind('<KeyRelease>', save_page)
        txt.bind('<Button-1>', save_page)
        
        # Bind typing sound remains unchanged
        if self.typing_sound_loaded:
            def _on_keypress(evt):
                now = time.time()
                if now - self.last_typing_sound_time >= TYPING_SOUND_COOLDOWN:
                    self.last_typing_sound_time = now
                    try:
                        self.typing_sound.play()
                    except Exception:
                        pass
            txt.bind('<Key>', _on_keypress)
        
        # Navigation buttons function definitions remain below unchanged
        def create_pixel_button(parent, text, command, bg_color="#3d3d3d", text_color="#ffffff", width=80, height=32):
            # Create a frame to hold the custom button
            btn_frame = tk.Frame(parent, bg=parent.cget('bg'))
            
            # Create canvas for custom button rendering
            btn_canvas = tk.Canvas(btn_frame, width=width, height=height, highlightthickness=0, bd=0, bg=parent.cget('bg'))
            btn_canvas.pack()
            
            # Button state tracking
            button_state = {'hovered': False, 'pressed': False}
            
            def draw_button():
                btn_canvas.delete('all')
                
                # Choose colors based on state
                if button_state['pressed']:
                    bg = "#6b5d42"
                    border_light = "#5a4d32"
                    border_dark = "#d4a574"
                    text_offset = 1
                elif button_state['hovered']:
                    bg = "#a08660"
                    border_light = "#c29552"
                    border_dark = "#6b5d42"
                    text_offset = 0
                else:
                    bg = bg_color
                    border_light = "#c29552"
                    border_dark = "#6b5d42"
                    text_offset = 0
                
                # Draw 3D button effect
                # Main button body
                btn_canvas.create_rectangle(2, 2, width-2, height-2, fill=bg, outline="")
                
                # Light borders (top and left)
                btn_canvas.create_line(2, 2, width-2, 2, fill=border_light, width=2)  # top
                btn_canvas.create_line(2, 2, 2, height-2, fill=border_light, width=2)  # left
                
                # Dark borders (bottom and right)
                btn_canvas.create_line(2, height-2, width-2, height-2, fill=border_dark, width=2)  # bottom
                btn_canvas.create_line(width-2, 2, width-2, height-2, fill=border_dark, width=2)  # right
                
                # Outer frame with warm café styling
                btn_canvas.create_rectangle(0, 0, width, height, outline="#8b7355", width=2)
                btn_canvas.create_rectangle(1, 1, width-1, height-1, outline="#c29552", width=1)
                
                # Text with blocky font if enabled
                text_x = width // 2 + text_offset
                text_y = height // 2 - 3 + text_offset
                
                if USE_BLOCKY_FONT and hasattr(self, '_draw_blocky_text_on_canvas'):
                    # Calculate text position for centering
                    text_width = self._get_blocky_text_width(text)
                    text_x = (width - text_width) // 2 + text_offset
                    text_y = (height - 7) // 2 + text_offset
                    self._draw_blocky_text_on_canvas(btn_canvas, text_x, text_y, text, text_color)
                else:
                    btn_canvas.create_text(text_x, text_y, text=text, fill=text_color, 
                                         font=("Courier New", 9, "bold"))
            
            def on_enter(event):
                button_state['hovered'] = True
                draw_button()
            
            def on_leave(event):
                button_state['hovered'] = False
                button_state['pressed'] = False
                draw_button()
            
            def on_press(event):
                button_state['pressed'] = True
                draw_button()
            
            def on_release(event):
                if button_state['hovered']:
                    command()
                button_state['pressed'] = False
                draw_button()
            
            # Bind events
            btn_canvas.bind('<Enter>', on_enter)
            btn_canvas.bind('<Leave>', on_leave)
            btn_canvas.bind('<Button-1>', on_press)
            btn_canvas.bind('<ButtonRelease-1>', on_release)
            
            # Initial draw
            draw_button()
            
            return btn_frame
        
        def prev_page():
            save_page()
            if self.current_page > 0:
                self.play_page_flip()
                self.current_page -= 1
                win.destroy()
                self.note_win = None
                self.open_note_window()
        
        def next_page():
            save_page()
            if self.current_page < len(self.notebook_pages) - 1:
                self.play_page_flip()
                self.current_page += 1
            else:
                # Add new page
                self.play_page_flip()
                self.notebook_pages.append("")
                self.current_page += 1
            win.destroy()
            self.note_win = None
            self.open_note_window()
        
        def add_page():
            save_page()
            self.play_page_flip()
            self.notebook_pages.append("")
            self.current_page = len(self.notebook_pages) - 1
            win.destroy()
            self.note_win = None
            self.open_note_window()
        
        def close_notebook():
            save_page()
            win.destroy()
            self.note_win = None
        
        def go_back_to_scene():
            save_page()
            win.destroy()
            self.note_win = None
            # Return to inside scene and re-show mood question
            # 1. If we were in focused scene, switch back to inside
            if self.scene.state == SceneManager.STATE_FOCUSED:
                self.scene.state = SceneManager.STATE_INSIDE
            # 2. Reset mood selection so activation condition in draw() triggers again
            self.menu_selected_index = -1
            self.menu_active = False  # will be re-activated automatically in draw()
            self.cozy_music_button = None
        
        # Button layout with improved spacing and organization
        btn_frame.grid_columnconfigure(0, weight=1)  # Left spacer
        btn_frame.grid_columnconfigure(6, weight=1)  # Right spacer
        
        # Create warm café-styled buttons
        prev_btn = create_pixel_button(btn_frame, "◄ PREV", prev_page, "#8b7355", "#f4f1ea", 80, 35)
        prev_btn.grid(row=0, column=1, padx=6, pady=7)
        
        add_btn = create_pixel_button(btn_frame, "+ PAGE", add_page, "#9d8a6b", "#fff9f0", 80, 35)
        add_btn.grid(row=0, column=2, padx=6, pady=7)
        
        next_btn = create_pixel_button(btn_frame, "NEXT ►", next_page, "#8b7355", "#f4f1ea", 80, 35)
        next_btn.grid(row=0, column=3, padx=6, pady=7)
        
        # Add back to scene button (more visible)
        back_btn = create_pixel_button(btn_frame, "◄ BACK", go_back_to_scene, "#6b5d42", "#d4a574", 80, 35)
        back_btn.grid(row=0, column=4, padx=6, pady=7)
        
        # Add close button
        close_btn = create_pixel_button(btn_frame, "✕ CLOSE", close_notebook, "#7a5a3a", "#f0c090", 80, 35)
        close_btn.grid(row=0, column=5, padx=6, pady=7)
        
        # Enable/disable buttons based on page position
        if self.current_page == 0:
            # Disable prev button by making it look inactive
            prev_btn.destroy()
            prev_btn = create_pixel_button(btn_frame, "◄ PREV", lambda: None, "#5a4d32", "#a0907a", 80, 35)
            prev_btn.grid(row=0, column=1, padx=6, pady=7)
        
        self.note_win = win
        self.note_text_widget = txt
    
    def _draw_blocky_text_on_canvas(self, canvas, x, y, text, color):
        """Draw blocky text directly on a tkinter canvas (for notebook headers)."""
        if not USE_BLOCKY_FONT:
            return
            
        char_width = 5 * BLOCKY_FONT_SCALE + BLOCKY_FONT_SPACING
        char_height = 7 * BLOCKY_FONT_SCALE
        
        for i, char in enumerate(text):
            bitmap = self._blocky_font_char_bitmap(char)
            char_x = x + i * char_width
            
            # Draw character pixels
            for row_idx, row in enumerate(bitmap):
                for col_idx, pixel in enumerate(row):
                    if pixel == '1':
                        pixel_x = char_x + col_idx * BLOCKY_FONT_SCALE
                        pixel_y = y + row_idx * BLOCKY_FONT_SCALE
                        canvas.create_rectangle(
                            pixel_x, pixel_y,
                            pixel_x + BLOCKY_FONT_SCALE,
                            pixel_y + BLOCKY_FONT_SCALE,
                            fill=color, outline=""
                        )

    def open_calendar_window(self):
        print("[DEBUG] Calendar window opening...")  # Debug print
        # Check if calendar window already exists
        if hasattr(self, 'cal_win') and self.cal_win:
            try:
                if self.cal_win.winfo_exists():
                    print("[DEBUG] Calendar window already exists, bringing to front")
                    self.cal_win.lift()
                    self.cal_win.attributes('-topmost', True)
                    self.cal_win.after(1000, lambda: self.cal_win.attributes('-topmost', False))
                    return
            except tk.TclError:
                # Window was destroyed, proceed to create new one
                print("[DEBUG] Previous calendar window was destroyed, creating new one")
                pass
        win = tk.Toplevel(self.root)
        win.title("Enhanced Calendar")
        win.configure(bg="#0c0c0c")
        
        # Calculate window size
        cell_w, cell_h = 70, 55  # Larger cells for better event display
        pad = 15
        width = cell_w*7 + pad*2
        height = cell_h*7 + 110  # More space for enhanced header
        
        # Simple positioning - start at top-left and let user move if needed
        win.geometry(f"{width}x{height}+100+100")
        win.resizable(True, True)  # Allow resizing to fix if window gets stuck
        win.lift()  # Bring to front
        win.attributes('-topmost', True)  # Keep on top temporarily
        
        # Remove topmost after a delay and print debug info
        def remove_topmost():
            try:
                win.attributes('-topmost', False)
                print(f"[DEBUG] Calendar window opened at size {width}x{height}")
            except:
                pass
        win.after(2000, remove_topmost)  # Keep on top for 2 seconds
        cv = tk.Canvas(win, width=width, height=height, bg="#0c0c0c", highlightthickness=0)
        cv.pack(fill='both', expand=True)
        now = datetime.now()
        year, month = now.year, now.month
        
        # Enhanced header with gradient effect
        header_text = now.strftime("%B %Y").upper()
        cv.create_rectangle(0,0,width,75, fill="#d3031c", outline="")  # Main header
        cv.create_rectangle(0,0,width,15, fill="#ff4444", outline="")  # Top gradient
        cv.create_text(width//2, 15, text=header_text, fill="#ffffff", font=("Courier New", 18, 'bold'), anchor='n')
        cv.create_text(width//2, 45, text="📅 CLICK ANY DAY TO ADD EVENTS", fill="#fffbe6", font=("Courier New", 10, 'bold'))
        cv.create_text(width//2, 62, text="Events are saved automatically", fill="#cccccc", font=("Courier New", 8))
        
        # Weekday labels with background
        weekdays = ['MON','TUE','WED','THU','FRI','SAT','SUN']
        for i, wd in enumerate(weekdays):
            x_pos = pad + cell_w*i + cell_w/2
            cv.create_rectangle(pad + cell_w*i, 82, pad + cell_w*i + cell_w, 102, fill="#262626", outline="#666")
            cv.create_text(x_pos, 92, text=wd, fill="#ffffff", font=("Courier New", 9, 'bold'))
        # Enhanced calendar grid generation (Monday=0)
        month_cal = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
        start_y = 110  # Adjusted for enhanced header
        today_day = now.day
        
        # Store day positions for click detection
        day_positions = {}
        
        for row_idx, week in enumerate(month_cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue
                x = pad + col_idx * cell_w
                y = start_y + row_idx * cell_h
                
                # Create date string for events
                date_str = f"{year}-{month:02d}-{day:02d}"
                events = self.get_events_for_date(date_str)
                event_count = len(events)
                
                # Store position for click detection
                day_positions[day] = (x, y, x+cell_w-2, y+cell_h-2, date_str)
                
                # Enhanced cell appearance
                is_today = (day == today_day)
                is_weekend = (col_idx >= 5)
                has_events = (event_count > 0)
                
                # Base colors
                if is_today:
                    base_color = "#ffec00"
                    text_color = "#000000"
                    border_color = "#ff8800"
                elif has_events:
                    base_color = "#2a5298"  # Blue for events
                    text_color = "#ffffff"
                    border_color = "#4477cc"
                elif is_weekend:
                    base_color = "#1a1a1a"
                    text_color = "#cccccc"
                    border_color = "#444444"
                else:
                    base_color = "#262626"
                    text_color = "#ffffff"
                    border_color = "#666666"
                
                # Draw cell shadow
                cv.create_rectangle(x+3, y+3, x+cell_w+1, y+cell_h+1, fill="#000000", outline="")
                
                # Draw main cell
                cv.create_rectangle(x, y, x+cell_w-2, y+cell_h-2, fill=base_color, outline=border_color, width=2)
                
                # Draw day number
                cv.create_text(x+cell_w/2, y+12, text=str(day), fill=text_color, 
                               font=("Courier New", 14, 'bold'), anchor='n')
                
                # Event indicators
                if has_events:
                    # Event count badge
                    badge_x = x + cell_w - 15
                    badge_y = y + 5
                    cv.create_oval(badge_x-8, badge_y-6, badge_x+8, badge_y+6, 
                                   fill="#d3031c", outline="#ffffff", width=1)
                    cv.create_text(badge_x, badge_y, text=str(event_count), 
                                   fill="#ffffff", font=("Courier New", 8, 'bold'))
                    
                    # Show first event preview (if space allows)
                    if event_count > 0:
                        first_event = events[0]
                        preview_text = first_event.get('title', '')
                        if len(preview_text) > 8:
                            preview_text = preview_text[:6] + "..."
                        
                        # Event preview text
                        cv.create_text(x+cell_w/2, y+cell_h-8, text=preview_text, 
                                       fill="#ffffcc", font=("Courier New", 7), anchor='s')
                
                # Hover effect preparation (will be added via bind)
                def create_hover_handler(day_num, x_pos, y_pos, events_list):
                    def on_enter(event):
                        if events_list:
                            # Show tooltip with events
                            tooltip_text = f"{len(events_list)} event(s):\n"
                            for i, evt in enumerate(events_list[:3]):  # Show max 3
                                tooltip_text += f"• {evt.get('title', 'Untitled')}"
                                if evt.get('time'):
                                    tooltip_text += f" ({evt['time']})"
                                tooltip_text += "\n"
                            if len(events_list) > 3:
                                tooltip_text += "..."
                    return on_enter
                
                # Make cells interactive
                cell_id = cv.create_rectangle(x, y, x+cell_w-2, y+cell_h-2, fill="", outline="", width=0)
        
        # Add click handler for calendar days
        def on_calendar_click(event):
            click_x, click_y = event.x, event.y
            for day, (x1, y1, x2, y2, date_str) in day_positions.items():
                if x1 <= click_x <= x2 and y1 <= click_y <= y2:
                    self.open_day_events_window(date_str, day, month, year)
                    break
        
        cv.bind("<Button-1>", on_calendar_click)
        cv.focus_set()  # Allow the canvas to receive focus for key events
        
        # Add escape key to close window
        def close_calendar(event=None):
            win.destroy()
        
        win.bind("<Escape>", close_calendar)
        cv.bind("<Escape>", close_calendar)
        
        self.cal_win = win

    def open_day_events_window(self, date_str, day, month, year):
        """Open a window to view and manage events for a specific day."""
        # Check if day events window already exists
        if hasattr(self, 'day_events_win') and self.day_events_win:
            try:
                if self.day_events_win.winfo_exists():
                    self.day_events_win.destroy()
            except tk.TclError:
                pass
        
        win = tk.Toplevel(self.root)
        win.title(f"📅 Events - {calendar.month_name[month]} {day}, {year}")
        win.configure(bg="#0c0c0c")
        win.geometry("500x750+150+100")
        win.resizable(True, True)  # Allow resizing to see content better
        
        # Ensure the window appears on top
        win.lift()
        win.attributes('-topmost', True)
        win.after(1000, lambda: win.attributes('-topmost', False))  # Remove topmost after 1 second
        win.focus_force()  # Force focus to this window
        
        # Enhanced header with gradient
        header_frame = tk.Frame(win, bg="#d3031c", height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Date display
        date_label = tk.Label(header_frame, text=f"{calendar.month_name[month]} {day}", 
                              bg="#d3031c", fg="#ffffff", font=("Courier New", 20, 'bold'))
        date_label.pack(pady=(10, 0))
        
        year_label = tk.Label(header_frame, text=str(year), 
                              bg="#d3031c", fg="#ffcccc", font=("Courier New", 12))
        year_label.pack()
        
        # Event count indicator
        events = self.get_events_for_date(date_str)
        event_count = len(events)
        count_label = tk.Label(header_frame, text=f"📋 {event_count} Event{'s' if event_count != 1 else ''}", 
                               bg="#d3031c", fg="#fffbe6", font=("Courier New", 10, 'bold'))
        count_label.pack(pady=(5, 10))
        
        # Main content area with scrolling
        main_frame = tk.Frame(win, bg="#0c0c0c")
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Create scrollable canvas for events
        canvas = tk.Canvas(main_frame, bg="#0c0c0c", highlightthickness=0, height=200)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview, 
                                 bg="#1a1a1a", troughcolor="#0c0c0c", activebackground="#d3031c")
        scrollable_frame = tk.Frame(canvas, bg="#0c0c0c")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Events display with enhanced styling
        if events:
            for i, event in enumerate(events):
                # Event card with modern design
                event_card = tk.Frame(scrollable_frame, bg="#1a1a1a", relief='flat', bd=0)
                event_card.pack(fill='x', pady=(0, 12), padx=5)
                
                # Add subtle shadow effect with border
                shadow_frame = tk.Frame(event_card, bg="#333333", height=2)
                shadow_frame.pack(fill='x', side='bottom')
                
                time_text = event.get('time', '')
                title_text = event.get('title', 'Untitled Event')
                desc_text = event.get('description', '')
                
                # Event header with gradient-like effect
                header_frame = tk.Frame(event_card, bg="#d3031c", height=40)
                header_frame.pack(fill='x')
                header_frame.pack_propagate(False)
                
                # Time badge
                if time_text:
                    time_badge = tk.Label(header_frame, text=f"🕒 {time_text}", 
                                          bg="#d3031c", fg="#ffffff", font=("Courier New", 11, 'bold'))
                    time_badge.pack(side='left', padx=15, pady=10)
                
                # Delete button with hover effect
                delete_btn = tk.Button(header_frame, text="✖", 
                                       bg="#d3031c", fg="#ffffff", bd=0,
                                       font=("Courier New", 12, 'bold'),
                                       cursor="hand2", width=3,
                                       activebackground="#b8021a", activeforeground="#ffffff",
                                       command=lambda idx=i: self.delete_event(date_str, idx, win))
                delete_btn.pack(side='right', padx=15, pady=8)
                
                # Content area
                content_frame = tk.Frame(event_card, bg="#1a1a1a")
                content_frame.pack(fill='x', padx=15, pady=12)
                
                # Title with icon
                title_label = tk.Label(content_frame, text=f"📌 {title_text}", 
                                       bg="#1a1a1a", fg="#fffbe6", 
                                       font=("Courier New", 13, 'bold'))
                title_label.pack(anchor='w')
                
                # Description with better formatting
                if desc_text:
                    desc_label = tk.Label(content_frame, text=f"📝 {desc_text}", 
                                          bg="#1a1a1a", fg="#cccccc", 
                                          font=("Courier New", 10),
                                          wraplength=400, justify='left')
                    desc_label.pack(anchor='w', pady=(8, 0))
        else:
            # Empty state with better design
            empty_frame = tk.Frame(scrollable_frame, bg="#0c0c0c")
            empty_frame.pack(fill='both', expand=True, pady=50)
            
            empty_icon = tk.Label(empty_frame, text="📅", bg="#0c0c0c", fg="#666666", 
                                  font=("Courier New", 30))
            empty_icon.pack()
            
            empty_text = tk.Label(empty_frame, text="No events scheduled", 
                                  bg="#0c0c0c", fg="#888888", 
                                  font=("Courier New", 14, 'bold'))
            empty_text.pack(pady=(10, 5))
            
            empty_subtitle = tk.Label(empty_frame, text="Click 'Add Event' below to create one!", 
                                      bg="#0c0c0c", fg="#666666", 
                                      font=("Courier New", 10))
            empty_subtitle.pack()
        
        # Pack scrolling components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enhanced Add Event Section with menu consistency
        add_frame = tk.Frame(win, bg="#1a1a1a", relief='raised', bd=2)
        add_frame.pack(fill='x', padx=10, pady=(10, 15))
        
        # Add event header with menu styling
        header_add = tk.Frame(add_frame, bg="#d3031c", height=45)
        header_add.pack(fill='x')
        header_add.pack_propagate(False)
        
        add_label = tk.Label(header_add, text="📝 ADD NEW EVENT", 
                             bg="#d3031c", fg="#ffffff", 
                             font=("Courier New", 14, 'bold'))
        add_label.pack(pady=12)
        
        # Form container with menu styling
        form_frame = tk.Frame(add_frame, bg="#2a2a2a")
        form_frame.pack(fill='x', padx=15, pady=15)
        
        # Title entry with menu-consistent styling
        title_container = tk.Frame(form_frame, bg="#2a2a2a")
        title_container.pack(fill='x', pady=(0, 10))
        
        title_label = tk.Label(title_container, text="EVENT TITLE:", 
                               bg="#2a2a2a", fg="#ffffff", 
                               font=("Courier New", 11, 'bold'))
        title_label.pack(anchor='w')
        
        title_entry = tk.Entry(title_container, bg="#ffffff", fg="#000000", 
                               font=("Courier New", 11), relief='flat', bd=3,
                               insertbackground="#000000")
        title_entry.pack(fill='x', pady=(5, 0))
        
        # Time entry with menu-consistent styling
        time_container = tk.Frame(form_frame, bg="#2a2a2a")
        time_container.pack(fill='x', pady=(0, 10))
        
        time_label = tk.Label(time_container, text="TIME:", 
                              bg="#2a2a2a", fg="#ffffff", 
                              font=("Courier New", 11, 'bold'))
        time_label.pack(anchor='w')
        
        time_entry = tk.Entry(time_container, bg="#ffffff", fg="#000000", 
                              font=("Courier New", 11), relief='flat', bd=3,
                              insertbackground="#000000")
        time_entry.pack(fill='x', pady=(5, 0))
        time_entry.insert(0, "10:00 AM")  # Default time with AM/PM
        
        # Description entry with menu-consistent styling
        desc_container = tk.Frame(form_frame, bg="#2a2a2a")
        desc_container.pack(fill='x', pady=(0, 15))
        
        desc_label = tk.Label(desc_container, text="DESCRIPTION:", 
                              bg="#2a2a2a", fg="#ffffff", 
                              font=("Courier New", 11, 'bold'))
        desc_label.pack(anchor='w')
        
        desc_entry = tk.Text(desc_container, bg="#ffffff", fg="#000000", 
                             font=("Courier New", 10), height=3, relief='flat', bd=3,
                             insertbackground="#000000", wrap='word')
        desc_entry.pack(fill='x', pady=(5, 0))
        
        # Enhanced Add button with menu-style consistency
        def add_event():
            title = title_entry.get().strip()
            time = time_entry.get().strip()
            description = desc_entry.get(1.0, tk.END).strip()
            
            if title:
                self.add_calendar_event(date_str, title, time, description)
                win.destroy()  # Close and refresh
                self.open_day_events_window(date_str, day, month, year)  # Reopen to show new event
                # Refresh calendar if it's open
                if hasattr(self, 'cal_win') and self.cal_win:
                    try:
                        if self.cal_win.winfo_exists():
                            self.cal_win.destroy()
                            self.open_calendar_window()
                    except tk.TclError:
                        pass
            else:
                # Show error feedback
                title_entry.configure(bg="#ffcccc")  # Light red tint for error
                title_entry.after(1000, lambda: title_entry.configure(bg="#ffffff"))  # Reset to white background
        
        # Button frame with proper spacing
        button_frame = tk.Frame(form_frame, bg="#2a2a2a")
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Add button with menu-style design
        add_btn = tk.Button(button_frame, text="✅ ADD EVENT", 
                            bg="#d3031c", fg="#ffffff", 
                            font=("Courier New", 12, 'bold'), 
                            relief='flat', bd=0, cursor="hand2",
                            activebackground="#ff1a33", 
                            activeforeground="#ffffff",
                            command=add_event, height=2, padx=20)
        add_btn.pack(pady=(5, 10))
        
        # Add hover effects for consistency
        def on_enter_btn(e):
            add_btn.configure(bg="#ff1a33", fg="#ffffff")
        
        def on_leave_btn(e):
            add_btn.configure(bg="#d3031c", fg="#ffffff")
        
        add_btn.bind("<Enter>", on_enter_btn)
        add_btn.bind("<Leave>", on_leave_btn)
        
        # Focus on title entry for better UX
        title_entry.focus_set()
        
        # Bind Enter key to add event
        def on_enter(event):
            add_event()
        
        title_entry.bind('<Return>', on_enter)
        time_entry.bind('<Return>', on_enter)
        
        # Add escape key to close window
        def close_day_events(event=None):
            win.destroy()
        
        win.bind("<Escape>", close_day_events)
        title_entry.bind("<Escape>", close_day_events)
        time_entry.bind("<Escape>", close_day_events)
        desc_entry.bind("<Escape>", close_day_events)
        
        self.day_events_win = win

    def delete_event(self, date_str, event_index, window):
        """Delete an event from a specific date."""
        if date_str in self.calendar_events and 0 <= event_index < len(self.calendar_events[date_str]):
            del self.calendar_events[date_str][event_index]
            if not self.calendar_events[date_str]:  # Remove empty date entry
                del self.calendar_events[date_str]
            self.save_calendar_events()
            window.destroy()  # Close and refresh
            # Extract date parts from date_str
            year, month, day = map(int, date_str.split('-'))
            self.open_day_events_window(date_str, day, month, year)  # Reopen to show updated events
            # Refresh calendar if it's open
            if hasattr(self, 'cal_win') and self.cal_win:
                try:
                    if self.cal_win.winfo_exists():
                        self.cal_win.destroy()
                        self.open_calendar_window()
                except tk.TclError:
                    pass

    def play_page_flip(self):
        """Play page flip sound effect."""
        if self.pageflip_sound_loaded:
            try:
                self.pageflip_sound.play()
            except Exception as e:
                print(f"[WARN] Page flip sound failed: {e}")

    def load_notebook_data(self):
        """Load notebook pages from JSON file."""
        try:
            if os.path.isfile(NOTEBOOK_SAVE_FILE):
                with open(NOTEBOOK_SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.notebook_pages = data.get('pages', [""])
                    self.current_page = data.get('current_page', 0)
                    # Ensure current page is valid
                    if self.current_page >= len(self.notebook_pages):
                        self.current_page = len(self.notebook_pages) - 1
            else:
                self.notebook_pages = [""]
                self.current_page = 0
        except Exception as e:
            print(f"[WARN] Failed to load notebook data: {e}")
            self.notebook_pages = [""]
            self.current_page = 0

    def save_notebook_data(self):
        """Save notebook pages to JSON file."""
        try:
            os.makedirs(ASSETS_DIR, exist_ok=True)
            data = {
                'pages': self.notebook_pages,
                'current_page': self.current_page,
                'last_saved': datetime.now().isoformat()
            }
            with open(NOTEBOOK_SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARN] Failed to save notebook data: {e}")


def main():
    root = tk.Tk()
    app = CafeApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
