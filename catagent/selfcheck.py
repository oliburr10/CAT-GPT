"""Check the cat is set up properly: `python -m catagent.selfcheck`

It checks Python and packages, then starts the agent exactly as the app does and confirms
the model, the login and every tool, and finally (on a Mac) the permissions the cat needs.
The live part is one tiny model call (free with OpenRouter's free models or Ollama).
"""

import asyncio
import importlib.metadata
import json
import os
import shutil
import sys
import urllib.request

from claude_agent_sdk import AssistantMessage, ClaudeSDKClient, ResultMessage, SystemMessage, TextBlock

from . import config, context, providers
from .agent import BUILTIN_TOOLS, build_options

OK, BAD, WARN = "✅", "❌", "⚠️ "
CAT_TOOLS = [
    "what_am_i_working_on", "look_at_screen", "show_tip", "open_in_editor", "copy_to_clipboard", "remember",
    "write_study_notes",
]
failures = 0


def report(ok: bool | None, what: str, detail: str = "") -> None:
    global failures
    mark = OK if ok else (WARN if ok is None else BAD)
    failures += ok is False
    print(f"  {mark} {what}" + (f"  ({detail})" if detail else ""))


def check_install() -> None:
    print("Install")
    report(sys.version_info >= (3, 10), "Python 3.10 or newer", sys.version.split()[0])
    for package in ("claude-agent-sdk", "PySide6"):
        try:
            report(True, package, importlib.metadata.version(package))
        except importlib.metadata.PackageNotFoundError:
            report(False, package, "not installed: pip install -r requirements.txt")
    try:
        # The Notepad shows its notes with it.
        from PySide6 import QtWebEngineWidgets  # noqa: F401
        report(True, "Qt WebEngine, for the Notepad")
    except ImportError as e:
        report(False, "Qt WebEngine, for the Notepad", f"{e}; reinstall with: pip install --force-reinstall PySide6")


def check_provider() -> None:
    print(f"AI provider: {config.PROVIDER}")
    if config.PROVIDER == "anthropic":
        has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
        report(True if has_key else None, "ANTHROPIC_API_KEY", "set" if has_key else "not set; the live check shows whether another login works")
    elif config.PROVIDER == "openrouter":
        report(bool(os.environ.get("OPENROUTER_API_KEY")), "OPENROUTER_API_KEY",
               "set" if os.environ.get("OPENROUTER_API_KEY") else "not set: create one at openrouter.ai under Keys")
        try:
            free = providers.free_tool_models()
        except OSError as e:
            report(False, "Can reach OpenRouter", str(e))
            return
        report(bool(free), "Free models that can use tools", f"{len(free)}, e.g. {', '.join(m['id'] for m in free[:3])}")
        if not os.environ.get("OPENROUTER_API_KEY"):
            return
        providers.forget_model()  # pick afresh, in case the remembered model stopped working
        try:
            chosen = providers.model()
        except SystemExit as e:
            report(False, "Found a free model that answers", str(e))
            return
        problem = providers.try_model(chosen)
        report(problem is None, "Chosen model answers", chosen + (f": {problem}" if problem else ""))
    else:
        try:
            with urllib.request.urlopen(f"{config.OLLAMA_URL}/api/version", timeout=5) as r:
                version = json.load(r)["version"]
            parts = tuple(int(x) for x in version.split(".")[:2] if x.isdigit())
            report(parts >= (0, 14), "Ollama is running (needs 0.14 or newer)", version)
            with urllib.request.urlopen(f"{config.OLLAMA_URL}/api/tags", timeout=5) as r:
                names = {m["name"] for m in json.load(r)["models"]}
            report(config.MODEL in names or f"{config.MODEL}:latest" in names, f"Model {config.MODEL} is downloaded",
                   "" if config.MODEL in names or f"{config.MODEL}:latest" in names else f"run: ollama pull {config.MODEL}")
        except OSError as e:
            report(False, "Ollama is running", f"{e}; open the Ollama app")


async def check_agent() -> None:
    print("Agent (one tiny live call)")

    async def deny(*_):
        from claude_agent_sdk import PermissionResultDeny
        return PermissionResultDeny(message="self-check")

    options = build_options(context.ContextWatcher(), lambda *a: None, lambda *a: None, deny)
    init, reply, result = {}, "", None
    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query("This is an automated self-check. Reply with exactly: meow")
            async for msg in client.receive_response():
                if isinstance(msg, SystemMessage) and msg.subtype == "init":
                    init = msg.data
                elif isinstance(msg, AssistantMessage):
                    reply += "".join(b.text for b in msg.content if isinstance(b, TextBlock))
                elif isinstance(msg, ResultMessage):
                    result = msg
    except Exception as e:
        report(False, "Agent starts and logs in", str(e))
        return

    failed = result is None or result.is_error
    detail = "; ".join(result.errors or []) if result is not None and result.is_error else ""
    report(not failed, "Agent starts and logs in", detail or f"via {init.get('apiKeySource', '?')}")
    report(init.get("model") == providers.model(), "Model", init.get("model", "?"))
    available = set(init.get("tools", []))
    for name in BUILTIN_TOOLS:
        report(name in available, f"Tool: {name}")
    for name in CAT_TOOLS:
        report(f"mcp__cat__{name}" in available, f"Cat tool: {name}")
    extra = sorted(t for t in available if t not in BUILTIN_TOOLS and not t.startswith("mcp__cat__"))
    report(not extra or None, "No unexpected tools", ", ".join(extra))
    answered = "meow" in reply.lower()
    # Show the whole reply when something went wrong: it usually carries the provider's error message.
    report(answered, "Answers sensibly", reply.strip()[:40] if answered else " ".join(reply.split())[:500])
    if not config.COSTS_MONEY:
        print("     (free model: no charge)")
    elif result is not None and result.total_cost_usd is not None:
        usage = next(iter((result.model_usage or {}).values()), None)
        guessed = getattr(usage, "costBasis", None) == "unknown" or (isinstance(usage, dict) and usage.get("costBasis") == "unknown")
        note = "; a rough estimate, since this SDK version doesn't know the model's price yet" if guessed else ""
        print(f"     (that check cost about ${result.total_cost_usd:.4f}{note})")


def check_mac() -> None:
    print("Mac permissions")
    if not context.IS_MAC:
        report(None, "Not running on macOS, so skipping these")
        return
    ctx = context.front_context()
    report(ctx is not None, "Can see the frontmost app (Accessibility / Automation)",
           ctx.describe().replace("\n", "; ") if ctx else "allow your terminal in System Settings > Privacy & Security")
    try:
        png = context.screenshot()
        report(len(png) > 10_000, "Can take a screenshot (Screen Recording)", f"{len(png) // 1024} KB")
    except Exception as e:
        report(False, "Can take a screenshot (Screen Recording)", str(e))
    report(shutil.which("code") is not None or None, "`code` command for Show me",
           "found" if shutil.which("code") else "in VS Code run: Shell Command: Install 'code' command in PATH")
    report(shutil.which("pbcopy") is not None, "Clipboard (pbcopy)")


def main() -> int:
    print(f"{config.CAT_NAME} self-check\n")
    check_install()
    check_provider()
    if failures:
        print("\nFix the problems above first, then run the self-check again.")
        return 1
    asyncio.run(check_agent())
    check_mac()
    print("\n" + ("All good! 🐾" if not failures else f"{failures} problem(s) found."))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
