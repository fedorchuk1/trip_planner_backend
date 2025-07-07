import asyncio
import os
from textwrap import dedent
from typing import List, Optional

from agno.agent import Agent
from agno.team import Team
from mcp import StdioServerParameters
from pydantic import BaseModel
from agno.models.litellm import LiteLLM

from trip_planner.tools.agno.flights import get_flights
from trip_planner.models.flights import Flight, FlightsPlan, FlightRoutePlan

llm = LiteLLM(
    id="groq/llama-3.3-70b-versatile",
    request_params={
        "num_retries": 3,
    }
)

env = {
    **os.environ,
    "SERPAPI_KEY": os.getenv("SERPAPI_KEY"),
}


async def run(flight_cities: list[str], flight_dates: list[str]):
    flights_agent = Agent(
        name="FlightsFinderAgent",
        role="Flights search agent",
        model=llm,
        tools=[get_flights],
        instructions=dedent("""\
            You are the best at searching flights for user.
            You are an agent that can find flights for a given departure and arrival cities and an arrival date OR departure date. 
            You will be given a list of cities and dates. This is a plan for a trip, where user will depart from origin city, visit 1 or more cities and return to origin city.
            Here are the rules for each route:
            - If there is no departure date, then the departure date is the day before the arrival date or the same day if plane leaves early and arrives in the morning.
            - If there is no arrival date, then the arrival date is the day after the departure date.
            
            Use get_flights tool to find flights. Notice! You need to use the IATA code of the airports in the input cities in order to use the tool. 
            
            For each of the routes reccomend at least 5 different flight options.
            
            If there is only one route, then you can use ROUND_TRIP type of flight while calling the tool.

            IF YOU ARE GOING TO USE ROUND_TRIP, ONLY USE ROUND_TRIP FOR THE FIRST FLIGHT, FOR THE REST OF THE FLIGHTS USE ONE_WAY.
        """),
        add_datetime_to_instructions=True,
        show_tool_calls=True,
        markdown=True,
        response_model=FlightRoutePlan,
    )
    # query = f"Find flights for the following parameters: {input_parameters}"
    query = f"Find flights for the following parameters:"
    for i in range(len(flight_cities)-1):
        query += f"\n- Departure city: {flight_cities[i]}, Arrival date: {flight_dates[i]}, Arrival city: {flight_cities[i+1]}"
    if len(flight_cities) > 2:
        query += f"\n- Departure city: {flight_cities[-1]}, Departure date: {flight_dates[-1]}, Arrival city: {flight_cities[0]}"
    response = await flights_agent.arun(query)
    return response.content 


# async def get_mock_response():
#     response = await run({"departure_date": "2025-07-25", "arrival_date": "2025-07-30", "departure_city": "London", "arrival_city": "Paris"})
#     print(response)

# if __name__ == "__main__":
#     asyncio.run(get_mock_response())