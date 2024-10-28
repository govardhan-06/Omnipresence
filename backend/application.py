from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import sys,uvicorn
from src.utils.exception import customException
from src.utils.logger import logging
from starlette.responses import JSONResponse
from src.database.supabase_config import Supabase
from src.database.firebase_config import Firebase
from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import Enum
import ipfshttpclient, json, requests

app = FastAPI()
firebase=Firebase()
supabase=Supabase()

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

@app.post("/report-incident/")
async def report_incident(incident: Incident):
    # Convert to JSON string
    data_json = json.dumps(incident.model_dump())
    
    # Add JSON data to IPFS
    response = requests.post("http://127.0.0.1:5001/api/v0/add", files={"file": data_json})
    
    if response.status_code == 200:
        res = response.json()["Hash"]  # IPFS returns a hash for the stored data
        # Add the hash to the database
        if(supabase.insert_ipfs_hash(res)):
            return JSONResponse(content={"message":"Data inserted to IPFS and hash inserted to supabase","ipfs_hash": res},status_code=200)
        else:
            return JSONResponse(content={"message":"Failed to insert hash to supabase"},status_code=500)

    else:
        print("Failed to add data to IPFS:", response.status_code)
        return JSONResponse(content={"message":"Failed to insert data to IPFS","ipfs_hash": None},status_code=500)

@app.get("/retrieve-incident")
async def retrieve_incident():
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

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

