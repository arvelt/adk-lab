"""
Question: Can a minimal ADK Agent answer a text prompt using local Ollama?
Environment: ADK 2.11.0; Python 3.11.17; ollama_chat/qwen3:8b; LiteLLM 1.103.2.
Observed behavior: 2026-10-03 on Mac mini: final text '5'; RESULT: PASS.
"""
import asyncio
import json
import os
import platform
from importlib.metadata import version

from google.adk.agents import Agent
from google.adk.agents.run_config import RunConfig
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# ADK's documented Ollama chat connector; no API key is needed.
MODEL = "ollama_chat/qwen3:8b"
API_BASE = "http://localhost:11434"
os.environ["OLLAMA_API_BASE"] = API_BASE

agent = Agent(
    name="basic_agent",
    model=LiteLlm(model=MODEL, api_base=API_BASE, timeout=120),
    instruction="Answer the user's question briefly.",
    generate_content_config=types.GenerateContentConfig(temperature=0),
)

async def main() -> None:
    print(json.dumps({"adk": version("google-adk"), "python": platform.python_version(),
                      "litellm": version("litellm"), "model": MODEL,
                      "api_base": API_BASE}, ensure_ascii=False))
    sessions = InMemorySessionService()
    await sessions.create_session(app_name="basic_agent", user_id="experiment", session_id="run")
    runner = Runner(agent=agent, app_name="basic_agent", session_service=sessions)
    final_text = None
    try:
        async with asyncio.timeout(180):
            async for event in runner.run_async(
                user_id="experiment", session_id="run",
                new_message=types.Content(role="user", parts=[types.Part(text="What is 2 + 3? Answer with only the number. /no_think")]),
                run_config=RunConfig(max_llm_calls=6),
            ):
                for call in event.get_function_calls():
                    print("FUNCTION_CALL:", call.name, json.dumps(call.args))
                for response in event.get_function_responses():
                    print("FUNCTION_RESPONSE:", response.name, json.dumps(response.response))
                if event.error_code:
                    raise RuntimeError(f"{event.error_code}: {event.error_message}")
                if event.is_final_response() and event.content:
                    final_text = "".join(part.text or "" for part in event.content.parts or [] if not part.thought)
                    print("FINAL_TEXT:", repr(final_text))
        if not final_text:
            raise RuntimeError("No final text response was emitted")
        if final_text.strip() != "5":
            raise AssertionError(f"Expected 5, received {final_text!r}")
        print("RESULT: PASS")
    finally:
        await runner.close()


if __name__ == "__main__":
    asyncio.run(main())
