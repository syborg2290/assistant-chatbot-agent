from crewai.tools import BaseTool
from langchain_community.agent_toolkits.load_tools import load_tools


class HumanTool(BaseTool):
    name: str = "Human Tool"
    description: str = (
        "A tool that prompts the user for input. Use when you need to ask the user a question."
    )

    def _run(self, query: str) -> str:
        return input(f"\n{query}\n")
