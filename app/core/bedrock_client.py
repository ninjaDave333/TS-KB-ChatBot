import re
import json
from pathlib import Path
from typing import Dict, Any
from .llm_client import LLMClient
from .prompt_profiles import classify_question_intent, get_prompt_for_intent
from .cypher_validator import validate_and_clean, suggest_correction

class BedrockClient:
    def __init__(self, llm_client: LLMClient = None):
        """Initialize with LLMClient for actual model calls."""
        self.llm_client = llm_client or LLMClient()
        self.best_config = self._load_best_config()
        print(f"BedrockClient initialized with self-learning logic, temperature={self.best_config.get('temperature', 0.1)}")
    
    def _load_best_config(self) -> Dict[str, Any]:
        """Load best config from training."""
        config_path = Path("data/best_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {"temperature": 0.1, "prompt_profile": "strict_v1"}
    
    async def generate_cypher(self, user_query: str, schema: Dict[str, Any], trace=None) -> tuple[str, str, int]:
        """
        Generate Cypher queries using intent-based routing and validation retry.
        
        Returns: (cypher_query, intent, validation_attempts)
        
        Flow:
        1. Classify intent (sales_v1, calendar_v1, product_v1, strict_v1)
        2. Get intent-specific prompts
        3. Generate Cypher with LLM
        4. Validate and clean
        5. Retry with correction if validation fails (max 2 attempts)
        """
        
        if not self.llm_client:
            raise Exception("LLMClient not initialized")
        
        # Step 1: Classify intent
        intent = classify_question_intent(user_query)
        print(f"[Intent Classification] Detected: {intent}")
        
        # Step 2: Get intent-specific prompts
        system_prompt, user_prompt = get_prompt_for_intent(intent, user_query)
        
        # Step 3: Get temperature from best config
        temperature = self.best_config.get("temperature", 0.1)
        
        # Step 4: Generate Cypher with validation retry (max 2 attempts)
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                # Record prompts in trace
                if trace:
                    trace.prompt_system = system_prompt
                    trace.prompt_user = user_prompt
                    trace.llm_model_role = "primary"
                    trace.intent = intent  # Add intent to trace
                    from .config import get_model_config
                    model_config = get_model_config("primary")
                    trace.llm_model_id = model_config.get("model_id", "unknown")
                
                # Generate Cypher
                raw_cypher = await self.llm_client.complete(
                    system_prompt, 
                    user_prompt, 
                    role="primary", 
                    max_tokens=4096,
                    temperature=temperature if attempt == 0 else 0.0  # Drop to 0.0 on retry
                )
                
                print(f"[Attempt {attempt + 1}] Raw LLM output: {raw_cypher[:200]}...")
                
                # Validate and clean
                cypher, errors = validate_and_clean(raw_cypher)
                
                if not errors:
                    print(f"[Validation] ✓ Passed on attempt {attempt + 1}")
                    print(f"[Final Cypher] {cypher}")
                    return cypher, intent, attempt + 1
                
                # Validation failed
                print(f"[Validation] ✗ Failed on attempt {attempt + 1}: {errors}")
                
                if attempt < max_attempts - 1:
                    # Retry with correction guidance
                    error_msg = "; ".join(errors)
                    correction = suggest_correction(cypher or raw_cypher, error_msg)
                    
                    user_prompt = (
                        f"Question: {user_query}\n\n"
                        f"Your previous response had errors: {error_msg}\n"
                        f"Correction needed: {correction}\n"
                        f"Generate a corrected Cypher query using proper Neo4j Cypher syntax.\n"
                        f"Return ONLY the corrected Cypher query."
                    )
                    print(f"[Retry] Attempting correction with temperature=0.0")
                else:
                    # Max attempts reached
                    raise ValueError(f"Query validation failed after {max_attempts} attempts: {error_msg}")
                    
            except Exception as e:
                if attempt < max_attempts - 1:
                    print(f"[Error] Attempt {attempt + 1} failed: {e}, retrying...")
                    continue
                else:
                    print(f"[Error] All attempts failed: {e}")
                    raise
        
        raise ValueError("Failed to generate valid Cypher after all attempts")
    
    async def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        """
        Generate natural language text using LLM.
        Used for answer rendering and explanations.
        """
        if not self.llm_client:
            raise Exception("LLMClient not initialized")
        
        return await self.llm_client.complete(
            system_prompt,
            user_prompt,
            role="primary",
            max_tokens=2048,
            temperature=temperature
        )
