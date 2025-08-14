"""
Base Agent Classes and Error Tracking System

This module contains the foundational classes for all agents in the multi-agent system,
including error handling, retry logic, and circuit breaker patterns.
"""

import time
import json
from typing import List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from ..utils.state import State


# Global error tracking for circuit breaker pattern
class WorkflowErrorTracker:
    """Circuit breaker pattern implementation for API failure tracking"""
    
    def __init__(self, max_failures=5):
        self.failures = 0
        self.max_failures = max_failures
        self.circuit_open = False
    
    def record_failure(self):
        """Record an API failure and check if circuit should open"""
        self.failures += 1
        if self.failures >= self.max_failures:
            self.circuit_open = True
            print(f"🚨 CIRCUIT BREAKER ACTIVATED: Too many API failures ({self.failures})")
            print("🔧 Recommendations:")
            print("   1. Check your API keys and configuration")
            print("   2. Verify internet connectivity")
            print("   3. Check OpenRouter service status")
            print("   4. Consider switching to a different model")
    
    def record_success(self):
        """Record successful API call and reset circuit if needed"""
        if self.failures > 0:
            print(f"✅ API recovered after {self.failures} failures")
        self.failures = 0
        self.circuit_open = False
    
    def is_circuit_open(self):
        """Check if circuit breaker is currently open"""
        return self.circuit_open


# Global error tracker instance
error_tracker = WorkflowErrorTracker()


class BaseAgent:
    """
    Base class for all agents in the multi-agent system.
    
    Provides common functionality including:
    - LLM interaction with retry logic
    - Error handling and circuit breaker support
    - Fallback response generation
    - State management utilities
    """
    
    def __init__(self, system_prompt: str, llm: ChatOpenAI = None):
        self.system_prompt = system_prompt
        self.llm = llm
        self.max_retries = 2
        self.retry_delay = 2  # seconds
    
    def get_messages(self, content: str) -> List:
        """Create message list for LLM with system prompt and user content"""
        return [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=content)
        ]
    
    def invoke_llm_with_retry(self, messages, context=""):
        """
        Invoke LLM with retry logic, error handling, and circuit breaker
        
        Args:
            messages: List of messages to send to LLM
            context: Context description for error logging
            
        Returns:
            AIMessage: Response from LLM or fallback response
        """
        # Check circuit breaker
        if error_tracker.is_circuit_open():
            print(f"⚠️ Circuit breaker is open. Generating fallback response for {context}")
            return self.generate_fallback_response(context, "Circuit breaker activated")
        
        for attempt in range(self.max_retries):
            try:
                print(f"🔄 Attempting API call for {context} (attempt {attempt + 1}/{self.max_retries})...")
                response = self.llm.invoke(messages)
                print(f"✅ API call successful for {context}")
                error_tracker.record_success()
                return response
                
            except json.JSONDecodeError as e:
                print(f"❌ JSONDecodeError on attempt {attempt + 1} for {context}: {str(e)}")
                error_tracker.record_failure()
                
                if attempt < self.max_retries - 1 and not error_tracker.is_circuit_open():
                    print(f"⏳ Waiting {self.retry_delay} seconds before retry...")
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2  # Exponential backoff
                else:
                    print(f"❌ All API attempts failed for {context}. Generating fallback response")
                    return self.generate_fallback_response(context, f"JSONDecodeError: {str(e)}")
                    
            except Exception as e:
                print(f"❌ API Error on attempt {attempt + 1} for {context}: {str(e)}")
                error_tracker.record_failure()
                
                if attempt < self.max_retries - 1 and not error_tracker.is_circuit_open():
                    print(f"⏳ Waiting {self.retry_delay} seconds before retry...")
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2
                else:
                    print(f"❌ All API attempts failed for {context}. Generating fallback response")
                    return self.generate_fallback_response(context, f"API Error: {str(e)}")
        
        return self.generate_fallback_response(context, "Max retries exceeded")
    
    def generate_fallback_response(self, context="", error_details=""):
        """
        Generate a fallback response when API calls fail
        
        Args:
            context: Description of the operation context
            error_details: Specific error information
            
        Returns:
            AIMessage: Fallback response with error information
        """
        fallback_content = f"""
        FALLBACK RESPONSE - API Service Unavailable
        
        Agent: {self.__class__.__name__}
        Context: {context}
        Error: {error_details}
        
        This is a generated fallback response due to API connectivity issues.
        The workflow will continue with basic placeholder content.
        
        RECOMMENDATIONS:
        1. Check API key configuration in .env file
        2. Verify OpenRouter service status
        3. Check internet connectivity
        4. Consider rate limiting or quota exhaustion
        5. Try switching to a different model
        
        The campaign generation will continue with available data.
        Please manually review and enhance this section when API service is restored.
        """
        
        return AIMessage(content=fallback_content)
    
    @staticmethod
    def return_state(state: State, response, new_artifacts: dict = None, feedback: list = None) -> dict:
        """
        Create new state with updated artifacts and messages
        
        Args:
            state: Current workflow state
            response: LLM response or message
            new_artifacts: New artifacts to add to state
            feedback: Feedback messages to add
            
        Returns:
            dict: Updated state dictionary
        """
        return {
            "messages": [response] if response else [],
            "artifacts": {
                **state.get("artifacts", {}),
                **(new_artifacts or {})
            },
            "feedback": [*state.get("feedback", []), *(feedback or [])],
            "revision_count": state.get("revision_count", 0),
            "campaign_brief": state["campaign_brief"],
            "previous_artifacts": state.get("previous_artifacts", {}),
            "workflow_start_time": state.get("workflow_start_time", time.time())
        }
    
    def run(self, state: State) -> dict:
        """
        Main execution method for the agent.
        Should be implemented by each specific agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            dict: Updated state after agent execution
        """
        raise NotImplementedError("Each agent must implement the run method") 