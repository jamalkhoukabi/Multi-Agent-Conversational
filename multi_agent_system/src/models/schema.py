# src/models/schema.py

class JSONSchema:
    def __init__(self):
        # Define the expected structure for the Job Details JSON.
        self.schema_def = {
            "jobDetails": {
                "type": "object",
                "required": True,
                "properties": {
                    "title": {"type": "string", "required": True},
                    "description": {"type": "string", "required": True},
                    "discipline": {"type": "string", "required": True},
                    "availability": {"type": "number", "required": True},  # in weeks
                    "seniority": {"type": "string", "required": True},  # e.g., JUNIOR, MID, SENIOR
                    "languages": {"type": "array", "required": True},  # expected as array of objects
                    "skills": {"type": "array", "required": True},     # expected as array of objects
                    "type": {"type": "string", "required": True},       # REMOTE, ONSITE, HYBRID
                    "jobType": {"type": "string", "required": True},    # FREELANCE, FULLTIME, PARTTIME
                    # For REMOTE positions:
                    "countries": {"type": "array", "required": False},
                    "continents": {"type": "array", "required": False},
                    "regions": {"type": "array", "required": False},
                    "timeZone": {"type": "object", "required": False},
                    # For ONSITE/HYBRID positions:
                    "country": {"type": "object", "required": False},
                    "city": {"type": "string", "required": False},
                    # For FREELANCE jobs:
                    "minHourlyRate": {"type": "number", "required": False},
                    "maxHourlyRate": {"type": "number", "required": False},
                    "weeklyHours": {"type": "number", "required": False},
                    "estimatedWeeks": {"type": "number", "required": False},
                    # For FULLTIME jobs:
                    "minFullTimeSalary": {"type": "number", "required": False},
                    "maxFullTimeSalary": {"type": "number", "required": False},
                    # For PARTTIME jobs:
                    "minPartTimeSalary": {"type": "number", "required": False},
                    "maxPartTimeSalary": {"type": "number", "required": False}
                }
            }
        }
    
    def get_required_fields(self, current_data: dict) -> list:
        # Get the current jobDetails data (or an empty dict if missing)
        job_details = current_data.get("jobDetails", {})
        # Start with all properties marked as required in the schema_def
        base_required = [
            key for key, prop in self.schema_def["jobDetails"]["properties"].items()
            if prop.get("required")
        ]
        required = set(base_required)
        
        # Dynamically add extra required fields based on the provided values
        job_type = job_details.get("jobType", "").upper()
        position_type = job_details.get("type", "").upper()
        
        if position_type == "REMOTE":
            required.update(["countries", "continents", "regions", "timeZone"])
        elif position_type in ["ONSITE", "HYBRID"]:
            required.update(["country", "city"])
        
        if job_type == "FREELANCE":
            required.update(["minHourlyRate", "maxHourlyRate", "weeklyHours", "estimatedWeeks"])
        elif job_type == "FULLTIME":
            required.update(["minFullTimeSalary", "maxFullTimeSalary"])
        elif job_type == "PARTTIME":
            required.update(["minPartTimeSalary", "maxPartTimeSalary"])
        
        return list(required)
