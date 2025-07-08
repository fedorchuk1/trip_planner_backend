from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

import asyncio
import os
from textwrap import dedent
from typing import List, Optional

from agno.agent import Agent
from agno.team import Team
from mcp import StdioServerParameters
from pydantic import BaseModel
from agno.models.litellm import LiteLLM
from agno.models.openai import OpenAIChat

from trip_planner.models.hotels import HotelsPlannerResponse

async def run(cities: list[str], dates: list[str]):
    # Define server parameters
    env = {
        **os.environ, 
    }
    airbnb_server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
        env=env,
    )

    async with (
        MCPTools(server_params=airbnb_server_params) as airbnb_tools,
    ):
        # Create all agents
        airbnb_agent = Agent(
            name="Airbnb",
            role="Airbnb Agent",
            model=OpenAIChat("gpt-4.1-nano"),
            tools=[airbnb_tools],
            instructions=dedent("""\
            You are the best at searching apartments for user.
            You are an agent that can find apartments for a given city and dates.

            Use your airbnb tool in order to find apartments. Use this tool at least once for each of the input cities.
            For each of the cities reccomend at least 5 different apartment options. 
            You must retry the tool call if you get an error, up until you have at least 3 options for each of the cities.
            Concentrate on getting the right url for each of the apartments in airbnb and the right info.
            """),
            add_datetime_to_instructions=True,
            response_model=HotelsPlannerResponse,
            show_tool_calls=True,
        )
        query = f"Find hotels for the following cities and dates:"
        for i in range(len(cities)):
            query += f"\n- City: {cities[i]}, Dates: {dates[i]}"
        response = await airbnb_agent.arun(query)
        return response.content 
