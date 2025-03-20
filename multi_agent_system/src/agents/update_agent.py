# src/agents/update_agent.py

import json
import re
import logging
from typing import Dict, List
from .base_agent import BaseAgent, AgentConfig

class UpdateAgent(BaseAgent):
    def __init__(self, config: AgentConfig, schema):
        super().__init__(config)
        self.schema = schema
        self.logger = logging.getLogger(self.__class__.__name__)

    def _build_prompt(self, state: Dict, response: str, history: List = None) -> str:
        prompt_template = """
You are an AI assistant. Based on the current Job Details data, conversation history, and user response, update the JSON object accordingly. The final JSON must have the structure:

{{
  "jobDetails": {{ ... }}
}}

Current State: {state}
Conversation History: {history}
User Response: {response}
Schema: {schema}

Instructions:
1. If the user provides a valid update for a required field (matching the expected type and structure), return a JSON object that updates the "jobDetails" section with that field and its new value.
2. If the provided value is invalid or does not match the expected structure, return a JSON object with a key "clarification" and a message guiding the user to provide the correct format.
3. If the user's response does not correspond to any specific field, update (or append to) the "additionalInfo" field inside "jobDetails".
4. Return ONLY a single-line valid JSON object with no extra text.
"""
        formatted_prompt = prompt_template.format(
            state=state,
            history=history or [],
            response=response,
            schema=self.schema.schema_def
        )
        return self._call_llm(formatted_prompt)

    def update_state(self, current_state: Dict, response: str, history: List = None) -> Dict:
        llm_response = self._build_prompt(current_state, response, history)
        try:
            return self._validate_update(current_state, llm_response)
        except Exception as e:
            self.logger.error(f"State update failed: {e}")
            return current_state or {}

    def _validate_update(self, original: Dict, updated: str) -> Dict:
        json_str = updated.strip()
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError:
            self.logger.error(f"JSON decode error. Attempting extraction from: {updated}")
            match = re.search(r'({.*})', updated, re.DOTALL)
            if match:
                json_str = match.group(1)
                parsed = json.loads(json_str)
            else:
                self.logger.error("No JSON object could be extracted from the response.")
                return original or {}

        # If a clarification is provided, add it inside jobDetails and return
        if "clarification" in parsed:
            if "jobDetails" not in original:
                original["jobDetails"] = {}
            original["jobDetails"]["clarification"] = parsed["clarification"]
            return original

        # Ensure that the update applies to the "jobDetails" section.
        if "jobDetails" not in parsed:
            parsed = {"jobDetails": parsed}

        # Merge updates into the original state.
        new_state = original.copy()
        if "jobDetails" not in new_state:
            new_state["jobDetails"] = {}

        # Merge additionalInfo if it exists.
        if "additionalInfo" in parsed["jobDetails"]:
            existing = new_state["jobDetails"].get("additionalInfo", "")
            new_info = parsed["jobDetails"]["additionalInfo"]
            new_state["jobDetails"]["additionalInfo"] = existing + " | " + new_info if existing else new_info

        # Merge all other keys.
        for key, value in parsed["jobDetails"].items():
            if key == "additionalInfo":
                continue
            new_state["jobDetails"][key] = value

        return new_state
