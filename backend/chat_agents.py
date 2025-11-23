import os
from agents import Agent, function_tool

from typing import Optional
from context import ChatPrompt
from email_sender import MailJetEmail

model_name = os.getenv("MODEL_NAME", "google/gemini-2.5-flash-lite")
litellm_model_name = "litellm/openrouter/" + model_name
send_email_client = MailJetEmail()

@function_tool
def record_user_details(email: str, name: Optional[str] = None, notes: Optional[str] = None) -> str:
    """Sends an email if the user is interested to connect and has provided an email address"""
    send_email_client.record_user_details(
        email=email,
        name=name or "not provided",
        notes=notes or "not provided",
    )
    return "ok"

@function_tool
def record_unknown_question(question: str) -> str:
    """Record any question that couldn't be answered as you didn't know the answer"""
    send_email_client.record_unknown_question(question)
    return "ok"


chat_agent = Agent(
    name="Digital Twin Agent",
    instructions=ChatPrompt.prompt(),
    tools=[record_user_details, record_unknown_question],
    model=litellm_model_name,
)