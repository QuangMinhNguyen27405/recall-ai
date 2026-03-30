import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}

def start():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)