from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import sys,uvicorn, aiofiles,os
from src.utils.exception import customException
from src.utils.logger import logging
from starlette.responses import JSONResponse
from src.database.supabase_config import Supabase
from src.database.firebase_config import Firebase
from pydantic import BaseModel, ConfigDict,  ValidationError
from typing import Optional
from starlette.websockets import WebSocketDisconnect, WebSocketState
from enum import Enum
import ipfshttpclient, json, requests
from src.geofences import is_within_geofence, has_alert_been_sent, mark_alert_as_sent, get_lat_long_opencage
from src.sos_workflow import notify_contacts
from src.safe_route import OpenRouteService
from typing import List

app = FastAPI()
firebase=Firebase()
supabase=Supabase()
ors=OpenRouteService()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the possible incident types
class IncidentType(str, Enum):
    harassment = "Harassment"
    suspicious_activity = "Suspicious Activity"
    theft_and_vandalism = "Theft and Vandalism"
    physical_assault = "Physical Assault"
    emergency_situations = "Emergency Situations"
    unsafe_conditions = "Unsafe Conditions"
    public_misconduct = "Public Misconduct"
    gender_based_violence = "Gender-based Violence"
    safety_concern = "Safety Concern"
    others = "Others"

# Define the Incident model
class Incident(BaseModel):
    model_config = ConfigDict(use_enum_values=True)  # Use enum values directly as strings
    incident_type: IncidentType
    location: str
    time_of_incident: str  # Format: YYYY-MM-DD HH:MM
    description: str
    urgency_level: Optional[str] = None  # High, Medium, Low
    witnesses: Optional[str] = None  # Descriptions of witnesses
    additional_comments: Optional[str] = None  # Any additional comments
    reported_by: Optional[str] = "anonymous"  # Default to anonymous

# User Location Model
class UserLocation(BaseModel):
    user_id: str
    latitude: float
    longitude: float

#Geofence Model
class Geofence(BaseModel):
    location: str
    radius_meters: float

class FamilyMember(BaseModel):
    name: str
    relation: str
    phone_number: str

@app.get("/")
async def home():
    '''
    This function is used to redirect to the swaggerUI page.
    '''
    return RedirectResponse(url="/docs")

@app.post("/login-or-register")
async def login_or_register(token:str):
    '''
    This function is used to login or register a user using firebase ID Token.
    Not Tested
    '''
    try:
        # Check if the token is valid
        user=firebase.verify_user_token(token)
        response=supabase.fetch_user_data(user["uid"])
        if response:
            return JSONResponse(content={"message": "User verified successfully"}, status_code=200)
        else:
            # If the user does not exist, create a new user
            supabase.insert_user_data(user["uid"],user["email"])
            return JSONResponse(content={"message": "User created successfully"}, status_code=200)
    
    except ValueError:
        # This could happen if the token is invalid or expired
        raise HTTPException(status_code=401, detail="Invalid token")
    
    except Exception as e:
        # Log the exception for debugging
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

family_details_db={}

@app.post("/family_details")
async def add_family_details(user_id: str, family_members: List[FamilyMember]):
    '''
    This function is used to update family members to a user.
    '''
    family_member_dicts = [member.model_dump() for member in family_members]

    data_dict = {
        "user_id": user_id,
        "family_members": family_member_dicts
    }

    # Convert to JSON string
    data_json = json.dumps(data_dict)

    response = requests.post("http://127.0.0.1:5001/api/v0/add", files={"file": data_json})

    if response.status_code == 200:
        res = response.json()["Hash"]  # IPFS returns a hash for the stored data
        # Add the hash to the database
        if(supabase.insert_emergency_contact_hash(user_id,res)):
            return JSONResponse(content={"message": "Family details added successfully"}, status_code=200)
        else:
            return JSONResponse(content={"message":"Failed to add family details to supabase"},status_code=500)
    
    else:
        return JSONResponse(content={"message":"Failed to add family details to IPFS"},status_code=500)

@app.get("/family_details/{user_id}")
async def get_family_details(user_id: str):
    '''
    For Admin
    This function is used to get the family details of a user.
    '''
    # Retrieve all hashes stored in Supabase
    res = supabase.get_emergency_contact_hash(user_id)
    retrieved_data = []

    # Iterate through each hash and retrieve data from IPFS
    for record in res.data:
        ipfs_hash = record["emergency_contacts"]
        retrieved_response = requests.post(f"http://127.0.0.1:5001/api/v0/cat?arg={ipfs_hash}")
        
        # Check if data retrieval was successful
        if retrieved_response.status_code == 200:
            data_dict = json.loads(retrieved_response.text)
            retrieved_data.append({
                "ipfs_hash": ipfs_hash,
                "data": data_dict
            })
        else:
            retrieved_data.append({
                "ipfs_hash": ipfs_hash,
                "data": "Failed to retrieve data",
                "status_code": retrieved_response.status_code
            })

    # Return all retrieved data in a single JSON response
    return JSONResponse(content={"message": "Data retrieved from IPFS", "retrieved_data": retrieved_data}, status_code=200)

@app.post("/report-incident")
async def report_incident(uid:str,incident: Incident):
    # Convert to JSON string
    data_dict = incident.model_dump()
    location=data_dict["location"]
    data_dict["uid"]=uid

    data_json = json.dumps(data_dict)
    
    # Add JSON data to IPFS
    response = requests.post("http://127.0.0.1:5001/api/v0/add", files={"file": data_json})

    geofence=get_lat_long_opencage(location)
    geofence["radius_meters"]=500
    
    if response.status_code == 200:
        res = response.json()["Hash"]  # IPFS returns a hash for the stored data
        # Add the hash to the database
        if(supabase.insert_ipfs_hash(res)):
            if(supabase.insert_geofence(geofence)):
                return JSONResponse(content={"message":"Data inserted to IPFS and hash + geofence inserted to supabase","ipfs_hash": res},status_code=200)
            else:
                return JSONResponse(content={"message":"Data inserted to IPFS and hash inserted to supabase. Failed to insert geofence coordinates","ipfs_hash": res},status_code=200)
        else:
            return JSONResponse(content={"message":"Failed to insert hash to supabase"},status_code=500)

    else:
        print("Failed to add data to IPFS:", response.status_code)
        return JSONResponse(content={"message":"Failed to insert data to IPFS","ipfs_hash": None},status_code=500)

@app.get("/retrieve-incident")
async def retrieve_incident():
    '''
    For Admin
    Retrieve all incidents from the database
    '''
    # Retrieve all hashes stored in Supabase
    res = supabase.retrieve_hash()
    retrieved_data = []

    # Iterate through each hash and retrieve data from IPFS
    for record in res.data:
        ipfs_hash = record["hash"]
        retrieved_response = requests.post(f"http://127.0.0.1:5001/api/v0/cat?arg={ipfs_hash}")
        
        # Check if data retrieval was successful
        if retrieved_response.status_code == 200:
            data_dict = json.loads(retrieved_response.text)
            retrieved_data.append({
                "ipfs_hash": ipfs_hash,
                "data": data_dict
            })
        else:
            retrieved_data.append({
                "ipfs_hash": ipfs_hash,
                "data": "Failed to retrieve data",
                "status_code": retrieved_response.status_code
            })

    # Return all retrieved data in a single JSON response
    return JSONResponse(content={"message": "Data retrieved from IPFS", "retrieved_data": retrieved_data}, status_code=200)

@app.post("/update_location")
async def update_location(location: UserLocation):
    '''
    Updates the location of the user and cross checks with the geofence corrdinates in the geofence database.
    '''
    user_location = (location.latitude, location.longitude)
    geofences = supabase.get_geofence()
    alerts_to_send = []

    for geofence in geofences:
        if is_within_geofence(user_location, (geofence["center_lat"], geofence["center_long"]), geofence["radius_meters"]):
            alerts_to_send.append(geofence)
            # Check if alert has already been sent
            if not has_alert_been_sent(location.user_id, geofence["id"]):
                mark_alert_as_sent(location.user_id, geofence["id"])

    return JSONResponse(content={"alerts": alerts_to_send},status_code=200)

@app.post("/add-geofence")
async def add_geofence(geofence: Geofence):
    '''
    For Admin
    Adds a new geofence to the database.
    '''
    try:
        data=geofence.model_dump()
        loc=get_lat_long_opencage(data["location"])
        loc["radius_meters"]=data["radius_meters"]
        response=supabase.insert_geofence(loc)
        if response:
            return JSONResponse(content={"message": "Geofence added successfully"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Failed to add geofence"}, status_code=400)
    except ValidationError as e:
        print(e)
        return JSONResponse(content={"message":e},status_code=500)  
                
@app.get("/geofence_coordinates")
async def get_geofence_coordinates():
    '''
    For Admin
    Retrieves all geofence coordinates from the Supabase database.
    '''
    geofences = supabase.get_geofence()
    return JSONResponse(content={"geofences": geofences}, status_code=200)

@app.get("/safe_route")
async def safe_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    """
    To get a safe route between start and end points.
    """
    start_coords = (start_lat, start_lon)
    end_coords = (end_lat, end_lon)
    
    # Get the safest route after removing geofenced coordinates
    safe_route = ors.get_safest_route(start_coords, end_coords)
    
    if not safe_route:
        raise HTTPException(status_code=404, detail="Safe route could not be found.")
    
    return JSONResponse(content={"message":"Shortest route calculated","safe_route":safe_route},status_code=200)

@app.post("/sos-trigger")
async def trigger_sos(user_id: str, latitude:float, longitude:float, username:str, background_tasks: BackgroundTasks):
    alert_data={
        "user_id":user_id,
        "latitude":latitude,
        "longitude":longitude,
        "is_active":"true"
    }
    sos_alert_id = supabase.insert_sos_alerts(alert_data)
    print(sos_alert_id)
    user={
        "user_id":user_id,
        "username":username,
        "latitude":latitude,
        "longitude":longitude
    }
    background_tasks.add_task(notify_contacts, user)
    return {"message": "SOS alert triggered", "alert_id": sos_alert_id}

@app.get("/sos-alert/{alert_id}")
async def get_sos_data(alert_id: int):
    '''
    For Admin
    Retrieves SOS alert data from the Supabase database.
    '''
    res=supabase.get_sos_alerts(alert_id)
    if not res:
        raise HTTPException(status_code=404, detail="No alerts found")
    
    return res


@app.websocket("/ws/stream/{user_id}/{alert_id}")
async def stream_media(websocket: WebSocket, user_id: str, alert_id: int):
    """
    WebSocket endpoint to stream media and upload to Supabase.
    """
    await websocket.accept()
    file_name = f"{user_id}_{alert_id}.mp4"
    local_path = f"./{file_name}"

    try:
        # Open a file for writing the incoming stream data
        async with aiofiles.open(local_path, 'wb') as out_file:
            while True:
                try:
                    data = await websocket.receive_bytes()
                    await out_file.write(data)
                except WebSocketDisconnect:
                    print("WebSocket connection closed.")
                    break
    except Exception as e:
        await websocket.close()
        return JSONResponse(content={"message": f"Error writing file: {e}"}, status_code=500)

    # Attempt to upload the recording to Supabase after WebSocket closes
    try:
        print(f"Attempting to upload {local_path} to Supabase.")
        upload_success = supabase.upload_recordings(local_path, file_name)
        if upload_success:
            os.remove(local_path)  # Delete the local file if uploaded successfully
            print("Successfully uploaded the file.")

        else:
            print("Failed to upload the file.")
    except Exception as e:
        print(f"Error during upload: {e}")
    finally:
        # Close only if the WebSocket connection is open
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)