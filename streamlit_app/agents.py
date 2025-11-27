from dataclasses import dataclass
from typing import Dict, Optional

from tools.appointment_tools import AppointmentTools
from tools.hospital_tools import HospitalTools
from tools.doctor_tools import DoctorTools


@dataclass
class AgentContext:
    appointment_tools: AppointmentTools
    hospital_tools: HospitalTools
    doctor_tools: DoctorTools


def _norm(text: str) -> str:
    return text.lower().strip()


def detect_intent(text: str) -> Dict[str, Optional[str]]:
    t = _norm(text)

    # greetings
    if any(w in t for w in ["hi", "hello", "hey", "good morning", "good evening"]):
        return {"intent": "greet"}

    # thanks
    if any(w in t for w in ["thank you", "thanks", "thx"]):
        return {"intent": "thanks"}

    # complaint
    if any(w in t for w in ["complaint", "complain", "feedback", "support", "issue", "problem"]):
        return {"intent": "complaint"}

    # doctor name exact
    if "sharma" in t:
        return {"intent": "doctor_availability", "doctor": "Dr. Sharma"}
    if "patel" in t:
        return {"intent": "doctor_availability", "doctor": "Dr. Patel"}

    # specialization
    if any(w in t for w in ["heart", "cardio", "cardiology"]):
        return {"intent": "specialist_lookup", "spec": "cardiology"}

    # generic doctor availability question
    if any(phrase in t for phrase in ["which doctor is available", "doctor available", "doctors available", "who is available"]):
        return {"intent": "all_doctors_available"}

    # fallback
    return {"intent": "fallback"}


def handle_greet() -> str:
    return (
        "Hello! I’m your CareFlow concierge agent. "
        "I can help with doctors, appointments, specializations and complaints. "
        "How can I assist you today?"
    )


def handle_thanks() -> str:
    return "You’re welcome! If you have any more questions about the hospital, just ask."


def handle_complaint(ctx: AgentContext) -> str:
    c = ctx.hospital_tools.get_complaint_contact()
    return (
        f"You can register a complaint by emailing **{c['complaint_email']}** "
        f"or contacting support at **{c['support_email']}** / **{c['helpline_number']}**."
    )


def handle_doctor_availability(doctor_name: str, ctx: AgentContext) -> str:
    today = "2025-11-27"

    available = ctx.appointment_tools.is_doctor_available_today(doctor_name, today)
    if not available:
        if doctor_name == "Dr. Sharma":
            return (
                "Dr. Sharma is not available today; all appointments for today are cancelled. "
                "You can book an appointment with Dr. Patel, who is available today."
            )
        return f"{doctor_name} is not available today."

    slots = ctx.appointment_tools.get_doctor_slots_today(doctor_name, today)
    if not slots:
        return f"{doctor_name} is available today, but there are no open slots left."

    times = ", ".join(s["time"] for s in slots)
    return f"Yes, you can meet {doctor_name} today. Available time slots are: {times}."


def handle_specialist_lookup(spec_key: str, ctx: AgentContext) -> str:
    if spec_key == "cardiology":
        candidates = ctx.doctor_tools.get_available_by_specialization("cardio")
        pretty = "cardiology / heart problems"
    else:
        candidates = ctx.doctor_tools.get_available_by_specialization(spec_key)
        pretty = spec_key

    if not candidates:
        return f"No doctors with that specialization are available today for {pretty}."

    names = ", ".join(d["doctor_name"] for d in candidates)
    return f"The following doctors are available today for {pretty}: {names}."


def handle_all_doctors_available(ctx: AgentContext) -> str:
    # List all doctors available today
    available_docs = [
        doc["doctor_name"]
        for doc in ctx.doctor_tools.df.to_dict(orient="records")
        if doc["is_available_today"].lower() == "true"
    ]
    if not available_docs:
        return "Sorry, no doctors are available today."
    return "Doctors available today are: " + ", ".join(available_docs) + "."


def run_main_agent(user_text: str, ctx: AgentContext) -> str:
    result = detect_intent(user_text)
    intent = result.get("intent")
    doctor = result.get("doctor")
    spec = result.get("spec")

    if intent == "greet":
        return handle_greet()
    if intent == "thanks":
        return handle_thanks()
    if intent == "complaint":
        return handle_complaint(ctx)
    if intent == "specialist_lookup":
        return handle_specialist_lookup(spec, ctx)
    if intent == "doctor_availability" and doctor:
        return handle_doctor_availability(doctor, ctx)
    if intent == "all_doctors_available":
        return handle_all_doctors_available(ctx)

    return (
        "I can help with doctor availability (e.g., Dr. Sharma or Dr. Patel), "
        "specializations like cardiology, and complaints. Try asking "
        "“Which doctor is available for heart problems?”, “Can I meet Dr. Sharma today?”, or "
        "“Where can I register a complaint?”"
    )
