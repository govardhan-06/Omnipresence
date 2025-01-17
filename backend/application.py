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
import json, requests
from src.geofences import is_within_geofence, has_alert_been_sent, mark_alert_as_sent, get_lat_long_opencage
from src.sos_workflow import notify_contacts
from src.safe_route import OpenRouteService
from typing import List
from src.services.pinata_config import Pinata
from src.pipelines.audio_processing import Audio_Processing
import asyncio

app = FastAPI()
firebase=Firebase()
supabase=Supabase()
ors=OpenRouteService()
pinata=Pinata()
audio=Audio_Processing()

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

async def trigger_sos_logic(user_id: str, latitude: float, longitude: float, username: str, background_tasks: BackgroundTasks):
    """
    Triggers an SOS event logic (insert alert data and send notifications).
    """
    alert_data = {
        "user_id": user_id,
        "latitude": latitude,
        "longitude": longitude,
    }
    sos_alert_id = (supabase.insert_sos_alerts(alert_data)).data
    sos_alert_id = sos_alert_id[0]["id"]
    
    user = {
        "user_id": user_id,
        "username": username,
        "latitude": latitude,
        "longitude": longitude
    }
    
    await notify_contacts(user)
    
    return sos_alert_id

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

    response = pinata.upload_to_pinata(data_dict)

    if response.status_code == 200:
            # Parse the JSON response
            res = response.json()["IpfsHash"]  # IPFS returns a hash for the stored data
            # Add the hash to the database
            if(supabase.insert_emergency_contact_hash(user_id,res)):
                return JSONResponse(content={"message": "Family details added successfully","response":res}, status_code=200)
            else:
                return JSONResponse(content={"message":"Failed to add family details to supabase"},status_code=500)
    else:
        return JSONResponse(content={"message":"Failed to add family details to Pinata","error":response.text,"pinata_status_code":response.status_code},status_code=500)

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
        retrieved_response = pinata.get_data_from_ipfs(ipfs_hash)
        
        # Check if data retrieval was successful
        if retrieved_response.status_code == 200:
            data_dict = retrieved_response.json()
            retrieved_data.append({
                "ipfs_hash": ipfs_hash,
                "data": data_dict
            })
        else:
            retrieved_data.append({
                "ipfs_hash": ipfs_hash,
                "data": "Failed to retrieve data",
                "status_code": retrieved_response.status_code,
                "error": retrieved_response.text
            })

    # Return all retrieved data in a single JSON response
    return JSONResponse(content={"message": "Data retrieved from IPFS", "retrieved_data": retrieved_data}, status_code=200)

@app.post("/report-incident")
async def report_incident(incident: Incident,uid:Optional[str]=None):
    '''
    Crowdsourcing of incidents
    '''
    # Convert to JSON string
    data_dict = incident.model_dump()
    location=data_dict["location"]
    print(data_dict)
    try:
        if data_dict["uid"]:
            pass
    except:
        data_dict["uid"]=None

    response = pinata.upload_to_pinata(data_dict)

    geofence=get_lat_long_opencage(location)
    geofence["radius_meters"]=500
    
    if response.status_code == 200:
        res = response.json()["IpfsHash"]  # IPFS returns a hash for the stored data
        # Add the hash to the database
        if(supabase.insert_ipfs_hash(res)):
            if(supabase.insert_geofence(geofence)):
                return JSONResponse(content={"message":"Data inserted to IPFS and hash + geofence inserted to supabase","ipfs_hash": res},status_code=200)
            else:
                return JSONResponse(content={"message":"Data inserted to IPFS and hash inserted to supabase. Failed to insert geofence coordinates","ipfs_hash": res},status_code=200)
        else:
            return JSONResponse(content={"message":"Failed to insert hash to supabase"},status_code=500)

    else:
        print("Failed to add data to Pinata:", response.status_code)
        return JSONResponse(content={"message":"Failed to insert data to Pinata","ipfs_hash": None,"error":response.text,"pinata_status_code":response.status_code},status_code=500)

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
        try:
            retrieved_response = pinata.get_data_from_ipfs(ipfs_hash)
            # Check if data retrieval was successful
            if retrieved_response.status_code == 200:
                data_dict = retrieved_response.json()
                retrieved_data.append({
                    "ipfs_hash": ipfs_hash,
                    "data": data_dict
                })
            else:
                retrieved_data.append({
                    "ipfs_hash": ipfs_hash,
                    "data": "Failed to retrieve data",
                    "status_code": retrieved_response.status_code,
                    "error": retrieved_response.text
                })
        except ConnectionError as e:
            # Handle the connection error
            raise HTTPException(status_code=500, detail="Failed to connect to IPFS")
        except Exception as e:
            # Handle any other exceptions
            raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/safe_route")
async def safe_route(start:str, end:str):
    """
    To get a safe route between start and end points.
    """
    loc=get_lat_long_opencage(start)
    start_lat=loc["center_lat"]
    start_lon=loc["center_long"]
    loc=get_lat_long_opencage(end)
    end_lat=loc["center_lat"]
    end_lon=loc["center_long"]
    start_coords = (start_lat, start_lon)
    end_coords = (end_lat, end_lon)
    
    # Get the safest route after removing geofenced coordinates
    safe_route = ors.get_safest_route(start_coords, end_coords)
    
    if not safe_route:
        raise HTTPException(status_code=404, detail="Safe route could not be found.")
    
    return JSONResponse(content={"message":"Shortest route calculated","safe_route":safe_route},status_code=200)

@app.post("/sos-trigger")
async def trigger_sos(user_id: str, latitude:float, longitude:float, username:str, background_tasks: BackgroundTasks):
    '''
    Triggers an SOS event.
    '''
    alert_data={
        "user_id":user_id,
        "latitude":latitude,
        "longitude":longitude,
    }
    sos_alert_id = (supabase.insert_sos_alerts(alert_data)).data
    sos_alert_id=sos_alert_id[0]["id"]
    user={
        "user_id":user_id,
        "username":username,
        "latitude":latitude,
        "longitude":longitude
    }
    background_tasks.add_task(notify_contacts, user)
    return {"message": "SOS alert triggered", "alert_id": sos_alert_id}

@app.get("/sos-alert/{user_id}/{alert_id}")
async def get_sos_data(user_id:str, alert_id: int):
    '''
    For Admin
    Retrieves SOS alert data from the Supabase database.
    '''
    res=supabase.get_sos_alerts(alert_id)[0]
    rec_url,audio_url=supabase.get_recording_URL(alert_id,user_id)
    res["video_stream_url"]=rec_url
    res["audio_stream_url"]=audio_url
    if not res:
        raise HTTPException(status_code=404, detail="No alerts found")
    
    return res

@app.websocket("/ws/stream/{user_id}/{alert_id}/{file_format}")
async def stream_media(websocket: WebSocket, user_id: str, alert_id: int, file_format:str):
    """
    WebSocket endpoint to stream media and upload to Supabase.
    """
    await websocket.accept()
    file_name = f"{user_id}_{alert_id}.{file_format}"
    local_path = f"./{file_name}"

    try:
        # Open a file for writing the incoming stream data
        async with aiofiles.open(local_path, 'wb') as out_file:
            while True:
                try:
                    data = await websocket.receive_bytes()
                    await out_file.write(data)
                    await websocket.send_json({
                        "message":"Video transmitted successfully"
                    })
                except WebSocketDisconnect:
                    print("WebSocket connection closed.")
                    break
    except Exception as e:
        await websocket.close()
        await websocket.send_json({
                        "message":"Failed to transmit video"
                    })

@app.websocket("/ws/audio-stream/{user_id}/{username}/{latitude}/{longitude}")
async def stream_media(websocket: WebSocket, user_id: str, latitude: float, longitude: float, username: str, background_tasks: BackgroundTasks):
    """
    WebSocket endpoint to analyze the real-time audio from user device
    """
    await websocket.accept()
    file_name = f"{user_id}.wav"
    local_path = f"{file_name}"

    try:
        # Open a file for writing the incoming stream data
        async with aiofiles.open(local_path, 'wb') as out_file:
            while True:
                try:
                    data = await websocket.receive_bytes()
                    print("Received data chunk:", len(data))

                    await out_file.write(data)

                    # Ensure the file is flushed and ready for processing
                    await out_file.flush()
                    print("Audio file received from client")

                    # Process the audio only when the file is ready
                    res = audio.process_audio(local_path)
                    print(res)

                    if res == 'Scream':
                        # File should only be deleted after it's completely processed
                        print("SOS detected...")

                        # Send notification to frontend
                        await websocket.send_json({
                            "sos_triggered": None,
                            "message": "Potential SOS detected! Please confirm if help is needed."
                        })

                        response = await websocket.receive_json()
                        print("Response from client:", response)

                        if response.get('action') == 'trigger_sos':
                                    print("SOS action triggered by the client.")
                                    sos_alert_id = await trigger_sos_logic(user_id, latitude, longitude, username, background_tasks)
                                    await websocket.send_json({
                                        "sos_triggered": True,
                                        "alert_id": sos_alert_id,
                                        "message": "SOS alert has been triggered, help is on the way!"
                                    })

                        else:
                            print("No SOS action from the client.")
                            await websocket.send_json({
                                "sos_triggered": False,
                                "message": "No SOS triggered. Everything is safe."
                            })

                    else:
                        print("Safe surroundings...")
                        # os.remove(local_path)
                        await websocket.send_json({
                            "sos_triggered": False,
                            "message": "Everything is safe."
                        })

                except WebSocketDisconnect:
                    print("WebSocket connection closed.")
                    break
    except Exception as e:
        await websocket.close()
        return JSONResponse(content={"message": f"Error writing file: {e}"}, status_code=500)

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)