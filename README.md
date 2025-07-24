# 🎨 AURORA - Autonomous Drawing AI with Operation Codes

> An AI that sees through ASCII vision and paints through operation codes

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![GPU](https://img.shields.io/badge/GPU-Optional-green.svg)](https://github.com)
[![Autonomous](https://img.shields.io/badge/100%25-Autonomous-purple.svg)](https://github.com)

## 🤖 What is AURORA?

AURORA is an autonomous AI artist that creates art by generating and executing operation codes - pure strings of commands like `"red533333orange511111yellow522222"`. No neural style transfer. No diffusion. Just an AI learning to move a brush.

## 🧠 ASCII Vision System

AURORA literally sees its canvas as ASCII art:

```
What AURORA sees:        What AURORA draws:
  ..###..                
  .#####.        →       "larger_brush5yellow3333blue1111"
  ..###..                
```

The AI interprets these text patterns and responds with drawing operations, creating a unique feedback loop between perception and creation.

## ⚡ Core Features

### Operation Code Language
```
Movement: 0=↑ 1=↓ 2=← 3=→
Control:  4=pen_up 5=pen_down
Tools:    brush | large_brush | larger_brush | star | circle | diamond
Colors:   red | blue | yellow | green | cyan | purple | pink | ...
Think:    0123456789 (pause sequence)
```

### Autonomous Behaviors
- **Self-adjusting tools**: Detects when coverage is too small and switches to larger brushes
- **Creative reflection**: Uses thinking pauses between drawing sessions
- **Dynamic pacing**: Adjusts speed with `faster`/`slower` commands
- **No human intervention**: Completely self-directed after initialization

### Real Examples from AURORA
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

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/elijahsylar/Aurora_op_coding.git
cd Aurora_op_coding

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

## 📊 Performance Metrics

From actual sessions:
- **Operations per cycle**: 40-150 (turbo mode)
- **Canvas size**: 841x841 pixels
- **Brush sizes**: 3x3 to 28x28 pixels
- **Decision latency**: ~1.3 FPS
- **Autonomous decisions**: 1710+ recorded
- **Zero human input** after initialization

## 🎨 The Creative Process

1. **ASCII Vision** → AURORA sees current canvas state as text patterns
2. **Contextual Analysis** → Evaluates position, color, recent actions
3. **Code Generation** → Outputs operation string (max 40 chars)
4. **Execution** → Movements and drawing happen in real-time
5. **Feedback Loop** → Sees results, adjusts strategy

## 💾 Memory System

AURORA maintains persistent memory of:
- Previous drawing sessions
- Color usage patterns
- Successful techniques
- Tool preferences

Located in `aurora_canvas_newestversions/` and `aurora_memory/`

## 🛠️ Technical Stack

- **LLM Backend**: Llama-2 7B (GGUF quantized)
- **Canvas Engine**: PIL/Pillow
- **Vision System**: Custom ASCII renderer
- **Op-Code Executor**: Real-time command processor
- **Memory**: JSON-based persistent storage

## 📈 What Makes This Different?

Traditional AI Art:
- Mathematical patterns
- Pre-trained style transfer
- Pixel manipulation

AURORA:
- Learns to control tools
- Sees through ASCII
- Writes movement code
- Makes mistakes and adapts
- Truly autonomous creation

## 🔧 Requirements

- Python 3.8+
- 8GB+ RAM
- GGUF-compatible model
- GPU optional but recommended

## 📄 License

MIT License - Create freely

---

<p align="center">
<b>AURORA doesn't generate art. It learns to draw.</b>
</p>
