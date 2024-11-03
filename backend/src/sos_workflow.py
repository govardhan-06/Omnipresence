from src.database.supabase_config import Supabase
from src.utils.exception import customException
from src.utils.logger import logging
from src.whatsapp_config import WhatsApp
import requests, json

supabase=Supabase()
meta=WhatsApp()

def get_contacts(user_id):
    # Retrieve all hashes stored in Supabase
    res = supabase.get_emergency_contact_hash(user_id)

    # Iterate through each hash and retrieve data from IPFS
    for record in res.data:
        ipfs_hash = record["emergency_contacts"]
        retrieved_response = requests.post(f"http://127.0.0.1:5001/api/v0/cat?arg={ipfs_hash}")
        
        # Check if data retrieval was successful
        if retrieved_response.status_code == 200:
            data_dict = json.loads(retrieved_response.text)
            print(data_dict)
            return data_dict["family_members"]
        else:
            return None

async def notify_contacts(user_details):
    # Retrieve contacts from Supabase
    contacts=get_contacts(user_details["user_id"])
    
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
        print(f'Notified {contact["name"]} at {contact["phone_number"]}')
        logging.info(f'Notified {contact["name"]} at {contact["phone_number"]}')

if __name__=="__main__":
    user={
        "user_id":"Z9ZLeZ0DO6Z0qtbIs3Ha6eV4fSV2",
        "username":"The M",
        "latitude":12.3456,
        "longitude":78.9012
    }
    notify_contacts(user)