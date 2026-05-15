import logging
from dotenv import load_dotenv
from agents import Agent, function_tool, set_tracing_disabled

from typing import Optional
from .context import ChatPrompt
from .email_sender import MailJetEmail
from .model_client import create_agent_model

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv(override=True)

set_tracing_disabled(True)

send_email_client = MailJetEmail()

@function_tool
def record_user_details(email: str, name: Optional[str] = None, notes: Optional[str] = None) -> str:
    """Sends an email if the user is interested to connect and has provided an email address"""
    try:
        send_email_client.record_user_details(
            email=email,
            name=name or "not provided",
            notes=notes or "not provided",
        )
        return "ok"
    except Exception as e:
        logger.error("record_user_details failed for email=%s: %s", email, str(e))
        raise

@function_tool
def record_unknown_question(question: str) -> str:
    """Record any question that couldn't be answered as you didn't know the answer"""
    try:
        send_email_client.record_unknown_question(question)
        return "ok"
    except Exception as e:
        logger.error("record_unknown_question failed: %s", str(e))
        raise

@function_tool
def send_resume_to_user(email: str) -> str:
    """Send the resume PDF to the user's email address when they request it and has provided an email address"""
    try:
        send_email_client.send_resume_to_user(to_email=email)
        return "Resume sent successfully"
    except Exception as e:
        logger.error("send_resume_to_user failed for email=%s: %s", email, str(e))
        raise

chat_agent = Agent(
    name="Digital Twin Agent",
    instructions=ChatPrompt.prompt(),
    tools=[record_user_details, record_unknown_question, send_resume_to_user],
    model=create_agent_model(),
)
