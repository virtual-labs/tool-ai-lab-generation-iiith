from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field

class BasePromptEnhancer(BaseModel):
    """Base class for prompt enhancement using Gemini."""
    
    model: Any = Field(default=None, exclude=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
    
    def enhance_prompt(self, user_prompt: str) -> str:
        """
        Enhance the user prompt using Gemini.
        
        Args:
            user_prompt (str): The original user prompt
            
        Returns:
            str: Enhanced prompt
        """
        try:
            response = self.model.generate_content(
                f"Enhance this prompt for better clarity and detail: {user_prompt}"
            )
            return response.text
        except Exception as e:
            print(f"Error enhancing prompt: {str(e)}")
            return user_prompt
    
    def generate_content(self, prompt: str) -> Dict[str, Any]:
        """
        Generate content based on the enhanced prompt.
        
        Args:
            prompt (str): The prompt to generate content from
            
        Returns:
            Dict[str, Any]: Generated content in structured format
        """
        try:
            enhanced_prompt = self.enhance_prompt(prompt)
            response = self.model.generate_content(enhanced_prompt)
            return {
                "original_prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "generated_content": response.text
            }
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return {
                "original_prompt": prompt,
                "error": str(e)
            } 