# 🧪 Human-in-the-Loop Sandbox Generator

A sophisticated sandbox content generator that uses **LangGraph** for workflow management and **human-in-the-loop** interaction. This system generates educational sandbox content step-by-step, allowing users to provide feedback and make updates at each stage.

## Features
- **Step-by-step generation**: Content is generated file-by-file, with user review and feedback at each step
- **Human-in-the-Loop**: Interactive feedback and content refinement
- **Web-based simulation**: Each sandbox includes a simulation directory with HTML/JS/CSS
- **Progress tracking**: Progress bar and download options in the GUI

## Generated Files
- **aim.md**: Sandbox objectives and learning goals
- **procedure.md**: Step-by-step sandbox procedure
- **pretest.json**: Pre-sandbox assessment questions
- **posttest.json**: Post-sandbox assessment questions
- **sandbox-name.md**: Clean sandbox name for file system
- **theory.md**: Theoretical background
- **reference.md**: Academic references and sources
- **simulation/**: Interactive web simulation (HTML/JS/CSS)

## Workflow
1. **Sandbox Name**: Generate file-system-friendly sandbox name
2. **Aim**: Create detailed sandbox objectives
3. **Pretest**: Generate pre-sandbox assessment questions
4. **Posttest**: Generate post-sandbox assessment questions
5. **Theory**: Generate theoretical background
6. **Procedure**: Generate step-by-step sandbox procedure
7. **References**: Generate academic references
8. **Simulation**: Create interactive simulation directory

## Usage
- **CLI**: Run `langgraph_cli.py` for step-by-step, feedback-driven sandbox generation
- **GUI**: Run `langgraph_streamlit_gui.py` for a Streamlit-based interactive interface

## Example Directory Structure
```
sandbox-generator/
├── langgraph_sandbox_generator.py  # Core LangGraph engine
├── langgraph_streamlit_gui.py      # Streamlit GUI
├── langgraph_cli.py               # CLI version
├── generated_sandboxes/           # Output directory
│   └── sandbox-name/
│       ├── aim.md
│       ├── sandbox-name.md
│       ├── pretest.json
│       ├── posttest.json
│       ├── theory.md
│       ├── procedure.md
│       ├── reference.md
│       └── simulation/
│           ├── index.html
│           └── src/
│               ├── main.js
│               └── style.css
```

**🧪 Happy Sandbox Generation!** 