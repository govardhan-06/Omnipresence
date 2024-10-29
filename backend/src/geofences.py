from geopy.distance import geodesic
from src.database.supabase_config import Supabase
from opencage.geocoder import OpenCageGeocode
from dotenv import load_dotenv
import os

load_dotenv()
supabase=Supabase()

def get_lat_long_opencage(location):
    api_key=os.getenv("OPEN_CAGE_API")
    geocoder = OpenCageGeocode(api_key)
    result = geocoder.geocode(location)
    if result:
        loc={
            "center_lat":result[0]['geometry']['lat'],
            "center_long":result[0]['geometry']['lng']
        }
        return loc
    else:
        print("Location not found.")
        return None

def is_within_geofence(user_location, geofence_center, radius):
    # Calculate the distance
    distance = geodesic(user_location, geofence_center).meters
    
    # Return whether the user is within the geofence
    return distance <= radius

def has_alert_been_sent(user_id, geofence_id):
    # Check in the database if the alert has been sent
    alert = supabase.get_geofence_alerts(user_id, geofence_id)
    if len(alert)==0:
        alert=None
    return alert is not None and alert[0]["is_sent"]

def mark_alert_as_sent(user_id, geofence_id):
    # Insert a new record in UserAlert
    new_alert={
        "uid":user_id,
        "geofence_id":geofence_id,
        "message":f"Alert for geofence {geofence_id}",
        "is_sent":True
    }
    return supabase.insert_geofence_alerts(new_alert)
