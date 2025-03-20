# src/models/state.py

from pydantic import BaseModel, Field
from typing import Dict, Optional, List

class ConversationState(BaseModel):
    json_data: Dict = Field(default_factory=dict)
    complete: bool = False
    current_field: Optional[str] = None
    question: Optional[str] = None
    iteration: int = 0
    max_iterations: int = 20
    history: List[Dict] = Field(default_factory=list)
    remaining_steps: int = 50

    def is_complete(self, schema_obj) -> bool:
        required_fields = schema_obj.get_required_fields(self.json_data)
        job_details = self.json_data.get("jobDetails", {})
        # Ensure every required field is present and no clarification is pending.
        return all(field in job_details and not job_details.get("clarification") for field in required_fields)
