from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from typing import Annotated
from langgraph.graph import StateGraph, START, END


import getpass
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Define the tools that the agent can use
# The tools are defined as functions that take arguments and return a value
# The tools are then registered with the agent and can be used in the agent's interactions
tavily_tool = TavilySearchResults(max_results=5)

# Warning: This executes code locally, which can be unsafe when not sandboxed

repl = PythonREPL()


@tool
def python_repl_tool(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return (
        result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    )



from typing import Literal
from langchain_openai import ChatOpenAI

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState, END
from langgraph.types import Command


def make_system_prompt(suffix: str) -> str:
    return f"""You are a helpful AI assistant collaborating with other assistants.
Use the provided tools to progress toward answering the question.
If you are unable to fully answer, that's OK—another assistant with different tools will help where you left off.
Execute what you can to make progress.
Once you or any team member have the final answer or deliverable, prefix your response with "FINAL ANSWER" so the team knows to stop.
{suffix}"""



def get_next_node(last_message: BaseMessage, goto: str):
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return END
    return goto



research_llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base=os.getenv("OPENROUTER_BASE_URL"),
            model_name="meta-llama/llama-3.1-8b-instruct")


# Research agent and node
research_agent = create_react_agent(
    research_llm,
    tools=[tavily_tool],
    prompt=make_system_prompt(
        "You can only do research to find detailed and accurate data. You are working with a chart generator colleague that can code."
    ),
)


def research_node(
    state: MessagesState,
) -> Command[Literal["programmer", END]]:
    result = research_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "programmer")
    # wrap in a human message, as not all providers allow
    # AI message at the last position of the input messages list
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="researcher"
    )
    return Command(
        update={
            # share internal message history of research agent with other agents
            "messages": result["messages"],
        },
        goto=goto,
    )


coding_llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base=os.getenv("OPENROUTER_BASE_URL"),
            model_name="google/gemini-2.0-flash-001")
# Chart generator agent and node
# NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION, WHICH CAN BE UNSAFE WHEN NOT SANDBOXED

programming_agent = create_react_agent(
    coding_llm,
    [python_repl_tool],
    prompt=make_system_prompt(
        "You can only write code and generate charts. You are working with a researcher colleague that provides you with data and instructions. Use the seaborn library for creating nice visualizations and always show your chart before finishing."
    ),
)


def programming_node(state: MessagesState) -> Command[Literal["researcher", END]]:
    result = programming_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "researcher")
    # wrap in a human message, as not all providers allow
    # AI message at the last position of the input messages list
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="programmer"
    )
    return Command(
        update={
            # share internal message history of chart agent with other agents
            "messages": result["messages"],
        },
        goto=goto,
    )



from langgraph.graph import StateGraph, START

workflow = StateGraph(MessagesState)
workflow.add_node("researcher", research_node)
workflow.add_node("programmer", programming_node)

workflow.add_edge(START, "researcher")
graph = workflow.compile()