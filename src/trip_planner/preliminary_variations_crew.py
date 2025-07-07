import asyncio
from datetime import date, datetime
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
from pydantic import BaseModel, Field
from agno.models.litellm import LiteLLM

from trip_planner.models.itinerary import Itinerary


from phoenix.otel import register

# configure the Phoenix tracer
tracer_provider = register(
    endpoint="http://localhost:6006/v1/traces",
    project_name="agno_trip_planner",
    auto_instrument=True
)


class UserPreference(BaseModel):
    user_id: str
    user_name: str
    raw_preferences: List[str]


class PreliminaryPlanInputArgs(BaseModel):
    """Example:
{    
    "destination": "Paris",
    "consesnsus_dates": ["2025-08-01", "2025-08-02", "2025-08-03"],
    "grouped_preferences": [
        {
            "user_id": "1234",
            "user_name": "Jenya",
            "preferred_length_days": 3,
            "raw_preferences": ["museums", "restaurants"]
        },
        {
            "user_id": "1235",
            "user_name": "Illia",
            "raw_preferences": ["parks", "restaurants", "landmarks"]
        }
    ]
}
"""
    destination: str
    budget: Optional[str] = None
    preferred_length_days: Optional[int] = None
    consesnsus_dates: List[date]
    grouped_preferences: List[UserPreference]


class Activity(BaseModel):
    name: str
    description: str
    location: str
    preliminary_length: Optional[str] = Field(None, description="Length of time this activity will take. For example, '3 hours'")
    cost: Optional[int] = None


class DayPlan(BaseModel):
    acitivites: List[Activity] = Field(
        ...,
        description=dedent("""
            List of things to do or places to visit; not limited to any particular activity type;
            Could be restaurants, museums, river boats, landmarks to visit, etc...
        """)
    )

# Define response models
class PreliminaryPlan(BaseModel):
    duration_days: int
    start_date: date
    end_date: date
    name: str
    summary: str
    day_plans: List[DayPlan] = Field(..., description="Activies per day")


class ProposedPlans(BaseModel):
    plans: List[PreliminaryPlan]


async def run_agent(input_parameters: PreliminaryPlanInputArgs, reasoning: bool = False) -> ProposedPlans:
    
    additional_kwargs = {}
    if reasoning:
        additional_kwargs["tools"] = [ReasoningTools()]

    agent = Agent(
        name="Planner",
        role="Proposes various preliminary trip plans for selected dates",
        model=OpenAIChat("gpt-4o"),
        instructions=dedent("""\
            You are an agent that, based on the user selected dates, preferences and a travel destination,
            helps find and plan different activites and plan a trip that will satisfy everyone.
            Start by reasoning and outlining where all users' preferences intersect. 
            Then, if there are multiple possibles date ranges for a trip, select up to 3 most suitable date ranges 
            and propose a per-day list of activities for them. 
        """),
        add_datetime_to_instructions=True,
        response_model=ProposedPlans,
        **additional_kwargs
    )

    query = f"Plan a trip with parameters: {input_parameters.model_dump_json()}"
    result = await agent.arun(query)
    return result.content # type: ignore
