import os
import streamlit as st
import extra_streamlit_components as stx
from typing import TypedDict, Optional, List
from streamlit_local_storage import LocalStorage
from dotenv import load_dotenv

from labloom.content.main import ABOUT
from labloom.models import ModelParameters, get_llm
import base64

# Load environment variables
load_dotenv()

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="Lab Loom | Generate Pedagogically sound experiments in minutes",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "About": ABOUT,
    }
)

st.logo(
    "https://cdn.vlabs.ac.in/logo/vlabs-color-large-moe.png",
    icon_image="https://cdn.vlabs.ac.in/logo/vlabs-large-moe.png",
    size="large",
)

# ---------------------------------------------------
# Session State Management
# ---------------------------------------------------
class OutputState(TypedDict, total=False):
    requirements: str
    reviewed_requirements: str
    implementation: str
    coding_agent: str
    documentation: str
    website: str

class ControlState(TypedDict, total=False):
    current_step: str
    code_loop: int
    server_started: bool
    uploaded_file: object
    dark_mode: bool
    current_step: str

class UserModelState(TypedDict, total=False):
    chat_history: List

class PreviewRAGState(TypedDict, total=False):
    preview_url: Optional[str]
    rag_enabled: bool
    rag_documents: List
    rag_n_results: int

class SessionState(TypedDict, total=False):
    outputs: OutputState
    control: ControlState
    user_model: UserModelState
    preview_rag: PreviewRAGState



class Application:
    # https://ai.google.dev/gemini-api/docs/pricing
    MODELS = {
        "Gemini": [
            ("gemini-2.5-pro", "Gemini 2.5 Pro"),
            ("gemini-2.5-flash", "Gemini 2.5 Flash"),
            ("gemini-2.5-flash-lite-preview-06-17", "Gemini 2.5 Flash-Lite Preview 06-17"),
            ("gemini-2.0-flash", "Gemini 2.0 Flash"),
            ("gemini-2.0-flash-preview-image-generation", "Gemini 2.0 Flash Preview Image Generation"),
            ("gemini-2.0-flash-lite", "Gemini 2.0 Flash-Lite"),
        ]
    }
    EMBEDDING_MODELS = {
        "Gemini": [
            "gemini-embedding-exp"
        ]
    }
    TTS_MODELS = {
        "Gemini TTS": [
            "gemini-2.5-flash-preview-tts",
        ]
    }
    LIVE_MODELS = {
        "Gemini": [
            "gemini-live-2.5-flash-preview",
            "gemini-2.0-flash-live-001",
        ]
    }


    # Define phase map for easy index-based access and future extensibility
    PHASES = [
        ("Define Learning Objectives", "define_learning_objectives"),
        ("Instructional Strategy", "instructional_strategy"),
        ("Task & Assessment", "task_and_assessment"),
        ("Simulator Interactions", "simulator_interactions"),
        ("Storyboarding", "storyboarding"),
        ("Flowchart & Mindmap", "flowchart_and_mindmap"),
        ("Sandbox Preview (Later Phase)", "sandbox_preview"),
    ]
    PHASE_LABELS = [label for label, _ in PHASES]
    PHASE_KEYS = [key for _, key in PHASES]

    localS = LocalStorage()


    @staticmethod
    def init_session_state():
        """Initialize session state variables. or from local storage if available."""
        if "outputs" not in st.session_state:
            if Application.localS.getItem("outputs"):
                st.session_state.outputs = Application.localS.getItem("outputs")
            else:
                # Initialize with default values
                st.session_state.outputs = OutputState()
        if "control" not in st.session_state:
            if Application.localS.getItem("control"):
                st.session_state.control = Application.localS.getItem("control")
            else:
                # Initialize with default values
                st.session_state.control = ControlState()
        if "user_model" not in st.session_state:
            if Application.localS.getItem("user_model"):
                st.session_state.user_model = Application.localS.getItem("user_model")
            else:
                # Initialize with default values
                st.session_state.user_model = UserModelState()
        if "preview_rag" not in st.session_state:
            if Application.localS.getItem("preview_rag"):
                st.session_state.preview_rag = Application.localS.getItem("preview_rag")
            else:
                # Initialize with default values
                st.session_state.preview_rag = PreviewRAGState()
        if "model_parameters" not in st.session_state:
            if Application.localS.getItem("model_parameters"):
                st.session_state.model_parameters = Application.localS.getItem("model_parameters")
            else:
                # Initialize with default values
                st.session_state.model_parameters = ModelParameters(
                    selected_model="gemini-2.5-flash-lite-preview-06-17",
                    temperature=0.7,
                    max_tokens=1024,
                    gemini_token=os.getenv("GOOGLE_API_KEY", ""),
                    embedding_model="gemini-embedding-exp",
                    tts_model="gemini-2.5-flash-preview-tts",
                    live_model="gemini-live-2.5-flash-preview"
                )

    @staticmethod
    def set_llm_model(parameters: ModelParameters):
        """Set the LLM model parameters in session state"""
        st.session_state.llm = get_llm(parameters)

    @staticmethod
    def save_session_state():
        """Save session state to local storage."""
        # delete keys first
        Application.localS.deleteAll(key="outputs_remove")
        Application.localS.deleteAll(key="control_remove")
        Application.localS.deleteAll(key="user_model_remove")
        Application.localS.deleteAll(key="preview_rag_remove")
        Application.localS.deleteAll(key="model_parameters_remove")
        # then set them
        Application.localS.setItem("outputs", st.session_state.outputs, key="outputs")
        Application.localS.setItem("control", st.session_state.control, key="control")
        Application.localS.setItem("user_model", st.session_state.user_model, key="user_model")
        Application.localS.setItem("preview_rag", st.session_state.preview_rag, key="preview_rag")
        Application.localS.setItem("model_parameters", st.session_state.model_parameters, key="model_parameters")
    
    def __enter__(self):
        """Enter method to automatically save session state on exit."""
        Application.init_session_state()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        """Exit method to save session state."""
        Application.save_session_state()
        if exc_type is not None:
            st.error(f"An error occurred: {exc_value}")
        return False


def render_selectbox(label, options, key, default=None):
    """Reusable selectbox with default selection."""
    idx = options.index(default) if default in options else 0
    return st.selectbox(label, options, index=idx, key=key)

def render_model_selection():
    """Render AI model selection with temperature, max tokens, Gemini API token, and option to show model limits."""

    st.markdown("#### Gemini API Token")
    gemini_token = st.text_input(
        "Enter your Gemini API Token",
        type="password",
        value=st.session_state.model_parameters.get("gemini_token", ""),
        key="gemini_token_input",
        help="Paste your Gemini API token here. It will be used for all Gemini API requests."
    )

    model_tuples = Application.MODELS["Gemini"]
    model_keys, model_labels = zip(*model_tuples)
    default_model = st.session_state.model_parameters.get("selected_model", model_keys[0])

    selected_idx = st.selectbox(
        "Choose AI Model:",
        options=range(len(model_keys)),
        format_func=lambda i: model_labels[i],
        index=model_keys.index(default_model) if default_model in model_keys else 0,
        key="model_selector"
    )
    selected_model = model_keys[selected_idx]

    temp = st.slider("Temperature", 0.0, 1.0, st.session_state.model_parameters.get("temperature", 0.1), 0.01)
    max_tokens = st.number_input(
        "Max Tokens", min_value=1, max_value=1_000_000,
        value=st.session_state.model_parameters.get("max_tokens", 100_000),
        step=1,
        key="max_tokens_input"
    )

    # Show model limits button
    if st.button("📊 Show Model Limits", key="show_model_limits_btn"):
        st.session_state.show_model_limits = True

    if st.session_state.get("show_model_limits"):
        render_model_limits()

    # Check for changes and update if needed
    model_parameters = st.session_state.model_parameters
    changed = (
        selected_model != model_parameters.get("selected_model") or
        temp != model_parameters.get("temperature") or
        max_tokens != model_parameters.get("max_tokens") or
        gemini_token != model_parameters.get("gemini_token")
    )

    if changed or gemini_token:
        model_parameters.update({
            "selected_model": selected_model,
            "temperature": temp,
            "max_tokens": max_tokens,
            "gemini_token": gemini_token or os.getenv("GOOGLE_API_KEY", "")
        })

        Application.set_llm_model(ModelParameters(
            selected_model=selected_model,
            temperature=temp,
            max_tokens=max_tokens,
            gemini_token=gemini_token or ""
        ))
        st.session_state.model_parameters = model_parameters

        # st.success("✅ Model/settings updated automatically!")


def render_advanced_settings():
    """Render advanced settings for embedding and TTS models."""
    embedding_model = render_selectbox(
        "Embedding Model", Application.EMBEDDING_MODELS["Gemini"], "embedding_model_select",
        default=st.session_state.model_parameters.get("embedding_model", "gemini-embedding-exp")
    )
    tts_model = render_selectbox(
        "TTS Model", Application.TTS_MODELS["Gemini TTS"], "tts_model_select",
        default=st.session_state.model_parameters.get("tts_model", "gemini-2.5-flash-preview-tts")
    )
    live_model = render_selectbox(
        "Live Model", Application.LIVE_MODELS["Gemini"], "live_model_select",
        default=st.session_state.model_parameters.get("live_model", "gemini-live-2.5-flash-preview")
    )

    # Update session state with selected models
    if (
        embedding_model != st.session_state.model_parameters.get("embedding_model") or
        tts_model != st.session_state.model_parameters.get("tts_model") or
        live_model != st.session_state.model_parameters.get("live_model")
    ):
        st.session_state.model_parameters["embedding_model"] = embedding_model
        st.session_state.model_parameters["tts_model"] = tts_model
        st.session_state.model_parameters["live_model"] = live_model
        st.success("✅ Advanced settings updated successfully!")


def render_rag_settings():
    """Render RAG settings with preview URL, document upload, and results slider."""
    rag_enabled = st.checkbox("Enable RAG", key="rag_enabled", value=st.session_state.preview_rag.get("rag_enabled", False))
    preview_url = st.session_state.preview_rag.get("preview_url", "")
    rag_documents_objs = []
    rag_documents = st.session_state.preview_rag.get("rag_documents", [])
    n_results = st.session_state.preview_rag.get("rag_n_results", 5)
    if rag_enabled:
        preview_url = st.text_input(
            "Preview URL", value=st.session_state.preview_rag.get("preview_url", ""),
            key="rag_preview_url"
        )
        rag_documents_objs = st.file_uploader(
            "Upload Documents", type=["pdf", "txt"], key="rag_documents_uploader",
            accept_multiple_files=True
        )
        n_results = st.slider(
            "Number of Results", 1, 10, st.session_state.preview_rag.get("rag_n_results", 5), key="rag_n_results_slider"
        )
        if rag_documents_objs:    
            rag_documents = []
            for uploaded_file in rag_documents_objs:
                bytes_data = uploaded_file.read()
                if uploaded_file.type == "application/pdf":
                    # Handle PDF files: store as base64 encoded string
                    b64_content = base64.b64encode(bytes_data).decode("utf-8")
                    rag_documents.append({
                    "name": uploaded_file.name,
                    "type": "pdf",
                    "base64": True,
                    "content": b64_content
                    })
                elif uploaded_file.type == "text/plain":
                    # Handle text files
                    rag_documents.append({
                    "name": uploaded_file.name,
                    "type": "text",
                    "content": bytes_data.decode("utf-8")
                    })
                else:
                    st.warning(f"Unsupported file type: {uploaded_file.type}. Only PDF and text files are allowed.")
                    continue
            if len(rag_documents) > 0:
                st.session_state.preview_rag["rag_documents"] = rag_documents
                st.success(f"Uploaded {len(rag_documents)} document(s) successfully!")
    
    if (
        rag_enabled != st.session_state.preview_rag.get("rag_enabled", False) or
        preview_url != st.session_state.preview_rag.get("preview_url", "") or
        n_results != st.session_state.preview_rag.get("rag_n_results", 5)
    ):
        st.session_state.preview_rag["rag_enabled"] = rag_enabled
        st.session_state.preview_rag["preview_url"] = preview_url
        st.session_state.preview_rag["rag_n_results"] = n_results


@st.dialog("Gemini Model Limits")
def render_model_limits():
    st.markdown("### Gemini Model Limits")
    st.markdown("""
| Model | RPM | TPM | RPD |
|-------|-----|------|------|
| Gemini 2.5 Pro | -- | -- | -- |
| Gemini 2.5 Flash | 10 | 250,000 | 250 |
| Gemini 2.5 Flash-Lite Preview 06-17 | 15 | 250,000 | 1,000 |
| Gemini 2.5 Flash Preview TTS | 3 | 10,000 | 15 |
| Gemini 2.5 Pro Preview TTS | -- | -- | -- |
| Gemini 2.0 Flash | 15 | 1,000,000 | 200 |
| Gemini 2.0 Flash Preview Image Generation | 10 | 200,000 | 100 |
| Gemini 2.0 Flash-Lite | 30 | 1,000,000 | 200 |
| Imagen 3 | -- | -- | -- |
| Veo 2 | -- | -- | -- |
| Gemini 1.5 Flash (Deprecated) | 15 | 250,000 | 50 |
| Gemini 1.5 Flash-8B (Deprecated) | 15 | 250,000 | 50 |
| Gemini 1.5 Pro (Deprecated) | -- | -- | -- |
| Gemma 3 & 3n | 30 | 15,000 | 14,400 |
| Gemini Embedding Experimental 03-07 | 5 | -- | 100 |
""")
    st.info("RPM = Requests Per Minute, TPM = Tokens Per Minute, RPD = Requests Per Day")
    st.session_state.show_model_limits = False  # Reset state after showing limits





# setup sidebar
def setup_sidebar():
    """Setup the sidebar with tabs for phases, model settings, advanced settings, and RAG settings."""
    st.sidebar.title("Lab Loom")
    with st.sidebar:
        tab0, tab1, tab2, tab3 = st.tabs(["Phases", "Model", "Advanced", "RAG"])
        with tab0:
            st.markdown("### Experiment Design Phases")
            val = stx.stepper_bar(
                steps=Application.PHASE_LABELS,
                is_vertical=True,
                lock_sequence=False,
            )
            st.info(
                """
                **Instructions:**  
                - Click on a phase to view and fill in the required details.  
                - Your progress is saved automatically as you move between phases.
                """
            )

            if not isinstance(val, int):
                exit()
            selected_phase = Application.PHASE_LABELS[val]
            selected_phase_key = Application.PHASE_KEYS[val]
            st.session_state.control["current_step"] = {
                "label": selected_phase,
                "key": selected_phase_key
            }
    with tab1:
        st.header("Settings")
        st.subheader("Model Parameters")
        render_model_selection()
    with tab2:
        st.header("Advanced Settings")
        st.subheader("Model Parameters")
        render_advanced_settings()
    with tab3:
        st.header("RAG Settings")
        render_rag_settings()


# --- Phase Render Functions ---

def render_define_learning_objectives():
    st.subheader("Define Learning Objectives")
    st.markdown("Fill in Bloom's levels aligned to your experiment goals")
    with st.form("lo_form"):
        recall = st.text_area("Recall", value=st.session_state.outputs.get("recall", ""))
        understand = st.text_area("Understand", value=st.session_state.outputs.get("understand", ""))
        apply = st.text_area("Apply", value=st.session_state.outputs.get("apply", ""))
        analyze = st.text_area("Analyze", value=st.session_state.outputs.get("analyze", ""))
        evaluate = st.text_area("Evaluate", value=st.session_state.outputs.get("evaluate", ""))
        create = st.text_area("Create", value=st.session_state.outputs.get("create", ""))
        if st.form_submit_button("Save Objectives"):
            st.session_state.outputs.update({
                "recall": recall,
                "understand": understand,
                "apply": apply,
                "analyze": analyze,
                "evaluate": evaluate,
                "create": create,
            })
            st.success("Objectives saved successfully")

def render_instructional_strategy():
    st.subheader("Instructional Strategy")
    strategy = st.selectbox(
        "Select Strategy Type",
        ["Expository", "Guided Inquiry", "Problem Based", "Project Based"],
        index=["Expository", "Guided Inquiry", "Problem Based", "Project Based"].index(
            st.session_state.outputs.get("strategy", "Expository")
        ) if st.session_state.outputs.get("strategy") else 0,
    )
    strategy_desc = st.text_area(
        "Describe how the strategy is used in the experiment",
        value=st.session_state.outputs.get("strategy_desc", "")
    )
    if st.button("Save Instructional Strategy"):
        st.session_state.outputs.update({
            "strategy": strategy,
            "strategy_desc": strategy_desc,
        })
        st.success("Instructional strategy saved successfully")

def render_task_and_assessment():
    st.subheader("Task and Assessments")
    assessment_method = st.radio(
        "Assessment Method",
        ["Formative", "Summative", "Both"],
        index=["Formative", "Summative", "Both"].index(
            st.session_state.outputs.get("assessment_method", "Formative")
        ) if st.session_state.outputs.get("assessment_method") else 0,
    )
    sample_tasks = st.text_area(
        "Define sample tasks aligned with LOs",
        value=st.session_state.outputs.get("sample_tasks", "")
    )
    assessment_examples = st.text_area(
        "MCQ or Assessment Examples",
        value=st.session_state.outputs.get("assessment_examples", "")
    )
    if st.button("Save Task & Assessment"):
        st.session_state.outputs.update({
            "assessment_method": assessment_method,
            "sample_tasks": sample_tasks,
            "assessment_examples": assessment_examples,
        })
        st.success("Task & Assessment saved successfully")

def render_simulator_interactions():
    st.subheader("Simulator Interactions")
    student_action = st.text_input(
        "What will the student do?",
        value=st.session_state.outputs.get("student_action", "")
    )
    simulator_action = st.text_input(
        "What will the simulator do?",
        value=st.session_state.outputs.get("simulator_action", "")
    )
    task_purpose = st.text_input(
        "Purpose of the Task",
        value=st.session_state.outputs.get("task_purpose", "")
    )
    if st.button("Save Simulator Interactions"):
        st.session_state.outputs.update({
            "student_action": student_action,
            "simulator_action": simulator_action,
            "task_purpose": task_purpose,
        })
        st.success("Simulator interactions saved successfully")

def render_storyboarding():
    st.subheader("Storyboard")
    story_outline = st.text_area("Story Outline", value=st.session_state.outputs.get("story_outline", ""))
    visual_stage = st.text_area("Set the Visual Stage", value=st.session_state.outputs.get("visual_stage", ""))
    user_objectives = st.text_area("Set User Objectives & Goals", value=st.session_state.outputs.get("user_objectives", ""))
    pathway_activities = st.text_area("Set Pathway Activities", value=st.session_state.outputs.get("pathway_activities", ""))
    challenges = st.text_area("Set Challenges & Complexity", value=st.session_state.outputs.get("challenges", ""))
    pitfalls = st.text_area("Allow Pitfalls", value=st.session_state.outputs.get("pitfalls", ""))
    conclusion = st.text_area("Conclusion", value=st.session_state.outputs.get("conclusion", ""))
    st.markdown("Equations can be uploaded separately in the reference sheet.")
    if st.button("Save Storyboard"):
        st.session_state.outputs.update({
            "story_outline": story_outline,
            "visual_stage": visual_stage,
            "user_objectives": user_objectives,
            "pathway_activities": pathway_activities,
            "challenges": challenges,
            "pitfalls": pitfalls,
            "conclusion": conclusion,
        })
        st.success("Storyboard saved successfully")

def render_flowchart_and_mindmap():
    st.subheader("Flowchart and Mindmap Upload")
    flowchart_file = st.file_uploader(
        "Upload Flowchart (.png)",
        type=["png"],
        key="flowchart_file"
    )
    mindmap_file = st.file_uploader(
        "Upload Mindmap (.pdf)",
        type=["pdf"],
        key="mindmap_file"
    )
    st.markdown("[Use Google Drawings](https://docs.google.com/drawings/) and [FreeMind](http://freemind.sourceforge.net/wiki/index.php/Main_Page) for creation")
    if st.button("Save Flowchart & Mindmap"):
        if flowchart_file:
            st.session_state.outputs["flowchart_file"] = flowchart_file.getvalue()
            st.session_state.outputs["flowchart_filename"] = flowchart_file.name
        if mindmap_file:
            st.session_state.outputs["mindmap_file"] = mindmap_file.getvalue()
            st.session_state.outputs["mindmap_filename"] = mindmap_file.name
        st.success("Flowchart and Mindmap saved successfully")

def render_sandbox_preview():
    st.info("Sandbox generation is a later phase where the experiment will be auto-generated and previewed with live interactions.")

# --- Phase Map ---
PHASE_RENDER_MAP = {
    "define_learning_objectives": render_define_learning_objectives,
    "instructional_strategy": render_instructional_strategy,
    "task_and_assessment": render_task_and_assessment,
    "simulator_interactions": render_simulator_interactions,
    "storyboarding": render_storyboarding,
    "flowchart_and_mindmap": render_flowchart_and_mindmap,
    "sandbox_preview": render_sandbox_preview,
}


with Application() as app:
    # Setup sidebar
    setup_sidebar()

    # Main content area
    st.title("Lab Loom - Experiment Design Tool")
    st.markdown("Generate pedagogically sound experiments in minutes using AI.")

    # Display selected phase
    st.subheader(f"Current Phase: {st.session_state.control['current_step']}")
    # --- Main content for each phase ---
    current_step = st.session_state.control.get("current_step", {})
    selected_phase_key = current_step.get("key", "")

    render_func = PHASE_RENDER_MAP.get(selected_phase_key)
    if render_func:
        render_func()
