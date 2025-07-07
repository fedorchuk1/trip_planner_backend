import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException

from trip_planner.itinerary_crew import run_team
from trip_planner.flights_crew import run as run_flights_team
from trip_planner.models.itinerary import Itinerary
from trip_planner.models.flights import FlightRoutePlan
from .models.api import PlanItineraryRequest, PlanItineraryResponse, FlightsRequest, FlightsResponse

app = FastAPI(title="Trip Planner API", version="0.1.0")

@app.post("/flights", response_model=FlightsResponse)
async def get_flights(request: FlightsRequest):
    """Get flights for a given itinerary. This shit can fail in response parsing."""
    
    conversation_id = request.conversation_id or str(uuid.uuid4())
    flight_cities = [request.departure_city]
    flight_dates = []
    for plan in request.itinerary.city_plans:
        flight_cities.append(plan.city)
        flight_dates.append(plan.date_range.split("to")[0].strip())
    flight_dates.append(request.itinerary.city_plans[-1].date_range.split("to")[1].strip())

    
    flights_plan: FlightRoutePlan = await run_flights_team(flight_cities, flight_dates)
   
    return FlightsResponse(
        conversation_id=conversation_id, 
        flights_plan=flights_plan, 
        message="Flights found successfully", 
        timestamp=datetime.now())

@app.post("/plan_itinerary", response_model=PlanItineraryResponse)
async def plan_itinerary(request: PlanItineraryRequest):
    """Plan a trip using the itinerary planner crew"""
    
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # try:
    # Create itinerary crew and process
    crew_inputs = {
        'country': request.traveler_input.country,
        'cities': ', '.join(request.traveler_input.cities),
        'date_range': request.traveler_input.date_range,
        'age': request.traveler_input.age,
        'preferences': ', '.join(request.traveler_input.preferences or []),
        'constraints': ', '.join(request.traveler_input.constraints or [])
    }
    
    itinerary: Itinerary = await run_team(crew_inputs)

    return PlanItineraryResponse(
        conversation_id=conversation_id,
        itinerary=itinerary,
        message="Trip planning completed successfully",
        timestamp=datetime.now()
    )
        
    # except Exception as e:
    #     print(e)
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Error processing itinerary: {str(e)}"
    #     )
