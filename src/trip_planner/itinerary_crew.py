import json

import yaml
from agno.agent import Agent
from agno.models.groq import Groq
from agno.team import Team
from agno.tools.reasoning import ReasoningTools
from agno.models.litellm import LiteLLM

from trip_planner.models.itinerary import Itinerary
from trip_planner.tools.internet_search import get_top_k_internet_search_results


from phoenix.otel import register

# configure the Phoenix tracer
tracer_provider = register(
    endpoint="http://localhost:6006/v1/traces",
    project_name="agno_trip_planner",
    auto_instrument=True
)


# Instrument Agno
# AgnoInstrumentor().instrument(tracer_provider=tracer_provider)

# print("Agno instrumented for Arize.")

def read_agents_config(config_path: str):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def get_agent_prompt(agents_config: dict, agent_name: str):
    agent_config = agents_config[agent_name]
    prompt = ""
    # prompt += f"Role: {agent_config['role']}\n"
    prompt += f"{agent_config['backstory']}\n"
    prompt += f"Goal: {agent_config['goal']}\n"
    prompt += f"Task Description: {agent_config['description']}\n"
    prompt += f"Expected Output: {agent_config['expected_output']}\n"
    return prompt

import litellm
# litellm._turn_on_debug()

# llm = Groq(id="meta-llama/llama-4-scout-17b-16e-instruct")
# llm = LiteLLM(id="groq/meta-llama/llama-4-scout-17b-16e-instruct")
llm = LiteLLM(
    id="groq/llama-3.3-70b-versatile",
    request_params={
        "num_retries": 3,
    }
)


async def run_team(input_parameters: dict):
    agents_config = read_agents_config("src/trip_planner/config/agents_prompts.yaml")

    restaurant_search_agent = Agent(
        name="Restaurant Search",
        role="Restaurant Search Agent",
        model=llm,
        tools=[get_top_k_internet_search_results],
        instructions=get_agent_prompt(agents_config, "restaurant_search_agent"),
        add_datetime_to_instructions=True,
    )

    events_search_agent = Agent(
        name="Events Search",
        role="Events Search Agent",
        model=llm,
        tools=[get_top_k_internet_search_results],
        instructions=get_agent_prompt(agents_config, "events_search_agent"),
        add_datetime_to_instructions=True,
    )

    city_attractions_explorer_agent = Agent(
        name="City Attractions Explorer",
        role="City Attractions Explorer Agent",
        model=llm,
        tools=[get_top_k_internet_search_results],
        instructions=get_agent_prompt(agents_config, "city_attractions_explorer_agent"),
        add_datetime_to_instructions=True,
    )

    # Create and run the team
    team = Team(
        name="SkyPlanner",
        mode="coordinate",
        model=llm,
        members=[
            restaurant_search_agent,
            events_search_agent,
            city_attractions_explorer_agent,
        ],
        instructions=get_agent_prompt(agents_config, "trip_planning_agent"),
        # tools=[ReasoningTools(add_instructions=True)],
        response_model=Itinerary,
        show_tool_calls=True,
        markdown=True,
        debug_mode=True,
        show_members_responses=True,
        add_datetime_to_instructions=True,
        tool_call_limit=10,
    )

    # Execute the team's task
    query = f"Plan a trip with parameters: {input_parameters}"
    result = team.run(query)
    with open("agno_result.json", "w") as f:
        json.dump(result.to_dict(), f)
    result = result.content
    # team.print_response()
    import asyncio
    await asyncio.sleep(0.1)
    print("-" * 30)
    print(result)
    print("-" * 30)
    return result
