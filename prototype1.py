import os
import json
import re
from typing import Dict, List, Optional
import google.generativeai as genai
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ExperimentConfig:
    """Configuration for experiment generation"""
    discipline: str
    lab_name: str
    experiment_name: str
    experiment_number: str
    developer_name: str
    developer_email: str
    developer_institute: str
    developer_department: str

class VirtualLabsExperimentGenerator:
    """
    AI Agent for generating Virtual Labs experiment content using Google Gemini.
    
    This agent analyzes the provided template files and generates appropriate
    content based on user prompts, maintaining the structure and format
    required by the Virtual Labs platform.
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro"):
        """
        Initialize the AI ag
        ent with Gemini API.
        
        Args:
            api_key: Google AI API key
            model_name: Gemini model to use
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.file_processors = {
            'aim.md': self._generate_aim,
            'theory.md': self._generate_theory,
            'procedure.md': self._generate_procedure,
            'references.md': self._generate_references,
            'experiment-name.md': self._generate_experiment_name,
            'contributors.md': self._generate_contributors,
            'pretest.json': self._generate_pretest,
            'posttest.json': self._generate_posttest,
            # 'README.md': self._update_readme_templates
        }
    
    def generate_experiment(self, 
                          user_prompt: str, 
                          config: ExperimentConfig,
                          output_dir: str = "generated_experiment") -> Dict[str, str]:
      
        """
        Generate complete experiment content based on user prompt.
        
        Args:
            user_prompt: User's description of the experiment
            config: Experiment configuration details
            output_dir: Directory to save generated files
            
        Returns:
            Dictionary mapping file names to generated content
        """
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Store generated content
        generated_content = {}
        
        # Generate content for each file
        for filename, processor in self.file_processors.items():
            try:
                print(f"Generating content for {filename}...")
                content = processor(user_prompt, config)
                generated_content[filename] = content
                
                # Save to file
                file_path = Path(output_dir) / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            except Exception as e:
                print(f"Error generating {filename}: {str(e)}")
                generated_content[filename] = f"Error: {str(e)}"
        
        # Generate simulation folder structure
        self._create_simulation_structure(output_dir, user_prompt, config)
        
        print(f"\nExperiment generated successfully in '{output_dir}' directory!")
        return generated_content
    
    def _generate_aim(self, user_prompt: str, config: ExperimentConfig) -> str:
        """Generate aim.md content"""
        prompt = f"""
        Based on this experiment description: "{user_prompt}"
        
        Generate a clear and concise aim for this {config.discipline} experiment.
        The aim should:
        1. State the broad learning objectives
        2. Explain what students will achieve
        3. Be written in academic language
        4. Be 2-3 sentences long
        
        Format as markdown with "### Aim of the experiment" as header.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def _generate_theory(self, user_prompt: str, config: ExperimentConfig) -> str:
        """Generate theory.md content"""
        prompt = f"""
        Based on this experiment description: "{user_prompt}"
        
        Generate comprehensive theoretical background for this {config.discipline} experiment.
        Include:
        1. Fundamental principles and concepts
        2. Mathematical formulations (use LaTeX notation where needed)
        3. Key equations and relationships
        4. Theoretical framework
        5. Relevant scientific principles
        
        Format as markdown with proper headers and LaTeX for mathematical expressions.
        Use ### for main headers and #### for subheaders.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def _generate_procedure(self, user_prompt: str, config: ExperimentConfig) -> str:
        """Generate procedure.md content"""
        prompt = f"""
        Based on this experiment description: "{user_prompt}"
        
        Generate detailed step-by-step procedure for this {config.discipline} experiment.
        Include:
        1. Pre-experiment setup
        2. Numbered step-by-step instructions
        3. What to observe at each step
        4. Safety considerations if applicable
        5. Data collection points
        6. Post-experiment analysis steps
        
        Format as markdown with "### Procedure" as main header.
        Use numbered lists for steps.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def _generate_references(self, user_prompt: str, config: ExperimentConfig) -> str:
        """Generate references.md content"""
        prompt = f"""
        Based on this experiment description: "{user_prompt}"
        
        Generate a list of 5-8 relevant academic references for this {config.discipline} experiment.
        Include:
        1. Textbooks
        2. Research papers
        3. Online resources
        4. Standards/guidelines if applicable
        
        Format as markdown with "### References" as header.
        Use proper academic citation format.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def _generate_experiment_name(self, user_prompt: str, config: ExperimentConfig) -> str:
        """Generate experiment-name.md content"""
        return f"## {config.experiment_name}"
    
    def _generate_contributors(self, user_prompt: str, config: ExperimentConfig) -> str:
        """Generate contributors.md content"""
        return f"""### Subject Matter Experts
| SNo. | Name | Email | Institute | ID |
| :---: | :---: | :---: | :---: | :---: |
| 1 | {config.developer_name} | {config.developer_email} | {config.developer_institute} | SME001 |

### Developers
| SNo. | Name | Email | Institute | ID |
| :---: | :---: | :---: | :---: | :---: |
| 1 | {config.developer_name} | {config.developer_email} | {config.developer_institute} | DEV001 |"""
    
    def _generate_pretest(self, user_prompt: str, config: ExperimentConfig) -> str:
        """Generate pretest.json content"""
        prompt = f"""
        Based on this experiment description: "{user_prompt}"
        
        Generate 5 multiple-choice questions for a pretest to assess prerequisite knowledge.
        Each question should test fundamental concepts students need before starting the experiment.
        
        Return as valid JSON with this structure:
        {{
          "version": 2.0,
          "questions": [
            {{
              "question": "Question text?",
              "answers": {{
                "a": "option1",
                "b": "option2", 
                "c": "option3",
                "d": "option4"
              }},
              "explanations": {{
                "a": "Explanation for option a",
                "b": "Explanation for option b",
                "c": "Explanation for option c", 
                "d": "Explanation for option d"
              }},
              "correctAnswer": "a",
              "difficulty": "beginner"
            }}
          ]
        }}
        
        Ensure all questions are relevant to the prerequisite knowledge for: {config.experiment_name}
        """
        
        response = self.model.generate_content(prompt)
        # Clean and validate JSON
        json_text = self._extract_json(response.text)
        try:
            json.loads(json_text)  # Validate JSON
            return json_text
        except json.JSONDecodeError:
            # Return template if AI response is invalid
            return self._get_default_quiz_template("pretest")
    
    def _generate_posttest(self, user_prompt: str, config: ExperimentConfig) -> str:
        """Generate posttest.json content"""
        prompt = f"""
        Based on this experiment description: "{user_prompt}"
        
        Generate 5 multiple-choice questions for a posttest to assess learning outcomes.
        Each question should test concepts students should understand after completing the experiment.
        
        Return as valid JSON with this structure:
        {{
          "version": 2.0,
          "questions": [
            {{
              "question": "Question text?",
              "answers": {{
                "a": "option1",
                "b": "option2", 
                "c": "option3",
                "d": "option4"
              }},
              "explanations": {{
                "a": "Explanation for option a",
                "b": "Explanation for option b",
                "c": "Explanation for option c", 
                "d": "Explanation for option d"
              }},
              "correctAnswer": "a",
              "difficulty": "intermediate"
            }}
          ]
        }}
        
        Focus on learning outcomes from: {config.experiment_name}
        """
        
        response = self.model.generate_content(prompt)
        json_text = self._extract_json(response.text)
        try:
            json.loads(json_text)  
            return json_text
        except json.JSONDecodeError:
            return self._get_default_quiz_template("posttest")
        
if __name__ == "__main__":
    api_key = "AIzaSyDtIftiUGFBL9w3DV_YqmdU_eI9hpg6Sno"
    user_prompt = "Design an experiment to demonstrate the principles of Newton's second law of motion."
    
    config = ExperimentConfig(
        discipline="Physics",
        lab_name="Mechanics Lab",
        experiment_name="Newton's Second Law",
        experiment_number="PHY101",
        developer_name="John Doe",
        developer_email="john.doe@example.com",
        developer_institute="Example Institute of Technology",
        developer_department="Physics Department"
    )
    
    generator = VirtualLabsExperimentGenerator(api_key=api_key)
    output_dir = "output_experiment"
    
    generator.generate_experiment(user_prompt, config, output_dir)