import streamlit as st
import json
from experiment_generator import ExperimentGenerator
import os
import zipfile
import io

# --- Initialize ---
generator = ExperimentGenerator()

st.set_page_config(page_title="Experiment Generator", layout="wide")
st.title("🧪 Experiment Content Generator: v1.1")

# --- Sidebar Input ---
with st.sidebar:
    st.header("📝 Input")
    topic = st.text_input("Enter Experiment Topic", "")
    generate_button = st.button("Generate Content")

# --- Generate Content ---
generated_content = None
if generate_button and topic.strip():
    with st.status("Generating content, please wait...", expanded=True) as status:
        try:
            st.write("🔍 Generating experiment name...")
            experiment_name = generator.generate_experiment_name(topic)

            st.write("🎯 Generating aim...")
            aim = generator.generate_aim(topic)

            st.write("📋 Generating pretest questions...")
            pretest = generator.generate_quiz(topic, is_pretest=True)

            st.write("📋 Generating posttest questions...")
            posttest = generator.generate_quiz(topic, is_pretest=False)

            st.write("📚 Generating theory...")
            theory = generator.generate_theory(topic)

            st.write("⚙️ Generating procedure...")
            procedure = generator.generate_procedure(topic)

            st.write("🔗 Generating references...")
            references = generator.generate_references(topic)

            generated_content = {
                "experiment_name": experiment_name,
                "aim": aim,
                "pretest": pretest,
                "posttest": posttest,
                "theory": theory,
                "procedure": procedure,
                "references": references
            }

            status.update(label="✅ Content generated successfully!", state="complete")

        except Exception as e:
            st.error(f"Error during generation: {e}")
            status.update(label="❌ Failed to generate content", state="error")

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

# --- Download Section (inside sidebar) ---
with st.sidebar:
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