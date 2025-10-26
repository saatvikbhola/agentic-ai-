from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

# Local imports
from ..config.models import gemini_model
from ..tools.web_scraper import web_scraper_tool
from ..tools.file_tools import file_reader_tool, file_writer_tool
from ..tools.search_tool import web_search_tool
from ..tools.word_tools import word_writer_tool  # <- new Word tool
from . import prompts

# --- 1. Content Acquisition ---
content_acquisition_agent = LlmAgent(
    model=gemini_model,
    instruction=prompts.CONTENT_ACQUISITION_INSTRUCTION,
    tools=[web_scraper_tool, file_reader_tool, file_writer_tool],
    name="ContentAcquisitionAgent"
)

# --- 2. Quiz Generation Sub-Agents ---
mcq_generation_agent = LlmAgent(
    model=gemini_model,
    instruction=prompts.MCQ_AGENT_INSTRUCTION,
    name="MCQGenerationAgent"
)

tf_generation_agent = LlmAgent(
    model=gemini_model,
    instruction=prompts.TRUE_FALSE_AGENT_INSTRUCTION,
    name="TFGenerationAgent"
)

# --- 2b. Parallel Wrapper ---
quiz_generation_agent = ParallelAgent(
    sub_agents=[mcq_generation_agent, tf_generation_agent],
    name="ParallelQuizGenerator"
)

# --- 3. Review & Format ---
validator_agent = LlmAgent(
    model=gemini_model,
    instruction=prompts.VALIDATOR_AGENT_INSTRUCTION,
    tools=[web_search_tool],
    name="ValidatorAgent"
)

formatter_agent = LlmAgent(
    model=gemini_model,
    instruction=prompts.FORMATTER_AGENT_INSTRUCTION,
    name="FormatterAgent"
)

review_and_format_agent = SequentialAgent(
    sub_agents=[validator_agent, formatter_agent],
    name="ReviewAndFormatAgent"
)

# --- 4. Word Document Generation Agent ---
word_agent = LlmAgent(
    model=gemini_model,
    instruction=prompts.WORD_AGENT_INSTRUCTION,
    tools=[word_writer_tool],  # tool that writes Word docs
    name="QuizWordAgent"
)

# --- 5. Orchestrator ---
quiz_orchestrator = SequentialAgent(
    sub_agents=[
        content_acquisition_agent,
        quiz_generation_agent,
        review_and_format_agent
        #word_agent  # <- added as final step
    ],
    name="QuizOrchestrator"
)
