import streamlit as st
from cyber_agent import CyberAgent

st.title("Agentic Cybersecurity Workflow Dashboard")

target = st.text_input("Enter target domain (e.g., google.com):", "google.com")
if st.button("Start Scan"):
    st.info("Starting scan... Check logs in the terminal for detailed output.")
    agent = CyberAgent(target)
    agent.run()
    st.success("Scan completed! Check the generated report file for details.")
