import pandas as pd
from pathlib import Path

class DoctorTools:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.df = pd.read_csv(self.csv_path, dtype=str)

    def get_available_by_specialization(self, specialty_text: str):
        t = specialty_text.lower()
        matching = self.df["specialization"].str.lower().str.contains(t)
        available = self.df[matching & (self.df["is_available_today"].str.lower() == "true")]
        return available.to_dict(orient="records")

    def get_all_specializations(self):
        return sorted(set(self.df["specialization"].tolist()))
