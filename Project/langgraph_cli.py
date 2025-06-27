#!/usr/bin/env python3
"""
CLI version of the LangGraph-based experiment generator.
This provides a command-line interface for testing the human-in-the-loop functionality.
"""

import json
import os
from langgraph_experiment_generator import SandboxGenerator, SandboxState, SystemPrompts

def print_step_header(step_name: str, progress: float):
    """Print a formatted step header."""
    print(f"\n{'='*60}")
    print(f"📋 STEP: {step_name.upper()} ({progress:.1f}%)")
    print(f"{'='*60}")

def print_content(content, content_type: str):
    """Print formatted content."""
    print(f"\n📄 {content_type.upper()}:")
    print("-" * 40)
    
    if content_type in ["pretest", "posttest"]:
        for i, question in enumerate(content, 1):
            print(f"\nQuestion {i}:")
            print(f"  Q: {question.get('question', 'N/A')}")
            print("  Options:")
            for j, option in enumerate(question.get('options', [])):
                print(f"    {chr(65+j)}. {option}")
            print(f"  Correct: {question.get('correctAnswer', 'N/A')}")
            if question.get('explanation'):
                print(f"  Explanation: {question['explanation']}")
    else:
        print(content)

def get_user_feedback() -> tuple[str, str]:
    """Get user feedback and action."""
    print("\n💬 Provide feedback (optional):")
    feedback = input("Your feedback: ").strip()
    
    print("\n🎯 Choose action:")
    print("1. Update (regenerate with feedback)")
    print("2. Save & Continue")
    print("3. Skip feedback")
    
    while True:
        choice = input("Enter choice (1-3): ").strip()
        if choice == "1":
            return feedback, "update"
        elif choice == "2":
            return feedback, "save"
        elif choice == "3":
            return "", "save"
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def main():
    """Main CLI function."""
    print("🧪 Human-in-the-Loop Sandbox Generator (CLI)")
    print("=" * 60)
    
    # Initialize generator
    try:
        generator = SandboxGenerator()
    except Exception as e:
        print(f"❌ Error initializing generator: {e}")
        return
    
    # Get sandbox topic
    sandbox_topic = input("\n🎯 Enter sandbox topic: ").strip()
    if not sandbox_topic:
        print("❌ No topic provided. Exiting.")
        return
    
    # Initialize state
    current_state = SandboxState(
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
    
    # Start workflow
    print(f"\n🚀 Starting generation for: {sandbox_topic}")
    
    try:
        # Step 1: Generate sandbox name
        print_step_header("sandbox_name", 14.3)
        prompt = SystemPrompts.SANDBOX_NAME_PROMPT.format(topic=sandbox_topic)
        name = generator.generate_content(prompt).strip()
        
        # Clean up the name
        name = name.lower()
        name = name.replace(" ", "-")
        name = ''.join(c for c in name if c.isalnum() or c in ['-', '_'])
        name = name[:50]
        
        current_state["sandbox_name"] = name
        current_state["current_step"] = "aim"
        current_state["system_message"] = f"Generated sandbox name: {name}"
        current_state["progress"] = 14.3
        current_state["completed_steps"].append("sandbox_name")
        
        print(f"📝 Generated name: {name}")
        
        # Step 2: Generate aim
        print_step_header("aim", 28.6)
        prompt = SystemPrompts.AIM_PROMPT.format(topic=sandbox_topic)
        aim = generator.generate_content(prompt)
        current_state["aim"] = aim
        print_content(aim, "aim")
        
        feedback, action = get_user_feedback()
        if action == "update" and feedback:
            prompt = f"{SystemPrompts.AIM_PROMPT.format(topic=sandbox_topic)}\n\nUser feedback: {feedback}\n\nPlease update the aim based on this feedback."
            current_state["aim"] = generator.generate_content(prompt)
            print_content(current_state["aim"], "aim")
        
        current_state["current_step"] = "pretest"
        current_state["progress"] = 28.6
        current_state["completed_steps"].append("aim")
        
        # Step 3: Generate pretest
        print_step_header("pretest", 42.9)
        prompt = SystemPrompts.PRETEST_PROMPT.format(topic=sandbox_topic)
        content = generator.generate_content(prompt)
        pretest = generator.parse_json_content(content)
        current_state["pretest"] = pretest
        print_content(pretest, "pretest")
        
        feedback, action = get_user_feedback()
        if action == "update" and feedback:
            prompt = f"{SystemPrompts.PRETEST_PROMPT.format(topic=sandbox_topic)}\n\nUser feedback: {feedback}\n\nPlease update the pretest questions based on this feedback."
            content = generator.generate_content(prompt)
            current_state["pretest"] = generator.parse_json_content(content)
            print_content(current_state["pretest"], "pretest")
        
        current_state["current_step"] = "posttest"
        current_state["progress"] = 42.9
        current_state["completed_steps"].append("pretest")
        
        # Step 4: Generate posttest
        print_step_header("posttest", 57.1)
        prompt = SystemPrompts.POSTTEST_PROMPT.format(topic=sandbox_topic)
        content = generator.generate_content(prompt)
        posttest = generator.parse_json_content(content)
        current_state["posttest"] = posttest
        print_content(posttest, "posttest")
        
        feedback, action = get_user_feedback()
        if action == "update" and feedback:
            prompt = f"{SystemPrompts.POSTTEST_PROMPT.format(topic=sandbox_topic)}\n\nUser feedback: {feedback}\n\nPlease update the posttest questions based on this feedback."
            content = generator.generate_content(prompt)
            current_state["posttest"] = generator.parse_json_content(content)
            print_content(current_state["posttest"], "posttest")
        
        current_state["current_step"] = "theory"
        current_state["progress"] = 57.1
        current_state["completed_steps"].append("posttest")
        
        # Step 5: Generate theory
        print_step_header("theory", 71.4)
        prompt = SystemPrompts.THEORY_PROMPT.format(topic=sandbox_topic)
        theory = generator.generate_content(prompt)
        current_state["theory"] = theory
        print_content(theory, "theory")
        
        feedback, action = get_user_feedback()
        if action == "update" and feedback:
            prompt = f"{SystemPrompts.THEORY_PROMPT.format(topic=sandbox_topic)}\n\nUser feedback: {feedback}\n\nPlease update the theory content based on this feedback."
            current_state["theory"] = generator.generate_content(prompt)
            print_content(current_state["theory"], "theory")
        
        current_state["current_step"] = "procedure"
        current_state["progress"] = 71.4
        current_state["completed_steps"].append("theory")
        
        # Step 6: Generate procedure
        print_step_header("procedure", 85.7)
        prompt = SystemPrompts.PROCEDURE_PROMPT.format(topic=sandbox_topic)
        procedure = generator.generate_content(prompt)
        current_state["procedure"] = procedure
        print_content(procedure, "procedure")
        
        feedback, action = get_user_feedback()
        if action == "update" and feedback:
            prompt = f"{SystemPrompts.PROCEDURE_PROMPT.format(topic=sandbox_topic)}\n\nUser feedback: {feedback}\n\nPlease update the procedure based on this feedback."
            current_state["procedure"] = generator.generate_content(prompt)
            print_content(current_state["procedure"], "procedure")
        
        current_state["current_step"] = "references"
        current_state["progress"] = 85.7
        current_state["completed_steps"].append("procedure")
        
        # Step 7: Generate references
        print_step_header("references", 100.0)
        prompt = SystemPrompts.REFERENCES_PROMPT.format(topic=sandbox_topic)
        references = generator.generate_content(prompt)
        current_state["references"] = references
        print_content(references, "references")
        
        feedback, action = get_user_feedback()
        if action == "update" and feedback:
            prompt = f"{SystemPrompts.REFERENCES_PROMPT.format(topic=sandbox_topic)}\n\nUser feedback: {feedback}\n\nPlease update the references based on this feedback."
            current_state["references"] = generator.generate_content(prompt)
            print_content(current_state["references"], "references")
        
        current_state["current_step"] = "complete"
        current_state["progress"] = 100.0
        current_state["completed_steps"].append("references")
        
        # Generation complete
        print("\n" + "="*60)
        print("✅ GENERATION COMPLETE!")
        print("="*60)
        
        # Save files
        sandbox_name = generator.save_content(current_state)
        print(f"\n📁 Files saved in directory: {sandbox_name}")
        
        # List generated files
        print("\n📋 Generated files:")
        for filename in os.listdir(sandbox_name):
            filepath = os.path.join(sandbox_name, filename)
            if os.path.isfile(filepath):
                print(f"  - {filename}")
            elif os.path.isdir(filepath):
                print(f"  📁 {filename}/")
                # List simulation files
                if filename == "simulation":
                    sim_path = os.path.join(sandbox_name, filename)
                    for sim_file in os.listdir(sim_path):
                        sim_filepath = os.path.join(sim_path, sim_file)
                        if os.path.isfile(sim_filepath):
                            print(f"    - {sim_file}")
                        elif os.path.isdir(sim_filepath):
                            print(f"    📁 {sim_file}/")
                            src_path = os.path.join(sim_path, sim_file)
                            for src_file in os.listdir(src_path):
                                print(f"      - {src_file}")
        
        print(f"\n🎉 Sandbox generation completed successfully!")
        print(f"\n🌐 To run the simulation:")
        print(f"   1. Navigate to: {sandbox_name}/simulation/")
        print(f"   2. Open index.html in your web browser")
        print(f"   3. Follow the instructions in procedure.md")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 