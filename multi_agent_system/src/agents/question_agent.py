# src/agents/question_agent.py

from .base_agent import BaseAgent, AgentConfig

class QuestionAgent(BaseAgent):
    def __init__(self, config: AgentConfig, schema):
        super().__init__(config)
        self.schema = schema

    def next_question(self, current_data: dict, history: list = None) -> str:
        prompt_template = """
You are a smart AI agent assisting a user in filling out a Job Details JSON object. The final JSON must have the following structure:

{{
  "jobDetails": {{
    "title": "string",
    "description": "string",
    "discipline": "Fullstack",
    "availability": 0,  // weeks
    "seniority": "JUNIOR",  // must be one of JUNIOR, MID, SENIOR
    "languages": [
      {{
        "name": "string",
        "level": "string",
        "required": true
      }}
    ],
    "skills": [
      {{
        "name": "string",
        "mandatory": true
      }}
    ],
    "type": "REMOTE",  // must be one of REMOTE, ONSITE, HYBRID
    "jobType": "FREELANCE",  // must be one of FREELANCE, FULLTIME, PARTTIME

    // For REMOTE positions only:
    "countries": [
      {{ "name": "string" }}
    ],
    "continents": [
      {{ "name": "string" }}
    ],
    "regions": [
      {{ "name": "string" }}
    ],
    "timeZone": {{
      "name": "string",
      "overlap": 0
    }},

    // For ONSITE/HYBRID positions:
    "country": {{ "name": "string" }},
    "city": "string",

    // For FREELANCE jobs:
    "minHourlyRate": 0,
    "maxHourlyRate": 0,
    "weeklyHours": 0,
    "estimatedWeeks": 0,

    // For FULLTIME jobs:
    "minFullTimeSalary": 0,
    "maxFullTimeSalary": 0,

    // For PARTTIME jobs:
    "minPartTimeSalary": 0,
    "maxPartTimeSalary": 0
  }}
}}

Current Job Details Data: {current_data}
Conversation History: {history}
Schema: {schema}

Instructions:
1. Identify any missing or invalid required fields based on the above schema.
2. Ask a clear and concise question to obtain the missing or corrected value.
3. If all required fields are valid, ask an open-ended follow-up question.
4. Respond ONLY with the question text.
"""
        formatted_prompt = prompt_template.format(
            current_data=current_data,
            history=history or [],
            schema=self.schema.schema_def
        )
        question = self._call_llm(formatted_prompt)
        return question
