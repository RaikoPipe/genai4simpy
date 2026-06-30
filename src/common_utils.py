from pathlib import Path

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document


def load_prompt(prompt_path: Path) -> str:
    """Load and validate prompt from markdown file.

    Args:
        prompt_path: prompt filename within the package 'prompts' directory.
                      e.g., "simpy_code_agent/reasoning_step_prompt.md"
    """
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    # Load prompt
    prompt_loader = UnstructuredMarkdownLoader(str(prompt_path))
    prompt_doc = prompt_loader.load()

    assert len(prompt_doc) == 1
    assert isinstance(prompt_doc[0], Document)

    return prompt_doc[0].page_content
