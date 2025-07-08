from typing import Any, Optional

from pydantic import BaseModel, Field, field_serializer, model_validator
from datetime import datetime


from .flights import FlightsPlan
from .itinerary import Itinerary


class TravelerInput(BaseModel):
    country: str = Field(..., description="Country of the trip")
    cities: list[str] = Field(..., description="Cities of the trip")
    arrival_date: str = Field(..., description="Arrival date of the trip in YYYY-MM-DD format")
    departure_date: str = Field(..., description="Departure date of the trip in YYYY-MM-DD format")
    age: int = Field(..., description="Age of the traveler")
    preferences: Optional[list[str]] = Field(None, description="Preferences of the traveler")

    @field_serializer("preferences")
    def serialize_preferences(self, preferences: Optional[list[str]], _info: Any) -> str:
        return ", ".join(preferences) if preferences else ""
    
    @model_validator(mode='after')
    def validate_dates(self) -> 'TravelerInput':
        try:
            arrival = datetime.strptime(self.arrival_date, "%Y-%m-%d")
            departure = datetime.strptime(self.departure_date, "%Y-%m-%d")
            
            if arrival > departure:
                raise ValueError("Arrival date cannot be after departure date")
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
            raise e
        
        return self


class TripPlannerState(BaseModel):
    traveler_input: Optional[TravelerInput] = None
    itinerary: Optional[Itinerary] = None
    flights: Optional[FlightsPlan] = None


class TripPlanResult(BaseModel):
    itinerary: Itinerary = Field(..., description="Complete travel itinerary with activities and restaurants")
    flights: FlightsPlan = Field(..., description="Flight booking information and details")
