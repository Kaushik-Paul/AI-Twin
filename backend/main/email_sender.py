import os
from dotenv import load_dotenv
from mailjet_rest import Client


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
                        "Name": "Kaushik Paul"
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
