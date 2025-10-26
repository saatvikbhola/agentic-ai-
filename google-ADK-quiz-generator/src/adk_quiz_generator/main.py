import os
import json
import uuid
import asyncio
import re
import time
import logging
from dotenv import load_dotenv

# --- ADK imports ---
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import google.generativeai as genai

# --- Prometheus Imports ---
try:
    from prometheus_client import CollectorRegistry, Counter, Gauge, push_to_gateway
    PROMETHEUS_ENABLED = True
except ImportError:
    print("[WARNING] prometheus_client not installed. Metrics will not be pushed.")
    PROMETHEUS_ENABLED = False

# --- Local imports ---
from adk_quiz_generator.agents import quiz_orchestrator
from adk_quiz_generator.tools.file_tools import file_writer_tool
from adk_quiz_generator.tools.word_tools import word_writer_tool

# --- Load environment variables ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env file.")
genai.configure(api_key=api_key)

# --- 1. CONFIGURE LOGGING ---
class AgentLogFilter(logging.Filter):
    def filter(self, record):
        return record.getMessage().startswith('[AGENT]')

log_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)-5.5s] [%(name)-12.12s]  %(message)s"
)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler("quiz_generator.log", mode="a", encoding="utf-8")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)
console_handler.addFilter(AgentLogFilter())
root_logger.addHandler(console_handler)

logging.getLogger('google.adk').setLevel(logging.INFO)
logging.getLogger('hpack').setLevel(logging.WARNING)

# --- Prometheus Metrics Definitions ---
if PROMETHEUS_ENABLED:
    registry = CollectorRegistry()
    quiz_runs_total = Counter(
        "quiz_generator_runs_total",
        "Total number of quiz generation runs",
        ["status"],
        registry=registry
    )
    quiz_last_run_duration = Gauge(
        "quiz_generator_last_run_duration_seconds",
        "Duration of the last quiz generation run in seconds",
        registry=registry
    )
    quiz_questions_generated = Gauge(
        "quiz_generator_questions_generated_total",
        "Total number of questions in the last generated quiz",
        registry=registry
    )

# --- Helper function: Create session ---
async def create_session(runner):
    logging.info("Creating new user session...")
    user_id = str(uuid.uuid4())
    new_session = await runner.session_service.create_session(
        user_id=user_id,
        app_name=runner.app_name
    )
    logging.info(f"Session created with ID: {new_session.id}")
    return new_session, user_id

# --- Robust extraction of final JSON ---
def extract_final_json(event):
    if not event.content or not event.content.parts:
        return ""
    
    for part in event.content.parts:
        if hasattr(part, "function_response") and part.function_response:
            response = part.function_response.response
            return json.dumps(response) if isinstance(response, dict) else str(response)

    for part in event.content.parts:
        if hasattr(part, "text") and part.text:
            text = part.text.strip()
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"```$", "", text)
            return text.strip()

    return ""

def main():
    logging.info("--- Quiz Generator Process Started ---")
    if PROMETHEUS_ENABLED:
        start_time = time.time()
    
    final_quiz_json = {}
    raw_output_for_debugging = []
    run_status = "failure"  # <-- FIX: Assume failure until proven success
    question_count = 0

    try:
        # --- 1. Initialize Memory and Runner ---
        logging.info("Initializing InMemorySessionService and Runner...")
        memory_service = InMemorySessionService()
        runner = Runner(
            agent=quiz_orchestrator,
            session_service=memory_service,
            app_name="quiz_generator_terminal"
        )

        # --- 2. Get user inputs ---
        url = input("Enter the URL for quiz generation: ").strip()
        use_cache_input = input("Use cached content if available? (yes/no): ").strip().lower()
        use_cache = use_cache_input in ["yes", "y"]
        logging.info(f"User input received: URL={url}, UseCache={use_cache}")

        # --- 3. Create session ---
        new_session, user_id = asyncio.run(create_session(runner))
        session_id = new_session.id

        # --- 4. Build prompt ---
        prompt_text = f"Generate a quiz for the URL: {url}. Use cache: {use_cache}"
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=prompt_text)]
        )
        logging.debug(f"Built user message: {user_message}")

        logging.info("--- Starting Quiz Orchestrator ---")

        # --- 5. Run the orchestrator ---
        final_response_events_generator = runner.run(
            new_message=user_message,
            session_id=session_id,
            user_id=user_id
        )

        # --- 6. Parse output ---
        final_response = ""
        last_final_event = None

        logging.debug("Streaming agent events...")
        for event in final_response_events_generator:
            logging.debug(f"ADK_EVENT: {str(event)}")
            raw_output_for_debugging.append(str(event))
            author = getattr(event, "author", "UnknownAgent")
            logging.info(f"[AGENT] {author} is producing output...")

            if event.is_final_response():
                last_final_event = event

        if last_final_event:
            final_response = extract_final_json(last_final_event)
            logging.info("Extracted final JSON response.")
            logging.debug(f"Final JSON content: {final_response}")

        if not final_response:
            logging.error("No valid JSON found in final agent output.")
            raise ValueError("No valid JSON found in final agent output.")

        final_quiz_json = json.loads(final_response)
        logging.info("Successfully loaded final JSON string.")

        # --- FIX: Validate JSON structure BEFORE declaring success ---
        if not isinstance(final_quiz_json, dict):
            logging.error(f"Final JSON is a {type(final_quiz_json)}, not a dict. Content: {final_quiz_json}")
            raise ValueError(f"Expected final JSON to be a dictionary (dict), but got {type(final_quiz_json)} instead.")

        mcq_count = len(final_quiz_json.get("multiple_choice", []))
        tf_count = len(final_quiz_json.get("true_false", []))
        question_count = mcq_count + tf_count

        if question_count == 0:
            logging.warning("JSON was valid, but contained no questions.")
            # We'll let this count as a "success" but log the warning.
        
        logging.info(f"Quiz contains {mcq_count} MCQs and {tf_count} T/F questions.")
        
        # --- FIX: Move success flag to the VERY END of the 'try' block ---
        run_status = "success"
        
    except Exception as e:
        # Log the full traceback to the file
        logging.error(f"Error during agent run or parsing: {e}", exc_info=True)
        raw_output = "\n".join(raw_output_for_debugging)
        final_quiz_json = {
            "error": f"Agent run failed: {e}",
            "raw_output": raw_output
        }
        # run_status remains "failure"

    finally:
        # --- 7. Save JSON for debugging ---
        output_file_json = "quiz_output.json"
        logging.info(f"Saving debug JSON to '{output_file_json}'...")
        result_message_json = file_writer_tool.func(output_file_json, json.dumps(final_quiz_json, indent=2))
        logging.info(f"Save JSON result: {result_message_json}")

        # --- 8. Generate Word document (only if successful) ---
        # This 'if' block will now work correctly
        if run_status == "success":
            output_file_docx = "quiz_output.docx"
            logging.info(f"Generating Word document at '{output_file_docx}'...")
            quiz_json_str = json.dumps(final_quiz_json)
            result_message_docx = word_writer_tool.func(output_file_docx, quiz_json_str)
            logging.info(f"Generate Word result: {result_message_docx}")
        
        # --- 9. Push metrics to Pushgateway ---
        if PROMETHEUS_ENABLED:
            logging.info("Preparing to push metrics to Prometheus Pushgateway...")
            try:
                end_time = time.time()
                duration = end_time - start_time
                quiz_last_run_duration.set(duration)
                quiz_runs_total.labels(status=run_status).inc()
                quiz_questions_generated.set(question_count)

                push_to_gateway(
                    "localhost:9091", 
                    job="quiz_generator_batch", 
                    registry=registry
                )
                logging.info(f"Metrics pushed (Duration: {duration:.2f}s, Status: {run_status}, Questions: {question_count}).")
            except Exception as push_e:
                logging.error(f"Could not push metrics to Pushgateway at localhost:9091. Is it running? \n{push_e}", exc_info=True)

        logging.info(f"--- Quiz Generator Process Finished (Status: {run_status}) ---")


if __name__ == "__main__":
    main()