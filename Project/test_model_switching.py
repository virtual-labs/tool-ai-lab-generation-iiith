#!/usr/bin/env python3
"""
Test script for model switching functionality
"""

import os
from langgraph_experiment_generator import SandboxGenerator

def test_model_switching():
    """Test the model switching functionality."""
    print("Testing model switching functionality...")
    
    # Test with default model (Gemini)
    try:
        generator = SandboxGenerator()
        print(f"✓ Default model initialized: {generator.model_name}")
        
        # Test content generation
        test_prompt = "Create a simple test response."
        response = generator.generate_content(test_prompt)
        print(f"✓ Content generation works: {response[:50]}...")
        
        # Test model switching (this will fail without proper API keys, but should handle gracefully)
        try:
            generator.update_model("gpt-3.5-turbo")
            print(f"✓ Model switched to: {generator.model_name}")
        except Exception as e:
            print(f"⚠ Model switching failed (expected without API key): {str(e)}")
        
        print("✓ Model switching functionality test completed!")
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")

if __name__ == "__main__":
    test_model_switching() 