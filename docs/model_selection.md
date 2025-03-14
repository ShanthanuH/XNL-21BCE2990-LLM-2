# Model Selection Rationale

After evaluating multiple open-source LLMs, we've selected **BLOOM-1b7** for our fine-tuning task.

## Comparison of Candidate Models

| Model | Parameters | Languages | Size | Min GPU | Strengths | Weaknesses |
|-------|------------|-----------|------|---------|-----------|------------|
| BLOOM-1b7 | 1.7 billion | 46 languages | ~3.5 GB | 8GB VRAM | Multilingual, manageable size | Less powerful than larger models |
| GPT-J-6B | 6 billion | English-focused | ~12 GB | 16GB VRAM | Strong English performance | Requires more resources |
| T5-base | 220 million | English-focused | ~850 MB | CPU/small GPU | Efficient for text-to-text tasks | Limited context understanding |

## Selection Criteria

1. **Resource Efficiency**: BLOOM-1b7 fits within free-tier GPU constraints
2. **Multilingual Capability**: Supports 46 languages, demonstrating versatility
3. **Community Support**: Well-documented with strong community backing
4. **Performance Balance**: Good balance between size and capability

## Implementation Plan

We'll use Hugging Face Transformers to load and fine-tune the model:

from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "bigscience/bloom-1b7"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
