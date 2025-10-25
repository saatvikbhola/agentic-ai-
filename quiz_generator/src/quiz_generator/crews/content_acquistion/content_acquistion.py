from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from crewai import LLM

# Import the custom tool
from quiz_generator.tools.custom_tool import WebsiteScrapingTool

@CrewBase
class ContentAcquistionCrew():
    """ContentAcquistion crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    scraper_llm = LLM(
        model="gemini/gemini-2.5-flash"
    )

    analyst_llm = LLM(
        model="gemini/gemini-2.5-flash"
    )


    # Define the agents for this crew
    @agent
    def content_scraper(self) -> Agent:
        return Agent(
            config=self.agents_config['content_scraper'], # type: ignore[index]
            tools=[WebsiteScrapingTool()],  # Assign the tool to the agent
            llm=self.scraper_llm,
            verbose=True
        )

    @agent
    def research_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['research_analyst'], # type: ignore[index]
            llm=self.analyst_llm,
            verbose=True
            # No tools needed for this agent
        )

    # Define the tasks for this crew
    @task
    def scrape_task(self) -> Task:
        return Task(
            config=self.tasks_config['scrape_task'], # type: ignore[index]
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
            # This task implicitly depends on scrape_task because it's in a sequential process
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ContentAcquistion crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential, # As required by the user's breakdown
            verbose=True
        )
