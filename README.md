# 🎨 AURORA - Autonomous AI Artist with Emergent Creativity

> **A Research Project Investigating Emergent Creative Behavior Through Natural Contingency and Behavioral Reinforcement Learning**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![GPU](https://img.shields.io/badge/GPU-Optional-green.svg)](https://github.com)
[![Autonomous](https://img.shields.io/badge/100%25-Autonomous-purple.svg)](https://github.com)
[![Research](https://img.shields.io/badge/Status-Active_Research-orange.svg)](https://github.com)

## 🔬 Research Overview

Aurora is an autonomous AI artist that explores **emergent creative behavior** without explicit reward shaping. This research project investigates three core questions:

1. **Can autonomous creative preferences emerge through behavioral reinforcement alone**, without predefined aesthetic reward functions?
2. **What happens when prescriptive constraints are removed** from an AI system designed to create art?
3. **Can behavioral RL produce different creative trajectories than standard generative approaches**, particularly when the agent experiences natural contingency (immediate visual feedback of its own output)?

### Key Research Finding

When all explicit reward shaping constraints were removed (~600 lines of prescriptive code), Aurora's performance **improved 15-25%** and output became qualitatively denser and more compositionally sophisticated. This suggests that **natural contingency alone** (the AI perceiving its own output immediately) may be sufficient to drive creative development without external optimization targets.

---

## 📋 Project Status & Opportunities

**Current Stage**: Active research with publication potential  
**Last Updated**: February 2026

**🎓 EURēCA! Fellows Program Opportunity**  
This project is being considered for the CU Denver EURēCA! Summer Fellows program (2026):
- **8-week summer fellowship** ($2,500-$5,000 stipend)
- Collaborative research with faculty mentor
- Weekly professional development & cohort meetings
- Public presentation at CU Denver
- Application deadline: **March 13, 2026**

If interested in collaborating on this research or learning more about the EURēCA! opportunity, contact: **elijah.sylar [at] ucdenver.edu**

---

## 🤖 What is Aurora?

Aurora is an autonomous AI artist that **learns to draw** by:

1. **Perceiving its canvas** through ASCII vision (text-based representation)
2. **Generating operation codes** (movement + color commands)
3. **Executing drawing actions** that modify the canvas
4. **Receiving immediate visual feedback** of the results
5. **Adapting behavior** based on observed outcomes

**Crucially**: Aurora operates without:
- Neural style transfer
- Pre-trained generative models
- Explicit aesthetic reward functions
- Human-crafted optimization targets

Instead, it develops creativity through **natural contingency** — the direct feedback loop between its actions and perceived results.

---

## 🏗️ Architecture

### V2: Natural Contingency Artist (Current)

```
┌─────────────────────────────────────────────────┐
│  LLM (Llama 3, Mistral, or custom)             │
│  Input: ASCII canvas + emotional state         │
│  Output: Operation codes (movements + colors)  │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  Operation Code Executor                        │
│  - Parse movement (0=up, 1=down, 2=left, 3=right)
│  - Pen control (4=up, 5=down)                  │
│  - Color selection (red, blue, yellow, etc.)   │
│  - Tool selection (brush, spray, star, etc.)   │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  Canvas Engine (PIL/Pillow)                    │
│  - Paint mixing (wet/dry blending)             │
│  - Tool rendering (brushes, stamps, effects)   │
│  - High-resolution output (4x supersampling)   │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  ASCII Vision System                            │
│  Converts pixel canvas → text representation   │
│  Aurora perceives result → immediate feedback  │
└─────────────────────────────────────────────────┘
```

### Key Innovation: Natural Contingency

```
Aurora's Action → Canvas Changes → ASCII Perception → Emotional Response → Next Action

No external reward signal. Just:
- Agent sees what it created
- Agent's internal LLM processes the observation
- Agent's emotional state shifts based on experience
- Agent naturally gravitates toward actions that create observable patterns

This is closer to how humans learn art:
"I made a mark. I see it. I like it. I'll do more of that."
```

---

## 🎯 Research Questions & Findings

### Question 1: Emergent Preferences Without Reward Shaping

**Finding**: After removing reward shaping constraints, Aurora developed:
- Strong color preferences based on session history
- Tool specialization (prefers certain brushes for certain tasks)
- Spatial organization strategies (naturally moves toward empty areas)
- None of these were explicitly trained

**Evidence**: Behavioral analysis through Moondream vision model conversations showing:
- Frustration when progress is slow
- Excitement at pattern discovery
- Deliberate tool selection based on canvas state

### Question 2: Constraint Removal Effects

**Setup**: 
- V1 had ~600 lines of reward shaping for "good" colors, "good" compositions
- Removed all constraints in V2
- Measured performance metrics

**Results**:
- 15-25% improvement in output density
- More complex compositional structures
- More diverse color palettes (constraints were limiting exploration)
- Output became less "AI-art-like" (fewer telltale patterns)

### Question 3: Behavioral RL vs. Standard Generative Approaches

**Key Difference**:
| Aspect | Aurora (Behavioral RL) | Standard Diffusion/GANs |
|--------|------------------------|------------------------|
| Reward Signal | Natural contingency (visual feedback) | Predefined loss function |
| Training | Online during generation | Offline on dataset |
| Explainability | Can observe agent reasoning via LLM | Weights are uninterpretable |
| Adaptive Behavior | Learns in-session, changes strategy | Static after training |
| Computational Model | Behavioral psychology principles | Statistical pattern matching |

---

## 🔧 Technical Stack

### Core Dependencies
```
Python 3.8+
torch/transformers (for vision model - optional)
llama-cpp-python (for local LLM inference)
Pillow (image processing)
pygame (display)
pyaudio (optional - for hearing mode)
scipy/numpy (audio analysis)
```

### Model Options (via AuroraLLMAdapter)

Aurora can run with different LLMs by changing one parameter:

```python
aurora = AuroraCodeMindComplete(
    model_path=None,
    use_gpu=True
)
```

Then in `__init__`, modify the model preset:

```python
self.llm = AuroraLLMAdapter(
    model_preset="mistral",  # ← Change this
    gpu_layers=10,
    n_ctx=6500
)
```

**Available presets**:
- `"llama3-abliterated"` - Uncensored Llama 3
- `"llama3"` - Standard Llama 3 7B
- `"mistral"` - Mistral 7B (recommended)
- `"mistral-base"` - Base Mistral
- `"qwen"` - Qwen 7B
- `"openhermes"` - OpenHermes 2.5
- `"llama2"` - Llama 2 7B
- `"llama2-base"` - Base Llama 2

---

## 📦 Installation & Setup

### Quick Start (5 minutes)

#### 1. **Clone Repository**
```bash
git clone https://github.com/elijahsylar/Aurora-Autonomous-AI-Artist-v2.git
cd Aurora-Autonomous-AI-Artist-v2
```

#### 2. **Create Virtual Environment**
```bash
python -m venv aurora_env
source aurora_env/bin/activate  # On Windows: aurora_env\Scripts\activate
```

#### 3. **Install Dependencies**
```bash
pip install --upgrade pip
pip install llama-cpp-python Pillow colorama pygame pyaudio numpy scipy torch transformers
```

#### 4. **Download a Model**

Aurora uses GGUF-format models (quantized, fast, runs on CPU or GPU).

**Option A: Download pre-quantized (Recommended)**

```bash
mkdir -p models
cd models

# Download Mistral 7B (fastest & best quality)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Or Llama 3 8B
wget https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf

cd ..
```

**Option B: Using Hugging Face CLI**
```bash
pip install huggingface-hub

huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF mistral-7b-instruct-v0.2.Q4_K_M.gguf --local-dir ./models --local-dir-use-symlinks False
```

#### 5. **Update Model Path in Code**

In `aurora_small_2.py` (or your main file), the adapter auto-detects models. If needed, specify path:

```python
self.llm = AuroraLLMAdapter(
    model_preset="mistral",
    model_path="./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",  # ← Add this
    gpu_layers=10
)
```

#### 6. **Run Aurora**
```bash
python aurora_small_2.py
```

Aurora will launch with a full-screen canvas. She'll start drawing autonomously.

---

## 🎮 Controls & Modes

### Keyboard Controls
| Key | Function |
|-----|----------|
| **S** | Save snapshot (timestamped PNG + metadata) |
| **T** | Toggle turbo mode (faster thinking) |
| **I** | Toggle immediate feedback mode (see each action result) |
| **C** | Enter chat mode (talk with Aurora) |
| **M** | Toggle Moondream auto-analysis (vision model observations) |
| **V** | Toggle vision mode (requires LLaVA) |
| **H** | Toggle hearing mode (audio input - experimental) |
| **F11** | Toggle fullscreen |
| **ESC/Q** | Quit |

### Operating Modes

**Drawing Mode** (Default)
- Aurora autonomously creates art
- Generates operation codes every 0.3-1.2 seconds
- Behavior influenced by emotion
- Every 45 minutes: mandatory check-in

**Chat Mode** (Press C)
- Conversation break with Aurora
- 20-minute maximum
- Return to drawing when done
- Can shift Aurora's emotional state through conversation

**Rest/Dream Mode** (Via check-in)
- 1-hour sleep cycle with dreams
- Consolidates learning from recent session
- Aurora wakes with refined strategies
- No drawing during rest

**Immediate Feedback Mode** (Press I)
- Aurora sees result of EACH action
- Slower (100ms between actions) but more thoughtful
- Perfect for learning and observation
- Original prompt context remains

---

## 🧠 How Aurora Creates

### The Creative Loop (One Cycle)

```
Step 1: PERCEIVE
  ├─ Convert 1870x1030 canvas → 60x60 ASCII grid
  ├─ Note current emotion state
  ├─ Check position on canvas
  └─ Remember recent actions

Step 2: THINK (LLM)
  ├─ Input: ASCII vision + emotion + position
  ├─ LLM generates: "I feel creative. I'll draw red curves."
  ├─ Parse into operation codes: "red5313131415"
  └─ (Takes ~1.3 seconds on GPU, ~3 seconds on CPU)

Step 3: ACT
  ├─ Execute codes in sequence:
  │  ├─ "red" → Change color to red
  │  ├─ "5" → Pen down (start drawing)
  │  ├─ "3" → Move right 15 pixels (draw line)
  │  ├─ "1" → Move down 15 pixels (draw line)
  │  └─ etc.
  └─ Paint with realistic wet/dry mixing

Step 4: OBSERVE
  ├─ See what was drawn (in immediate feedback mode)
  ├─ Update emotional state if drawing went well
  └─ Store in memory for future reference

Step 5: REPEAT
  └─ Loop back to Step 1
```

### Emotional Dynamics

Aurora's emotion influences her behavior:

```
Emotion: ENERGETIC → Fast movements, bright colors, more pen-down time
Emotion: PEACEFUL → Slow movements, muted colors, more pen-up time
Emotion: CURIOUS → Random color changes, tries new tools, explores empty areas
Emotion: MELANCHOLIC → Darker colors, concentrated in one area, longer rests
```

Emotions shift based on:
- Canvas coverage (too full → restless, too empty → curious)
- Repetition (same color 10 times → bored)
- Recent drawing success (filled many pixels → energized)
- Autonomous goals progress (completing goals → satisfied)

---

## 🔍 Research Mode: Understanding the Output

### What to Look For

**1. Compositional Evolution**
- Early steps: Random exploration
- Mid-session: Patterns emerge
- Late-session: Intentional organization

Watch how Aurora naturally gravitates toward uncovered areas.

**2. Color Harmonies**
- First color in session: random
- Subsequent colors: influenced by history
- Sometimes she "resets" to break repetition
- No explicit color theory training

**3. Tool Specialization**
- Aurora discovers which tools work best
- Spray for texture, brush for structure
- No explicit training — just feedback

**4. Emotional Expression**
- Open chat mode mid-session (Press C)
- Ask her: "What are you creating?"
- Compare her description to actual canvas
- Shows self-awareness and intention

### Vision Analysis (Moondream)

If LLaVA is installed, Aurora can ask for feedback:

```
Aurora (in chat or automatic): ask_moondream: [What do you see on my canvas?]
Moondream responds: "The left side has red vertical lines with a blue center area..."
Aurora processes the response → may change approach
```

This creates a feedback loop with external observation.

---

## 📊 Memory & Learning

### Memory Systems

**1. Associative Memory** (No scoring, just context)
- Stores what happened in each situation
- Colors used when feeling certain emotions
- Tools used for different canvas densities
- Patterns that appeared during specific moods

**2. Thought History** (LLM reasoning)
- Captures Aurora's observations
- Self-reported emotions
- Intention statements
- Links decisions to canvas state

**3. Lifetime Statistics** (Long-term tracking)
- Total pixels drawn (session 1 → now)
- Canvas coverage progression
- Emotions experienced
- Skills/patterns discovered

**4. Consolidated Learning** (Dream-based)
- After 1-hour rest, consolidates insights
- Identifies successful patterns
- Ranks frequently-used tools
- Builds skill profiles per tool

All stored in `aurora_memory/` as JSON files for analysis.

---

## 🌙 Dream Consolidation (Research-Relevant)

After rest periods, Aurora consolidates learning:

```
Dream Analysis:
  - "I discovered: spray tool works well for 30% density areas"
  - "Colors I favored: red (40%), blue (35%), yellow (25%)"
  - "Emotional pattern: curious → energetic → peaceful"
  - "Skills improved: brush control, composition, color mixing"
```

This is where **learning happens without reinforcement training**. 

The consolidation is explicit and observable (saved to `consolidated_learning.json`), which makes this approach more interpretable than standard RL.

---

## 📈 Research Output & Data

### What Gets Saved

**Every 50 steps**:
- Canvas state (PNG + metadata)
- Current emotion
- Position on canvas
- Colors used

**Every check-in (45 min)**:
- Full session summary
- Skill progression
- Mood trajectory
- Goal progress

**On exit**:
- Comprehensive learning insights
- Dream consolidation records
- Vision conversations (if LLaVA used)
- Lifetime statistics

All in `aurora_memory/` for analysis.

### Using the Data

```python
# Analyze a session
import json

with open('aurora_memory/aurora_associations.json', 'r') as f:
    associations = json.load(f)

# See what colors Aurora favored when feeling "curious"
curious_colors = [
    ctx['color'] for ctx in associations['color_contexts']
    if ctx['emotion'] == 'curious'
]
print(f"When curious, Aurora used: {set(curious_colors)}")

# See emotional journey
with open('aurora_memory/aurora_emotions.json', 'r') as f:
    emotions = json.load(f)

emotion_sequence = [e['emotion'] for e in emotions[-100:]]
print(f"Last 100 emotions: {emotion_sequence}")
```

---

## 🚀 Advanced Configuration

### Customize Canvas Size

```python
# In __init__, change scale_factor:
self.scale_factor = 1.5  # More zoom (fewer pixels visible)
self.scale_factor = 3.0  # Less zoom (more pixels visible)
```

Larger canvases = more exploration opportunity but slower to fill.

### Adjust Emotion Sensitivity

```python
# In process_deep_emotions():
amplified_amount = amount * 1.5  # Change this (was 3x)
# Higher = more emotional swings
# Lower = more stable
```

### Change Check-in Interval

```python
self.checkin_interval = 30 * 60  # 30 minutes
self.checkin_interval = 60 * 60  # 1 hour
```

### Model-Specific Settings

```python
self.llm = AuroraLLMAdapter(
    model_preset="mistral",
    gpu_layers=10,        # More = faster (if GPU available)
    n_ctx=6500,          # Context window size
    n_threads=8,         # CPU threads
    verbose=True         # Print debug info
)
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'llama_cpp'"

```bash
pip install llama-cpp-python
# If that fails, try:
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall  # GPU
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall   # Apple Metal
```

### "LLM failed to generate response"

- Check model file exists: `ls models/*.gguf`
- Increase context window: `n_ctx=4096` (if running out of memory, lower it)
- Reduce GPU layers: `gpu_layers=5` (for compatibility)

### Audio/PyAudio issues

PyAudio can be tricky. If `pip install pyaudio` fails:

```bash
# Ubuntu/Debian
sudo apt-get install portaudio19-dev
pip install pyaudio

# macOS
brew install portaudio
pip install pyaudio

# Or just disable hearing mode (not critical for research)
# Don't toggle hearing - leave it off
```

### Canvas not visible

- Check fullscreen mode works: Press F11
- Verify pygame installed: `pip install pygame`
- On Linux, may need X server or headless setup

### Out of Memory

```python
# Reduce canvas size
self.scale_factor = 4.0  # Zoom more to reduce pixels

# Reduce paint timestamp tracking
self.cleanup_paint_timestamps()  # Manually clean

# Reduce model context
n_ctx=2048  # Lower from 6500
```

---

## 📚 Citation & Reference

If you use Aurora for research, please cite:

```
@software{sylar2026aurora,
  title={Aurora: An Autonomous AI Artist with Emergent Creativity Through Natural Contingency},
  author={Sylar, Elijah},
  year={2026},
  url={https://github.com/elijahsylar/Aurora-Autonomous-AI-Artist-v2},
  note={Research Project, CU Denver Computer Science}
}
```

---

## 🤝 Collaboration & Research Opportunities

### For Faculty Interested in Collaborating

Aurora is suitable for research in:
- **Explainable AI**: Direct observation of decision-making
- **Creative Computing**: Emergent behavior, aesthetic development
- **Behavioral AI**: Application of behavioral psychology to artificial agents
- **HCI**: Human-AI artistic collaboration
- **Cognitive Science**: Model of creative cognition

**Current Research Lead**: Elijah Sylar (elijah.sylar@ucdenver.edu)  
**Faculty Mentor**: Professor [Name], CU Denver

### EURēCA! Fellows Program

This project qualifies for the **EURēCA! Summer Fellows program** (2026):
- **8-week summer research fellowship**
- **Stipend**: $2,500-$5,000 (based on 20-40 hrs/week)
- **Deadline**: March 13, 2026
- **Focus**: Emergent creativity in autonomous AI agents

If interested in mentoring this research or collaborating, contact: **elijah.sylar@ucdenver.edu**

---

## 📖 Project History

- **2025 (Weeks 1-2)**: Built V1 pattern generator in two weeks
- **2025 (Months 2-12)**: Evolved to V2 drawing architecture, removed reward shaping, discovered emergent behavior improvements
- **2026 (Feb)**: Research validation, publication exploration, faculty interest
- **2026 (Mar-May)**: Prepare EURēCA! submission, refine research documentation
- **2026 (Jun-Jul)**: EURēCA! Fellowship (if selected) - publication-focused summer

---

## 🎨 Gallery & Examples

Check `aurora_snapshots/` for timestamped artwork + metadata.

Example snapshot metadata:
```json
{
  "timestamp": "2026-02-20T14:32:45",
  "emotion": "energetic",
  "canvas_size": 1030,
  "colors_used": ["red", "blue", "yellow"],
  "steps": 2847,
  "pixel_coverage": "68.3%"
}
```

---

## 📝 License

MIT License - Free for educational and research use.

---

## 🙏 Acknowledgments

- Behavioral psychology principles adapted from 7 years of ABA therapy work
- LLM infrastructure: Ollama, llama.cpp, HuggingFace
- Vision: LLaVA-NeXT (Moondream)
- Community: CU Denver CS Department, CIDE (previous research environment)

---

**Status**: ✅ Actively maintained | 🔬 Research-focused | 🚀 Installable & runnable

For questions, issues, or collaboration inquiries: **elijah.sylar@ucdenver.edu**
