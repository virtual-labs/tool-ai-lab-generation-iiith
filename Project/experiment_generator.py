import json
from typing import Dict, Any, List
from base_prompt import BasePromptEnhancer

class ExperimentGenerator(BasePromptEnhancer):
    """Class for generating experiment content using the base prompt enhancer."""
    
    def generate_aim(self, experiment_topic: str) -> str:
        """Generate the aim.md content."""
        print(f"\nGenerating aim document for: {experiment_topic}")
        prompt = f"Create a detailed aim document for the experiment: {experiment_topic}. Include multiple objectives and long-term intentions."
        result = self.generate_content(prompt)
        print("✓ Aim document generated successfully")
        return result["generated_content"]
    
    def generate_experiment_name(self, experiment_topic: str) -> str:
        """Generate the experiment name."""
        print(f"\nGenerating experiment name for: {experiment_topic}")
        prompt = f"""Create a short, precise name for the experiment: {experiment_topic}. 
        Requirements:
        - Maximum 50 characters
        - No special characters except hyphens and underscores
        - No spaces (use hyphens instead)
        - Must be file-system friendly
        - Should be descriptive but concise
        Example format: 'newton-laws-motion-demo' or 'gravity-pendulum-test'
        """
        result = self.generate_content(prompt)
        name = result["generated_content"].strip()
        
        # Clean up the name to ensure it's file-system friendly
        name = name.lower()
        name = name.replace(" ", "-")
        name = ''.join(c for c in name if c.isalnum() or c in ['-', '_'])
        name = name[:50]  # Ensure maximum length
        
        print(f"✓ Experiment name generated: {name}")
        return name
    
    def generate_quiz(self, experiment_topic: str, is_pretest: bool = True) -> List[Dict[str, Any]]:
        """Generate quiz questions in JSON format."""
        quiz_type = "pretest" if is_pretest else "posttest"
        print(f"\nGenerating {quiz_type} quiz for: {experiment_topic}")
        prompt = f"Create a {quiz_type} quiz for the experiment: {experiment_topic}. Format as JSON with questions, answers, and correctAnswer fields."
        result = self.generate_content(prompt)
        try:
            quiz_data = json.loads(result["generated_content"])
            print(f"✓ {quiz_type.capitalize()} quiz generated successfully")
            return quiz_data
        except json.JSONDecodeError:
            print(f"⚠ Warning: Failed to parse {quiz_type} quiz JSON")
            return []
    
    def generate_theory(self, experiment_topic: str) -> str:
        """Generate the theory.md content."""
        print(f"\nGenerating theory content for: {experiment_topic}")
        prompt = f"Create detailed theoretical principles for the experiment: {experiment_topic}. Include mathematical notations and explanations."
        result = self.generate_content(prompt)
        print("✓ Theory content generated successfully")
        return result["generated_content"]
    
    def generate_procedure(self, experiment_topic: str) -> str:
        """Generate the procedure.md content."""
        print(f"\nGenerating procedure steps for: {experiment_topic}")
        prompt = f"Create step-by-step procedure for the experiment: {experiment_topic}. Include clear instructions and safety measures."
        result = self.generate_content(prompt)
        print("✓ Procedure steps generated successfully")
        return result["generated_content"]
    
    def generate_references(self, experiment_topic: str) -> str:
        """Generate the reference.md content."""
        print(f"\nGenerating references for: {experiment_topic}")
        prompt = f"Create a list of academic references and sources for the experiment: {experiment_topic}"
        result = self.generate_content(prompt)
        print("✓ References generated successfully")
        return result["generated_content"]
    
    def generate_all_content(self, experiment_topic: str) -> Dict[str, Any]:
        """Generate all experiment content files."""
        print("\n=== Starting Content Generation ===")
        print(f"Topic: {experiment_topic}")
        
        experiment_name = self.generate_experiment_name(experiment_topic)
        print(f"\nExperiment name: {experiment_name}")
        
        content = {
            "experiment_name": experiment_name,
            "aim": self.generate_aim(experiment_topic),
            "pretest": self.generate_quiz(experiment_topic, is_pretest=True),
            "posttest": self.generate_quiz(experiment_topic, is_pretest=False),
            "theory": self.generate_theory(experiment_topic),
            "procedure": self.generate_procedure(experiment_topic),
            "references": self.generate_references(experiment_topic)
        }
        
        print("\n=== Content Generation Complete ===")
        return content 