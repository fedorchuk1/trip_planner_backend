from pydantic import BaseModel, Field
from typing import Optional


class Restaurant(BaseModel):
    name: str = Field(..., description="Name of the restaurant")
    location: str = Field(..., description="Location of the restaurant")
    description: str = Field(..., description="Description of the restaurant")
    cousine: str = Field(..., description="Cousine of the restaurant")
    rating: Optional[float] = Field(..., description="Rating of the activity")


class Activity(BaseModel):
    name: str = Field(..., description="Name of the activity")
    location: str = Field(..., description="Location of the activity")
    description: str = Field(..., description="Description of the activity")
    why_its_suitable: str = Field(..., description="Why it's suitable for the traveler")


class DayPlan(BaseModel):
	date: str = Field(..., description="Date of the day")
	activities: list[Activity] = Field(..., description="List of activities to visit")
	restaurants: Optional[list[Restaurant]] = Field(None, description="List of restaurants to visit")


class CityPlan(BaseModel):
    city: str = Field(..., description="City of the plan")
    date_range: str = Field(..., description="Date range of the plan")
    day_plans: list[DayPlan] = Field(..., description="List of day plans")


class Itinerary(BaseModel):
    name: str = Field(..., description="Name of the itinerary, something funny")
    city_plans: list[CityPlan] = Field(..., description="List of city plans")
