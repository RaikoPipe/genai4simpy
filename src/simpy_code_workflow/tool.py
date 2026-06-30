from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from .graph import run_workflow

def make_simpy_code_agent_tool(
    model_name: str = "qwen3.5:27b",
    base_url: str = "http://localhost:41434",
    temperature: float = 0.0,
    max_output_tokens: int = 64000,
):
    """
    Return a tool that delegates SimPy code generation and editing to the
    SimPy Code Agent. Model configuration is fixed at construction time.
    """
    _config = RunnableConfig(
        configurable={
            "model_name": model_name,
            "base_url": base_url,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        }
    )

    @tool
    def simpy_code_agent(
        task: str,
        current_code: str | None = None,
    ) -> str:
        """
        Generate or edit SimPy discrete-event simulation code.

        Delegate to this agent whenever simulation code needs to be created
        from scratch or modified. The agent reasons about the system structure,
        writes SimPy code, and iteratively repairs it until it executes
        without errors.

        Provide all simulation parameters and structural information the agent
        needs directly in the task description — it has no access to the
        dataset or prior conversation context.

        Args:
            task: Full description of what the simulation should model.
                  Include resources, routing, processing time distributions,
                  arrival patterns, and any special behaviors (batching,
                  priorities, shifts). Be explicit — the agent works only
                  from what you supply here.
            current_code: Existing SimPy code to modify, if any. When
                          provided, the agent edits rather than regenerates
                          from scratch. Pass None for initial generation.

        Returns:
            On success: validated, executable SimPy Python code as a string.
            On failure: a string starting with ``CODE_GENERATION_FAILED``
            containing the iteration count, the last error message, and the
            last code attempt (fenced in a python code block) so the caller
            can decide whether to retry or adjust the task description.
        """
        return run_workflow(
            user_prompt=task,
            dummy_knowledge="",   # superseded by task description
            config=_config,
            current_code=current_code,
        )

    return simpy_code_agent