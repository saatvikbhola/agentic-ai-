from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os

class FileWriterInput(BaseModel):
    """Input schema for FileWriterTool"""
    content: str = Field(..., description="The complete travel plan (itinerary + budget)")

class FileWriterTool(BaseTool):
    name: str = "file_writer_tool"
    description: str = "Writes the final combined travel plan (itinerary + budget) into trip_plan.txt"
    args_schema: Type[BaseModel] = FileWriterInput

    def _run(self, content: str) -> str:
        try:
            os.makedirs("outputs", exist_ok=True)
            file_path =  os.path.join("outputs", "trip_plan.txt")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("++++++++++ Final Travel Plan +++++++++++ \n\n")
                f.write(content.strip() + "\n")
            
            return f"saved to {file_path}"

        except Exception as e:
            return f"failed to save, exception {str(e)}"