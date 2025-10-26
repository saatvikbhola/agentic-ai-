### Installation Steps

1.  **Clone the Repository**
    Open your terminal, navigate to where you want to store the project, and run:
    ```bash
    git clone <your-repository-url>
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









###File structure

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
