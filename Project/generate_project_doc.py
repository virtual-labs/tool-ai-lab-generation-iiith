from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_project_documentation(output_file="Project_Documentation.pdf"):
    # File structure and descriptions
    file_structure = {
        "main.py": "Main script to handle the experiment generation and saving content.",
        "gui.py": "Graphical User Interface for interacting with the project.",
        "experiment_generator.py": "Contains the ExperimentGenerator class to generate experiment data.",
        "base_prompt.py": "Defines the BasePromptEnhancer class for prompt handling.",
        "requirements.txt": "Lists all the dependencies required for the project.",
        "README.md": "Provides an overview and instructions for the project.",
    }

    # Setup instructions
    setup_instructions = [
        "1. Clone the repository or download the project files.",
        "2. Navigate to the project directory.",
        "3. Create a virtual environment: `python3 -m venv myenv`.",
        "4. Activate the virtual environment: `source myenv/bin/activate`.",
        "5. Install dependencies: `pip install -r requirements.txt`.",
        "6. Run the GUI: `python3 gui.py`.",
    ]

    # Create the PDF
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Project Documentation")

    # File Structure Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 100, "File Structure and Descriptions:")
    c.setFont("Helvetica", 12)
    y = height - 130
    for file, description in file_structure.items():
        c.drawString(70, y, f"- {file}: {description}")
        y -= 20

    # Setup Instructions Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y - 20, "Setup Instructions:")
    c.setFont("Helvetica", 12)
    y -= 50
    for instruction in setup_instructions:
        c.drawString(70, y, instruction)
        y -= 20

    # Save the PDF
    c.save()
    print(f"Documentation saved as {output_file}")

# Generate the documentation
generate_project_documentation()