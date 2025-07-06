#!/usr/bin/env python
from typing import Optional
from trip_planner.models.general import TravelerInput, TripPlannerState
from trip_planner.flow import run_trip_planner, TripPlanResult

from phoenix.otel import register
from openinference.instrumentation.crewai import CrewAIInstrumentor


tracer_provider = register(
    endpoint="http://localhost:6006/v1/traces")
CrewAIInstrumentor().instrument(skip_dep_check=True, tracer_provider=tracer_provider)


def run(input: Optional[TravelerInput] = None) -> TripPlanResult:
    if input is None:
        inputs = {
            "country": "France",
            "cities": ["Paris", "Lyon"],
            "date_range": "2025-08-01 to 2025-08-10",
            "age": 31,
        }
    elif isinstance(input, dict):
        inputs = input
    else:
        inputs = input.model_dump()

    result = run_trip_planner(inputs)
    print(result)

    return result


if __name__ == "__main__":
    # asyncio.run(run())

    inputs = TravelerInput(
        country="France",
        cities=["Paris"],
        date_range="2025-08-01 to 2025-08-07",
        age=31,
        preferences=[
            "The main purpose of the trip is to visit the main landmarks and museums of the city",
            "Two days should be allocated to different events like festivals, concerts, etc.",
            # "I want to visit 3 museums",
            "Add restaurants for 3 days with french cuisine",
        ],
        constraints=[]
    )

    input_state = TripPlannerState(traveler_input=inputs)
    result = run(input_state)

    import json
    with open("results.json", "w") as f:
        json.dump(result.model_dump(), f)

    print(result)
