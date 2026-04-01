"""
Configuration settings for the Self-Evolving Agent (Tetris/Code Generator).
Author: Danish (Dan-445)
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Model Configuration
GENERATION_MODEL = "gpt-4o-mini"
VERIFICATION_MODEL = "anthropic/claude-3-7-sonnet-20250219"

# Generation Settings
MAX_TOKENS_GEN = 16000
MAX_TOKENS_VERIFY = 20000

# Paths
DEFAULT_TARGET_DIRECTORY = "examples/output/tetris_game"

# Logging functionality
def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def validate_config():
    """Validate that necessary configuration is present."""
    if not OPENAI_API_KEY:
        logging.warning("OPENAI_API_KEY is missing. Code generation may fail.")
    if not ANTHROPIC_API_KEY:
        logging.warning("ANTHROPIC_API_KEY is missing. Code verification may fail.")
