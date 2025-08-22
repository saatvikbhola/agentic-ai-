Assignment – 2: Travel Planner Crew 
Problem Statement: 
You are tasked with building a Travel Planner Crew using CrewAI that helps users design a travel  itinerary based on their preferences.  
1. Create a crew with the following agents: 
- Destination Expert Agent: Suggests top destinations based on user input (e.g., “I want a  5-day budget-friendly trip in Europe”).  
- Itinerary Planner Agent: Creates a day-by-day plan with activities, food options, and  cultural experiences.  
- Budget Advisor Agent: Estimates the total cost of the trip and provides a budget  breakdown (accommodation, food, transport, activities). 
2. The crew should take two inputs from the user via CLI:  
- Preferred region/destination (e.g., “Europe”, “Japan”)  
- Type of trip (e.g., “budget-friendly”, “luxury”, “adventure”, “cultural”) 
3. Conϐigure the crew so that: 
- The Destination Expert selects possible destinations.  
- The Itinerary Planner designs a schedule.  


# Mycrew1 Crew (need to change some part of it)

Welcome to the Mycrew1 Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/mycrew1/config/agents.yaml` to define your agents
- Modify `src/mycrew1/config/tasks.yaml` to define your tasks
- Modify `src/mycrew1/crew.py` to add your own logic, tools and specific args
- Modify `src/mycrew1/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the mycrew1 Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The mycrew1 Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the Mycrew1 Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
