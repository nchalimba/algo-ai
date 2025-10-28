from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, load_tool, tool
import datetime
import requests
import pytz
import yaml
import random
import string
from tools.final_answer import FinalAnswerTool

from Gradio_UI import GradioUI

@tool
def fib(n: int) -> str:
    """A tool that generates the Fibonacci sequence up to the n-th number.
    Args:
        n: The number of Fibonacci terms to generate. Must be a positive integer.
    """
    if not isinstance(n, int):
        return "Error: Input must be an integer."
    if n <= 0:
        return "Error: Please provide a positive integer greater than zero."

    sequence = [1, 1]
    for _ in range(n - 2):
        sequence.append(sequence[-1] + sequence[-2])

    return f"The first {n} Fibonacci numbers are: " + ", ".join(map(str, sequence[:n]))

@tool
def generate_password(length: int) -> str:
    """A tool that generates a secure password
    Args:
        length: The length of the password (min. 5)
    """
    if not isinstance(length, int) or length < 5:
        return "Error: Password length must be an integer of at least 6 characters."

    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(random.choice(characters) for _ in range(length))
    return f"Generated password: {password}"


final_answer = FinalAnswerTool()

# alternative: model_id='https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud' 

model = HfApiModel(
max_tokens=2096,
temperature=0.5,
model_id='Qwen/Qwen2.5-Coder-32B-Instruct',
custom_role_conversions=None,
)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[final_answer, fib, generate_password],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)


GradioUI(agent).launch()