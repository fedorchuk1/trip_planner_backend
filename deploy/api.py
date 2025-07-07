import uuid
from datetime import datetime
from textwrap import dedent

from fastapi import FastAPI, HTTPException
from phoenix.otel import register

from trip_planner.itinerary_crew import run_team
from trip_planner.models.itinerary import Itinerary
from trip_planner.preliminary_variations_crew import PreliminaryPlanInputArgs, ProposedPlans, run_agent
from .models.api import PlanItineraryRequest, PlanItineraryResponse, RefineItineraryRequest


# configure the Phoenix tracer
tracer_provider = register(
    endpoint="http://localhost:6006/v1/traces",
    project_name="agno_trip_planner",
    auto_instrument=True
)


app = FastAPI(title="Trip Planner API", version="0.1.0")


@app.post("/plan_itinerary", response_model=PlanItineraryResponse)
async def plan_itinerary(request: PlanItineraryRequest):
    """Plan a trip using the itinerary planner crew"""    
    conversation_id = request.conversation_id or str(uuid.uuid4())
    try:
        input_query = f"Plan a trip with parameters: {request.traveler_input.model_dump_json()}"
        itinerary: Itinerary = await run_team(input_query)

        return PlanItineraryResponse(
            conversation_id=conversation_id,
            itinerary=itinerary,
            message="Trip planning completed successfully",
            timestamp=datetime.now()
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
    """)
    return await run_team(query)


@app.post("/preliminary_plan", response_model=ProposedPlans)
async def plan_preliminary_activities(request: PreliminaryPlanInputArgs):
    return await run_agent(request)
