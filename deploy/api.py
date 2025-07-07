import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException

from trip_planner.itinerary_crew import run_team
from trip_planner.models.itinerary import Itinerary
from trip_planner.preliminary_variations_crew import PreliminaryPlanInputArgs, ProposedPlans, run_agent, PreliminaryPlan
from .models.api import PlanItineraryRequest, PlanItineraryResponse

app = FastAPI(title="Trip Planner API", version="0.1.0")


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


@app.post("/preliminary_plan", response_model=ProposedPlans)
async def plan_preliminary_activities(request: PreliminaryPlanInputArgs):
    return await run_agent(request)
