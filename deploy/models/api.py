from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from trip_planner.models.general import TravelerInput
from trip_planner.models.itinerary import Itinerary


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