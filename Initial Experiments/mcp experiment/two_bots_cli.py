import asyncio
import json
import os
import socket
from typing import Any, Dict
from urllib.parse import urlparse

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.exceptions import McpError

SERVER_URL = os.getenv("MCP_URL") or "http://127.0.0.1:8000/mcp"

HELP = """
Commands:
  /use alice               - talk to alice
  /use bob                 - talk to bob
  /a2b <message>            - send message Alice -> Bob (Bob auto-replies back to Alice)
  /b2a <message>            - send message Bob -> Alice (Alice auto-replies back to Bob)
  /hist [alice|bob] [n]     - show last n messages (default 10)
  /history [alice|bob] [n]  - same as /hist
  /reset [alice|bob]        - reset bot conversation
  /help                     - show this help
  /quit                     - exit
Otherwise: your line is sent to the currently selected bot as user chat.
""".strip()


def _tcp_preflight(url: str) -> None:
    u = urlparse(url)
    host = u.hostname or "127.0.0.1"
    port = u.port or (443 if u.scheme == "https" else 80)
    try:
        with socket.create_connection((host, port), timeout=2.0):
            return
    except OSError as e:
        raise SystemExit(
            f"Cannot reach MCP server at {url}\n"
            f"- Is the server running?\n"
            f"- Is it listening on {host}:{port}?\n"
            f"Underlying error: {e}"
        )


def _unwrap_result(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Some MCP stacks wrap tool output as {"result": {...}}.
    Normalize so callers always see the inner dict.
    """
    if "result" in d and isinstance(d["result"], dict):
        return d["result"]
    return d


def _extract_tool_result_as_dict(res: Any) -> Dict[str, Any]:
    # 1) Best case: structuredContent is present
    sc = getattr(res, "structuredContent", None)
    if isinstance(sc, dict):
        return _unwrap_result(sc)

    # 2) Otherwise inspect content items
    content = getattr(res, "content", None) or []
    for item in content:
        t = getattr(item, "type", None) if not isinstance(item, dict) else item.get("type")

        if t == "json":
            data = getattr(item, "data", None) if not isinstance(item, dict) else item.get("data")
            if isinstance(data, dict):
                return _unwrap_result(data)

        if t == "text":
            text = getattr(item, "text", None) if not isinstance(item, dict) else item.get("text")
            if isinstance(text, str):
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, dict):
                        return _unwrap_result(parsed)
                except Exception:
                    pass

    return {"ok": False, "error": "Could not parse tool result", "raw": repr(res)}


def _print_result(title: str, obj: Dict[str, Any]) -> None:
    obj = _unwrap_result(obj)
    print(f"\n== {title} ==")
    for k, v in obj.items():
        if k == "history" and isinstance(v, list):
            print("history:")
            for m in v:
                role = m.get("role")
                content = m.get("content")
                tool_name = m.get("tool_name")
                if role == "tool":
                    print(f"  - tool({tool_name}): {content}")
                else:
                    print(f"  - {role}: {content}")
        else:
            print(f"{k}: {v}")


def _toggle_trailing_slash(url: str) -> str:
    return url[:-1] if url.endswith("/") else (url + "/")


async def _run_session(url: str) -> None:
    current_bot = "alice"

    async with streamable_http_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            while True:
                line = input(f"\n[{current_bot}]> ").strip()
                if not line:
                    continue

                if line in ("/quit", "/exit"):
                    break

                if line == "/help":
                    print(HELP)
                    continue

                if line.startswith("/use "):
                    bot = line.split(maxsplit=1)[1].strip().lower()
                    if bot in ("alice", "bob"):
                        current_bot = bot
                    else:
                        print("Unknown bot. Use 'alice' or 'bob'.")
                    continue

                if line.startswith("/a2b "):
                    msg = line.split(maxsplit=1)[1]
                    res = await session.call_tool(
                        "send_bot_message",
                        arguments={"from_bot": "alice", "to_bot": "bob", "message": msg, "auto_reply": True},
                    )
                    _print_result("Alice -> Bob", _extract_tool_result_as_dict(res))
                    continue

                if line.startswith("/b2a "):
                    msg = line.split(maxsplit=1)[1]
                    res = await session.call_tool(
                        "send_bot_message",
                        arguments={"from_bot": "bob", "to_bot": "alice", "message": msg, "auto_reply": True},
                    )
                    _print_result("Bob -> Alice", _extract_tool_result_as_dict(res))
                    continue

                if line.startswith("/hist") or line.startswith("/history"):
                    parts = line.split()
                    bot = (parts[1].lower() if len(parts) >= 2 else current_bot)
                    n = int(parts[2]) if len(parts) >= 3 else 10
                    res = await session.call_tool("get_bot_history", arguments={"bot": bot, "last_n": n})
                    _print_result(f"History ({bot})", _extract_tool_result_as_dict(res))
                    continue

                if line.startswith("/reset"):
                    parts = line.split()
                    bot = (parts[1].lower() if len(parts) >= 2 else current_bot)
                    res = await session.call_tool("reset_bot", arguments={"bot": bot})
                    _print_result(f"Reset ({bot})", _extract_tool_result_as_dict(res))
                    continue

                # Default: chat with selected bot
                res = await session.call_tool(
                    "chat_with_bot",
                    arguments={"bot": current_bot, "user_message": line},
                )
                data = _extract_tool_result_as_dict(res)

                if not isinstance(data, dict):
                    _print_result("Unexpected output", {"ok": False, "raw": repr(data)})
                    continue

                if not data.get("ok", True) and "reply" not in data:
                    _print_result("Error / Unexpected output", data)
                    continue

                print(f"\n{current_bot}: {data.get('reply')}")


async def main() -> None:
    print(f"Connecting to MCP server at {SERVER_URL} ...\n")
    print(HELP)

    _tcp_preflight(SERVER_URL)

    try:
        await _run_session(SERVER_URL)
    except McpError as e:
        alt = _toggle_trailing_slash(SERVER_URL)
        print(f"\nMCP session failed ({e}). Retrying with: {alt}")
        await _run_session(alt)


if __name__ == "__main__":
    asyncio.run(main())