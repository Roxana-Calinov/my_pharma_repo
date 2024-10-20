"""
About Medication page

Main components:
-> Image upload & display functionality
-> Image analysis using Anthropic's Claude vision model
-> Generation of medications alternatives
-> Generation information about pharmaceutical suppliers
"""
import streamlit as st
import requests
from PIL import Image
import io
import base64
import os
from dotenv import load_dotenv


#Load env variables
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
API_URL = "https://api.anthropic.com/v1/messages"


def encode_image(image):
    """
    Encode image to base64
    """
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def analyze_image(image):
    """
    Analyze the image using Claude's vision model
    """
    encoded_image = encode_image(image)

    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }

    data = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": encoded_image
                        }
                    },
                    {
                        "type": "text",
                        "text": """
                                Analyze the uploaded image. The image should be a medication or a pharmaceutical product.
                                If the image does NOT represent a medication or a pharmaceutical product, your ENTIRE 
                                response must be ONLY:
                                'The image is not a medication or a pharmaceutical product!'
                                Do NOT provide ANY additional information or description if it's not a medication.
                                
                                If the image represent a medication or a pharma product, provide JUST the following
                                informations:\n
                                1. Identify the medication.\n
                                2. Specify the medication's type (RX or OTC).\n
                                3. Identify the active substance/ingredients.\n
                                4. When this medication should be recommended and for what treatment. 
                                Fit it under 250 characters.
                        """
                    }
                ]
            }
        ]
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['content'][0]['text']


def generate_alternatives(image_description):
    """
    Generates alternatives for the uploaded medication/product.
    """
    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }

    data = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 300,
        "messages": [
            {
                "role": "user",
                "content": f"Generate 3 alternatives for the medication based on the uploaded image description:"
                           f" {image_description}."
                           f"Display the contained active substances for each alternative."
                           f"The response should look like: ***medicadion***: contains ***active substance***"
                           f"Do NOT provide ANY additional informations!"
            }
        ]
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['content'][0]['text']


def about_suppliers(image_description):
    """
    Generates advices about pharmaceutical suppliers.
    """
    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }

    data = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 300,
        "messages": [
            {
                "role": "user",
                "content": f"Generate TOP 3 pharmaceutical romanian suppliers and tell me in max 150 characters why shoud"
                           f"I made business with them."
                           f"The response should look like: top no. ***supplier***: reason."
                           f"Do NOT provide ANY additional informations!"
            }
        ]
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['content'][0]['text']


def main():
    """
    Main function that handle the uploaded medication, image analysis, medication alternative generation, and
    suppliers informations
    """
    st.subheader("Identify the medication and discover alternatives")
    st.info("Upload a medication image, and find out details along with 3 alternatives based on the active substance.")

    uploaded_file = st.file_uploader("Upload a medication image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Medication Image', use_column_width=True)

        if st.button("Analyze"):
            with st.spinner("Analyzing image..."):
                try:
                    image_description = analyze_image(image)
                    if image_description == "The image is not a medication or a pharmaceutical product!":
                        st.warning(image_description)
                    else:
                        st.subheader("About medication:")
                        st.write(image_description)

                        generated_response = generate_alternatives(image_description)
                        st.subheader("Generated alternatives:")
                        st.write(generated_response)

                        top_suppliers = about_suppliers(image_description)
                        st.subheader("TOP 3 suppliers:")
                        st.write(top_suppliers)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")


if __name__ == '__main__':
    main()
