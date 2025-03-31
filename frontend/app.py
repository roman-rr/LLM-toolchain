import streamlit as st
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="LangSmith Feedback", layout="wide")
st.title("📊 LangSmith LLM Call Feedback")

# Step 1: Select Project
with st.spinner("Loading projects..."):
    project_response = requests.get(f"{API_URL}/langsmith/projects")
    projects = project_response.json()
    project_names = [p["name"] for p in projects]

selected_project = st.selectbox("Select a LangSmith Project", project_names)

if selected_project:
    # Step 2: Load LLM Calls for the selected project
    with st.spinner(f"Fetching LLM runs for '{selected_project}'..."):
        response = requests.get(f"{API_URL}/langsmith/runs/{selected_project}")
        runs = response.json()

        if not runs:
            st.warning("No LLM runs found.")
        else:
            run_options = {
                f"{r['name']} – {datetime.fromisoformat(r['start_time'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')}"
                : r["id"] for r in runs
            }
            selected_run = st.selectbox("Select an LLM Call to Rate", list(run_options.keys()))

            selected_run_id = run_options[selected_run]
            selected_run_data = next(r for r in runs if r["id"] == selected_run_id)

            with st.container():
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.subheader("Input")
                    st.json(selected_run_data["inputs"])
                    if selected_run_data.get("outputs"):
                        st.subheader("Output")
                        st.json(selected_run_data["outputs"])

                with col2:
                    st.subheader("Submit Feedback")
                    score = st.slider("Rate this LLM call (1-5)", 1, 5, 3)
                    comment = st.text_area("Add a comment (optional)")
                    if st.button("Submit Feedback"):
                        payload = {
                            "run_id": selected_run_id,
                            "score": score,
                            "comment": comment
                        }
                        r = requests.post(f"{API_URL}/langsmith/submit", json=payload)
                        if r.status_code == 200:
                            st.success("✅ Feedback submitted!")
                        else:
                            st.error(f"❌ Failed to submit: {r.text}")