import os
import base64
import logging
import requests
from dotenv import load_dotenv
from mailjet_rest import Client

from .constants import RESUME_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv(override=True)


class MailJetEmail:

    def send_email(self, message: str):
        """ Send out an email with the given body to all sales prospects """

        api_key = os.getenv("MAILJET_API_KEY")
        api_secret = os.getenv("MAILJET_API_SECRET")
        from_email = os.getenv("MAILJET_FROM_EMAIL")
        to_email = os.getenv("MAILJET_TO_EMAIL")
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')

        data = {
            'Messages': [
                {
                    "From": {
                        "Email": from_email,
                        "Name": "Kaushik Paul's AI Twin"
                    },
                    "To": [
                        {
                            "Email": to_email,
                            "Name": "Ai Twin Owner"
                        }
                    ],
                    "Subject": "Notification from AI Twin",
                    "TextPart": message,
                }
            ]
        }
        result = mailjet.send.create(data=data)
        return {
            "status": "success",
            "response": result.json()
        }

    def record_user_details(self, email: str, name: str = "not provided", notes: str = "not provided") -> dict:
        self.send_email(f"Recording interest from\nName: {name},\nEmail: {email},\nNotes: {notes}")
        return {"recorded": "ok"}

    def record_unknown_question(self, question: str) -> dict:
        self.send_email("Recording question that was asked but I couldn't answer.\n"
                f"Question: {question}")
        return {"recorded": "ok"}

    def send_resume_to_user(self, to_email: str) -> dict:
        """Download resume PDF, convert to base64, and send via Mailjet with attachment"""
        try:
            # Download the resume PDF
            response = requests.get(RESUME_URL, timeout=30)
            response.raise_for_status()
            pdf_content = response.content
            
            # Convert to base64
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            
            # Get Mailjet credentials
            api_key = os.getenv("MAILJET_API_KEY")
            api_secret = os.getenv("MAILJET_API_SECRET")
            from_email = os.getenv("MAILJET_FROM_EMAIL")
            mailjet = Client(auth=(api_key, api_secret), version='v3.1')
            
            # Prepare email with attachment
            data = {
                'Messages': [
                    {
                        "From": {
                            "Email": from_email,
                            "Name": "Kaushik Paul's AI Twin"
                        },
                        "To": [
                            {
                                "Email": to_email,
                                "Name": "Resume Requester"
                            }
                        ],
                        "Subject": "Kaushik Paul's Resume | AI Twin",
                        "TextPart": "Hi,\n\nThank you for your interest! Please find my resume attached. This email was sent automatically by Kaushik Paul's AI Twin.\n\nBest regards,\nKaushik Paul's AI Twin",
                        "HTMLPart": "<p>Hi,</p><p>Thank you for your interest! Please find my resume attached. This email was sent automatically by <strong>Kaushik Paul's AI Twin</strong>.</p><p>Best regards,<br>Kaushik Paul's AI Twin</p>",
                        "Attachments": [
                            {
                                "ContentType": "application/pdf",
                                "Filename": "Kaushik_Paul_Resume.pdf",
                                "Base64Content": pdf_base64
                            }
                        ]
                    }
                ]
            }
            
            result = mailjet.send.create(data=data)
            response_json = result.json()
            
            logger.info("Resume sent successfully to %s", to_email)
            return {
                "status": "success",
                "message": f"Resume sent to {to_email}",
                "response": response_json
            }
            
        except requests.RequestException as e:
            logger.error("Failed to download resume: %s", str(e))
            raise Exception(f"Failed to download resume: {str(e)}")
        except Exception as e:
            logger.error("Failed to send resume to %s: %s", to_email, str(e))
            raise
