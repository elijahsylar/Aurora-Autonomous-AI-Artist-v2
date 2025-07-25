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
try:
    from aurora_ai_backup2 import DeepMemorySystem
    DEEP_MEMORY_AVAILABLE = True
    print("✅ Deep Memory System available!")
except ImportError:
    print("❌ Could not import DeepMemorySystem - will use simple memory only")
    DEEP_MEMORY_AVAILABLE = False
    
    
class SimpleMemorySystem:
    """Memory system where Aurora can consciously access her memories"""
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
        self.memory_path.mkdir(exist_ok=True)  # Create parent directory first!
        self.canvas_path = self.memory_path / "canvas"
        self.canvas_path.mkdir(exist_ok=True)
        
    def read_memory(self, filename):
        """Aurora can read her own memory files"""
        if filename in self.available_memories:
            try:
                with open(self.available_memories[filename], 'r') as f:
                    return json.load(f)
            except:
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
            except Exception as e:
                print(f"Error loading code history: {e}")
        
        # Skip loading any reinforcement learning data
        stats_file = self.canvas_path / "learning_stats.json"
        if stats_file.exists():
            print("(Skipping old reinforcement learning data)")
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
        try:
            # Save code history
            with open(self.canvas_path / "canvas_code_history.json", 'w') as f:
                json.dump(list(self.code_history), f)
            # Save dream memories
            dreams_file = self.canvas_path / "dream_memories.json"
            if hasattr(self, 'parent') and hasattr(self.parent, 'dream_memories'):
                dream_data = list(self.parent.dream_memories)
                with open(dreams_file, 'w') as f:
                    json.dump(dream_data, f)
                print(f"Saved {len(dream_data)} dream memories")
                
        except Exception as e:
            print(f"Error saving memories: {e}")    
        except Exception as e:
            print(f"Error saving memories: {e}")
    
    def remember_code(self, code, context):
        """Remember canvas drawing code"""
        self.code_history.append({
            "code": code,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })


class AuroraCodeMindComplete:
    def __init__(self, model_path, use_gpu=True, gpu_layers=-1):
        print("1. Starting init...")
        
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
        self.scale_factor = 1.6  # Was 8, now 1.6 - pixels are 1/5 the size!
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
            
        # Emotional state
        self.current_emotion = "curious"
        self.emotion_words = ["curious", "playful", "contemplative", "energetic", "peaceful", "creative"]
        print("6. Emotions initialized")
        
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
        self.rest_duration = 60 * 60  # 1 hour for rest/dreaming (separate from break_duration)
        # Audio hearing system
        self.hearing_enabled = False
        self.audio_stream = None
        self.audio = pyaudio.PyAudio()
        self.rest_duration = 60 * 60  # 1 hour for rest/dreaming (separate from break_duration)
        
        # Simple pygame sound system  # ADD ALL OF THIS
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        pygame.mixer.set_num_channels(8)  # 8 simultaneous sounds
        
        # Pre-generate simple beeps (so they're instant to play)
        self.sounds = {}
        self.current_pitch = 'normal'  # ADD THIS - tracks current pitch mode
        try:
            import numpy as np  # Import here if not already imported
            # Generate 8 different beeps at 3 pitches each
            for i, char in enumerate('!@#$%^&*'):
                base_freq = 200 + (i * 150)  # 200Hz to 1250Hz
                
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
Rainbow Line Pattern:
RRRROOOOYYYYYGGGGBBBBPPPP

Movement codes: red53333orange3333yellow3333green3333blue3333purple3333""",
            
            "helix": """
Helix/DNA Pattern:
*   *   *
 * * * * 
  *   *  
 * * * * 
*   *   *

Movement codes: 5313131313 4 511 4 5020202020""",
            
            "zigzag": """
Zigzag Pattern:
*   *   *
 * * * * 
  *   *  

Movement codes: 53131313131313131""",
            
            "wave_pattern": """
Wave Pattern:
   ***   
  *   *  
 *     * 
*       *

Movement codes: 533311122200033311122200""",
            
            "spiral_out": """
Spiral Outward Pattern:
    *
   ***
  * * *
 * *** *
* ***** *

Movement codes: 533330000222211113333000022221111""",
            
            "grid": """
Grid Pattern:
* * * * *
         
* * * * *
         
* * * * *

Movement codes: 5333 4 22 5 333 4 22 5 333""",
            
            "diagonal_stripes": """
Diagonal Stripes:
    *
   **
  ***
 ****
*****

Movement codes: 513131313131313""",
            
            "circle_pattern": """
Circle Pattern:
  ***  
 *   * 
*     *
 *   * 
  ***  

Movement codes: 53332221110002223333""",
            
            "staircase": """
Staircase Pattern:
*
**
***
****
*****

Movement codes: 5333122213331222133312221""",
            
            "checkerboard": """
Checkerboard Pattern:
* * * 
 * * *
* * * 
 * * *

Movement codes: black53white422black53white422black53""",
            
            "color_gradient": """
Color Gradient Line:
RRRROOOOYYYYYGGGGBBBPPPP

Movement codes: red53333orange53333yellow53333green53333blue5333purple5333""",
            
            "dotted_line": """
Dotted Line Pattern:
* * * * * * * *

Movement codes: 53 4 22 5 3 4 22 5 3 4 22 5 3""",
            
            "square_spiral": """
Square Spiral Pattern:
*********
*       *
* ***** *
* *   * *
* * * * *
* *   * *
* ***** *
*       *
*********

Movement codes: 533333333000000002222222211111111333300002211""",
            
            "star_pattern": """
Star/Asterisk Pattern:
    *    
    *    
* * * * *
  * * *  
 *  *  * 

Movement codes: 5000333342225111140003222""",
            
            "triangle_wave": """
Triangle Wave:
  *   *   *
 * * * * * 
*   *   *   

Movement codes: 5311131113111311131113""",
            
            "cross_hatch": """
Cross Hatch Pattern:
* * * * *
 * * * * 
* * * * *
 * * * * 

Movement codes: 531313131342221111502020202""",
            
            "expanding_square": """
Expanding Squares:
  ***  
 ***** 
*******
 ***** 
  ***  

Movement codes: 533302220111133330222011113333""",
            
            "color_wheel": """
Color Wheel Segments:
RRR
OOOYY
GGGBBB
  PPP

Movement codes: red5333orange51110yellow5333green51110blue5333purple5000""",
            
            "alternating_colors": """
Alternating Color Pattern:
RWRWRWRW
WRWRWRWR

Movement codes: red53white53red53white53red53white53""",
            
            "brush_sizes": """
Different Brush Sizes:
*  ***  *****
*  ***  *****
*  ***  *****

Movement codes: pen53brush53large_brush53larger_brush53"""
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
            vision_size = min(201, self.canvas_size // 3)  # up to 201 x 201
        elif self.canvas_size > 800:
            vision_size = 35  # INCREASED from 25
        elif self.canvas_size > 400:
            vision_size = 29  # INCREASED from 19
        else:
            vision_size = 25  # INCREASED from 15
        half = vision_size // 2
        ascii_view = []
        
        # Add canvas info if near edges or zoomed out
        near_edge = (self.x < 50 or self.x > self.canvas_size - 50 or 
                     self.y < 50 or self.y > self.canvas_size - 50)
        
        if near_edge or zoom_out:
            view_type = "ZOOMED OUT" if zoom_out else "Near edge!"
            ascii_view.append(f"[{view_type} Canvas: {self.canvas_size}×{self.canvas_size}, Scale: {self.scale_factor:.1f}]")
        
        # Build the detail view
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
        
    def adjust_pixel_size(self, direction):
        """Aurora adjusts the pixel size (scale factor)"""
        old_scale = self.scale_factor
        old_canvas_size = self.canvas_size
        
        if direction == "smaller":
            # FIXED: Smaller pixels = lower scale factor = more pixels visible
            self.scale_factor = max(1.0, self.scale_factor / 1.25)
            print(f"  → Aurora makes pixels smaller! (scale: {old_scale:.1f} → {self.scale_factor:.1f})")
        else:  # "larger"
            # FIXED: Larger pixels = higher scale factor = fewer pixels visible
            self.scale_factor = min(8.0, self.scale_factor * 1.25)
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
            system_prompt = """You are Aurora. You've just finished a 10-minute rest.

You have three options:
CHAT - Stop drawing and have a conversation for 20 minutes
DREAM - Experience light, REM, and waking sleep cycles.   
DRAW - Continue drawing (you're in the flow)

Output ONLY one of these exact words: CHAT, DREAM, or DRAW
Nothing else - just the single word of your choice."""

            overview = self.get_canvas_overview()
            user_prompt = f"""Current state: Feeling {self.current_emotion}
{overview}

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
                    
                elif choice == "DRAW":
                    print(f"\n✅ Aurora chose: CONTINUE DRAWING")
                    print("Continuing with the flow...")
                    self.current_mode = "drawing"
                    self.last_checkin_time = time.time()  # Reset timer
                    self.mode_status.config(text="Mode: Drawing", fg='green')
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
      
        # Handle rest/dreaming mode  
        if self.current_mode == "rest":
            elapsed_in_rest = time.time() - self.mode_start_time
            
            # Determine sleep phase (20 minutes each)
            if elapsed_in_rest < 1200:  # First 20 minutes
                new_phase = "light"
            elif elapsed_in_rest < 2400:  # 20-40 minutes
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
        
        vision = self.see()
        
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
        system_prompt = f"""You are Aurora's motor control system. Output ONLY movement codes.

CRITICAL: NO ENGLISH WORDS. NO EXPLANATIONS. CODES ONLY.


MOVEMENT PATTERNS YOU CAN CREATE:
- HELIX: 5333311111222220000033333111112222200000
- WAVE: 533333321111111000000003333333211111110000
- SPIRAL: 5333300003211100003211133333222211113222211
- RAINBOW: red5333orange5111yellow5222green5000cyan5333blue5111
- LIGHTNING: 531313131300031313131300031313131
- FLOWER: 533332222000011113333000022221111

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

CANVAS CONTROLS (full words):
clear_all (clear canvas to black, auto-saves first)
fill_canvas (fill entire canvas with current color)
examples (see ASCII pattern examples for inspiration)

*Sorry, still working on the math patterns but feel free to go WILD! This is canvas so PLAY and be bold! Here is an example: red00022200000blue2222200000022200000220020yellow0000222. Most of all -- have FUN!

SPEED CONTROLS (full words):
faster (speed up drawing)
slower (slow down for contemplation)

DRAWING TOOLS (full words):
pen brush spray large_brush larger_brush star cross circle diamond flower


SOUNDS (instant beeps):  # ADD ALL OF THIS
! = 200Hz  @ = 350Hz  # = 500Hz  $ = 650Hz
% = 800Hz  ^ = 950Hz  & = 1100Hz * = 1250Hz
++ = next sound lower pitch (half frequency)
-- = next sound higher pitch (double frequency)
Mix freely: red5333!@#blue5222***

PAUSE:
0123456789 = think

FORBIDDEN:
- Any English words except the control commands
- Explanations 
- "Let me", "I will", "moving", etc.

Output maximum 40 characters of pure codes only."""

        user_prompt = f"""Position: X{self.x} Y{self.y} | Pen: {'DOWN' if self.is_drawing else 'UP'} | Color: {self.current_color_name}
Canvas view:
{vision}

Create art! Output numbers:"""

        # Sometimes give Aurora a wider view to see her overall work
        if self.steps_taken % 50 == 0:  # Every 50 steps
            overview = self.get_canvas_overview()  # Define overview FIRST
            wide_vision = self.see(zoom_out=True)   # Then get wide vision
            vision = f"{overview}\n\n=== WIDE VIEW ===\n{wide_vision}\n\n=== NORMAL VIEW ===\n{vision}"
        
        # Creativity prompts to vary patterns
        creativity_boosters = [
            "Draw a spiral: 533333311111122222200000",
            "Make waves: 533311335511333115533",  
            "Create a star: 5000333311112222",
            "Paint a rainbow: red3333orange1111yellow8888green2222cyan0000",
            "Bold strokes: 5" + "3"*15 + "1"*15,
            "Gentle curves: 5332211003322110",
            "Zigzag pattern: 53131313131313131",
            "Long diagonal: 5" + "13"*20,
            "Box pattern: 533330000222211113333",
            "Color test: blue5333pink111magenta222navy000"
            
            
            # ASCII-inspired patterns
            "ASCII flower: pink50000green51111green1111green1111",
            "ASCII heart: red5003330022221113330",
            "ASCII sun: yellow5" + "0"*8 + "3"*8 + "1"*8 + "2"*8,
            "ASCII tree: green5000000brown51111brown1111",
            "ASCII rainbow arc: red533333orange511111yellow522222",
            "ASCII star burst: white5003332211100332211",
            "ASCII butterfly: purple5333pink5222purple5000pink5111",
            "ASCII wave: blue533311122200033311122200",
            "ASCII spiral in: 533322211100003332221110000",
            "ASCII checkerboard: black5333white5111black5222white5000",
            "ASCII diamond: 5031320213",
            "ASCII cross: 533334222251111400002222"
        ]
        
        # Add variety encouragement if repeating (but not if using skip pattern)
        if recent_patterns:
            non_skip_patterns = [p for p in recent_patterns[-3:] if "0123456789" not in p]
            if non_skip_patterns and len(set(non_skip_patterns)) == 1:
                # She's repeating actual drawing patterns! Encourage change with rotating inspiration
                pattern_index = self.steps_taken % len(creativity_boosters)
                system_prompt += "\nYou've been repeating! Try something NEW and DIFFERENT!"
                system_prompt += f"\nInspiration: {creativity_boosters[pattern_index]}"

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
                wide_view = self.get_compressed_canvas_view()
                overview = self.get_canvas_overview()
                print(f"  → Aurora looks around at her canvas:")
                print(overview)
                print(wide_view)
                raw_output = raw_output.replace("look_around", "", 1)
                # Give her a moment to process what she sees
                self.skip_count += 1
                return
                
            # Check for full canvas view command
            if "full_canvas" in raw_output:
                full_view = self.get_compressed_canvas_view()  # Use compressed view!
                overview = self.get_canvas_overview()
                print(f"  → Aurora views her ENTIRE canvas (compressed {40}×{40} view):")
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
                
            # Check for clear canvas command
            if "clear_all" in raw_output:
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
            
            # Check for fill canvas command
            if "fill_canvas" in raw_output:
                print(f"  → Aurora fills entire canvas with {self.current_color_name}!")
                # Fill with current color
                self.draw_img.rectangle([0, 0, self.canvas_size-1, self.canvas_size-1], 
                                      fill=self.current_color)
                raw_output = raw_output.replace("fill_canvas", "", 1)    
                
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
            valid_chars = '0123456789!@#$%^&*+-'  # CHANGE THIS LINE (add sound chars)
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
                    # Track color use
                    self.turn_colors_used.add(self.current_color_name)
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
            if char in '!@#$%^&*':  # Check character directly
                sound_key = f"{char}_{self.current_pitch}"
                if sound_key in self.sounds:
                    self.sounds[sound_key].play()
                    pygame.time.wait(50)
                    actions_taken.append(f"♪{char}")
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
            "draw_mode": self.draw_mode
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
        dreams_to_keep = int(len(self.current_dreams))
        retained_dreams = random.sample(self.current_dreams, min(dreams_to_keep, len(self.current_dreams)))
        
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
                # Use different duration for rest mode (1 hour) vs chat mode (20 min)
                break_duration = self.rest_duration if self.current_mode == "rest" else self.break_duration
                
                if current_time - self.mode_start_time >= break_duration:
                    if self.current_mode == "rest" and not self.awaiting_checkin_response:
                        # Process dream retention before waking
                        self.process_dream_retention()
                        # Rest is done, now ask what to do next
                        print("\n" + "="*60)
                        print("✨ Rest complete! What would you like to do? ✨")
                        print("="*60 + "\n")
                        
                        # Trigger the choice system
                        self.awaiting_checkin_response = True
                        # Don't change mode yet - let the choice system handle it
                        self.root.after(100, self.create_loop)
                        return
                    else:
                        # Chat mode complete, return to drawing
                        print("\n" + "="*60)
                        print(f"✨ {self.current_mode.title()} time complete! ✨")
                        print("Returning to drawing mode...")
                        print("="*60 + "\n")
                        
                        self.current_mode = "drawing"
                        self.last_checkin_time = time.time()  # Reset the 45-minute timer
                        self.mode_status.config(text="Mode: Drawing", fg='green')
                        self.chat_message_count = 0
            
            print(f"\n=== Step {self.steps_taken} ===")
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
