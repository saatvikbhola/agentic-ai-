#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from mycrew1.crew import Mycrew1

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    
    if len(sys.argv) < 3:
        print("missing arguments")
        print("usage: uv run run_crew <prefered_region> <trip_type>")
        print("usage: <trip_type> : (budget, luxury, adventure, cultural)")
        print("Example: uv run run_crew europe budget")
        sys.exit(1)

    preferred_region = sys.argv[1]
    trip_type = sys.argv[2]

    inputs = {
        "preferred_region" : preferred_region,
        "trip_type" : trip_type
    }

    try:
        Mycrew1().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    return "not implemented"

def replay():
    """
    Replay the crew execution from a specific task.
    """
    return "not implemented"    

def test():
    """
    Test the crew execution and returns the results.
    """
    return "not implemented"    