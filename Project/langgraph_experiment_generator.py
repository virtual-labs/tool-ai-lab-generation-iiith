import json
import os
from typing import Dict, Any, List, TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

class SandboxState(TypedDict):
    """State for the sandbox generation workflow."""
    sandbox_topic: str
    current_step: str
    sandbox_name: str
    aim: str
    pretest: List[Dict[str, Any]]
    posttest: List[Dict[str, Any]]
    theory: str
    procedure: str
    references: str
    user_feedback: str
    user_action: Literal["update", "save", "continue"]
    progress: float
    completed_steps: List[str]
    system_message: str
    user_message: str

class SystemPrompts:
    """System prompts for different stages of sandbox generation."""
    
    SANDBOX_NAME_PROMPT = """You are an expert sandbox designer. Create a short, precise name for the sandbox: {topic}.

Requirements:
- Maximum 50 characters
- No special characters except hyphens and underscores
- No spaces (use hyphens instead)
- Must be file-system friendly
- Should be descriptive but concise

Example format: 'newton-laws-motion-demo' or 'gravity-pendulum-test'

Generate only the name, nothing else."""

    AIM_PROMPT = """You are an expert sandbox designer. Create a detailed aim document for the sandbox: {topic}.

The aim should include:
- Primary objective
- Secondary objectives
- Long-term learning goals
- Expected outcomes

Format as clear, structured markdown."""

    PRETEST_PROMPT = """You are an expert educator. Create a pretest quiz for the sandbox: {topic}.

Generate 5-8 multiple choice questions that assess:
- Prior knowledge
- Basic concepts
- Common misconceptions

Format as JSON array with structure:
[
  {{
    "question": "Question text",
    "options": ["A", "B", "C", "D"],
    "correctAnswer": "A",
    "explanation": "Why this is correct"
  }}
]"""

    POSTTEST_PROMPT = """You are an expert educator. Create a posttest quiz for the sandbox: {topic}.

Generate 5-8 multiple choice questions that assess:
- Understanding gained from the sandbox
- Application of concepts
- Critical thinking skills

Format as JSON array with structure:
[
  {{
    "question": "Question text",
    "options": ["A", "B", "C", "D"],
    "correctAnswer": "A",
    "explanation": "Why this is correct"
  }}
]"""

    THEORY_PROMPT = """You are an expert physicist/educator. Create detailed theoretical principles for the sandbox: {topic}.

Include:
- Fundamental concepts
- Mathematical formulations
- Scientific principles
- Real-world applications

Format as clear, structured markdown with equations and explanations."""

    PROCEDURE_PROMPT = """You are an expert educator. Create step-by-step procedure for the sandbox: {topic}.
Include clear instructions and safety measures. Format as markdown."""

    REFERENCES_PROMPT = """You are an academic researcher. Create a list of academic references and sources for the sandbox: {topic}"""

class SandboxGenerator:
    """LangGraph-based sandbox generator with human-in-the-loop."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash-preview-05-20"):
        self.model_name = model_name
        self.model = None
        self._setup_model()
    
    def _setup_model(self):
        """Setup the AI model based on the model name."""
        if self.model_name.startswith("gemini"):
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
        elif self.model_name.startswith("gpt"):
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            openai.api_key = api_key
            self.model = self.model_name
        else:
            raise ValueError(f"Unsupported model: {self.model_name}")
    
    def update_model(self, model_name: str):
        """Update the AI model."""
        self.model_name = model_name
        self._setup_model()
    
    def generate_content(self, prompt: str) -> str:
        """Generate content using the selected AI model."""
        try:
            if self.model_name.startswith("gemini"):
                response = self.model.generate_content(prompt)
                return response.text
            elif self.model_name.startswith("gpt"):
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert educational content generator."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            else:
                return f"Error: Unsupported model {self.model_name}"
        except Exception as e:
            return f"Error generating content: {str(e)}"
    
    def parse_json_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse JSON content from generated text."""
        try:
            # Try to extract JSON from the response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            return []
        except json.JSONDecodeError:
            return []
    
    def workflow_step(self, state: SandboxState) -> SandboxState:
        """Main workflow step that handles the entire process."""
        current_step = state.get("current_step", "sandbox_name")
        user_action = state.get("user_action", "continue")
        user_feedback = state.get("user_feedback", "")
        
        # Handle user feedback for updates
        if user_action == "update" and user_feedback:
            if current_step == "aim":
                prompt = f"{SystemPrompts.AIM_PROMPT.format(topic=state['sandbox_topic'])}\n\nUser feedback: {user_feedback}\n\nPlease update the aim based on this feedback."
                state["aim"] = self.generate_content(prompt)
                state["system_message"] = "Updated aim based on your feedback. Review again."
                return state
            elif current_step == "pretest":
                prompt = f"{SystemPrompts.PRETEST_PROMPT.format(topic=state['sandbox_topic'])}\n\nUser feedback: {user_feedback}\n\nPlease update the pretest questions based on this feedback."
                content = self.generate_content(prompt)
                state["pretest"] = self.parse_json_content(content)
                state["system_message"] = f"Updated pretest questions based on your feedback. Review again."
                return state
            elif current_step == "posttest":
                prompt = f"{SystemPrompts.POSTTEST_PROMPT.format(topic=state['sandbox_topic'])}\n\nUser feedback: {user_feedback}\n\nPlease update the posttest questions based on this feedback."
                content = self.generate_content(prompt)
                state["posttest"] = self.parse_json_content(content)
                state["system_message"] = f"Updated posttest questions based on your feedback. Review again."
                return state
            elif current_step == "theory":
                prompt = f"{SystemPrompts.THEORY_PROMPT.format(topic=state['sandbox_topic'])}\n\nUser feedback: {user_feedback}\n\nPlease update the theory content based on this feedback."
                state["theory"] = self.generate_content(prompt)
                state["system_message"] = "Updated theory content based on your feedback. Review again."
                return state
            elif current_step == "procedure":
                prompt = f"{SystemPrompts.PROCEDURE_PROMPT.format(topic=state['sandbox_topic'])}\n\nUser feedback: {user_feedback}\n\nPlease update the procedure based on this feedback."
                state["procedure"] = self.generate_content(prompt)
                state["system_message"] = "Updated procedure based on your feedback. Review again."
                return state
            elif current_step == "references":
                prompt = f"{SystemPrompts.REFERENCES_PROMPT.format(topic=state['sandbox_topic'])}\n\nUser feedback: {user_feedback}\n\nPlease update the references based on this feedback."
                state["references"] = self.generate_content(prompt)
                state["system_message"] = "Updated references based on your feedback. Review again."
                return state
        
        # Handle save action - move to next step
        if user_action == "save":
            if current_step == "sandbox_name":
                # Generate sandbox name
                prompt = SystemPrompts.SANDBOX_NAME_PROMPT.format(topic=state["sandbox_topic"])
                name = self.generate_content(prompt).strip()
                
                # Clean up the name
                name = name.lower()
                name = name.replace(" ", "-")
                name = ''.join(c for c in name if c.isalnum() or c in ['-', '_'])
                name = name[:50]
                
                state["sandbox_name"] = name
                state["current_step"] = "aim"
                state["system_message"] = f"Generated sandbox name: {name}"
                state["progress"] = 14.3
                state["completed_steps"].append("sandbox_name")
                
            elif current_step == "aim":
                # Generate aim
                prompt = SystemPrompts.AIM_PROMPT.format(topic=state["sandbox_topic"])
                aim = self.generate_content(prompt)
                
                state["aim"] = aim
                state["current_step"] = "pretest"
                state["system_message"] = "Generated aim document. Review and provide feedback."
                state["progress"] = 28.6
                state["completed_steps"].append("aim")
                
            elif current_step == "pretest":
                # Generate pretest
                prompt = SystemPrompts.PRETEST_PROMPT.format(topic=state["sandbox_topic"])
                content = self.generate_content(prompt)
                pretest = self.parse_json_content(content)
                
                state["pretest"] = pretest
                state["current_step"] = "posttest"
                state["system_message"] = f"Generated {len(pretest)} pretest questions. Review and provide feedback."
                state["progress"] = 42.9
                state["completed_steps"].append("pretest")
                
            elif current_step == "posttest":
                # Generate posttest
                prompt = SystemPrompts.POSTTEST_PROMPT.format(topic=state["sandbox_topic"])
                content = self.generate_content(prompt)
                posttest = self.parse_json_content(content)
                
                state["posttest"] = posttest
                state["current_step"] = "theory"
                state["system_message"] = f"Generated {len(posttest)} posttest questions. Review and provide feedback."
                state["progress"] = 57.1
                state["completed_steps"].append("posttest")
                
            elif current_step == "theory":
                # Generate theory
                prompt = SystemPrompts.THEORY_PROMPT.format(topic=state["sandbox_topic"])
                theory = self.generate_content(prompt)
                
                state["theory"] = theory
                state["current_step"] = "procedure"
                state["system_message"] = "Generated theory content. Review and provide feedback."
                state["progress"] = 71.4
                state["completed_steps"].append("theory")
                
            elif current_step == "procedure":
                # Generate procedure
                prompt = SystemPrompts.PROCEDURE_PROMPT.format(topic=state["sandbox_topic"])
                procedure = self.generate_content(prompt)
                
                state["procedure"] = procedure
                state["current_step"] = "references"
                state["system_message"] = "Generated procedure steps. Review and provide feedback."
                state["progress"] = 85.7
                state["completed_steps"].append("procedure")
                
            elif current_step == "references":
                # Generate references
                prompt = SystemPrompts.REFERENCES_PROMPT.format(topic=state["sandbox_topic"])
                references = self.generate_content(prompt)
                
                state["references"] = references
                state["current_step"] = "complete"
                state["system_message"] = "Generated references. Review and provide feedback."
                state["progress"] = 100.0
                state["completed_steps"].append("references")
        
        return state
    
    def should_continue(self, state: SandboxState) -> Literal["continue", "end"]:
        """Determine if the workflow should continue or end."""
        current_step = state.get("current_step", "")
        
        # End if we've reached the complete step
        if current_step == "complete":
            return "end"
        
        # End if user action is not set (initial state)
        if not state.get("user_action"):
            return "end"
        
        # Continue for all other cases
        return "continue"
    
    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(SandboxState)
        
        # Add single workflow node
        workflow.add_node("workflow_step", self.workflow_step)
        
        # Set entry point
        workflow.set_entry_point("workflow_step")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "workflow_step",
            self.should_continue,
            {
                "continue": "workflow_step",
                "end": END
            }
        )
        
        return workflow
    
    def save_content(self, state: SandboxState) -> str:
        """Save generated content to files."""
        sandbox_name = state["sandbox_name"]
        os.makedirs(sandbox_name, exist_ok=True)
        
        # Create simulation directory structure
        simulation_dir = os.path.join(sandbox_name, "simulation")
        src_dir = os.path.join(simulation_dir, "src")
        os.makedirs(simulation_dir, exist_ok=True)
        os.makedirs(src_dir, exist_ok=True)
        
        # Create basic simulation files
        self._create_simulation_files(simulation_dir, src_dir, state)
        
        # Save all files
        with open(f"{sandbox_name}/aim.md", "w") as f:
            f.write(state["aim"])
        
        with open(f"{sandbox_name}/sandbox-name.md", "w") as f:
            f.write(state["sandbox_name"])
        
        with open(f"{sandbox_name}/pretest.json", "w") as f:
            json.dump({"questions": state["pretest"]}, f, indent=4)
        
        with open(f"{sandbox_name}/posttest.json", "w") as f:
            json.dump({"questions": state["posttest"]}, f, indent=4)
        
        with open(f"{sandbox_name}/theory.md", "w") as f:
            f.write(state["theory"])
        
        with open(f"{sandbox_name}/procedure.md", "w") as f:
            f.write(state["procedure"])
        
        with open(f"{sandbox_name}/reference.md", "w") as f:
            f.write(state["references"])
        
        return sandbox_name
    
    def _create_simulation_files(self, simulation_dir: str, src_dir: str, state: SandboxState):
        """Create basic simulation files."""
        sandbox_topic = state["sandbox_topic"]
        sandbox_name = state["sandbox_name"]
        
        # Create index.html
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{sandbox_topic} - Interactive Simulation</title>
    <link rel="stylesheet" href="src/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{sandbox_topic}</h1>
            <p>Interactive Simulation for Educational Purposes</p>
        </header>
        
        <main>
            <div class="simulation-area">
                <div class="controls">
                    <h3>Simulation Controls</h3>
                    <div class="control-group">
                        <label for="parameter1">Parameter 1:</label>
                        <input type="range" id="parameter1" min="0" max="100" value="50">
                        <span id="value1">50</span>
                    </div>
                    <div class="control-group">
                        <label for="parameter2">Parameter 2:</label>
                        <input type="range" id="parameter2" min="0" max="100" value="25">
                        <span id="value2">25</span>
                    </div>
                    <button id="startBtn">Start Simulation</button>
                    <button id="resetBtn">Reset</button>
                </div>
                
                <div class="visualization">
                    <canvas id="simulationCanvas" width="600" height="400"></canvas>
                    <div class="data-display">
                        <h4>Real-time Data</h4>
                        <div id="dataOutput">Waiting for simulation to start...</div>
                    </div>
                </div>
            </div>
            
            <div class="instructions">
                <h3>Instructions</h3>
                <ol>
                    <li>Adjust the parameters using the sliders above</li>
                    <li>Click "Start Simulation" to begin the simulation</li>
                    <li>Observe the changes in the visualization</li>
                    <li>Record your observations in the data display</li>
                    <li>Use "Reset" to start over with new parameters</li>
                </ol>
            </div>
        </main>
        
        <footer>
            <p>This simulation demonstrates the principles of {sandbox_topic.lower()}</p>
        </footer>
    </div>
    
    <script src="src/main.js"></script>
</body>
</html>"""
        
        with open(os.path.join(simulation_dir, "index.html"), "w") as f:
            f.write(html_content)
        
        # Create style.css
        css_content = """/* Simulation Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 30px;
    color: white;
}

header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

header p {
    font-size: 1.2em;
    opacity: 0.9;
}

.simulation-area {
    background: white;
    border-radius: 15px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    margin-bottom: 30px;
}

.controls {
    margin-bottom: 30px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 10px;
}

.controls h3 {
    margin-bottom: 20px;
    color: #495057;
}

.control-group {
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 15px;
}

.control-group label {
    min-width: 120px;
    font-weight: 600;
}

.control-group input[type="range"] {
    flex: 1;
    height: 6px;
    border-radius: 3px;
    background: #ddd;
    outline: none;
    -webkit-appearance: none;
}

.control-group input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #667eea;
    cursor: pointer;
}

.control-group span {
    min-width: 40px;
    text-align: center;
    font-weight: 600;
    color: #667eea;
}

button {
    background: #667eea;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
    margin-right: 10px;
    transition: all 0.3s ease;
}

button:hover {
    background: #5a6fd8;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.visualization {
    display: flex;
    gap: 30px;
    align-items: flex-start;
}

#simulationCanvas {
    border: 2px solid #e9ecef;
    border-radius: 10px;
    background: #f8f9fa;
    flex: 1;
}

.data-display {
    flex: 1;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 10px;
    border: 2px solid #e9ecef;
}

.data-display h4 {
    margin-bottom: 15px;
    color: #495057;
}

#dataOutput {
    font-family: 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.6;
    color: #6c757d;
}

.instructions {
    background: white;
    border-radius: 15px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.instructions h3 {
    margin-bottom: 20px;
    color: #495057;
}

.instructions ol {
    padding-left: 20px;
}

.instructions li {
    margin-bottom: 10px;
    line-height: 1.6;
    color: #6c757d;
}

footer {
    text-align: center;
    margin-top: 30px;
    color: white;
    opacity: 0.8;
}

/* Responsive Design */
@media (max-width: 768px) {
    .visualization {
        flex-direction: column;
    }
    
    .control-group {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    
    .control-group label {
        min-width: auto;
    }
}"""
        
        with open(os.path.join(src_dir, "style.css"), "w") as f:
            f.write(css_content)
        
        # Create main.js
        js_content = f"""// {sandbox_topic} Simulation
class ExperimentSimulation {{
    constructor() {{
        this.canvas = document.getElementById('simulationCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.isRunning = false;
        this.animationId = null;
        this.time = 0;
        
        this.initializeControls();
        this.setupEventListeners();
        this.drawInitialState();
    }}
    
    initializeControls() {{
        this.param1Slider = document.getElementById('parameter1');
        this.param2Slider = document.getElementById('parameter2');
        this.value1Display = document.getElementById('value1');
        this.value2Display = document.getElementById('value2');
        this.startBtn = document.getElementById('startBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.dataOutput = document.getElementById('dataOutput');
        
        // Update displays when sliders change
        this.param1Slider.addEventListener('input', (e) => {{
            this.value1Display.textContent = e.target.value;
            this.updateDataDisplay();
        }});
        
        this.param2Slider.addEventListener('input', (e) => {{
            this.value2Display.textContent = e.target.value;
            this.updateDataDisplay();
        }});
    }}
    
    setupEventListeners() {{
        this.startBtn.addEventListener('click', () => this.toggleSimulation());
        this.resetBtn.addEventListener('click', () => this.resetSimulation());
    }}
    
    toggleSimulation() {{
        if (this.isRunning) {{
            this.stopSimulation();
        }} else {{
            this.startSimulation();
        }}
    }}
    
    startSimulation() {{
        this.isRunning = true;
        this.startBtn.textContent = 'Stop Simulation';
        this.startBtn.style.background = '#dc3545';
        this.animate();
    }}
    
    stopSimulation() {{
        this.isRunning = false;
        this.startBtn.textContent = 'Start Simulation';
        this.startBtn.style.background = '#667eea';
        if (this.animationId) {{
            cancelAnimationFrame(this.animationId);
        }}
    }}
    
    resetSimulation() {{
        this.stopSimulation();
        this.time = 0;
        this.param1Slider.value = 50;
        this.param2Slider.value = 25;
        this.value1Display.textContent = '50';
        this.value2Display.textContent = '25';
        this.drawInitialState();
        this.updateDataDisplay();
    }}
    
    animate() {{
        if (!this.isRunning) return;
        
        this.time += 0.016; // Approximately 60 FPS
        this.updateSimulation();
        this.draw();
        this.updateDataDisplay();
        
        this.animationId = requestAnimationFrame(() => this.animate());
    }}
    
    updateSimulation() {{
        // This is where the specific experiment logic would go
        // For now, we'll create a simple animated visualization
        const param1 = parseFloat(this.param1Slider.value);
        const param2 = parseFloat(this.param2Slider.value);
        
        // Example: Create a wave pattern based on parameters
        this.waveData = [];
        for (let x = 0; x < this.canvas.width; x++) {{
            const y = this.canvas.height/2 + 
                     Math.sin(x * 0.02 + this.time) * param1 * 0.5 +
                     Math.cos(x * 0.01 + this.time * 0.5) * param2 * 0.3;
            this.waveData.push({{x, y}});
        }}
    }}
    
    draw() {{
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw background grid
        this.drawGrid();
        
        // Draw simulation data
        if (this.waveData) {{
            this.drawWave();
        }}
        
        // Draw particles or objects based on experiment type
        this.drawParticles();
    }}
    
    drawGrid() {{
        this.ctx.strokeStyle = '#e9ecef';
        this.ctx.lineWidth = 1;
        
        // Vertical lines
        for (let x = 0; x < this.canvas.width; x += 50) {{
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }}
        
        // Horizontal lines
        for (let y = 0; y < this.canvas.height; y += 50) {{
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }}
    }}
    
    drawWave() {{
        this.ctx.strokeStyle = '#667eea';
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        
        for (let i = 0; i < this.waveData.length; i++) {{
            const point = this.waveData[i];
            if (i === 0) {{
                this.ctx.moveTo(point.x, point.y);
            }} else {{
                this.ctx.lineTo(point.x, point.y);
            }}
        }}
        
        this.ctx.stroke();
    }}
    
    drawParticles() {{
        const param1 = parseFloat(this.param1Slider.value);
        const param2 = parseFloat(this.param2Slider.value);
        
        // Draw some particles that respond to the parameters
        for (let i = 0; i < 5; i++) {{
            const x = 100 + i * 100;
            const y = 100 + Math.sin(this.time + i) * param1 * 0.5;
            
            this.ctx.fillStyle = `hsl(${{240 + param2 * 2}}, 70%, 60%)`;
            this.ctx.beginPath();
            this.ctx.arc(x, y, 10 + param1 * 0.1, 0, Math.PI * 2);
            this.ctx.fill();
        }}
    }}
    
    drawInitialState() {{
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawGrid();
        
        // Draw initial message
        this.ctx.fillStyle = '#6c757d';
        this.ctx.font = '20px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('Adjust parameters and click Start to begin simulation', 
                         this.canvas.width/2, this.canvas.height/2);
    }}
    
    updateDataDisplay() {{
        const param1 = parseFloat(this.param1Slider.value);
        const param2 = parseFloat(this.param2Slider.value);
        
        this.dataOutput.innerHTML = `
            <strong>Current Parameters:</strong><br>
            Parameter 1: ${{param1}}<br>
            Parameter 2: ${{param2}}<br><br>
            <strong>Simulation Status:</strong><br>
            Running: ${{this.isRunning ? 'Yes' : 'No'}}<br>
            Time: ${{this.time.toFixed(2)}}s<br><br>
            <strong>Calculated Values:</strong><br>
            Amplitude: ${{(param1 * 0.5).toFixed(2)}}<br>
            Frequency: ${{(param2 * 0.01).toFixed(3)}}<br>
            Phase: ${{(this.time * 0.5).toFixed(2)}}
        `;
    }}
}}

// Initialize simulation when page loads
document.addEventListener('DOMContentLoaded', () => {{
    new ExperimentSimulation();
}});"""
        
        with open(os.path.join(src_dir, "main.js"), "w") as f:
            f.write(js_content) 