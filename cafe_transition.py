import os
import time
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
BELL_SOUND  = os.path.join(ASSETS_DIR, 'bell.wav')
LEAF_IMAGE  = os.path.join(ASSETS_DIR, 'leaf.png')  # user-supplied leaf sprite (prefer small like 16x16 or 24x24)
RAIN_SOUND  = os.path.join(ASSETS_DIR, 'rain.wav')  # soft looping ambience (optional)
HOVER_SOUND = os.path.join(ASSETS_DIR, 'hover.mp3') # menu hover blip (optional)
TYPING_SOUND = os.path.join(ASSETS_DIR, 'typing.mp3')  # short subtle key tap (optional)
PAGEFLIP_SOUND = os.path.join(ASSETS_DIR, 'pageflip.mp3')  # page flip sound for notebook
MUSIC_DEFAULT = os.path.join(ASSETS_DIR, 'music.mp3')  # default background music (looped)
MUSIC_VOLUME = 0.45
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

# Door hotspot (x1, y1, x2, y2) in original GIF pixel coordinates
DOOR_HITBOX = (50, 40, 70, 90)  # Adjust after you add real outside.gif
CLICK_ANYWHERE_OUTSIDE = True  # If True, any click while outside starts transition
SHOW_DOOR_DEBUG = False        # If True, draws red door hotspot rectangle
SHOW_FOCUSED_DEBUG = False     # If True, draws book/calendar hitboxes in focused scene
SHOW_COORDS = True             # If True, displays logical cursor coordinates top-left
CURSOR_MODE = 'leaf'           # 'leaf' or 'crosshair' for precision aiming
USE_LEAF_CURSOR = True         # Enable custom leaf cursor instead of system pointer
LEAF_SCALE = 1                 # Optional extra scale on the leaf image (logical before canvas scale)
LEAF_OFFSET = (0, 0)           # Pixel offset (logical) to adjust anchor (e.g., (-8,-8) to center)
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
    ("Phone", "play & relax")
]

# Creative submenu configuration  
CREATIVE_SUBMENU_ITEMS = [
    ("Edit Code", "open source code editor"),
    ("Mood Menu", "return to main menu")
]

# Phone game configuration
PHONE_IMAGE = os.path.join(ASSETS_DIR, 'phone.png')
PHONE_GAME_WIDTH = 160   # Game area width (matches phone screen width exactly)
PHONE_GAME_HEIGHT = 235  # Game area height (nearly fills phone screen height)
PHONE_GAME_SCALE = 1.0   # Overall game scale multiplier
PHONE_GAME_OFFSET_X = 20 # Horizontal offset from phone left edge (aligned with screen)
PHONE_GAME_OFFSET_Y = 52 # Vertical offset from phone top edge (centered in screen area)

# Ping pong game settings
PONG_BALL_SIZE = 3       # Ball size
PONG_PADDLE_WIDTH = 6    # Paddle width
PONG_PADDLE_HEIGHT = 25  # Paddle height
PONG_PADDLE_SPEED = 3    # Paddle movement speed
PONG_BALL_SPEED = 2      # Ball movement speed

# Meditation timer configuration
MEDITATION_DURATION = 60  # 1 minute in seconds
BREATHING_CYCLE_DURATION = 8  # 4 seconds inhale + 4 seconds exhale
MEDITATION_BG_COLOR = "#1a1a2e"
MEDITATION_TEXT_COLOR = "#eee2dc"
MEDITATION_ACCENT_COLOR = "#f4a261"

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

ENLARGED_INTERACTIVE_SIZE = 200  # logical pixels (square) - made even bigger for easier clicking
BOOK_HITBOX = _expand_centered(BOOK_HITBOX, ENLARGED_INTERACTIVE_SIZE)
CALENDAR_HITBOX = _expand_centered(CALENDAR_HITBOX, ENLARGED_INTERACTIVE_SIZE)

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
    STATE_FOCUSED = 'focused'
    STATE_TEARING = 'tearing'

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
            self.app.play_bell()

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
        self.bell_loaded = False
        self.rain_loaded = False
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
        
        # Creative submenu state
        self.creative_submenu_active = False
        self.creative_submenu_boxes = []
        self.creative_submenu_hover_index = -1
        self.creative_submenu_selected = ""
        
        # Phone game state
        self.phone_game_active = False
        self.phone_image = None
        self.ping_pong_game = None
        
        # Key state tracking for smooth phone game controls
        self.keys_pressed = set()
        
        # Meditation state
        self.meditation_active = False
        self.meditation_timer = None
        
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
        # Remove specific w/s bindings to avoid conflicts with KeyPress/KeyRelease
        
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
                        print('[DEBUG] Mouse click selecting Focused – initiating focused transition')
                        self.scene.trigger_fade_to_focused()
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
        # Cozy music change button click
        if self.cozy_music_button and self.scene.state == SceneManager.STATE_INSIDE and self.menu_selected_index != -1:
            # check if Cozy selected
            label, _ = MOOD_MENU_ITEMS[self.menu_selected_index]
            if label == 'Cozy':
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

    def loop(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        self.scene.update(dt)
        self.update_animation_time(dt)
        
        # Update phone game if active
        if self.phone_game_active and self.ping_pong_game:
            # Handle continuous key input for smooth paddle movement
            if 'w' in self.keys_pressed or 'Up' in self.keys_pressed:
                self.ping_pong_game.move_player_up()
            if 's' in self.keys_pressed or 'Down' in self.keys_pressed:
                self.ping_pong_game.move_player_down()
            
            self.ping_pong_game.update()
            
        # Update meditation timer if active
        if self.meditation_active and self.meditation_timer:
            self.meditation_timer.update(dt)
            if not self.meditation_timer.is_active:
                # Timer finished
                self.meditation_active = False
                
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
        if self.scene.state in (SceneManager.STATE_OUTSIDE, SceneManager.STATE_FADING):
            frame_out = self.outside.get_frame(self.elapsed_outside_ms) if self.outside.valid else self.placeholder_frame("OUTSIDE")
        if self.scene.state in (SceneManager.STATE_INSIDE, SceneManager.STATE_FADING, SceneManager.STATE_FADING_TO_FOCUSED):
            frame_in = self.inside.get_frame(self.elapsed_inside_ms) if self.inside.valid else None
        if self.scene.state in (SceneManager.STATE_FOCUSED, SceneManager.STATE_FADING_TO_FOCUSED):
            frame_focus = self.focused_scene.get_frame(self.elapsed_focused_ms) if self.focused_scene.valid else None

        if frame_out is not None:
            frame_out = self._standardize_frame(frame_out)
        if frame_in is not None:
            frame_in = self._standardize_frame(frame_in)
        if frame_focus is not None:
            frame_focus = self._standardize_frame(frame_focus)

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
            if self.scene.state == SceneManager.STATE_FOCUSED and frame_focus is not None:
                base = frame_focus
            elif self.scene.state in (SceneManager.STATE_INSIDE, SceneManager.STATE_FADING_TO_FOCUSED) and frame_in is not None:
                base = frame_in
            else:
                base = frame_out
            disp = self._to_photo(base)
        self.canvas.create_image(0, 0, anchor="nw", image=disp)
        self._frame_refs.append(disp)

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
        # Always show the music button when a mood is selected and in the inside scene
        if self.menu_selected_index == -1 or self.scene.state != SceneManager.STATE_INSIDE:
            self.cozy_music_button = None
            return
        
        # Show music button for any selected mood, not just Cozy
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
        # ESC during focus transition or focused state - return to inside view and show menu
        if self.scene.state in (SceneManager.STATE_FADING_TO_FOCUSED, SceneManager.STATE_FOCUSED, SceneManager.STATE_TEARING):
            if event.keysym == 'Escape':
                self.scene.state = SceneManager.STATE_INSIDE
                # Reactivate the menu when returning from focus mode
                self.activate_mood_menu()
                return
        
        # Meditation controls
        if self.meditation_active:
            if event.keysym == 'Escape':
                self.meditation_active = False
                self.meditation_timer = None
                self.cozy_submenu_active = True  # Return to cozy submenu
                return
                
        # Phone game controls - only handle ESC for exit, movement is now continuous
        if self.phone_game_active and self.ping_pong_game:
            if event.keysym == 'Escape':
                self.phone_game_active = False
                self.ping_pong_game = None
                self.cozy_submenu_active = True  # Return to cozy submenu
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
                    elif label == "iPod":
                        self.start_ipod()
            elif event.keysym == 'Escape':
                self.cozy_submenu_active = False
                self.menu_active = True  # Go back to main menu
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
                        print('[DEBUG] Enter pressed: triggering fade to focused')
                        self.scene.trigger_fade_to_focused()
                except Exception:
                    pass

    def on_key_press(self, event):
        """Handle key press events for continuous movement tracking"""
        self.keys_pressed.add(event.keysym)
    
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
    
    # -------- Phone Game Methods --------
    def start_phone_game(self):
        if not self.phone_image:
            print("[WARN] Phone image not loaded, cannot start phone game")
            return
            
        self.phone_game_active = True
        # Use configurable game dimensions with scale factor
        game_w = int(PHONE_GAME_WIDTH * PHONE_GAME_SCALE)
        game_h = int(PHONE_GAME_HEIGHT * PHONE_GAME_SCALE)
        self.ping_pong_game = PingPongGame(game_w, game_h, PONG_BALL_SPEED, PONG_PADDLE_SPEED)
        
    def draw_phone_game(self):
        if not self.phone_image or not self.ping_pong_game:
            return
            
        px = self.scale
        
        # Center phone on screen
        phone_w, phone_h = self.phone_image.size
        phone_x = (self.width - phone_w) // 2
        phone_y = (self.height - phone_h) // 2
        
        # Draw phone image
        phone_photo = self._to_photo(self.phone_image)
        self.canvas.create_image(phone_x*px, phone_y*px, anchor="nw", image=phone_photo)
        self._frame_refs.append(phone_photo)
        
        # Game area positioning using configurable offsets
        game_offset_x = phone_x + int(PHONE_GAME_OFFSET_X * PHONE_GAME_SCALE)
        game_offset_y = phone_y + int(PHONE_GAME_OFFSET_Y * PHONE_GAME_SCALE)
        
        # Draw game area background
        game_w, game_h = self.ping_pong_game.width, self.ping_pong_game.height
        self.canvas.create_rectangle(game_offset_x*px, game_offset_y*px, 
                                     (game_offset_x + game_w)*px, (game_offset_y + game_h)*px,
                                     fill="#000000", outline="#ffffff", width=1)
        
        # Draw center line
        center_x = game_offset_x + game_w // 2
        line_spacing = max(8, int(10 * PHONE_GAME_SCALE))
        for y in range(game_offset_y, game_offset_y + game_h, line_spacing):
            line_height = max(3, int(5 * PHONE_GAME_SCALE))
            self.canvas.create_rectangle(center_x*px, y*px, (center_x+1)*px, (y+line_height)*px, 
                                         fill="#ffffff", outline="")
        
        # Draw paddles
        # Player paddle (left)
        paddle_x = game_offset_x
        paddle_y = game_offset_y + self.ping_pong_game.player_y
        self.canvas.create_rectangle(paddle_x*px, paddle_y*px, 
                                     (paddle_x + self.ping_pong_game.paddle_width)*px,
                                     (paddle_y + self.ping_pong_game.paddle_height)*px,
                                     fill="#ffffff", outline="")
        
        # AI paddle (right)
        ai_paddle_x = game_offset_x + game_w - self.ping_pong_game.paddle_width
        ai_paddle_y = game_offset_y + self.ping_pong_game.ai_y
        self.canvas.create_rectangle(ai_paddle_x*px, ai_paddle_y*px,
                                     (ai_paddle_x + self.ping_pong_game.paddle_width)*px,
                                     (ai_paddle_y + self.ping_pong_game.paddle_height)*px,
                                     fill="#ffffff", outline="")
        
        # Draw ball
        ball_x = game_offset_x + self.ping_pong_game.ball_x
        ball_y = game_offset_y + self.ping_pong_game.ball_y
        ball_size = self.ping_pong_game.ball_size
        self.canvas.create_rectangle(ball_x*px, ball_y*px, 
                                     (ball_x + ball_size)*px, (ball_y + ball_size)*px,
                                     fill="#ffffff", outline="")
        
        # Draw score
        score_text = f"{self.ping_pong_game.player_score} - {self.ping_pong_game.ai_score}"
        score_x = game_offset_x + game_w // 2
        score_y = game_offset_y - int(20 * PHONE_GAME_SCALE)
        if USE_BLOCKY_FONT:
            score_width = self._get_blocky_text_width(score_text)
            self._draw_blocky_text(score_x - score_width//2, score_y, score_text, "#ffffff")
        else:
            font_size = max(8, int(12 * PHONE_GAME_SCALE))
            self.canvas.create_text(score_x*px, score_y*px, text=score_text, 
                                    fill="#ffffff", font=("Courier New", font_size, "bold"))
        
        # Draw controls hint
        controls_text = "W/S or ↑/↓ to move • ESC to exit"
        controls_x = game_offset_x + game_w // 2
        controls_y = game_offset_y + game_h + int(15 * PHONE_GAME_SCALE)
        hint_font_size = max(6, int(8 * PHONE_GAME_SCALE))
        self.canvas.create_text(controls_x*px, controls_y*px, text=controls_text,
                                fill="#ffffff", font=("Courier New", hint_font_size), anchor="n")
    
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
        # Check if calendar window already exists
        if hasattr(self, 'cal_win') and self.cal_win:
            try:
                if self.cal_win.winfo_exists():
                    self.cal_win.lift()
                    return
            except tk.TclError:
                # Window was destroyed, proceed to create new one
                pass
        win = tk.Toplevel(self.root)
        win.title("Calendar")
        win.configure(bg="#0c0c0c")
        cell_w, cell_h = 54, 42  # enlarged cells
        pad = 10
        width = cell_w*7 + pad*2
        height = cell_h*7 + 95  # Increased from 90 to 95 to accommodate larger header
        win.geometry(f"{width}x{height}")
        win.resizable(False, False)  # Prevent maximizing and resizing
        cv = tk.Canvas(win, width=width, height=height, bg="#0c0c0c", highlightthickness=0)
        cv.pack(fill='both', expand=True)
        now = datetime.now()
        year, month = now.year, now.month
        # Header stylized with proper spacing to prevent overlap
        header_text = now.strftime("%B %Y").upper()
        cv.create_rectangle(0,0,width,65, fill="#d3031c", outline="")  # Increased height to 65
        cv.create_text(width//2, 16, text=header_text, fill="#ffffff", font=("Courier New", 16, 'bold'), anchor='n')  # Reduced font from 18 to 16
        cv.create_text(width//2, 42, text="STAY ON TRACK", fill="#fffbe6", font=("Courier New", 10, 'bold'))  # Moved down from 38 to 42
        # Weekday labels - adjusted for increased header height
        weekdays = ['M','T','W','T','F','S','S']
        for i, wd in enumerate(weekdays):
            cv.create_text(pad + cell_w*i + cell_w/2, 75, text=wd, fill="#ffffff", font=("Courier New", 12, 'bold'))  # Moved from 70 to 75
        # Calendar grid generation (Monday=0) - adjusted for increased header height
        month_cal = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
        start_y = 95  # Moved from 90 to 95
        today_day = now.day
        for row_idx, week in enumerate(month_cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue
                x = pad + col_idx * cell_w
                y = start_y + row_idx * cell_h
                # Slight skew effect by drawing layered rectangles
                base_color = "#1b1b1b"
                if day == today_day:
                    base_color = "#ffec00"
                elif col_idx >=5:  # weekend
                    base_color = "#262626"
                cv.create_rectangle(x+2, y+4, x+cell_w-3, y+cell_h+2, fill="#000", outline="")  # shadow
                cv.create_rectangle(x, y, x+cell_w-3, y+cell_h-3, fill=base_color, outline="#666")
                cv.create_text(x+cell_w/2-2, y+cell_h/2-6, text=str(day), fill="#000" if day==today_day else "#ffffff", font=("Courier New", 12, 'bold'))
        self.cal_win = win

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
