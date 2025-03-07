#!/usr/bin/env python3
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import jwt

app = FastAPI()
engine = create_engine("sqlite:///user_service/db.sqlite")
Base = declarative_base()
Session = sessionmaker(bind=engine)
SECRET_KEY = "secret_key"
security = HTTPBearer()

# Model
class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    bio = Column(String, nullable=True)

Base.metadata.create_all(engine)

# Authentication
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoints
@app.post("/profiles")
def create_profile(profile_data: dict):
    session = Session()
    profile = Profile(user_id=profile_data["user_id"], bio="")
    session.add(profile)
    session.commit()
    session.close()
    return {"message": "Profile created"}

@app.get("/profiles/{user_id}")
def get_profile(user_id: int, current_user: int = Depends(get_current_user)):
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    session = Session()
    profile = session.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    session.close()
    return {"user_id": user_id, "bio": profile.bio}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)