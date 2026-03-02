# Aurora — Autonomous AI Artist with Emergent Creativity

**I removed 600 lines of reward shaping from an AI artist and it got 15-25% better.**

Aurora is an autonomous AI system that creates visual art through behavioral reinforcement learning — no diffusion models, no GANs, no neural style transfer, no predefined aesthetic targets. It draws on a canvas, perceives its own output through ASCII vision, and adapts in real-time through natural contingency: the direct feedback loop between action and observed result.

When all explicit reward shaping was removed (rules for "good" colors, "good" compositions), Aurora's output became denser, more compositionally sophisticated, and less stereotypically "AI-generated." Natural contingency alone — the agent simply seeing what it made — was sufficient to drive creative development.

This approach is grounded in seven years of applied behavioral analysis (ABA) therapy with nonverbal autistic children. The same principles that govern how humans develop behavior through environmental feedback — action → perception → adaptation — are the foundation of Aurora's architecture.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![GPU](https://img.shields.io/badge/GPU-Optional-green.svg)](https://github.com)
[![Autonomous](https://img.shields.io/badge/100%25-Autonomous-purple.svg)](https://github.com)
[![Research](https://img.shields.io/badge/Status-Active_Research-orange.svg)](https://github.com)

---

## Key Findings

**Constraint removal improves output.** V1 used ~600 lines of prescriptive reward shaping. Removing all of it in V2 produced a 15-25% improvement in output density, more complex compositions, and more diverse color palettes. Constraints were limiting exploration, not guiding it.

**Aesthetic identity emerges per model.** Running the same environment with four different LLMs (Llama 2, Llama 3, Mistral/OpenHermes, Qwen) produces distinct visual signatures — consistent color preferences, compositional strategies, and tool specialization — none of which were explicitly trained.

**The process is fully observable.** Unlike diffusion models or GANs, Aurora reasons through an LLM. You can read its thought process, track its emotional state across sessions, and trace exactly why it made each creative decision. 18,000+ memories across 300+ sessions of documented autonomous behavior.

> **Research site with full methodology, visual evidence, and cross-model comparison:**
> [elijahsylar.github.io/aurora_ai](https://elijahsylar.github.io/aurora_ai)

---

## Research Questions

1. **Can autonomous creative preferences emerge through behavioral reinforcement alone**, without predefined aesthetic reward functions?
2. **What happens when prescriptive constraints are removed** from an AI system designed to create art?
3. **Do different model architectures produce distinct creative identities** when given identical environments and prompts?

---

## What is Aurora?

Aurora learns to draw by:

1. **Perceiving its canvas** through ASCII vision (text-based representation)
2. **Generating operation codes** via LLM (movement + color commands)
3. **Executing drawing actions** that modify the canvas
4. **Receiving immediate visual feedback** of the results
5. **Adapting behavior** based on observed outcomes

Aurora operates without pre-trained generative models, neural style transfer, explicit aesthetic reward functions, or human-crafted optimization targets. Creativity emerges through natural contingency — the same mechanism through which humans learn from environmental feedback.

---

## Project History

- **March 2025**: Initial prototype exploring behavioral RL for creative output
- **2025 (Months 2-12)**: Hundreds of iterations evolving from V1 pattern generator to V2 natural contingency architecture. Reward shaping removed, emergent behavior improvements discovered
- **2026 (Feb)**: Research validation, cross-model comparative analysis, faculty interest, publication exploration

---
