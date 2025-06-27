import streamlit as st
import json
import os
import zipfile
import io
from langgraph_experiment_generator import SandboxGenerator, SandboxState, SystemPrompts

# Page configuration
st.set_page_config(
    page_title="🧪 Human-in-the-Loop Sandbox Generator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .step-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .content-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .feedback-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    .progress-container {
        margin: 1rem 0;
    }
    .chat-message {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        word-wrap: break-word;
    }
    .chat-user {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .chat-ai {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .settings-box {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        background-color: #fafafa;
    }
    .stButton > button {
        border-radius: 0.5rem;
    }
    .stTextInput > div > div > input {
        border-radius: 0.5rem;
    }
    .stSelectbox > div > div > select {
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generator' not in st.session_state:
    st.session_state.generator = SandboxGenerator()
    st.session_state.current_state = None
    st.session_state.is_generating = False
    st.session_state.completed = False
    st.session_state.feedback = ""
    st.session_state.action = ""
    st.session_state.chat_history = []
    st.session_state.selected_model = "gemini-2.5-flash-preview-05-20"

# Main header
st.markdown('<h1 class="main-header">🧪 Human-in-the-Loop Sandbox Generator</h1>', unsafe_allow_html=True)

# Create 3 columns
left_col, middle_col, right_col = st.columns([1, 2, 1])

# Left Column - Settings
with left_col:
    st.markdown('<h3 class="step-header">⚙️ Settings</h3>', unsafe_allow_html=True)
    
    # AI Model Selection
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    st.subheader("🤖 AI Model")
    model_options = {
        "gemini-2.5-flash-preview-05-20": "Gemini 2.5 Flash (Recommended)",
        "gemini-1.5-flash": "Gemini 1.5 Flash",
        "gemini-1.5-pro": "Gemini 1.5 Pro",
        "gpt-4": "GPT-4 (OpenAI)",
        "gpt-3.5-turbo": "GPT-3.5 Turbo (OpenAI)"
    }
    
    selected_model = st.selectbox(
        "Choose AI Model:",
        options=list(model_options.keys()),
        index=0,
        format_func=lambda x: model_options[x],
        key="model_selector"
    )
    
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        try:
            st.session_state.generator.update_model(selected_model)
            st.success(f"Model changed to: {model_options[selected_model]}")
        except Exception as e:
            st.error(f"Failed to update model: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sandbox Setup
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    st.subheader("🎯 Sandbox Setup")
    sandbox_topic = st.text_input(
        "Enter Sandbox Topic",
        placeholder="e.g., Newton's Laws of Motion",
        help="Describe the sandbox you want to generate content for"
    )
    
    if st.button("🚀 Start Generation", type="primary", use_container_width=True):
        if sandbox_topic.strip():
            initial_state = SandboxState(
                sandbox_topic=sandbox_topic,
                current_step="sandbox_name",
                sandbox_name="",
                aim="",
                pretest=[],
                posttest=[],
                theory="",
                procedure="",
                references="",
                user_feedback="",
                user_action="save",
                progress=0.0,
                completed_steps=[],
                system_message="Starting sandbox generation...",
                user_message=""
            )
            st.session_state.current_state = initial_state
            st.session_state.is_generating = True
            st.session_state.completed = False
            st.session_state.feedback = ""
            st.session_state.action = ""
            st.session_state.chat_history.append({
                "role": "system",
                "content": f"Started new sandbox generation for: {sandbox_topic}"
            })
            st.rerun()
        else:
            st.error("Please enter a sandbox topic.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Download Section (when complete)
    if st.session_state.completed and st.session_state.current_state:
        st.markdown('<div class="settings-box">', unsafe_allow_html=True)
        st.subheader("📥 Downloads")
        
        # Main ZIP download
        sandbox_name = st.session_state.generator.save_content(st.session_state.current_state)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(sandbox_name):
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, sandbox_name)
                    with open(filepath, 'rb') as f:
                        zipf.writestr(arcname, f.read())
        
        st.download_button(
            label="📦 All Files (ZIP)",
            data=buffer.getvalue(),
            file_name=f"{sandbox_name}.zip",
            mime="application/zip",
            use_container_width=True
        )
        
        # Individual files
        st.markdown("**Individual Files:**")
        if st.session_state.current_state.get("aim"):
            st.download_button(
                label="🎯 Aim (aim.md)",
                data=st.session_state.current_state["aim"],
                file_name="aim.md",
                mime="text/markdown",
                use_container_width=True
            )
        if st.session_state.current_state.get("theory"):
            st.download_button(
                label="📚 Theory (theory.md)",
                data=st.session_state.current_state["theory"],
                file_name="theory.md",
                mime="text/markdown",
                use_container_width=True
            )
        if st.session_state.current_state.get("procedure"):
            st.download_button(
                label="⚙️ Procedure (procedure.md)",
                data=st.session_state.current_state["procedure"],
                file_name="procedure.md",
                mime="text/markdown",
                use_container_width=True
            )
        if st.session_state.current_state.get("pretest"):
            st.download_button(
                label="📋 Pretest (pretest.json)",
                data=json.dumps({"questions": st.session_state.current_state["pretest"]}, indent=4),
                file_name="pretest.json",
                mime="application/json",
                use_container_width=True
            )
        if st.session_state.current_state.get("posttest"):
            st.download_button(
                label="📋 Posttest (posttest.json)",
                data=json.dumps({"questions": st.session_state.current_state["posttest"]}, indent=4),
                file_name="posttest.json",
                mime="application/json",
                use_container_width=True
            )
        if st.session_state.current_state.get("references"):
            st.download_button(
                label="🔗 References (reference.md)",
                data=st.session_state.current_state["references"],
                file_name="reference.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        # Simulation directory download
        sim_dir = os.path.join(sandbox_name, "simulation")
        if os.path.exists(sim_dir):
            sim_buffer = io.BytesIO()
            with zipfile.ZipFile(sim_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(sim_dir):
                    for file in files:
                        filepath = os.path.join(root, file)
                        arcname = os.path.relpath(filepath, sandbox_name)
                        with open(filepath, 'rb') as f:
                            zipf.writestr(arcname, f.read())
            st.download_button(
                label="🕹️ Simulation (ZIP)",
                data=sim_buffer.getvalue(),
                file_name=f"{sandbox_name}_simulation.zip",
                mime="application/zip",
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

# Middle Column - Main Content
with middle_col:
    st.markdown('<h3 class="step-header">📝 Content Generation</h3>', unsafe_allow_html=True)
    
    if st.session_state.current_state is not None:
        state = st.session_state.current_state
        generator = st.session_state.generator
        
        # Progress bar
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        progress = state.get("progress", 0.0)
        st.progress(progress / 100.0)
        st.caption(f"Progress: {progress:.1f}% - {state.get('current_step', 'Unknown').title()}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # System message
        if state.get("system_message"):
            st.markdown(f'<div class="content-box">{state["system_message"]}</div>', unsafe_allow_html=True)
        
        # Display current content based on step
        current_step = state.get("current_step", "")
        
        if current_step == "sandbox_name":
            st.markdown('<h4>📝 Sandbox Name</h4>', unsafe_allow_html=True)
            if state.get("sandbox_name"):
                st.markdown(f"**Generated Name:** `{state['sandbox_name']}`")
                st.info("This name will be used for the sandbox folder and files.")
                
        elif current_step == "aim":
            st.markdown('<h4>🎯 Aim</h4>', unsafe_allow_html=True)
            if state.get("aim"):
                st.markdown(state["aim"])
                
        elif current_step == "pretest":
            st.markdown('<h4>📋 Pretest Questions</h4>', unsafe_allow_html=True)
            pretest = state.get("pretest", [])
            if pretest:
                for i, question in enumerate(pretest, 1):
                    with st.expander(f"Question {i}", expanded=True):
                        st.write(f"**Question:** {question.get('question', 'N/A')}")
                        st.write("**Options:**")
                        for j, option in enumerate(question.get('options', [])):
                            st.write(f"  {chr(65+j)}. {option}")
                        st.write(f"**Correct Answer:** {question.get('correctAnswer', 'N/A')}")
                        if question.get('explanation'):
                            st.write(f"**Explanation:** {question['explanation']}")
                            
        elif current_step == "posttest":
            st.markdown('<h4>📋 Posttest Questions</h4>', unsafe_allow_html=True)
            posttest = state.get("posttest", [])
            if posttest:
                for i, question in enumerate(posttest, 1):
                    with st.expander(f"Question {i}", expanded=True):
                        st.write(f"**Question:** {question.get('question', 'N/A')}")
                        st.write("**Options:**")
                        for j, option in enumerate(question.get('options', [])):
                            st.write(f"  {chr(65+j)}. {option}")
                        st.write(f"**Correct Answer:** {question.get('correctAnswer', 'N/A')}")
                        if question.get('explanation'):
                            st.write(f"**Explanation:** {question['explanation']}")
                            
        elif current_step == "theory":
            st.markdown('<h4>📚 Theory</h4>', unsafe_allow_html=True)
            if state.get("theory"):
                st.markdown(state["theory"])
                
        elif current_step == "procedure":
            st.markdown('<h4>⚙️ Procedure</h4>', unsafe_allow_html=True)
            if state.get("procedure"):
                st.markdown(state["procedure"])
                
        elif current_step == "references":
            st.markdown('<h4>🔗 References</h4>', unsafe_allow_html=True)
            if state.get("references"):
                st.markdown(state["references"])
                
        elif current_step == "complete":
            st.markdown('<h4>✅ Generation Complete!</h4>', unsafe_allow_html=True)
            st.markdown('<div class="success-box">All sandbox content has been generated successfully!</div>', unsafe_allow_html=True)
            st.session_state.completed = True
        
        # User feedback section (if not complete)
        if current_step != "complete":
            st.markdown("---")
            st.markdown('<h4>💬 Provide Feedback</h4>', unsafe_allow_html=True)
            feedback = st.text_area(
                "Your feedback (optional):",
                value=st.session_state.feedback,
                placeholder="Enter any feedback, suggestions, or changes you'd like to make...",
                height=100
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🔄 Update", use_container_width=True, key="update_btn"):
                    st.session_state.feedback = feedback
                    st.session_state.action = "update"
                    st.session_state.current_state = step_logic(state, generator, feedback, "update")
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": f"Feedback: {feedback}"
                    })
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "Updated content based on your feedback."
                    })
                    st.rerun()
            with col2:
                if st.button("💾 Save & Continue", type="primary", use_container_width=True, key="save_btn"):
                    st.session_state.feedback = feedback
                    st.session_state.action = "save"
                    st.session_state.current_state = step_logic(state, generator, feedback, "save")
                    if feedback:
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": f"Feedback: {feedback}"
                        })
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"Completed {current_step} step and moving to next."
                    })
                    st.rerun()
            with col3:
                if st.button("⏭️ Skip Feedback", use_container_width=True, key="skip_btn"):
                    st.session_state.feedback = ""
                    st.session_state.action = "skip"
                    st.session_state.current_state = step_logic(state, generator, "", "skip")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"Skipped feedback for {current_step} step."
                    })
                    st.rerun()
    
    else:
        st.markdown("""
        ## 🚀 How to Use
        1. **Choose AI Model**: Select your preferred AI model from the settings
        2. **Enter Sandbox Topic**: Describe the sandbox you want to generate
        3. **Start Generation**: Click "Start Generation" to begin
        4. **Review & Provide Feedback**: For each component:
           - Review the content
           - Provide feedback if needed
           - Choose to update, save & continue, or skip
        5. **Download Files**: Once complete, download all files
        
        ## 📋 Generated Files
        - **aim.md**: Sandbox objectives and goals
        - **theory.md**: Theoretical background and principles
        - **procedure.md**: Step-by-step experimental procedure
        - **pretest.json**: Pre-sandbox assessment questions
        - **posttest.json**: Post-sandbox assessment questions
        - **reference.md**: Academic references and sources
        - **simulation/**: Interactive web simulation (HTML/JS/CSS)
        """)

# Right Column - Chat
with right_col:
    st.markdown('<h3 class="step-header">💬 Chat</h3>', unsafe_allow_html=True)
    
    # Chat history with scrollable container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message chat-user"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        elif message["role"] == "assistant":
            st.markdown(f'<div class="chat-message chat-ai"><strong>AI:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        elif message["role"] == "system":
            st.markdown(f'<div class="chat-message chat-ai"><strong>System:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    chat_input = st.text_input(
        "Ask a question or provide feedback:",
        placeholder="Type your message here...",
        key="chat_input"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Send", use_container_width=True):
            if chat_input.strip():
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": chat_input
                })
                
                # Generate AI response using the selected model
                try:
                    chat_prompt = f"""You are a helpful AI assistant for an educational sandbox generator. 
The user is working on creating educational content and may ask questions about the process, 
request help with content generation, or need guidance.

User message: {chat_input}

Please provide a helpful, informative response that assists the user with their sandbox generation process.
Keep responses concise but helpful."""

                    ai_response = st.session_state.generator.generate_content(chat_prompt)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": ai_response
                    })
                except Exception as e:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"I apologize, but I encountered an error: {str(e)}. Please try again."
                    })
                st.rerun()
    
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🧪 Human-in-the-Loop Sandbox Generator | Powered by LangGraph & AI Models</p>
</div>
""", unsafe_allow_html=True)

def step_logic(state, generator, feedback, action):
    """Step logic for the workflow."""
    current_step = state["current_step"]
    sandbox_topic = state["sandbox_topic"]
    
    if action == "update" and feedback:
        if current_step == "aim":
            prompt = f"{SystemPrompts.AIM_PROMPT.format(topic=sandbox_topic)}\n\nUser feedback: {feedback}\n\nPlease update the aim based on this feedback."
            state["aim"] = generator.generate_content(prompt)
            state["system_message"] = "Updated aim based on your feedback. Review again."
        elif current_step == "pretest":
            prompt = f"{SystemPrompts.PRETEST_PROMPT.format(topic=sandbox_topic)}\n\nUser feedback: {feedback}\n\nPlease update the pretest questions based on this feedback."
            content = generator.generate_content(prompt)
            state["pretest"] = generator.parse_json_content(content)
            state["system_message"] = f"Updated pretest questions based on your feedback. Review again."
        elif current_step == "posttest":
            prompt = f"{SystemPrompts.POSTTEST_PROMPT.format(topic=sandbox_topic)}\n\nUser feedback: {feedback}\n\nPlease update the posttest questions based on this feedback."
            content = generator.generate_content(prompt)
            state["posttest"] = generator.parse_json_content(content)
            state["system_message"] = f"Updated posttest questions based on your feedback. Review again."
        elif current_step == "theory":
            prompt = f"{SystemPrompts.THEORY_PROMPT.format(topic=sandbox_topic)}\n\nUser feedback: {feedback}\n\nPlease update the theory content based on this feedback."
            state["theory"] = generator.generate_content(prompt)
            state["system_message"] = "Updated theory content based on your feedback. Review again."
        elif current_step == "procedure":
            prompt = f"{SystemPrompts.PROCEDURE_PROMPT.format(topic=sandbox_topic)}\n\nUser feedback: {feedback}\n\nPlease update the procedure based on this feedback."
            state["procedure"] = generator.generate_content(prompt)
            state["system_message"] = "Updated procedure based on your feedback. Review again."
        elif current_step == "references":
            prompt = f"{SystemPrompts.REFERENCES_PROMPT.format(topic=sandbox_topic)}\n\nUser feedback: {feedback}\n\nPlease update the references based on this feedback."
            state["references"] = generator.generate_content(prompt)
            state["system_message"] = "Updated references based on your feedback. Review again."
        return state
    
    if action in ["save", "skip"]:
        if current_step == "sandbox_name":
            prompt = SystemPrompts.SANDBOX_NAME_PROMPT.format(topic=sandbox_topic)
            name = generator.generate_content(prompt).strip()
            name = name.lower().replace(" ", "-")
            name = ''.join(c for c in name if c.isalnum() or c in ['-', '_'])
            name = name[:50]
            state["sandbox_name"] = name
            state["current_step"] = "aim"
            state["system_message"] = f"Generated sandbox name: {name}"
            state["progress"] = 14.3
            state["completed_steps"].append("sandbox_name")
        elif current_step == "aim":
            prompt = SystemPrompts.AIM_PROMPT.format(topic=sandbox_topic)
            aim = generator.generate_content(prompt)
            state["aim"] = aim
            state["current_step"] = "pretest"
            state["system_message"] = "Generated aim document. Review and provide feedback."
            state["progress"] = 28.6
            state["completed_steps"].append("aim")
        elif current_step == "pretest":
            prompt = SystemPrompts.PRETEST_PROMPT.format(topic=sandbox_topic)
            content = generator.generate_content(prompt)
            pretest = generator.parse_json_content(content)
            state["pretest"] = pretest
            state["current_step"] = "posttest"
            state["system_message"] = f"Generated {len(pretest)} pretest questions. Review and provide feedback."
            state["progress"] = 42.9
            state["completed_steps"].append("pretest")
        elif current_step == "posttest":
            prompt = SystemPrompts.POSTTEST_PROMPT.format(topic=sandbox_topic)
            content = generator.generate_content(prompt)
            posttest = generator.parse_json_content(content)
            state["posttest"] = posttest
            state["current_step"] = "theory"
            state["system_message"] = f"Generated {len(posttest)} posttest questions. Review and provide feedback."
            state["progress"] = 57.1
            state["completed_steps"].append("posttest")
        elif current_step == "theory":
            prompt = SystemPrompts.THEORY_PROMPT.format(topic=sandbox_topic)
            theory = generator.generate_content(prompt)
            state["theory"] = theory
            state["current_step"] = "procedure"
            state["system_message"] = "Generated theory content. Review and provide feedback."
            state["progress"] = 71.4
            state["completed_steps"].append("theory")
        elif current_step == "procedure":
            prompt = SystemPrompts.PROCEDURE_PROMPT.format(topic=sandbox_topic)
            procedure = generator.generate_content(prompt)
            state["procedure"] = procedure
            state["current_step"] = "references"
            state["system_message"] = "Generated procedure steps. Review and provide feedback."
            state["progress"] = 85.7
            state["completed_steps"].append("procedure")
        elif current_step == "references":
            prompt = SystemPrompts.REFERENCES_PROMPT.format(topic=sandbox_topic)
            references = generator.generate_content(prompt)
            state["references"] = references
            state["current_step"] = "complete"
            state["system_message"] = "Generated references. Review and provide feedback."
            state["progress"] = 100.0
            state["completed_steps"].append("references")
    return state 