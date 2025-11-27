import pandas as pd
from pathlib import Path
from datetime import date as date_cls

class AppointmentTools:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.df = pd.read_csv(self.csv_path, dtype=str)
        # ensure date/time are strings for simple filtering

    def is_doctor_available_today(self, doctor_name: str, today_str: str | None = None) -> bool:
        """Return True if doctor has at least one NON-cancelled appointment today."""
        if today_str is None:
            today_str = date_cls.today().strftime("%Y-%m-%d")

        q = self.df[
            (self.df["doctor_name"].str.lower() == doctor_name.lower())
            & (self.df["date"] == today_str)
        ]
        if q.empty:
            # no schedule at all today → treat as not available
            return False

        # if all are cancelled, doctor effectively off / on leave
        active = q[~q["status"].str.lower().isin(["cancelled"])]
        return not active.empty

    def get_doctor_slots_today(self, doctor_name: str, today_str: str | None = None):
        if today_str is None:
            today_str = date_cls.today().strftime("%Y-%m-%d")
        q = self.df[
            (self.df["doctor_name"].str.lower() == doctor_name.lower())
            & (self.df["date"] == today_str)
            & (~self.df["status"].str.lower().isin(["cancelled"]))
        ].sort_values("time")
        return q[["time", "location"]].to_dict(orient="records")
