# 🧪 Experiment Content Generator - Setup Guide

## Project Overview

This repository contains a sophisticated experiment content generator that uses AI to create educational laboratory experiments and simulations. The system supports both CLI and GUI interfaces with human-in-the-loop feedback capabilities powered by LangGraph workflow management.

## File Structure

### Core Application Files

- **[main.py](main.py)** - Main CLI script for basic experiment generation using [`ExperimentGenerator`](experiment_generator.py)
- **[experiment_generator.py](experiment_generator.py)** - Contains the [`ExperimentGenerator`](experiment_generator.py) class for generating experiment content
- **[base_prompt.py](base_prompt.py)** - Defines the [`BasePromptEnhancer`](base_prompt.py) class for AI prompt handling with Gemini

### GUI Applications

- **[gui_streamlit.py](gui_streamlit.py)** - Basic Streamlit GUI for experiment generation
- **[langgraph_streamlit_gui.py](langgraph_streamlit_gui.py)** - Advanced Streamlit GUI with human-in-the-loop workflow

### LangGraph Workflow System

- **[langgraph_experiment_generator.py](langgraph_experiment_generator.py)** - Advanced [`SandboxGenerator`](langgraph_experiment_generator.py) with LangGraph workflow management
- **[langgraph_cli.py](langgraph_cli.py)** - CLI version with step-by-step feedback system

### Utility and Documentation

- **[rag_cli.py](rag_cli.py)** - RAG (Retrieval-Augmented Generation) CLI for PDF document processing
- **[generate_project_doc.py](generate_project_doc.py)** - Utility to generate PDF documentation
- **[experiment_reflection.txt](experiment_reflection.txt)** - Development reflection and lessons learned
- **[todo.txt](todo.txt)** - Project tasks and improvements

### Configuration and Dependencies

- **[requirements.txt](requirements.txt)** - Python package dependencies
- **[.env](.env)** - Environment variables (contains API keys)
- **[README.md](README.md)** - Project documentation

### Directories

- **[doucuments/](doucuments/)** - Directory for PDF documents used by RAG system
- **[myenv/](myenv/)** - Python virtual environment
- **[__pycache__/](__pycache__/)** - Python cache files
- **[.vscode/](.vscode/)** - VS Code settings

## Generated Content Structure

When you run the experiment generator, it creates the following files:
experiment-name/ ├── aim.md # Experiment objectives ├── experiment-name.md # Clean experiment name ├── pretest.json # Pre-experiment questions ├── posttest.json # Post-experiment questions ├── theory.md # Theoretical background ├── procedure.md # Step-by-step instructions ├── reference.md # Academic references └── simulation/ # Interactive web simulation (LangGraph version) ├── index.html └── src/ ├── main.js └── style.css


## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Google API key for Gemini AI

### 2. Clone and Navigate

```bash
git clone <repository-url>
cd experiment-content-generator

. Create Virtual Environment
python3 -m venv myenv

5. Install Dependencies
7. Running the Applications
python langgraph_cli.py

Basic Streamlit GUI
streamlit run gui_streamlit.py

RAG CLI for PDF Processing
python rag_cli.py

Key Features
Human-in-the-Loop: Review and provide feedback at each generation step
Multiple Interfaces: Choose between CLI and web-based GUI
Simulation Generation: Creates interactive HTML/JS simulations
Progress Tracking: Visual progress indicators and status updates
File Downloads: Export generated content as individual files or ZIP archives
Workflow Management: LangGraph-powered step-by-step content generation
Workflow Steps
Sandbox Name: Generate file-system-friendly sandbox name
Aim: Create detailed sandbox objectives
Pretest: Generate pre-sandbox assessment questions
Posttest: Generate post-sandbox assessment questions
Theory: Generate theoretical background
Procedure: Generate step-by-step sandbox procedure
References: Generate academic references
Simulation: Create interactive simulation directory
Usage Workflow
Input Topic: Enter your experiment topic
Step-by-Step Generation: Content is generated file-by-file
Review & Feedback: Examine generated content and provide feedback
Refinement: Update content based on your feedback
Download: Export all files when satisfied
Application Comparison
Feature	Basic CLI	Advanced CLI	Basic GUI	Advanced GUI
File	main.py	langgraph_cli.py	gui_streamlit.py	langgraph_streamlit_gui.py
Human-in-Loop	❌	✅	❌	✅
Progress Tracking	❌	✅	✅	✅
Simulation Generation	❌	✅	❌	✅
Step-by-Step	❌	✅	❌	✅
Feedback System	❌	✅	❌	✅
Recommended Usage
For the best experience, use the LangGraph versions:

langgraph_cli.py for command-line interaction
langgraph_streamlit_gui.py for web-based GUI
These provide the most advanced features with structured workflow management and human feedback integration.

Dependencies
Key packages required:

streamlit - Web GUI framework
langgraph - Workflow management
google-generativeai - Gemini AI integration
python-dotenv - Environment variable management
PyPDF2 - PDF processing for RAG
pydantic - Data validation
Troubleshooting
API Key Issues: Ensure your Google API key is correctly set in .env
Environment: Always activate the virtual environment before running scripts
Dependencies: Verify all packages are installed with pip list
Known Issues: Check experiment_reflection.txt for documented solutions
File Permissions: Ensure write permissions for output directories
Output
Generated experiments will be saved in directories named after your experiment topic, containing all necessary files for educational use including interactive simulations ready for deployment.

Development Notes
This project evolved from a simple content generator to a sophisticated human-in-the-loop system. See experiment_reflection.txt for detailed development insights and lessons learned during the creation process. ```