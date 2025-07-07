from pydantic import BaseModel, Field


class Flight(BaseModel):
    departure_airport: str = Field(..., description="Departure airport")
    arrival_airport: str = Field(..., description="Arrival airport")
    departure_timestamp: str = Field(..., description="Departure timestamp")
    arrival_timestamp: str = Field(..., description="Arrival timestamp")
    duration: str = Field(..., description="Duration of the flight")
    airline: str = Field(..., description="Airline")
    flight_number: str = Field(..., description="Flight number")
    price: str = Field(..., description="Price of the flight")
    aircraft: str = Field(..., description="Aircraft of the flight")
    booking_link: str = Field(..., description="Booking link of the flight")


class FlightsPlan(BaseModel):
    flights: list[Flight] = Field(..., description="List of flights")
