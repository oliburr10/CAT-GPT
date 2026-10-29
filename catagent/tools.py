"""The cat's own tools, served in-process to the agent as the MCP server "cat"."""

import asyncio
import base64
import json
from typing import Callable

from claude_agent_sdk import create_sdk_mcp_server, tool

from . import config, connections, context, costumes, memory, study

SERVER_NAME = "cat"


def _text(msg: str, is_error: bool = False) -> dict:
    result = {"content": [{"type": "text", "text": msg}]}
    if is_error:
        result["is_error"] = True
    return result


def _unpack(args: dict) -> dict:
    """Some models send nested fields as JSON strings; turn those back into lists and objects."""
    notes = dict(args)
    for key in ("answer", "colors", "given", "find", "methods", "solution", "checks", "options", "takeaways", "exam"):
        if isinstance(notes.get(key), str):
            try:
                notes[key] = json.loads(notes[key])
            except ValueError:
                pass
    return notes


def build_server(
    watcher: context.ContextWatcher,
    show_tip: Callable[[str, str, str, int], None],
    set_hidden: Callable[[bool], None],
    show_notes: Callable[[dict], None] = lambda notes: None,
    set_costume: Callable[[str], None] = lambda costume: None,
):
    """Create the tool server. The callbacks (show_tip, set_hidden, show_notes, set_costume) are
    thread-safe calls into the UI."""

    @tool(
        "what_am_i_working_on",
        "Which app, window, browser tab or document the user was using most recently "
        "(not counting the cat itself).",
        {},
    )
    async def what_am_i_working_on(args):
        where = connections.describe(watcher.last())
        if where is None:
            return _text("Unknown: no app has been seen yet (or this isn't macOS).")
        return _text(where)

    @tool(
        "look_at_screen",
        "Take a screenshot of the user's main display to see what they are looking at.",
        {},
    )
    async def look_at_screen(args):
        off_limits = connections.blocked(watcher.last())
        if off_limits:
            return _text(f"{off_limits} is in front and isn't connected, so you may not look at the screen. "
                         f"Ask the user to connect it in your panel (the arrow under you) first.", is_error=True)
        if config.HIDE_DURING_SCREENSHOT:
            set_hidden(True)
            await asyncio.sleep(0.4)  # give the windows time to disappear
        try:
            png = await asyncio.to_thread(context.screenshot)
        except Exception as e:
            return _text(f"Couldn't take a screenshot: {e}", is_error=True)
        finally:
            if config.HIDE_DURING_SCREENSHOT:
                set_hidden(False)
        return {
            "content": [
                {"type": "image", "data": base64.b64encode(png).decode(), "mimeType": "image/png"},
                {"type": "text", "text": "Screenshot of the user's main display."},
            ]
        }

    @tool(
        "show_tip",
        "Pop up a short speech bubble next to the cat on the desktop. Use it to point the user "
        "at something: what's wrong and exactly where. If the problem is in a local file, pass "
        "file_path (and line) so the bubble gets a 'Show me' button that opens it.",
        {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "A few words, e.g. 'Missing bracket'"},
                "message": {"type": "string", "description": "One to three short sentences."},
                "file_path": {"type": "string"},
                "line": {"type": "integer"},
            },
            "required": ["title", "message"],
        },
    )
    async def show_tip_tool(args):
        show_tip(args["title"], args["message"], args.get("file_path", ""), int(args.get("line", 0)))
        return _text("Tip shown.")

    @tool(
        "open_in_editor",
        "Open a local file for the user, in VS Code at a specific line when possible.",
        {
            "type": "object",
            "properties": {"file_path": {"type": "string"}, "line": {"type": "integer"}},
            "required": ["file_path"],
        },
    )
    async def open_in_editor(args):
        return _text(context.open_in_editor(args["file_path"], int(args.get("line", 0)),
                                            use_vscode=connections.is_connected("vscode")))

    @tool(
        "copy_to_clipboard",
        "Put text (code, a rewritten paragraph, a command) on the user's clipboard so they can "
        "paste it. Use this whenever they ask for something to copy, since your reply only "
        "shows up in a small speech cloud.",
        {"text": str},
    )
    async def copy_to_clipboard(args):
        return _text(context.copy_to_clipboard(args["text"]))

    @tool(
        "remember",
        "Save a lasting fact about the user (a preference, a project, how they like things "
        "done) to long-term memory.",
        {"fact": str},
    )
    async def remember(args):
        memory.add(args["fact"])
        return _text("Remembered.")

    @tool(
        "write_study_notes",
        "Write study notes that teach how to solve a problem and open them in the Notepad, laid out "
        "that get to the point: the answer first, what is given and what to find, every method and "
        "formula used (with what it says and why it applies), a plan, the solution in blocks named "
        "after what they work out, checks, takeaways and the exam version. "
        "Use this whenever the user wants to understand, learn, solve or prove something.",
        study.SCHEMA,
    )
    async def write_study_notes(args):
        notes = _unpack(args)
        found = study.problems(notes)
        if found:
            return _text("The notes weren't shown. Fix these and call write_study_notes again:\n- "
                         + "\n- ".join(found), is_error=True)
        show_notes(notes)
        return _text("The notes are open in the Notepad. Reply with one short sentence.")

    @tool(
        "change_costume",
        "Change your own costume on the desktop; the user watches you dress up. Use it when they "
        "ask you to dress up, change costume or turn into something. 'random' picks a different one.",
        {
            "type": "object",
            "properties": {"costume": {"type": "string", "enum": [*costumes.COSTUMES, "random"],
                                       "description": "ginger is your plain self, with no costume."}},
            "required": ["costume"],
        },
    )
    async def change_costume(args):
        costume = args.get("costume", "")
        if costume not in costumes.COSTUMES and costume != "random":
            return _text(f"There's no {costume!r} costume. Choose from: {', '.join(costumes.COSTUMES)} or random.",
                         is_error=True)
        set_costume(costume)
        return _text("You're changing now. Reply with one short, in-character sentence.")

    tools = [
        what_am_i_working_on, look_at_screen, show_tip_tool, open_in_editor, copy_to_clipboard, remember,
        write_study_notes, change_costume,
    ]
    server = create_sdk_mcp_server(SERVER_NAME, tools=tools)
    names = [f"mcp__{SERVER_NAME}__{t.name}" for t in tools]
    return server, names
