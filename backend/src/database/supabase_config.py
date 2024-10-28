import os,sys
from supabase import create_client, Client
from dataclasses import dataclass
from dotenv import load_dotenv
from backend.src.utils.exception import customException
from backend.src.utils.logger import logging

@dataclass
class Supabase_config:
    load_dotenv()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class Supabase:
    def __init__(self):
        self.config=Supabase_config()
        self.supabase: Client = create_client(self.config.SUPABASE_URL, self.config.SUPABASE_KEY)
    
    def insert_user_data(self,uid,emailid):
        '''
        Insert user data into supabase
        '''
        try:
            data={
                "user_id":uid,
                "email_id":emailid
            }
            response = (self.supabase.table("user")
                        .insert(data)
                        .execute()
                        )
            logging.info(f"Inserted data into supabase.")
            return response
        except Exception as e:
            logging.error(f"Error inserting data into supabase: {e}")
            return "user already exists"
    
    def fetch_user_data(self,uid):
        '''
        Fetch user data from supabase
        '''
        try:
            response = (
                        self.supabase.table("user")
                        .select("user_id, email_id")
                        .eq("user_id", uid)
                        .execute()
                        )
            logging.info(f"Fetched user data from supabase.")
            return response
        except:
            logging.error(f"Error fetching user data from supabase.")
            return None
    
    def insert_ipfs_hash(self,hash):
        '''
        Insert ipfs hash into supabase
        '''
        try:
            data={
                "hash":hash
            }
            response = (self.supabase.table("incident_reporting")
                        .insert(data)
                        .execute()
                        )
            logging.info(f"Inserted data into supabase.")
            return response
        except Exception as e:
            logging.error(f"Error inserting data into supabase: {e}")
            return None
    
    def retrieve_hash(self):
        '''
        Retrieve ipfs hash from supabase
        '''
        try:
            response = (
                        self.supabase.table("incident_reporting")
                        .select("*")
                        .execute()
                        )
            logging.info(f"Fetched hashes from supabase.")
            return response
        except:
            logging.error(f"Error fetching hashes from supabase.")
            return None

# Module testing
if __name__=="__main__":
    supabase=Supabase()
    response=supabase.insert_user_data("MJmSNW4r9fanot9rOo2CRukngO13","tester2@example.com")
    print(response)
    response=supabase.insert_user_data("MJmSNW4r9fanot9rOo2CRukngO13","tester2@example.com")
    print(response)
    response=supabase.insert_user_data("Z9ZLeZ0DO6Z0qtbIs3Ha6eV4fSV2","tester1@example.com")
    print(response)
    response=supabase.fetch_user_data("Z9ZLeZ0DO6Z0qtbIs3Ha6eV4fSV2")
    print(response)
    response=supabase.fetch_user_data("qweLeZ0DO6Z0qtbIs3Ha6eV4fSV2")
    print(response)


    

        
    
    
