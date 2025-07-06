import asyncio
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.flow.flow import Flow, start, listen
from pydantic import BaseModel, Field
from typing import Optional

from trip_planner.models.itinerary import Itinerary
from trip_planner.models.flights import FlightsPlan
from trip_planner.models.general import TravelerInput, TripPlanResult, TripPlannerState
from trip_planner.tools.internet_search import GetTopKSearchResultsTool
from trip_planner.tools.flights import FlightsSearchTool

# llm = LLM(
#     model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
#     temperature=0.2,
# )

#import logging
# lite_llm_logger = logging.getLogger("LiteLLM")
# lite_llm_logger.setLevel(logging.DEBUG)


# llm = LLM(
#     model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
#     temperature=0.2
# )
llm = LLM(
    model="gpt-4o-mini"
)


@CrewBase
class ItineraryPlannerCrew:
    """Crew responsible for creating the travel itinerary"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def restaurant_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['restaurant_scout'], # type: ignore
            tools=[GetTopKSearchResultsTool()],
            verbose=True,
            allow_delegation=False,
            llm=llm,
        ) # type: ignore
    
    @agent
    def events_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['events_scout'], # type: ignore
            tools=[GetTopKSearchResultsTool()],
            verbose=True,
            allow_delegation=False,
            llm=llm,
        ) # type: ignore
    
    @agent
    def city_explorer(self) -> Agent:
        return Agent(
            config=self.agents_config['city_explorer'], # type: ignore
            tools=[GetTopKSearchResultsTool()],
            verbose=True,
            allow_delegation=False,
            llm=llm,
        ) # type: ignore
    
    @agent
    def itinerary_compiler(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_compiler'], # type: ignore
            verbose=True,
            allow_delegation=False,
            reasoning=True,
            llm=llm,
        ) # type: ignore
    
    @task
    def restaurant_scout_task(self) -> Task:
        return Task(
            config=self.tasks_config['restaurants_scout_task'], # type: ignore
            agent=self.restaurant_scout(),
            async_execution=False,
        ) # type: ignore

    @task
    def events_scout_task(self) -> Task:
        return Task(
            config=self.tasks_config['events_scout_task'], # type: ignore
            agent=self.events_scout(),
            async_execution=False,
        ) # type: ignore

    @task
    def city_explorer_task(self) -> Task:
        return Task(
            config=self.tasks_config['city_explorer_task'], # type: ignore
            agent=self.city_explorer(),
            async_execution=False,
        ) # type: ignore
    
    @task
    def itinerary_compilation_task(self) -> Task:
        return Task(
            config=self.tasks_config['itinerary_compilation_task_seq'], # type: ignore
            agent=self.itinerary_compiler(),
            output_pydantic=Itinerary,
            context=[self.restaurant_scout_task(), self.events_scout_task(), self.city_explorer_task()],
        ) # type: ignore
    
    @crew
    def crew(self) -> Crew:
        """Creates the Itinerary Planning crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


@CrewBase
class FlightBookingCrew:
    """Crew responsible for finding and booking flights"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
        
    @agent
    def flight_search_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['flight_search_agent'], # type: ignore
            tools=[FlightsSearchTool()],
            verbose=True,
            allow_delegation=False,
            reasoning=True,
            llm=llm,
        ) # type: ignore
    
    @task
    def flight_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['flight_search_task'], # type: ignore
            agent=self.flight_search_agent(),
            output_pydantic=FlightsPlan,
        ) # type: ignore
    
    @crew
    def crew(self) -> Crew:
        """Creates the Flight Booking crew"""
        return Crew(
            agents=[self.flight_search_agent()],
            tasks=[self.flight_search_task()],
            process=Process.sequential,
            verbose=True,
        )

class TripPlannerFlow(Flow[TripPlannerState]):
    """Main flow that orchestrates itinerary planning and flight booking"""
    
    @start()
    def plan_itinerary(self) -> Itinerary:
        """Step 1: Create the travel itinerary using multiple specialized agents"""
        print("🗺️ Starting itinerary planning...")
        
        itinerary_crew = ItineraryPlannerCrew().crew()        
        crew_inputs = {
            'country': self.state.traveler_input.country,
            'cities': ', '.join(self.state.traveler_input.cities),
            'date_range': self.state.traveler_input.date_range,
            'age': self.state.traveler_input.age,
            'preferences': ', '.join(self.state.traveler_input.preferences or []),
            'constraints': ', '.join(self.state.traveler_input.constraints or [])
        }

        result = itinerary_crew.kickoff(inputs=crew_inputs)
        self.state.itinerary = Itinerary(**result.to_dict())
        
        print("✅ Itinerary planning completed!")
        return result
    
    @listen(plan_itinerary)
    def book_flights(self) -> FlightsPlan:
        """Step 2: Find and book flights based on the created itinerary"""
        print("✈️ Starting flight search...")
        
        if not self.state.itinerary:
            raise ValueError("No itinerary available for flight booking")
        
 
        flight_inputs = {
            "itinerary": self.state.itinerary.model_dump_json(),
            "flight_preferences": "",
        }
        
        result = FlightBookingCrew().crew().kickoff(inputs=flight_inputs)
        self.state.flights = FlightsPlan(**result.to_dict())
        
        print("✅ Flight search completed!")
        return result
    
    @listen(book_flights)
    def finalize_trip_plan(self) -> TripPlanResult:
        print("📋 Finalizing complete trip plan...")
        
        if not self.state.itinerary or not self.state.flights:
            raise ValueError("Missing itinerary or flights data")
        
        trip_plan = TripPlanResult(
            itinerary=self.state.itinerary,
            flights=self.state.flights
        )
        
        print("🎉 Complete trip plan ready!")
        return trip_plan

def run_trip_planner(traveler_input: TripPlannerState) -> TripPlanResult:
    """Run the complete trip planning flow"""
    flow = TripPlannerFlow()
    result = flow.kickoff(inputs=traveler_input)
    return result
