"""
GenAI4Sim Agentic Workflow - LangGraph Implementation
Generates code using python and simpy for manufacturing simulation based on user prompts and factory knowledge.
"""
from pathlib import Path
from typing import Literal, List, Optional

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from src.common_utils import load_prompt
from dataclasses import dataclass, field
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from loguru import logger
from src.simpy_code_workflow.context_engineering.docs_knowledge_retriever import SimPyKnowledgeRetriever
import subprocess
import sys
from datetime import datetime

# ==================== load prompt templates ====================
PROMPTS_DIR = Path(__file__).parent / "prompts"
REASONING_PHASE_PROMPT = load_prompt(PROMPTS_DIR / "reasoning_step_prompt.md")
CODE_GENERATION_PROMPT = load_prompt(PROMPTS_DIR /"code_generation_prompt.md")
CODE_REPAIR_PROMPT = load_prompt(PROMPTS_DIR /"code_repair_prompt.md")
EDITING_STEPS_PROMPT = load_prompt(PROMPTS_DIR /"editing_steps_determination_prompt.md")
CODE_EDITING_PROMPT = load_prompt(PROMPTS_DIR /"code_editing_prompt.md")

# ==================== Pydantic Input Models ====================

class Input(BaseModel):
    """Input data structure for the GenAI4Sim workflow."""

    user_prompt: str = Field(
        ...,
        description="User's description of the manufacturing system to be modeled",
        max_length=3050
    )

    dummy_knowledge: str = Field(
        ...,
        description="Factory planning knowledge and context for the simulation",
        max_length=2048
    )

# ==================== Pydantic Output Models ====================
# class Code(BaseModel):
#     """Schema for code solutions from the coding assistant"""
#
#     code: str = Field(description="Python Code block implementing the solution including imports")

class CodeEdit(BaseModel):
    """Schema for code editing operations"""
    old_str: str = Field(description="Exact string to replace (must be unique)")
    new_str: str = Field(description="Replacement string")
    reason: str = Field(description="Why this edit is needed")

class CodeEditPlan(BaseModel):
    """Schema for multiple edit operations"""
    edits: List[CodeEdit] = Field(description="List of str_replace operations to perform")


# ==================== State Definition ====================

@dataclass
class State:
    user_prompt: str
    factory_planning_context: str = ""
    simpy_knowledge: str = ""
    current_code: Optional[str] = None
    code_history: List = field(default_factory=list)
    editing_steps: str = ""
    code_plan: str = ""
    code_generation_output: str = ""
    message: str = ""
    messages: List = field(default_factory=list)
    iteration: int = 0
    error_iterations: int = 0
    max_iterations: int = 5
    result: str = ""
    error: str = ""
    current_code_edits: Optional[CodeEditPlan] = None
    broken_edits: Optional[List[CodeEdit]] = None

# ==================== Graph Construction ====================

def create_workflow(llm: ChatOllama) -> StateGraph:
    """
    Create and compile the LangGraph workflow.
    """

    # ==================== Code Validation Function ====================

    def check_code(code: str):
        # check execution

        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        logger.debug(result.stdout)

        if result.returncode != 0:
            logger.error("---- Code Execution Failed ----")
            logger.error(f"Stdout: {result.stdout}")
            logger.error(f"Stderr: {result.stderr}")
            return False, HumanMessage(f"Your Code solution failed the code execution test:\n{result.stderr}")
        else:
            logger.info("---- Code Execution Succeeded ----")
            logger.debug(f"Stdout: {result.stdout}")
            return True, HumanMessage(content=f"Code executed successfully.")

    # ==================== Node Functions ====================

    def plan_node(state: State) -> State:
        """
        Analyze the manufacturing system and reason about its structure.
        """

        # get simpy knowledge reference
        state.simpy_knowledge = simpy_docs_retriever.retrieve(state.user_prompt)

        system_message = SystemMessage(content=f"""
        {REASONING_PHASE_PROMPT}
        
        ## Simpy Reference Knowledge:
        {state.simpy_knowledge}
        """)
        human_message = HumanMessage(content=state.user_prompt)

        messages = [
            system_message,
            human_message,
        ]

        reasoning_output = llm.invoke(messages)

        state.code_plan = reasoning_output.content
        return state

    def code_generation_node(state: State) -> State:

        # retrieve simpy knowledge reference with plan output
        state.simpy_knowledge = simpy_docs_retriever.retrieve(state.code_plan)
        system_message = SystemMessage(content=f"""
        {CODE_GENERATION_PROMPT}

        ## Simpy Reference Knowledge:
        {state.simpy_knowledge}
        """)
        human_message = HumanMessage(content=state.user_prompt)
        ai_message = AIMessage(content=state.code_plan)

        messages = [
            ai_message,
            human_message,
            system_message,
        ]
        code_output = llm.invoke(messages)

        # remove code block markers if present
        code_output.content = code_output.content.replace("```python", "").replace("```", "").strip()

        state.current_code = code_output.content
        state.message = code_output.content  # Initialize loop message
        state.iteration = 0
        state.max_iterations = 5  # Default max iterations for validation loop

        return state

    def code_validation_node(state: State) -> State:
        """
        Validate the generated code. If invalid, prepare for repair.
        """
        # import_result = check_imports(state.code_generation_output)
        code_execution_result = check_code(state.current_code)
        logger.info(f"Code validation result: {code_execution_result[0]}")

        if code_execution_result[0]:
            state.result = state.current_code
            state.error = ""

            # Add to history
            state.code_history.append({
                "iteration": len(state.code_history),
                "code": state.current_code,
                "prompt": state.user_prompt,
                "status": "validated"
            })
            # write current code to file for inspection
            with open(f"current_code_{datetime.now()}.py", "w", encoding="utf-8") as f:
                f.write(state.current_code)

            logger.info("Code validated successfully and saved to current_code")
        else:

            state.error = code_execution_result[1].content
            # Keep current message for repair

        state.iteration += 1

        return state

    def code_repair_node(state: State) -> State:
        """
        Repair invalid code based on validation errors.
        """
        prompt = CODE_REPAIR_PROMPT.format(
            current_code=state.current_code,
            error_message=state.error
        )

        repaired_code = llm.invoke(prompt)

        state.message = repaired_code.message  # Update message with repaired code

        return state

    def determine_editing_steps_node(state: State) -> State:
        """
        Analyze current code and user request to determine editing steps.
        """
        system_message = SystemMessage(content=EDITING_STEPS_PROMPT)

        if not state.error:
            # we are editing based on user request
            human_message = HumanMessage(
                content=f"{state.current_code}\n\n**User Request:**\n{state.user_prompt}"
            )
        else:
            # we are repairing based on validation error
            human_message = HumanMessage(
                content=f"{state.current_code}\n\n**Please fix the following Code error:**\n{state.error}"
            )

        messages = [system_message, human_message]

        editing_steps_output = llm.invoke(messages)
        state.editing_steps = editing_steps_output.content

        logger.info(f"Determined editing steps:\n{state.editing_steps}")

        return state

    def code_editing_node(state: State) -> State:
        """
        Edit existing code based on determined editing steps.
        """
        system_message = SystemMessage(content=CODE_EDITING_PROMPT)

        human_message = HumanMessage(
            content=f"{state.current_code}\n\n**Editing Steps:**\n{state.editing_steps}"
        )

        messages = [system_message, human_message]

        max_edit_iterations = 3
        broken_edits = []
        for edit_iteration in range(max_edit_iterations):
            # Get edit operations from LLM
            edit_plan = llm.with_structured_output(CodeEditPlan).invoke(messages)

            edited_code = state.current_code
            # Apply the edits sequentially
            for edit in edit_plan.edits:
                try:
                    # apply to imports or code based on where old_str is found
                    if edited_code.count(edit.old_str) == 1:
                        edited_code = edited_code.replace(edit.old_str, edit.new_str, 1)
                    elif edited_code.count(edit.old_str) > 1:
                        raise ValueError(
                            f"Multiple occurrences found for edit: {edit.reason} for String: {edit.old_str}")
                    else:
                        raise ValueError(
                            f"String to replace not found for edit: {edit.reason} for String: {edit.old_str}")
                except ValueError as ve:
                    logger.error(str(ve))
                    broken_edits.append(edit)
            # If no broken edits, break the loop
            if not broken_edits:
                break
            else:
                # Prepare messages for next iteration with broken edits feedback
                feedback = "\n".join([f"- {be.reason}: '{be.old_str}'" for be in broken_edits])
                feedback_message = HumanMessage(
                    content=f"The following edits could not be applied due to issues:\n{feedback}\nPlease revise your edit plan."
                )
                messages.append(feedback_message)
                broken_edits = []  # Reset for next iteration

        # Add current code to history before updating
        # fixme: adjust code history (imports missing, edits missing)
        state.code_history.append({
            "iteration": len(state.code_history),
            "code": state.current_code,
            "prompt": state.user_prompt,
            "editing_steps": state.editing_steps
        })

        # Update code generation output with edited code
        state.current_code = edited_code
        state.message = edited_code  # For validation loop
        state.iteration = 0
        state.max_iterations = 5

        return state

    def should_edit_or_generate(state: State) -> Literal["edit", "generate"]:
        """
        Determine whether to edit existing code or generate from scratch.
        """

        if state.current_code is not None:
            logger.info("Current code exists - using editing workflow")
            return "edit"
        else:
            logger.info("No current code - using generation workflow")
            return "generate"

    def should_continue_loop(state: State) -> Literal["continue", "exit"]:
        """
        Determine whether to continue the validation loop or exit.
        """
        # Exit if validation passed (result is set)
        if state.result:
            return "exit"

        # Exit if max iterations reached
        if state.iteration >= state.max_iterations:
            # Set result to last attempt even if invalid
            state.result = state.message
            return "exit"

        # Continue loop for repair
        return "continue"


    # Initialize the graph
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("reasoning_step", plan_node)
    workflow.add_node("code_generation", code_generation_node)
    workflow.add_node("determine_editing_steps", determine_editing_steps_node)
    workflow.add_node("code_editing", code_editing_node)
    workflow.add_node("code_validation", code_validation_node)
    #workflow.add_node("code_repair", code_repair_node)

    # Define the flow
    workflow.set_entry_point("reasoning_step")

    # Conditional: edit existing code or generate from scratch
    workflow.add_conditional_edges(
        "reasoning_step",
        should_edit_or_generate,
        {
            "edit": "determine_editing_steps",
            "generate": "code_generation"
        }
    )

    # Editing workflow path
    workflow.add_edge("reasoning_step", "code_generation")
    workflow.add_edge("determine_editing_steps", "code_editing")
    workflow.add_edge("code_editing", "code_validation")

    # Generation workflow path
    workflow.add_edge("code_generation", "code_validation")

    # Conditional loop: validation -> continue/exit
    workflow.add_conditional_edges(
        "code_validation",
        should_continue_loop,
        {
            "continue": "determine_editing_steps" ,  # loop back to editing for repairs
            "exit": END
        }
    )

    # # Loop back from repair to validation
    # workflow.add_edge("code_repair", "code_validation")

    # Compile the graph
    app = workflow.compile()

    # save the graph visualization
    # app.get_graph().draw_mermaid_png(output_file_path="simpy_code_agent_workflow.png")

    return app

llm = ChatOllama(
    model="stewartpark/qwen3.5:27b-bf16",
    base_url="http://localhost:41435",
    temperature=0.0
)

# init agent and docs retriever
simpy_docs_retriever = SimPyKnowledgeRetriever()
simpy_code_agent = create_workflow(llm)

# ==================== Main Execution ====================

def run_workflow(user_prompt: str, dummy_knowledge: str, config: RunnableConfig, current_code: str = None) -> str:
    """
    Execute the workflow with the given inputs.

    Args:
        user_prompt: User's description of the manufacturing system
        dummy_knowledge: Factory planning knowledge and context
        config: Configuration for the LLM and workflow
        current_code: Optional existing code to edit instead of generating from scratch

    Returns:
        SimPy code as Code object
    """
    # Validate inputs using Pydantic
    workflow_input = Input(
        user_prompt=user_prompt,
        dummy_knowledge=dummy_knowledge
    )

    # initialize base llm
    configuration = config.get("configurable", {})
    model_name = configuration.get("model_name", "qwen3.5:27b")

    initial_state = State(
    user_prompt= workflow_input.user_prompt,
    factory_planning_context= workflow_input.dummy_knowledge,
    simpy_knowledge = "",
    current_code= current_code,
    code_history= [],
    editing_steps= "",
    code_plan="",
    code_generation_output= "",
    message= "",
    messages= [],
    iteration= 0,
    error_iterations= 0,
    max_iterations= 5,
    result= "",
    error= "",
    current_code_edits=None,
    broken_edits=None
    )

    # Create and run the workflow
    final_state = simpy_code_agent.invoke(initial_state)

    if final_state.get("error"):
        return (
            f"CODE_GENERATION_FAILED\n"
            f"Iterations: {final_state['iteration']}\n"
            f"Last error:\n{final_state['error']}\n\n"
            f"Last code attempt:\n```python\n{final_state.get('result', '')}\n```"
        )
    return final_state["result"]



# ==================== Example Usage ====================

# if __name__ == "__main__":
#     # Example inputs
#     user_prompt = """
#     Create a simple assembly line in the python programming language using the simpy library with:
#     - 3 workstations in sequence
#     - Each workstation performs one operation
#     - Buffer capacity of 5 units between stations
#     - Cycle time of 30 seconds per operation
#     """
#
#     dummy_knowledge = """
#     """
#
#     config = RunnableConfig(
#         configurable={
#             "model_name": "qwen3.5:27b",
#             "base_url": "http://localhost:11434",
#             "temperature": 0.0,
#             "max_output_tokens": 64000,
#         }
#     )
#
#     # Run the workflow
#     result_code = run_workflow(user_prompt, dummy_knowledge, config)
#
#     print("Generated Code:")
#     print(result_code)


