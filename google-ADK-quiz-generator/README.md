### Installation Steps

1.  **Clone the Repository**
    Open your terminal, navigate to where you want to store the project, and run:
    ```bash
    git clone https://github.com/saatvikbhola/agentic-ai-.git
    cd google-ADK-quiz-generator
    ```

2.  **Create and Activate a Virtual Environment**

    **On Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Project Dependencies**
    Install the project in "editable" mode. This command reads the `pyproject.toml` file and installs all listed dependencies.
    ```bash
    pip install -e .
    ```

4.  **Set Up Your API Key**
    The application requires a Google Gemini API key to run.
    
    Create a new file named `.env` in the root of the `google-ADK-quiz-generator` directory:

    ```
    # On Windows
    echo. > .env
    ```

    Open the `.env` file with a text editor and add your API key:
    ```
    GEMINI_API_KEY=your_api_key_here
    ```

------------------

## Running the Script with Prometheus

This project is configured to automatically send run metrics to a **Prometheus Pushgateway**. The `main.py` script will detect if the `prometheus-client` library is installed and, if so, attempt to push metrics to `localhost:9091` at the end of every run.

Download prometheus and docker in you local system.

To get this to work, you need to run two services: the **Pushgateway** itself, and then your **Python script**. 



### Step 1: Run the Prometheus Pushgateway

Before you run the Python script, you must start the Pushgateway service.

1.  Open a new terminal window.
2.  Run the following Docker command to download and start the official Pushgateway image. This will run it in the background and map it to `localhost:9091`.

    ```bash
    docker run -d --name pushgateway -p 9091:9091 prom/pushgateway
    ```

3.  You can verify it's running by opening `http://localhost:9091` in your browser.


### Step 2: Run the Quiz Generator Script

With the Pushgateway running in your first terminal, go back to the terminal you used for installation (where your virtual environment is active).

1.  Run the `main.py` script as usual:

    ```bash
    python src/adk_quiz_generator/main.py
    ```

2.  Follow the prompts to enter a URL and caching preference.

3.  When the script finishes, check its output. You should see a log message confirming the metrics were pushed successfully:

    ```
    [INFO] Metrics pushed (Duration: 56.63s, Status: success, Questions: 10).
    ```



### Step 3: Check Your Metrics

Go back to your browser at `http://localhost:9091`. You will now see metrics listed for the `quiz_generator_batch` job, including:

* `quiz_generator_last_run_duration_seconds`
* `quiz_generator_questions_generated_total`
* `quiz_generator_runs_total` (labeled by `status`)

**Note:** If you see an error in the log like `Could not push metrics to Pushgateway...`, it means you forgot to start the Pushgateway in Step 1. The script will still generate the quiz files, but no monitoring data will be sent.

--------------





### File structure

    google-ADK-quiz-generator/
    ├── pyproject.toml            # Project configuration and dependencies
    └── src/
        └── adk_quiz_generator/   # Main application package
            │
            ├── main.py           # Main script to run the application
            ├── agents/
            │   ├── __init__.py   # Defines the multi-agent pipeline (Orchestrator, Validator, etc.)
            │   └── prompts.py    # Contains all system instructions for the LLM agents
            │
            ├── config/
            │   ├── __init__.py
            │   └── models.py     # Configures the Gemini model and loads the API key
            │
            └── tools/
                ├── __init__.py
                ├── file_tools.py     # Custom tool for reading/writing local files (caching)
                ├── search_tool.py    # Custom tool for DuckDuckGo web search (fact-checking)
                ├── web_scraper.py    # Custom tool for scraping content from URLs
                └── word_tools.py     # Custom tool for generating .docx files
        
            Generated Files (appear after running) 
            ├── content_brief.md      # Cached content from the web scraper
            ├── quiz_generator.log    # Log file for debugging agent steps
            ├── quiz_output.json      # Final validated quiz in JSON format
            └── quiz_output.docx      # Final quiz as a Word document
