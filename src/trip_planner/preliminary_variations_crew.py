from datetime import date
from textwrap import dedent
from typing import List, Optional

from agno.agent import Agent
from agno.models.openai.chat import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from pydantic import BaseModel, Field
from agno.models.litellm import LiteLLM

from trip_planner.tools.generate_image import generate_image

# from phoenix.otel import register

# # configure the Phoenix tracer
# tracer_provider = register(
#     endpoint="http://localhost:6006/v1/traces",
#     project_name="agno_trip_planner",
#     auto_instrument=True
# )


llm = LiteLLM(
    id="groq/llama-3.3-70b-versatile",
    request_params={
        "num_retries": 3,
    }
)

class UserPreference(BaseModel):
    user_id: str
    user_name: str
    raw_preferences: List[str]


class PreliminaryPlanInputArgs(BaseModel):
    """Example:
{    
    "destination": "Paris",
    "consesnsus_dates": ["2025-08-01", "2025-08-02", "2025-08-03", "2025-08-04", "2025-08-05", "2025-08-06"],
    "grouped_preferences": [
        {
            "user_id": "1234",
            "user_name": "Jenya",
            "raw_preferences": ["museums", "restaurants"]
        },
        {
            "user_id": "1235",
            "user_name": "Illia",
            "preferred_length_days": 3,
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
    summary: str = Field(..., description="Must accurately, but consicely desribe and summarize planned activities")
    base64_image_string: Optional[str] = Field(None, description="Internal field, skip or return null")
    day_plans: List[DayPlan] = Field(..., description="Activies per day")


class ProposedPlans(BaseModel):
    plans: List[PreliminaryPlan]


def generate_image_for_plan(plan: PreliminaryPlan):
    prompt = f"A beautiful stok background image for a trip called '{plan.name}' with the following summary: {plan.summary}"
    return generate_image(prompt)


async def run_agent(input_parameters: PreliminaryPlanInputArgs, reasoning: bool = False, generate_images: bool = True) -> ProposedPlans:
    
    additional_kwargs = {}
    if reasoning:
        additional_kwargs["tools"] = [ReasoningTools()]

    agent = Agent(
        name="Planner",
        role="Proposes various preliminary trip plans for selected dates",
        model=llm, #OpenAIChat("gpt-4o"),
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
    proposition: ProposedPlans = result.content # type: ignore
    for plan in proposition.plans:
        plan.base64_image_string = generate_image_for_plan(plan)

    return proposition
