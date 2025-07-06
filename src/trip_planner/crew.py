from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from trip_planner.models.general import FlightsPlan, Itinerary
from trip_planner.tools.flights import FlightsSearchTool
from trip_planner.tools.internet_search import GetTopKSearchResultsTool

llm = LLM(
    model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.2,
)


@CrewBase
class TripPlannerCrew():
    """Trip Planner Crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # @agent
    # def manager_agent(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['manager_agent'], # type: ignore
    #         verbose=True,
    #         reasoning=True,
    #         allow_delegation=True,
    #     ) # type: ignore

    @agent
    def restaurant_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['restaurant_scout'], # type: ignore
            tools=[GetTopKSearchResultsTool()],
            verbose=True,
            allow_delegation=False,
        ) # type: ignore
    
    @agent
    def events_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['events_scout'], # type: ignore
            tools=[GetTopKSearchResultsTool()],
            verbose=True,
            allow_delegation=False,
        ) # type: ignore
    
    @agent
    def city_explorer(self) -> Agent:
        return Agent(
            config=self.agents_config['city_explorer'], # type: ignore
            tools=[GetTopKSearchResultsTool()],
            verbose=True,
            allow_delegation=False,
        ) # type: ignore
    
    @agent
    def itinerary_compiler(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_compiler'], # type: ignore
            verbose=True,
            allow_delegation=False,
            reasoning=True,
        ) # type: ignore
        
    @agent
    def flight_search_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['flight_search_agent'], # type: ignore
            tools=[FlightsSearchTool()],
            verbose=True,
            allow_delegation=False,
            reasoning=True,
        ) # type: ignore
    
    @task
    def restaurant_scout_task(self) -> Task:
        return Task(
            config=self.tasks_config['restaurants_scout_task'], # type: ignore
            agent=self.restaurant_scout(),
            async_execution=True,
        ) # type: ignore

    @task
    def events_scout_task(self) -> Task:
        return Task(
            config=self.tasks_config['events_scout_task'], # type: ignore
            agent=self.events_scout(),
            async_execution=True,
        ) # type: ignore

    @task
    def city_explorer_task(self) -> Task:
        return Task(
            config=self.tasks_config['city_explorer_task'], # type: ignore
            agent=self.city_explorer(),
            async_execution=True,
        ) # type: ignore
    
    # @task
    # def itinerary_compilation_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['itinerary_compilation_task'], # type: ignore
    #         output_pydantic=Itinerary,
    #     ) # type: ignore
    
    @task
    def itinerary_compilation_task_seq(self) -> Task:
        return Task(
            config=self.tasks_config['itinerary_compilation_task_seq'], # type: ignore
            agent=self.itinerary_compiler(),
            output_pydantic=Itinerary,
            context=[self.restaurant_scout_task(), self.events_scout_task(), self.city_explorer_task()],
        ) # type: ignore
    
    @task
    def flight_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['flight_search_task'], # type: ignore
            agent=self.flight_search_agent(),
            output_pydantic=FlightsPlan,
            context=[self.itinerary_compilation_task_seq()],
        ) # type: ignore
    
    @crew
    def crew(self) -> Crew:
        """Creates the TripPlanner crew"""
        # return Crew(
        #     agents=[self.restaurant_scout(), self.events_scout(), self.city_explorer()],
        #     tasks=[self.itinerary_compilation_task()],
        #     manager_agent=self.manager_agent(),
        #     process=Process.hierarchical,
        #     verbose=True,
        # )
        return Crew(
            # agents=self.agents,
            # tasks=self.tasks,
            agents=[self.flight_search_agent()],
            tasks=[self.flight_search_task()],
            process=Process.sequential,
            verbose=True,
        )
