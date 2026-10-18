"""Which AI the cat talks to, and how to reach it.

The agent engine speaks Claude's API. OpenRouter and Ollama both accept that same format, so
switching is just a matter of pointing the engine somewhere else.
"""

import json
import os
import urllib.request

from . import config

# When no model is chosen, the cat picks a free OpenRouter model that can use tools,
# preferring the ones that are strongest at coding (first match wins).
FREE_PREFERENCE = ["gpt-oss-120b", "deepseek", "kimi-k2", "glm", "qwen3-coder", "llama-3.3-70b", "gpt-oss-20b"]


def free_tool_models() -> list[dict]:
    """OpenRouter's free models that support tool calling, best first. No API key needed."""
    with urllib.request.urlopen(f"{config.OPENROUTER_URL}/v1/models", timeout=20) as response:
        models = json.load(response)["data"]

    def is_free(m: dict) -> bool:
        pricing = m.get("pricing") or {}
        return m["id"].endswith(":free") or (str(pricing.get("prompt")) == "0" and str(pricing.get("completion")) == "0")

    usable = [m for m in models if is_free(m) and "tools" in (m.get("supported_parameters") or [])]

    def rank(m: dict) -> tuple:
        preferred = [i for i, name in enumerate(FREE_PREFERENCE) if name in m["id"]]
        return (preferred[0] if preferred else len(FREE_PREFERENCE), -(m.get("context_length") or 0))

    return sorted(usable, key=rank)


def model() -> str:
    """The model the cat uses, picking a free OpenRouter one the first time if none was chosen."""
    if not config.MODEL and config.PROVIDER == "openrouter":
        try:
            choices = free_tool_models()
        except OSError as e:
            raise SystemExit(f"Couldn't reach OpenRouter to pick a free model ({e}). Set CAT_MODEL to choose one.")
        if not choices:
            raise SystemExit("OpenRouter has no free models with tool calling right now. Set CAT_MODEL to choose one.")
        config.MODEL = choices[0]["id"]
        print(f"{config.CAT_NAME} is using the free model {config.MODEL} (set CAT_MODEL to choose another).")
    return config.MODEL


def env() -> dict[str, str]:
    """Settings that point the agent engine at the chosen provider instead of Claude's API."""
    if config.PROVIDER == "anthropic":
        return {}
    if config.PROVIDER == "openrouter":
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise SystemExit("Set OPENROUTER_API_KEY (from openrouter.ai, under Keys) to use OpenRouter.")
        base_url, token = config.OPENROUTER_URL, key
    else:
        base_url, token = config.OLLAMA_URL, "ollama"  # Ollama wants a token but ignores it
    name = model()
    return {
        # A private settings folder, so the engine never reads (or sends on) your own Claude login.
        "CLAUDE_CONFIG_DIR": str(config.HOME_DIR / "engine"),
        "ANTHROPIC_BASE_URL": base_url,
        "ANTHROPIC_AUTH_TOKEN": token,
        "ANTHROPIC_API_KEY": "",  # never send an Anthropic key anywhere else
        # The engine uses smaller "helper" models for background jobs; make them all the chosen one.
        "ANTHROPIC_DEFAULT_OPUS_MODEL": name,
        "ANTHROPIC_DEFAULT_SONNET_MODEL": name,
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": name,
        "ANTHROPIC_SMALL_FAST_MODEL": name,
        "CLAUDE_CODE_SUBAGENT_MODEL": name,
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    }
