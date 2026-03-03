from fastapi import APIRouter, HTTPException
from src.api.models.schemas import (
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventResponse,
    CalendarEventsListResponse,
)
from src.database import create_event, get_events, update_event, delete_event

router = APIRouter()


@router.get("/calendar", response_model=CalendarEventsListResponse)
async def list_events(month: int = 1, year: int = 2026):
    events = get_events(month, year)
    return CalendarEventsListResponse(events=events)


@router.post("/calendar", response_model=CalendarEventResponse)
async def add_event(data: CalendarEventCreate):
    event = create_event(
        title=data.title,
        date=data.date,
        event_type=data.event_type,
        description=data.description,
        time=data.time,
    )
    return CalendarEventResponse(**event)


@router.put("/calendar/{event_id}", response_model=CalendarEventResponse)
async def edit_event(event_id: int, data: CalendarEventUpdate):
    event = update_event(
        event_id,
        title=data.title,
        description=data.description,
        date=data.date,
        time=data.time,
        event_type=data.event_type,
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return CalendarEventResponse(**event)


@router.delete("/calendar/{event_id}")
async def remove_event(event_id: int):
    if not delete_event(event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return {"detail": "Event deleted"}
