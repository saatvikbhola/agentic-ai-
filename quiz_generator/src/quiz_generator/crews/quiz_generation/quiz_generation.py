from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

# --- Import the crewAI LLM class ---
from crewai.llm import LLM


@CrewBase
class QuizGenerationCrew():
    """QuizGeneration crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # --- Define the LLM for this crew ---
    # We use a creative temperature for question generation
    question_llm = LLM(
        model="gemini/gemini-2.5-flash", # Use a powerful model
        temperature=0.7
    )

    
    manager_llm = LLM(
        model = "gemini/gemini-2.5-flash",
        temperature=0.2
    )

    # --- Define the agents for this crew ---
    @agent
    def mcq_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['mcq_generator'], # type: ignore[index]
            llm=self.question_llm,
            verbose=True
        )

    @agent
    def true_false_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['true_false_generator'], # type: ignore[index]
            llm=self.question_llm,
            verbose=True
        )
    
    '''    @agent
    def quiz_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['quiz_manager'],
            llm=self.manager_llm,
            verbose=True
        )'''
        
    # --- Define the tasks for this crew ---
    @task
    def mcq_task(self) -> Task:
        return Task(
            config=self.tasks_config['mcq_task'], # type: ignore[index]
        )

    @task
    def tf_task(self) -> Task:
        return Task(
            config=self.tasks_config['tf_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the QuizGeneration crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            
            process=Process.hierarchical, # <-- Set to parallel as required
            manager_llm=self.manager_llm,
            
            #manager_agent=self.quiz_manager(),
            
            verbose=True
        )

