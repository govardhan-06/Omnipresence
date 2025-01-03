import os,sys
from supabase import create_client, Client
from dataclasses import dataclass
from dotenv import load_dotenv
from src.utils.exception import customException
from src.utils.logger import logging

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
    
    def insert_emergency_contact_hash(self,uid,hash):
        '''
        Insert emergency contact ipfs hash into supabase
        '''
        try:
            data={
                "emergency_contacts":hash
            }
            response = (self.supabase.table("user")
                        .update(data)
                        .eq("user_id", uid)
                        .execute()
                        )
            logging.info(f"Inserted contact hash into supabase.")
            return response
        except Exception as e:
            logging.error(f"Error inserting contact hash into supabase: {e}")
            return None
    
    def get_emergency_contact_hash(self,uid):
        '''
        Retrieve emergency contact ipfs hash into supabase
        '''
        try:
            response = (self.supabase.table("user")
                        .select("emergency_contacts")
                        .eq("user_id", uid)
                        .execute()
                        )
            logging.info(f"Inserted contact hash into supabase.")
            return response
        except Exception as e:
            logging.error(f"Error inserting contact hash into supabase: {e}")
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
        
    def insert_geofence(self,fence):
        '''
        Insert geofence into supabase
        '''
        try:
            response = (self.supabase.table("geofences")
                        .insert(fence)
                        .execute()
                        )
            logging.info(f"Inserted geofence coordinates into supabase.")
            return response
        except Exception as e:
            logging.error(f"Error inserting geofence coordinates into supabase: {e}")
            return None
    
    def get_geofence(self):
        '''
        Retrieve geofence data from supabase
        '''
        try:
            response = (
                        self.supabase.table("geofences")
                        .select("*")
                        .execute()
                        )
            logging.info(f"Fetched geofences from supabase.")
            return response.data
        except:
            logging.error(f"Error fetching geofences from supabase.")
            return None
    
    def insert_geofence_alerts(self,alert):
        '''
        Insert geofence alerts into supabase
        '''
        try:
            response = (self.supabase.table("geofence_alerts")
                        .insert(alert)
                        .execute()
                        )
            logging.info(f"Inserted alerts into supabase.")
            return response
        except Exception as e:
            logging.error(f"Error inserting alerts into supabase: {e}")
            return None
    
    def get_geofence_alerts(self,uid,geofence_id):
        '''
        Retrieve alerts from supabase
        '''
        try:
            response = (
                        self.supabase.table("geofence_alerts")
                        .select("*")
                        .eq("uid", uid)
                        .execute()
                        )
            logging.info(f"Fetched geofence alerts from supabase.")
            alerts=response.data
            return [alert for alert in alerts if alert['geofence_id'] == geofence_id]
        except:
            logging.error(f"Error fetching geofence alerts from supabase.")
            print(f"Error fetching geofence alerts from supabase.")
            return None
    
    def insert_sos_alerts(self,alert):
        '''
        Insert sos alerts into supabase
        '''
        try:
            response = (self.supabase.table("sos_alerts")
                        .insert(alert)
                        .execute()
                        )
            logging.info(f"Inserted alerts into supabase.")
            return response
        except Exception as e:
            logging.error(f"Error inserting alerts into supabase: {e}")
            return None
    
    def get_sos_alerts(self,id):
        '''
        Retrieve alerts from supabase
        '''
        try:
            response = (
                        self.supabase.table("sos_alerts")
                        .select("*")
                        .eq("id", id)
                        .execute()
                        )
            logging.info(f"Fetched sos alerts from supabase.")
            alerts=response.data
            return alerts
        except:
            logging.error(f"Error fetching sos alerts from supabase.")
            print(f"Error fetching sos alerts from supabase.")
            return None
    
    def upload_recordings(self, local_path, file_name):
        bucket_name = "sos_recordings"
        try:
            # Determine the file extension to set content type
            file_extension = local_path.split('.')[-1].lower()
            
            # Set content type based on file extension
            if file_extension in ['mp3', 'wav', 'flac']:  # Common audio file types
                content_type = "audio/mp3"
            elif file_extension == 'mp4':  # Video file type
                content_type = "video/mp4"
            else:
                print("Unsupported file type.")
                return 0
            
            with open(local_path, 'rb') as f:
                path_on_supastorage = f"{file_name}"
                # Upload the file to Supabase storage
                response = self.supabase.storage.from_(bucket_name).upload(
                    file=f,
                    path=path_on_supastorage,
                    file_options={"content-type": content_type}
                )
                return 1
        except Exception as e:
            print(f"Exception occurred during upload: {e}")
            return 0
    
    def get_recording_URL(self,alert_id,user_id):
        bucket_name = "sos_recordings"
        try:
            res1 = self.supabase.storage.from_(bucket_name).get_public_url(f'./{user_id}_{alert_id}.mp4')
            res2 = self.supabase.storage.from_(bucket_name).get_public_url(f'./{user_id}_{alert_id}.mp3')
            return res1, res2
        except Exception as e:
            print(f"Exception occurred during retrieval: {e}")
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
    response=supabase.get_geofence()
    print(response)


    

        
    
    
