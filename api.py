# A standalone RESTful server used to send simulated navigation data to a remote comm unit for testing. 
import uvicorn
from fastapi import FastAPI

app = FastAPI()

def start_server(): 
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        log_level="debug",
        reload=True,
    )

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/get_nextpos")
async def nextpos():
    return {"r": "r",
            "c": "c"
            }

if __name__ == "__main__":
    start_server()   

# To execute uvicorn server via terminal run the following command
# uvicorn api:app --reload