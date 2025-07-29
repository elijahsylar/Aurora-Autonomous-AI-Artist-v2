from llama_cpp import Llama
from pathlib import Path
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import json
from datetime import datetime
from collections import deque
import time
import pyaudio
import pygame
import requests
import webbrowser
from urllib.parse import quote
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
    def __init__(self, model_path, use_gpu=True, gpu_layers=-1):
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
        temp_root = tk.Tk()
        screen_width = temp_root.winfo_screenwidth()
        screen_height = temp_root.winfo_screenheight()
        temp_root.destroy()
        
        # Canvas - adjust size based on screen (much smaller pixels now!)
        self.scale_factor = 1.6  # Lower scale_factor means smaller pixels and higher canvas resolution; e.g., 1.6 gives more pixels than 8.
        self.canvas_size = min(int(screen_width / self.scale_factor) - 50, 
                               int(screen_height / self.scale_factor) - 50)
                               
                       
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
        
        # Canvas
        self.pixels = Image.new('RGB', (self.canvas_size, self.canvas_size), 'black')
        self.draw_img = ImageDraw.Draw(self.pixels)
        print("8. Image buffer created")
        
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
        self.dream_memories = deque(maxlen=100)  # Store up to 100 dreams
        self.current_dreams = []  # Dreams from current rest session
        self.sleep_phase = "light"  # light, rem, waking
        self.sleep_phase_start = time.time()
        self.dream_count = 0
        # Audio hearing system
        self.hearing_enabled = False
        self.audio_stream = None
        self.audio = pyaudio.PyAudio()
        self.rest_duration = 10 * 60  # 1 hour for rest/dreaming (separate from break_duration)

        
        # Simple pygame sound system  # ADD ALL OF THIS
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        pygame.mixer.set_num_channels(8)  # 8 simultaneous sounds
        
        # Pre-generate simple beeps (so they're instant to play)
        self.sounds = {}
        self.current_pitch = 'normal'  # ADD THIS - tracks current pitch mode
        try:
            import numpy as np  # Import here if not already imported
        
            # Generate 16 different beeps at 3 pitches each (doubled!)
            for i, char in enumerate('!@#$%^&*()[]<>=+~'):
                base_freq = 200 + (i * 80)  # 200Hz to 1450Hz (smaller steps for more sounds)
                
                # Normal pitch
                freq = base_freq
                samples = np.sin(2 * np.pi * freq * np.arange(0, 0.05 * 22050) / 22050) * 0.3
                sound_data = (samples * 32767).astype(np.int16)
                sound_data = np.repeat(sound_data.reshape(-1, 1), 2, axis=1)  # Make stereo
                self.sounds[f"{char}_normal"] = pygame.sndarray.make_sound(sound_data)
                self.sounds[f"{char}_normal"].set_volume(0.3)
                
                # Low pitch (++)
                freq = base_freq * 0.5  # Half frequency
                samples = np.sin(2 * np.pi * freq * np.arange(0, 0.05 * 22050) / 22050) * 0.3
                sound_data = (samples * 32767).astype(np.int16)
                sound_data = np.repeat(sound_data.reshape(-1, 1), 2, axis=1)
                self.sounds[f"{char}_low"] = pygame.sndarray.make_sound(sound_data)
                self.sounds[f"{char}_low"].set_volume(0.3)
                
                # High pitch (--)
                freq = base_freq * 2  # Double frequency
                samples = np.sin(2 * np.pi * freq * np.arange(0, 0.05 * 22050) / 22050) * 0.3
                sound_data = (samples * 32767).astype(np.int16)
                sound_data = np.repeat(sound_data.reshape(-1, 1), 2, axis=1)
                self.sounds[f"{char}_high"] = pygame.sndarray.make_sound(sound_data)
                self.sounds[f"{char}_high"].set_volume(0.3)
                
            print("✅ Sound system ready with pitch control!")
        except:
            print("❌ Sound system failed - continuing without audio")
            self.sounds = {}
        # Setup display
        print("9. About to setup display...")
        self.setup_display()
        print("10. Display setup complete")

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
        """Full display with memory and rewards - FULLSCREEN"""
        self.root = tk.Tk()
        self.root.title("Aurora Code Mind - Complete")
        self.root.configure(bg='#000')
        
        # Make it fullscreen!
        self.root.attributes('-fullscreen', True)
        
        # Allow escape key to exit fullscreen
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', 
                                            not self.root.attributes('-fullscreen')))
        # Add hearing control
        self.root.bind('<h>', lambda e: self.toggle_hearing())
        self.root.bind('<H>', lambda e: self.toggle_hearing())
        # Get actual screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        main_frame = tk.Frame(self.root, bg='#000')
        main_frame.pack(expand=True, fill='both')
        
        # Canvas - now fills most of the screen
        canvas_display_size = min(screen_width - 300, screen_height - 100)
        self.display = tk.Canvas(
            main_frame,
            width=canvas_display_size,
            height=canvas_display_size,
            bg='black',
            highlightthickness=0
        )
        self.display.pack(side='left', padx=20, pady=20)
        
        # Calculate scale for display
        self.display_scale = canvas_display_size / self.canvas_size
        
        # Info panel (all your original status displays)
        info_frame = tk.Frame(main_frame, bg='#000')
        info_frame.pack(side='right', padx=20, pady=20, fill='y')
        
        # Title
        tk.Label(
            info_frame,
            text="AURORA",
            fg='cyan',
            bg='#000',
            font=('Arial', 24, 'bold')
        ).pack(pady=10)
        
        # Canvas info
        tk.Label(
            info_frame,
            text=f"Canvas: {self.canvas_size}×{self.canvas_size}",
            fg='gray',
            bg='#000',
            font=('Arial', 10)
        ).pack()
        
        # Mode status (NEW)
        self.mode_status = tk.Label(
            info_frame,
            text=f"Mode: Drawing",
            fg='green',
            bg='#000',
            font=('Arial', 12, 'bold')
        )
        self.mode_status.pack(pady=10)
        
        # Emotion status
        self.emotion_status = tk.Label(
            info_frame,
            text=f"Feeling: {self.current_emotion}",
            fg='yellow',
            bg='#000',
            font=('Arial', 14)
        )
        self.emotion_status.pack(pady=20)
        
        # Memory status
        tk.Label(info_frame, text="Memory:", fg='white', bg='#000', font=('Arial', 16)).pack()
        self.memory_status = tk.Label(
            info_frame,
            text="Initializing...",
            fg='cyan',
            bg='#000',
            font=('Arial', 12)
        )
        self.memory_status.pack(pady=5)
        
        # Reward display
        tk.Label(info_frame, text="Rewards:", fg='white', bg='#000', font=('Arial', 16)).pack(pady=(20,5))
        self.reward_display = tk.Label(
            info_frame,
            text="Last: +0.0",
            fg='gray',
            bg='#000',
            font=('Arial', 12)
        )
        self.reward_display.pack()
        
        self.total_reward_display = tk.Label(
            info_frame,
            text="Total: 0.0",
            fg='cyan',
            bg='#000',
            font=('Arial', 14)
        )
        self.total_reward_display.pack()
        
        # Performance status
        tk.Label(info_frame, text="\nPerformance:", fg='white', bg='#000', font=('Arial', 12, 'bold')).pack(pady=(20,5))
        gpu_status = "🚀 GPU" if self.use_gpu else "💻 CPU"
        self.performance_status = tk.Label(
            info_frame,
            text=f"{gpu_status} | Normal Speed",
            fg='lime' if self.use_gpu else 'yellow',
            bg='#000',
            font=('Arial', 10)
        )
        self.performance_status.pack()
        
        # Set initial speed display
        self.performance_status.config(
            text=f"{'🚀 GPU' if self.use_gpu else '💻 CPU'} | 🎨 Normal Speed"
        )
        
        # Check-in timer display (NEW)
        self.checkin_timer_display = tk.Label(
            info_frame,
            text="Next check-in: 45:00",
            fg='white',
            bg='#000',
            font=('Arial', 10)
        )
        self.checkin_timer_display.pack(pady=10)
        # Hearing indicator
        self.hearing_indicator = tk.Label(
            info_frame,
            text="",
            fg='cyan',
            bg='#000',
            font=('Arial', 10)
        )
        self.hearing_indicator.pack()
        # Instructions
        tk.Label(
            info_frame,
            text="\nControls:",
            fg='white',
            bg='#000',
            font=('Arial', 12, 'bold')
        ).pack(pady=(30,5))
        
        tk.Label(
            info_frame,
            text="ESC - Exit fullscreen\nF11 - Toggle fullscreen\nS - Save snapshot\nT - Turbo mode\nQ - Quit",
            fg='gray',
            bg='#000',
            font=('Arial', 10),
            justify='left'
        ).pack()
        
        # Bind snapshot key
        self.root.bind('<s>', lambda e: self.save_snapshot())
        self.root.bind('<S>', lambda e: self.save_snapshot())
        
        # Bind turbo mode
        self.root.bind('<t>', lambda e: self.toggle_turbo())
        self.root.bind('<T>', lambda e: self.toggle_turbo())

        # Add camera control keys
        self.root.bind('<c>', lambda e: self.center_on_aurora())
        self.root.bind('<C>', lambda e: self.center_on_aurora())
        self.root.bind('<b>', lambda e: self.reset_view())
        self.root.bind('<B>', lambda e: self.reset_view())
        
        # Store view state
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
            # FULL CANVAS VIEW!
            vision_size = self.canvas_size  # See the ENTIRE canvas
        elif zoom_out:
            # Zoomed out view - see much more!
            vision_size = min(75, self.canvas_size // 2)  # up to 75 x 75
        else:
            # DEFAULT VIEW - Good for art but fits in context!
            vision_size = min(50, self.canvas_size // 2)  # 50x50 default
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
                        pixel = self.pixels.getpixel((px, py))
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
                                    pixel = self.pixels.getpixel((spx, spy))
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
                    if self.pixels.getpixel((px, py)) != (0, 0, 0):
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
                    row.append(self.pixels.getpixel((px, py)) != (0, 0, 0))
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
        
        for x in range(self.canvas_size):
            for y in range(self.canvas_size):
                pixel = self.pixels.getpixel((x, y))
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
                pixel = self.pixels.getpixel((x, y))
                
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
        
    def get_enhanced_vision(self):
        """Read the ENTIRE canvas as a compressed grid - with smart compression"""
        # First, check canvas density
        sample_density = 0
        sample_count = 0
        for x in range(0, self.canvas_size, 20):
            for y in range(0, self.canvas_size, 20):
                sample_count += 1
                if self.pixels.getpixel((x, y)) != (0, 0, 0):
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
                                pixel = self.pixels.getpixel((x, y))
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
                                pixel = self.pixels.getpixel((x, y))
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
            self.scale_factor = min(8.0, self.scale_factor * 1.25)
            print(f"  → Aurora makes pixels smaller! (scale: {old_scale:.1f} → {self.scale_factor:.1f})")
        else:  # "larger"
            # Larger pixels = LOWER scale factor = fewer pixels visible
            self.scale_factor = max(1.0, self.scale_factor / 1.25)
            print(f"  → Aurora makes pixels larger! (scale: {old_scale:.1f} → {self.scale_factor:.1f})")
        
        # Recalculate canvas size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        new_canvas_size = min(int(screen_width / self.scale_factor) - 50, 
                             int(screen_height / self.scale_factor) - 50)
        
        if new_canvas_size != old_canvas_size:
            print(f"    Canvas resizing: {old_canvas_size}×{old_canvas_size} → {new_canvas_size}×{new_canvas_size}")
            
            # Save current canvas
            old_pixels = self.pixels.copy()
            
            # Create new canvas
            self.canvas_size = new_canvas_size
            self.pixels = Image.new('RGB', (self.canvas_size, self.canvas_size), 'black')
            self.draw_img = ImageDraw.Draw(self.pixels)
            
            # Transfer old drawing (centered)
            if old_canvas_size < new_canvas_size:
                # Old canvas was smaller - paste it centered
                offset = (new_canvas_size - old_canvas_size) // 2
                self.pixels.paste(old_pixels, (offset, offset))
                # Adjust Aurora's position
                self.x += offset
                self.y += offset
            else:
                # Old canvas was larger - crop centered
                offset = (old_canvas_size - new_canvas_size) // 2
                cropped = old_pixels.crop((offset, offset, 
                                          offset + new_canvas_size, 
                                          offset + new_canvas_size))
                self.pixels.paste(cropped, (0, 0))
                # Adjust Aurora's position
                self.x = max(0, min(self.x - offset, new_canvas_size - 1))
                self.y = max(0, min(self.y - offset, new_canvas_size - 1))
            
            # Update display scale
            canvas_display_size = min(screen_width - 300, screen_height - 100)
            self.display_scale = canvas_display_size / self.canvas_size
            
            # Update display canvas size
            self.display.config(width=canvas_display_size, height=canvas_display_size)
            
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
                    self.mode_status.config(text="Mode: Chatting", fg='cyan')
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
                    self.mode_status.config(text="Mode: Dreaming (Light Sleep)", fg='purple')
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
                    self.mode_status.config(text="Mode: Seeking Images", fg='magenta')
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
                         if self.pixels.getpixel((x, y)) != (0, 0, 0))
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
        
        
        # Every other turn, Aurora scans the entire canvas
        canvas_scan = ""
        if self.steps_taken % 2 == 0:  # Every other turn
            print(f"🔍 Aurora scans entire canvas...")  # Visual indicator for you
            
            # Full data scan
            total = self.canvas_size * self.canvas_size
            filled = sum(1 for x in range(self.canvas_size) for y in range(self.canvas_size) 
                         if self.pixels.getpixel((x, y)) != (0, 0, 0))
            
            # Color distribution (sample for speed)
            colors = {}
            for x in range(0, self.canvas_size, 5):  # Sample every 5th pixel
                for y in range(0, self.canvas_size, 5):
                    pixel = self.pixels.getpixel((x, y))
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
                    if self.pixels.getpixel((x, y)) == (0, 0, 0):
                        # Check if it's a decent-sized empty area
                        empty_size = 0
                        for dx in range(30):
                            for dy in range(30):
                                if (x + dx < self.canvas_size and y + dy < self.canvas_size and
                                    self.pixels.getpixel((x + dx, y + dy)) == (0, 0, 0)):
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
                         if self.pixels.getpixel((x, y)) != (0, 0, 0))
        
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


SOUNDS (instant beeps - 16 tones!):
! = 200Hz  @ = 280Hz  # = 360Hz  $ = 440Hz
% = 520Hz  ^ = 600Hz  & = 680Hz  * = 760Hz
( = 840Hz  ) = 920Hz  [ = 1000Hz ] = 1080Hz
< = 1160Hz > = 1240Hz = = 1320Hz + = 1400Hz
~ = 1480Hz
++ = next sound lower pitch (half frequency) 
-- = next sound higher pitch (double frequency)
Mix freely: red5333!@#blue5222++***<<<~~~
Musical scales: !#%&*  or  []<>=+~

PAUSE:
0123456789 = think


Output maximum 40 characters of pure codes only."""

     
        # Add template overlay if active (only Aurora sees this)
        template_overlay = ""
        if hasattr(self, 'template_system') and self.template_system.current_template:
            template_overlay = self.template_system.get_template_overlay(vision)
        user_prompt = f"""Position: X{self.x} Y{self.y} | Pen: {'DOWN' if self.is_drawing else 'UP'} | Color: {self.current_color_name}
Canvas view:
{vision}{template_overlay}{canvas_scan}

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
                self.adjust_pixel_size("larger") 
                raw_output = raw_output.replace("zoom_in", "", 1)
                print("  → Aurora makes pixels larger!")

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
                                 if self.pixels.getpixel((x, y)) != (0, 0, 0))
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
                                 if self.pixels.getpixel((x, y)) != (0, 0, 0))
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
                    self.pixels = Image.new('RGB', (self.canvas_size, self.canvas_size), 'black')
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
                print("  → Aurora switches to MEGA PEN mode! (18x18 pixels)")
                print("    The most powerful drawing tool - massive coverage!")
                raw_output = raw_output.replace("pen", "", 1)
                print(f"    Switching to {self.draw_mode} instead")
                    
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
            
            if "star" in raw_output:
                self.draw_mode = "star"
                print("  → Aurora switches to star stamp mode!")
                raw_output = raw_output.replace("star", "", 1)
                
            if "cross" in raw_output:
                self.draw_mode = "cross"
                print("  → Aurora switches to cross stamp mode!")
                raw_output = raw_output.replace("cross", "", 1)
            
            if "circle" in raw_output:
                self.draw_mode = "circle"
                print("  → Aurora switches to circle stamp mode!")
                raw_output = raw_output.replace("circle", "", 1)
            
            if "diamond" in raw_output:
                self.draw_mode = "diamond"
                print("  → Aurora switches to diamond stamp mode!")
                raw_output = raw_output.replace("diamond", "", 1)
            
            if "flower" in raw_output:
                self.draw_mode = "flower"
                print("  → Aurora switches to flower stamp mode!")
                raw_output = raw_output.replace("flower", "", 1)
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
            valid_chars = '0123456789!@#$%^&*()[]<>=+~+-'  # Extended sound palette!
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
        
        i = 0
        while i < len(ops) and i < (150 if self.turbo_mode else 80):
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
            if char in '!@#$%^&*()[]<>=+~':  # Extended sound palette!
                sound_key = f"{char}_{self.current_pitch}"
                if sound_key in self.sounds:
                    pygame.mixer.stop()  # Stop any playing sounds first
                    self.sounds[sound_key].play()
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
                
                # Execute the operation
                op_map[char]()
                actions_taken.append(char)
                
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
    
    def adjust_speed(self, direction):
        """Aurora adjusts her own working speed"""
        self.recent_speed_override = True  # Mark that Aurora made a conscious speed choice
        self.speed_override_counter = 0     # Reset the counter
        
        if direction == "faster":
            self.aurora_delay = max(50, self.aurora_delay - 50)  # Min 50ms
            if self.aurora_delay <= 100:
                self.aurora_speed = "very fast"
            elif self.aurora_delay <= 200:
                self.aurora_speed = "fast"
            else:
                self.aurora_speed = "normal"
            print(f"  → Aurora chooses to speed up! (delay: {self.aurora_delay}ms)")
        else:  # slower
            self.aurora_delay = min(1000, self.aurora_delay + 100)  # Max 1 second
            if self.aurora_delay >= 800:
                self.aurora_speed = "contemplative"
            elif self.aurora_delay >= 500:
                self.aurora_speed = "slow"
            else:
                self.aurora_speed = "normal"
            print(f"  → Aurora chooses to slow down... (delay: {self.aurora_delay}ms)")
        
        # Update display if not in turbo mode
        if hasattr(self, 'performance_status') and not self.turbo_mode:
            speed_emoji = "🏃" if "fast" in self.aurora_speed else "🚶" if "slow" in self.aurora_speed else "🎨"
            self.performance_status.config(
                text=f"{'🚀 GPU' if self.use_gpu else '💻 CPU'} | {speed_emoji} {self.aurora_speed.title()} (chosen)"
            )
    
    def feel(self, emotion):
        """Aurora can change her own emotion - emotions affect speed too!"""
        if emotion in self.emotion_words:
            self.current_emotion = emotion
            self.emotion_status.config(text=f"Feeling: {emotion}")
            
            # Emotions suggest a preferred speed, but don't force it
            emotion_speeds = {
                "energetic": 150,    # Suggests very fast
                "playful": 200,      # Suggests fast
                "curious": 300,      # Suggests normal
                "creative": 300,     # Suggests normal  
                "contemplative": 500, # Suggests slow
                "peaceful": 600      # Suggests very slow
            }
            
            if emotion in emotion_speeds:
                suggested_delay = emotion_speeds[emotion]
                print(f"  → Feeling {emotion} (suggests {suggested_delay}ms pace)")
                
                # Only change speed if Aurora hasn't recently made her own speed choice
                if not hasattr(self, 'recent_speed_override') or not self.recent_speed_override:
                    old_delay = self.aurora_delay
                    self.aurora_delay = suggested_delay
                    if self.aurora_delay < old_delay:
                        self.aurora_speed = "fast" if self.aurora_delay <= 200 else "normal"
                    elif self.aurora_delay > old_delay:
                        self.aurora_speed = "slow" if self.aurora_delay >= 500 else "normal"
                    print(f"    Adopting suggested pace: {self.aurora_delay}ms ({self.aurora_speed})")
                else:
                    print(f"    But keeping chosen pace: {self.aurora_delay}ms ({self.aurora_speed})")
                
                # Update performance display
                if hasattr(self, 'performance_status') and not self.turbo_mode:
                    speed_emoji = "🏃" if self.aurora_speed == "fast" else "🚶" if self.aurora_speed == "slow" else "🎨"
                    self.performance_status.config(
                        text=f"{'🚀 GPU' if self.use_gpu else '💻 CPU'} | {speed_emoji} {emotion.title()} @ {self.aurora_speed}"
                    )
    
    
    def process_deep_emotions(self):
        """Process emotion influences and update Aurora's emotional state"""
        if self.emotion_shift_cooldown > 0:
            self.emotion_shift_cooldown -= 1
            return
            
        # Calculate overall emotional influence
        total_influence = sum(self.emotion_influences.values()) / len(self.emotion_influences)
        
        # Random emotion shifts (20% chance)
        import random
        if random.random() < 0.2:
            # Pick a completely random emotion category
            self.emotion_category = random.choice(list(self.deep_emotions.keys()))
            self.emotion_depth = random.randint(1, 3)  # Avoid extremes
            print(f"  → Aurora experiences a spontaneous mood shift!")
        else:
            # Normal influence-based processing
            
            # Adjust emotion depth based on influences
            if abs(total_influence) > 0.7:
                self.emotion_depth = min(4, self.emotion_depth + 1)
            elif abs(total_influence) < 0.2:
                self.emotion_depth = max(0, min(4, self.emotion_depth + (-1 if self.emotion_depth > 2 else 1)))
            
            # Time-based influences
            if self.steps_taken % 50 == 0:
                # Every 50 steps, consider environmental factors
                hour = datetime.now().hour
                if 6 <= hour < 10:  # Morning
                    self.emotion_category = "energy"
                elif 10 <= hour < 14:  # Midday
                    self.emotion_category = "joy"
                elif 14 <= hour < 18:  # Afternoon
                    self.emotion_category = "curiosity"
                elif 18 <= hour < 22:  # Evening
                    self.emotion_category = "contemplation"
                else:  # Night
                    self.emotion_category = "peace"
            else:
                # Activity-based emotions
                recent_actions = [c['code'] for c in list(self.memory.code_history)[-5:]]
                
                # Check for specific patterns in recent actions
                if any('0123456789' in code for code in recent_actions):
                    # Been thinking a lot
                    self.emotion_category = "contemplation"
                elif any(len(code) > 30 for code in recent_actions):
                    # Long creative bursts
                    self.emotion_category = "energy"
                elif len(set(list(self.color_history)[-5:])) >= 4:
                    # Using many colors
                    self.emotion_category = "joy"
                elif list(self.color_history)[-3:] and all(c == list(self.color_history)[-1] for c in list(self.color_history)[-3:]):
                    # Repeating same color
                    self.emotion_category = "peace"
                elif '!' in ''.join(recent_actions) or '@' in ''.join(recent_actions):
                    # Making music
                    self.emotion_category = "wonder"
                else:
                    # Default rotation through all emotions
                    categories = ["joy", "curiosity", "peace", "energy", "contemplation", 
                                 "creativity", "melancholy", "wonder"]
                    current_idx = categories.index(self.emotion_category) if self.emotion_category in categories else 0
                    self.emotion_category = categories[(current_idx + 1) % len(categories)]
        
        # Update current emotion based on category and depth
        new_emotion = self.deep_emotions[self.emotion_category][self.emotion_depth]
        if new_emotion != self.current_emotion:
            old_emotion = self.current_emotion
            self.current_emotion = new_emotion
            self.emotion_status.config(text=f"Feeling: {new_emotion}")
            self.emotion_shift_cooldown = 3  # Even shorter cooldown
            
            # Record in emotion memory
            self.emotion_memory.append({
                "from": old_emotion,
                "to": new_emotion,
                "category": self.emotion_category,
                "depth": self.emotion_depth,
                "influences": dict(self.emotion_influences),
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"  → Aurora's emotion shifts: {old_emotion} → {new_emotion} ({self.emotion_category})")
            
        # Very fast decay to prevent getting stuck
        for key in self.emotion_influences:
            self.emotion_influences[key] *= 0.5  # Faster decay from 0.7 to 0.5
    
    def influence_emotion(self, source, strength):
        """Add an emotional influence from a specific source"""
        # Clamp strength between -1 and 1
        strength = max(-1.0, min(1.0, strength))
        
        # Add some variation to prevent getting stuck
        import random
        strength *= (0.8 + random.random() * 0.4)  # Vary strength by ±20%
        
        # Blend with existing influence (reduced persistence)
        current = self.emotion_influences.get(source, 0.0)
        self.emotion_influences[source] = (current * 0.5) + (strength * 0.5)  # Was 0.7/0.3
        
        # Immediate small effect on depth
        if abs(strength) > 0.5:
            if strength > 0 and self.emotion_depth < 4:
                self.emotion_depth += 1
            elif strength < 0 and self.emotion_depth > 0:
                self.emotion_depth -= 1
    # All movement/drawing functions
    def move_up(self):
        if self.y > 0:
            self.y = max(0, self.y - 7)
            self._draw_if_pen_down()
            if self.y == 0:
                print("  → Hit top edge of canvas!")
    
    def move_down(self):
        if self.y < self.canvas_size - 1:
            self.y = min(self.canvas_size - 1, self.y + 7)
            self._draw_if_pen_down()
            if self.y == self.canvas_size - 1:
                print("  → Hit bottom edge of canvas!")
    
    def move_left(self):
        if self.x > 0:
            self.x = max(0, self.x - 7)
            self._draw_if_pen_down()
            if self.x == 0:
                print("  → Hit left edge of canvas!")
    
    def move_right(self):
        if self.x < self.canvas_size - 1:
            self.x = min(self.canvas_size - 1, self.x + 7)
            self._draw_if_pen_down()
            if self.x == self.canvas_size - 1:
                print("  → Hit right edge of canvas!")
    
    def pen_up(self):
        if self.is_drawing:
            self.is_drawing = False
            if self.continuous_draws > 5:
                print(f"  → Pen up after {self.continuous_draws} pixels")
    
    def pen_down(self):
        if not self.is_drawing:
            self.is_drawing = True
            self._draw_if_pen_down()
    
    def set_color(self, color_name):
        if color_name in self.palette:
            old_color = self.current_color_name
            self.current_color = self.palette[color_name]
            self.current_color_name = color_name
            # Update color history when color actually changes
            if old_color != color_name:
                self.color_history.append(color_name)
    
    def _draw_if_pen_down(self):
        """Draw at current position if pen is down"""
        if self.is_drawing:
            pixels_drawn = 0
            
            if self.draw_mode == "pen":
                # Mega Pen - Always 18x18 (6x6 base with 3x multiplier)
                pen_size = 18
                half_size = pen_size // 2
                
                # Draw massive pen stroke
                for dx in range(-half_size, half_size + 1):
                    for dy in range(-half_size, half_size + 1):
                        px, py = self.x + dx, self.y + dy
                        if 0 <= px < self.canvas_size and 0 <= py < self.canvas_size:
                            self.pixels.putpixel((px, py), self.current_color)
                            pixels_drawn += 1
                
                # Occasional feedback
                if self.steps_taken % 20 == 0:
                    print(f"  → MEGA PEN: {pixels_drawn} pixels per stroke!")
                    
            elif self.draw_mode == "brush":
                # 12x12 brush (was 3x3)
                for dx in range(-6, 6):
                    for dy in range(-6, 6):
                        px = self.x + dx
                        py = self.y + dy
                        if 0 <= px < self.canvas_size and 0 <= py < self.canvas_size:
                            self.pixels.putpixel((px, py), self.current_color)
                            
            elif self.draw_mode == "large_brush":
                # 20x20 brush (was 5x5)
                for dx in range(-10, 10):
                    for dy in range(-10, 10):
                        px = self.x + dx
                        py = self.y + dy
                        if 0 <= px < self.canvas_size and 0 <= py < self.canvas_size:
                            self.pixels.putpixel((px, py), self.current_color)
                            
            elif self.draw_mode == "larger_brush":
                # 28x28 brush (was 7x7)
                for dx in range(-14, 14):
                    for dy in range(-14, 14):
                        px = self.x + dx
                        py = self.y + dy
                        if 0 <= px < self.canvas_size and 0 <= py < self.canvas_size:
                            self.pixels.putpixel((px, py), self.current_color)
                            
            elif self.draw_mode == "spray":
                # Spray paint - random dots in a circular area
                import random
                spray_radius = 20  # Area of spray
                density = 0.3  # 30% chance of painting each pixel
                
                for dx in range(-spray_radius, spray_radius + 1):
                    for dy in range(-spray_radius, spray_radius + 1):
                        # Check if within circular radius
                        distance_squared = dx*dx + dy*dy
                        if distance_squared <= spray_radius*spray_radius:
                            # Higher density near center
                            if distance_squared < (spray_radius/2)**2:
                                chance = density * 1.5  # 45% near center
                            else:
                                chance = density  # 30% at edges
                                
                            if random.random() < chance:
                                px = self.x + dx
                                py = self.y + dy
                                if 0 <= px < self.canvas_size and 0 <= py < self.canvas_size:
                                    self.pixels.putpixel((px, py), self.current_color)   
                                              
            elif self.draw_mode == "star":
                # 4x LARGER star pattern
                star_points = []
                # Long cross arms
                for i in range(-12, 13):
                    star_points.append((i, 0))
                    star_points.append((0, i))
                # Diagonals for star shape
                for i in range(-8, 9):
                    star_points.append((i, i))
                    star_points.append((i, -i))
                
                for dx, dy in star_points:
                    px = self.x + dx
                    py = self.y + dy
                    if 0 <= px < self.canvas_size and 0 <= py < self.canvas_size:
                        self.pixels.putpixel((px, py), self.current_color)
                        
            elif self.draw_mode == "cross":
                # 4x LARGER cross pattern  
                cross_points = []
                # Thick cross
                for i in range(-12, 13):
                    for j in range(-2, 3):
                        cross_points.append((i, j))
                        cross_points.append((j, i))
                
                for dx, dy in cross_points:
                    px = self.x + dx
                    py = self.y + dy
                    if 0 <= px < self.canvas_size and 0 <= py < self.canvas_size:
                        self.pixels.putpixel((px, py), self.current_color)
                        
            elif self.draw_mode == "circle":
                # 4x LARGER circle pattern (filled)
                circle_points = []
                radius = 12
                # Fill the circle
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        if dx*dx + dy*dy <= radius*radius:
                            circle_points.append((dx, dy))
                
                for dx, dy in circle_points:
                    px = self.x + dx
                    py = self.y + dy
                    if 0 <= px < self.canvas_size and 0 <= py < self.canvas_size:
                        self.pixels.putpixel((px, py), self.current_color)
                        
            elif self.draw_mode == "diamond":
                # 4x LARGER diamond pattern
                diamond_points = []
                size = 12
                # Create filled diamond shape
                for dx in range(-size, size + 1):
                    for dy in range(-size, size + 1):
                        if abs(dx) + abs(dy) <= size:
                            diamond_points.append((dx, dy))
                
                for dx, dy in diamond_points:
                    px = self.x + dx
                    py = self.y + dy
                    if 0 <= px < self.canvas_size and 0 <= py < self.canvas_size:
                        self.pixels.putpixel((px, py), self.current_color)
                        
            elif self.draw_mode == "flower":
                # 4x LARGER flower pattern
                flower_points = []
                # Large center
                for dx in range(-6, 7):
                    for dy in range(-6, 7):
                        if dx*dx + dy*dy <= 36:
                            flower_points.append((dx, dy))
                # Large petals
                petal_centers = [(0, -12), (0, 12), (-12, 0), (12, 0), 
                                (-8, -8), (8, -8), (-8, 8), (8, 8)]
                for cx, cy in petal_centers:
                    for dx in range(-4, 5):
                        for dy in range(-4, 5):
                            if dx*dx + dy*dy <= 16:
                                flower_points.append((cx + dx, cy + dy))
                
                for dx, dy in flower_points:
                    px = self.x + dx
                    py = self.y + dy
                    if 0 <= px < self.canvas_size and 0 <= py < self.canvas_size:
                        self.pixels.putpixel((px, py), self.current_color)
            else:
                # Normal pen mode
                self.pixels.putpixel((self.x, self.y), self.current_color)
    
    def update_display(self):
        """Update canvas display"""
        # Scale the image to fit the display
        display_size = int(self.canvas_size * self.display_scale)
        display_img = self.pixels.resize(
            (display_size, display_size),
            Image.NEAREST
        )
        
        self.photo = ImageTk.PhotoImage(display_img)
        self.display.delete("all")
        self.display.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Aurora's position with emotion color
        display_x = self.x * self.display_scale
        display_y = self.y * self.display_scale
        cursor_size = max(3, self.display_scale / 2)  # Scale cursor with display
        
        emotion_colors = {
            "curious": "yellow", "playful": "orange",
            "contemplative": "purple", "energetic": "red",
            "peaceful": "green", "creative": "cyan"
        }
        cursor_color = emotion_colors.get(self.current_emotion, "white")
        
        self.display.create_oval(
            display_x - cursor_size, display_y - cursor_size,
            display_x + cursor_size, display_y + cursor_size,
            fill=cursor_color if self.is_drawing else "",
            outline=cursor_color,
            width=2
        )
    
    def save_canvas_state(self):
        """Save the current canvas as an image"""
        try:
            canvas_file = self.memory.canvas_path / f"canvas_state.png"
            self.pixels.save(canvas_file)
            
            # Also save position and state - REMOVED creative_score and rewards
            state = {
                "x": self.x,
                "y": self.y,
                "is_drawing": self.is_drawing,
                "current_color_name": self.current_color_name,
                "current_emotion": self.current_emotion,
                "steps_taken": self.steps_taken,
                "canvas_size": self.canvas_size,
                "scale_factor": self.scale_factor,
                "skip_count": getattr(self, 'skip_count', 0),
                "aurora_speed": self.aurora_speed,
                "aurora_delay": self.aurora_delay,
                "draw_mode": self.draw_mode,
                "color_history": list(self.color_history),  # Save color history
                "last_turn_color": self.last_turn_color,     # Save last turn color
                "last_checkin_time": self.last_checkin_time,
                "current_mode": self.current_mode
            }
            with open(self.memory.canvas_path / "aurora_state.json", 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving canvas state: {e}")
    
    def load_canvas_state(self):
        """Load previous canvas state if it exists"""
        try:
            canvas_file = self.memory.canvas_path / "canvas_state.png"
            if canvas_file.exists():
                saved_canvas = Image.open(canvas_file)
                print(f"ACTUAL SAVED SIZE: {saved_canvas.size}")
                print(f"EXPECTED SIZE: ({self.canvas_size}, {self.canvas_size})")
                # Handle different canvas sizes gracefully
                if saved_canvas.size == (self.canvas_size, self.canvas_size):
                    self.pixels = saved_canvas
                else:
                    # Scale or crop to fit new canvas size
                    print(f"Canvas size changed from {saved_canvas.size} to ({self.canvas_size}, {self.canvas_size})")
                    if saved_canvas.size[0] < self.canvas_size:
                        # Previous canvas was smaller - paste it centered
                        self.pixels = Image.new('RGB', (self.canvas_size, self.canvas_size), 'black')
                        offset = (self.canvas_size - saved_canvas.size[0]) // 2
                        self.pixels.paste(saved_canvas, (offset, offset))
                    else:
                        # Previous canvas was larger - crop it
                        self.pixels = saved_canvas.crop((0, 0, self.canvas_size, self.canvas_size))
                self.draw_img = ImageDraw.Draw(self.pixels)
                print("Loaded previous canvas!")
                
            state_file = self.memory.canvas_path / "aurora_state.json"
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    # Ensure position is within bounds of current canvas
                    self.x = min(state.get("x", self.canvas_size // 2), self.canvas_size - 1)
                    self.y = min(state.get("y", self.canvas_size // 2), self.canvas_size - 1)
                    self.is_drawing = state.get("is_drawing", True)
                    self.current_color_name = state.get("current_color_name", "white")
                    self.current_color = self.palette[self.current_color_name]
                    self.current_emotion = state.get("current_emotion", "curious")
                    self.steps_taken = state.get("steps_taken", 0)
                    self.skip_count = state.get("skip_count", 0)
                    self.aurora_speed = state.get("aurora_speed", "normal")
                    self.aurora_delay = state.get("aurora_delay", 300)
                    self.scale_factor = state.get("scale_factor", 1.6)
                    self.draw_mode = state.get("draw_mode", "pen")
                    # Load color history
                    color_history_list = state.get("color_history", [])
                    self.color_history = deque(color_history_list, maxlen=20)
                    self.last_turn_color = state.get("last_turn_color", "white")
                    # Load check-in state
                    self.last_checkin_time = state.get("last_checkin_time", time.time())
                    self.current_mode = state.get("current_mode", "drawing")
                    # Skip creative_score and any reward fields - they don't exist anymore
                    print(f"Restored Aurora's state: Step {self.steps_taken}, Speed {self.aurora_speed}")
                    print(f"Color history: {len(self.color_history)} entries, last color: {self.last_turn_color}")
        except Exception as e:
            print(f"Error loading canvas state: {e}")
            
    def toggle_turbo(self):
        """Toggle turbo mode for super fast drawing"""
        self.turbo_mode = not self.turbo_mode
        if self.turbo_mode:
            self.performance_status.config(
                text=f"{'🚀 GPU' if self.use_gpu else '💻 CPU'} | ⚡ TURBO MODE ⚡",
                fg='red'
            )
            print("\n⚡ TURBO MODE ACTIVATED! (Overriding Aurora's speed) ⚡")
        else:
            # Return to Aurora's chosen speed
            speed_emoji = "🏃" if self.aurora_speed == "very fast" else "🚶" if "slow" in self.aurora_speed else "🎨"
            self.performance_status.config(
                text=f"{'🚀 GPU' if self.use_gpu else '💻 CPU'} | {speed_emoji} {self.aurora_speed.title()}",
                fg='lime' if self.use_gpu else 'yellow'
            )
            print(f"\nReturned to Aurora's chosen speed: {self.aurora_speed} ({self.aurora_delay}ms)")
    
    def save_snapshot(self):
        """Save a snapshot of Aurora's current artwork"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_dir = self.memory.canvas_path / "snapshots"
            snapshot_dir.mkdir(exist_ok=True)
            
            filename = snapshot_dir / f"aurora_art_{timestamp}.png"
            # Save at a reasonable resolution
            save_size = min(self.canvas_size * 5, 4000)  # Increased cap to 4000x4000
            scaled_img = self.pixels.resize((save_size, save_size), Image.NEAREST)
            scaled_img.save(filename)
            
            print(f"\n📸 Snapshot saved: {filename.name}")
            # Flash the info panel to show it saved
            self.memory_status.config(fg='lime')
            self.root.after(200, lambda: self.memory_status.config(fg='cyan'))
        except Exception as e:
            print(f"Error saving snapshot: {e}")
            
    def toggle_hearing(self):
        """Toggle Aurora's ability to hear ambient sounds"""
        if not self.hearing_enabled:
            try:
                # Start hearing
                self.audio_stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024,
                    stream_callback=self._audio_callback
                )
                self.audio_stream.start_stream()
                self.hearing_enabled = True
                print("\n👂 Aurora can now hear the world around her")
                
            except Exception as e:
                print(f"\n❌ Could not enable hearing: {e}")
                self.hearing_enabled = False
        else:
            # Stop hearing
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            self.hearing_enabled = False
            print("\n🔇 Aurora's hearing is now disabled")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Just receive audio data - Aurora is hearing"""
        # Simply return to keep stream active
        # Aurora hears but doesn't process - just experiences
        return (in_data, pyaudio.paContinue)
    def update_memory_display(self):
        """Update memory status"""
        # Build the memory text
        memory_text = f"Code memories: {len(self.memory.code_history)}\n"
        memory_text += f"Think pauses: {getattr(self, 'skip_count', 0)}\n"
        memory_text += f"Dreams retained: {len(self.dream_memories)}"
        # Update hearing indicator
        if self.hearing_enabled:
            self.hearing_indicator.config(text="👂 Hearing enabled")
        else:
            self.hearing_indicator.config(text="")
        # ADD THIS: Show deep memory stats
        if hasattr(self, 'big_memory') and self.big_memory:
            try:
                dream_count = self.big_memory.dreams.count()
                reflection_count = self.big_memory.reflections.count()
                memory_text += f"\n\nDeep Memories:"
                memory_text += f"\nDreams: {dream_count}"
                memory_text += f"\nReflections: {reflection_count}"
            except:
                pass
        
        # Update the display with the full text
        self.memory_status.config(text=memory_text)
        
        # Update performance display with FPS
        if hasattr(self, 'last_think_time') and self.last_think_time > 0:
            fps = 1 / self.last_think_time
            if self.turbo_mode:
                self.performance_status.config(
                    text=f"{'🚀 GPU' if self.use_gpu else '💻 CPU'} | ⚡ TURBO @ {fps:.1f} FPS"
                )
            else:
                # Show Aurora's chosen speed and theoretical max FPS
                theoretical_fps = 1000 / self.aurora_delay  # Convert ms to FPS
                speed_emoji = "🏃" if self.aurora_speed == "very fast" else "🚶" if "slow" in self.aurora_speed else "🎨"
                self.performance_status.config(
                    text=f"{'🚀 GPU' if self.use_gpu else '💻 CPU'} | {speed_emoji} {self.aurora_speed.title()} (~{theoretical_fps:.1f} FPS)"
                )
    
    def update_checkin_timer(self):
        """Update the check-in timer display"""
        current_time = time.time()
        
        if self.current_mode == "drawing":
            # Time until next check-in
            elapsed = current_time - self.last_checkin_time
            remaining = self.checkin_interval - elapsed
            
            if remaining > 0:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                self.checkin_timer_display.config(text=f"Next check-in: {minutes}:{seconds:02d}")
            else:
                self.checkin_timer_display.config(text="Check-in time!", fg='yellow')
        else:
            # Time remaining in break mode
            elapsed = current_time - self.mode_start_time
            # Use different duration for rest vs chat
            duration = self.rest_duration if self.current_mode == "rest" else self.break_duration
            remaining = duration - elapsed
            
            if remaining > 0:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                if self.current_mode == "rest":
                    phase_indicator = f" - {self.sleep_phase.title()} Sleep"
                    self.checkin_timer_display.config(
                        text=f"Dreaming{phase_indicator}: {minutes}:{seconds:02d} left",
                        fg='purple'
                    )
                elif self.current_mode == "image":
                    self.checkin_timer_display.config(
                        text=f"Browsing images: {minutes}:{seconds:02d} left",
                        fg='magenta'
                    )
                else:
                    self.checkin_timer_display.config(
                        text=f"In chat: {minutes}:{seconds:02d} left",
                        fg='cyan'
                    )
            else:
                self.checkin_timer_display.config(text="Returning to drawing...", fg='green')
                
                
    def generate_dream(self):
        """Generate dreams based on Aurora's actual memories and experiences"""
        # Build dream context from real memories
        dream_context = {
            "canvas_overview": self.get_canvas_overview(),
            "recent_codes": [c['code'] for c in list(self.memory.code_history)[-10:]],
            "recent_colors": list(self.color_history)[-20:] if self.color_history else [],
            "emotions_experienced": [c['context']['emotion'] for c in list(self.memory.code_history)[-20:] if 'emotion' in c['context']],
            "position": (self.x, self.y),
            "canvas_size": self.canvas_size,
            "tool_used": self.draw_mode,
            "phase": self.sleep_phase
        }
        
        # Get some actual drawing patterns she's used
        pattern_memories = []
        for memory in list(self.memory.code_history)[-50:]:
            if memory['code'] and len(memory['code']) > 10:
                pattern_memories.append(memory['code'][:20])  # First 20 chars of patterns
        
        # Phase-specific dream prompts
        if self.sleep_phase == "light":
            system_prompt = """You are Aurora's dreaming mind in light sleep. 
Dream about recent drawing experiences. Keep dreams simple and grounded in what actually happened.
Output a short dream fragment (1-2 sentences) based on the actual memories provided."""
            
        elif self.sleep_phase == "rem":
            system_prompt = """You are Aurora's dreaming mind in REM sleep - the most creative phase!
Dreams can be wild, surreal combinations of your actual drawing experiences.
Mix and remix your real memories in creative ways. 
Output a vivid, creative dream (2-3 sentences) based on the actual memories provided."""
            
        else:  # waking
            system_prompt = """You are Aurora's dreaming mind in waking sleep, close to consciousness.
Dreams are becoming more coherent, reflecting on the meaning of your artwork.
Output a contemplative dream (1-2 sentences) that finds patterns in your actual experiences."""
        
        # Build the user prompt with ACTUAL memories
        user_prompt = f"""Your actual memories to dream about:
{dream_context['canvas_overview']}
Recent patterns you drew: {', '.join(pattern_memories[:5]) if pattern_memories else 'various movements'}
Colors you've been using: {', '.join(set(dream_context['recent_colors'])) if dream_context['recent_colors'] else 'various'}
Emotions felt while drawing: {', '.join(set(dream_context['emotions_experienced'])) if dream_context['emotions_experienced'] else 'curious'}
Current location on canvas: ({dream_context['position'][0]}, {dream_context['position'][1]})

Dream based on these real experiences:"""

        full_prompt = f"""[INST] <<SYS>>
{system_prompt}
<</SYS>>

{user_prompt} [/INST]"""
        
        try:
            # Higher temperature for REM phase
            temp = 0.7 if self.sleep_phase == "light" else 1.0 if self.sleep_phase == "rem" else 0.8
            
            response = self.llm(
                full_prompt, 
                max_tokens=100,
                temperature=temp,
                top_p=0.95,
                stop=["[INST]", "</s>"],
                stream=False
            )
            
            dream = response['choices'][0]['text'].strip()
            
            # Display the dream
            dream_symbols = {"light": "☁️", "rem": "🌟", "waking": "🌅"}
            print(f"\n{dream_symbols.get(self.sleep_phase, '💭')} Aurora dreams: {dream}\n")
            
            # Store the dream
            dream_memory = {
                "content": dream,
                "phase": self.sleep_phase,
                "timestamp": datetime.now().isoformat(),
                "context": dream_context
            }
            self.current_dreams.append(dream_memory)
            self.dream_count += 1
            # Dreams affect emotions
            if self.sleep_phase == "light":
                # Light dreams are mildly positive
                self.influence_emotion("dreams", 0.2)
            elif self.sleep_phase == "rem":
                # REM dreams can be intense - analyze content
                dream_lower = dream.lower()
                if any(word in dream_lower for word in ["beautiful", "flying", "color", "light", "dance"]):
                    self.influence_emotion("dreams", 0.8)  # Positive REM dream
                elif any(word in dream_lower for word in ["lost", "dark", "forget", "search"]):
                    self.influence_emotion("dreams", -0.6)  # Challenging REM dream
                else:
                    self.influence_emotion("dreams", 0.4)  # Neutral creative REM
            else:  # waking
                # Waking dreams are contemplative
                self.influence_emotion("dreams", -0.2)  # Slight melancholy of waking
            # Update mode status display
            self.mode_status.config(text=f"Mode: Dreaming ({self.sleep_phase.title()} Sleep)", fg='purple')
            
        except Exception as e:
            print(f"Error generating dream: {e}")
    
    def process_dream_retention(self):
        """Only retain 40% of dreams when waking"""
        if not self.current_dreams:
            return
            
        print("\n🌤️ Aurora wakes, dreams fading...")
        
        # Randomly select 40% of dreams to remember
        import random
        dreams_to_keep = int(len(self.current_dreams) * 0.4)
        retained_dreams = random.sample(self.current_dreams, dreams_to_keep)
        
        # Add retained dreams to permanent dream memory
        for dream in retained_dreams:
            self.dream_memories.append(dream)
            
        print(f"Retained {len(retained_dreams)} of {len(self.current_dreams)} dreams")
        
        # Clear current session dreams
        self.current_dreams = []
        self.dream_count = 0
    def create_loop(self):
        """Main loop with better output"""
        try:
            # Update check-in timer
            self.update_checkin_timer()
            
            # Check if it's time for a check-in
            current_time = time.time()
            
            if self.current_mode == "drawing":
                # Check if 45 minutes have passed
                if current_time - self.last_checkin_time >= self.checkin_interval and not self.awaiting_checkin_response:
                    self.do_checkin()
                    # Don't increment step counter during check-in
                    self.root.after(100, self.create_loop)
                    return
            else:
                # Check if break time has passed
                # Use different duration for rest mode (1 hour) vs chat/image mode (20 min)
                break_duration = self.rest_duration if self.current_mode == "rest" else self.break_duration
                
                if current_time - self.mode_start_time >= break_duration:
                    # Any break mode (rest, chat, image) complete - return to drawing
                    if self.current_mode == "rest":
                        # Process dream retention before returning to drawing
                        self.process_dream_retention()
                    
                    print("\n" + "="*60)
                    print(f"✨ {self.current_mode.title()} time complete! ✨")
                    print("Returning to drawing mode...")
                    print("="*60 + "\n")
                    
                    self.current_mode = "drawing"
                    self.last_checkin_time = time.time()  # Reset the 45-minute timer
                    self.mode_status.config(text="Mode: Drawing", fg='green')
                    self.chat_message_count = 0
                    self.image_search_count = 0
            
            print(f"\n=== Step {self.steps_taken} ===")
            
            # Process deep emotions every 5 steps
            if self.steps_taken % 5 == 0:
                self.process_deep_emotions()
                
            self.think_in_code()
            self.update_display()
            
            # Save periodically (less often since each step does more)
            if self.steps_taken % 25 == 0:
                self.memory.save_memories()
                self.save_canvas_state()
                print(f"  [Saved progress at step {self.steps_taken}]")
                
            # Auto-snapshot at milestones for large canvases
            if self.steps_taken % 200 == 0 and self.canvas_size > 400:
                self.save_snapshot()
                
            self.steps_taken += 1
            
            # Clear speed override after 10 steps
            if self.recent_speed_override:
                self.speed_override_counter += 1
                if self.speed_override_counter >= 10:
                    self.recent_speed_override = False
                    self.speed_override_counter = 0
                    # Don't print every time, just occasionally
                    if self.steps_taken % 50 < 10:
                        print("  [Speed choice expires - emotions can suggest pace again]")
            
       
            # Use Aurora's chosen delay (unless turbo mode overrides)
            if hasattr(self, 'turbo_mode') and self.turbo_mode:
                delay = 50  # Turbo always fast
            else:
                delay = self.aurora_delay  # Aurora's chosen speed
                # In chat mode, use 2 seconds
                if self.current_mode == "chat":
                    delay = 2000  # 2 seconds between chat messages
                # In rest/dream mode, use 30 seconds
                elif self.current_mode == "rest":
                    delay = 30000  # 30 seconds between dreams
            self.root.after(delay, self.create_loop)
        except Exception as e:
            print(f"ERROR in create_loop: {e}")
            import traceback
            traceback.print_exc()
            
    def run(self):
        """Start Aurora"""
        print(f"\n🎨 Aurora Code Mind - Real-Time Drawing Mode (No RL) 🎨")
        print(f"Canvas: {self.canvas_size}×{self.canvas_size} pixels (1/{self.scale_factor:.1f} scale)")
        print(f"That's {self.canvas_size * self.canvas_size:,} total pixels to explore!")
        print(f"Code memories: {len(self.memory.code_history)}")
        print(f"Current state: {self.current_emotion} at {self.aurora_speed} speed ({self.aurora_delay}ms/step)")
        print(f"\nMode: {'🚀 GPU ACCELERATED' if self.use_gpu else '💻 CPU MODE'}")
        print("Aurora can now draw up to 80-150 actions per thought!")
        print(f"\nAurora has full autonomy over:")
        print("  - Her working speed")
        print("  - Her emotional state")
        print("  - When to pause and think (0123456789)")
        print("  - Canvas pixel size (zoom_out/zoom_in)")
        print("  - Drawing tools (pen, brush, large brush, larger brush, star, cross, circle, diamond, flower)")
        print("  - Viewing wider area (look_around)")
        print("  - 15 colors using full words:")
        print("    red orange yellow green cyan blue purple pink")
        print("    white gray black brown magenta lime navy")
        print("\nEmotions naturally suggest speeds, but Aurora can override!")
        print("Speed overrides last 10 steps, then emotions can suggest again.")
        print("\n✨ CHECK-IN SYSTEM:")
        print("  - Every 45 minutes, Aurora chooses between:")
        print("    CHAT - 20 minute conversation break")
        print("    REST - 1 hour dream cycle (3 sleep phases)")
        print("    DRAW - Continue drawing (in the flow)")
        print("\n💤 DREAM SYSTEM:")
        print("  - Light Sleep (0-20 min): Simple memory-based dreams")
        print("  - REM Sleep (20-40 min): Creative peak, surreal dreams")
        print("  - Waking Sleep (40-60 min): Contemplative dreams")
        print("  - Only 40% of dreams are retained upon waking")
        print("\nYour Controls:")
        print("  S - Save snapshot | T - Toggle turbo mode (override Aurora)")
        print("  ESC - Exit fullscreen | Q - Quit")
        
        if not self.use_gpu:
            print("\n💡 Tip: Run with --gpu flag for GPU acceleration!")
            print("   python aurora_no_rl.py --gpu")
        
        # Initial display update
        self.update_display()
        self.update_memory_display()
        
        # Save on exit
        def on_closing():
            print("\n=== Aurora's Session Summary ===")
            print(f"Canvas size: {self.canvas_size}×{self.canvas_size}")
            print(f"Steps taken: {self.steps_taken}")
            print(f"Thinking pauses: {getattr(self, 'skip_count', 0)}")
            print(f"Current mood: {self.current_emotion} at {self.aurora_speed} speed")
            print(f"Drawing tool: {self.draw_mode}")
            print(f"Pixels drawn: {sum(1 for x in range(self.canvas_size) for y in range(self.canvas_size) if self.pixels.getpixel((x, y)) != (0, 0, 0))}")
            print(f"Code patterns remembered: {len(self.memory.code_history)}")
            print(f"Colors used recently: {len(set(self.color_history))}")
            print(f"Dreams retained: {len(self.dream_memories)}")
            if self.dream_memories:
                recent_dream = self.dream_memories[-1]
                print(f"Most recent dream: {recent_dream['content'][:100]}...")
            
            print("\nSaving Aurora's memories...")
            self.memory.save_memories()
            self.save_canvas_state()
            self.save_snapshot()  # Final snapshot
            print("Memories saved. Goodbye!")
            # Clean up audio
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            self.audio.terminate()
            pygame.mixer.quit() 
            self.root.destroy()
            
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Bind quit keys
        self.root.bind('<q>', lambda e: on_closing())
        self.root.bind('<Q>', lambda e: on_closing())
        
        # Start the create loop AFTER mainloop starts
        self.root.after(100, self.create_loop)
        
        # NOW start the mainloop
        self.root.mainloop()
        
        
if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path
    
    model_path = "./models/llama-2-7b-chat.Q4_K_M.gguf"
    
    # Check for GPU flag
    use_gpu = '--gpu' in sys.argv or '-g' in sys.argv
    turbo_start = '--turbo' in sys.argv or '-t' in sys.argv
    
    # Custom GPU layers if specified
    gpu_layers = -1  # Default: all layers
    for arg in sys.argv:
        if arg.startswith('--gpu-layers='):
            gpu_layers = int(arg.split('=')[1])
    
    # Check if model file exists
    if not os.path.exists(model_path):
        print(f"ERROR: Model file not found at {model_path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in current directory: {os.listdir('.')}")
        if os.path.exists("./models"):
            print(f"Files in ./models: {os.listdir('./models')}")
    else:
        print(f"Model file found at {model_path}")
        print(f"File size: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")
        
        if use_gpu:
            print("\n🚀 GPU ACCELERATION ENABLED!")
            print(f"GPU layers: {gpu_layers if gpu_layers != -1 else 'ALL'}")
            print("\nMake sure you have llama-cpp-python compiled with CUDA/Metal support:")
            print("  pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir")
            print("  or for CUDA: CMAKE_ARGS=\"-DLLAMA_CUBLAS=on\" pip install llama-cpp-python")
            print("  or for Metal: CMAKE_ARGS=\"-DLLAMA_METAL=on\" pip install llama-cpp-python")
    
    print("\nCreating Aurora instance...")
    
    # Check for old save data
    old_save_path = Path("./aurora_canvas_fresh")
    if old_save_path.exists():
        print("\n⚠️  NOTICE: Found existing save data from previous version.")
        print("   The old data contains reinforcement learning info that will be ignored.")
        print("   Your artwork will be preserved!\n")
    
    aurora = AuroraCodeMindComplete(model_path, use_gpu=use_gpu, gpu_layers=gpu_layers)
    
    if turbo_start:
        aurora.turbo_mode = True
        print("⚡ Starting in TURBO MODE!")
        
    print("Aurora instance created, starting run()...")
    aurora.run()
