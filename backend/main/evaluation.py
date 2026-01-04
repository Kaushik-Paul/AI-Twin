import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI

from .context import EvaluationPrompt
from . import constants

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv(override=True)

groq_api_key = os.getenv('GROQ_API_KEY')
openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
model_name = os.getenv("DEFAULT_MODEL_NAME", "google/gemini-2.5-flash-lite")
evaluator_model_name = os.getenv("EVALUATION_MODEL_NAME", "google/gemini-2.5-flash-lite")


def _parse_comma_separated_env(var_name: str) -> Optional[List[str]]:
    value = os.getenv(var_name)

    if not value:
        return None

    parsed = [item.strip() for item in value.split(",") if item.strip()]
    return parsed or None


def _parse_bool_env(var_name: str) -> Optional[bool]:
    value = os.getenv(var_name)
    if value is None:
        return False

    return value.strip().lower() == "true"

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

class ChatEvaluation:
    def __init__(self):
        self.evaluator_system_prompt = EvaluationPrompt().fetch_evaluator_system_prompt()
        self.client = OpenAI(api_key=openrouter_api_key, base_url=constants.OPENROUTER_BASE_URL)
        self.provider_preferences = self._build_provider_preferences()

    @staticmethod
    def _build_provider_preferences() -> Dict:
        provider_config: Dict = {}
        order = _parse_comma_separated_env("EVALUATION_PROVIDER_ORDER")
        order_enabled = _parse_bool_env("EVALUATION_PROVIDER_ORDER_ENABLED")

        if order_enabled and order:
            provider_config["order"] = order

        return provider_config

    def evaluate(self, reply, message, history) -> Evaluation:
        """
        Evaluate the response from the agent
        :param reply: Response from agent
        :param message: Message from user
        :param history: Conversation history
        :return: Evaluation result
        """

        messages = [{"role": "system", "content": self.evaluator_system_prompt}] + [{"role": "user", "content": EvaluationPrompt.evaluator_user_prompt(reply, message, history)}]
        try:
            request_kwargs = {
                "model": evaluator_model_name,
                "input": messages,
                "text_format": Evaluation,
            }

            # Extra body for provider preferences
            if self.provider_preferences:
                request_kwargs["extra_body"] = {"provider": self.provider_preferences}
            response = self.client.responses.parse(**request_kwargs)
            return response.output_parsed
        except Exception as e:
            logger.error("Evaluation API call failed: %s", str(e))
            raise

    def rerun(self, system_prompt, reply, message, history, feedback):
        """
        Rerun the chat agent with the updated system prompt
        :param system_prompt: Original system chat prompt
        :param reply: Previous failed response from agent
        :param message: Message from user
        :param history: Conversation history
        :param feedback: Feedback received
        :return: Updated response from agent
        """

        updated_system_prompt = system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
        updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
        updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
        messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
        try:
            response = self.client.chat.completions.create(model=model_name, messages=messages)
            return response.choices[0].message.content
        except Exception as e:
            logger.error("Rerun API call failed: %s", str(e))
            raise
