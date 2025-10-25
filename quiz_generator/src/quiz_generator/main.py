import sys
import json
import os # Import the os module for file checking
from dotenv import load_dotenv
from pydantic import BaseModel

from crewai.flow import Flow, listen, start

# --- Import All Three Crews ---
from quiz_generator.crews.content_acquistion.content_acquistion import ContentAcquistionCrew
from quiz_generator.crews.quiz_generation.quiz_generation import QuizGenerationCrew
from quiz_generator.crews.review_and_format.review_and_format import ReviewAndFormatCrew

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv()


# --- Define the state of our flow ---
class QuizState(BaseModel):
    """Holds the state of the quiz generation flow."""
    url: str = ""
    content_brief: str = ""
    generated_quiz: dict = {"multiple_choice": [], "true_false": []}
    # Optional: Store the final confirmation message from Crew 3
    final_output_message: str = ""


class QuizGeneratorFlow(Flow[QuizState]):

    @start()
    def get_url(self, crewai_trigger_payload: dict = None):
        """Starts the flow by getting the URL."""
        print("--- Flow Started: Getting URL ---")
        if crewai_trigger_payload:
            self.state.url = crewai_trigger_payload.get('url')
            if not self.state.url:
                print("Error: No 'url' found in trigger payload.")
                sys.exit(1)
        else:
            # Default URL for 'crewai run kickoff'
            self.state.url = "https://genai.owasp.org/llmrisk/llm01-prompt-injection/"
        print(f"Processing URL: {self.state.url}")

    @listen(get_url)
    def run_crew_1(self):
        """
        Runs Crew 1 (Content Acquisition) to get the content brief,
        or loads it if content_brief.md already exists.
        """
        brief_file = "content_brief.md"

        if os.path.exists(brief_file):
            print(f"--- Found existing '{brief_file}'. Loading content and skipping Crew 1. ---")
            try:
                with open(brief_file, "r", encoding="utf-8") as f:
                    self.state.content_brief = f.read()
                if not self.state.content_brief:
                    print(f"Warning: '{brief_file}' exists but is empty. Crew 1 will run.")
                else:
                    print("--- Content loaded from file. ---")
                    return
            except Exception as e:
                print(f"Error reading existing '{brief_file}': {e}\nRaw Exception: {repr(e)}")
                print("Proceeding to run Crew 1.")

        print("--- Running Content Acquisition Crew (Crew 1) ---")
        try:
            crew_1_inputs = {'url': self.state.url}
            result = ContentAcquistionCrew().crew().kickoff(inputs=crew_1_inputs)
            self.state.content_brief = result.raw
            print("--- Crew 1 Finished ---")
        except Exception as e:
            print(f"Error running Crew 1: {e}\nRaw Exception: {repr(e)}")
            sys.exit(1)

    @listen(run_crew_1)
    def save_content_brief(self):
        """Saves the content brief (either newly generated or loaded) to a file."""
        if self.state.content_brief:
            print("--- Saving/Updating Content Brief File ---")
            try:
                with open("content_brief.md", "w", encoding="utf-8") as f:
                    f.write(self.state.content_brief)
                print("Successfully saved content brief to 'content_brief.md'")
                print("\n--- Content Brief (Preview) ---")
                print(self.state.content_brief[:500] + "...")
                print("---------------------")
            except Exception as e:
                print(f"Error saving content brief: {e}\nRaw Exception: {repr(e)}")
                sys.exit(1)
        else:
            print("Error: No content brief available to save.")
            sys.exit(1)

    @listen(save_content_brief)
    def run_crew_2(self):
        """Runs Crew 2 (Quiz Generation) using the brief."""
        print("--- Running Quiz Generation Crew (Crew 2) ---")
        mcq_questions = []
        tf_questions = []
        try:
            crew_2_inputs = {'content_brief': self.state.content_brief}
            result = QuizGenerationCrew().crew().kickoff(inputs=crew_2_inputs)

            if hasattr(result, 'tasks_output') and result.tasks_output:
                print(f"--- Found {len(result.tasks_output)} task outputs ---")
                for output_item in result.tasks_output:
                    current_output_str = str(output_item.raw)
                    print(f"Processing output item: '{current_output_str[:100]}...'")

                    # --- FIX: Clean JSON markers ---
                    cleaned_str = current_output_str.strip().strip('```json').strip('```').strip()
                    parsed_data = None
                    try:
                        if cleaned_str:
                            # --- FIX: Use json.loads instead of yaml.safe_load ---
                            parsed_data = json.loads(cleaned_str)
                    # --- FIX: Catch json.JSONDecodeError ---
                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not parse potential JSON: {e}\nRaw item:\n{current_output_str}")
                        continue

                    if isinstance(parsed_data, list) and parsed_data:
                        first_item = parsed_data[0]
                        if isinstance(first_item, dict):
                            if 'options' in first_item and 'correct_answer' in first_item:
                                if not mcq_questions:
                                    print("-> Identified as MCQ output.")
                                    mcq_questions = parsed_data
                                else:
                                    print("Warning: Found another potential MCQ output, skipping.")
                            elif 'answer' in first_item and 'options' not in first_item:
                                if not tf_questions:
                                    print("-> Identified as T/F output.")
                                    tf_questions = parsed_data
                                else:
                                    print("Warning: Found another potential T/F output, skipping.")
                            else:
                                print("-> Parsed JSON list, but structure didn't match MCQ or T/F.")
                        else:
                            print("-> Parsed JSON list, but first item is not a dictionary.")
                    elif parsed_data:
                        print(f"-> Parsed JSON, but it's not a list (Type: {type(parsed_data)}).")
                    else:
                        print("-> Output item was empty after cleaning.")
            else:
                print("--- No task outputs found in result.tasks_output or result.tasks_output is empty---")
            print("--- Crew 2 Finished ---")
        except Exception as e:
            print(f"Error running Crew 2: {e}\nRaw Exception: {repr(e)}")
            sys.exit(1)

        self.state.generated_quiz = {
            "multiple_choice": mcq_questions if isinstance(mcq_questions, list) else [],
            "true_false": tf_questions if isinstance(tf_questions, list) else []
        }

    @listen(run_crew_2)
    def save_quiz_file(self):
        """Saves the combined quiz data from Crew 2 to one JSON file."""
        print("--- Saving Generated Quiz JSON File ---")
        try:
            if not isinstance(self.state.generated_quiz, dict) or \
               not self.state.generated_quiz.get("multiple_choice") and \
               not self.state.generated_quiz.get("true_false"):
                print("Error: Crew 2 did not produce valid quiz data. Cannot save JSON.")
                sys.exit(1)

            file_name = "generated_quiz.json"
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(self.state.generated_quiz, f, indent=4)
            print(f"Successfully saved combined quiz to '{file_name}'")
            print("\n--- Generated Quiz (JSON Preview) ---")
            print(json.dumps(self.state.generated_quiz, indent=4)[:500] + "...")
            print("----------------------")
        except Exception as e:
            print(f"Error saving generated quiz JSON: {e}\nRaw Exception: {repr(e)}")
            sys.exit(1)

    @listen(save_quiz_file)
    def run_crew_3(self):
        """Runs Crew 3 (Review and Format) using the brief and generated quiz."""
        print("--- Running Review and Format Crew (Crew 3) ---")
        try:
            crew_3_inputs = {
                'content_brief': self.state.content_brief,
                'generated_quiz': json.dumps(self.state.generated_quiz, indent=4)
            }
            result = ReviewAndFormatCrew().crew().kickoff(inputs=crew_3_inputs)
            self.state.final_output_message = result.raw
            print("--- Crew 3 Finished ---")
            print(f"Crew 3 Result: {self.state.final_output_message}")
        except Exception as e:
            print(f"Error running Crew 3: {e}\nRaw Exception: {repr(e)}")
            sys.exit(1)

    @listen(run_crew_3)
    def flow_complete(self):
        """Prints the final confirmation message."""
        print("----------------------")
        print("--- Flow Complete ---")
        if self.state.final_output_message:
            print(self.state.final_output_message)
        else:
            print("Flow finished, but Crew 3 did not return a confirmation message.")
        print("----------------------")

# --- Functions to run the flow ---
def kickoff():
    print("Running with default URL...")
    QuizGeneratorFlow().kickoff()

def plot():
    QuizGeneratorFlow().plot()

def run_with_trigger():
    print("--- Starting Quiz Generator Flow ---")
    try:
        url = input("Please enter the URL you want to process: ")
        if not url.startswith(("http://", "https://")):
            print("Invalid URL. Please include 'http://' or 'https://'.")
            sys.exit(1)
        trigger_payload = {"url": url}
        QuizGeneratorFlow().kickoff(inputs={"crewai_trigger_payload": trigger_payload})
    except Exception as e:
        print(f"An error occurred: {e}\nRaw Exception: {repr(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url_arg = sys.argv[1]
        print(f"Running with provided URL: {url_arg}")
        if not url_arg.startswith(("http://", "https://")):
             print("Invalid URL. Please include 'http://' or 'https://'.")
             sys.exit(1)
        trigger = {"url": url_arg}
        QuizGeneratorFlow().kickoff(inputs={"crewai_trigger_payload": trigger})
    else:
        print("Running in main (checking for existing brief)...")
        QuizGeneratorFlow().kickoff()

