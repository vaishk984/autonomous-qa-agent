"""LLM client for test case and script generation."""
import json
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

import config

class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate a response from the LLM."""
        pass


class GroqClient(BaseLLMClient):
    
    def __init__(self):
        from groq import Groq
        if not config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set. Please add it to your .env file.")
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.GROQ_MODEL
        print(f"Groq client initialized with model: {self.model}")
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {str(e)}")
            raise


class OllamaClient(BaseLLMClient):
    
    def __init__(self):
        import ollama
        self.client = ollama
        self.model = config.OLLAMA_MODEL
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        full_prompt = ""
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n"
        full_prompt += prompt
        
        response = self.client.generate(
            model=self.model,
            prompt=full_prompt
        )
        return response["response"]


def get_llm_client() -> BaseLLMClient:
    if config.LLM_PROVIDER == "groq":
        return GroqClient()
    elif config.LLM_PROVIDER == "ollama":
        return OllamaClient()
    else:
        raise ValueError(f"Unknown LLM provider: {config.LLM_PROVIDER}")


class QAAgent:
    """Agent for generating test cases and Selenium scripts."""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = get_llm_client()
    
    def generate_test_cases(self, user_query: str, n_context: int = 10) -> str:
        """Generate test cases based on user query and retrieved context."""
        
        # Retrieve relevant context
        context_results = self.vector_store.search(user_query, n_results=n_context)
        
        # Build context string with source attribution
        context_parts = []
        for result in context_results:
            source = result["metadata"].get("source_document", "unknown")
            content = result["content"]
            context_parts.append(f"[Source: {source}]\n{content}")
        
        context_str = "\n\n---\n\n".join(context_parts)
        
        system_prompt = """You are an expert QA engineer specializing in test case generation. 
Your task is to generate comprehensive test cases based STRICTLY on the provided documentation.

IMPORTANT RULES:
1. ONLY generate test cases for features explicitly mentioned in the documentation
2. NEVER invent or hallucinate features not in the documents
3. Each test case MUST reference the source document it's grounded in
4. Generate both positive and negative test cases
5. Be thorough but only test what's documented

Output format - Return a JSON array of test cases:
[
  {
    "test_id": "TC-001",
    "feature": "Feature Name",
    "test_scenario": "Description of what is being tested",
    "preconditions": ["List of preconditions"],
    "test_steps": ["Step 1", "Step 2", ...],
    "test_data": {"key": "value"},
    "expected_result": "Expected outcome",
    "test_type": "positive|negative",
    "priority": "high|medium|low",
    "grounded_in": "source_document.ext"
  }
]"""

        prompt = f"""Based on the following documentation, generate test cases for this request:

USER REQUEST: {user_query}

DOCUMENTATION CONTEXT:
{context_str}

Generate comprehensive test cases in the specified JSON format. Only include test cases that are directly supported by the provided documentation."""

        response = self.llm.generate(prompt, system_prompt)
        return response
    
    def generate_selenium_script(self, test_case: Dict[str, Any], html_content: str) -> str:
        """Generate a Selenium Python script for a specific test case."""
        
        # Get additional context from vector store
        feature = test_case.get("feature", "")
        context_results = self.vector_store.search(feature, n_results=5)
        
        context_parts = []
        for result in context_results:
            source = result["metadata"].get("source_document", "unknown")
            content = result["content"]
            context_parts.append(f"[Source: {source}]\n{content}")
        
        context_str = "\n\n".join(context_parts)
        
        system_prompt = """You are an expert Selenium automation engineer.
Your task is to generate clean, executable Python Selenium scripts.

REQUIREMENTS:
1. Use appropriate selectors (prefer IDs, then names, then CSS selectors)
2. Include proper waits (explicit waits preferred)
3. Add clear comments explaining each step
4. Include assertions to verify expected results
5. Handle potential errors gracefully
6. Make the script self-contained and runnable
7. Use the actual HTML structure provided - match selectors EXACTLY

Output ONLY the Python code, no explanations before or after."""

        prompt = f"""Generate a Selenium Python script for this test case:

TEST CASE:
{json.dumps(test_case, indent=2)}

HTML STRUCTURE (use these exact selectors):
{html_content}

ADDITIONAL CONTEXT:
{context_str}

Generate a complete, runnable Selenium Python script that:
1. Sets up the WebDriver
2. Navigates to the page
3. Executes the test steps
4. Verifies the expected result
5. Cleans up properly"""

        response = self.llm.generate(prompt, system_prompt)
        
        # Extract code block if present
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            if end > start:
                response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                response = response[start:end].strip()
        
        return response
    
    def parse_test_cases(self, llm_response: str) -> List[Dict[str, Any]]:
        """Parse LLM response to extract test cases."""
        # Try to find JSON in the response
        try:
            # Look for JSON array
            start_idx = llm_response.find("[")
            end_idx = llm_response.rfind("]") + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = llm_response[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # If JSON parsing fails, return the raw response wrapped
        return [{"raw_response": llm_response, "parse_error": True}]