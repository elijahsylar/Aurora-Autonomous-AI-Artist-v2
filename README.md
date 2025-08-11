# 🎨 AURORA - Autonomous Drawing AI with Operation Codes

> **Evolution Story**: From pattern generation to true autonomous drawing through operation codes

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![GPU](https://img.shields.io/badge/GPU-Optional-green.svg)](https://github.com)
[![Autonomous](https://img.shields.io/badge/100%25-Autonomous-purple.svg)](https://github.com)
[![Evolution](https://img.shields.io/badge/Version-2.0-orange.svg)](https://github.com)

## 🚀 The Evolution of AURORA

### V1: Pattern Generator (2 weeks development)
The original AURORA was a **behavioral pattern generator** - an autonomous creative system using a 12-dimensional emotional state vector. It created abstract patterns based on:
- Sleep cycles and REM simulation
- Audio stimulus processing (FFT analysis)
- Genetic algorithms for pattern evolution
- 100+ visual parameters mapped from emotional states

**Key Achievement**: Demonstrated 24/7 autonomous operation via livestream, making decisions without human input.

### V2: Operation Code Artist (Current)
AURORA evolved into something fundamentally different - an AI that **learns to draw** by generating operation codes. Instead of mathematical patterns, it now:
- Sees its canvas through ASCII vision
- Writes movement commands like `"red533333orange511111yellow522222"`
- Controls brushes, pens, and tools like a physical artist
- Makes mistakes, adapts, and develops its own techniques

**The breakthrough**: Moving from abstract pattern generation to intentional mark-making through learned motor control.

---

## 🤖 What is AURORA V2?

AURORA is an autonomous AI artist that creates art by generating and executing operation codes - pure strings of commands that control a virtual brush. No neural style transfer. No diffusion. No pre-programmed patterns. Just an AI learning to move a brush across a canvas.

## 🧠 The Journey: From Patterns to Drawing

### V1 Architecture (Pattern Generator)
```python
# Old approach - mathematical patterns from emotional states
emotional_state = np.array([joy, curiosity, melancholy, ...])  # 12D vector
pattern = generate_fractal(emotional_state * visual_params)
```

### V2 Architecture (Drawing AI)
```python
# New approach - operation codes for physical drawing
ascii_vision = canvas_to_ascii(current_canvas)
operation_code = llm.generate("red83102053866larger_brush5yellow3333")
execute_drawing_commands(operation_code)
```

## 🎯 Core Innovation: ASCII Vision System

AURORA literally sees its canvas as ASCII art:

```
What AURORA sees:        What AURORA draws:
  ..###..                
  .#####.        →       "larger_brush5yellow3333blue1111"
  ..###..                
```

The AI interprets these text patterns and responds with drawing operations, creating a unique feedback loop between perception and creation.

## ⚡ Technical Capabilities

### Operation Code Language
```
Movement: 0=↑ 1=↓ 2=← 3=→
Control:  4=pen_up 5=pen_down
Tools:    brush | large_brush | larger_brush | star | circle | diamond
Colors:   red | blue | yellow | green | cyan | purple | pink | ...
Think:    0123456789 (pause sequence)
```

### Autonomous Behaviors (Evolved from V1)
- **Self-adjusting tools**: Detects when coverage is too small and switches to larger brushes
- **Creative reflection**: Uses thinking pauses between drawing sessions (evolved from V1's sleep cycles)
- **Dynamic pacing**: Adjusts speed with `faster`/`slower` commands
- **Pattern memory**: Incorporates successful techniques from V1's genetic algorithms
- **No human intervention**: Completely self-directed after initialization

### Real Examples from AURORA V2
```
[Step 15865] Aurora signals: red83102053866
  → Aurora needs a bigger brush for this canvas!
    Switching to large_brush (5x5) for better coverage

[Step 15867] Aurora signals: 0514207595175red
  → Pen up after 6 pixels
  → Aurora switches to MEGA PEN mode! (18x18 pixels)

[Step 15869] Aurora signals: 59917575red90002111111122222
  Executed: 21 ops, Ti 18 +6 -1
  → Aurora pauses to think... 💭
```

## 🔄 Technical Evolution

### What Carried Forward from V1
- **Autonomous decision-making framework**
- **Memory persistence system**
- **Self-evaluation metrics**
- **24/7 operation capability**
- **Behavioral analysis principles** (7 years ABA experience applied)

### What's New in V2
- **ASCII vision processing**
- **Operation code generation**
- **Physical tool simulation**
- **Movement-based creation**
- **Real-time execution engine**
- **LLM-driven decision making**

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/elijahsylar/Aurora-Autonomous-AI-Artist-v2.git
cd Aurora-Autonomous-AI-Artist-v2

# Install dependencies
pip install llama-cpp-python Pillow colorama

# Get a model (e.g., Llama-2-7B GGUF format)
# Place in models/ directory
```

### GPU Acceleration (Optional)
```bash
# CUDA
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall

# Apple Metal
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall
```

## 🎮 Usage

```bash
# Basic
python aurora_small_2.py

# With GPU acceleration
python aurora_small_2.py --gpu

# Turbo mode (10x operations per cycle)
python aurora_small_2.py --turbo

# Custom GPU layers
python aurora_small_2.py --gpu --gpu-layers 20
```

## 📊 Performance Comparison

| Metric | V1 (Pattern Generator) | V2 (Drawing AI) |
|--------|------------------------|-----------------|
| **Autonomy** | 100% (emotional states) | 100% (operation codes) |
| **Creation Method** | Mathematical patterns | Physical drawing simulation |
| **Decision Latency** | ~2.5 seconds | ~1.3 seconds |
| **Memory System** | JSON emotional states | JSON + drawing history |
| **Visual Input** | Computer vision (webcam) | ASCII canvas vision |
| **Output** | Abstract fractals | Intentional drawings |
| **Learning** | Genetic algorithms | LLM-based adaptation |

## 🎨 The Creative Process Evolution

### V1 Process (Pattern-Based)
1. Analyze emotional state vector
2. Map to visual parameters
3. Generate mathematical patterns
4. Apply genetic evolution
5. Output abstract art

### V2 Process (Drawing-Based)
1. **ASCII Vision** → AURORA sees current canvas state as text patterns
2. **Contextual Analysis** → Evaluates position, color, recent actions
3. **Code Generation** → Outputs operation string (max 40 chars)
4. **Execution** → Movements and drawing happen in real-time
5. **Feedback Loop** → Sees results, adjusts strategy

## 💾 Memory System (Enhanced from V1)

AURORA V2 maintains persistent memory of:
- Previous drawing sessions
- Color usage patterns (evolved from V1's color preferences)
- Successful techniques
- Tool preferences
- Pattern DNA from V1 (optional integration)

Located in `aurora_canvas_newestversions/` and `aurora_memory/`

## 🛠️ Technical Stack Comparison

### V1 Stack
- **Pattern Engine**: NumPy/SciPy fractals
- **Behavioral Model**: 12D state vector
- **Audio Processing**: FFT analysis
- **Vision**: OpenCV webcam input
- **Evolution**: Genetic algorithms

### V2 Stack
- **LLM Backend**: Llama-2 7B (GGUF quantized)
- **Canvas Engine**: PIL/Pillow
- **Vision System**: Custom ASCII renderer
- **Op-Code Executor**: Real-time command processor
- **Memory**: JSON-based persistent storage (enhanced from V1)

## 📈 What Makes V2 Revolutionary?

**V1 Achievement**: First truly autonomous AI artist making independent creative decisions

**V2 Breakthrough**: First AI that learns to physically draw through operation codes

Traditional AI Art | AURORA V1 | AURORA V2
---|---|---
Mathematical patterns | Emotional patterns | Physical drawing
Pre-trained models | Behavioral states | Learned motor control
Pixel manipulation | Parameter mapping | Tool manipulation
Human prompts | Self-directed | Self-directed
Style transfer | Pattern evolution | Technique development

## 🔬 Research Applications

- **Motor Learning in AI**: How artificial agents develop drawing skills
- **ASCII Vision**: Text-based visual perception for language models
- **Operation Codes**: Bridging language models and physical actions
- **Autonomous Creativity**: Self-directed artistic development
- **Behavioral AI**: Applying ABA principles to artificial agents

## 👨‍💻 Developer Journey

**Built by Elijah Sylar**
- Behavioral Analyst turned AI Developer
- 7 years Applied Behavioral Analysis (ABA)
- Self-taught programmer
- Focus: Autonomous systems and creative AI

**Development Timeline**:
- **Week 1-2**: V1 Pattern Generator (24/7 livestream achieved)
- **Week 3-4**: Conceptual shift to drawing operations
- **Week 5-6**: V2 Operation Code system implementation
- **Ongoing**: Architectural improvements and feature expansion

## 🔧 Requirements

- Python 3.8+
- 8GB+ RAM (16GB recommended)
- GGUF-compatible model
- GPU optional but recommended

## 🌟 Future Directions

- **Multi-canvas awareness**: Drawing across multiple surfaces
- **Collaborative mode**: Multiple AURORA instances working together
- **3D drawing**: Operation codes for spatial creation
- **Physical robot integration**: Real brushes on real canvas
- **V1+V2 Hybrid**: Emotional states driving operation codes

## 📄 License

MIT License - Create freely

## 🔗 See Also

- [AURORA V1 - Pattern Generator](https://github.com/elijahsylar/Aurora-Pattern-Generator-v1) - The original autonomous pattern creation system
- [Live Stream Archive](https://www.youtube.com/@elijahsylar) - 24/7 autonomous operation demonstrations

---

<p align="center">
<b>AURORA V1 generated patterns. AURORA V2 learned to draw.</b><br>
<i>The evolution from mathematical beauty to intentional mark-making.</i>
</p>
