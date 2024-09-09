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

# Initialize the Amazon Bedrock runtime client
bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

class ImageError(Exception):
    "Custom exception for errors returned by Amazon Titan Image Generator G1"

    def __init__(self, message):
        self.message = message

def invoke_llm_text(prompt="", model_id = "anthropic.claude-3-sonnet-20240229-v1:0"):
    # Initialize the Amazon Bedrock runtime client
    # Invoke Claude 3 with the text prompt
    try:
        max_tokens = 512
        response = bedrock_client.invoke_model(modelId=model_id,body=json.dumps(
                {"anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "messages": [
                        {"role": "user",
                            "content": [{"type": "text", "text": prompt}],}
                    ], } ),
        )
        # Process and print the response
        result = json.loads(response.get("body").read())

    except ClientError as err:
        print(
            "Couldn't invoke Claude 3 Sonnet. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
    
    return result.get("content", []), result.get('usage', [])


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
        slide_json = ast.literal_eval(str(slide_json))
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



def generate_text(prompt="", N_SLIDES=1, model_id = "anthropic.claude-3-sonnet-20240229-v1:0"):
    # Invoke Claude 3 with the text prompt
    # model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

    try:
        max_tokens = int(4096/15*N_SLIDES)
        print("Max tokens: ",max_tokens)
        response = bedrock_client.invoke_model(modelId=model_id,body=json.dumps(
                {"anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "messages": [
                        {"role": "user",
                            "content": [{"type": "text", "text": prompt}],}
                    ], } ),
        )

        # Process and print the response
        result = json.loads(response.get("body").read())
        input_tokens = result["usage"]["input_tokens"]
        output_tokens = result["usage"]["output_tokens"]
        output_list = result.get("content", [])

        print("Invocation details:")
        print(f"- The input length is {input_tokens} tokens.")
        print(f"- The output length is {output_tokens} tokens.")
        print(f"- The model returned {len(output_list)} response(s):")
        # for output in output_list:
        #     print(output["text"])

    except ClientError as err:
        print(
            "Couldn't invoke Claude 3 Sonnet. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
    
    return result.get("content", []), result.get('usage', [])


def check_text_generation_consistency(slides_list=[],N_SLIDES=1):
    print("len(slides_list)",len(slides_list), "N_SLIDES",N_SLIDES)
    # print("slides_list",slides_list)
    return len(slides_list), len(slides_list) == N_SLIDES

def generate_bedrock_image(img_prompt="", current_slide_format_json={}, image_placeholder=None, cwd="", bkg=""):
    model_id = 'amazon.titan-image-generator-v1'
    body = json.dumps({"taskType": "TEXT_IMAGE","textToImageParams": {
            "text": img_prompt
        },
        "imageGenerationConfig": {"numberOfImages": 1,
            "height": current_slide_format_json["image_height"], 
            "width": current_slide_format_json["image_width"],
            "cfgScale": 8.0, "seed": np.random.randint(0, int(1e9))
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
        print(f"Finished generating image with Amazon Titan Image Generator G1 model {model_id}.")


def generate_image(model_id, body):
    print("Generating image with Amazon Titan Image Generator G1 model", model_id)

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

    print("Successfully generated image with Amazon Titan Image Generator G1 model", model_id)
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


