#!/usr/bin/env python3
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
index = {}  # {id: {"title": str, "body": str}}

# Pydantic schema
class IndexRequest(BaseModel):
    id: int
    title: str
    body: str

# Endpoints
@app.post("/index/content")
def index_content(request: IndexRequest):
    index[request.id] = {"title": request.title, "body": request.body}
    return {"message": "Indexed"}

@app.get("/search")
def search(query: str):
    results = [data for data in index.values() if query.lower() in data["title"].lower() or query.lower() in data["body"].lower()]
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)