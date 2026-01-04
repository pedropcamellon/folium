"""Clinical summarization prompt templates."""

from pathlib import Path

# Load prompts from external markdown files
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(filename: str) -> str:
    """Load prompt from markdown file."""
    prompt_path = PROMPTS_DIR / filename
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8").strip()


def get_prompt_template(format: str = "soap") -> str:
    """Get prompt template for specified format.

    Args:
        format: Output format ('soap' or 'narrative')

    Returns:
        Prompt template string
    """
    # Default to SOAP if format is None or empty
    if not format or format.lower() == "soap":
        return load_prompt("soap.md")
    if format.lower() == "narrative":
        return load_prompt("narrative.md")
    return load_prompt("soap.md")


def format_prompt(transcript: str, format: str = "soap") -> str:
    """Format a complete prompt from transcript and format.

    Args:
        transcript: Clinical transcript text
        format: Output format ('soap' or 'narrative')

    Returns:
        Formatted prompt string
    """
    template = get_prompt_template(format)
    return f"{template}\n\n**Transcript:**\n{transcript}\n\n**Generate JSON:**"
