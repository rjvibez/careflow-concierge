import json
from pathlib import Path

class HospitalTools:
    def __init__(self, json_path: str):
        self.json_path = Path(json_path)
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.info = json.load(f)

    def get_complaint_contact(self):
        return {
            "complaint_email": self.info.get("complaint_email"),
            "support_email": self.info.get("support_email"),
            "helpline_number": self.info.get("helpline_number"),
        }
