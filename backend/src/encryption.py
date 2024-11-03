from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

class Encryption:
    def __init__(self):
        WHEREABOUTS_FERNET_KEY=os.getenv("WHEREABOUTS_FERNET_KEY")
        INCIDENT_FERNET_KEY=os.getenv("INCIDENT_FERNET_KEY")
        self.fernet_whereabouts = Fernet(WHEREABOUTS_FERNET_KEY)
        self.fernet_incidents=Fernet(INCIDENT_FERNET_KEY)
    
    #Whereabouts encryption
    def encrypt_whereabouts(self,data):
        encrypted_data = self.fernet_whereabouts.encrypt(data.encode())
        return encrypted_data

    #Whereabouts decryption
    def decrypt_whereabouts(self,encrypted_data):
        decrypted_data = self.fernet_whereabouts.decrypt(encrypted_data).decode()
        return decrypted_data
    
    #Incident encryption
    def encrypt_incidents(self,data):
        encrypted_data = self.fernet_incidents.encrypt(data.encode())
        return encrypted_data

    #Incident decryption
    def decrypt_incidents(self,encrypted_data):
        decrypted_data = self.fernet_incidents.decrypt(encrypted_data).decode()
        return decrypted_data