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
from trip_planner.models.flights import Flight, FlightsPlan

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


async def run(input_parameters: dict):
    flights_agent = Agent(
        name="FlightsFinderAgent",
        role="Flights search agent",
        model=llm,
        tools=[get_flights],
        instructions=dedent("""\
            You are the best at searching flights for user.
            You are an agent that can find flights for a given departure and arrival cities, departure and return date.
            Use get_flights tool to find flights. Notice! You need to use the IATA code of the airports in the input cities in order to use the tool.            Reccomend at least 5 different flight options.
        """),
        add_datetime_to_instructions=True,
        show_tool_calls=True,
        markdown=True,
        response_model=FlightsPlan,
    )
    query = f"Find flights for the following parameters: {input_parameters}"
    response = await flights_agent.arun(query)
    return response.content 


# async def get_mock_response():
#     response = await run({"departure_date": "2025-07-25", "arrival_date": "2025-07-30", "departure_city": "London", "arrival_city": "Paris"})
#     print(response)

# if __name__ == "__main__":
#     asyncio.run(get_mock_response())