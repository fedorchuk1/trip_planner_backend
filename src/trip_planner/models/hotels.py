import os
from typing import Any, Type, Optional, List

from agno.tools import tool
from pydantic import BaseModel, Field
from serpapi import GoogleSearch

from enum import Enum

class AirbnbListing(BaseModel):
    name: str
    description: str
    address: Optional[str] = None
    price: Optional[str] = None
    url: Optional[str] = None

class CityHotelListings(BaseModel):
    city: str
    dates: str
    listings: List[AirbnbListing]

class HotelsPlannerResponse(BaseModel):
    hotels_plans: List[CityHotelListings]