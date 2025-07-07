import asyncio
import os
from textwrap import dedent
from typing import List, Optional

from agno.agent import Agent
from agno.models.openai.chat import OpenAIChat
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.mcp import MCPTools
from agno.tools.reasoning import ReasoningTools
from mcp import StdioServerParameters
from pydantic import BaseModel
from agno.models.litellm import LiteLLM

from trip_planner.models.itinerary import Itinerary


from phoenix.otel import register

# configure the Phoenix tracer
tracer_provider = register(
    endpoint="http://localhost:6006/v1/traces",
    project_name="agno_trip_planner",
    auto_instrument=True
)


llm = LiteLLM(
    id="groq/llama-3.3-70b-versatile",
    request_params={
        "num_retries": 3,
    }
)


# Define response models
class AirbnbListing(BaseModel):
    name: str
    description: str
    address: Optional[str] = None
    price: Optional[str] = None
    dates_available: Optional[List[str]] = None
    url: Optional[str] = None


class Attraction(BaseModel):
    name: str
    description: str
    location: str
    rating: Optional[float] = None
    visit_duration: Optional[str] = None
    best_time_to_visit: Optional[str] = None


class WeatherInfo(BaseModel):
    average_temperature: str
    precipitation: str
    recommendations: str


class TravelPlan(BaseModel):
    airbnb_listings: List[AirbnbListing]
    attractions: List[Attraction]
    weather_info: Optional[WeatherInfo] = None
    suggested_itinerary: Optional[List[str]] = None


env = {
    **os.environ,
    "GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY"),
}

maps_server_params = StdioServerParameters(
    command="npx", args=["-y", "@modelcontextprotocol/server-google-maps"], env=env
)


async def run_team(input_parameters: dict) -> Itinerary:
    # Use AsyncExitStack to manage multiple context managers
    async with MCPTools(server_params=maps_server_params) as maps_tools:

        maps_agent = Agent(
            name="Google Maps",
            role="Location Services Agent",
            model=llm,
            tools=[maps_tools],
            instructions=dedent("""\
                You are an agent that helps find attractions, points of interest,
                and provides directions in travel destinations. Help plan travel
                routes and find interesting places to visit for a given location and date.\
            """),
            add_datetime_to_instructions=True,
        )

        web_search_agent = Agent(
            name="Web Search",
            role="Web Search Agent",
            model=llm,
            tools=[DuckDuckGoTools(cache_results=True)],
            instructions=dedent("""\
                You are an agent that can search the web for information.
                Search for information about a given location.\
            """),
            add_datetime_to_instructions=True,
        )

        weather_search_agent = Agent(
            name="Weather Search",
            role="Weather Search Agent",
            model=llm,
            tools=[DuckDuckGoTools()],
            instructions=dedent("""\
                You are an agent that can search the web for information.
                Search for the weather forecast for a given location and date.\
            """),
            add_datetime_to_instructions=True,
        )

        team = Team(
            name="SkyPlanner",
            mode="coordinate",
            model=OpenAIChat("gpt-4o"),
            members=[
                web_search_agent,
                maps_agent,
                weather_search_agent,
            ],
            instructions=[
                "Plan a full itinerary for the trip.",
                "Continue asking individual team members until you have ALL the information you need.",
                "Think about the best way to tackle the task.",
            ],
            tools=[ReasoningTools(add_instructions=True)],
            response_model=Itinerary,
            show_tool_calls=True,
            markdown=True,
            debug_mode=True,
            show_members_responses=True,
            add_datetime_to_instructions=True,
        )

        query = f"Plan a trip with parameters: {input_parameters}"
        result = await team.arun(query)
        return result.content # type: ignore
