#!/usr/bin/env python3
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import os
import uuid

app = FastAPI()
STORAGE_PATH = "media_service/storage"
os.makedirs(STORAGE_PATH, exist_ok=True)

# Endpoints
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(STORAGE_PATH, f"{file_id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"file_url": f"http://localhost:8005/media/{file_id}"}

@app.get("/media/{file_id}")
def get_file(file_id: str):
    for filename in os.listdir(STORAGE_PATH):
        if filename.startswith(file_id):
            return FileResponse(os.path.join(STORAGE_PATH, filename))
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)