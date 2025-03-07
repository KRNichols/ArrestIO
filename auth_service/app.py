#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt
import jwt
from datetime import datetime, timedelta

app = FastAPI()
engine = create_engine("sqlite:///auth_service/db.sqlite")
Base = declarative_base()
Session = sessionmaker(bind=engine)
SECRET_KEY = "secret_key"  # In production, use env variable

# Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)

Base.metadata.create_all(engine)

# Pydantic schemas
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

# Endpoints
@app.post("/register")
def register(request: RegisterRequest):
    session = Session()
    if session.query(User).filter((User.username == request.username) | (User.email == request.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already exists")
    password_hash = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt())
    user = User(username=request.username, email=request.email, password_hash=password_hash)
    session.add(user)
    session.commit()
    user_id = user.id
    session.close()
    # Notify User Management Service
    import requests
    requests.post("http://localhost:8001/profiles", json={"user_id": user_id, "username": request.username, "email": request.email})
    return {"message": "User created"}

@app.post("/login")
def login(request: LoginRequest):
    session = Session()
    user = session.query(User).filter(User.username == request.username).first()
    if not user or not bcrypt.checkpw(request.password.encode(), user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"sub": user.id, "exp": datetime.utcnow() + timedelta(hours=24)}, SECRET_KEY, algorithm="HS256")
    session.close()
    return {"token": token}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)