"""
# pip install streamlit requests pillow
# python -m pip install python-dotenv
"""

import streamlit as st
import requests
from PIL import Image
import io
import base64
import os
from dotenv import load_dotenv

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
                        "text": "The uploaded image should be a medication."
                                "It is necessary to identify the medication/product and to assist the Pharmacy Users"
                                " in associating it with relevant symptoms."
                                "Specify the medication's type (RX or OTC)."
                                "Finally, it is important to identify the substances contained."
                                "In addition, it is important to determine when this medication should be recommended "
                                "and for what treatment. Fit it under 200 characters."
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
                "content": f"Your target audience are the healthcare professionals."
                           f"Generate alternatives for the medication based on the uploaded image description: {image_description}. "
                           f"Give 3 other alternatives to this medication, based on the contained substances."
            }
        ]
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['content'][0]['text']


def main():
    st.subheader("Identify the medication and discover alternatives")
    st.info("Upload an image of the medication, and find out details along with 3 alternatives based on the active substance.")

    uploaded_file = st.file_uploader("Upload a medication image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Medication Image', use_column_width=True)

        if st.button("Analyze"):
            with st.spinner("Analyzing image..."):
                try:
                    image_description = analyze_image(image)
                    st.subheader("Image Description:")
                    st.write(image_description)

                    generated_post = generate_alternatives(image_description)
                    st.subheader("Generated alternatives:")
                    st.write(generated_post)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")


if __name__ == '__main__':
    main()
