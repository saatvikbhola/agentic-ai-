from mycrew1.tools.custom_tool import FileWriterTool
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class Mycrew1():
    """Mycrew1 crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools

#--------------------------
#       tools
#-------------------------

    @tool
    def file_writer_tool(self) -> FileWriterTool:
        """Tool for saving the generated trip plan to file """
        return FileWriterTool()
    

#--------------------------
#       Agents
#-------------------------


    @agent
    def destination_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['destination_expert'], # type: ignore[index]
            verbose=True
        )

    @agent
    def itinerary_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_planner'], # type: ignore[index]
            verbose=True
        )
    
    @agent
    def budget_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['budget_advisor'],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    

#--------------------------
#       tasks
#-------------------------


    @task
    def select_destination(self) -> Task:
        return Task(
            config=self.tasks_config['select_destination'], # type: ignore[index]
        )

    @task
    def plan_itinerary(self) -> Task:
        return Task(
            config=self.tasks_config['plan_itinerary'], # type: ignore[index]
        )

    @task
    def estimate_budget(self) -> Task:
        return Task(
            config=self.tasks_config['estimate_budget'],
            output_file='trip_plan.txt'
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Mycrew1 crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
