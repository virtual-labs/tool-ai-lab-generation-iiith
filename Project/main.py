import json
from experiment_generator import ExperimentGenerator
import os

def save_content(content: dict, experiment_name: str):
    """Save generated content to files."""
    print(f"\n=== Saving Content to Files ===")
    print(f"Creating directory: {experiment_name}")
    
    # Create directory for the experiment
    os.makedirs(experiment_name, exist_ok=True)
    
    # Save aim.md
    print("Saving aim.md...")
    with open(f"{experiment_name}/aim.md", "w") as f:
        f.write(content["aim"])
    
    # Save experiment name
    print("Saving experiment-name.md...")
    with open(f"{experiment_name}/experiment-name.md", "w") as f:
        f.write(content["experiment_name"])
    
    # Save pretest.json
    print("Saving pretest.json...")
    with open(f"{experiment_name}/pretest.json", "w") as f:
        json.dump({"questions": content["pretest"]}, f, indent=4)
    
    # Save posttest.json
    print("Saving posttest.json...")
    with open(f"{experiment_name}/posttest.json", "w") as f:
        json.dump({"questions": content["posttest"]}, f, indent=4)
    
    # Save theory.md
    print("Saving theory.md...")
    with open(f"{experiment_name}/theory.md", "w") as f:
        f.write(content["theory"])
    
    # Save procedure.md
    print("Saving procedure.md...")
    with open(f"{experiment_name}/procedure.md", "w") as f:
        f.write(content["procedure"])
    
    # Save reference.md
    print("Saving reference.md...")
    with open(f"{experiment_name}/reference.md", "w") as f:
        f.write(content["references"])
    
    print("\n✓ All files saved successfully!")

def main():
    print("=== Experiment Content Generator ===")
    print("Initializing generator...")
    
    # Initialize the experiment generator
    generator = ExperimentGenerator()
    
    # Get experiment topic from user
    experiment_topic = input("\nEnter the experiment topic: ")
    
    # Generate all content
    content = generator.generate_all_content(experiment_topic)
    
    # Save content to files
    save_content(content, content["experiment_name"])
    
    print(f"\n=== Generation Complete ===")
    print(f"All content has been generated and saved in the '{content['experiment_name']}' directory.")
    print("You can now find the following files:")
    print(f"- {content['experiment_name']}/aim.md")
    print(f"- {content['experiment_name']}/experiment-name.md")
    print(f"- {content['experiment_name']}/pretest.json")
    print(f"- {content['experiment_name']}/posttest.json")
    print(f"- {content['experiment_name']}/theory.md")
    print(f"- {content['experiment_name']}/procedure.md")
    print(f"- {content['experiment_name']}/reference.md")

if __name__ == "__main__":
    main() 