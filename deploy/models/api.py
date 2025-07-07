from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from trip_planner.models.general import TravelerInput
from trip_planner.models.itinerary import Itinerary
from trip_planner.models.flights import FlightsPlannerResponse
from trip_planner.models.hotels import HotelsPlannerResponse

class PlanItineraryRequest(BaseModel):
    """Request model for the plan_itinerary endpoint"""
    conversation_id: Optional[str] = Field(None, description="Conversation ID for tracking")
    traveler_input: TravelerInput = Field(..., description="Travel planning input data")


class RefineItineraryRequest(PlanItineraryRequest):
    """Request model for the refine_itinerary endpoint"""
    itinerary: Itinerary = Field(..., description="Generated itinerary")


class PlanItineraryResponse(BaseModel):
    """Response model for the plan_itinerary endpoint"""
    conversation_id: str = Field(..., description="Conversation ID for tracking")
    itinerary: Itinerary = Field(..., description="Generated itinerary")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(..., description="Response timestamp")

class FlightsRequest(BaseModel):
    """Request model for the flights endpoint"""
    conversation_id: Optional[str] = Field(None, description="Conversation ID for tracking")
    departure_city: str = Field(..., description="Departure city")
    itinerary: Itinerary = Field(..., description="Itinerary")

class FlightsResponse(BaseModel):
    """Response model for the flights endpoint"""
    conversation_id: str = Field(..., description="Conversation ID for tracking")
    flights_plan: FlightsPlannerResponse = Field(..., description="Flights plan")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(..., description="Response timestamp")

class HotelsRequest(BaseModel):
    """Request model for the hotels endpoint"""
    conversation_id: Optional[str] = Field(None, description="Conversation ID for tracking")
    itinerary: Itinerary = Field(..., description="Itinerary")

class HotelsResponse(BaseModel):
    """Response model for the hotels endpoint"""
    conversation_id: str = Field(..., description="Conversation ID for tracking")
    hotels_plan: HotelsPlannerResponse = Field(..., description="Hotels plan")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(..., description="Response timestamp")


class HotelsAndFlightsRequest(BaseModel):
    """Request model for the hotels and flights endpoint"""
    conversation_id: Optional[str] = Field(None, description="Conversation ID for tracking")
    itinerary: Itinerary = Field(..., description="Itinerary")
    departure_city: str = Field(..., description="Departure city")

class HotelsAndFlightsResponse(BaseModel):
    """Response model for the hotels and flights endpoint"""
    conversation_id: str = Field(..., description="Conversation ID for tracking")
    hotels_plan: HotelsPlannerResponse = Field(..., description="Hotels plan")
    flights_plan: FlightsPlannerResponse = Field(..., description="Flights plan")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(..., description="Response timestamp")