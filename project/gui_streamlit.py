import streamlit as st
import json
from experiment_generator import ExperimentGenerator
import os
import zipfile
import io

# --- Initialize ---
generator = ExperimentGenerator()

st.set_page_config(page_title="Experiment Generator", layout="wide")
st.title("🧪 Experiment Content Generator")

# --- Sidebar Input ---
with st.sidebar:
    st.header("📝 Input")
    topic = st.text_input("Enter Experiment Topic", "")
    generate_button = st.button("Generate Content")

# --- Generate Content ---
generated_content = None
if generate_button and topic.strip():
    try:
        with st.spinner("Generating content..."):
            generated_content = generator.generate_all_content(topic.strip())
            st.success("Content generated successfully!")
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")

# --- Preview Tabs ---
if generated_content:
    tabs = st.tabs([
        "Aim", "Experiment Name", "Pretest", "Posttest",
        "Theory", "Procedure", "References"
    ])

    # Render markdown tabs
    markdown_tabs = {
        "Aim": generated_content.get("aim", ""),
        "Experiment Name": generated_content.get("experiment_name", ""),
        "Theory": generated_content.get("theory", ""),
        "Procedure": generated_content.get("procedure", ""),
        "References": generated_content.get("references", "")
    }

    # JSON-style tabs
    json_tabs = {
        "Pretest": generated_content.get("pretest", {}),
        "Posttest": generated_content.get("posttest", {})
    }

    # Display markdown content
    for tab_name, content in markdown_tabs.items():
        with tabs[list(markdown_tabs.keys()).index(tab_name)]:
            st.markdown(content, unsafe_allow_html=True)

    # Display JSON content
    for tab_name, content in json_tabs.items():
        with tabs[list(json_tabs.keys()).index(tab_name) + len(markdown_tabs)]:
            st.code(json.dumps(content, indent=2), language="json")

# --- Download Section ---
if generated_content:
    st.markdown("### 📥 Download Content")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("aim.md", generated_content["aim"])
        zipf.writestr("experiment-name.md", generated_content["experiment_name"])
        zipf.writestr("pretest.json", json.dumps({"questions": generated_content["pretest"]}, indent=4))
        zipf.writestr("posttest.json", json.dumps({"questions": generated_content["posttest"]}, indent=4))
        zipf.writestr("theory.md", generated_content["theory"])
        zipf.writestr("procedure.md", generated_content["procedure"])
        zipf.writestr("reference.md", generated_content["references"])

    st.download_button(
        label="📦 Download as ZIP",
        data=buffer.getvalue(),
        file_name=f"{generated_content['experiment_name'].replace(' ', '_')}.zip",
        mime="application/zip"
    )