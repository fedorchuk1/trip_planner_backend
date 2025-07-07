import os
from typing import Any, Type

from agno.tools import tool
from pydantic import BaseModel, Field
from serpapi import GoogleSearch

from enum import Enum

class FlightType(Enum):
    ROUND_TRIP = "ROUND_TRIP"
    ONE_WAY = "ONE_WAY"

    @property
    def type_int(self) -> int:
        return 1 if self == FlightType.ROUND_TRIP else 2

class Flight(BaseModel):
    departure_airport: str
    arrival_airport: str
    departure_date: str
    return_date: str
    flight_type: FlightType

@tool(
    name="FlightsSearchTool",
    description="Given a departure and arrival airport, departure and return date, returns available flights. Use ROUND_TRIP type of flight if the trip contains only one city in the itinerary.",
    show_result=True,
    cache_results=False
)
def get_flights(
    departure_airport: str,
    arrival_airport: str,
    departure_date: str,
    return_date: str,
    flight_type: FlightType,
) -> dict:
    """
    This function, given a departure and arrival airport, departure and return date, returns available flights.
    Use ROUND_TRIP type of flight if the trip contains only one city in the itinerary.

    Args:
        departure_airport (str): The departure airport IATA code
        arrival_airport (str): The arrival airport IATA code
        departure_date (str): The departure date
        return_date (str): The return date
        flight_type (FlightType): The type of flight

    Returns:
        dict: The search results
    """

    params = {
            "engine": "google_flights",
            "type": flight_type.type_int,
            "departure_id": departure_airport,
            "arrival_id": arrival_airport,
            "outbound_date": departure_date,
            "return_date": return_date,
            "currency": "USD",
            "hl": "en",
            "api_key": os.getenv("SERPAPI_KEY")
        }

    search_results = GoogleSearch(params)
    return search_results.get_dict()