import boto3
from botocore.exceptions import ClientError 
import json
import base64
import numpy as np
from PIL import Image
import io
import streamlit as st
import jsonschema
from jsonschema import validate
import ast
import re
import time
import random

# Initialize the Amazon Bedrock runtime client
bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

class ImageError(Exception):
    "Custom exception for errors returned by Amazon Nova Canvas"

    def __init__(self, message):
        self.message = message


def retry_with_exponential_backoff(max_retries=3, base_delay=1, max_delay=60, backoff_factor=2):
    """
    Decorator that implements exponential backoff retry mechanism for handling throttling and transient errors.
    
    Args:
        max_retries (int): Maximum number of retry attempts
        base_delay (float): Initial delay in seconds
        max_delay (float): Maximum delay in seconds
        backoff_factor (float): Multiplier for delay between retries
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    
                    # Check if it's a retryable error
                    if error_code in ['ThrottlingException', 'ServiceUnavailableException', 'InternalServerException']:
                        last_exception = e
                        
                        if attempt < max_retries:
                            # Calculate delay with jitter
                            delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                            jitter = random.uniform(0, delay * 0.1)  # Add up to 10% jitter
                            total_delay = delay + jitter
                            
                            print(f"Attempt {attempt + 1} failed with {error_code}. Retrying in {total_delay:.2f} seconds...")
                            time.sleep(total_delay)
                        else:
                            print(f"Max retries ({max_retries}) exceeded for {error_code}")
                            raise e
                    else:
                        # Non-retryable error, raise immediately
                        raise e
                except Exception as e:
                    # Non-ClientError exceptions are not retried
                    raise e
            
            # If we get here, all retries were exhausted
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator

@retry_with_exponential_backoff(max_retries=3, base_delay=1, max_delay=60)
def invoke_llm_text(prompt="", model_id="anthropic.claude-3-sonnet-20240229-v1:0"):
    """
    Invoke the LLM using Bedrock Converse API for simple text generation tasks.
    This is used for moderation and agenda generation.
    """
    try:
        # Call the Converse API for simple text generation
        response = bedrock_client.converse(
            modelId=model_id,
            messages=[{
                "role": "user",
                "content": [{"text": prompt}]
            }]
        )
        
        # Extract the text response
        result = []
        if "output" in response and "message" in response["output"]:
            message = response["output"]["message"]
            if "content" in message:
                content_list = message["content"]
                for content in content_list:
                    if isinstance(content, dict) and "text" in content:
                        result.append({"text": content["text"]})
                        break
        
        # Get usage information
        usage = {
            "input_tokens": response.get("usage", {}).get("inputTokens", 0),
            "output_tokens": response.get("usage", {}).get("outputTokens", 0)
        }
        
        return result, usage

    except ClientError as err:
        print(
            "Couldn't invoke Bedrock model. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise





def is_valid_text_gen_json(raw_json={}):
    
    def validateJSON(jsonData):
        try:
            json.loads(jsonData)
        except ValueError:
            return False
        return True

    isValid = validateJSON(raw_json)
    return isValid

def validate_slide_json(slide_json={}):
    # Describe what kind of json you expect.
    expected_schema = {
        "type": "object",
        "properties": {
            "slide_n": {"type": "number"},
            "title": {"type": "string"},
            "subtitle": {"type": "string"},
            "text": {"type": "string"},
            "speaker_notes": {"type": "string"},
            "slideFormat": {"type": "string"},
        },
        "required": ["slide_n", "title", "subtitle", "text", "speaker_notes", "slideFormat"]
        }
    try:
        # Ensure slide_json is a dictionary
        if isinstance(slide_json, str):
            slide_json = json.loads(slide_json)
        # print("!!!!!!!!! slide_json",type(slide_json),slide_json)
        print("expected_schema",expected_schema["properties"].keys(),"slide_json",slide_json.keys())
        validate(instance=slide_json, schema=expected_schema)
    except jsonschema.exceptions.ValidationError as err:
        print("SLIDE JSON VALIDATE ERROR:",err)
        return False
    except ValueError:
        print("SLIDE JSON VALIDATE ERROR UNKNOWN")
        return False
    return True


def check_text_generation_consistency(slides_list=[],N_SLIDES=1):
    print("len(slides_list)",len(slides_list), "N_SLIDES",N_SLIDES)
    # print("slides_list",slides_list)
    return len(slides_list), len(slides_list) == N_SLIDES

@retry_with_exponential_backoff(max_retries=3, base_delay=1, max_delay=60)
def generate_bedrock_image(img_prompt="", current_slide_format_json={}, image_placeholder=None, cwd="", bkg=""):
    model_id = 'amazon.nova-canvas-v1:0'
    body = json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": img_prompt
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": current_slide_format_json["image_height"], 
            "width": current_slide_format_json["image_width"],
            "cfgScale": 8.0, 
            "seed": np.random.randint(0, int(1e9))
        }
    })

    try:
        image_bytes = generate_image(model_id=model_id, body=body)
        image = Image.open(io.BytesIO(image_bytes))
        image.save(cwd+"/tmp/test_image"+bkg+".jpg")
        if image_placeholder:
            image_placeholder.insert_picture(cwd+"/tmp/test_image"+bkg+".jpg")
    except ClientError as err:
        message = err.response["Error"]["Message"]
        print("A client error occurred:", message)
        print("A client error occured: " + format(message))
    except ImageError as err:
        print(err.message)
        print(err.message)
    else:
        print(f"Finished generating image with Amazon Nova Canvas model {model_id}.")


def generate_image(model_id, body):
    print("Generating image with Amazon Nova Canvas model", model_id)

    accept = "application/json"
    content_type = "application/json"

    response = bedrock_client.invoke_model(
        body=body, modelId=model_id, accept=accept, contentType=content_type
    )
    response_body = json.loads(response.get("body").read())

    base64_image = response_body.get("images")[0]
    base64_bytes = base64_image.encode('ascii')
    image_bytes = base64.b64decode(base64_bytes)

    finish_reason = response_body.get("error")

    if finish_reason is not None:
        raise ImageError(f"Image generation error. Error is {finish_reason}")

    print("Successfully generated image with Amazon Nova Canvas model", model_id)
    return image_bytes


def check_password(app_name: str):
    """Returns `True` if the user had a correct password."""

    login_screen = st.empty()

    if "username" not in st.session_state:
        st.session_state["username"] = ""

    if "passwords" not in st.session_state:
        st.session_state["passwords"] = ""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        password_check_not_active = (
            "username" not in st.session_state or "password" not in st.session_state
        )
        if password_check_not_active:
            return

        username_and_password_correct = (
            st.session_state["username"] == st.session_state["glb_username"]
            and st.session_state["password"]
            == st.session_state["glb_pwd"]
        )
        if username_and_password_correct:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    need_to_check_password = (
        "password_correct" not in st.session_state
        or not st.session_state["password_correct"]
    )
    if need_to_check_password:
        with login_screen.container():
            st.title(app_name)
            st.text_input("Username", key="username", on_change=password_entered)
            st.text_input(
                "Password", type="password", key="password", on_change=password_entered
            )
            username = st.session_state["username"]
            password = st.session_state["password"]

            entered_username_password_not_correct = (
                "password_correct" in st.session_state
                and not st.session_state["password_correct"]
                and username
                and password
            )
            if entered_username_password_not_correct:
                # Only show if customer already entered username + password
                st.error("😕 User not known or password incorrect")
            return False
    else:
        # Password correct.
        login_screen.empty()

        return True


def get_slide_generation_schema():
    """
    Define the schema for slide generation using the Bedrock Converse API.
    Returns the tool configuration in the format expected by the API.
    """
    # Define the schema for slide generation
    schema = {
        "type": "object",
        "properties": {
            "slides": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "slide_n": {"type": "integer", "description": "Slide number"},
                        "title": {"type": "string", "description": "Slide title"},
                        "subtitle": {"type": "string", "description": "Slide subtitle"},
                        "text": {"type": "string", "description": "Main slide content"},
                        "speaker_notes": {"type": "string", "description": "Speaker notes for the slide"},
                        "slideFormat": {"type": "string", "description": "Layout format for the slide"}
                    },
                    "required": ["slide_n", "title", "subtitle", "text", "speaker_notes", "slideFormat"]
                }
            }
        },
        "required": ["slides"]
    }
    
    # Return the tool configuration in the format expected by the Converse API
    return {
        "tools": [
            {
                "toolSpec": {
                    "name": "generate_presentation_slides",
                    "description": "Generate structured presentation slides based on a topic",
                    "inputSchema": {
                        "json": schema
                    }
                }
            }
        ]
    }

@retry_with_exponential_backoff(max_retries=3, base_delay=1, max_delay=60)
def generate_text(prompt="", N_SLIDES=1, model_id="anthropic.claude-3-sonnet-20240229-v1:0"):
    """
    Generate presentation slides using the Bedrock Converse API with function calling.
    This provides better control over the output format and ensures consistent slide generation.
    """
    try:
        # Get the tool schema for slide generation
        tool_config = get_slide_generation_schema()
        
        # Create the conversation message with instructions for slide generation
        full_prompt = f"""You are a presentation creation assistant. Generate a well-structured presentation about "{prompt}" with {N_SLIDES} slides.

For each slide, provide the following information:
1. slide_n: The slide number (integer)
2. title: A concise, informative title for the slide
3. subtitle: A subtitle or brief description
4. text: The main content of the slide (use *** to separate bullet points)
5. speaker_notes: Notes for the presenter
6. slideFormat: Choose one of the following formats:
   - "Title page" (for the first slide)
   - "Slide with bullet points"
   - "Slide with image and text"
   - "Slide with image only"
   - "Slide with 4 takeaways" (for the last slide)

Use the generate_presentation_slides tool to create the presentation.
"""
        
        # Call the Converse API with the tool configuration
        response = bedrock_client.converse(
            modelId=model_id,
            messages=[{
                "role": "user",
                "content": [{"text": full_prompt}]
            }],
            toolConfig=tool_config
        )
        
        # Extract the slides from the tool response
        slides = []
        
        # The response structure is different from what we expected
        # The tool response is in response["output"]["message"]["content"]
        if "output" in response and "message" in response["output"]:
            message = response["output"]["message"]
            if "content" in message:
                content_list = message["content"]
                for content in content_list:
                    if isinstance(content, dict) and "toolUse" in content:
                        tool_use = content["toolUse"]
                        if tool_use.get("name") == "generate_presentation_slides":
                            slides = tool_use.get("input", {}).get("slides", [])
                            break
        
        # Get usage information
        usage = {
            "input_tokens": response.get("usage", {}).get("inputTokens", 0),
            "output_tokens": response.get("usage", {}).get("outputTokens", 0)
        }
        
        # Validate the slides
        if slides and validate_slides_response(slides):
            return slides, usage
        else:
            print("Error: Generated slides failed validation or are empty")
            return [], usage

    except ClientError as err:
        print(
            "Couldn't invoke Bedrock model. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
    except Exception as err:
        print(f"Error generating slides: {err}")
        raise
        
        # Get usage information
        usage = {
            "input_tokens": response.get("usage", {}).get("inputTokens", 0),
            "output_tokens": response.get("usage", {}).get("outputTokens", 0)
        }
        
        # Validate the slides
        if slides and validate_slides_response(slides):
            return slides, usage
        else:
            print("Error: Generated slides failed validation or are empty")
            return [], usage

    except ClientError as err:
        print(
            "Couldn't invoke Bedrock model. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
    except Exception as err:
        print(f"Error generating slides: {err}")
        raise

def validate_slides_response(slides):
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "slide_n": {"type": ["integer", "number"]},
                "title": {"type": "string"},
                "subtitle": {"type": "string"},
                "text": {"type": "string"},
                "speaker_notes": {"type": "string"},
                "slideFormat": {"type": "string"}
            },
            "required": ["slide_n", "title", "subtitle", "text", "speaker_notes", "slideFormat"]
        }
    }
    
    try:
        validate(instance=slides, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as err:
        print("Validation error:", err)
        return False

def generate_presentation(topic, n_slides):
    prompt = topic
    
    slides, usage = generate_text(prompt=prompt, N_SLIDES=n_slides)
    
    if not validate_slides_response(slides):
        raise ValueError("Generated slides failed validation")
        
    return slides
