from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

class Twilio:
    def __init__(self):
        ACCOUNt_SID = os.getenv("TWILIO_ACCOUNT_SID")
        AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
        self.TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
        self.client = Client(ACCOUNt_SID, AUTH_TOKEN)

    def make_emergency_call(self, user_name, family_contacts):
        # Create a dynamic emergency message
        emergency_message = (
            f"<Response>"
            f"<Say voice='alice'>"
            f"Hello, this is an automated emergency alert from Omnipresence."
            f" We have detected a possible emergency involving {user_name}."
            f" Please check in with {user_name} immediately."
            f" Please check your whatsapp for {user_name}'s location"
            f" If you're unable to reach them, consider reaching out to emergency services."
            f" Thank you, and stay safe."
            f" Team Omnipresence"
            f"</Say>"
            f"</Response>"
        )
        
        # Send emergency call to each family number
        for number in family_contacts:
            call = self.client.calls.create(
                to=number,
                from_=self.TWILIO_NUMBER,
                twiml=emergency_message
            )
            print(f"Emergency call initiated to {number}: {call.sid}")
