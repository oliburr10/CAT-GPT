"""Which AI the cat talks to, and how to reach it.

The agent engine speaks Claude's API. OpenRouter and Ollama both accept that same format, so
switching is just a matter of pointing the engine somewhere else.
"""

import json
import os
import urllib.error
import urllib.request

from . import config

# When no model is chosen, the cat picks a free OpenRouter model that can use tools,
# preferring the ones that are strongest at coding (first match wins).
FREE_PREFERENCE = ["gpt-oss-120b", "deepseek", "kimi-k2", "glm", "qwen3-coder", "llama-3.3-70b", "gpt-oss-20b"]
MAX_TRIES = 8  # how many free models to try before giving up
CHOSEN_MODEL_FILE = config.HOME_DIR / "openrouter_model.txt"  # remembers the pick between runs


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


def try_model(model_id: str) -> str | None:
    """Send a model a one-word message. Returns None if it answers, otherwise why it didn't.

    Some free models only work for particular apps, or are overloaded, even though OpenRouter
    lists them as available, so the only reliable test is to ask.
    """
    request = urllib.request.Request(
        f"{config.OPENROUTER_URL}/v1/messages",
        data=json.dumps({"model": model_id, "max_tokens": 16,
                         "messages": [{"role": "user", "content": "Say hi."}]}).encode(),
        headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}",
                 "anthropic-version": "2023-06-01", "content-type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90):
            return None
    except urllib.error.HTTPError as e:
        try:
            message = json.load(e)["error"]["message"]
        except (ValueError, KeyError, TypeError):
            message = e.reason
        return f"{e.code} {message}"
    except OSError as e:
        return str(e)


def pick_free_model() -> str:
    """Try OpenRouter's free tool-using models, best first, and return the first that answers."""
    try:
        candidates = free_tool_models()
    except OSError as e:
        raise SystemExit(f"Couldn't reach OpenRouter to pick a free model ({e}). Set CAT_MODEL to choose one.")
    for candidate in candidates[:MAX_TRIES]:
        problem = try_model(candidate["id"])
        if problem is None:
            return candidate["id"]
        print(f"  (skipping {candidate['id']}: {problem[:150]})")
    raise SystemExit("None of OpenRouter's free models answered. Wait a while and try again, "
                     "or set CAT_MODEL to choose one.")


def forget_model() -> None:
    """Forget the remembered free model, so the next start picks again."""
    CHOSEN_MODEL_FILE.unlink(missing_ok=True)
    if config.PROVIDER == "openrouter" and not os.environ.get("CAT_MODEL"):
        config.MODEL = ""


def model() -> str:
    """The model the cat uses. With OpenRouter and no CAT_MODEL, a free one that really answers."""
    if not config.MODEL and config.PROVIDER == "openrouter":
        remembered = CHOSEN_MODEL_FILE.read_text().strip() if CHOSEN_MODEL_FILE.exists() else ""
        if remembered:
            config.MODEL = remembered
        else:
            print(f"Finding a free model that works (this takes a few seconds the first time)...")
            config.MODEL = pick_free_model()
            config.HOME_DIR.mkdir(parents=True, exist_ok=True)
            CHOSEN_MODEL_FILE.write_text(config.MODEL)
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
