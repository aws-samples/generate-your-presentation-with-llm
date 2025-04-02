"""
Simple test script to verify the Bedrock Converse API function calling works correctly
"""
import json
from src.utils import generate_text, validate_slides_response, get_slide_generation_schema

def test_function_calling():
    # Test topic and number of slides
    topic = "Benefits of cloud computing with Amazon Web Services"
    n_slides = 5
    
    # Create a simple prompt
    prompt = f"{topic}"
    
    print(f"Testing Bedrock Converse API function calling with topic: {topic}")
    print(f"Using schema: {json.dumps(get_slide_generation_schema(), indent=2)}")
    
    # Call the generate_text function with function calling
    try:
        slides, usage = generate_text(prompt=prompt, N_SLIDES=n_slides)
        
        # Print usage information
        print(f"\nUsage information:")
        print(f"- Input tokens: {usage.get('input_tokens', 'N/A')}")
        print(f"- Output tokens: {usage.get('output_tokens', 'N/A')}")
        
        # Validate the response
        is_valid = validate_slides_response(slides)
        print(f"\nResponse validation: {'Passed' if is_valid else 'Failed'}")
        
        # Print the number of slides generated
        print(f"\nGenerated {len(slides)} slides:")
        
        # Print a summary of each slide
        for i, slide in enumerate(slides):
            print(f"\nSlide {i+1}: {slide.get('title', 'No title')}")
            print(f"Format: {slide.get('slideFormat', 'Unknown format')}")
        
        # Print the full response for the first slide
        if slides:
            print(f"\nExample slide content (first slide):")
            print(json.dumps(slides[0], indent=2))
        
        return slides
        
    except Exception as e:
        print(f"Error during function calling: {str(e)}")
        return None

if __name__ == "__main__":
    test_function_calling()
