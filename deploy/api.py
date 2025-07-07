import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException

from trip_planner.itinerary_crew import run_team
from trip_planner.crew_backup import ItineraryPlannerCrew
from trip_planner.models.itinerary import Itinerary
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
    
    result = await run_team(crew_inputs)
    # itinerary_crew = ItineraryPlannerCrew().crew()
    # result = itinerary_crew.kickoff(inputs=crew_inputs)

    # itinerary = {}
    # with open("agno_result.json", "w") as f:
    # Handle both direct Itinerary objects and raw results

    if isinstance(result, Itinerary):
        itinerary = result
    else:
        itinerary = Itinerary(**result.to_dict()) if hasattr(result, 'to_dict') else result
    
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
