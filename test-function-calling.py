#!/usr/bin/env python3
"""
Test script to verify the Bedrock Converse API function calling implementation
for presentation generation.
"""

import json
import boto3
from src.utils import generate_text, get_slide_generation_schema, validate_slides_response

def main():
    """
    Test the generate_text function with Converse API and function calling.
    """
    print("Testing presentation generation with Bedrock Converse API and function calling...")
    
    # Test topic and number of slides
    topic = "Introduction to AWS Cloud Services"
    n_slides = 3
    
    print(f"Generating a presentation about '{topic}' with {n_slides} slides...")
    
    # Test with Claude 3 Haiku (faster for testing)
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    
    try:
        # Generate slides using the updated function
        slides, usage = generate_text(prompt=topic, N_SLIDES=n_slides, model_id=model_id)
        
        # Print usage information
        print(f"\nUsage Information:")
        print(f"Input tokens: {usage['input_tokens']}")
        print(f"Output tokens: {usage['output_tokens']}")
        
        # Validate the slides
        is_valid = validate_slides_response(slides)
        print(f"\nSlides validation result: {'Success' if is_valid else 'Failed'}")
        
        # Print the number of slides generated
        print(f"Number of slides generated: {len(slides)}")
        print(f"Number of slides requested: {n_slides}")
        
        # Print the slides in a readable format
        print("\nGenerated Slides:")
        for slide in slides:
            print(f"\n--- Slide {slide['slide_n']} ---")
            print(f"Title: {slide['title']}")
            print(f"Subtitle: {slide['subtitle']}")
            print(f"Format: {slide['slideFormat']}")
            print(f"Text: {slide['text'][:100]}..." if len(slide['text']) > 100 else f"Text: {slide['text']}")
        
        # Save the slides to a JSON file for inspection
        with open('test_slides_output.json', 'w') as f:
            json.dump(slides, f, indent=2)
        print("\nSlides saved to test_slides_output.json")
        
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main()
