import os
from typing import Any, Type

from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from serpapi import GoogleSearch

from enum import Enum


class FlightType(Enum):
    ROUND_TRIP = "ROUND_TRIP"
    ONE_WAY = "ONE_WAY"

    @property
    def type_int(self) -> int:
        return 1 if self == FlightType.ROUND_TRIP else 2


class FlightSearchToolSchema(BaseModel):
    departure_airport: str = Field(..., description="The departure airport IATA code")
    arrival_airport: str = Field(..., description="The arrival airport IATA code")
    departure_date: str = Field(..., description="The departure date")
    return_date: str = Field(..., description="The return date")
    flight_type: FlightType = Field(FlightType.ONE_WAY, description="The type of flight")


class FlightsSearchTool(BaseTool):
    name: str = "FlightsSearchTool"
    description: str = """
        Given a departure and arrival airport, departure and return date, returns available flights
        Use ROUND_TRIP if the trip contains only one city in the itinerary.
    """
    args_schema: Type[BaseModel] = FlightSearchToolSchema

    def _run(self, **kwargs: Any) -> Any:
        departure_airport = kwargs.get("departure_airport")
        arrival_airport = kwargs.get("arrival_airport")
        departure_date = kwargs.get("departure_date")
        return_date = kwargs.get("return_date")
        flight_type = FlightType(kwargs.get("flight_type"))

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
