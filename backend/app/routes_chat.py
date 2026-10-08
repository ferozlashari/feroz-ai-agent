from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from . import llm, memory, tools
from .prompts import build_system_prompt
from .security import require_key

router = APIRouter(prefix="/api", dependencies=[Depends(require_key)])


class ChatRequest(BaseModel):
    messages: List[dict]
    provider: str = "auto"  # auto | groq | gemini | cerebras | mistral | openrouter | huggingface | ollama
    mode: str = "chat"  # chat | copilot
    temperature: float = Field(0.7, ge=0, le=1.5)
    reply_style: str = "auto"
    custom_instructions: str = ""
    user_name: str = ""


@router.post("/chat")
async def chat(req: ChatRequest):
    system = build_system_prompt(req.mode, req.reply_style, req.custom_instructions, req.user_name)
    history, has_images = llm.clean_messages(req.messages)
    history = llm.trim_history(history)
    messages = [{"role": "system", "content": system}] + history
    tool_specs = tools.specs_for("copilot" if req.mode == "copilot" else "chat")
    # Tasveer wale message me tool calls kam models support karte hain - is turn ke liye vision-only jao
    use_tools = None if has_images else (tool_specs or None)
    return await llm.chat_completion(
        messages, provider=req.provider, tools=use_tools, temperature=req.temperature, vision=has_images
    )


class ToolRequest(BaseModel):
    name: str
    arguments: dict = {}


@router.post("/tools/execute")
async def execute_tool(req: ToolRequest):
    result = await tools.execute_tool(req.name, req.arguments)
    return {"result": result}


# ------------------------------------------------------------------ memory


@router.get("/memory")
async def memory_list():
    return {"items": memory.list_all()}


class MemoryAdd(BaseModel):
    text: str


@router.post("/memory")
async def memory_add(req: MemoryAdd):
    mid = memory.add(req.text)
    return {"id": mid}


@router.delete("/memory/{memory_id}")
async def memory_delete(memory_id: int):
    memory.delete(memory_id)
    return {"ok": True}
