from src.database.supabase_config import Supabase
from src.utils.exception import customException
from src.utils.logger import logging
from src.services.whatsapp_config import WhatsApp
import requests, json
from src.services.pinata_config import Pinata
from src.services.twilio_config import Twilio

supabase=Supabase()
meta=WhatsApp()
pinata=Pinata()
twilio=Twilio()

def get_contacts(user_id):
    # Retrieve all hashes stored in Supabase
    res = supabase.get_emergency_contact_hash(user_id)

    # Iterate through each hash and retrieve data from IPFS
    for record in res.data:
        ipfs_hash = record["emergency_contacts"]
        retrieved_response = pinata.get_data_from_ipfs(ipfs_hash)

        # Check if data retrieval was successful
        if retrieved_response.status_code == 200:
            data_dict = retrieved_response.json()
            return data_dict["family_members"]
        else:
            return None

async def notify_contacts(user_details):
    # Retrieve contacts from Supabase
    contacts=get_contacts(user_details["user_id"])
    family_contacts=[]
    
    if not contacts:
        print("No contacts added.")
        return

    for contact in contacts:
        data={
            "recipient":contact["name"],
            "user":user_details["username"],
            "latitude":user_details["latitude"],
            "longitude":user_details["longitude"]
        }
        
        meta.send_whatsapp_message(contact["phone_number"],data)
        family_contacts.append(contact["phone_number"])
        print(f'Notified {contact["name"]} at {contact["phone_number"]}')
        logging.info(f'Notified {contact["name"]} at {contact["phone_number"]}')
    
    twilio.make_emergency_call(user_details["username"],family_contacts)

if __name__=="__main__":
    user={
        "user_id":"Z9ZLeZ0DO6Z0qtbIs3Ha6eV4fSV2",
        "username":"The M",
        "latitude":12.3456,
        "longitude":78.9012
    }
    notify_contacts(user)