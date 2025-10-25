from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

# --- Import the crewAI LLM class ---
from crewai.llm import LLM

# --- Import the Word Output Tool ---
from quiz_generator.tools.word_output_tool import WordOutputTool


@CrewBase
class ReviewAndFormatCrew():
    """ReviewAndFormat crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # --- Define the LLMs for this crew ---
    # A more precise/critical LLM for the critic
    critic_llm = LLM(
        model="gemini/gemini-2.5-flash", # Use a more powerful model for review
        temperature=0.2 # Lower temperature for consistency
    )
    # A standard LLM for the formatter (mostly needs to call the tool)
    formatter_llm = LLM(
        model="gemini/gemini-2.5-flash",
        temperature=0.1
    )

    # --- Define the agents for this crew ---
    @agent
    def quiz_critic(self) -> Agent:
        return Agent(
            config=self.agents_config['quiz_critic'], # type: ignore[index]
            llm=self.critic_llm,
            verbose=True
            # No tools needed for the critic
        )

    @agent
    def word_formatter(self) -> Agent:
        return Agent(
            config=self.agents_config['word_formatter'], # type: ignore[index]
            tools=[WordOutputTool()], # Assign the WordOutputTool
            llm=self.formatter_llm,
            verbose=True
        )

    # --- Define the tasks for this crew ---
    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task'], # type: ignore[index]
            # Context (generated_quiz, content_brief) will be provided by the main flow
        )

    @task
    def format_task(self) -> Task:
        return Task(
            config=self.tasks_config['format_task'], # type: ignore[index]
            # This task implicitly depends on review_task in the sequential process
            # It will receive the JSON output from review_task as input context
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ReviewAndFormat crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential, # As required by the breakdown
            verbose=True
        )

