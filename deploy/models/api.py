from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from trip_planner.models.general import TravelerInput
from trip_planner.models.itinerary import Itinerary
from trip_planner.models.flights import FlightsPlan


class PlanItineraryRequest(BaseModel):
    """Request model for the plan_itinerary endpoint"""
    conversation_id: Optional[str] = Field(None, description="Conversation ID for tracking")
    traveler_input: TravelerInput = Field(..., description="Travel planning input data")


class PlanItineraryResponse(BaseModel):
    """Response model for the plan_itinerary endpoint"""
    conversation_id: str = Field(..., description="Conversation ID for tracking")
    itinerary: Itinerary = Field(..., description="Generated itinerary")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(..., description="Response timestamp")

class FlightsRequest(BaseModel):
    """Request model for the flights endpoint"""
    conversation_id: Optional[str] = Field(None, description="Conversation ID for tracking")
    departure_date: str = Field(..., description="Departure date")
    arrival_date: str = Field(..., description="Arrival date")
    departure_city: str = Field(..., description="Departure city")
    arrival_city: str = Field(..., description="Arrival city")

class FlightsResponse(BaseModel):
    """Response model for the flights endpoint"""
    conversation_id: str = Field(..., description="Conversation ID for tracking")
    flights_plan: FlightsPlan = Field(..., description="Flights plan")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(..., description="Response timestamp")