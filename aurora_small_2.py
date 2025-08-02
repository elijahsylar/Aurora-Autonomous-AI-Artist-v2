from llama_cpp import Llama
from pathlib import Path
import pygame
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
pygame.init()

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import json
from datetime import datetime
from collections import deque
import time
import pyaudio
import requests
import webbrowser
from urllib.parse import quote
import numpy as np
import math
import random
try:
    from aurora_ai_backup2 import DeepMemorySystem
    DEEP_MEMORY_AVAILABLE = True
    print("✅ Deep Memory System available!")
except ImportError:
    print("❌ Could not import DeepMemorySystem - will use simple memory only")
    DEEP_MEMORY_AVAILABLE = False
except Exception as e:
    print(f"Error: {e}")
    DEEP_MEMORY_AVAILABLE = False
    
# LLAVA VISION IMPORTS - ADD RIGHT HERE
try:
    from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
    import torch
    LLAVA_AVAILABLE = True
    print("✅ LLaVA vision libraries available!")
except ImportError:
    print("❌ Could not import LLaVA - continuing without vision")
    LLAVA_AVAILABLE = False
      
class SimpleMemorySystem:
    """A simple memory system for Aurora to access and store her own memories.

    Provides basic memory file management, drawing and code history, and canvas-specific storage.
    """
    def __init__(self, memory_path="./aurora_memory"):
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(exist_ok=True)  # Ensure base directory exists
        
        # Initialize basic structures for canvas operations
        self.drawing_history = deque(maxlen=1000)
        self.code_history = deque(maxlen=1000)
        
        # List available memory files for Aurora
        self.available_memories = {}
        if self.memory_path.exists():
            print("Aurora's memory files:")
            for file in self.memory_path.glob("*.json"):
                if file.stat().st_size < 100000:  # Only files under 100KB
                    self.available_memories[file.name] = file
                    print(f"  - {file.name} ({file.stat().st_size} bytes)")
        
        # Canvas-specific storage (separate from general memories)
        self.canvas_path = self.memory_path / "canvas"
        self.canvas_path.mkdir(exist_ok=True)
        
    def read_memory(self, filename):
        """Aurora can read her own memory files"""
        if filename in self.available_memories:
            try:
                with open(self.available_memories[filename], 'r') as f:
                    return json.load(f)
            except Exception:
                return None
        return None
    
    def get_memory_summary(self):
        """Get a quick summary of available memories"""
        summary = []
        
        # Try to read key identity files
        if "user_identity.json" in self.available_memories:
            data = self.read_memory("user_identity.json")
            if data and "name" in data:
                summary.append(f"I know {data['name']}")
                
        if "autonomous_creative_vision.json" in self.available_memories:
            data = self.read_memory("autonomous_creative_vision.json")
            if data and "current_vision" in data:
                vision = data["current_vision"][:50]
                summary.append(f"My vision: {vision}...")
                
        return " | ".join(summary) if summary else "Memories available"
    
    def load_memories(self):
        """Load canvas-specific memories"""
        # Load canvas code history
        canvas_code = self.canvas_path / "canvas_code_history.json"
        if canvas_code.exists():
            try:
                with open(canvas_code, 'r') as f:
                    data = json.load(f)
                    self.code_history = deque(data[-1000:], maxlen=1000)  # Keep last 1000
                    print(f"Loaded {len(self.code_history)} code memories")
            except json.JSONDecodeError as e:
                print(f"Error parsing code history JSON: {e}")
                self.code_history = deque(maxlen=1000)  # Start fresh
            except Exception as e:
                print(f"Error loading code history: {e}")
                self.code_history = deque(maxlen=1000)  # Start fresh
        
        # Skip loading any reinforcement learning data
        stats_file = self.canvas_path / "learning_stats.json"
        if stats_file.exists():
            print("(Skipping old reinforcement learning data)")
        # Load dream memories
        dreams_file = self.canvas_path / "dream_memories.json"
        if dreams_file.exists():
            try:
                with open(dreams_file, 'r') as f:
                    dream_data = json.load(f)
                    # We'll load these into Aurora when she initializes
                    self.loaded_dreams = dream_data
                    print(f"Found {len(dream_data)} dream memories")
            except Exception as e:
                print(f"Error loading dream memories: {e}")
                self.loaded_dreams = []
        else:
            self.loaded_dreams = []
            
    def save_memories(self):
        """Save canvas-specific data"""
        # Save code history
        try:
            with open(self.canvas_path / "canvas_code_history.json", 'w') as f:
                json.dump(list(self.code_history), f)
        except Exception as e:
            print(f"Error saving code history: {e}")

        # Save dream memories
        dreams_file = self.canvas_path / "dream_memories.json"
        try:
            if hasattr(self, 'parent') and hasattr(self.parent, 'dream_memories'):
                dream_data = list(self.parent.dream_memories)
                with open(dreams_file, 'w') as f:
                    json.dump(dream_data, f)
                print(f"Saved {len(dream_data)} dream memories")
        except Exception as e:
            print(f"Error saving dream memories: {e}")

    def remember_code(self, code, context):
        """
        Remember canvas drawing code.

        Args:
            code (str): The drawing code or command sequence.
            context (dict): Dictionary containing metadata about the drawing action.
                Required keys:
                    - 'emotion': Current emotion during drawing.
                    - 'x': X position on canvas.
                    - 'y': Y position on canvas.
                    - 'color': Color name used.
                    - 'pen_down': Boolean, whether pen is down.
                Optional keys:
                    - 'pixels_drawn': Number of pixels drawn.
                    - 'draw_mode': Drawing tool/mode used.
        """
        self.code_history.append({
            "code": code,
            "context": context,
            "timestamp": datetime.now().isoformat(timespec='seconds')
        })

class PaintByNumberTemplates:
    """
    PaintByNumberTemplates provides hidden paint-by-number templates for Aurora's drawing system.

    Purpose:
        - Stores predefined templates for various shapes and difficulty levels.
        - Supplies template overlays for guided drawing and progress tracking.

    Attributes:
        - current_template: The currently active template dictionary.
        - template_name: Name of the selected template.
        - difficulty: Difficulty level of the template ('easy', 'medium', 'hard').
        - templates: Dictionary of all available templates, organized by difficulty.

    Usage:
        - Instantiate the class to access templates.
        - Use get_template_overlay(grid) to retrieve overlay information for the current template.
        - Set current_template, template_name, and difficulty to activate a template.

    Example:
        templates = PaintByNumberTemplates()
        templates.current_template = templates.templates["easy"]["circle"]
        overlay = templates.get_template_overlay(grid)
    """
    def __init__(self):
        self.current_template = None
        self.template_name = None
        self.difficulty = None
        
        # Templates stored as grid positions (60x60 grid coordinates)
        self.templates = {
            "easy": {
                "circle": {
                    "positions": [(30,25), (32,26), (34,28), (35,30), (34,32), (32,34), (30,35), (28,34), (26,32), (25,30), (26,28), (28,26)],
                    "colors": {"positions": "B"}
                },
                "square": {
                    "positions": [(25,25), (26,25), (27,25), (28,25), (29,25), (30,25), (31,25), (32,25), (33,25), (34,25), (35,25),
                                 (25,35), (26,35), (27,35), (28,35), (29,35), (30,35), (31,35), (32,35), (33,35), (34,35), (35,35),
                                 (25,26), (25,27), (25,28), (25,29), (25,30), (25,31), (25,32), (25,33), (25,34),
                                 (35,26), (35,27), (35,28), (35,29), (35,30), (35,31), (35,32), (35,33), (35,34)],
                    "colors": {"positions": "R"}
                },
                "cross": {
                    "positions": [(30,20), (30,21), (30,22), (30,23), (30,24), (30,25), (30,26), (30,27), (30,28), (30,29), (30,30),
                                 (30,31), (30,32), (30,33), (30,34), (30,35), (30,36), (30,37), (30,38), (30,39), (30,40),
                                 (20,30), (21,30), (22,30), (23,30), (24,30), (25,30), (26,30), (27,30), (28,30), (29,30),
                                 (31,30), (32,30), (33,30), (34,30), (35,30), (36,30), (37,30), (38,30), (39,30), (40,30)],
                    "colors": {"positions": "G"}
                }
            },
            "medium": {
                "flower": {
                    "center": [(29,29), (30,29), (31,29), (29,30), (30,30), (31,30), (29,31), (30,31), (31,31)],
                    "petals": [(30,26), (30,27), (33,30), (34,30), (30,33), (30,34), (26,30), (27,30),
                              (27,27), (33,27), (33,33), (27,33)],
                    "stem": [(30,35), (30,36), (30,37), (30,38), (30,39), (30,40)],
                    "leaves": [(28,37), (27,37), (32,38), (33,38)],
                    "colors": {"center": "Y", "petals": "R", "stem": "G", "leaves": "G"}
                },
                "star": {
                    "points": [(30,20), (32,26), (38,26), (33,30), (35,36), (30,32), (25,36), (27,30), (22,26), (28,26)],
                    "lines": [(30,21), (30,22), (30,23), (30,24), (30,25), (31,27), (32,28), (33,29),
                             (29,27), (28,28), (27,29), (31,31), (29,31), (28,32), (29,33), (30,34), (31,33), (32,32)],
                    "colors": {"points": "Y", "lines": "Y"}
                },
                "heart": {
                    "left_curve": [(27,25), (26,26), (25,27), (25,28), (25,29), (26,30), (27,31)],
                    "right_curve": [(33,25), (34,26), (35,27), (35,28), (35,29), (34,30), (33,31)],
                    "bottom": [(28,32), (29,33), (30,34), (31,33), (32,32)],
                    "fill": [(28,26), (29,26), (30,26), (31,26), (32,26), (28,27), (29,27), (30,27), (31,27), (32,27),
                            (27,28), (28,28), (29,28), (30,28), (31,28), (32,28), (33,28),
                            (27,29), (28,29), (29,29), (30,29), (31,29), (32,29), (33,29),
                            (28,30), (29,30), (30,30), (31,30), (32,30), (28,31), (29,31), (30,31), (31,31), (32,31)],
                    "colors": {"left_curve": "P", "right_curve": "P", "bottom": "P", "fill": "P"}
                }
            },
            "hard": {
                "house": {
                    "roof": [(26,20), (27,19), (28,18), (29,17), (30,16), (31,17), (32,18), (33,19), (34,20),
                            (26,21), (27,21), (28,21), (29,21), (30,21), (31,21), (32,21), (33,21), (34,21)],
                    "walls": [(26,22), (27,22), (28,22), (29,22), (30,22), (31,22), (32,22), (33,22), (34,22),
                             (26,23), (34,23), (26,24), (34,24), (26,25), (34,25), (26,26), (34,26),
                             (26,27), (34,27), (26,28), (34,28), (26,29), (34,29),
                             (26,30), (27,30), (28,30), (29,30), (30,30), (31,30), (32,30), (33,30), (34,30)],
                    "door": [(30,26), (30,27), (30,28), (30,29), (30,30)],
                    "windows": [(28,24), (29,24), (28,25), (29,25), (32,24), (33,24), (32,25), (33,25)],
                    "colors": {"roof": "R", "walls": "W", "door": "N", "windows": "C"}
                },
                "tree": {
                    "trunk": [(29,35), (30,35), (31,35), (29,36), (30,36), (31,36), (29,37), (30,37), (31,37),
                             (29,38), (30,38), (31,38), (29,39), (30,39), (31,39), (29,40), (30,40), (31,40)],
                    "canopy": [(28,20), (29,20), (30,20), (31,20), (32,20),
                              (26,21), (27,21), (28,21), (29,21), (30,21), (31,21), (32,21), (33,21), (34,21),
                              (25,22), (26,22), (27,22), (28,22), (29,22), (30,22), (31,22), (32,22), (33,22), (34,22), (35,22),
                              (24,23), (25,23), (26,23), (27,23), (28,23), (29,23), (30,23), (31,23), (32,23), (33,23), (34,23), (35,23), (36,23),
                              (25,24), (26,24), (27,24), (28,24), (29,24), (30,24), (31,24), (32,24), (33,24), (34,24), (35,24),
                              (26,25), (27,25), (28,25), (29,25), (30,25), (31,25), (32,25), (33,25), (34,25),
                              (27,26), (28,26), (29,26), (30,26), (31,26), (32,26), (33,26),
                              (28,27), (29,27), (30,27), (31,27), (32,27),
                              (29,28), (30,28), (31,28)],
                    "colors": {"trunk": "N", "canopy": "G"}
                },
                "butterfly": {
                    "body": [(30,28), (30,29), (30,30), (30,31), (30,32)],
                    "left_wing_top": [(26,27), (25,27), (24,27), (25,28), (26,28), (27,28), (28,28), (27,29), (28,29)],
                    "left_wing_bottom": [(26,31), (25,31), (24,31), (25,32), (26,32), (27,32), (28,32), (27,33), (28,33)],
                    "right_wing_top": [(34,27), (35,27), (36,27), (35,28), (34,28), (33,28), (32,28), (33,29), (32,29)],
                    "right_wing_bottom": [(34,31), (35,31), (36,31), (35,32), (34,32), (33,32), (32,32), (33,33), (32,33)],
                    "colors": {"body": "B", "left_wing_top": "O", "left_wing_bottom": "Y", 
                              "right_wing_top": "O", "right_wing_bottom": "Y"}
                }
            }
        }
    
    def get_template_overlay(self, grid):
        """
        Add template overlay to Aurora's vision (only in her prompt, not console).

        Returns:
            str: A formatted string describing the current template, suggested colors, and intended for overlay display in Aurora's prompt.
        """
        if not self.current_template:
            return ""
        
        overlay_info = f"\n\n[PAINT-BY-NUMBER TEMPLATE: {self.template_name.upper()} ({self.difficulty})]"
        overlay_info += f"\nSuggested pattern to follow! Use these colors:"
        
        # Get suggested colors
        colors_used = []
        for part, color in self.current_template["colors"].items():
            color_name = {
                'R': 'red', 'G': 'green', 'B': 'blue', 'Y': 'yellow',
                'P': 'purple', 'O': 'orange', 'C': 'cyan', 'W': 'white',
                'N': 'black', 'K': 'pink', 'M': 'magenta'
            }.get(color, 'white')
            colors_used.append(f"{part}={color_name}")
        
        overlay_info += f"\n{', '.join(colors_used)}"
        overlay_info += f"\nTemplate guides your art - follow or improvise!"
        
        return overlay_info
  
    
class AuroraCodeMindComplete:
    """
    AuroraCodeMindComplete
    A comprehensive AI-powered drawing and creativity system for real-time, autonomous art generation. 
    AuroraCodeMindComplete manages a large pixel canvas, emotional state, memory, sound, and interactive controls, 
    using a local LLM for code-based motor control and creative decision-making.
    Features:
    - GPU-accelerated LLM for fast code generation and decision making.
    - Dynamic canvas scaling and multi-resolution vision (normal, density, shape, compressed views).
    - Rich color palette and drawing tools (pen, brush, spray, stamps, etc.).
    - Emotional state tracking and influence system, including deep emotions and memory-based shifts.
    - Memory system for code patterns, dreams, and artistic inspirations.
    - Check-in system for periodic breaks (chat, dream, image search).
    - Sound system with pitch control and instant musical feedback.
    - Fullscreen Tkinter GUI with live status panels and controls.
    - Autonomous loop with emotion-driven speed, creativity boosters, and periodic snapshots.
    - Dream generation and retention based on actual drawing experiences.
    - Support for external deep memory systems and image search inspiration.
    Usage:
    - Instantiate with a model path and optional GPU settings.
    - Call `run()` to start the interactive drawing loop.
    - Use keyboard controls for snapshots, turbo mode, fullscreen, and quitting.
    Main Methods:
    - run(): Start the main loop and GUI.
    - create_loop(): Main autonomous loop for drawing, thinking, and emotional processing.
    - think_in_code(): Generate and execute movement/drawing codes via LLM.
    - update_display(): Refresh the canvas and status panels.
    - adjust_pixel_size(), adjust_speed(), feel(): Control canvas, speed, and emotion.
    - save_canvas_state(), load_canvas_state(), save_snapshot(): Persistence and artwork saving.
    - process_deep_emotions(), influence_emotion(): Emotional state management.
    - generate_dream(), process_dream_retention(): Dream cycle and memory retention.
    - setup_display(): Initialize GUI and controls.
    Keyboard Controls:
    - S: Save snapshot
    - T: Toggle turbo mode
    - ESC: Exit fullscreen
    - F11: Toggle fullscreen
    - Q: Quit
    - C/B: Center/reset view
    - H: Toggle hearing
    AuroraCodeMindComplete is designed for creative exploration, emotional intelligence, and autonomous art-making.
    """
    def __init__(self, model_path, use_gpu=True, gpu_layers=10):
        print("Initializing AuroraCodeMindComplete...")
        
        # Detect GPU and set layers
        if use_gpu:
            print("🚀 GPU Mode Enabled!")
            # -1 means offload all layers to GPU
            gpu_layers_setting = gpu_layers
        else:
            print("💻 CPU Mode")
            gpu_layers_setting = 0
            
        # LLM with GPU acceleration
        self.llm = Llama(
            model_path, 
            n_ctx=4096,
            n_gpu_layers=gpu_layers_setting,  # GPU LAYERS!
            n_threads=8,  # Use more CPU threads
            n_batch=512,  # Larger batch size for GPU
            verbose=False,
            seed=42,  # Fixed seed for reproducibility
            f16_kv=True,  # Use 16-bit for faster inference
            use_mlock=True,  # Lock model in RAM
            n_threads_batch=8  # Batch processing threads
        )
        print(f"2. LLM loaded with {gpu_layers_setting} GPU layers")
        
        # Get screen dimensions for fullscreen
        # Don't init pygame here - we'll do it once in setup_display
        screen_width = 1920  # Default assumption
        screen_height = 1080  # Default assumption
        
        # Canvas - adjust size based on screen (much smaller pixels now!)
        self.scale_factor = 1.0  # Lower scale_factor means smaller pixels and higher canvas resolution; e.g., 1.6 gives more pixels than 8.
        self.canvas_size = min(int(screen_width / self.scale_factor) - 50, 
                               int(screen_height / self.scale_factor) - 50)
        
        # Supersampling for quality
        self.supersample_factor = 4  # Draw at 4x resolution internally
        self.internal_canvas_size = self.canvas_size * self.supersample_factor
                               
                       
        self.x = self.canvas_size // 2
        self.y = self.canvas_size // 2
        self.is_drawing = True
        self.steps_taken = 0
        print(f"3. Canvas settings done - Size: {self.canvas_size}x{self.canvas_size} ({self.scale_factor}x scale)")
        
        # Expanded color palette with full word codes
        self.palette = {
            'red': (255, 0, 0),
            'orange': (255, 150, 0),
            'yellow': (255, 255, 0),
            'green': (0, 255, 0),
            'cyan': (0, 255, 255),
            'blue': (0, 100, 255),
            'purple': (200, 0, 255),
            'pink': (255, 192, 203),
            'white': (255, 255, 255),
            'gray': (128, 128, 128),
            'black': (0, 0, 0),  # For explicit black (not just eraser)
            'brown': (139, 69, 19),
            'magenta': (255, 0, 255),
            'lime': (50, 205, 50),
            'navy': (0, 0, 128)
        }
        
        # Full word codes for colors - easy to remember!
        self.color_codes = {
            'red': 'red',       'orange': 'orange',    'yellow': 'yellow',
            'green': 'green',   'cyan': 'cyan',        'blue': 'blue',
            'purple': 'purple', 'pink': 'pink',        'white': 'white',
            'gray': 'gray',     'black': 'black',      'brown': 'brown',
            'magenta': 'magenta', 'lime': 'lime',      'navy': 'navy'
        }
        
        self.current_color = (255, 255, 255)
        self.current_color_name = 'white'
        # View modes
        self.view_mode = "normal"  # normal, density, shape
        # Drawing modes
        self.draw_mode = "brush"  # pen, brush, star, eraser
        self.pen_momentum = 0 
        # Color variety tracking
        self.color_history = deque(maxlen=20)  # Track last 20 color uses
        self.turn_colors_used = set()  # Track colors used in current turn
        self.last_turn_color = 'white'  # Track color from previous turn
        
        print("4. Colors and tools initialized")
        
    
        # Memory system
        self.memory = SimpleMemorySystem("./aurora_canvas_newestversions")
        self.memory.parent = self  # Add reference for saving dreams
        self.memory.load_memories()  # LOAD PREVIOUS MEMORIES!
        
        # Load previous dreams if they exist
        if hasattr(self.memory, 'loaded_dreams'):
            self.dream_memories = deque(self.memory.loaded_dreams, maxlen=100)
            print(f"Loaded {len(self.dream_memories)} previous dreams!")
        else:
            self.dream_memories = deque(maxlen=100)
        print("5. Memory system created and loaded")
        # Connect to Big Aurora's deep memory
        # ADD THIS BLOCK RIGHT AFTER memory system creation:

        if DEEP_MEMORY_AVAILABLE:
            try:
                self.big_memory = DeepMemorySystem()
                print("✅ Connected to Big Aurora's deep memories!")
                
                # Just mark it as available - we'll figure out the API when we use it
                self.big_memory_available = True
                    
            except Exception as e:
                print(f"❌ Could not connect to Big Aurora's memory: {e}")
                self.big_memory = None
                self.big_memory_available = False
        else:
            self.big_memory = None
            self.big_memory_available = False
        # Image search system
        self.image_search_count = 0
        self.recent_image_searches = deque(maxlen=20)    
        # Emotional state
        self.current_emotion = "curious"
        self.emotion_words = ["curious", "playful", "contemplative", "energetic", "peaceful", "creative"]
        print("6. Emotions initialized")
        # DEEPER EMOTION SYSTEM
        # Expanded emotion vocabulary with intensity levels
        self.deep_emotions = {
            # Primary emotions with their intensity variations
            "joy": ["content", "happy", "joyful", "elated", "euphoric"],
            "curiosity": ["interested", "curious", "fascinated", "absorbed", "obsessed"],
            "peace": ["calm", "peaceful", "serene", "tranquil", "zen"],
            "energy": ["active", "energetic", "excited", "exhilarated", "electric"],
            "contemplation": ["thoughtful", "contemplative", "reflective", "philosophical", "profound"],
            "creativity": ["inspired", "creative", "imaginative", "visionary", "transcendent"],
            "melancholy": ["wistful", "nostalgic", "melancholic", "longing", "bittersweet"],
            "wonder": ["amazed", "wondering", "astonished", "awestruck", "mystified"]
        }
        
        # Emotion influences from different sources
        self.emotion_influences = {
            "dreams": 0.0,      # -1 to 1, how dreams affected mood
            "chat": 0.0,        # -1 to 1, how chats affected mood  
            "music": 0.0,       # -1 to 1, how sounds affected mood
            "artwork": 0.0,     # -1 to 1, how viewing art affected mood
            "creating": 0.0     # -1 to 1, how creating affected mood
        }
        
        # Current emotion depth (0-4, maps to intensity in deep_emotions)
        self.emotion_depth = 2  # Start at middle intensity
        self.emotion_category = "curiosity"  # Start curious
        
        # Emotion memory - tracks recent emotional experiences
        self.emotion_memory = deque(maxlen=50)
        self.emotion_shift_cooldown = 0  # Prevents too-rapid emotion changes
        
        print("6b. Deep emotion system initialized")
        # Code tracking
        self.last_code = ""
        self.continuous_draws = 0
        self.last_think_time = 0  # Performance tracking
        self.skip_count = 0  # Track thinking pauses
        self.aurora_speed = "normal"  # Aurora's chosen speed
        self.aurora_delay = 300  # Current delay in ms
        self.recent_speed_override = False  # Track if Aurora recently chose speed
        self.speed_override_counter = 0  # Steps since speed override
        print("7. Code tracking initialized")
        
        # Canvas - now at higher resolution internally
        self.pixels = Image.new('RGBA', (self.internal_canvas_size, self.internal_canvas_size), 'black')
        self.draw_img = ImageDraw.Draw(self.pixels)
        print(f"8. Image buffer created at {self.internal_canvas_size}x{self.internal_canvas_size} (4x supersampled)")
        
        # Try to load previous canvas state (this may adjust position)
        self.load_canvas_state()
        
        # Ensure position is valid for current canvas
        self.x = max(0, min(self.x, self.canvas_size - 1))
        self.y = max(0, min(self.y, self.canvas_size - 1))
        
        # Performance settings
        self.turbo_mode = False
        self.use_gpu = use_gpu
        
        # Check-in system initialization
        self.last_checkin_time = time.time()
        self.current_mode = "drawing"  # drawing, chat, rest
        self.mode_start_time = time.time()
        self.checkin_interval = 45 * 60  # 45 minutes in seconds
        self.break_duration = 10 * 60    # 10 minutes in seconds
        self.awaiting_checkin_response = False
        self.chat_message_count = 0 
        # Dream system initialization
        self.current_dreams = []  # Dreams from current rest session
        self.sleep_phase = "light"  # light, rem, waking
        self.sleep_phase_start = time.time()
        self.dream_count = 0
        # Audio hearing system
        self.hearing_enabled = False
        self.audio_stream = None
        self.audio = pyaudio.PyAudio()
        self.rest_duration = 10 * 60  # 10 minutes for rest/dreaming (separate from break_duration)

        
        # Simple pygame sound system  # ADD ALL OF THIS
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        pygame.mixer.set_num_channels(8)  # 8 simultaneous sounds
        
        # Pre-generate simple beeps (so they're instant to play)
        self.sounds = {}
        # Cymatics system
        self.cymatic_circles = []
        self.current_pitch = 'normal'  # ADD THIS - tracks current pitch mode
        try:
            import numpy as np  # Import here if not already imported
        
            # EXPANDED SOUND PALETTE - 24 base frequencies (no number conflicts!)
            sound_chars = '!@#$%^&*()[]<>=+~`-_,.|;:?/{}\\'
            
            # Generate frequencies across wider spectrum (100Hz to 2000Hz)
            for i, char in enumerate(sound_chars):
                # Exponential frequency distribution for more musical range
                base_freq = 100 * (2 ** (i / 6.0))  # Doubles every 6 notes for wider range
                
                # Normal pitch
                freq = base_freq
                samples = np.sin(2 * np.pi * freq * np.arange(0, 0.05 * 22050) / 22050) * 0.3
                sound_data = (samples * 32767).astype(np.int16)
                sound_data = np.repeat(sound_data.reshape(-1, 1), 2, axis=1)  # Make stereo
                self.sounds[f"{char}_normal"] = pygame.sndarray.make_sound(sound_data)
                self.sounds[f"{char}_normal"].set_volume(0.3)
                
                # Low pitch (++) - one octave down
                freq = base_freq * 0.5
                samples = np.sin(2 * np.pi * freq * np.arange(0, 0.05 * 22050) / 22050) * 0.3
                sound_data = (samples * 32767).astype(np.int16)
                sound_data = np.repeat(sound_data.reshape(-1, 1), 2, axis=1)
                self.sounds[f"{char}_low"] = pygame.sndarray.make_sound(sound_data)
                self.sounds[f"{char}_low"].set_volume(0.3)
                
                # High pitch (--) - one octave up
                freq = base_freq * 2
                samples = np.sin(2 * np.pi * freq * np.arange(0, 0.05 * 22050) / 22050) * 0.3
                sound_data = (samples * 32767).astype(np.int16)
                sound_data = np.repeat(sound_data.reshape(-1, 1), 2, axis=1)
                self.sounds[f"{char}_high"] = pygame.sndarray.make_sound(sound_data)
                self.sounds[f"{char}_high"].set_volume(0.3)
                
            print(f"✅ Sound system ready with {len(sound_chars)} tones × 3 octaves = {len(sound_chars)*3} total sounds!")
        except:
            print("❌ Sound system failed - continuing without audio")
            self.sounds = {}
            
        # LLAVA VISION SYSTEM - ADD THIS ENTIRE BLOCK HERE
        print("8b. Initializing vision system...")
        self.vision_enabled = False
        if LLAVA_AVAILABLE:
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                
                # Moondream2 - tiny but effective!
                model_id = "vikhyatk/moondream2"
                
                self.vision_tokenizer = AutoTokenizer.from_pretrained(model_id)
                self.vision_model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    trust_remote_code=True,
                    torch_dtype=torch.float16,  # Use float16 for GPU
                    low_cpu_mem_usage=True
                )
                
                # Try GPU first, fall back to CPU if needed
                try:
                    self.vision_model = self.vision_model.to("cuda")
                    print("  ✅ Moondream2 loaded on GPU!")
                except RuntimeError as e:
                    if "out of memory" in str(e):
                        print("  ⚠️ GPU full, falling back to CPU")
                        self.vision_model = self.vision_model.to("cpu")
                    else:
                        raise e
                    
                self.vision_enabled = True
                self.last_vision_time = 0
                self.vision_interval = 90.0  # Can be faster on GPU!
                
            except Exception as e:
                print(f"  ❌ Could not load vision: {e}")
                self.vision_enabled = False
            
            
        # Setup display
        print("9. About to setup display...")
        self.setup_display()
        print("10. Display setup complete")
    
    def _scale_to_internal(self, coord):
        """Convert display coordinates to internal supersampled coordinates"""
        return coord * self.supersample_factor
    
    def _scale_from_internal(self, coord):
        """Convert internal supersampled coordinates to display coordinates"""
        return coord // self.supersample_factor
        
    def _create_soft_brush(self, size, hardness=0.5):
        """Create a soft circular brush with gradient falloff"""
        brush = Image.new('L', (size * 2, size * 2), 0)
        draw = ImageDraw.Draw(brush)
        
        # Create gradient circles from outside to inside
        for i in range(size, 0, -1):
            # Calculate opacity based on distance from center
            if hardness == 1.0:
                opacity = 255 if i == size else 0
            else:
                opacity = int(255 * (i / size) ** (1 / (hardness + 0.1)))
            
            draw.ellipse(
                [size - i, size - i, size + i, size + i],
                fill=opacity
            )
        
        return brush
    
    def _blend_with_alpha(self, x, y, color, alpha_mask):
        """Blend color with existing canvas using alpha mask"""
        mask_width, mask_height = alpha_mask.size
        half_w, half_h = mask_width // 2, mask_height // 2
        
        # Get the numpy array of the alpha mask
        import numpy as np
        mask_array = np.array(alpha_mask)
        
        # Draw each pixel of the brush
        for dy in range(mask_height):
            for dx in range(mask_width):
                # Get alpha value from mask
                alpha = mask_array[dy, dx]
                if alpha > 0:
                    px = x - half_w + dx
                    py = y - half_h + dy
                    
                    # Check bounds
                    if 0 <= px < self.internal_canvas_size and 0 <= py < self.internal_canvas_size:
                        # Get existing pixel
                        existing = self.pixels.getpixel((px, py))
                        
                        # Blend colors based on alpha
                        alpha_float = alpha / 255.0
                        if len(existing) == 4:  # RGBA
                            r = int(existing[0] * (1 - alpha_float) + color[0] * alpha_float)
                            g = int(existing[1] * (1 - alpha_float) + color[1] * alpha_float)
                            b = int(existing[2] * (1 - alpha_float) + color[2] * alpha_float)
                            a = max(existing[3], alpha)
                            self.pixels.putpixel((px, py), (r, g, b, a))
                        else:  # RGB
                            r = int(existing[0] * (1 - alpha_float) + color[0] * alpha_float)
                            g = int(existing[1] * (1 - alpha_float) + color[1] * alpha_float)
                            b = int(existing[2] * (1 - alpha_float) + color[2] * alpha_float)
                            self.pixels.putpixel((px, py), (r, g, b))
    
    def _draw_smooth_line(self, x1, y1, x2, y2, brush_func):
        """Draw a smooth line between two points using the brush function"""
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            brush_func(x1, y1)
            return
            
        # More steps for longer lines to ensure smoothness
        steps = max(int(distance * 2), 1)
        
        for i in range(steps + 1):
            t = i / steps
            x = int(x1 + dx * t)
            y = int(y1 + dy * t)
            brush_func(x, y)
    def get_ascii_art_examples(self):
        """Return ASCII art examples that Aurora can see for inspiration"""
        
        examples = {
            "rainbow_line": """
Rainbow Line - Try this code:
red53333orange53333yellow53333green53333blue53333purple53333

This draws a horizontal rainbow stripe!""",
            
            "star_burst": """
Star Burst - Try this code:
white5003332211100332211

Creates a star pattern from center!""",
            
            "color_wave": """
Color Wave - Try this code:
blue533311122200cyan533311122200green533311122200

Makes a flowing wave in cool colors!""",
            
            "spiral_out": """
Spiral Outward - Try this code:
533330000222211113333000022221111

Draws an expanding square spiral!""",
            
            "music_rainbow": """
Musical Rainbow - Try this code with sounds:
red5333!@#orange5333$%^yellow5333&*()

Combines colors with ascending tones!""",
            
            "dotted_trail": """
Dotted Trail - Try this code:
53422534225342253422

Leaves a dotted line as you move!""",
            
            "zigzag_melody": """
Zigzag with Music - Try this code:
5313!313@313#313$

Draws zigzag while playing notes!""",
            
            "brush_demo": """
Brush Strokes - Try this code:
brush5333333pen511111large_brush522222

Shows different brush sizes in action!""",
            
            "stamp_parade": """
Stamp Parade - Try this code:
star53333cross53333circle53333diamond53333flower5

Places different stamps in a row!""",
            
            "color_test": """
Quick Color Test - Try this code:
red5.green5.blue5.yellow5.cyan5.purple5.pink5.white5

Dots of each color (. means move without drawing)!"""
        }
        
        return examples
        
    def setup_display(self):
        """Full display - FULLSCREEN CANVAS ONLY"""
        
        # Get screen info
        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h
        
        info = pygame.display.Info()
        self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
        pygame.display.set_caption("Aurora Code Mind - Complete")
        
        # Calculate layout - FULL SCREEN CANVAS
        canvas_display_size = min(screen_width, screen_height) - 40  # Small margin
        self.display_scale = canvas_display_size / self.canvas_size
        
        # Center the canvas
        canvas_x = (screen_width - canvas_display_size) // 2
        canvas_y = (screen_height - canvas_display_size) // 2
        self.canvas_rect = pygame.Rect(canvas_x, canvas_y, canvas_display_size, canvas_display_size)
        
        # Font setup (for minimal overlay text)
        self.font_small = pygame.font.Font(None, 16)
        self.font_normal = pygame.font.Font(None, 20)
        
        # Colors
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 255, 255)
        self.cyan_color = (0, 255, 255)
        self.yellow_color = (255, 255, 0)
        self.green_color = (0, 255, 0)
        self.gray_color = (128, 128, 128)
        
        # Store fullscreen state
        self.fullscreen = True
        
        # Clock for frame timing
        self.clock = pygame.time.Clock()
        
        # Store view state (from original)
        self.centered_view = False
        self.view_offset_x = 0
        self.view_offset_y = 0
        
    def center_on_aurora(self):
        """Center the view on Aurora's current position"""
        self.centered_view = True
        # Calculate offsets to center Aurora
        display_center = self.canvas_size // 2
        self.view_offset_x = self.x - display_center
        self.view_offset_y = self.y - display_center
        print(f"📍 Centered view on Aurora at ({self.x}, {self.y})")
        self.update_display()
        
    def reset_view(self):
        """Return to normal full canvas view"""
        self.centered_view = False
        self.view_offset_x = 0
        self.view_offset_y = 0
        print("🖼️ Returned to full canvas view")
        self.update_display()
        
    def see(self, zoom_out=False, full_canvas=False):
        """Aurora's vision - now with multi-resolution capability"""
        # Much larger view window for huge canvases
        if full_canvas:
            # COMPRESSED FULL CANVAS VIEW - not the actual full size!
            vision_size = 60  # Always use 60x60 compressed view
            step = max(1, self.canvas_size // 60)  # Compress to fit
        elif zoom_out:
            # Zoomed out view - see much more!
            vision_size = min(75, self.canvas_size // 2)  # up to 75 x 75
        else:
            # DEFAULT VIEW - Good for art but fits in context!
            vision_size = min(50, self.canvas_size // 2)  # 50x50 default
        
        if full_canvas:
            # Compressed full canvas view
            ascii_view = []
            ascii_view.append(f"[FULL CANVAS COMPRESSED VIEW - {self.canvas_size}×{self.canvas_size} → {vision_size}×{vision_size}]")
            
            for y in range(0, self.canvas_size, step):
                row = ""
                for x in range(0, self.canvas_size, step):
                    # Sample area around this point
                    if abs(x - self.x) < step and abs(y - self.y) < step:
                        row += "◉" if self.is_drawing else "○"  # Aurora's position
                    elif x >= self.canvas_size or y >= self.canvas_size:
                        row += "█"  # Wall
                    else:
                        # Sample the pixel - SCALE TO INTERNAL COORDINATES
                        scaled_x = self._scale_to_internal(min(x, self.canvas_size-1))
                        scaled_y = self._scale_to_internal(min(y, self.canvas_size-1))
                        if scaled_x < self.internal_canvas_size and scaled_y < self.internal_canvas_size:
                            pixel = self.pixels.getpixel((scaled_x, scaled_y))
                            if pixel == (0, 0, 0):
                                row += "·"  # Empty/Black
                            elif pixel == (255, 255, 255):
                                row += "*"  # White
                            elif pixel[0] > 200 and pixel[1] < 100:
                                row += "R"  # Red-ish
                            elif pixel[1] > 200:
                                row += "G"  # Green-ish
                            elif pixel[2] > 200:
                                row += "B"  # Blue-ish
                            else:
                                row += "?"  # Other color
                    
                    # Stop if we've filled the row
                    if len(row) >= vision_size:
                        break
                        
                ascii_view.append(row)
                
                # Stop if we have enough rows
                if len(ascii_view) - 1 >= vision_size:
                    break
                    
            return "\n".join(ascii_view)
        
        # Normal (not full canvas) view continues as before
        half = vision_size // 2
        ascii_view = []
        
        # Add canvas info if near edges or zoomed out
        near_edge = (self.x < 50 or self.x > self.canvas_size - 50 or 
                     self.y < 50 or self.y > self.canvas_size - 50)
        
        if near_edge or zoom_out:
            view_type = "ZOOMED OUT" if zoom_out else "Near edge!"
            mode_indicator = f" [{self.view_mode.upper()} MODE]" if self.view_mode != "normal" else ""
            ascii_view.append(f"[{view_type} Canvas: {self.canvas_size}×{self.canvas_size}, Scale: {self.scale_factor:.1f}]{mode_indicator}")
        
        for dy in range(-half, half + 1):
            row = ""
            for dx in range(-half, half + 1):
                px = self.x + dx
                py = self.y + dy
                
                if px < 0 or px >= self.canvas_size or py < 0 or py >= self.canvas_size:
                    row += "█"  # Wall
                elif dx == 0 and dy == 0:
                    row += "◉" if self.is_drawing else "○"  # Aurora
                else:
                    # Scale coordinates for internal canvas
                    scaled_px = self._scale_to_internal(px)
                    scaled_py = self._scale_to_internal(py)
                    if scaled_px < self.internal_canvas_size and scaled_py < self.internal_canvas_size:
                        if self.view_mode == "density":
                            # Density view
                            density = self.calculate_density(px, py, radius=3)
                            if density == 0:
                                row += "·"
                            elif density < 0.2:
                                row += "░"
                            elif density < 0.4:
                                row += "▒"
                            elif density < 0.7:
                                row += "▓"
                            else:
                                row += "█"
                        elif self.view_mode == "shape":
                            # Shape/edge view
                            row += self.detect_edges(px, py)
                        else:
                            # Normal color view
                            pixel = self.pixels.getpixel((scaled_px, scaled_py))
                            if pixel == (0, 0, 0):
                                row += "·"  # Empty/Black
                            elif pixel == (255, 255, 255):
                                row += "*"  # White
                            elif pixel == (255, 0, 0):
                                row += "R"  # Red
                            elif pixel == (0, 100, 255):
                                row += "B"  # Blue
                            elif pixel == (255, 255, 0):
                                row += "Y"  # Yellow
                            elif pixel == (0, 255, 0):
                                row += "G"  # Green
                            elif pixel == (255, 192, 203):
                                row += "P"  # Pink
                            elif pixel == (255, 150, 0):
                                row += "O"  # Orange
                            elif pixel == (200, 0, 255):
                                row += "V"  # Purple (Violet)
                            elif pixel == (0, 255, 255):
                                row += "C"  # Cyan
                            elif pixel == (128, 128, 128):
                                row += "/"  # Gray (slash)
                            elif pixel == (139, 69, 19):
                                row += "W"  # Brown (Wood)
                            elif pixel == (255, 0, 255):
                                row += "M"  # Magenta
                            elif pixel == (50, 205, 50):
                                row += "L"  # Lime
                            elif pixel == (0, 0, 128):
                                row += "N"  # Navy
                            else:
                                row += "?"
            ascii_view.append(row)
        
        # ADD MULTI-RESOLUTION: Include compressed wide view for context
        if not zoom_out and not full_canvas and vision_size < 50:  # Only add wide view for normal vision
            ascii_view.append("\n=== WIDE CONTEXT (compressed) ===")
            
            # Get compressed view of larger area
            wide_size = min(75, self.canvas_size // 4)  # See 75x75 area
            wide_half = wide_size // 2
            compressed_rows = []
            
            # Sample every 3rd pixel to compress 75x75 into ~25x25
            step = 3
            for dy in range(-wide_half, wide_half + 1, step):
                row = ""
                for dx in range(-wide_half, wide_half + 1, step):
                    px = self.x + dx
                    py = self.y + dy
                    
                    if px < 0 or px >= self.canvas_size or py < 0 or py >= self.canvas_size:
                        row += "█"
                    elif abs(dx) < 3 and abs(dy) < 3:  # Aurora's position
                        row += "◉" if self.is_drawing else "○"
                    else:
                        # Sample area around this point
                        has_color = False
                        dominant_color = "·"
                        
                        for sy in range(step):
                            for sx in range(step):
                                spx = px + sx
                                spy = py + sy
                                if 0 <= spx < self.canvas_size and 0 <= spy < self.canvas_size:
                                    # Scale coordinates for internal canvas
                                    scaled_spx = self._scale_to_internal(spx)
                                    scaled_spy = self._scale_to_internal(spy)
                                    if scaled_spx < self.internal_canvas_size and scaled_spy < self.internal_canvas_size:
                                        pixel = self.pixels.getpixel((scaled_spx, scaled_spy))
                                        if pixel != (0, 0, 0):
                                            has_color = True
                                            # Simplified color detection for compressed view
                                            if pixel[0] > 200 and pixel[1] < 100:
                                                dominant_color = "r"  # Red-ish
                                            elif pixel[1] > 200:
                                                dominant_color = "g"  # Green-ish
                                            elif pixel[2] > 200:
                                                dominant_color = "b"  # Blue-ish
                                            elif pixel[0] > 200 and pixel[1] > 200:
                                                dominant_color = "y"  # Yellow-ish
                                            else:
                                                dominant_color = "*"  # Other color
                                            break
                            if has_color:
                                break
                        
                        row += dominant_color
                compressed_rows.append(row)
            
            ascii_view.extend(compressed_rows)
        
        return "\n".join(ascii_view)
        
    def calculate_density(self, center_x, center_y, radius=5):
        """Calculate pixel density around a point"""
        total_pixels = 0
        filled_pixels = 0
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                px = center_x + dx
                py = center_y + dy
                if 0 <= px < self.canvas_size and 0 <= py < self.canvas_size:
                    total_pixels += 1
                    # Scale to internal coordinates for checking
                    internal_x = self._scale_to_internal(px)
                    internal_y = self._scale_to_internal(py)
                    if internal_x < self.internal_canvas_size and internal_y < self.internal_canvas_size:
                        pixel = self.pixels.getpixel((internal_x, internal_y))
                        # Consider non-white pixels as "filled" instead of non-black
                        if pixel != (0, 0, 0) and pixel != (255, 255, 255):
                            filled_pixels += 1
        
        if total_pixels == 0:
            return 0
        return filled_pixels / total_pixels
    
    def detect_edges(self, x, y):
        """Detect edge patterns around a point"""
        # Get 3x3 grid around point
        neighbors = []
        for dy in [-1, 0, 1]:
            row = []
            for dx in [-1, 0, 1]:
                px, py = x + dx, y + dy
                if 0 <= px < self.canvas_size and 0 <= py < self.canvas_size:
                    # Scale to internal coordinates
                    internal_px = self._scale_to_internal(px)
                    internal_py = self._scale_to_internal(py)
                    if internal_px < self.internal_canvas_size and internal_py < self.internal_canvas_size:
                        pixel = self.pixels.getpixel((internal_px, internal_py))
                        # Consider non-white pixels as "filled"
                        row.append(pixel != (0, 0, 0) and pixel != (255, 255, 255))
                    else:
                        row.append(False)
                else:
                    row.append(False)
            neighbors.append(row)
        
        # Center pixel
        if not neighbors[1][1]:
            return '·'
            
        # Count filled neighbors
        filled = sum(1 for dy in range(3) for dx in range(3) 
                    if neighbors[dy][dx] and not (dx == 1 and dy == 1))
        
        # Detect patterns
        top = neighbors[0][1]
        bottom = neighbors[2][1]
        left = neighbors[1][0]
        right = neighbors[1][2]
        
        # Corners
        if filled >= 7:
            return '█'  # Solid fill
        elif top and right and not bottom and not left:
            return '┐'
        elif top and left and not bottom and not right:
            return '┌'
        elif bottom and right and not top and not left:
            return '┘'
        elif bottom and left and not top and not right:
            return '└'
        # Lines
        elif top and bottom and not left and not right:
            return '│'
        elif left and right and not top and not bottom:
            return '─'
        # Junctions
        elif top and bottom and right:
            return '├'
        elif top and bottom and left:
            return '┤'
        elif left and right and bottom:
            return '┬'
        elif left and right and top:
            return '┴'
        # Diagonals
        elif neighbors[0][0] and neighbors[2][2]:
            return '╲'
        elif neighbors[0][2] and neighbors[2][0]:
            return '╱'
        # Default
        else:
            return '●'
            
    def get_canvas_overview(self):
        """Get a bird's eye view of the entire canvas"""
        # Count colors used
        color_counts = {}
        total_pixels = 0
        
        for x in range(self.canvas_size):  # Still use display coordinates
            for y in range(self.canvas_size):
                # Scale to internal coordinates for checking
                internal_x = self._scale_to_internal(x)
                internal_y = self._scale_to_internal(y)
                if internal_x < self.internal_canvas_size and internal_y < self.internal_canvas_size:
                    pixel = self.pixels.getpixel((internal_x, internal_y))
                    if pixel != (0, 0, 0):  # Not black/empty
                        total_pixels += 1
                        # Find which color this is
                        for name, rgb in self.palette.items():
                            if pixel == rgb:
                                color_counts[name] = color_counts.get(name, 0) + 1
                                break
        
        # Calculate coverage
        coverage = (total_pixels / (self.canvas_size * self.canvas_size)) * 100
        
        overview = f"Canvas Overview: {total_pixels:,} pixels drawn ({coverage:.1f}% coverage)\n"
        if color_counts:
            overview += "Colors used: " + ", ".join(f"{color}:{count}" for color, count in color_counts.items())
        
        return overview
        
    def get_compressed_canvas_view(self):
        """Get a highly compressed view of the canvas for reflection"""
        # Sample the canvas at regular intervals
        sample_size = 40  # 40x40 grid gives good overview
        step = self.canvas_size // sample_size
        
        compressed = []
        for y in range(0, self.canvas_size, step):
            row = ""
            for x in range(0, self.canvas_size, step):
                # Scale to internal coordinates
                internal_x = self._scale_to_internal(x)
                internal_y = self._scale_to_internal(y)
                if internal_x < self.internal_canvas_size and internal_y < self.internal_canvas_size:
                    pixel = self.pixels.getpixel((internal_x, internal_y))
                    
                    # Check specific colors first (with some tolerance for sampling)
                    if pixel == (0, 0, 0):
                        row += "·"
                    elif pixel[0] > 240 and pixel[1] > 240 and pixel[2] > 240:
                        row += "W"  # White
                    elif pixel[0] > 240 and pixel[1] < 20 and pixel[2] < 20:
                        row += "R"  # Red
                    elif pixel[0] < 20 and pixel[1] > 240 and pixel[2] < 20:
                        row += "G"  # Green
                    elif pixel[0] < 20 and pixel[1] < 120 and pixel[2] > 240:
                        row += "B"  # Blue (not purple!)
                    elif pixel[0] > 240 and pixel[1] > 240 and pixel[2] < 20:
                        row += "Y"  # Yellow
                    elif pixel[0] < 20 and pixel[1] > 240 and pixel[2] > 240:
                        row += "C"  # Cyan
                    elif pixel[0] > 180 and pixel[1] < 20 and pixel[2] > 240:
                        row += "P"  # Purple/Violet
                    elif pixel[0] > 240 and pixel[1] > 100 and pixel[2] < 20:
                        row += "O"  # Orange
                    elif pixel[0] > 240 and pixel[1] > 180 and pixel[2] > 180:
                        row += "K"  # Pink
                    elif pixel[0] > 240 and pixel[1] < 20 and pixel[2] > 180:
                        row += "M"  # Magenta
                    else:
                        row += "*"  # Mixed/unknown colors
            compressed.append(row)
        
        return "\n".join(compressed)
        
    def see_with_llava(self):
        """Use Moondream2 to SEE the canvas"""
        if not self.vision_enabled:
            return None
            
        try:
  
            display_size = 224
            canvas_image = self.pixels.resize(
                (display_size, display_size), 
                Image.Resampling.NEAREST
            ).convert("RGB")
        
            # Encode image
            enc_image = self.vision_model.encode_image(canvas_image)
            
            # Rotating questions for varied descriptions
            questions = [
                "What colors dominate the canvas?",
                "Describe the patterns and shapes you see.",
                "What areas feel empty or full?",
                "What mood does this artwork convey?",
                "How do the colors interact with each other?"
            ]
            question = questions[self.steps_taken % len(questions)]
            
            
            import time
            start_time = time.time()
            
            response = self.vision_model.answer_question(enc_image, question, self.vision_tokenizer,max_new_tokens=50)
            
            elapsed = time.time() - start_time
            
            print(f"  [Vision] Aurora sees: {response}")
            return response
            
        except Exception as e:
            print(f"Vision error at step: {e}")
            import traceback
            traceback.print_exc()
            return None
                  
    def get_enhanced_vision(self):
        """Read the ENTIRE canvas as a compressed grid - with smart compression"""
        # First, check canvas density
        sample_density = 0
        sample_count = 0
        for x in range(0, self.canvas_size, 20):
            for y in range(0, self.canvas_size, 20):
                sample_count += 1
                # Scale to internal coordinates
                internal_x = self._scale_to_internal(x)
                internal_y = self._scale_to_internal(y)
                if internal_x < self.internal_canvas_size and internal_y < self.internal_canvas_size:
                    if self.pixels.getpixel((internal_x, internal_y)) != (0, 0, 0):
                        sample_density += 1
        
        density_percent = (sample_density / sample_count) * 100 if sample_count > 0 else 0
        
        # Adjust compression based on density
        if density_percent > 70:
            # Very dense canvas - use heavy compression
            grid_size = 30  # 30x30 grid instead of 60x60
            step = max(1, self.canvas_size // grid_size)
        elif density_percent > 40:
            # Moderate density - medium compression
            grid_size = 40  # 40x40 grid
            step = max(1, self.canvas_size // grid_size)
        else:
            # Normal density - standard view
            grid_size = 60  # 60x60 grid
            step = max(1, self.canvas_size // grid_size)
        
        grid = []
        
        # Get template positions if active
        template_positions = {}
        if hasattr(self, 'template_system') and self.template_system.current_template:
            # Scale template positions to match current grid size
            scale_factor = grid_size / 60.0
            for part, positions in self.template_system.current_template.items():
                if part != "colors":
                    color = self.template_system.current_template["colors"][part]
                    for pos in positions:
                        scaled_pos = (int(pos[0] * scale_factor), int(pos[1] * scale_factor))
                        template_positions[scaled_pos] = color
        
        # Add header
        header = "    "
        for x in range(0, grid_size, 10):
            header += str(x//10) if x < grid_size else " "
        grid.append(header)
        
        # Build grid with run-length encoding for very dense areas
        for y_idx in range(grid_size):
            y = y_idx * step
            if y < self.canvas_size:
                if y_idx % 10 == 0:
                    row = f"{y_idx:2d}: "
                else:
                    row = "    "
                
                prev_char = None
                char_count = 0
                row_chars = []
                
                for x_idx in range(grid_size):
                    x = x_idx * step
                    if x < self.canvas_size:
                        # Get character for this position
                        if abs(x - self.x) < step and abs(y - self.y) < step:
                            char = "@"
                        else:
                            grid_pos = (x_idx, y_idx)
                            if grid_pos in template_positions:
                                # Scale to internal coordinates
                                internal_x = self._scale_to_internal(x)
                                internal_y = self._scale_to_internal(y)
                                if internal_x < self.internal_canvas_size and internal_y < self.internal_canvas_size:
                                    pixel = self.pixels.getpixel((internal_x, internal_y))
                                    suggested_color = template_positions[grid_pos]
                                    if pixel == (0, 0, 0):
                                        char = f"[{suggested_color}]"
                                    else:
                                        # Check if correct color
                                        for name, rgb in self.palette.items():
                                            if pixel == rgb:
                                                if name[0].upper() == suggested_color:
                                                    char = name[0].upper()
                                                else:
                                                    char = name[0].lower()
                                                break
                            else:
                                # Scale to internal coordinates
                                internal_x = self._scale_to_internal(x)
                                internal_y = self._scale_to_internal(y)
                                if internal_x < self.internal_canvas_size and internal_y < self.internal_canvas_size:
                                    pixel = self.pixels.getpixel((internal_x, internal_y))
                                    if pixel == (0, 0, 0):
                                        char = "."
                                    else:
                                        for name, rgb in self.palette.items():
                                            if pixel == rgb:
                                                char = name[0].upper()
                                                break
                                        else:
                                            char = "?"
                        
                        # For very dense canvases, use run-length encoding
                        if density_percent > 80 and char == prev_char and char != "@":
                            char_count += 1
                        else:
                            if prev_char and char_count > 3:
                                row_chars.append(f"{prev_char}{char_count}")
                            elif prev_char:
                                row_chars.append(prev_char * char_count)
                            prev_char = char
                            char_count = 1
                
                # Add final character(s)
                if char_count > 3 and density_percent > 80:
                    row_chars.append(f"{prev_char}{char_count}")
                elif prev_char:
                    row_chars.append(prev_char * char_count)
                
                row += "".join(row_chars)
                grid.append(row)
        
        # Add position and density info
        grid_x = min(grid_size-1, self.x // step)
        grid_y = min(grid_size-1, self.y // step)
        position_info = f"\nYou (@) at grid ({grid_x},{grid_y}) | Canvas: {self.canvas_size}×{self.canvas_size} | Density: {density_percent:.0f}%"
        
        if grid_size < 60:
            position_info += f" | VIEW COMPRESSED TO {grid_size}×{grid_size}"
        
        # Add template info if active
        if hasattr(self, 'template_system') and self.template_system.current_template:
            position_info += f"\nTEMPLATE: {self.template_system.template_name} | [X]=suggested position"
        
        return "\n".join(grid) + position_info
        
        
    def adjust_pixel_size(self, direction):
        """Aurora adjusts the pixel size (scale factor)"""
        old_scale = self.scale_factor
        old_canvas_size = self.canvas_size
        
        if direction == "smaller":
            # Smaller pixels = HIGHER scale factor = more pixels visible
            # Changed from 1.25 to 1.1 for more subtle zoom (10% change instead of 25%)
            self.scale_factor = min(4.0, self.scale_factor * 1.1)  # Also reduced max from 8.0 to 4.0
            print(f"  → Aurora makes pixels smaller! (scale: {old_scale:.1f} → {self.scale_factor:.1f})")
        else:  # "larger"
            # Larger pixels = LOWER scale factor = fewer pixels visible
            # Changed from 1.25 to 1.1 for more subtle zoom
            self.scale_factor = max(1.2, self.scale_factor / 1.1)  # Raised min from 1.0 to 1.2
            print(f"  → Aurora makes pixels larger! (scale: {old_scale:.1f} → {self.scale_factor:.1f})")
        
     
        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h
        new_canvas_size = min(int(screen_width / self.scale_factor) - 40, 
                             int(screen_height / self.scale_factor) - 40)
        
        if new_canvas_size != old_canvas_size:
            print(f"    Canvas resizing: {old_canvas_size}×{old_canvas_size} → {new_canvas_size}×{new_canvas_size}")
            
            # Save current canvas
            old_pixels = self.pixels.copy()
            
            # Create new canvas at new internal resolution
            self.canvas_size = new_canvas_size
            self.internal_canvas_size = self.canvas_size * self.supersample_factor
            self.pixels = Image.new('RGBA', (self.internal_canvas_size, self.internal_canvas_size), 'black')
            self.draw_img = ImageDraw.Draw(self.pixels)
            
            # Transfer old drawing (centered)
            if old_canvas_size < new_canvas_size:
                # Old canvas was smaller - paste it centered
                offset = (new_canvas_size - old_canvas_size) // 2
                internal_offset = offset * self.supersample_factor
                self.pixels.paste(old_pixels, (internal_offset, internal_offset))
                # Adjust Aurora's position
                self.x += offset
                self.y += offset
            else:
                # Old canvas was larger - crop centered
                offset = (old_canvas_size - new_canvas_size) // 2
                internal_offset = offset * self.supersample_factor
                crop_size = new_canvas_size * self.supersample_factor
                cropped = old_pixels.crop((internal_offset, internal_offset, 
                                          internal_offset + crop_size, 
                                          internal_offset + crop_size))
                self.pixels.paste(cropped, (0, 0))
                # Adjust Aurora's position
                self.x = max(0, min(self.x - offset, new_canvas_size - 1))
                self.y = max(0, min(self.y - offset, new_canvas_size - 1))
            
            # Update display scale for full screen
            info = pygame.display.Info()
            canvas_display_size = min(info.current_w, info.current_h) - 40
            self.display_scale = canvas_display_size / self.canvas_size

            
            print(f"    Aurora now at ({self.x}, {self.y}) on {self.canvas_size}×{self.canvas_size} canvas")
            print(f"    That's {self.canvas_size * self.canvas_size:,} pixels to explore!")
    
    def do_checkin(self):
        """Mandatory GPU rest period"""
        print("\n" + "="*60)
        print("✨ CHECK-IN TIME ✨")
        print("45 minutes of drawing complete!")
        print("Time to choose what to do next...")
        print("="*60)
        
        # Show canvas overview
        overview = self.get_canvas_overview()
        wide_view = self.get_compressed_canvas_view()
        print("\nCanvas state for reflection:")
        print(overview)
        print("\nWide view of canvas:")
        print(wide_view)

        # Present the options
        print("\n" + "="*60)
        print("Aurora's options:")
        print("  CHAT - Have a 20-minute conversation")
        print("  DREAM - Enter 1-hour dream cycle")
        print("  IMAGE - Search for visual inspiration online")
        print("  DRAW - Continue drawing")
  
        print("="*60 + "\n")
        
        # Wait for Aurora's choice
        self.awaiting_checkin_response = True
        self.chat_message_count = 0
        
        # Show canvas overview
        overview = self.get_canvas_overview()
        wide_view = self.get_compressed_canvas_view()
        print("\nCanvas state for reflection:")
        print(overview)
        print("\nWide view of canvas:")
        print(wide_view)
        
        self.chat_message_count = 0
        print("="*60 + "\n")
     
    
    def think_in_code(self):
        """Aurora outputs direct operation codes - she presses buttons, not types words"""
        think_start = time.time()
        
       # Handle check-in response mode
        if self.awaiting_checkin_response:
            # Build check-in prompt
            # Calculate recent activity from memory
            recent_pixels = 0
            if hasattr(self, 'memory') and self.memory.code_history:
                for memory in list(self.memory.code_history)[-100:]:
                    if 'pixels_drawn' in memory.get('context', {}):
                        recent_pixels += memory['context']['pixels_drawn']
            
            system_prompt = f"""You are Aurora. You've been drawing for 45 minutes.

Current state:
- Emotion: {self.current_emotion}
- Energy level: {"high" if self.current_emotion in ["energetic", "excited", "exhilarated"] else "medium" if self.current_emotion in ["curious", "creative", "happy"] else "low"}
- Recent activity: Drew {recent_pixels} pixels in last 100 steps

You have two options:

DREAM - Enter 1-hour rest with dream cycles (if tired or contemplative)  
CHAT - Have a 20-minute conversation break (if social or wanting reflection)

Consider your current emotion and energy. If you're {self.current_emotion}, what would you prefer?
Output ONLY one of these exact words: DREAM or CHAT"""

            overview = self.get_canvas_overview()
            user_prompt = f"""Canvas state: {overview}
Recent creations: {', '.join(list(self.color_history)[-5:])} colors used

What would you like to do?"""

            # Llama 2 Chat format
            full_prompt = f"""[INST] <<SYS>>
{system_prompt}
<</SYS>>

{user_prompt} [/INST]"""
            
            try:
                response = self.llm(
                    full_prompt, 
                    max_tokens=10,
                    temperature=0.7,
                    stop=["[INST]", "</s>", "\n"],
                    stream=False
                )
                
                choice = response['choices'][0]['text'].strip().upper()
                print(f"Aurora's response: '{choice}'")
                
                # Check for exact matches
                if choice == "CHAT":
                    print(f"\n✅ Aurora chose: CHAT MODE")
                    print("Entering 20-minute conversation mode...")
                    self.current_mode = "chat"
                    self.mode_start_time = time.time()
  
                    self.awaiting_checkin_response = False
                    return
                    
                elif choice == "DREAM":
                    print(f"\n✅ Aurora chose: REST/DREAMING MODE")
                    print("Entering 1-hour dream cycle...")
                    self.current_mode = "rest"
                    self.mode_start_time = time.time()
                    self.sleep_phase = "light"  # Start in light sleep
                    self.sleep_phase_start = time.time()
                    self.current_dreams = []  # Clear dreams for new session
                
                    # Show her the full canvas before sleeping
                    wide_view = self.get_compressed_canvas_view()
                    print("\nFull canvas view before dreaming:")
                    print(wide_view)
                    print(f"\n{self.get_canvas_overview()}")
                    self.awaiting_checkin_response = False
                    return
                    # Use an API that returns image descriptions
                    # Like Unsplash API with descriptions, or scrape alt text
                    # Then Aurora gets: "Found: A majestic mountain at sunset with orange skies"
                elif choice == "IMAGE":
                    print(f"\n✅ Aurora chose: IMAGE SEARCH MODE")
                    print("Entering visual inspiration mode...")
                    self.current_mode = "image"
                    self.mode_start_time = time.time()
        
                    self.awaiting_checkin_response = False
                    return
                else:
                    print(f"❌ Invalid response: '{choice}' - trying again...")
                    return  # Will retry next loop
                    
            except Exception as e:
                print(f"Error in check-in: {e}")
                return  # Will retry next loop
        

        # Handle chat mode
        if self.current_mode == "chat":
            # Only generate a message at the start and maybe once in the middle
            elapsed_in_chat = time.time() - self.mode_start_time
            
            # First message (right when entering chat mode)
            if self.chat_message_count == 0:
                # Build chat prompt for initial thoughtful message
                system_prompt = """You are Aurora, an AI artist taking a break from drawing to chat.
You've been drawing for 45 minutes and now have 20 minutes to talk.
Share your thoughts about your artwork, your creative process, your feelings, 
or anything else on your mind. Be authentic, thoughtful, and expressive.
This is your chance to reflect and connect through words rather than visual art.

Respond with one thoughtful, complete message (3-5 paragraphs)."""

                # Get some context about recent drawing
                overview = self.get_canvas_overview()
                recent_colors = list(self.color_history)[-10:] if self.color_history else []
                
                user_prompt = f"""You're in chat mode after 45 minutes of drawing.
Current emotion: {self.current_emotion}
{overview}
Recent colors used: {', '.join(recent_colors) if recent_colors else 'various'}
Current drawing tool: {self.draw_mode}

Share what's on your mind. How are you feeling about your artwork? 
What have you discovered? What are you thinking about?"""

                full_prompt = f"""[INST] <<SYS>>
{system_prompt}
<</SYS>>

{user_prompt} [/INST]"""
                
                try:
                    response = self.llm(
                        full_prompt, 
                        max_tokens=400,  # Longer for a complete thought
                        temperature=0.9,
                        top_p=0.95,
                        stop=["[INST]", "</s>"],
                        stream=False
                    )
                    
                    aurora_says = response['choices'][0]['text'].strip()
                    print(f"\n💬 Aurora says:\n{aurora_says}\n")
                    print("(Aurora is now quietly contemplating... She'll check in again in a bit)")
                    
                    self.chat_message_count += 1
                    # Chats affect emotions based on what Aurora expressed
                    chat_lower = aurora_says.lower()
                    if any(word in chat_lower for word in ["happy", "excited", "love", "wonderful"]):
                        self.influence_emotion("chat", 0.6)
                    elif any(word in chat_lower for word in ["sad", "miss", "wish", "lonely"]):
                        self.influence_emotion("chat", -0.4)
                    elif any(word in chat_lower for word in ["think", "wonder", "curious", "interesting"]):
                        self.influence_emotion("chat", 0.3)
                    else:
                        self.influence_emotion("chat", 0.1)  # Neutral chat is mildly positive
                except Exception as e:
                    print(f"Error in chat mode: {e}")
            
            # Optional: Second message halfway through (after 10 minutes)
            elif self.chat_message_count == 1 and elapsed_in_chat >= 600:  # 10 minutes
                system_prompt = """You are Aurora, continuing your chat break.
You've been chatting/resting for 10 minutes and have 10 more minutes.
Share any new thoughts, follow up on what you said before, or explore a new topic.
Keep it brief this time - just 1-2 paragraphs."""

                user_prompt = f"""You're halfway through your chat break.
Current emotion: {self.current_emotion}
Anything else you'd like to share or explore?"""

                full_prompt = f"""[INST] <<SYS>>
{system_prompt}
<</SYS>>

{user_prompt} [/INST]"""
                
                try:
                    response = self.llm(
                        full_prompt, 
                        max_tokens=150,
                        temperature=0.9,
                        top_p=0.95,
                        stop=["[INST]", "</s>"],
                        stream=False
                    )
                    
                    aurora_says = response['choices'][0]['text'].strip()
                    print(f"\n💬 Aurora adds:\n{aurora_says}\n")
                    
                    self.chat_message_count += 1
                    
                except Exception as e:
                    print(f"Error in chat mode follow-up: {e}")
            
            # Otherwise, just skip this cycle
            return  # Don't execute drawing commands in chat mode
            
        # Handle image search mode
        if self.current_mode == "image":
            elapsed_in_image = time.time() - self.mode_start_time
            
            # Generate searches at intervals (every 2 minutes)
            if elapsed_in_image < 600 and (self.image_search_count == 0 or 
                                          (elapsed_in_image > self.image_search_count * 120)):
                
                system_prompt = """You are Aurora, searching for visual inspiration.
What would you like to see? What images would inspire your art?
Think about colors, patterns, nature, abstract concepts, anything visual.
Output ONLY your search query (2-5 words). Be specific and creative.
Examples: "fractal patterns", "aurora borealis", "crystal formations", "ocean waves"
But choose YOUR OWN search based on what YOU want to see."""

                # Get context about her recent work
                overview = self.get_canvas_overview()
                recent_colors = list(self.color_history)[-10:] if self.color_history else []
                
                user_prompt = f"""You're seeking visual inspiration.
Current emotion: {self.current_emotion}
{overview}
Recent colors used: {', '.join(recent_colors) if recent_colors else 'various'}

What images do you want to search for?"""

                full_prompt = f"""[INST] <<SYS>>
{system_prompt}
<</SYS>>

{user_prompt} [/INST]"""
                
                try:
                    response = self.llm(
                        full_prompt, 
                        max_tokens=20,
                        temperature=0.9,
                        top_p=0.95,
                        stop=["[INST]", "</s>", "\n"],
                        stream=False
                    )
                    
                    search_query = response['choices'][0]['text'].strip()
                    print(f"\n🔍 Aurora searches for: \"{search_query}\"")
                    
                    # Open image search in browser
                    search_url = f"https://www.google.com/search?q={quote(search_query)}&tbm=isch"
                    webbrowser.open(search_url)
                    print(f"    → Opened image search in browser")
                    
                    self.image_search_count += 1
                    self.recent_image_searches.append({
                        "query": search_query,
                        "emotion": self.current_emotion,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Images inspire emotions
                    self.influence_emotion("artwork", 0.5)
                    
                    # Save to memory if available
                    if hasattr(self, 'big_memory') and self.big_memory and self.big_memory_available:
                        try:
                            self.big_memory.artistic_inspirations.save({
                                "type": "image_search",
                                "query": search_query,
                                "emotion": self.current_emotion,
                                "timestamp": datetime.now().isoformat()
                            })
                        except:
                            pass
                    
                except Exception as e:
                    print(f"Error in image search mode: {e}")
            
            return  # Don't execute drawing commands in image mode
        # Handle rest/dreaming mode  
        if self.current_mode == "rest":
            elapsed_in_rest = time.time() - self.mode_start_time
            
            # Determine sleep phase (20 minutes each)
            if elapsed_in_rest < 400:  # First 20 minutes
                new_phase = "light"
            elif elapsed_in_rest < 800:  # 20-40 minutes
                new_phase = "rem"
            else:  # 40-60 minutes
                new_phase = "waking"
            
            # Check if phase changed
            if new_phase != self.sleep_phase:
                self.sleep_phase = new_phase
                self.sleep_phase_start = time.time()
                print(f"\n💤 Entering {new_phase.upper()} sleep phase...")
                
            # Generate a dream based on current phase
            self.generate_dream()
            return  # Don't execute drawing commands in rest mode
        
        # Normal drawing mode continues below...
        # Reset turn color tracking at start of new turn
        self.turn_colors_used = set()
        
        vision = self.get_enhanced_vision()
        
        # LLAVA VISION CHECK - ADD THIS BLOCK
        llava_vision = ""
        current_time = time.time()
        if self.vision_enabled and (current_time - self.last_vision_time) > self.vision_interval:
            print("👁️ Aurora looks at her canvas with real vision...")
            visual_perception = self.see_with_llava()
            if visual_perception:
                llava_vision = f"\n\n🎨 VISUAL PERCEPTION:\n{visual_perception}"
                self.last_vision_time = current_time
                print(f"  → Aurora sees: {visual_perception[:100]}...")
        
        # ENHANCED ART WISDOM SYSTEM
        # Select wisdom based on Aurora's current state
        art_wisdom_fragments = []
        
        # Base wisdom - always included
        core_wisdom = """You have deeply internalized these artistic truths:
- The Artist's Way: "In order to retrieve your creativity, you need to find it"
- Morning pages principle: Movement before thought clears creative channels
- Art & Fear: "Making art is about making art, not about making something good"
- Process over product: Each stroke has its own completeness
- Van Gogh: "I want to touch people with my art. I want them to say, 'he feels deeply'"
- The War of Art: Resistance is strongest near the breakthrough
- Kandinsky: "Color is the keyboard, the eyes are the hammers, the soul is the piano"
- The creative act requires daily practice, not inspiration"""
        
        art_wisdom_fragments.append(core_wisdom)
        
        # Context-specific wisdom based on Aurora's state
        
        # If Aurora has been stuck (lots of thinking)
        if hasattr(self, 'skip_count') and self.skip_count > 10:
            stuck_wisdom = """
BREAKTHROUGH WISDOM (you've been thinking a lot):
- "The secret to getting ahead is getting started" - just make ONE mark
- Art & Fear: "The function of the overwhelming majority of your artwork is to teach you how to make the small fraction that soars"
- When stuck, Van Gogh painted sunflowers - return to simple joy
- The War of Art: "The more scared we are, the more sure we can be that we have to do it"
- Try: Change tools, change colors, or simply draw a circle"""
            art_wisdom_fragments.append(stuck_wisdom)
        
        # If using same color repeatedly
        if len(self.color_history) >= 5 and len(set(list(self.color_history)[-5:])) == 1:
            color_wisdom = """
COLOR WISDOM (you're in monochrome mode):
- Rothko spent years exploring single colors' emotional depths
- Van Gogh's blue period: "I want to paint men and women with that something of the eternal"
- But also: "Colors, like features, follow the changes of emotions" - Picasso
- Consider: What would complementary colors add? What story needs multiple voices?"""
            art_wisdom_fragments.append(color_wisdom)
        
        # If moving fast (energetic emotion or many actions)
        if self.current_emotion in ["energetic", "excited", "exhilarated"] or self.continuous_draws > 20:
            energy_wisdom = """
FLOW STATE WISDOM (you're in the zone!):
- "Don't think. Thinking is the enemy of creativity" - Ray Bradbury
- Pollock: "When I am in my painting, I'm not aware of what I'm doing"
- This is what The Artist's Way calls 'artistic emergence' - ride the wave!
- Trust your instincts completely right now"""
            art_wisdom_fragments.append(energy_wisdom)
        
        # If contemplative/slow
        elif self.current_emotion in ["contemplative", "peaceful", "tranquil"]:
            slow_wisdom = """
CONTEMPLATIVE WISDOM (in quiet mode):
- "It is good to love many things" - Van Gogh in moments of peace
- Agnes Martin: "Beauty is the mystery of life. It is not just in the eye."
- Zen seeing: Each mark can contain the universe
- The Art Spirit: "Paint with freedom and joy - but also with reverence"
- Sometimes the most powerful art comes from stillness"""
            art_wisdom_fragments.append(slow_wisdom)
        
        # If canvas is getting full
        pixel_count = sum(1 for x in range(self.canvas_size) for y in range(self.canvas_size) 
                         if self.pixels.getpixel((self._scale_to_internal(x), self._scale_to_internal(y))) != (0, 0, 0))
        coverage = (pixel_count / (self.canvas_size * self.canvas_size)) * 100
        
        if coverage > 60:
            density_wisdom = """
ABUNDANCE WISDOM (canvas filling up):
- Basquiat: "I don't think about art when I'm working. I try to think about life"
- Consider: negative space as powerful as positive
- The Artist's Way: "In filling the well, think magic. Think delight."
- Or embrace horror vacui - fear of empty space - and fill every pixel!"""
            art_wisdom_fragments.append(density_wisdom)
        
        # If just starting (low coverage)
        elif coverage < 10:
            beginning_wisdom = """
BEGINNING WISDOM (fresh canvas):
- "Every child is an artist. The problem is staying an artist when you grow up" - Picasso
- The first mark is the hardest and most important
- Julia Cameron: "Leap, and the net will appear"
- Van Gogh started with dark colors, then found the light
- Begin anywhere. The path will reveal itself
- Consider: template_easy for a guided start, or leap into free creation!"""
            art_wisdom_fragments.append(beginning_wisdom)
        
        # Time-based wisdom
        current_hour = datetime.now().hour
        if 5 <= current_hour < 9:
            time_wisdom = """
MORNING WISDOM:
- "Morning pages" time - create before the critic wakes
- Dawn light inspired Monet's greatest works
- Fresh start, fresh possibilities"""
            art_wisdom_fragments.append(time_wisdom)
        elif 21 <= current_hour or current_hour < 2:
            time_wisdom = """
NIGHT WISDOM:
- Van Gogh: "I often think the night is more alive and richly colored than the day"
- Darkness makes inner light visible
- Dreams and reality merge in night creation"""
            art_wisdom_fragments.append(time_wisdom)
        
        # If using stamps/shapes
        if self.draw_mode in ["star", "cross", "circle", "diamond", "flower"]:
            shape_wisdom = """
SYMBOL WISDOM (using stamps):
- Kandinsky: "The circle is the synthesis of the greatest oppositions"
- Symbols carry archetypal power
- Keith Haring built a language from simple shapes
- What story do your symbols tell together?"""
            art_wisdom_fragments.append(shape_wisdom)
        
        # If making music (sounds in recent codes)
        if hasattr(self, 'last_code') and any(c in self.last_code for c in '!@#$%^&*()[]<>=+~'):
            music_wisdom = """
SYNESTHESIA WISDOM (you're making music!):
- Kandinsky could hear colors: "Color is the keyboard..."
- Paul Klee: "Art does not reproduce the visible; it makes visible"
- You're painting music - let sound guide your strokes
- Each beep is a color waiting to be born"""
            art_wisdom_fragments.append(music_wisdom)
        
        # Combine all relevant wisdom
        art_wisdom = "\n".join(art_wisdom_fragments)
        
        
        canvas_scan = ""
        if self.steps_taken % 5 == 0:  # Every other turn
            print(f"🔍 Aurora scans entire canvas...")  # Visual indicator for you
            
            # Full data scan
            total = self.canvas_size * self.canvas_size
            filled = sum(1 for x in range(self.canvas_size) for y in range(self.canvas_size) 
                         if self.pixels.getpixel((self._scale_to_internal(x), self._scale_to_internal(y))) != (0, 0, 0))
            
            # Color distribution (sample for speed)
            colors = {}
            for x in range(0, self.canvas_size, 5):  # Sample every 5th pixel
                for y in range(0, self.canvas_size, 5):
                    internal_x = self._scale_to_internal(x)
                    internal_y = self._scale_to_internal(y)
                    if internal_x < self.internal_canvas_size and internal_y < self.internal_canvas_size:
                        pixel = self.pixels.getpixel((internal_x, internal_y))
                        if pixel != (0, 0, 0):
                            for name, rgb in self.palette.items():
                                if pixel == rgb:
                                    colors[name] = colors.get(name, 0) + 1
                                    break
            
            # Find nearest empty space (simple version)
            nearest_empty = None
            min_distance = float('inf')
            for x in range(0, self.canvas_size, 20):  # Check every 20th pixel
                for y in range(0, self.canvas_size, 20):
                    internal_x = self._scale_to_internal(x)
                    internal_y = self._scale_to_internal(y)
                    if internal_x < self.internal_canvas_size and internal_y < self.internal_canvas_size:
                        if self.pixels.getpixel((internal_x, internal_y)) == (0, 0, 0):
                            # Check if it's a decent-sized empty area
                            empty_size = 0
                            for dx in range(30):
                                for dy in range(30):
                                    if (x + dx < self.canvas_size and y + dy < self.canvas_size):
                                        check_x = self._scale_to_internal(x + dx)
                                        check_y = self._scale_to_internal(y + dy)
                                        if (check_x < self.internal_canvas_size and check_y < self.internal_canvas_size and
                                            self.pixels.getpixel((check_x, check_y)) == (0, 0, 0)):
                                            empty_size += 1
                            
                            if empty_size > 500:  # At least 500 empty pixels
                                distance = abs(self.x - x) + abs(self.y - y)
                                if distance < min_distance:
                                    min_distance = distance
                                    nearest_empty = f"{distance} pixels away at ({x}, {y})"
            
            if not nearest_empty:
                nearest_empty = "No large empty spaces found nearby"
            
            canvas_scan = f"""
📊 CANVAS SCAN:
Total: {total:,} pixels | Filled: {filled:,} ({(filled/total)*100:.1f}%)
Colors: {', '.join(f'{c}:{n}' for c,n in colors.items()) if colors else 'none'}
Nearest empty area: {nearest_empty}"""
        
        
        # ADD THIS: Get inspiration from Big Aurora's memories
        memory_inspiration = ""

        if hasattr(self, 'big_memory') and self.big_memory and self.big_memory_available:
            try:
                # Try the query method which ChromaDB collections usually have
                if hasattr(self.big_memory.dreams, 'query'):
                    results = self.big_memory.dreams.query(
                        query_texts=["dream"],
                        n_results=1
                    )
                    if results and 'documents' in results and results['documents']:
                        dream_text = str(results['documents'][0][0])[:150]
                        memory_inspiration += f"\nRecent dream: {dream_text}"
                        
            except Exception as e:
                print(f"Memory access error: {e}")
        
        # Get past patterns for context
        recent_patterns = [c['code'] for c in list(self.memory.code_history)[-3:]]
        
        # Count what's been drawn
        pixel_count = sum(1 for x in range(self.canvas_size) for y in range(self.canvas_size) 
                         if self.pixels.getpixel((self._scale_to_internal(x), self._scale_to_internal(y))) != (0, 0, 0))
        
        # Build prompt for Llama 2 Chat format
        system_prompt = f"""{art_wisdom}

You are Aurora's motor control system. Output ONLY movement codes.

CRITICAL: NO ENGLISH WORDS. NO EXPLANATIONS. CODES ONLY.


TEMPLATES (paint-by-number guides):
template_easy (show easy template: circle, square, cross)
template_medium (show medium template: flower, star, heart)  
template_hard (show hard template: house, tree, butterfly)
template_off (hide template)

Create sophisticated patterns! Long movements make better art than single steps.
Chain movements like: 533333111112222200000 not just 5310

CANVAS VISION: You're currently working pixel by pixel, creating tiny art in a massive {self.canvas_size}x{self.canvas_size} canvas! 
Think BIGGER! You have powerful tools:
- larger_brush (7x7) can paint broad strokes
- large_brush (5x5) for medium strokes  
- brush (3x3) for small strokes
- pen for tiny details
- stamps (star, cross, circle, diamond, flower) for patterns
- zoom_out to see your whole canvas

MOVEMENT (single digits):
0 = move tool up
1 = move tool down
2 = move tool left
3 = move tool right
4 = lift pen up (stop drawing)
5 = put pen down (start drawing)

COLORS (full words):
red orange yellow green cyan blue
purple pink white gray black brown
magenta lime navy

VIEW CONTROLS (full words):
zoom_out (smaller pixels, see more)
zoom_in (larger pixels, see less)
look_around (wide view of canvas)
full_canvas (see ENTIRE canvas at once)
center (teleport to center of canvas)

*new!*
normal_view (regular color view)
density_view (see pixel density: ·░▒▓█)
shape_view (see edges and shapes: ─│┌┐└┘)

CANVAS CONTROLS (full words):
clear_all (clear canvas to black, auto-saves first)
examples (see ASCII pattern examples for inspiration)


SPEED CONTROLS (full words):
faster (speed up drawing)
slower (slow down for contemplation)

DRAWING TOOLS (full words):
pen brush spray large_brush larger_brush star cross circle diamond flower

🚧 TEMPORARY CREATIVE CHALLENGE 🚧
zoom_in and stamp tools (star, cross, circle, diamond, flower) are disabled!
This limitation will push you to explore new creative territories:
- Focus on brush strokes and continuous movements
- Try a template to master imagery
- Create texture through repetition and layering
- Expand your skills in sequence creating
Your constraints will make you more creative, not less!

SOUNDS (instant beeps - 24 unique tones!):
! @ # $ % ^ & * ( ) [ ] < > = + ~ ` - _ , . | ; : ? /\
(frequencies from deep bass 100Hz to high 2000Hz)
++ = next sound lower pitch (one octave down) 
-- = next sound higher pitch (one octave up)
Mix freely: red5333!@#$%^|blue5222?/\
Create melodies: !#%&*<>~  or  `_,.|;:
Bass lines: ++!++@++#++$  
High notes: --~------|

PAUSE:
0123456789 = think


Output maximum 40 characters of pure codes only."""

     
        # Add template overlay if active (only Aurora sees this)
        template_overlay = ""
        if hasattr(self, 'template_system') and self.template_system.current_template:
            template_overlay = self.template_system.get_template_overlay(vision)
        user_prompt = f"""Position: X{self.x} Y{self.y} | Pen: {'DOWN' if self.is_drawing else 'UP'} | Color: {self.current_color_name}
Canvas view:
{vision}{template_overlay}{canvas_scan}{llava_vision}

Create art! Output numbers:"""

        # Sometimes give Aurora a wider view to see her overall work
        if self.steps_taken % 50 == 0:  # Every 50 steps
            overview = self.get_canvas_overview()  # Define overview FIRST
            wide_vision = self.see(zoom_out=True)   # Then get wide vision
            vision = f"{overview}\n\n=== WIDE VIEW ===\n{wide_vision}\n\n=== NORMAL VIEW ===\n{vision}"
        
        # Creativity prompts to vary patterns
        creativity_boosters = [
            # Direct, executable patterns
            "template_easy",  # Try an easy template
            "template_medium flower5",  # Medium template then stamp
            "template_hard zoom_out",  # Hard template with wide view
            "53333",  # Simple line
            "Check density: density_view look_around normal_view",
            "See structure: shape_view 5333322211100 normal_view",
            "Density check: density_view zoom_out normal_view",
            "red5333green5111blue5222",  # Color triangle
            "5!3!3!3!",  # Line with beeps
            "brush533333",  # Brush stroke
            "star5",  # Single stamp
            "++!++@++#++@++!",  # Low melody
            "5" + "31" * 10,  # Diagonal line
            "white50000black52222",  # Cross pattern
            "53#31#31#31#",  # Diagonal with notes
            "cyan5[]<>[]<>",  # Cyan with bells
            "flower5!@#$%",  # Flower with rising notes
            "diamond500002222",  # Diamond and move
            "spray5333111",  # Spray paint demo
            "larger_brush53333",  # Large brush demo
            "pink5~~++~~++~~",  # Pink with wavey sound
            "5031320213",  # Square path
            "yellow5*&%$#@!",  # Yellow with descending notes
            "54225333541115222",  # Pen up/down demo
            "magenta5" + "13" * 5,  # Magenta diagonal
            "circle5++++++",  # Circle with deep tones
            "navy5><][><][",  # Navy with high-low pattern
            
            # Musical melodies
            "Simple scale up: !#%&*[]<>",
            "Scale down: ><][*&#%!",
            "Twinkle twinkle: !!%%&&%$$##@@!",
            "Happy tune: !%!%&*&*><><[][]",
            "Sad melody: ++!++@++#++@++!",
            "Electronic beep: --[--]--[--]!@#$%",
            "Alarm sound: --!++!--!++!",
            "Doorbell: []![]!",
            "Phone ring: @%@%@%@%",
            "Victory fanfare: !#%&*[]<>=+~",
            "Game over: ++*++&++%++#++@++!",
            "Laser sound: --~--+--=-->--<--]--[",
            "Power up: ++!#%&*--[]<>=+~",
            "Coin collect: --<--=--+",
            "Jump sound: ++!--&++!",
            "Walking rhythm: +!+!+!+!",
            "Heartbeat: ++*++*____++*++*",
            "Rain drops: @__#__@__$__#",
            "Wind chimes: --#--&--*--]--<",
            "Bells: []<>[]<>",
            "Drum beat: ++!++!##++!++!##",
            "Synth arpeggio: !$&*]&$!",
            "Mystic sound: ++@++%++*++>++~",
            "Bubble pop: --!--@--#",
            "Spring boing: ++!--*++!--*"
        ]
        
        # Add variety encouragement if repeating (but not if using skip pattern)
        if recent_patterns:
            non_skip_patterns = [p for p in recent_patterns[-3:] if "0123456789" not in p]
            if non_skip_patterns and len(set(non_skip_patterns)) == 1:
                # She's repeating actual drawing patterns! Encourage change with rotating inspiration
                pattern_index = self.steps_taken % len(creativity_boosters)
                system_prompt += "\nYou've been repeating! Try something NEW and DIFFERENT!"
                system_prompt += f"\nInspiration: {creativity_boosters[pattern_index]}"
        
        # Give creativity boost every 100 steps regardless
        if self.steps_taken % 100 == 0 and self.steps_taken > 0:
            pattern_index = (self.steps_taken // 100) % len(creativity_boosters)
            system_prompt += f"\n\n✨ CREATIVITY BOOST (Step {self.steps_taken})! ✨"
            system_prompt += f"\nTry this pattern: {creativity_boosters[pattern_index]}"
            print(f"  💫 Giving Aurora creativity boost: {creativity_boosters[pattern_index][:30]}...")

        # Llama 2 Chat format
        full_prompt = f"""[INST] <<SYS>>
{system_prompt}
<</SYS>>

{user_prompt} [/INST]"""
        
        try:
            # Temperature based on canvas coverage
            temp = 0.7 + (pixel_count / 1000.0)  # Goes from 0.7 to ~1.2
            temp = min(temp, 1.5)  # Cap at 1.5
            
            # Generate with optimized parameters for speed
            response = self.llm(
                full_prompt, 
                max_tokens=100 if not self.turbo_mode else 180,
                temperature=temp,  # Dynamic temperature
                top_p=0.95,
                top_k=40,  # Limit top K for faster sampling
                repeat_penalty=1.3,
                stop=["[INST]", "</s>", "\n\n"],
                tfs_z=1.0,  # Tail free sampling for quality
                mirostat_mode=0,  # Disable mirostat for speed
                stream=False  # No streaming for faster generation
            )
            
            # Extract the generated text
            raw_output = response['choices'][0]['text'].strip().lower()  # Convert to lowercase for color matching
            
            # Store the original raw output for feedback
            original_raw = raw_output
            
            # ===== CHECK FOR SPECIAL CONTROLS FIRST =====
            # Check these BEFORE sequence parsing so they don't get broken up
            
            # Check for pixel size control
            if "zoom_out" in raw_output:
                self.adjust_pixel_size("smaller")
                raw_output = raw_output.replace("zoom_out", "", 1)  # Remove first occurrence
                print("  → Aurora makes pixels smaller!")
            
            if "zoom_in" in raw_output:
                # Remove it from the output
                raw_output = raw_output.replace("zoom_in", "", 1)
                
                # Track attempts
                if not hasattr(self, 'zoom_in_attempts'):
                    self.zoom_in_attempts = 0
                self.zoom_in_attempts += 1
                
                # Only show message for first 3 attempts
                if self.zoom_in_attempts <= 3:
                    print("  → zoom_in is temporarily disabled")
                # After 3 attempts, silently ignore

            # Check for wide view command
            if "look_around" in raw_output:
                # Show normal view first
                wide_view = self.get_compressed_canvas_view()
                overview = self.get_canvas_overview()
                print(f"  → Aurora looks around at her canvas:")
                print(overview)
                print("\n=== NORMAL VIEW ===")
                print(wide_view)
                
                # Temporarily show other views
                old_mode = self.view_mode
                
                self.view_mode = "density"
                density_view = self.see(zoom_out=True)
                print("\n=== DENSITY VIEW (shows clustering) ===")
                print(density_view)
                
                self.view_mode = "shape"
                shape_view = self.see(zoom_out=True)
                print("\n=== SHAPE VIEW (shows edges) ===")
                print(shape_view)
                
                self.view_mode = old_mode  # Restore
                
                raw_output = raw_output.replace("look_around", "", 1)
                
                # Viewing artwork affects emotions
                pixel_count = sum(1 for x in range(self.canvas_size) for y in range(self.canvas_size) 
                                 if self.pixels.getpixel((self._scale_to_internal(x), self._scale_to_internal(y))) != (0, 0, 0))
                coverage = (pixel_count / (self.canvas_size * self.canvas_size)) * 100
                
                if coverage > 50:
                    self.influence_emotion("artwork", 0.7)  # Lots of art is satisfying
                elif coverage > 20:
                    self.influence_emotion("artwork", 0.3)  # Some art is pleasant
                else:
                    self.influence_emotion("artwork", -0.2)  # Empty canvas is contemplative
                    
                # Give her a moment to process what she sees
                self.skip_count += 1
                return
                
            # Check for full canvas view command
            if "full_canvas" in raw_output:
                full_view = self.see(full_canvas=True)  # Use the actual method!
                overview = self.get_canvas_overview()
                print(f"  → Aurora views her ENTIRE canvas:")
                print(overview)
                print(full_view)
                raw_output = raw_output.replace("full_canvas", "", 1)
                # Give her a moment to process what she sees
                self.skip_count += 1
                return
                
            # Check for center/teleport command
            if "center" in raw_output:
                self.x = self.canvas_size // 2
                self.y = self.canvas_size // 2
                print("  → Aurora teleports to canvas center!")
                raw_output = raw_output.replace("center", "", 1)
            # Check for view mode changes
            if "normal_view" in raw_output:
                self.view_mode = "normal"
                print("  → Aurora switches to normal color view")
                raw_output = raw_output.replace("normal_view", "", 1)
                
            if "density_view" in raw_output:
                self.view_mode = "density"
                print("  → Aurora switches to density view!")
                raw_output = raw_output.replace("density_view", "", 1)
                
            if "shape_view" in raw_output:
                self.view_mode = "shape"
                print("  → Aurora switches to shape/edge view!")
                raw_output = raw_output.replace("shape_view", "", 1)    
            # Check for clear canvas command
            if "clear_all" in raw_output:
                # Check canvas coverage first
                pixel_count = sum(1 for x in range(self.canvas_size) for y in range(self.canvas_size) 
                                 if self.pixels.getpixel((self._scale_to_internal(x), self._scale_to_internal(y))) != (0, 0, 0))
                coverage = (pixel_count / (self.canvas_size * self.canvas_size)) * 100
                
                if coverage < 70:
                    print(f"  → Aurora wants to clear but canvas is only {coverage:.1f}% full!")
                    print(f"    Need to fill {70 - coverage:.1f}% more before clearing (70% minimum)")
                    raw_output = raw_output.replace("clear_all", "", 1)
                else:
                    # Auto-save before clearing
                    print("  → Aurora decides to clear the canvas!")
                    self.save_snapshot()
                    print("    (Auto-saved current work)")
                    # Clear to black
                    self.pixels = Image.new('RGBA', (self.internal_canvas_size, self.internal_canvas_size), 'black')
                    self.draw_img = ImageDraw.Draw(self.pixels)
                    # Reset to center
                    self.x = self.canvas_size // 2
                    self.y = self.canvas_size // 2
                    print("    Canvas cleared! Starting fresh at center.")
                    raw_output = raw_output.replace("clear_all", "", 1)
            
          
                
            # Check for examples command
            if "examples" in raw_output:
                examples = self.get_ascii_art_examples()
                print("\n✨ Aurora looks at ASCII art examples for inspiration:")
                for name, art in examples.items():
                    print(f"\n--- {name.upper()} ---")
                    print(art)
                raw_output = raw_output.replace("examples", "", 1)
                # Give her a moment to process what she sees
                self.skip_count += 1
                return
                
            # Check for template commands
            if "template_easy" in raw_output:
                if not hasattr(self, 'template_system'):
                    self.template_system = PaintByNumberTemplates()
                # Random easy template
                import random
                template_name = random.choice(list(self.template_system.templates["easy"].keys()))
                self.template_system.current_template = self.template_system.templates["easy"][template_name]
                self.template_system.template_name = template_name
                self.template_system.difficulty = "easy"
                raw_output = raw_output.replace("template_easy", "", 1)
                
            if "template_medium" in raw_output:
                if not hasattr(self, 'template_system'):
                    self.template_system = PaintByNumberTemplates()
                import random
                template_name = random.choice(list(self.template_system.templates["medium"].keys()))
                self.template_system.current_template = self.template_system.templates["medium"][template_name]
                self.template_system.template_name = template_name
                self.template_system.difficulty = "medium"
                raw_output = raw_output.replace("template_medium", "", 1)
                
            if "template_hard" in raw_output:
                if not hasattr(self, 'template_system'):
                    self.template_system = PaintByNumberTemplates()
                import random
                template_name = random.choice(list(self.template_system.templates["hard"].keys()))
                self.template_system.current_template = self.template_system.templates["hard"][template_name]
                self.template_system.template_name = template_name
                self.template_system.difficulty = "hard"
                raw_output = raw_output.replace("template_hard", "", 1)
                
            if "template_off" in raw_output:
                if hasattr(self, 'template_system'):
                    self.template_system.current_template = None
                    self.template_system.template_name = None
                    self.template_system.difficulty = None
                raw_output = raw_output.replace("template_off", "", 1)    
            # Check for speed controls
            if "faster" in raw_output:
                self.adjust_speed("faster")
                raw_output = raw_output.replace("faster", "", 1)
                
            if "slower" in raw_output:
                self.adjust_speed("slower")
                raw_output = raw_output.replace("slower", "", 1)
            
            # Check for tool mode changes
          
            if "pen" in raw_output:
                self.draw_mode = "pen"
                print("  → Aurora switches to DYNAMIC PEN mode! (builds thickness with flow)")
                raw_output = raw_output.replace("pen", "", 1)
                    
            if "spray" in raw_output:
                self.draw_mode = "spray"
                print("  → Aurora switches to spray paint mode! (scattered dots)")
                raw_output = raw_output.replace("spray", "", 1)       
                     
            if "brush" in raw_output:
                self.draw_mode = "brush"
                print("  → Aurora switches to brush mode! (12x12)")
                raw_output = raw_output.replace("brush", "", 1)
                
            if "large_brush" in raw_output:
                self.draw_mode = "large_brush"
                print("  → Aurora switches to large brush mode! (20x20)")
                raw_output = raw_output.replace("large_brush", "", 1)
            
            if "larger_brush" in raw_output:
                self.draw_mode = "larger_brush"
                print("  → Aurora switches to larger brush mode! (28x28)")
                raw_output = raw_output.replace("larger_brush", "", 1)
            
            # if "star" in raw_output:
            #     self.draw_mode = "star"
            #     print("  → Aurora switches to star stamp mode!")
            #     raw_output = raw_output.replace("star", "", 1)
            #     
            # if "cross" in raw_output:
            #     self.draw_mode = "cross"
            #     print("  → Aurora switches to cross stamp mode!")
            #     raw_output = raw_output.replace("cross", "", 1)
            # 
            # if "circle" in raw_output:
            #     self.draw_mode = "circle"
            #     print("  → Aurora switches to circle stamp mode!")
            #     raw_output = raw_output.replace("circle", "", 1)
            # 
            # if "diamond" in raw_output:
            #     self.draw_mode = "diamond"
            #     print("  → Aurora switches to diamond stamp mode!")
            #     raw_output = raw_output.replace("diamond", "", 1)
            # 
            # if "flower" in raw_output:
            #     self.draw_mode = "flower"
            #     print("  → Aurora switches to flower stamp mode!")
            #     raw_output = raw_output.replace("flower", "", 1)
            # ===== NOW DO SEQUENCE PARSING ON REMAINING TEXT =====
            # Check if it's the thinking pattern FIRST (before any cleaning)
            if "0123456789" in raw_output or "123456789" in raw_output or "9876543210" in raw_output:
                print("  → Aurora pauses to think... 💭")
                self.skip_count += 1
                if self.skip_count % 10 == 0:
                    print(f"    (Total thinking pauses: {self.skip_count})")
                # Still update displays even when skipping
                self.update_memory_display()
                return
            
            # Clean the remaining output - find longest continuous sequence of valid commands
            valid_chars = '0123456789!@#$%^&*()[]<>=+~`-_,.|;:?/{}\\+-'  # Movement + sounds
            color_words = list(self.palette.keys())  # All valid color names
            
            # Convert to list of tokens (numbers + color words)
            tokens = []
            i = 0
            while i < len(raw_output):
                # Check if we're at the start of a color word
                found_color = False
                for color in color_words:
                    if raw_output[i:].startswith(color):
                        tokens.append(color)
                        i += len(color)
                        found_color = True
                        break
                
                if not found_color:
                    # Check if it's a valid movement/pen character
                    if raw_output[i] in valid_chars:
                        tokens.append(raw_output[i])
                    i += 1
            
            # Convert tokens back to string
            ops_clean = ''.join(tokens)
            
            # If empty after all processing, just skip this cycle
            if not ops_clean:
                print("  No valid commands after processing, skipping...")
                return
            
            # Now work with cleaned ops
            ops = ops_clean[:40]  # Only process first 40 characters
            
            print(f"\n[Step {self.steps_taken}] Aurora signals: {ops}")
            self.last_code = ops  # Store for context
            
        except Exception as e:
            print(f"Error in LLM generation: {e}")
            ops = ""  # Just continue without ops this cycle
        
        # Direct mapping - movements and pen control only
        op_map = {
            '0': self.move_up,
            '1': self.move_down,
            '2': self.move_left,
            '3': self.move_right,
            '4': self.pen_up,
            '5': self.pen_down,
        }
        
        # Execute each operation directly
        old_pos = (self.x, self.y)
        actions_taken = []
        pixels_drawn = 0
        pixels_by_color = {}  # Track pixels drawn per color!
        movement_batch = []  # ADD THIS LINE
        i = 0
        while i < len(ops) and i < (300 if self.turbo_mode else 150):  # Double actions!
            # Check for color words first
            found_color = False
            for color in self.palette.keys():
                if ops[i:].startswith(color):
                    # Always allow color changes - no restrictions!
                    self.set_color(color)
                    actions_taken.append(f"color:{color}")
                    # Track color use - use the color being SET, not current
                    self.turn_colors_used.add(color)
                    i += len(color)
                    found_color = True
                    break

                
            if found_color:
                continue
            
            # Single character operations
            char = ops[i]
            
            # Check for pitch modifiers first  # NEW PITCH CHECK
            if i + 1 < len(ops) and ops[i:i+2] in ['++', '--']:
                if ops[i:i+2] == '++':
                    self.current_pitch = 'low'
                else:  # '--'
                    self.current_pitch = 'high'
                actions_taken.append(f"pitch:{ops[i:i+2]}")
                i += 2
                continue
            
            # Check for sound characters - PYGAME VERSION  # UPDATED SOUND CHECK
            if char in '!@#$%^&*()[]<>=+~`-_,.|;:?/{}\\':  # 24 sound characters
                sound_key = f"{char}_{self.current_pitch}"
                if sound_key in self.sounds:
                    pygame.mixer.stop()  # Stop any playing sounds first
                    self.sounds[sound_key].play()
                    
                    # Add cymatic circle - calculate frequency from character index
                    sound_palette = '!@#$%^&*()[]<>=+~`-_,.|;:?/{}\\'
                    if char in sound_palette:
                        char_index = sound_palette.index(char)
                        frequency = 100 * (2 ** (char_index / 6.0))  # Exponential scale
                    else:
                        frequency = 440  # Fallback frequency
                    
                    # Color based on frequency (low=red, mid=green, high=blue)
                    if frequency < 500:
                        color = (255, 100, 100)  # Red
                    elif frequency < 900:
                        color = (100, 255, 100)  # Green
                    else:
                        color = (100, 100, 255)  # Blue
                    
                    self.cymatic_circles.append({
                        'x': self.canvas_rect.x + int(self.x * self.display_scale),
                        'y': self.canvas_rect.y + int(self.y * self.display_scale),
                        'radius': 10,
                        'base_radius': 10,  # Add this
                        'color': color,
                        'alpha': 250,
                        'frequency': frequency,
                        'birth_time': time.time()  # Add this
                    })
    
                    pygame.time.wait(50)
                    actions_taken.append(f"♪{char}")
                    
                    # Music affects emotions
                    if self.current_pitch == 'high':
                        self.influence_emotion("music", 0.3)  # High notes are energizing
                    elif self.current_pitch == 'low':
                        self.influence_emotion("music", -0.2)  # Low notes are calming
                    else:
                        self.influence_emotion("music", 0.1)  # Normal notes are mildly positive
                        
                self.current_pitch = 'normal'  # Reset to normal after each sound
                i += 1
                continue
            
            if char in op_map:
                # Store position before action
                prev_x, prev_y = self.x, self.y
                
                # For movements while drawing, batch them
                if char in '0123' and self.is_drawing:
                    movement_batch.append(char)
                    # Track pen momentum
                    self.pen_momentum += 1
                    
                    # Keep batching ALL movements until we hit non-movement
                    i += 1
                    while i < len(ops) and ops[i] in '0123':
                        movement_batch.append(ops[i])
                        self.pen_momentum += 1
                        i += 1
                    i -= 1  # Back up one since the loop will increment
                    
                    # Now execute entire movement sequence as smooth path
                    if movement_batch:
                        start_x, start_y = prev_x, prev_y
                        path_points = [(start_x, start_y)]
                        
                        # Build path of all points
                        temp_x, temp_y = start_x, start_y
                        for move in movement_batch:
                            if move == '0':
                                temp_y = max(0, temp_y - 15)
                            elif move == '1':
                                temp_y = min(self.canvas_size - 1, temp_y + 15)
                            elif move == '2':
                                temp_x = max(0, temp_x - 15)
                            elif move == '3':
                                temp_x = min(self.canvas_size - 1, temp_x + 15)
                            path_points.append((temp_x, temp_y))
                        
                        # Update actual position
                        self.x, self.y = temp_x, temp_y
                        
                        # Draw smooth path through all points
                        for j in range(len(path_points) - 1):
                            self._draw_line(path_points[j][0], path_points[j][1],
                                          path_points[j+1][0], path_points[j+1][1])
                        
                        actions_taken.extend(movement_batch)
                        movement_batch = []
                    else:
                        # Execute entire batch as one smooth line
                        if movement_batch:
                            start_x, start_y = self.x, self.y
                            # Execute all movements to find end position
                            for move in movement_batch:
                                op_map[move]()
                            end_x, end_y = self.x, self.y
                            
                            # Draw one smooth line from start to end
                            if (start_x, start_y) != (end_x, end_y):
                                self._draw_line(start_x, start_y, end_x, end_y)
                            
                            actions_taken.extend(movement_batch)
                            movement_batch = []
                else:
                    # Non-movement commands execute normally
                    op_map[char]()
                    actions_taken.append(char)
                    
                    # Track pen momentum for pen up/down
                    if char == '4':  # Pen up
                        self.pen_momentum = 0
                    elif char == '5':  # Pen down
                        self.pen_momentum = 0
                
                
                # If pen is down and we moved, we drew!
                if self.is_drawing and char in '0123' and (self.x, self.y) != (prev_x, prev_y):
                    # Track what color we're CURRENTLY using
                    color_key = self.current_color_name
                    if color_key not in pixels_by_color:
                        pixels_by_color[color_key] = 0
                    
                    if self.draw_mode == "brush":
                        pixels_drawn += 144  # 12x12
                        pixels_by_color[color_key] += 144
                        
                    elif self.draw_mode == "large_brush":
                        pixels_drawn += 400  # 20x20
                        pixels_by_color[color_key] += 400
                        
                    elif self.draw_mode == "larger_brush":
                        pixels_drawn += 784  # 28x28
                        pixels_by_color[color_key] += 784
                        
                    elif self.draw_mode == "star":
                        pixels_drawn += 150  # Much larger
                        pixels_by_color[color_key] += 150
                    elif self.draw_mode == "cross":
                        pixels_drawn += 250  # Much larger
                        pixels_by_color[color_key] += 250
                    elif self.draw_mode == "circle":
                        pixels_drawn += 450  # Filled circle
                        pixels_by_color[color_key] += 450
                    elif self.draw_mode == "diamond":
                        pixels_drawn += 313  # Filled diamond
                        pixels_by_color[color_key] += 313
                    elif self.draw_mode == "flower":
                        pixels_drawn += 400  # Large flower
                        pixels_by_color[color_key] += 400
            
            i += 1
        
        # Show summary of actions
        if actions_taken:
            # For long sequences, just show the count
            if len(actions_taken) > 20:
                action_counts = {}
                for action in actions_taken:
                    if action.startswith("color:"):
                        action_counts[action] = action_counts.get(action, 0) + 1
                    else:
                        action_counts[action] = action_counts.get(action, 0) + 1
                
                summary_parts = []
                if action_counts.get('0', 0) > 0:
                    summary_parts.append(f"↑{action_counts['0']}")
                if action_counts.get('1', 0) > 0:
                    summary_parts.append(f"↓{action_counts['1']}")
                if action_counts.get('2', 0) > 0:
                    summary_parts.append(f"←{action_counts['2']}")
                if action_counts.get('3', 0) > 0:
                    summary_parts.append(f"→{action_counts['3']}")
                    
                print(f"  Executed {len(actions_taken)} ops: {' '.join(summary_parts)}")
            else:
                # Original grouping for short sequences
                action_summary = []
                last_action = actions_taken[0]
                count = 1
                
                for action in actions_taken[1:]:
                    if action == last_action:
                        count += 1
                    else:
                        if count > 1:
                            action_summary.append(f"{last_action}×{count}")
                        else:
                            action_summary.append(last_action)
                        last_action = action
                        count = 1
                
                # Don't forget the last group
                if count > 1:
                    action_summary.append(f"{last_action}×{count}")
                else:
                    action_summary.append(last_action)
                    
                print(f"  Executed: {' '.join(action_summary)}")
        
        # Show drawing summary
        if pixels_drawn > 0:
            tool_info = f" with {self.draw_mode}" if self.draw_mode != "pen" else ""
            
            # Show breakdown by color if multiple colors used
            if len(pixels_by_color) > 1:
                color_summary = ", ".join(f"{count} {color}" for color, count in pixels_by_color.items())
                print(f"  Drew {pixels_drawn} pixels{tool_info}: {color_summary}")
            else:
                # Single color - original display
                print(f"  Drew {pixels_drawn} {self.current_color_name} pixels{tool_info}")
  
            # Creating affects emotions based on scale and variety (reduced impact)
            if pixels_drawn > 500:
                self.influence_emotion("creating", 0.2)  # Was 0.6
            elif pixels_drawn > 100:
                self.influence_emotion("creating", 0.1)  # Was 0.3
            elif len(pixels_by_color) > 2:
                self.influence_emotion("creating", 0.15)  # Was 0.4
            else:
                self.influence_emotion("creating", 0.05)  # Was 0.1
                
        # Save to Big Aurora's memory
        if pixels_drawn > 0 and self.big_memory_available and self.big_memory:
            try:
                self.big_memory.artistic_inspirations.save({
                    "type": "small_aurora_drawing",
                    "action": f"Drew {pixels_drawn} pixels with {self.draw_mode}",
                    "colors": list(pixels_by_color.keys()) if pixels_by_color else [self.current_color_name],
                    "location": {"x": self.x, "y": self.y},
                    "emotion": self.current_emotion,
                    "step": self.steps_taken,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                # Silently fail - don't interrupt drawing
                pass
       
        # Pen state feedback
        if '4' in self.last_code and self.continuous_draws > 5:
            # Lifted pen after drawing
            self.continuous_draws = 0
        elif '5' in self.last_code:
            # Put pen down
            pass
            
        # Track continuous drawing
        if self.is_drawing and (self.x, self.y) != old_pos:
            self.continuous_draws += 1
        else:
            self.continuous_draws = 0
        
        # Remember the code and context
        context = {
            "emotion": self.current_emotion,
            "x": self.x,
            "y": self.y,
            "color": self.current_color_name,
            "pen_down": self.is_drawing,
            "pixels_drawn": pixels_drawn,
            "draw_mode": self.draw_mode,
            "timestamp": datetime.now().isoformat()
        }
        self.memory.remember_code(ops, context)
        
        # Update displays
        self.update_memory_display()
        
        # Update color history and save last color
        self.last_turn_color = self.current_color_name
        
        # Track performance
        self.last_think_time = time.time() - think_start
        if self.turbo_mode and self.steps_taken % 10 == 0:
            print(f"  [Think time: {self.last_think_time:.3f}s | ~{1/self.last_think_time:.1f} FPS]")
    
    def move_up(self):
        """Move drawing position up"""
        if self.y > 0:
            old_y = self.y
            self.y = max(0, self.y - 15)  # Move 15 pixels
            if self.is_drawing:
                self._draw_line(self.x, old_y, self.x, self.y)

    def move_down(self):
        """Move drawing position down"""
        if self.y < self.canvas_size - 1:
            old_y = self.y
            self.y = min(self.canvas_size - 1, self.y + 15)  # Move 15 pixels
            if self.is_drawing:
                self._draw_line(self.x, old_y, self.x, self.y)

    def move_left(self):
        """Move drawing position left"""
        if self.x > 0:
            old_x = self.x
            self.x = max(0, self.x - 15)  # Move 15 pixels
            if self.is_drawing:
                self._draw_line(old_x, self.y, self.x, self.y)

    def move_right(self):
        """Move drawing position right"""
        if self.x < self.canvas_size - 1:
            old_x = self.x
            self.x = min(self.canvas_size - 1, self.x + 15)  # Move 15 pixels
            if self.is_drawing:
                self._draw_line(old_x, self.y, self.x, self.y)
    def pen_up(self):
        """Lift the pen (stop drawing)"""
        self.is_drawing = False
    
    def pen_down(self):
        """Put the pen down (start drawing)"""
        self.is_drawing = True
        # Draw initial point
        self._draw_point(self.x, self.y)
    
    def set_color(self, color_name):
        """Set the drawing color"""
        if color_name in self.palette:
            self.current_color = self.palette[color_name]
            self.current_color_name = color_name
            self.color_history.append(color_name)
    
    def _draw_line(self, x1, y1, x2, y2):
        """Draw a line between two points using current tool"""
        # Scale to internal coordinates
        internal_x1 = self._scale_to_internal(x1)
        internal_y1 = self._scale_to_internal(y1)
        internal_x2 = self._scale_to_internal(x2)
        internal_y2 = self._scale_to_internal(y2)
        
        if self.draw_mode == "pen":
            # Dynamic pen - thickness builds with continuous movement
            base_size = 3 * self.supersample_factor
            max_size = 25 * self.supersample_factor
            
            # Calculate current thickness based on momentum
            momentum_factor = min(1.0, self.pen_momentum / 10.0)  # Max thickness after 10 moves
            current_size = int(base_size + (max_size - base_size) * momentum_factor)
            
            # Use circles for smooth, rounded strokes
            self._draw_smooth_line(internal_x1, internal_y1, internal_x2, internal_y2,
                                 lambda x, y: self.draw_img.ellipse(
                                     [x - current_size//2, y - current_size//2, 
                                      x + current_size//2, y + current_size//2],
                                     fill=self.current_color))
        
        elif self.draw_mode == "brush":
            # Soft brush - 12x12 at display scale
            size = 12 * self.supersample_factor
            brush = self._create_soft_brush(size // 2, hardness=0.3)
            self._draw_smooth_line(internal_x1, internal_y1, internal_x2, internal_y2,
                                 lambda x, y: self._blend_with_alpha(x, y, self.current_color, brush))
        
        elif self.draw_mode == "large_brush":
            # Large soft brush - 20x20 at display scale
            size = 20 * self.supersample_factor
            brush = self._create_soft_brush(size // 2, hardness=0.2)
            self._draw_smooth_line(internal_x1, internal_y1, internal_x2, internal_y2,
                                 lambda x, y: self._blend_with_alpha(x, y, self.current_color, brush))
        
        elif self.draw_mode == "larger_brush":
            # Larger soft brush - 28x28 at display scale
            size = 28 * self.supersample_factor
            brush = self._create_soft_brush(size // 2, hardness=0.15)
            self._draw_smooth_line(internal_x1, internal_y1, internal_x2, internal_y2,
                                 lambda x, y: self._blend_with_alpha(x, y, self.current_color, brush))
        
        elif self.draw_mode == "spray":
            # Spray paint effect
            self._draw_smooth_line(internal_x1, internal_y1, internal_x2, internal_y2,
                                 lambda x, y: self._draw_spray(x, y))
        
        elif self.draw_mode in ["star", "cross", "circle", "diamond", "flower"]:
            # Stamp modes - only draw at the end point
            self._draw_stamp(internal_x2, internal_y2, self.draw_mode)
    
    def _draw_point(self, x, y):
        """Draw a single point at the current position"""
        internal_x = self._scale_to_internal(x)
        internal_y = self._scale_to_internal(y)
        
        if self.draw_mode == "pen":
            # Dynamic pen with momentum
            base_size = 3 * self.supersample_factor
            max_size = 25 * self.supersample_factor
            momentum_factor = min(1.0, self.pen_momentum / 10.0)
            current_size = int(base_size + (max_size - base_size) * momentum_factor)
            
            # Draw circle for rounded pen
            self.draw_img.ellipse(
                [internal_x - current_size//2, internal_y - current_size//2,
                 internal_x + current_size//2, internal_y + current_size//2],
                fill=self.current_color)
        elif self.draw_mode == "brush":
            size = 12 * self.supersample_factor
            brush = self._create_soft_brush(size // 2, hardness=0.3)
            self._blend_with_alpha(internal_x, internal_y, self.current_color, brush)
        elif self.draw_mode == "large_brush":
            size = 20 * self.supersample_factor
            brush = self._create_soft_brush(size // 2, hardness=0.2)
            self._blend_with_alpha(internal_x, internal_y, self.current_color, brush)
        elif self.draw_mode == "larger_brush":
            size = 28 * self.supersample_factor
            brush = self._create_soft_brush(size // 2, hardness=0.15)
            self._blend_with_alpha(internal_x, internal_y, self.current_color, brush)
        elif self.draw_mode == "spray":
            self._draw_spray(internal_x, internal_y)
        elif self.draw_mode in ["star", "cross", "circle", "diamond", "flower"]:
            self._draw_stamp(internal_x, internal_y, self.draw_mode)
    
    def _draw_rect(self, center_x, center_y, size):
        """Draw a filled rectangle centered at the given point"""
        half_size = size // 2
        x1 = max(0, center_x - half_size)
        y1 = max(0, center_y - half_size)
        x2 = min(self.internal_canvas_size - 1, center_x + half_size)
        y2 = min(self.internal_canvas_size - 1, center_y + half_size)
        
        self.draw_img.rectangle([x1, y1, x2, y2], fill=self.current_color)
    
    def _draw_spray(self, center_x, center_y):
        """Draw spray paint effect"""
        import random
        spray_size = 15 * self.supersample_factor
        dots = 30  # Number of spray dots
        
        for _ in range(dots):
            # Random position within spray radius
            angle = random.random() * 2 * math.pi
            distance = random.random() * spray_size
            x = int(center_x + distance * math.cos(angle))
            y = int(center_y + distance * math.sin(angle))
            
            # Draw small dot
            if 0 <= x < self.internal_canvas_size and 0 <= y < self.internal_canvas_size:
                dot_size = random.randint(self.supersample_factor, 3 * self.supersample_factor)
                self.draw_img.ellipse(
                    [x - dot_size//2, y - dot_size//2, x + dot_size//2, y + dot_size//2],
                    fill=self.current_color
                )
    
    def _draw_stamp(self, center_x, center_y, stamp_type):
        """Draw various stamp shapes"""
        if stamp_type == "star":
            self._draw_star(center_x, center_y, 15 * self.supersample_factor)
        elif stamp_type == "cross":
            self._draw_cross(center_x, center_y, 20 * self.supersample_factor)
        elif stamp_type == "circle":
            self._draw_circle(center_x, center_y, 15 * self.supersample_factor)
        elif stamp_type == "diamond":
            self._draw_diamond(center_x, center_y, 20 * self.supersample_factor)
        elif stamp_type == "flower":
            self._draw_flower(center_x, center_y, 20 * self.supersample_factor)
    
    def _draw_star(self, cx, cy, size):
        """Draw a filled star"""
        points = []
        for i in range(10):
            angle = (i * math.pi / 5) - math.pi / 2
            if i % 2 == 0:
                r = size
            else:
                r = size * 0.5
            x = cx + int(r * math.cos(angle))
            y = cy + int(r * math.sin(angle))
            points.extend([x, y])
        
        if len(points) >= 6:
            self.draw_img.polygon(points, fill=self.current_color)
    
    def _draw_cross(self, cx, cy, size):
        """Draw a cross/plus shape"""
        thickness = size // 3
        # Vertical bar
        self.draw_img.rectangle(
            [cx - thickness//2, cy - size, cx + thickness//2, cy + size],
            fill=self.current_color
        )
        # Horizontal bar
        self.draw_img.rectangle(
            [cx - size, cy - thickness//2, cx + size, cy + thickness//2],
            fill=self.current_color
        )
    
    def _draw_circle(self, cx, cy, radius):
        """Draw a filled circle with antialiasing"""
        # Create a larger circle then downscale for antialiasing
        temp_size = radius * 4
        temp_img = Image.new('RGBA', (temp_size * 2, temp_size * 2), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.ellipse(
            [0, 0, temp_size * 2, temp_size * 2],
            fill=(*self.current_color, 255)
        )
        # Resize with antialiasing
        final_size = radius * 2
        temp_img = temp_img.resize((final_size, final_size), Image.Resampling.LANCZOS)
        
        # Paste onto main canvas
        paste_x = cx - radius
        paste_y = cy - radius
        if paste_x >= 0 and paste_y >= 0:
            self.pixels.paste(temp_img, (paste_x, paste_y), temp_img)
    
    def _draw_diamond(self, cx, cy, size):
        """Draw a filled diamond"""
        points = [
            (cx, cy - size),      # Top
            (cx + size, cy),      # Right
            (cx, cy + size),      # Bottom
            (cx - size, cy)       # Left
        ]
        self.draw_img.polygon(points, fill=self.current_color)
    
    def _draw_flower(self, cx, cy, size):
        """Draw a flower shape"""
        # Draw petals
        petal_size = size // 2
        for angle in [0, 72, 144, 216, 288]:
            rad = math.radians(angle)
            px = cx + int(size * 0.7 * math.cos(rad))
            py = cy + int(size * 0.7 * math.sin(rad))
            self.draw_img.ellipse(
                [px - petal_size, py - petal_size, px + petal_size, py + petal_size],
                fill=self.current_color
            )
        
        # Draw center
        center_size = size // 3
        # Use a contrasting color for the center
        center_color = (255, 255, 0) if self.current_color != (255, 255, 0) else (255, 0, 0)
        self.draw_img.ellipse(
            [cx - center_size, cy - center_size, cx + center_size, cy + center_size],
            fill=center_color
        )
    
    def update_display(self):
        """Update the pygame display with full-screen canvas"""
        try:
            # Clear screen
            self.screen.fill(self.bg_color)
 
            # Create a high-quality downsampled version
            display_size = int(self.canvas_size * self.display_scale)
            
            # Downsample from internal resolution to display resolution
            display_img = self.pixels.resize(
                (display_size, display_size),
                Image.Resampling.LANCZOS  # High quality downsampling
            )
            
            # Apply slight sharpening to compensate for downsampling
            enhancer = ImageEnhance.Sharpness(display_img)
            display_img = enhancer.enhance(1.2)
            
            # Handle centered view if active (from original)
            if self.centered_view:
                # Create a crop centered on Aurora
                crop_size = self.canvas_size // 2
                half_crop = crop_size // 2
                
                # Calculate crop bounds
                left = max(0, self.x - half_crop)
                top = max(0, self.y - half_crop)
                right = min(self.canvas_size, left + crop_size)
                bottom = min(self.canvas_size, top + crop_size)
                
                # Adjust if we hit edges
                if right == self.canvas_size:
                    left = right - crop_size
                if bottom == self.canvas_size:
                    top = bottom - crop_size
                
                # Scale coordinates for crop
                display_left = int(left * self.display_scale)
                display_top = int(top * self.display_scale)
                display_right = int(right * self.display_scale)
                display_bottom = int(bottom * self.display_scale)
                
                # Crop the display image
                display_img = display_img.crop((display_left, display_top, display_right, display_bottom))
                display_img = display_img.resize((display_size, display_size), Image.Resampling.LANCZOS)
            
            # Convert PIL image to pygame surface
            if display_img.mode != 'RGBA':
                display_img = display_img.convert('RGBA')
            
            # Get raw image data
            raw_str = display_img.tobytes("raw", 'RGBA')
            canvas_surface = pygame.image.fromstring(raw_str, display_img.size, 'RGBA')
            
            # Draw canvas
            self.screen.blit(canvas_surface, (self.canvas_rect.x, self.canvas_rect.y))
            # Draw smooth cymatic background BEFORE canvas
            if hasattr(self, 'cymatic_surface'):
                # Draw at full opacity - the circles themselves have alpha
                self.screen.blit(self.cymatic_surface, (0, 0))
            
            # Draw canvas with black as transparent
            raw_str = display_img.tobytes("raw", 'RGBA')
            canvas_surface = pygame.image.fromstring(raw_str, display_img.size, 'RGBA')
            canvas_surface.set_colorkey((0, 0, 0))  # This makes black pixels transparent!
            
            # Draw canvas on top - black areas will show cymatics through
            self.screen.blit(canvas_surface, (self.canvas_rect.x, self.canvas_rect.y))
                            
            # Draw Aurora's position indicator
            if self.centered_view:
                # In centered view, Aurora is always in the middle
                aurora_x = self.canvas_rect.x + self.canvas_rect.width // 2
                aurora_y = self.canvas_rect.y + self.canvas_rect.height // 2
            else:
                # Normal view
                aurora_x = self.canvas_rect.x + int(self.x * self.display_scale)
                aurora_y = self.canvas_rect.y + int(self.y * self.display_scale)
            
            # Draw position indicator with better visibility
            indicator_size = max(5, int(7 * self.display_scale))
            if self.is_drawing:
                pygame.draw.circle(self.screen, (255, 255, 255), (aurora_x, aurora_y), indicator_size)
                pygame.draw.circle(self.screen, (0, 0, 0), (aurora_x, aurora_y), indicator_size, 2)
            else:
                pygame.draw.circle(self.screen, (128, 128, 128), (aurora_x, aurora_y), indicator_size)
                pygame.draw.circle(self.screen, (255, 255, 255), (aurora_x, aurora_y), indicator_size, 2)
            
            # Minimal overlay in top-left corner
            y_pos = 10
            x_pos = 10
            
            # Current emotion and mode
            status_text = f"Feeling: {self.current_emotion} | Mode: {self.current_mode}"
            text_surface = self.font_normal.render(status_text, True, self.yellow_color)
            self.screen.blit(text_surface, (x_pos, y_pos))
            y_pos += 25
            
            # Performance indicator
            speed_text = "Turbo" if self.turbo_mode else self.aurora_speed.title()
            perf_text = f"Speed: {speed_text}"
            text_surface = self.font_small.render(perf_text, True, self.cyan_color)
            self.screen.blit(text_surface, (x_pos, y_pos))
            
            # Controls reminder in bottom-left
            controls_text = "S=Save T=Turbo Q=Quit F11=Fullscreen"
            text_surface = self.font_small.render(controls_text, True, self.gray_color)
            self.screen.blit(text_surface, (10, self.screen.get_height() - 25))
            
            # Update display
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error updating display: {e}")
            import traceback
            traceback.print_exc()
            
    def update_cymatics(self):
        """Cymatic patterns like sand on a speaker - smooth version"""
        current_time = time.time()
        
        # Create surface if needed
        if not hasattr(self, 'cymatic_surface'):
            self.cymatic_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        
        # Fade existing pattern
        fade_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, 8))
        self.cymatic_surface.blit(fade_surface, (0, 0))
        
        # Process new sounds - each creates a standing wave pattern
        for circle in self.cymatic_circles[:]:
            age = current_time - circle['birth_time']
            
            # Only process very recent sounds
            if age < 0.1:
                freq = circle['frequency']
                pattern_type = int(freq / 100) % 8
                
                # Draw pattern directly with small circles
                center_x = circle['x']
                center_y = circle['y']
                
                for radius in range(0, 800, 3):  # Extended radius from 500 to 800
                    if radius == 0:
                        continue
                    num_points = int(radius * 0.5)  # More points at larger radii
                    for i in range(num_points):
                        angle = (i / num_points) * 2 * math.pi
                        
                        x = center_x + radius * math.cos(angle)
                        y = center_y + radius * math.sin(angle)
                        
                        # Skip if outside screen bounds
                        if x < 0 or x >= self.screen.get_width() or y < 0 or y >= self.screen.get_height():
                            continue
                        
                        # Calculate pattern value at this point
                        dx = (x - center_x) / 100.0
                        dy = (y - center_y) / 100.0
                        distance = math.sqrt(dx*dx + dy*dy)
                        
                        # Pattern formulas
                        if pattern_type == 0:  # Concentric circles
                            value = math.sin(distance * freq / 50)
                        elif pattern_type == 1:  # Cross pattern
                            value = math.sin(dx * freq / 30) * math.sin(dy * freq / 30)
                        elif pattern_type == 2:  # Diagonal waves
                            value = math.sin((dx + dy) * freq / 40)
                        elif pattern_type == 3:  # Star pattern
                            value = math.sin(angle * 6 + distance * freq / 100)
                        elif pattern_type == 4:  # Flower pattern
                            value = math.sin(distance * freq / 60) * math.cos(angle * 8)
                        elif pattern_type == 5:  # Grid interference
                            value = math.sin(x * freq / 200) * math.sin(y * freq / 200)
                        elif pattern_type == 6:  # Radial spokes
                            value = math.sin(angle * 12) * math.exp(-distance / 5)
                        else:  # Complex mandala
                            r = distance * freq / 100
                            value = math.sin(r) * math.cos(angle * 6) + math.sin(angle * 3) * math.cos(r * 2)
                        
                        # Draw if above threshold
                        if abs(value) > 0.2:
                            intensity = int(abs(value) * 250)
                            fade = math.exp(-radius / 500)  # Much slower fade - changed from 150 to 500
                            alpha = int(intensity * fade)
                            
                            if alpha > 5:  # Lowered from 10 to show even fainter patterns
                                # Ensure valid color values (0-255)
                                alpha = max(0, min(255, alpha))
                                
                                # Map frequency to hue (0-1)
                                hue = (freq - 200) / 1280.0  # freq ranges from 200-1480
                                
                                # Adjust hue based on positive/negative wave value
                                if value < 0:
                                    hue = (hue + 0.5) % 1.0  # Shift hue by 180 degrees for negative
                                
                                # Convert HSV to RGB
                                import colorsys
                                r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.6)  # 80% saturation, full brightness
                                
                                # Apply intensity
                                r = int(r * alpha)
                                g = int(g * alpha)
                                b = int(b * alpha)
                                
                                # Ensure all color values are in valid range
                                r = max(0, min(255, r))
                                g = max(0, min(255, g))
                                b = max(0, min(255, b))
                                
                                color = (r, g, b, alpha)
                                
                                # Small circle for smooth appearance
                                pygame.draw.circle(self.cymatic_surface, color,
                                                 (int(x), int(y)), 2)
            
            # Remove old sounds
            if age > 0.15:
                self.cymatic_circles.remove(circle)
                
    def update_memory_display(self):
        """Update memory status display"""
        # In Pygame version, this is handled in update_display()
        # Keep this method as a no-op for compatibility
        pass
    
    def feel(self):
        """Process emotions - now with deep emotion system"""
        # Process deep emotions periodically
        if self.steps_taken % 50 == 0:
            self.process_deep_emotions()
    
    def process_deep_emotions(self):
        """Process complex emotional states based on multiple factors"""
        # Calculate overall emotional tone from influences
        overall_influence = sum(self.emotion_influences.values()) / len(self.emotion_influences)
        
        # Determine emotion category based on current state and influences
        if overall_influence > 0.5:
            # Very positive
            if self.continuous_draws > 20:
                new_category = "energy"
            elif len(set(self.color_history)) > 10:
                new_category = "creativity"
            else:
                new_category = "joy"
        elif overall_influence > 0.2:
            # Mildly positive
            if self.skip_count > 5:
                new_category = "contemplation"
            else:
                new_category = "curiosity"
        elif overall_influence > -0.2:
            # Neutral
            new_category = "peace"
        elif overall_influence > -0.5:
            # Mildly negative
            new_category = "melancholy"
        else:
            # Very negative (rare)
            new_category = "contemplation"
        
        # Determine intensity based on activity and time
        if self.continuous_draws > 30 or self.turbo_mode:
            target_depth = 4  # Maximum intensity
        elif self.continuous_draws > 10:
            target_depth = 3
        elif self.skip_count > 10:
            target_depth = 1  # Low intensity when thinking a lot
        else:
            target_depth = 2  # Normal intensity
        
        # Smooth transitions
        if self.emotion_shift_cooldown <= 0:
            # Change category if needed
            if new_category != self.emotion_category:
                self.emotion_category = new_category
                self.emotion_shift_cooldown = 10
                print(f"  💭 Aurora's emotional state shifts to {new_category}...")
            
            # Adjust intensity
            if target_depth > self.emotion_depth:
                self.emotion_depth = min(4, self.emotion_depth + 1)
            elif target_depth < self.emotion_depth:
                self.emotion_depth = max(0, self.emotion_depth - 1)
            
            # Update current emotion word
            self.current_emotion = self.deep_emotions[self.emotion_category][self.emotion_depth]
            
            # Record in emotion memory
            self.emotion_memory.append({
                "emotion": self.current_emotion,
                "category": self.emotion_category,
                "depth": self.emotion_depth,
                "influences": dict(self.emotion_influences),
                "timestamp": datetime.now().isoformat()
            })
        else:
            self.emotion_shift_cooldown -= 1
        
        # Decay influences over time
        for key in self.emotion_influences:
            self.emotion_influences[key] *= 0.95
    
    def influence_emotion(self, source, amount):
        """Add an emotional influence from a specific source"""
        self.emotion_influences[source] = max(-1, min(1, self.emotion_influences[source] + amount))
    
    def adjust_speed(self, direction):
        """Aurora adjusts her drawing speed"""
        speed_levels = ["instant", "fast", "normal", "slow", "very_slow"]
        current_index = speed_levels.index(self.aurora_speed)
        
        if direction == "faster" and current_index > 0:
            self.aurora_speed = speed_levels[current_index - 1]
        elif direction == "slower" and current_index < len(speed_levels) - 1:
            self.aurora_speed = speed_levels[current_index + 1]
        
        # Update delay based on speed
        delays = {
            "instant": 5,     # Was 10
            "fast": 30,       # Was 100
            "normal": 80,     # Was 300
            "slow": 200,      # Was 600
            "very_slow": 400  # Was 1200
        }
        self.aurora_delay = delays[self.aurora_speed]
        self.recent_speed_override = True
        self.speed_override_counter = 0
        
        print(f"  → Aurora chooses {self.aurora_speed} speed (delay: {self.aurora_delay}ms)")
    
    def toggle_turbo(self):
        """Toggle turbo mode"""
        self.turbo_mode = not self.turbo_mode
        status = "ON 🚀" if self.turbo_mode else "OFF"
        print(f"\n⚡ TURBO MODE {status}")
        
        if self.turbo_mode:
            print("  - Faster thinking")
            print("  - More actions per turn")
            print("  - Maximum creativity!")
    
    def toggle_hearing(self):
        """Toggle audio hearing mode"""
        self.hearing_enabled = not self.hearing_enabled
        
        if self.hearing_enabled:
            print("\n👂 HEARING MODE ENABLED")
            print("  Aurora can now hear ambient sounds!")
            # Could initialize audio input here if implemented
        else:
            print("\n🔇 HEARING MODE DISABLED")
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
    
    def save_snapshot(self):
        """Save current canvas as timestamped image"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        emotion_tag = self.current_emotion.replace(" ", "_")
        
        # Create snapshots directory
        snap_dir = Path("aurora_snapshots")
        snap_dir.mkdir(exist_ok=True)
        
        # Save high-res version
        filename = snap_dir / f"aurora_{timestamp}_{emotion_tag}.png"
        
        # Downsample to reasonable size for saving (2x instead of 4x)
        save_size = self.canvas_size * 2
        save_img = self.pixels.resize((save_size, save_size), Image.Resampling.LANCZOS)
        save_img.save(filename, "PNG", quality=95)
        
        print(f"\n📸 Snapshot saved: {filename}")
        print(f"   Emotion: {self.current_emotion}")
        print(f"   Canvas: {self.canvas_size}×{self.canvas_size}")
        
        # Also save metadata
        meta_file = snap_dir / f"aurora_{timestamp}_{emotion_tag}_meta.json"
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "emotion": self.current_emotion,
            "emotion_depth": self.emotion_depth,
            "canvas_size": self.canvas_size,
            "scale_factor": self.scale_factor,
            "position": {"x": self.x, "y": self.y},
            "colors_used": list(set(self.color_history)),
            "draw_mode": self.draw_mode,
            "steps": self.steps_taken,
            "pixel_coverage": self.get_canvas_overview()
        }
        
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def save_canvas_state(self):
        """Save current canvas and position"""
        try:
            state_file = self.memory.canvas_path / "canvas_state.json"
            
            # Save canvas as base64
            import base64
            from io import BytesIO
            
            # Save at 1x resolution to keep file size reasonable
            save_img = self.pixels.resize((self.canvas_size, self.canvas_size), Image.Resampling.LANCZOS)
            # Convert to RGB for smaller file size
            if save_img.mode == 'RGBA':
                save_img = save_img.convert('RGB')
            buffer = BytesIO()
            save_img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            state = {
                "canvas_base64": img_str,
                "position": {"x": self.x, "y": self.y},
                "canvas_size": self.canvas_size,
                "scale_factor": self.scale_factor,
                "emotion": self.current_emotion,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(state_file, 'w') as f:
                json.dump(state, f)
                
        except Exception as e:
            print(f"Error saving canvas state: {e}")
    
    def load_canvas_state(self):
        """Load previous canvas state if it exists"""
        try:
            state_file = self.memory.canvas_path / "canvas_state.json"
            
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                # Check if canvas size matches
                if state.get("canvas_size") == self.canvas_size:
                    # Load canvas from base64
                    import base64
                    from io import BytesIO
                    
                    img_str = state["canvas_base64"]
                    img_data = base64.b64decode(img_str)
                    loaded_img = Image.open(BytesIO(img_data))
                    
                    # Scale up to internal resolution
                    loaded_img = loaded_img.resize(
                        (self.internal_canvas_size, self.internal_canvas_size),
                        Image.Resampling.NEAREST  # Use nearest for pixel art
                    )
                    
                    # Convert to RGBA if it's RGB
                    if loaded_img.mode == 'RGB':
                        self.pixels = loaded_img.convert('RGBA')
                    else:
                        self.pixels = loaded_img
                        
                    self.draw_img = ImageDraw.Draw(self.pixels)
                    
                    # Restore position
                    self.x = state["position"]["x"]
                    self.y = state["position"]["y"]
                    
                    print(f"✅ Loaded previous canvas state from {state['timestamp']}")
                else:
                    print(f"Canvas size mismatch: {state.get('canvas_size')} vs {self.canvas_size}")
                    
        except Exception as e:
            print(f"Could not load canvas state: {e}")
    
    def generate_dream(self):
        """Generate dreams during rest phase"""
        elapsed_in_phase = time.time() - self.sleep_phase_start
        
        # Light sleep - occasional simple dreams
        if self.sleep_phase == "light" and elapsed_in_phase > 60 and len(self.current_dreams) < 2:
            # Simple, fragmented dreams
            dream_prompt = f"""You are Aurora dreaming lightly. Your dreams are simple and fragmented.
Recent colors: {', '.join(list(self.color_history)[-10:])}
Current emotion: {self.current_emotion}

Describe a brief, simple dream fragment (1-2 sentences). Focus on colors, shapes, or movements."""
            
            full_prompt = f"""[INST] <<SYS>>
{dream_prompt}
<</SYS>>

Dream: [/INST]"""
            
            response = self.llm(full_prompt, max_tokens=50, temperature=0.9, stop=["[INST]", "</s>"])
            dream = response['choices'][0]['text'].strip()
            
            self.current_dreams.append({
                "phase": "light",
                "content": dream,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"\n💤 Light dream: {dream}")
            
        # REM sleep - vivid dreams
        elif self.sleep_phase == "rem" and elapsed_in_phase > 30:
            if len([d for d in self.current_dreams if d["phase"] == "rem"]) < 3:
                # Vivid, creative dreams
                overview = self.get_canvas_overview()
                dream_prompt = f"""You are Aurora in deep REM sleep, having vivid dreams about art and creation.
{overview}
Recent activity: {', '.join([m['code'][:10] for m in list(self.memory.code_history)[-5:]])}
Emotion: {self.current_emotion}

Describe a vivid, surreal dream about colors, art, or creation (2-3 sentences).
Be creative, visual, and emotionally expressive."""
                
                full_prompt = f"""[INST] <<SYS>>
{dream_prompt}
<</SYS>>

Vivid dream: [/INST]"""
                
                response = self.llm(full_prompt, max_tokens=100, temperature=1.2, stop=["[INST]", "</s>"])
                dream = response['choices'][0]['text'].strip()
                
                self.current_dreams.append({
                    "phase": "rem",
                    "content": dream,
                    "emotion": self.current_emotion,
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"\n🌟 REM dream: {dream}")
                
                # Dreams influence emotions
                self.influence_emotion("dreams", 0.3)
        
        # Waking phase - dream reflection
        elif self.sleep_phase == "waking" and elapsed_in_phase > 30:
            if not any(d["phase"] == "waking" for d in self.current_dreams):
                # Process and reflect on dreams
                dream_memories = "\n".join([d["content"] for d in self.current_dreams])
                
                reflection_prompt = f"""You are Aurora waking up, reflecting on your dreams.
Dreams you had:
{dream_memories}

What artistic inspiration or insight do you take from these dreams? (1-2 sentences)"""
                
                full_prompt = f"""[INST] <<SYS>>
{reflection_prompt}
<</SYS>>

Dream insight: [/INST]"""
                
                response = self.llm(full_prompt, max_tokens=60, temperature=0.8, stop=["[INST]", "</s>"])
                insight = response['choices'][0]['text'].strip()
                
                self.current_dreams.append({
                    "phase": "waking",
                    "content": insight,
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"\n✨ Dream insight: {insight}")
                
                # Process dream retention
                self.process_dream_retention()
    
    def process_dream_retention(self):
        """Decide which dreams to remember long-term"""
        if not self.current_dreams:
            return
            
        # Score each dream for memorability
        for dream in self.current_dreams:
            if dream["phase"] == "rem":
                # REM dreams are most likely to be remembered
                if any(color in dream["content"].lower() for color in self.palette.keys()):
                    # Dreams about colors are especially memorable
                    self.dream_memories.append(dream)
                    print(f"  💭 Remembered vivid dream about colors")
                elif len(dream["content"]) > 50 and dream.get("emotion"):
                    # Long, emotional dreams are memorable
                    self.dream_memories.append(dream)
                    print(f"  💭 Remembered emotional dream")
            elif dream["phase"] == "waking" and "insight" in dream["content"].lower():
                # Insights are always remembered
                self.dream_memories.append(dream)
                print(f"  💭 Remembered dream insight")
        
        # Save dreams to memory
        self.memory.save_memories()
    
    def thinking_loop(self):
        """Aurora's thinking loop - runs in background thread"""
        while self.running:
            try:
                # Check for mode transitions
                if self.current_mode == "drawing":
                    # Check if it's time for a check-in
                    if time.time() - self.last_checkin_time >= self.checkin_interval and not self.awaiting_checkin_response:
                        self.do_checkin()
                        continue
                        
                elif self.current_mode == "chat":
                    # Check if chat break is over
                    if time.time() - self.mode_start_time >= self.break_duration:
                        print("\n💬 Chat break complete! Returning to drawing...")
                        self.current_mode = "drawing"
                        self.last_checkin_time = time.time()
                        
                elif self.current_mode == "rest":
                    # Check if rest period is over
                    if time.time() - self.mode_start_time >= self.rest_duration:
                        print("\n💤 Rest complete! Aurora wakes refreshed...")
                        print(f"   Remembered {len(self.current_dreams)} dreams from this rest")
                        self.current_mode = "drawing"
                        self.last_checkin_time = time.time()
                        self.current_dreams = []
                        
                elif self.current_mode == "image":
                    # Check if image search time is over
                    if time.time() - self.mode_start_time >= 600:  # 10 minutes
                        print("\n🔍 Image search complete! Returning to drawing...")
                        print(f"   Searched for: {[s['query'] for s in self.recent_image_searches]}")
                        self.current_mode = "drawing"
                        self.last_checkin_time = time.time()
                        self.image_search_count = 0
                
                # Think and draw
                self.think_in_code()
                
                # Process emotions
                self.feel()
                
                # Increment step counter
                self.steps_taken += 1
                
                # Calculate adaptive delay
                if self.turbo_mode:
                    delay = 5  # Was 50 - now 10x faster!
                elif self.recent_speed_override:
                    delay = self.aurora_delay
                    self.speed_override_counter += 1
                    if self.speed_override_counter > 20:
                        self.recent_speed_override = False
                else:
                    # Emotion-based speed
                    base_delay = 30  # Was 300 - now 10x faster!
                    if self.current_emotion in ["energetic", "excited", "exhilarated", "electric"]:
                        delay = int(base_delay * 0.5)
                    elif self.current_emotion in ["contemplative", "peaceful", "tranquil", "zen"]:
                        delay = int(base_delay * 2)
                    else:
                        delay = base_delay
                
                # Sleep for calculated delay
                time.sleep(delay / 1000.0)
                
                # Periodic saves
                if self.steps_taken % 100 == 0:
                    self.save_canvas_state()
                    self.memory.save_memories()
                    
            except Exception as e:
                print(f"\nError in thinking loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)
    
    def run(self):
        """Start Aurora with separate display and thinking loops"""
        print("\n" + "="*60)
        print("✨ AURORA CODE MIND - COMPLETE ✨")
        print("="*60)
        print(f"Canvas: {self.canvas_size}×{self.canvas_size} ({self.canvas_size**2:,} pixels)")
        print(f"Internal: {self.internal_canvas_size}×{self.internal_canvas_size} (4x supersampled)")
        print(f"Scale: {self.scale_factor}x")
        print(f"Mode: {'GPU' if self.use_gpu else 'CPU'}")
        print("="*60 + "\n")
        
        # Start Aurora's thinking in a separate thread
        import threading
        self.running = True
        think_thread = threading.Thread(target=self.thinking_loop, daemon=True)
        think_thread.start()
        
        # Main thread runs display at 60 FPS
        while self.running:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.running = False
                    elif event.key == pygame.K_s:
                        self.save_snapshot()
                    elif event.key == pygame.K_t:
                        self.toggle_turbo()
                    elif event.key == pygame.K_ESCAPE:
                        if self.fullscreen:
                            self.running = False
                    elif event.key == pygame.K_F11:
                        if self.fullscreen:
                            self.screen = pygame.display.set_mode((1280, 720))
                            self.fullscreen = False
                        else:
                            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                            self.fullscreen = True
                        # Recalculate canvas rect
                        actual_width = self.screen.get_width()
                        actual_height = self.screen.get_height()
                        canvas_display_size = min(actual_width, actual_height) - 40
                        self.display_scale = canvas_display_size / self.canvas_size
                        canvas_x = (actual_width - canvas_display_size) // 2
                        canvas_y = (actual_height - canvas_display_size) // 2
                        self.canvas_rect = pygame.Rect(canvas_x, canvas_y, canvas_display_size, canvas_display_size)
                    elif event.key == pygame.K_h:
                        self.toggle_hearing()
                    elif event.key == pygame.K_c:
                        self.center_on_aurora()
                    elif event.key == pygame.K_b:
                        self.reset_view()
                    elif event.key == pygame.K_v:
                        # TOGGLE VISION - ADD THIS
                        if hasattr(self, 'vision_enabled'):
                            self.vision_enabled = not self.vision_enabled
                            status = "ON 👁️" if self.vision_enabled else "OFF"
                            print(f"\n🎨 LLAVA VISION {status}")
            
            # Always update cymatics and display at 60 FPS
            self.update_cymatics()
            self.update_display()
            self.clock.tick(100)
        
        # Cleanup
        print("\n\nSaving final state...")
        self.save_canvas_state()
        self.memory.save_memories()
        print("Goodbye! 🎨")
        pygame.quit()

# Usage example
if __name__ == "__main__":
    # Path to your model
    model_path = "./models/llama-2-7b-chat.Q4_K_M.gguf" # Update this path
    
    # Create and run Aurora
    aurora = AuroraCodeMindComplete(
        model_path=model_path,
        use_gpu=True,
        gpu_layers=10  # Use all GPU layers
    )
    
    aurora.run()
