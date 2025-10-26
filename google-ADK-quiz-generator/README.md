google-ADK-quiz-generator/
├── pyproject.toml            # Project configuration and dependencies
└── src/
    └── adk_quiz_generator/   # Main application package
        │
        ├── main.py           # 🚀 Main script to run the application
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
