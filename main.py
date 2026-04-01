"""
Main entry point for the Self-Evolving Agent application.
Author: Danish (Dan-445)
"""
import sys
from config import setup_logging, validate_config, DEFAULT_TARGET_DIRECTORY
from generator import CodeGeneratorAgent

def main():
    # Setup
    setup_logging()
    validate_config()

    # Define Goal
    # In a real app, this could come from CLI args or UI
    goal = "Generate html code for the Tetris game that can be played in the browser."
    target_dir = DEFAULT_TARGET_DIRECTORY
    
    # Initialize and Run
    try:
        agent = CodeGeneratorAgent()
        agent.generate_code(goal=goal, target_directory=target_dir)
        print("\n✅ Task Completed Successfully!")
        
    except Exception as e:
        print(f"\n❌ Application Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
