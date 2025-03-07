#!/usr/bin/env python3
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()
engine = create_engine("sqlite:///notification_service/db.sqlite")
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Model
class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    message = Column(String)

Base.metadata.create_all(engine)

# Pydantic schema
class NotificationRequest(BaseModel):
    user_id: int
    message: str

# Endpoints
@app.post("/notifications")
def create_notification(request: NotificationRequest):
    session = Session()
    notification = Notification(user_id=request.user_id, message=request.message)
    session.add(notification)
    session.commit()
    session.close()
    # Notify Real-time Service
    import requests
    requests.post("http://localhost:8007/notify", json={"user_id": request.user_id, "message": request.message})
    # Email sending omitted (requires SMTP setup)
    return {"message": "Notification created"}

@app.get("/notifications/{user_id}")
def get_notifications(user_id: int):
    session = Session()
    notifications = session.query(Notification).filter(Notification.user_id == user_id).all()
    session.close()
    return [{"message": n.message} for n in notifications]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)