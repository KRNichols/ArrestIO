#!/usr/bin/env python3
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()
engine = create_engine("sqlite:///analytics_service/db.sqlite")
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Model
class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    event_type = Column(String)
    timestamp = Column(String)

Base.metadata.create_all(engine)

# Pydantic schema
class EventRequest(BaseModel):
    user_id: int
    event_type: str
    timestamp: str

# Endpoints
@app.post("/events")
def log_event(request: EventRequest):
    session = Session()
    event = Event(user_id=request.user_id, event_type=request.event_type, timestamp=request.timestamp)
    session.add(event)
    session.commit()
    session.close()
    return {"message": "Event logged"}

@app.get("/analytics/active-users")
def get_active_users():
    session = Session()
    count = session.query(Event).distinct(Event.user_id).count()
    session.close()
    return {"active_users": count}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)