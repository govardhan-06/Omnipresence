from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import sys,uvicorn
from backend.src.utils.exception import customException
from backend.src.utils.logger import logging
from starlette.responses import JSONResponse

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    '''
    This function is used to redirect to the swaggerUI page.
    '''
    return RedirectResponse(url="/docs")

@app.post("/create_user")
async def create_user(firstName:str,lastName:str,phone:str,sex:str,emer_num1:str,emer_num2:str=None,emer_num3:str=None):
    '''
    This function is used to handle the user profile setup.
    '''
    try:
        logging.info("Getting the user details...")
        return JSONResponse(content={"status":"success","message":"User created successfully"},status_code=200)

    except Exception as e:
        raise customException(e,sys)

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

