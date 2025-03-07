#!/usr/bin/env python3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import jwt

app = FastAPI()
engine = create_engine("sqlite:///content_service/db.sqlite")
Base = declarative_base()
Session = sessionmaker(bind=engine)
SECRET_KEY = "secret_key"
security = HTTPBearer()

# Model
class Content(Base):
    __tablename__ = "content"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    title = Column(String)
    body = Column(String)

Base.metadata.create_all(engine)

# Authentication
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Pydantic schema
class ContentRequest(BaseModel):
    title: str
    body: str

# Endpoints
@app.post("/content")
def create_content(request: ContentRequest, user_id: int = Depends(get_current_user)):
    session = Session()
    content = Content(user_id=user_id, title=request.title, body=request.body)
    session.add(content)
    session.commit()
    session.close()
    # Notify Search Service (simplified)
    import requests
    requests.post("http://localhost:8006/index/content", json={"id": content.id, "title": request.title, "body": request.body})
    return {"message": "Content created"}

@app.get("/content/{content_id}")
def get_content(content_id: int):
    session = Session()
    content = session.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    session.close()
    return {"title": content.title, "body": content.body}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)