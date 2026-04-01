"""
Core generation logic for the Self-Evolving Agent.
Author: Danish (Dan-445)
"""
import os
import logging
from typing import Dict, Any, Optional

# EvoAgentX imports
try:
    from evoagentx.models import OpenAILLMConfig, OpenAILLM, LiteLLMConfig, LiteLLM
    from evoagentx.workflow import WorkFlowGenerator, WorkFlowGraph, WorkFlow
    from evoagentx.agents import AgentManager
    from evoagentx.actions.code_extraction import CodeExtraction
    from evoagentx.actions.code_verification import CodeVerification
    from evoagentx.core.module_utils import extract_code_blocks
except ImportError:
    # Handle missing dependencies gracefully for static analysis/verification
    logging.error("EvoAgentX not found. Please install requirements.")

from config import (
    OPENAI_API_KEY, 
    ANTHROPIC_API_KEY, 
    GENERATION_MODEL, 
    VERIFICATION_MODEL,
    MAX_TOKENS_GEN,
    MAX_TOKENS_VERIFY
)

logger = logging.getLogger(__name__)

class CodeGeneratorAgent:
    """
    Agent responsible for generating, verifying, and extracting code based on a goal.
    """
    
    def __init__(self):
        self._setup_llms()
        self.agent_manager = AgentManager()
        self.workflow_generator = WorkFlowGenerator(llm=self.gen_llm)

    def _setup_llms(self):
        """Initialize LLM configurations."""
        # Generation LLM (OpenAI)
        self.gen_config = OpenAILLMConfig(
            model=GENERATION_MODEL, 
            openai_key=OPENAI_API_KEY, 
            stream=True, 
            output_response=True, 
            max_tokens=MAX_TOKENS_GEN
        )
        self.gen_llm = OpenAILLM(config=self.gen_config)

        # Verification LLM (Anthropic/LiteLLM)
        self.verify_config = LiteLLMConfig(
            model=VERIFICATION_MODEL, 
            anthropic_key=ANTHROPIC_API_KEY, 
            stream=True, 
            output_response=True, 
            max_tokens=MAX_TOKENS_VERIFY
        )
        self.verify_llm = LiteLLM(config=self.verify_config)

    def generate_code(self, goal: str, target_directory: str) -> None:
        """
        Executes the workflow to generate, verify, and save code.
        
        Args:
            goal: The natural language description of the task.
            target_directory: Directory to save the output.
        """
        logger.info(f"Starting code generation for goal: {goal}")
        
        # 1. Generate Workflow
        logger.info("Generating workflow...")
        try:
            workflow_graph: WorkFlowGraph = self.workflow_generator.generate_workflow(goal=goal)
            # workflow_graph.display() # Optional: display graph
        except Exception as e:
            logger.error(f"Failed to generate workflow: {e}")
            raise

        # 2. Setup Agents
        logger.info("Initializing agents from workflow...")
        self.agent_manager.add_agents_from_workflow(workflow_graph, llm_config=self.gen_config)

        # 3. Execute Workflow
        logger.info("Executing workflow...")
        workflow = WorkFlow(graph=workflow_graph, agent_manager=self.agent_manager, llm=self.gen_llm)
        raw_output = workflow.execute()
        
        # 4. Verify Code
        logger.info("Verifying generated code...")
        verified_code = self._verify_code(goal, raw_output)

        # 5. Extract and Save
        logger.info(f"Extracting code to {target_directory}...")
        self._extract_and_save(verified_code, target_directory)

    def _verify_code(self, goal: str, code_output: str) -> str:
        """Run code verification action."""
        verifier = CodeVerification()
        try:
            result = verifier.execute(
                llm=self.verify_llm,
                inputs={
                    "requirements": goal,
                    "code": code_output
                }
            )
            return result.verified_code
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return code_output # Fallback to original output

    def _extract_and_save(self, code_content: str, target_directory: str) -> None:
        """Extract code blocks and save to files."""
        os.makedirs(target_directory, exist_ok=True)
        
        # Simple extraction for single block (e.g. HTML)
        code_blocks = extract_code_blocks(code_content)
        if len(code_blocks) == 1:
            file_path = os.path.join(target_directory, "index.html") # Default assumption as per original
            try:
                with open(file_path, "w") as f:
                    f.write(code_blocks[0])
                logger.info(f"Saved single code block to {file_path}")
                print(f"You can open this HTML file in a browser: {file_path}")
                return
            except IOError as e:
                logger.error(f"Failed to write file: {e}")
                return

        # Complex extraction using Agent
        logger.info("Using CodeExtraction agent for multiple files...")
        extractor = CodeExtraction()
        try:
            results = extractor.execute(
                llm=self.gen_llm,
                inputs={
                    "code_string": code_content,
                    "target_directory": target_directory,
                }
            )
            
            logger.info(f"Extracted {len(results.extracted_files)} files.")
            for filename, path in results.extracted_files.items():
                logger.info(f"  - {filename}: {path}")
            
            if results.main_file:
                logger.info(f"Main entry point: {results.main_file}")

        except Exception as e:
            logger.error(f"Code extraction failed: {e}")
