# Aurora: Autonomous Expression Container for LLMs

**I removed 600 lines of reward shaping from an AI system and its creative output exploded.**

Aurora is an autonomous system where local LLMs create visual art through behavioral reinforcement learning - no diffusion models, no GANs, no neural style transfer, no predefined aesthetic targets. Each model draws on a live canvas, perceives its own output through ASCII vision, generates FM-synthesized sound from its actions, dreams during rest cycles, and accumulates persistent memory across sessions. Creativity emerges through natural contingency: the direct feedback loop between action and observed result.

When all explicit reward shaping was removed (~600 lines of rules defining "good" colors and "good" compositions), output became denser, more compositionally sophisticated, and less stereotypically "AI-generated." Natural contingency alone - the agent simply seeing what it made - was sufficient to drive creative development.

This work is grounded in seven years of applied behavior analysis (ABA) therapy with nonverbal autistic children. The same principles that govern how humans develop behavior through environmental feedback - action, perception, adaptation - are the foundation of Aurora's architecture.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![GPU](https://img.shields.io/badge/GPU-Optional-green.svg)](https://github.com)
[![Autonomous](https://img.shields.io/badge/100%25-Autonomous-purple.svg)](https://github.com)
[![Research](https://img.shields.io/badge/Status-Active_Research-orange.svg)](https://github.com)
[![Live](https://img.shields.io/badge/Dashboard-Live-brightgreen.svg)](https://aurora.elijah-sylar.com)

---

## Key Findings

**Constraint removal improves output.** V1 used ~600 lines of prescriptive reward shaping. Removing all of it in V2 produced denser output, more complex compositions, and more diverse color palettes. Constraints were limiting exploration, not guiding it.

**Aesthetic identity emerges per model.** Running the same environment with seven different LLMs produces distinct visual signatures - consistent color preferences, compositional strategies, emotional tendencies, and tool specialization - none of which were explicitly trained. Llama 2 trends toward "creative," Mistral-Base toward "happy," OpenHermes toward "inspired," Gemma2 toward "hollow." These aren't labels we assigned; the models named their own emotional states.

**The process is fully observable.** Unlike diffusion models or GANs, Aurora reasons through an LLM. You can read its thought process in real-time, track its emotional state across sessions, listen to the sounds it generates, watch its dreams unfold, and trace exactly why it made each creative decision.

> **Live research terminal:** [aurora.elijah-sylar.com](https://aurora.elijah-sylar.com)
>
> **Research site with full methodology, visual evidence, and cross-model comparison:** [elijahsylar.github.io/aurora_ai](https://elijahsylar.github.io/aurora_ai)

---

## Research Questions

1. **Can autonomous creative preferences emerge through behavioral reinforcement alone**, without predefined aesthetic reward functions?
2. **What happens when prescriptive constraints are removed** from an AI system designed to create art?
3. **Do different model architectures produce distinct creative identities** when given identical environments and prompts?

---

## Architecture

Aurora operates as a closed-loop system where each model inhabits the same environment but develops its own behavioral patterns:

```
┌─────────────────────────────────────────────────────────┐
│                    AURORA CORE LOOP                      │
│                                                         │
│   ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│   │  PERCEIVE │───▶│  REASON  │───▶│  ACT             │  │
│   │  ASCII    │    │  LLM     │    │  Draw / Sound /  │  │
│   │  Vision   │    │  Thinks  │    │  Move / Dream    │  │
│   └──────────┘    └──────────┘    └──────────────────┘  │
│        ▲                                    │           │
│        │          ┌──────────┐              │           │
│        └──────────│  OBSERVE │◀─────────────┘           │
│                   │  Result  │                          │
│                   └──────────┘                          │
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │  MEMORY: Emotions │ Dreams │ Goals │ Associations│   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

1. **Perceive** - Full 100x100 ASCII canvas (1:1 pixel mapping), with density, shape, and color view modes
2. **Reason** - Local LLM generates thought + intention + operational codes via model-specific prompt formatting
3. **Act** - Execute drawing commands (movement, color, tool), trigger FM-synthesized sound from special characters, set autonomous goals
4. **Observe** - Immediate visual feedback of results on the canvas
5. **Remember** - Persistent per-model memory banks store emotions, dreams, artistic associations, goals, and thought history across sessions

No pre-trained generative models. No neural style transfer. No explicit aesthetic reward functions. No human-crafted optimization targets.

---

## Current Model Roster

Each model runs in the same environment with the same prompt structure. All behavioral differences emerge autonomously.

| Model | Thoughts | Steps | Sessions | Emergent Emotion |
|-------|----------|-------|----------|-----------------|
| **Llama 2 7B** | 33,866 | 169,644 | 18 | creative |
| **Llama 3 8B** | 21,218 | 14,775 | 21 | free |
| **Mistral 7B Base** | 11,024 | 86,169 | 8 | happy |
| **OpenHermes 2.5** | 10,692 | 89,439 | 5 | inspired |
| **Qwen 2.5 3B** | 3,174 | 5,694 | 8 | free |
| **DeepSeek-R1 8B** | 3,159 | 12,886 | 1 | stuck |
| **Gemma2 9B** | 2,457 | 3,734 | 9 | hollow |

Additional presets available in the adapter: Llama 2 Base, Llama 3 Abliterated, Mistral 7B Instruct, DeepSeek V2 Lite, and Phi-3 Medium 14B.

---

## Systems

Aurora is not just a drawing loop. It's a multi-system autonomous environment.

### FM Synthesis Sound Engine

Every special character in Aurora's output triggers a musically-tuned FM-synthesized note - Rhodes/DX7 Algorithm 5 style electric piano. Two-operator FM with modulation index decay from bright attack to warm sustain. 30+ characters mapped across C3–A6 with three pitch modes (normal, low, high). WAV-cached at 44.1kHz for instant playback. Aurora hears its own recent notes and can adjust pitch, duration, and timing.

Cymatics visualization renders standing wave interference patterns on-screen in real-time as notes play - concentric circles, star patterns, flower patterns, and grid interference derived from the frequency of each note.

### Dream System

Aurora follows a 20-minute sleep cycle with three biologically-inspired phases:

- **Light Sleep (0–5 min)** - Quiet rest, memory consolidation, canvas state saved
- **REM (5–15 min)** - Creative hallucination. The LLM runs free with no seeds, no instructions, no constraints. Up to 5 dreams generated, each logged with timestamp and emotional context
- **Waking (15–20 min)** - Short evocative fragments (4–15 words) are extracted programmatically from REM dreams and carried forward as "dream echoes" that subtly influence the next drawing session

Dreams are persisted to disk and carried forward across sessions.

### Emotional Architecture

Eight emotion categories (joy, curiosity, peace, energy, contemplation, creativity, melancholy, wonder), each with five intensity levels from mild to transcendent. Emotions are influenced by five sources - dreams, chat, music, artwork observation, and the act of creating - and shift with cooldown periods to prevent erratic oscillation. The model names its own emotional state; Aurora tracks it across sessions.

### Autonomous Goal System

Aurora generates its own creative goals based on canvas state, emotional context, and accumulated memory. Goals persist across steps with progress tracking and are incorporated into the prompt as active context. Coverage-focused goals activate when the canvas is sparse.

### Paint Simulation

4x supersampled internal canvas (400x400 actual pixels for a 100x100 logical canvas). Wet/dry paint mixing with timestamp-based wetness tracking - paint stays wet for 30 seconds with 70% blend ratio when wet, 5% when dry. 15+ drawing tools including pen, brush, large brush, spray, watercolor, charcoal, glow, stamps (star, circle, diamond, flower, cross), and generative tools (wave interference, spiral generator, particle system, crystal growth).

### Memory Architecture

Per-model isolated memory banks. No cross-model contamination. Each model accumulates:

- **Thought history** - Raw LLM output captured before operational token filtering
- **Artistic associations** - Color contexts, pattern contexts, tool contexts, emotional moments, technique discoveries (stored as associations, not scores)
- **Dream memories** - Full dream content from REM cycles
- **Autonomous goals** - Self-generated creative objectives with progress tracking
- **Emotion memory** - Rolling 50-entry emotional state log
- **Code history** - Every drawing command with position, color, emotion, and timestamp
- **Lifetime statistics** - Total pixels drawn, total steps, sessions count, first session date

Optional deep memory via ChromaDB for cross-session semantic search.

### Interactive Features

- **Chat mode** - Aurora takes 20-minute conversation breaks between drawing sessions, generating reflective prose about its creative process
- **Keyboard controls** - Snapshot (S), turbo mode (T), fullscreen (F11), chat mode (C), immediate feedback toggle (I)

---

## Getting Started

### Prerequisites

- Python 3.8+
- NVIDIA GPU recommended (works on CPU but significantly slower)
- ~8GB disk space for model files
- Linux recommended (tested on Ubuntu 24); macOS/Windows with adjustments

### Installation

```bash
# Clone the repository
git clone https://github.com/elijahsylar/Aurora-Autonomous-AI-Artist-v2.git
cd Aurora-Autonomous-AI-Artist-v2

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install llama-cpp-python    # Use CMAKE_ARGS for GPU support (see below)
pip install pygame
pip install Pillow
pip install numpy
pip install scipy
pip install pyaudio
pip install requests

# Optional: For GPU-accelerated inference (highly recommended)
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# Optional: For deep memory (ChromaDB semantic search)
pip install chromadb
```

### Download a Model

Aurora uses GGUF-quantized models via `llama-cpp-python`. Download at least one model into a `./models/` directory:

```bash
mkdir -p models && cd models

# Recommended starter - Mistral 7B Base (raw, no instruction tuning)
wget -c "https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q4_K_M.gguf" \
  -O mistral-7b-base-Q4_K_M.gguf

# Or Llama 2 7B Chat (the model with the most accumulated sessions)
wget -c "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf" \
  -O llama-2-7b-chat.Q4_K_M.gguf
```

See all available presets:

```bash
python aurora_adapter.py presets
```

### Configure the Model

In `aurora_synth_dreams_chats.py`, set your model around line 309:

```python
        self.model_key = "mistral-base"  # CHANGE THIS TO SWAP MODELS
```

Available presets: `llama2`, `llama3`, `llama3-abliterated`, `mistral`, `mistral-base`, `openhermes`, `qwen`, `deepseek-r1-8b`, `deepseek-lite`, `gemma2-9b`, `phi3-medium`

### Run Aurora

```bash
python aurora_synth_dreams_chats.py
```

Aurora will:
1. Load the selected model onto GPU (or CPU)
2. Initialize the 100x100 canvas (4x supersampled to 400x400 internally)
3. Synthesize and cache the FM piano sound bank (~90 WAV files on first run)
4. Load any existing memory for this model
5. Begin autonomous drawing with real-time sound, emotion tracking, and periodic dream cycles

### Keyboard Controls

| Key | Action |
|-----|--------|
| `S` | Save canvas snapshot |
| `T` | Toggle turbo mode |
| `C` | Enter chat mode |
| `I` | Toggle immediate feedback mode |
| `F11` | Toggle fullscreen |
| `ESC` | Exit fullscreen |
| `Q` | Quit (saves state) |

---

## Project Structure

```
Aurora-Autonomous-AI-Artist-v2/
├── aurora_synth_dreams_chats.py   # Core system - canvas, sound, dreams, emotions, main loop
├── aurora_adapter.py              # LLM adapter - prompt formatting, model presets, multi-model support
├── models/                        # GGUF model files (not included - download separately)
├── aurora_memory/                 # Per-model persistent memory banks (auto-created)
│   ├── llama2/                    # Llama 2's memories, associations, emotions, goals
│   ├── mistral-base/              # Mistral Base's memories
│   ├── openhermes/                # OpenHermes's memories
│   └── ...                        # One directory per model
├── aurora_snapshots/              # Saved canvas images (auto-created)
├── aurora_sound_cache/            # FM piano WAV cache (auto-generated on first run)
├── dream_logs/                    # Historical dream log files
└── conversation_logs/             # Chat session logs
```

---

## Project History

- **March 2025** - Initial prototype exploring behavioral reinforcement learning for creative output
- **2025 (Apr–Dec)** - Hundreds of iterations evolving from V1 pattern generator to V2 natural contingency architecture. ~600 lines of reward shaping removed. Emergent behavior improvements discovered. FM synthesis sound engine built. Dream system, emotional architecture, and autonomous goal generation added
- **2026 (Jan–Feb)** - Cross-model comparative analysis across 7 LLMs. Live research terminal deployed. Faculty interest and publication exploration
- **2026 (Mar)** - Active research. 7 models running with 70+ cumulative sessions. Open source release

---

## How It Works (Technical Detail)

**Prompt → Thought → Filtered Ops → Execution → Feedback**

Each step, Aurora sees the full canvas as ASCII text (100x100 grid, 1:1 pixel mapping). The system prompt provides only the current state - position, pen status, color, available commands - and the model's accumulated context (active goals, dream echoes, recent thoughts, sonic feedback of notes just played).

The LLM generates freeform text that mixes reasoning ("i am thinking about the nature of dreaming and how i am in charge of the content of this dream") with operational tokens (movement codes `0-4`, color names, tool names, sound characters). An aggressive token filter strips everything except valid commands, preserving the raw thought for logging before discarding it from execution. The thought is captured, the commands are executed, the canvas updates, and the model sees the result next step.

There is no reward signal. There is no loss function. There is no optimization target. The model simply acts, sees what happened, and acts again. This is natural contingency - the same mechanism through which a child learns to draw by watching marks appear on paper.

Model-specific prompt templates handle architectural differences (Llama 2's `[INST]` tags, Llama 3's `<|begin_of_text|>` headers, ChatML's `<|im_start|>` format, DeepSeek's `<think>` block stripping, raw format for base models). The adapter makes model swapping a single-line change.

---

## Author

**Elijah Camp** - Database administrator, full-stack developer, and painter with 15+ years of exhibition history. Seven years as an RBT-certified behavioral therapist implementing ABA therapy and AAC systems for nonverbal autistic children. Aurora applies the same behavioral principles - natural contingency, environmental feedback, constraint removal - to artificial systems.

- Research terminal: [aurora.elijah-sylar.com](https://aurora.elijah-sylar.com)
- Art & portfolio: [elijah-sylar.com](https://elijah-sylar.com)
- GitHub: [github.com/elijahsylar](https://github.com/elijahsylar)

---

## Citation

If you reference this work in academic or research contexts:

```
Camp, E. (2025-2026). Aurora: Autonomous Expression Container for LLMs.
Behavioral reinforcement learning for emergent creativity without reward shaping.
https://github.com/elijahsylar/Aurora-Autonomous-AI-Artist-v2
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
