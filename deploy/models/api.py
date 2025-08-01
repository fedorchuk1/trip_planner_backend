from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from trip_planner.models.general import TravelerInput
from trip_planner.models.itinerary import Itinerary
from trip_planner.models.flights import FlightsPlannerResponse
from trip_planner.models.hotels import HotelsPlannerResponse

class PlanItineraryRequest(BaseModel):
    """Request model for the plan_itinerary endpoint"""
    traveler_input: TravelerInput = Field(..., description="Travel planning input data")


class RefineItineraryRequest(PlanItineraryRequest):
    """Request model for the refine_itinerary endpoint"""
    itinerary: Itinerary = Field(..., description="Generated itinerary")
    user_feedback: str = Field(..., description="User feedback on the itinerary")


class PlanItineraryResponse(BaseModel):
    """Response model for the plan_itinerary endpoint"""
    itinerary: Itinerary = Field(..., description="Generated itinerary")
    message: str = Field(..., description="Status message")

class FlightsRequest(BaseModel):
    """Request model for the flights endpoint"""
    departure_city: str = Field(..., description="Departure city")
    itinerary: Itinerary = Field(..., description="Itinerary")

class FlightsResponse(BaseModel):
    """Response model for the flights endpoint"""
    flights_plan: FlightsPlannerResponse = Field(..., description="Flights plan")
    message: str = Field(..., description="Status message")

class HotelsRequest(BaseModel):
    """Request model for the hotels endpoint"""
    itinerary: Itinerary = Field(..., description="Itinerary")

class HotelsResponse(BaseModel):
    """Response model for the hotels endpoint"""
    hotels_plan: HotelsPlannerResponse = Field(..., description="Hotels plan")
    message: str = Field(..., description="Status message")


class HotelsAndFlightsRequest(BaseModel):
    """Request model for the hotels and flights endpoint"""
    itinerary: Itinerary = Field(..., description="Itinerary")
    departure_city: str = Field(..., description="Departure city")

class HotelsAndFlightsResponse(BaseModel):
    """Response model for the hotels and flights endpoint"""
    hotels_plan: HotelsPlannerResponse = Field(..., description="Hotels plan")
    flights_plan: FlightsPlannerResponse = Field(..., description="Flights plan")
    message: str = Field(..., description="Status message")
