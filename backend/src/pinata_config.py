import requests, os
from dotenv import load_dotenv

load_dotenv()

class Pinata:
    def __init__(self):
        self.PINATA_API_KEY=os.getenv("PINATA_API_KEY")
        self.PINATA_SECRET_API_KEY=os.getenv("PINATA_API_Secret")
    
    def upload_to_pinata(self,data):
        url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        headers = {
            'pinata_api_key': self.PINATA_API_KEY,
            'pinata_secret_api_key': self.PINATA_SECRET_API_KEY,
            'Content-Type': 'application/json'
        }

        # Make a POST request to Pinata
        response = requests.post(url, json=data, headers=headers)

        return response
    
    def get_data_from_ipfs(self,ipfs_hash):
        url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"

        # Make a GET request to the IPFS gateway
        response = requests.get(url)

        return response