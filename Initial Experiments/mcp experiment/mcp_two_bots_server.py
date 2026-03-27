# Disclaimer: The following code is an illustrative example produced by an LLM

import os
import json
from typing import Any, Dict, List, Literal, Optional, Tuple

from mcp.server.fastmcp import FastMCP
from ollama import AsyncClient

BotName = Literal["alice", "bob"]

DEFAULT_MODEL: str = os.getenv("OLLAMA_MODEL") or "llama3.2"
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST") or "http://localhost:11434"

# The key fix: make it crystal-clear who "the user" is.
BASE_SYSTEM_RULES = (
    "You are chatting with a HUMAN USER via a CLI.\n"
    "Messages from the other bot are INTERNAL NOTES, not the human user.\n"
    "Always respond to the HUMAN USER unless explicitly instructed otherwise.\n"
    "Do not address the other bot as if they are the user.\n"
    "If you need info from the other bot, use the send_to_bot tool.\n"
)

SYSTEM_PROMPTS: Dict[BotName, str] = {
    "alice": (
        BASE_SYSTEM_RULES
        + "You are Alice. You're concise, practical, and friendly.\n"
        "Tool rules:\n"
        "- Use tool calling (not JSON in text).\n"
        "- When done, answer the HUMAN USER in normal text.\n"
    ),
    "bob": (
        BASE_SYSTEM_RULES
        + "You are Bob. You're curious, playful, and asks good follow-up questions.\n"
        "Tool rules:\n"
        "- Use tool calling (not JSON in text).\n"
        "- When done, answer the HUMAN USER in normal text.\n"
    ),
}

def _new_history(bot: BotName) -> List[Dict[str, Any]]:
    """Create a new conversation history for a bot."""
    return [{"role": "system", "content": SYSTEM_PROMPTS[bot]}]

HISTORIES: Dict[BotName, List[Dict[str, Any]]] = {
    "alice": _new_history("alice"),
    "bob": _new_history("bob"),
}

ollama_client = AsyncClient(host=OLLAMA_HOST)

mcp = FastMCP("Two Bots (Ollama + Tools)", json_response=True)

def _inject_internal_note(bot: BotName, note: str) -> None:
    """
    INTERNAL NOTE channel: record cross-bot messages in a way that does NOT
    masquerade as a human 'user' turn.
    """
    HISTORIES[bot].append({"role": "system", "content": f"INTERNAL NOTE: {note}"})

@mcp.tool()
async def chat_with_bot(bot: BotName, user_message: str) -> Dict[str, Any]:
    """Chat with a specific bot."""
    if bot not in HISTORIES:
        return {"ok": False, "error": f"Unknown bot '{bot}'"}

    HISTORIES[bot].append({"role": "user", "content": user_message})
    reply = await _ollama_agent_reply(bot)
    HISTORIES[bot].append({"role": "assistant", "content": reply})

    return {"ok": True, "bot": bot, "model": DEFAULT_MODEL, "reply": reply, "history_len": len(HISTORIES[bot])}

@mcp.tool()
async def send_bot_message(
    from_bot: BotName,
    to_bot: BotName,
    message: str,
    auto_reply: bool = True
) -> Dict[str, Any]:
    """Send a message from one bot to another."""
    if from_bot not in HISTORIES or to_bot not in HISTORIES:
        return {"ok": False, "error": "Unknown bot name(s)"}
    if from_bot == to_bot:
        return {"ok": False, "error": "from_bot and to_bot must be different"}

    # ✅ deliver to receiver as INTERNAL NOTE, not as "user"
    _inject_internal_note(to_bot, f"Message from {from_bot}: {message}")

    result: Dict[str, Any] = {
        "ok": True,
        "from_bot": from_bot,
        "to_bot": to_bot,
        "delivered": message,
        "auto_reply": auto_reply,
    }

    if auto_reply:
        to_reply = await _ollama_agent_reply(to_bot)
        # store receiver reply as normal assistant message in receiver history
        HISTORIES[to_bot].append({"role": "assistant", "content": to_reply})

        # ✅ deliver back to sender as INTERNAL NOTE too
        _inject_internal_note(from_bot, f"Reply from {to_bot}: {to_reply}")

        result["to_bot_reply"] = to_reply

    return result

@mcp.tool()
def get_bot_history(bot: BotName, last_n: int = 20) -> Dict[str, Any]:
    """Get the recent history for a bot."""
    if bot not in HISTORIES:
        return {"ok": False, "error": f"Unknown bot '{bot}'"}

    last_n = max(1, min(200, int(last_n)))
    return {"ok": True, "bot": bot, "history": HISTORIES[bot][-last_n:]}

@mcp.tool()
def reset_bot(bot: BotName) -> Dict[str, Any]:
    """Reset a bot's conversation history."""
    if bot not in HISTORIES:
        return {"ok": False, "error": f"Unknown bot '{bot}'"}

    HISTORIES[bot] = _new_history(bot)
    return {"ok": True, "bot": bot, "history_len": len(HISTORIES[bot])}

# ----------------------------
# Ollama tool-calling agent loop
# ----------------------------

def _ollama_tools_for(_: BotName) -> List[Dict[str, Any]]:
    """Get the available tools for a bot."""
    return [
        {
            "type": "function",
            "function": {
                "name": "send_to_bot",
                "description": "Send a message to the other bot (alice<->bob).",
                "parameters": {
                    "type": "object",
                    "required": ["to_bot", "message"],
                    "properties": {
                        "to_bot": {"type": "string", "enum": ["alice", "bob"]},
                        "message": {"type": "string"},
                        "auto_reply": {"type": "boolean", "default": True},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_history",
                "description": "Get recent chat history for this bot.",
                "parameters": {
                    "type": "object",
                    "properties": {"last_n": {"type": "integer", "default": 10}},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "reset_me",
                "description": "Reset this bot's conversation history.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]

def _try_parse_pseudo_tool_call(content: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Try to parse a pseudo tool call from content."""
    content = content.strip()
    if not (content.startswith("{") and content.endswith("}")):
        return None
    try:
        obj = json.loads(content)
    except Exception:
        return None
    if not isinstance(obj, dict):
        return None
    name = obj.get("name")
    params = obj.get("parameters") or obj.get("arguments") or {}
    if not isinstance(name, str) or not isinstance(params, dict):
        return None
    if name not in {"send_to_bot", "get_history", "reset_me"}:
        return None
    return name, params

async def _execute_tool_for_bot(bot: BotName, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool for a bot."""
    if name == "send_to_bot":
        to_bot = args.get("to_bot")
        message = args.get("message")
        auto_reply = bool(args.get("auto_reply", True))
        if to_bot not in ("alice", "bob"):
            return {"ok": False, "error": f"Invalid to_bot: {to_bot}"}
        if to_bot == bot:
            return {"ok": False, "error": "Refusing to send_to_bot to self"}
        if not isinstance(message, str) or not message.strip():
            return {"ok": False, "error": "Missing/invalid message"}
        return await send_bot_message(from_bot=bot, to_bot=to_bot, message=message, auto_reply=auto_reply)

    if name == "get_history":
        last_n = int(args.get("last_n", 10))
        return get_bot_history(bot=bot, last_n=last_n)

    if name == "reset_me":
        return reset_bot(bot=bot)

    return {"ok": False, "error": f"Unknown tool: {name}"}

async def _ollama_agent_reply(bot: BotName) -> str:
    """Get a reply from the Ollama agent with streaming support."""
    tools = _ollama_tools_for(bot)

    for _step in range(10):
        resp = await ollama_client.chat(
            model=DEFAULT_MODEL,
            messages=HISTORIES[bot],
            tools=tools,
            stream=True,
        )

        # For streaming, we need to collect chunks
        full_content = ""
        accumulated_tool_calls = []

        # Process streaming response
        try:
            async for chunk in resp:
                # Safely access chunk attributes
                if hasattr(chunk, 'message'):
                    # Handle tool calls in streaming chunks
                    if hasattr(chunk.message, "tool_calls") and chunk.message.tool_calls:
                        accumulated_tool_calls.extend(chunk.message.tool_calls)

                    # Handle content in streaming chunks
                    if hasattr(chunk.message, "content") and chunk.message.content:
                        content_chunk = chunk.message.content
                        full_content += content_chunk
        except Exception as e:
            # If streaming fails, fall back to non-streaming
            print(f"Streaming failed, falling back to non-streaming: {e}")
            resp = await ollama_client.chat(
                model=DEFAULT_MODEL,
                messages=HISTORIES[bot],
                tools=tools,
                stream=False,
            )

            tool_calls = getattr(resp.message, "tool_calls", None)
            content = getattr(resp.message, "content", None)

            if tool_calls:
                # record tool-call request
                if hasattr(resp.message, "model_dump"):
                    HISTORIES[bot].append(resp.message.model_dump())
                else:
                    HISTORIES[bot].append({"role": "assistant", "content": content or "", "tool_calls": tool_calls})

                for call in tool_calls:
                    name = call.function.name
                    args = call.function.arguments or {}
                    if not isinstance(args, dict):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {}

                    result = await _execute_tool_for_bot(bot, name, args)
                    HISTORIES[bot].append({"role": "tool", "tool_name": name, "content": json.dumps(result)})

                continue

            return content or ""

        # After collecting all chunks, process the complete response
        if accumulated_tool_calls:
            # record tool-call request
            HISTORIES[bot].append({"role": "assistant", "content": full_content or "", "tool_calls": accumulated_tool_calls})

            for call in accumulated_tool_calls:
                name = call.function.name
                args = call.function.arguments or {}
                if not isinstance(args, dict):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {}

                result = await _execute_tool_for_bot(bot, name, args)
                HISTORIES[bot].append({"role": "tool", "tool_name": name, "content": json.dumps(result)})

            continue

        if isinstance(full_content, str) and full_content.strip():
            pseudo = _try_parse_pseudo_tool_call(full_content)
            if pseudo:
                name, args = pseudo
                HISTORIES[bot].append({"role": "assistant", "content": full_content})
                result = await _execute_tool_for_bot(bot, name, args)
                HISTORIES[bot].append({"role": "tool", "tool_name": name, "content": json.dumps(result)})
                continue

            return full_content

        # empty content: nudge
        HISTORIES[bot].append(
            {"role": "user", "content": "Please answer the HUMAN USER in normal text. Use tools only if needed."}
        )

    return "I got stuck in a tool loop. Please rephrase, or ask me to answer without tools."

if __name__ == "__main__":
    print("Starting MCP Streamable HTTP server (FastMCP)...")
    print("Expected endpoint (most installs): http://127.0.0.1:8000/mcp")
    mcp.run(transport="streamable-http")