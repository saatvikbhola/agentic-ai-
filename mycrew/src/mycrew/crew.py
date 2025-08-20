from mycrew.tools.custom_tool import FileSaverTool
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Mycrew():
    """Mycrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended 
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools

    @tool  # Add the @tool decorator
    def file_saver(self) -> FileSaverTool:
        """Method that defines and returns the FileSaverTool."""
        return FileSaverTool()


#-------------------------
#	Agents
#-------------------------


    @agent
    def problem_setter(self) -> Agent:
        return Agent(
            config=self.agents_config['problem_setter'], # type: ignore[index]
            verbose=True
        )

    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config['coder'], # type: ignore[index]
            verbose=True
        )

    @agent
    def reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['reviewer'], # type: ignore[index]
            verbose=True
        )



    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task

#-------------------------
#	tasks
#-------------------------


    @task
    def define_problem(self) -> Task:
        return Task(
            config=self.tasks_config['define_problem'], # type: ignore[index]
        )

    @task
    def generate_code(self) -> Task:
        return Task(
            config=self.tasks_config['generate_code'], # type: ignore[index]
            output_file='outputs/solution.py'
        )

    @task
    def review_code(self) -> Task:
        return Task(
            config=self.tasks_config['review_code'], # type: ignore[index]
            output_file='outputs/review.txt'
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Mycrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
