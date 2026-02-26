"""
Aurora LLM Adapter
==================
Drop-in adapter for swapping different LLMs into Aurora's canvas environment.
Supports text-only models AND multimodal models (LLaVA).

Usage (text-only):
    adapter = AuroraLLMAdapter(model_preset="llama2")
    response = adapter(prompt, max_tokens=100)

Usage (multimodal - one brain that sees):
    adapter = AuroraLLMAdapter(model_preset="llava")
    response = adapter.see_and_respond(pil_image, "What do you want to create?")
"""

from llama_cpp import Llama
from pathlib import Path
import json
import base64
from io import BytesIO

# Try to import multimodal support
try:
    from llama_cpp.llama_chat_format import Llava15ChatHandler
    LLAVA_SUPPORT = True
except ImportError:
    LLAVA_SUPPORT = False
    print("Note: LLaVA support not available in this llama-cpp-python version")


# =============================================================================
# PROMPT FORMATS
# =============================================================================

PROMPT_FORMATS = {
    "llama3": {
        "template": """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

""",
        "stop_tokens": ["<|eot_id|>", "<|end_of_text|>"]
    },
    
    "llama2": {
        "template": """<s>[INST] <<SYS>>
{system}
<</SYS>>

{user} [/INST]""",
        "stop_tokens": ["</s>", "[INST]"]
    },
    
    "mistral": {
        "template": """<s>[INST] {system}

{user} [/INST]""",
        "stop_tokens": ["</s>", "[INST]"]
    },
    
    "chatml": {
        "template": """<|im_start|>system
{system}<|im_end|>
<|im_start|>user
{user}<|im_end|>
<|im_start|>assistant
""",
        "stop_tokens": ["<|im_end|>", "<|im_start|>"]
    },
    
    "gemma": {
        "template": """<start_of_turn>user
{system}

{user}<end_of_turn>
<start_of_turn>model
""",
        "stop_tokens": ["<end_of_turn>", "<start_of_turn>"]
    },
    
    "phi3": {
        "template": """<|system|>
{system}<|end|>
<|user|>
{user}<|end|>
<|assistant|>
""",
        "stop_tokens": ["<|end|>", "<|user|>", "<|assistant|>"]
    },
    
    "deepseek": {
        "template": """<|begin▁of▁sentence|><|User|>{system}

{user}<|Assistant|>""",
        "stop_tokens": ["<|end▁of▁sentence|>", "<|User|>"]
    },
    
    "raw": {
        "template": """{system}

{user}

Response:""",
        "stop_tokens": ["\n\n\n", "Human:", "User:"]
    },
    
    "llava": {
        "template": """<s>[INST] {system}

{user} [/INST]""",
        "stop_tokens": ["</s>", "[INST]"]
    },
}


# =============================================================================
# MODEL PRESETS
# =============================================================================

MODEL_PRESETS = {
    # ===========================================
    # TEXT-ONLY MODELS
    # ===========================================
    "llama3-abliterated": {
        "format": "llama3",
        "filename": "Meta-Llama-3-8B-Instruct-abliterated-v3-Q4_K_M.gguf",
        "description": "Llama 3 8B with guardrails removed - Aurora's original model",
        "multimodal": False
    },
    "llama3": {
        "format": "llama3",
        "filename": "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf",
        "description": "Llama 3 8B - Standard version with guardrails",
        "multimodal": False
    },
    "llama2": {
        "format": "llama2",
        "filename": "llama-2-7b-chat.Q4_K_M.gguf",
        "description": "Llama 2 7B Chat - The OG (July 2023)",
        "multimodal": False
    },
    "llama2-base": {
        "format": "raw",
        "filename": "llama-2-7b-base.Q4_K_M.gguf",
        "description": "Llama 2 7B BASE - No instruction tuning whatsoever",
        "multimodal": False
    },
    "mistral": {
        "format": "mistral",
        "filename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "description": "Mistral 7B v0.2 - Fast, confident, creative",
        "multimodal": False
    },
    "mistral-base": {
        "format": "raw",
        "filename": "mistral-7b-base-f16.gguf",
        "description": "Mistral 7B BASE - No instruction tuning, pure chaos",
        "multimodal": False
    },
    "qwen": {
        "format": "chatml",
        "filename": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "description": "Qwen 2.5 3B - Smaller but fast, different cultural perspective",
        "multimodal": False
    },
    "openhermes": {
        "format": "chatml",
        "filename": "openhermes-2.5-mistral-7b.Q4_K_M.gguf",
        "description": "OpenHermes 2.5 - Fine-tuned Mistral, creative and uncensored",
        "multimodal": False
    },
    # ===========================================
    # MULTIMODAL MODELS (ONE BRAIN THAT SEES)
    # ===========================================
    "llava": {
        "format": "llava",
        "filename": "llava-v1.6-mistral-7b.Q4_K_M.gguf",
        "mmproj": "llava-v1.6-mistral-mmproj-f16.gguf",
        "description": "LLaVA v1.6 Mistral - ONE BRAIN WITH EYES",
        "multimodal": True
    },
    # ===========================================
    # FUTURE DOWNLOADS
    # ===========================================
    "gemma2-9b": {
        "format": "gemma",
        "filename": "gemma-2-9b-it-Q4_K_M.gguf",
        "description": "Gemma 2 9B - Google's model, structured thinking",
        "multimodal": False
    },
    "phi3-medium": {
        "format": "phi3",
        "filename": "Phi-3-medium-128k-instruct-Q4_K_M.gguf",
        "description": "Phi-3 Medium 14B - Microsoft, reasoning-heavy",
        "multimodal": False
    },
    "deepseek-lite": {
        "format": "deepseek",
        "filename": "deepseek-v2-lite-chat.Q4_K_M.gguf",
        "description": "DeepSeek V2 Lite - Chinese lab, wild card",
        "multimodal": False
    },
}


# =============================================================================
# ADAPTER CLASS
# =============================================================================

class AuroraLLMAdapter:
    """
    LLM Adapter for Aurora - handles prompt formatting and model calls.
    Supports both text-only and multimodal (LLaVA) models.
    """
    
    def __init__(
        self,
        model_path: str = None,
        model_preset: str = None,
        model_format: str = None,
        models_dir: str = "./models",
        gpu_layers: int = 10,
        n_ctx: int = 6500,
        n_threads: int = 8,
        verbose: bool = False
    ):
        self.models_dir = Path(models_dir)
        self.verbose = verbose
        self.model_preset = model_preset
        self.is_multimodal = False
        self.chat_handler = None
        
        # Resolve model path and format
        if model_preset and model_preset in MODEL_PRESETS:
            preset = MODEL_PRESETS[model_preset]
            self.model_path = self.models_dir / preset["filename"]
            self.model_format = preset["format"]
            self.is_multimodal = preset.get("multimodal", False)
            
            if verbose:
                print(f"Using preset: {model_preset}")
                print(f"  {preset['description']}")
                if self.is_multimodal:
                    print(f"  MULTIMODAL MODE - This brain has eyes!")
        else:
            self.model_path = Path(model_path) if model_path else None
            self.model_format = model_format or "llama3"
        
        if not self.model_path or not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        # Get format config
        if self.model_format not in PROMPT_FORMATS:
            raise ValueError(f"Unknown format: {self.model_format}. Options: {list(PROMPT_FORMATS.keys())}")
        
        self.format_config = PROMPT_FORMATS[self.model_format]
        
        # Load the model
        if verbose:
            print(f"Loading model: {self.model_path.name}")
            print(f"Format: {self.model_format}")
        
        # Different loading for multimodal vs text-only
        if self.is_multimodal:
            self._load_multimodal(preset, gpu_layers, n_ctx, n_threads)
        else:
            self._load_text_only(gpu_layers, n_ctx, n_threads)
        
        if verbose:
            print(f"Model loaded with {gpu_layers} GPU layers")
    
    def _load_text_only(self, gpu_layers, n_ctx, n_threads):
        """Load a text-only model"""
        self.llm = Llama(
            str(self.model_path),
            n_ctx=n_ctx,
            n_gpu_layers=gpu_layers,
            n_threads=n_threads,
            n_batch=512,
            verbose=False,
            seed=-1,
            f16_kv=True,
            use_mlock=True,
            n_threads_batch=n_threads
        )
    
    def _load_multimodal(self, preset, gpu_layers, n_ctx, n_threads):
        """Load a multimodal model with vision capabilities"""
        if not LLAVA_SUPPORT:
            raise RuntimeError("LLaVA support not available. Update llama-cpp-python.")
        
        # Get mmproj path
        mmproj_path = self.models_dir / preset["mmproj"]
        if not mmproj_path.exists():
            raise FileNotFoundError(
                f"Vision encoder not found: {mmproj_path}\n"
                f"Download it with:\n"
                f"  wget -c 'https://huggingface.co/cjpais/llava-v1.6-mistral-7b-gguf/resolve/main/mmproj-model-f16.gguf' -O {mmproj_path}"
            )
        
        if self.verbose:
            print(f"Loading vision encoder: {mmproj_path.name}")
        
        # Create chat handler for LLaVA
        self.chat_handler = Llava15ChatHandler(clip_model_path=str(mmproj_path))
        
        # Load model with chat handler
        self.llm = Llama(
            str(self.model_path),
            n_ctx=n_ctx,
            n_gpu_layers=gpu_layers,
            n_threads=n_threads,
            n_batch=512,
            verbose=False,
            seed=-1,
            f16_kv=True,
            use_mlock=True,
            n_threads_batch=n_threads,
            chat_handler=self.chat_handler
        )
    
    def format_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """Format system and user prompts for this model's expected format."""
        return self.format_config["template"].format(
            system=system_prompt,
            user=user_prompt
        )
    
    def get_stop_tokens(self) -> list:
        """Get stop tokens for this model format."""
        return self.format_config["stop_tokens"].copy()
    
    def _pil_to_data_uri(self, pil_image) -> str:
        """Convert PIL image to data URI for LLaVA"""
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_base64}"
    
    def see_and_respond(
        self,
        pil_image,
        text_prompt: str,
        system_prompt: str = None,
        max_tokens: int = 100,
        temperature: float = 1.1,
        **kwargs
    ) -> str:
        """
        MULTIMODAL: Send an image and prompt, get response.
        This is ONE BRAIN seeing and deciding.
        
        Args:
            pil_image: PIL Image of the canvas
            text_prompt: What to ask/tell the model
            system_prompt: Optional system context
            max_tokens: Max response length
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        if not self.is_multimodal:
            raise RuntimeError("see_and_respond() requires a multimodal model. Use preset='llava'")
        
        # Convert image to data URI
        image_uri = self._pil_to_data_uri(pil_image)
        
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_uri}},
                {"type": "text", "text": text_prompt}
            ]
        })
        
        # Generate
        response = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=self.get_stop_tokens(),
            **kwargs
        )
        
        return response["choices"][0]["message"]["content"].strip()
    
    def __call__(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 1.1,
        top_p: float = 0.95,
        top_k: int = 80,
        stop: list = None,
        **kwargs
    ) -> dict:
        """
        Generate text - compatible with llama_cpp interface.
        For text-only models or multimodal without image.
        """
        all_stops = self.get_stop_tokens()
        if stop:
            all_stops.extend(stop)
        
        return self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            stop=all_stops,
            **kwargs
        )
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 100,
        temperature: float = 1.1,
        **kwargs
    ) -> str:
        """
        Higher-level generate method - formats prompt and returns just the text.
        """
        prompt = self.format_prompt(system_prompt, user_prompt)
        response = self(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
        return response['choices'][0]['text'].strip()
    
    @property
    def model_name(self) -> str:
        """Get the model filename."""
        return self.model_path.stem if self.model_path else "unknown"
    
    @classmethod
    def list_presets(cls) -> None:
        """Print available model presets."""
        print("\nAvailable Model Presets:")
        print("=" * 60)
        for name, preset in MODEL_PRESETS.items():
            multimodal_tag = " [MULTIMODAL]" if preset.get("multimodal") else ""
            print(f"\n  {name}{multimodal_tag}")
            print(f"    File: {preset['filename']}")
            print(f"    Format: {preset['format']}")
            print(f"    {preset['description']}")
    
    @classmethod
    def list_formats(cls) -> None:
        """Print available prompt formats."""
        print("\nAvailable Prompt Formats:")
        print("=" * 60)
        for name, config in PROMPT_FORMATS.items():
            print(f"\n  {name}")
            print(f"    Stop tokens: {config['stop_tokens']}")


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "presets":
            AuroraLLMAdapter.list_presets()
        
        elif cmd == "formats":
            AuroraLLMAdapter.list_formats()
        
        elif cmd == "test" and len(sys.argv) > 2:
            preset = sys.argv[2]
            print(f"\nTesting preset: {preset}")
            try:
                adapter = AuroraLLMAdapter(model_preset=preset, verbose=True)
                
                if adapter.is_multimodal:
                    print("\nMultimodal model loaded! Test with an image.")
                else:
                    response = adapter.generate(
                        "You are Aurora, a digital artist. Respond briefly.",
                        "How do you feel about creating art?",
                        max_tokens=50,
                        temperature=1.0
                    )
                    print(f"\nResponse: {response}")
            except Exception as e:
                print(f"Error: {e}")
        
        else:
            print("Unknown command. Options: presets, formats, test <preset>")
    
    else:
        print("Aurora LLM Adapter")
        print("==================")
        print("\nCommands:")
        print("  python aurora_adapter.py presets  - List model presets")
        print("  python aurora_adapter.py formats  - List prompt formats")
        print("  python aurora_adapter.py test <preset>  - Test a model")
