from typing import Optional

from pydantic import BaseModel, Field

from .flights import FlightsPlan
from .itinerary import Itinerary


class TravelerInput(BaseModel):
    country: str = Field(..., description="Country of the trip")
    cities: list[str] = Field(..., description="Cities of the trip")
    date_range: str = Field(..., description="Date range of the trip")
    age: int = Field(..., description="Age of the traveler")
    preferences: Optional[list[str]] = Field(None, description="Preferences of the traveler")
    constraints: Optional[list[str]] = Field(None, description="Constraints of the traveler")


class TripPlannerState(BaseModel):
    traveler_input: Optional[TravelerInput] = None
    itinerary: Optional[Itinerary] = None
    flights: Optional[FlightsPlan] = None


class TripPlanResult(BaseModel):
    itinerary: Itinerary = Field(..., description="Complete travel itinerary with activities and restaurants")
    flights: FlightsPlan = Field(..., description="Flight booking information and details")
