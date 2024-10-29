import firebase_admin
from firebase_admin import auth, credentials
import os
from dotenv import load_dotenv

load_dotenv()

class Firebase:
    def __init__(self):
        FIREBASE_KEY=os.getenv("FIREBASE_KEY")
        self.cred = credentials.Certificate(FIREBASE_KEY)
        firebase_admin.initialize_app(self.cred)

    def verify_user_token(self,id_token):
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            email = decoded_token.get("email")
            return {"uid":uid,"email":email}
        except ValueError:
            return None
