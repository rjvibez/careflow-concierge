# streamlit_app/app.py

import sys
from pathlib import Path

# Add project root to Python path before importing anything else
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from tools.appointment_tools import AppointmentTools
from tools.hospital_tools import HospitalTools
from tools.doctor_tools import DoctorTools
from agents import AgentContext, run_main_agent


@st.cache_resource
def load_context() -> AgentContext:
    appt = AppointmentTools(ROOT_DIR / "data" / "appointments.csv")
    hosp = HospitalTools(ROOT_DIR / "data" / "hospital_info.json")
    docs = DoctorTools(ROOT_DIR / "data" / "doctors.csv")
    return AgentContext(
        appointment_tools=appt,
        hospital_tools=hosp,
        doctor_tools=docs,
    )


ctx = load_context()

st.set_page_config(
    page_title="CareFlow Concierge",
    page_icon="🏥",
    layout="centered",
)

st.title("🏥 CareFlow Concierge Agent")
st.caption("Ask about doctor availability, specializations, appointments, or how to register a complaint.")

with st.sidebar:
    st.header("About")
    st.write(
        "- Multi-agent concierge demo\n"
        "- Uses structured data (appointments, doctors, hospital info)\n"
        "- Handles greetings, doctor availability, specialization queries, and complaints"
    )
    st.markdown("---")
    st.write("Data files:")
    st.code(
        "data/appointments.csv\n"
        "data/doctors.csv\n"
        "data/hospital_info.json",
        language="text",
    )

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I’m your CareFlow concierge agent. Ask me about doctors, appointments, specializations, or complaints.",
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your question about the hospital..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    answer = run_main_agent(prompt, ctx)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
