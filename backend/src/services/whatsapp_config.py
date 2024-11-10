import requests
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

class WhatsApp:
    def __init__(self):
        self.token = os.getenv("META_ACCESS_TOKEN")
        self.phone_id = os.getenv("META_PHONE_ID") #Phone number ID from WhatsApp Business Account

    def send_whatsapp_message(self,recipient_phone,text):
        url = f"https://graph.facebook.com/v21.0/{self.phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        text["location"]=self.generate_location_link(text["latitude"],text["longitude"])
        data = {
            "messaging_product": "whatsapp",
            "to": recipient_phone,
            "type": "template",
            "template": {
                "name": "sos_alert",
                "language": { "code": "en_US" },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            { "type": "text", "text": text["recipient"] },
                            { "type": "text", "text": text["user"] },
                            { "type": "text", "text": text["location"] }
                        ]
                    }
                ]
            }
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print("Failed to send message:", response.json())

    def refresh_access_token(self):
        refresh_url = f"https://graph.facebook.com/v21.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": os.getenv("META_APP_ID"),
            "client_secret": os.getenv("META_APP_SECRET"),
            "fb_exchange_token": self.token
        }
        response = requests.get(refresh_url, params=params)
        if response.status_code == 200:
            new_token = response.json()["access_token"]
            # Save the new token securely
            os.environ["META_ACCESS_TOKEN"] = new_token
            print("Access token refreshed successfully!")
        else:
            print("Failed to refresh access token:", response.json())
        
    def generate_location_link(self,latitude, longitude):
        return f"https://www.google.com/maps?q={latitude},{longitude}"

if __name__=="__main__":
    meta = WhatsApp()
    ph="918590169903"
    data={
        "recipient":"Govardhan",
        "user":"The M",
        "latitude":"37.7749",
        "longitude":"-122.4194"
    }
    meta.send_whatsapp_message(ph,data)
