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
from pydantic import BaseModel
from typing import Optional
from enum import Enum

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

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

