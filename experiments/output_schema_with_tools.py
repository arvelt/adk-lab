"""
Question: Can one ADK Agent execute tools AND return output_schema with Ollama?
Environment: ADK 2.11.0; Python 3.11.17; ollama_chat/qwen3:8b; LiteLLM 1.103.2.
Observed behavior: 2026-10-03 on Mac mini: get_reading executed once, then
    set_model_response produced valid JSON and dict session state; RESULT: PASS.
    LiteLlm reported output_schema_and_tools=False: ADK used its tool fallback,
    not a native response schema. An EXPERIMENTAL schema warning was emitted.
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

from pydantic import BaseModel, ConfigDict

# ADK's documented Ollama chat connector; no API key is needed.
MODEL = "ollama_chat/qwen3:8b"
API_BASE = "http://localhost:11434"
os.environ["OLLAMA_API_BASE"] = API_BASE

tool_calls: list[str] = []


def get_reading(sample_id: str) -> dict:
    """Return a synthetic lab reading for sample_01; no external/private data."""
    tool_calls.append(sample_id)
    if sample_id != "sample_01":
        raise ValueError("Unknown synthetic sample")
    return {"sample_id": sample_id, "reading": 731}


class Reading(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    sample_id: str
    reading: int


def inspect_request(callback_context, llm_request):
    """Expose ADK's request route without changing the request."""
    config = llm_request.config
    names = [f.name for tool in config.tools or [] for f in tool.function_declarations or []]
    print("ADK_REQUEST:", json.dumps({
        "tools": names, "native_response_schema": bool(config.response_schema),
    }))


model = LiteLlm(model=MODEL, api_base=API_BASE, timeout=120)
agent = Agent(
    name="output_schema_with_tools",
    model=model,
    instruction="Call get_reading for the requested sample. Use the tool result for the final structured answer.",
    tools=[get_reading],
    output_schema=Reading,
    output_key="reading",
    before_model_callback=inspect_request,
    generate_content_config=types.GenerateContentConfig(temperature=0),
)

async def main() -> None:
    print(json.dumps({"adk": version("google-adk"), "python": platform.python_version(),
                      "litellm": version("litellm"), "model": MODEL,
                      "api_base": API_BASE}, ensure_ascii=False))
    sessions = InMemorySessionService()
    await sessions.create_session(app_name="output_schema_with_tools", user_id="experiment", session_id="run")
    runner = Runner(agent=agent, app_name="output_schema_with_tools", session_service=sessions)
    final_text = None
    try:
        async with asyncio.timeout(180):
            async for event in runner.run_async(
                user_id="experiment", session_id="run",
                new_message=types.Content(role="user", parts=[types.Part(text="Get the reading for sample_01 using get_reading. /no_think")]),
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
        parsed = Reading.model_validate_json(final_text)
        print("EXECUTED_TOOL_CALLS:", json.dumps(tool_calls))
        print("MODEL_CAPABILITIES:", model.capabilities.model_dump())
        if tool_calls != ["sample_01"]:
            raise AssertionError(f"Expected one real tool execution, got {tool_calls!r}")
        if parsed != Reading(sample_id="sample_01", reading=731):
            raise AssertionError(f"Unexpected reading: {parsed}")
        session = await sessions.get_session(app_name="output_schema_with_tools", user_id="experiment", session_id="run")
        stored = session.state.get("reading")
        print("SESSION_STATE:", type(stored).__name__, json.dumps(stored))
        if stored != parsed.model_dump():
            raise AssertionError("Session state differs from validated final output")
        print("RESULT: PASS")
    finally:
        await runner.close()


if __name__ == "__main__":
    asyncio.run(main())
