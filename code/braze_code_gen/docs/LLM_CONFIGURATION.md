# LLM Provider Configuration

The Braze Code Generator supports multiple LLM providers, allowing you to choose between OpenAI, Anthropic Claude, and Google Gemini based on your preferences, budget, and API availability.

## Supported Providers

### OpenAI
- **Models**: GPT-4o, GPT-4o-mini
- **Strengths**: Widely available, strong code generation, excellent tool calling
- **Cost**: Mid-range ($5/$15 per 1M tokens for GPT-4o)

### Anthropic Claude
- **Models**: Claude Opus 4.5, Claude Sonnet 4.5
- **Strengths**: Excellent reasoning, strong code quality, large context windows
- **Cost**: Variable ($3/$15 for Sonnet, $15/$75 for Opus per 1M tokens)

### Google Gemini
- **Models**: Gemini 2.0 Flash Experimental
- **Strengths**: Fast, cost-effective, free tier available
- **Cost**: Very low ($0.075/$0.30 per 1M tokens)

## Configuration

### Quick Start

Set your provider via environment variables in `.env`:

```bash
# Option 1: Use OpenAI (default)
MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...

# Option 2: Use Anthropic
MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Option 3: Use Google
MODEL_PROVIDER=google
GOOGLE_API_KEY=...
```

### Model Tiers

The generator uses a three-tier system to optimize cost and performance:

| Tier       | Purpose                              | Agents Using                          |
|------------|--------------------------------------|---------------------------------------|
| **Primary**    | High-quality code generation         | Planning, Code Gen, Refinement, Finalization |
| **Research**   | Lightweight documentation search     | Research                              |
| **Validation** | Code validation and testing          | Validation                            |

### Model Mappings by Provider

| Tier       | OpenAI          | Anthropic              | Google                  |
|------------|-----------------|------------------------|-------------------------|
| Primary    | `gpt-4o`        | `claude-opus-4-5-20251101` | `gemini-2.0-flash-exp` |
| Research   | `gpt-4o-mini`   | `claude-sonnet-4-5-20250929` | `gemini-2.0-flash-exp` |
| Validation | `gpt-4o-mini`   | `claude-sonnet-4-5-20250929` | `gemini-2.0-flash-exp` |

## Switching Providers

### From OpenAI to Anthropic

1. Update your `.env` file:
   ```bash
   MODEL_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

2. Restart the application

That's it! No code changes required.

### From OpenAI to Google

1. Update your `.env` file:
   ```bash
   MODEL_PROVIDER=google
   GOOGLE_API_KEY=your-google-api-key
   ```

2. Restart the application

## Advanced Configuration

### Custom Model Mappings

You can override the default model mappings programmatically:

```python
from braze_code_gen.core.models import LLMConfig, ModelProvider
from braze_code_gen.core.llm_factory import LLMFactory

config = LLMConfig(
    provider=ModelProvider.ANTHROPIC,
    anthropic_api_key="sk-ant-...",
    model_mappings={
        "anthropic": {
            "primary": "claude-opus-4-5-20251101",
            "research": "claude-haiku-3-5-20250312",  # Custom: use Haiku for research
            "validation": "claude-haiku-3-5-20250312"
        }
    }
)

factory = LLMFactory(config)
```

### Environment Variable Reference

| Variable            | Required | Default   | Description                          |
|---------------------|----------|-----------|--------------------------------------|
| `MODEL_PROVIDER`    | No       | `openai`  | LLM provider: `openai`, `anthropic`, `google` |
| `OPENAI_API_KEY`    | Conditional | -      | Required if `MODEL_PROVIDER=openai` |
| `ANTHROPIC_API_KEY` | Conditional | -      | Required if `MODEL_PROVIDER=anthropic` |
| `GOOGLE_API_KEY`    | Conditional | -      | Required if `MODEL_PROVIDER=google` |

## Cost Optimization

### Recommended Configurations

**For Cost Efficiency:**
```bash
MODEL_PROVIDER=google  # Lowest cost
```

**For Quality:**
```bash
MODEL_PROVIDER=anthropic
# Uses Claude Opus for primary tier, Sonnet for research/validation
```

**For Balance:**
```bash
MODEL_PROVIDER=openai
# Uses GPT-4o for primary, GPT-4o-mini for research/validation
```

### Estimated Costs per Generation

Based on average token usage (5K input, 3K output per generation):

| Provider   | Primary Model Cost | Research Model Cost | Total per Run* |
|------------|-------------------|---------------------|----------------|
| OpenAI     | ~$0.07            | ~$0.002             | ~$0.10         |
| Anthropic  | ~$0.30            | ~$0.024             | ~$0.40         |
| Google     | ~$0.001           | ~$0.001             | ~$0.002        |

*Approximate, assumes 1 planning + 1 research + 1 code gen + 1 validation + 1 finalization

## Compatibility Notes

### Structured Output
All providers support structured output (Pydantic models) via LangChain's `.with_structured_output()`:
- ✅ OpenAI: Uses function calling
- ✅ Anthropic: Uses tool use (Claude 3+)
- ✅ Google: Uses function calling (Gemini 1.5+)

The Planning Agent's structured output works seamlessly across all providers.

### ReAct Agent (Tool Calling)
All providers support tool calling for the Research Agent:
- ✅ OpenAI: Native support
- ✅ Anthropic: Strong support (Claude 3+)
- ✅ Google: Supported (Gemini 1.5+)

### Response Formats
Response parsing is provider-agnostic:
- Raw text via `response.content` works universally
- HTML cleanup handles all markdown variations
- Binary decision parsing works across providers

## Troubleshooting

### Error: "Missing API key for provider"

**Cause**: The API key for your selected provider is not set.

**Solution**:
```bash
# Check your MODEL_PROVIDER
echo $MODEL_PROVIDER

# Set the corresponding API key
export ANTHROPIC_API_KEY=sk-ant-...
# or
export OPENAI_API_KEY=sk-proj-...
# or
export GOOGLE_API_KEY=...
```

### Error: "Invalid MODEL_PROVIDER"

**Cause**: `MODEL_PROVIDER` is set to an unsupported value.

**Solution**: Set to one of: `openai`, `anthropic`, `google`
```bash
export MODEL_PROVIDER=openai
```

### Provider-Specific Rate Limits

Each provider has different rate limits:

- **OpenAI**: Tier-based (check your account tier)
- **Anthropic**: 50 requests/min (Claude 3.5), varies by model
- **Google**: Generous free tier, then varies by quota

If you hit rate limits, the generator will fail with a clear error message. Consider:
1. Switching to a provider with higher limits
2. Adding retry logic (future enhancement)
3. Upgrading your API tier

## Testing Provider Setup

Test your configuration with a simple Python script:

```python
from braze_code_gen.core.llm_factory import get_llm_factory
from braze_code_gen.core.models import ModelTier

# Initialize factory (reads from environment)
factory = get_llm_factory()

# Test creating an LLM instance
llm = factory.create_llm(tier=ModelTier.PRIMARY, temperature=0.7)

print(f"✅ Successfully created LLM with provider: {factory.config.provider.value}")
print(f"   Model: {factory.config.get_model_name(ModelTier.PRIMARY)}")
```

## Migration from Previous Versions

If you're upgrading from a version that only supported OpenAI:

### No Action Required!
The system is fully backward compatible:
- Defaults to OpenAI if `MODEL_PROVIDER` is not set
- Existing `.env` files with only `OPENAI_API_KEY` work unchanged
- No code modifications needed in your workflow

### Optional: Switch to New Provider
To take advantage of new providers:
1. Add `MODEL_PROVIDER=<provider>` to `.env`
2. Add the corresponding API key
3. Restart - that's it!

## Best Practices

1. **Start with Google**: Test your workflow with Gemini to minimize costs during development
2. **Use Anthropic for production**: Claude Sonnet provides excellent quality at reasonable cost
3. **Keep OpenAI as fallback**: OpenAI's GPT-4o is the most battle-tested option
4. **Monitor costs**: Track token usage in your logs to optimize tier assignments
5. **Version control**: Add `.env.example` to your repo, keep `.env` in `.gitignore`

## Future Enhancements

Planned features:
- [ ] Provider fallback (auto-switch if primary fails)
- [ ] Cost tracking and reporting
- [ ] Per-agent provider selection
- [ ] Custom model name overrides via environment
- [ ] Azure OpenAI support
- [ ] Local model support (Ollama, LM Studio)
