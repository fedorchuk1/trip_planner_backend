import os
from textwrap import dedent

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.models.openai.chat import OpenAIChat
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.mcp import MCPTools
from agno.tools.reasoning import ReasoningTools
from mcp import StdioServerParameters

from trip_planner.prompts.planning_team import INSTRUCTIONS
from trip_planner.models.itinerary import Itinerary
from trip_planner.tools.internet_search import get_top_internet_search_results


llm = LiteLLM(
    id="groq/llama-3.3-70b-versatile",
    request_params={
        "num_retries": 3,
    }
)


env = {
    **os.environ,
    "GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY"),
}

maps_server_params = StdioServerParameters(
    command="npx", args=["-y", "@modelcontextprotocol/server-google-maps"], env=env
)


async def run_team(query: str) -> Itinerary:
    async with MCPTools(server_params=maps_server_params) as maps_tools:
        maps_agent = Agent(
            name="Google Maps",
            role="Location Services Agent",
            model=llm,
            tools=[maps_tools],
            instructions=dedent("""\
                You are an agent that helps find attractions, points of interest,
                and provides directions in travel destinations from Google Maps.\
            """),
            add_datetime_to_instructions=True,
        )

        web_search_agent = Agent(
            name="Web Search",
            role="Web Search Agent",
            model=llm,
            tools=[get_top_internet_search_results],
            instructions=dedent("""\
                You are an agent that can search the web for any information related to restaurants, events, etc.
                Search for information about a given location.\
            """),
            add_datetime_to_instructions=True,
            tool_call_limit=2,
        )

        events_search_agent = Agent(
            name="Events Search",
            role="Events Search Agent",
            model=llm,
            tools=[get_top_internet_search_results],
            instructions=dedent("""\
                You are an agent that can search for the events in the given location and date range.
            """),
            add_datetime_to_instructions=True,
            tool_call_limit=2,
        )

        restaurants_search_agent = Agent(
            name="Restaurants Search",
            role="Restaurants Search Agent",
            model=llm,
            tools=[get_top_internet_search_results],
            instructions=dedent("""\
                You are an agent that can search for the restaurants in the given location and date range.
            """),
            add_datetime_to_instructions=True,
            tool_call_limit=2,
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
            model=OpenAIChat("gpt-4.1"),
            members=[
                web_search_agent,
                maps_agent,
                weather_search_agent,
                events_search_agent,
                restaurants_search_agent,
            ],
            instructions=[
                *INSTRUCTIONS,
            ],
            tools=[ReasoningTools(add_instructions=True)],
            response_model=Itinerary,
            show_tool_calls=True,
            markdown=True,
            debug_mode=True,
            show_members_responses=True,
            add_datetime_to_instructions=True,
            enable_agentic_context=True,
            tool_call_limit=10
        )

        result = await team.arun(query)
        return result.content # type: ignore
