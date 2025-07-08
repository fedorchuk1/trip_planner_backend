import asyncio
from textwrap import dedent

from fastapi import FastAPI, HTTPException
from phoenix.otel import register

from trip_planner.itinerary_crew import run_team
from trip_planner.flights_crew import run as run_flights_team
from trip_planner.hotels_crew import run as run_hotels_team
from trip_planner.models.itinerary import Itinerary

from trip_planner.models.flights import FlightsPlannerResponse
from trip_planner.models.hotels import HotelsPlannerResponse
from .models.api import PlanItineraryRequest, PlanItineraryResponse, FlightsRequest, FlightsResponse, RefineItineraryRequest, HotelsResponse, HotelsRequest, HotelsAndFlightsResponse, HotelsAndFlightsRequest
from trip_planner.preliminary_variations_crew import PreliminaryPlanInputArgs, ProposedPlans, run_agent, PreliminaryPlan


# # configure the Phoenix tracer
tracer_provider = register(
    endpoint="http://localhost:6006/v1/traces",
    project_name="agno_trip_planner",
    auto_instrument=True
)

app = FastAPI(title="Trip Planner API", version="0.1.0")
@app.post("/get_hotels_and_flights", response_model=HotelsAndFlightsResponse)
async def get_hotels_and_flights(request: HotelsAndFlightsRequest):
    """Get hotels and flights for a given itinerary."""

    cities = []
    dates = []
    flight_dates = []
    for plan in request.itinerary.city_plans:
        cities.append(plan.city)
        dates.append(f"{plan.arrival_date} to {plan.departure_date}")
        flight_dates.append(plan.arrival_date)
    flight_dates.append(request.itinerary.city_plans[-1].departure_date)

    hotels_plan, flights_plan = await asyncio.gather(
        run_hotels_team(cities, dates),
        run_flights_team([request.departure_city] + cities, flight_dates)
    )

    hotels_plan: HotelsPlannerResponse = hotels_plan
    flights_plan: FlightsPlannerResponse = flights_plan
    
    return HotelsAndFlightsResponse(
        hotels_plan=hotels_plan,
        flights_plan=flights_plan,
        message="Hotels and flights found successfully",
    )


@app.post("/hotels", response_model=HotelsResponse)
async def get_hotels(request: HotelsRequest):
    """Get hotels for a given itinerary. This shit can fail in response parsing."""

    cities = []
    dates = []
    for plan in request.itinerary.city_plans:
        cities.append(plan.city)
        dates.append(f"{plan.arrival_date} to {plan.departure_date}")
    
    hotels_plan: HotelsPlannerResponse = await run_hotels_team(cities, dates)
    return HotelsResponse(hotels_plan=hotels_plan, message="Hotels found successfully")

@app.post("/flights", response_model=FlightsResponse)
async def get_flights(request: FlightsRequest):
    """Get flights for a given itinerary. This shit can fail in response parsing."""
    
    flight_cities = [request.departure_city]
    flight_dates = []
    for plan in request.itinerary.city_plans:
        flight_cities.append(plan.city)
        flight_dates.append(plan.arrival_date)
    flight_dates.append(request.itinerary.city_plans[-1].departure_date)

    flights_plan: FlightsPlannerResponse = await run_flights_team(flight_cities, flight_dates)
   
    return FlightsResponse(
        flights_plan=flights_plan, 
        message="Flights found successfully",
    ) 

@app.post("/plan_itinerary", response_model=PlanItineraryResponse)
async def plan_itinerary(request: PlanItineraryRequest):
    """Plan a trip using the itinerary planner crew"""    
    try:
        input_query = f"Plan a trip with parameters: {request.traveler_input.model_dump_json()}"
        itinerary: Itinerary = await run_team(input_query)

        return PlanItineraryResponse(
            itinerary=itinerary,
            message="Trip planning completed successfully",
        )
        
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing itinerary: {str(e)}"
        )
    

@app.post("/refine_itinerary", response_model=PlanItineraryResponse)
async def refine_itinerary(request: RefineItineraryRequest):
    """Refine the itinerary using the itinerary planner crew"""

    query = dedent(f"""\
        Refine the itinerary with the following traveler input:
        {request.traveler_input}

        Itinerary:
        {request.itinerary}

        User feedback:
        {request.user_feedback}
    """)
    refined_itinerary = await run_team(query)
    return PlanItineraryResponse(
        itinerary=refined_itinerary,
        message="Itinerary refined successfully",
    )


@app.post("/preliminary_plan", response_model=ProposedPlans)
async def plan_preliminary_activities(request: PreliminaryPlanInputArgs):
    return await run_agent(request)
