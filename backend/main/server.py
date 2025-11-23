from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Optional
import json
import uuid
from datetime import datetime
from agents import Runner

from chat_agents import chat_agent
from context import ChatPrompt
from conversation import load_conversation, save_conversation
from evaluation import ChatEvaluation

# Load environment variables
load_dotenv(override=True)

model_name = os.getenv("MODEL_NAME", "google/gemini-2.5-flash-lite")
app = FastAPI()
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/")
async def root():
    return {
        "message": "AI Digital Twin API",
        "memory_enabled": True,
        "storage": "S3" if USE_S3 else "local",
        "ai_model": model_name,
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "use_s3": USE_S3,
        "model": model_name,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Load conversation history
        conversation = load_conversation(session_id)

        evaluate_response = ChatEvaluation()

        history_text = json.dumps(conversation, ensure_ascii=False)
        input_parts = [
            "Here is the prior conversation as a JSON array of messages:",
            history_text,
            "Each message has 'role' and 'content' fields.",
            "Here is the user's latest message:",
            request.message,
            "Respond to the user's latest message as the digital twin, using your tools when appropriate.",
        ]
        agent_input = "\n\n".join(input_parts)

        agent_result = await Runner.run(
            chat_agent,
            input=agent_input,
        )

        assistant_response = agent_result.final_output
        if isinstance(assistant_response, dict):
            assistant_response = json.dumps(assistant_response, ensure_ascii=False)
        elif not isinstance(assistant_response, str):
            assistant_response = str(assistant_response)

        evaluation = evaluate_response.evaluate(assistant_response, request.message, conversation)

        if not evaluation.is_acceptable:
            assistant_response = evaluate_response.rerun(ChatPrompt.prompt(), assistant_response, request.message, conversation, evaluation.feedback)

        conversation.append(
            {"role": "user", "content": request.message, "timestamp": datetime.now().isoformat()}
        )
        conversation.append(
            {
                "role": "assistant",
                "content": assistant_response,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Save conversation
        save_conversation(session_id, conversation)

        return ChatResponse(response=assistant_response, session_id=session_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Retrieve conversation history"""
    try:
        conversation = load_conversation(session_id)
        return {"session_id": session_id, "messages": conversation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)