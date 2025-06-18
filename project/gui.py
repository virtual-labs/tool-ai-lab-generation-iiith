import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
from experiment_generator import ExperimentGenerator
import os
from tkinter import filedialog
import shutil

class ExperimentGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Experiment Content Generator")
        self.root.geometry("1200x800")
        
        # Initialize generator
        self.generator = ExperimentGenerator()
        self.generated_content = None
        
        # Create main container
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input section
        self.create_input_section()
        
        # Preview section
        self.create_preview_section()
        
        # Download section
        self.create_download_section()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(1, weight=1)
        self.main_container.rowconfigure(1, weight=1)

    def create_input_section(self):
        """Create the input section with topic entry and generate button."""
        input_frame = ttk.LabelFrame(self.main_container, text="Input", padding="5")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(input_frame, text="Experiment Topic:").grid(row=0, column=0, padx=5, pady=5)
        self.topic_entry = ttk.Entry(input_frame, width=50)
        self.topic_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.generate_btn = ttk.Button(input_frame, text="Generate Content", command=self.generate_content)
        self.generate_btn.grid(row=0, column=2, padx=5, pady=5)

    def create_preview_section(self):
        """Create the preview section with tabs for different content types."""
        preview_frame = ttk.LabelFrame(self.main_container, text="Preview", padding="5")
        preview_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(preview_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs for different content types
        self.tabs = {}
        content_types = [
            "Aim", "Experiment Name", "Pretest", "Posttest",
            "Theory", "Procedure", "References"
        ]
        
        for content_type in content_types:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=content_type)
            
            # Create text widget for content
            text_widget = scrolledtext.ScrolledText(tab, wrap=tk.WORD, width=80, height=20)
            text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Configure grid weights
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(0, weight=1)
            
            self.tabs[content_type] = text_widget

    def create_download_section(self):
        """Create the download section with download button."""
        download_frame = ttk.LabelFrame(self.main_container, text="Download", padding="5")
        download_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.download_btn = ttk.Button(
            download_frame,
            text="Download Content",
            command=self.download_content,
            state=tk.DISABLED
        )
        self.download_btn.grid(row=0, column=0, padx=5, pady=5)

    def generate_content(self):
        """Generate content based on the input topic."""
        topic = self.topic_entry.get().strip()
        if not topic:
            messagebox.showerror("Error", "Please enter an experiment topic")
            return
        
        try:
            self.generate_btn.configure(state=tk.DISABLED)
            self.root.update()
            
            # Generate content
            self.generated_content = self.generator.generate_all_content(topic)
            
            # Update preview tabs
            self.update_previews()
            
            # Enable download button
            self.download_btn.configure(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate content: {str(e)}")
        finally:
            self.generate_btn.configure(state=tk.NORMAL)

    def update_previews(self):
        """Update the preview tabs with generated content."""
        if not self.generated_content:
            return
        
        # Update each tab
        self.tabs["Aim"].delete(1.0, tk.END)
        self.tabs["Aim"].insert(tk.END, self.generated_content["aim"])
        
        self.tabs["Experiment Name"].delete(1.0, tk.END)
        self.tabs["Experiment Name"].insert(tk.END, self.generated_content["experiment_name"])
        
        self.tabs["Pretest"].delete(1.0, tk.END)
        self.tabs["Pretest"].insert(tk.END, json.dumps(self.generated_content["pretest"], indent=2))
        
        self.tabs["Posttest"].delete(1.0, tk.END)
        self.tabs["Posttest"].insert(tk.END, json.dumps(self.generated_content["posttest"], indent=2))
        
        self.tabs["Theory"].delete(1.0, tk.END)
        self.tabs["Theory"].insert(tk.END, self.generated_content["theory"])
        
        self.tabs["Procedure"].delete(1.0, tk.END)
        self.tabs["Procedure"].insert(tk.END, self.generated_content["procedure"])
        
        self.tabs["References"].delete(1.0, tk.END)
        self.tabs["References"].insert(tk.END, self.generated_content["references"])

    def download_content(self):
        """Download the generated content to a selected directory."""
        if not self.generated_content:
            return
        
        # Ask for download directory
        download_dir = filedialog.askdirectory(title="Select Download Directory")
        if not download_dir:
            return
        
        try:
            # Create experiment directory
            experiment_dir = os.path.join(download_dir, self.generated_content["experiment_name"])
            os.makedirs(experiment_dir, exist_ok=True)
            
            # Save files
            with open(os.path.join(experiment_dir, "aim.md"), "w") as f:
                f.write(self.generated_content["aim"])
            
            with open(os.path.join(experiment_dir, "experiment-name.md"), "w") as f:
                f.write(self.generated_content["experiment_name"])
            
            with open(os.path.join(experiment_dir, "pretest.json"), "w") as f:
                json.dump({"questions": self.generated_content["pretest"]}, f, indent=4)
            
            with open(os.path.join(experiment_dir, "posttest.json"), "w") as f:
                json.dump({"questions": self.generated_content["posttest"]}, f, indent=4)
            
            with open(os.path.join(experiment_dir, "theory.md"), "w") as f:
                f.write(self.generated_content["theory"])
            
            with open(os.path.join(experiment_dir, "procedure.md"), "w") as f:
                f.write(self.generated_content["procedure"])
            
            with open(os.path.join(experiment_dir, "reference.md"), "w") as f:
                f.write(self.generated_content["references"])
            
            messagebox.showinfo("Success", f"Content downloaded successfully to:\n{experiment_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download content: {str(e)}")

def main():
    root = tk.Tk()
    app = ExperimentGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 