# Author -> Avratanu Biswas 
# Youtube video ->
# Blog -> 

import streamlit as st
import base64
import os
from dotenv import load_dotenv
load_dotenv()


from openai import OpenAI

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


st.set_page_config(page_title="Ophthalmology Image Analyst", initial_sidebar_state="collapsed")
# Streamlit page setup
st.title("Ask your ophthalmology question, AI will assist you")

hide_streamlit_style = """
            <style>
            #MainMenu {display: none;}
            footer {display: none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=OPENAI_API_KEY)

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    with st.expander("Image", expanded = True):
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

# Toggle for showing additional details input
show_details = st.toggle("Add details about the image", value=False)

if show_details:
    # Text input for additional details about the image, shown only if toggle is True
    additional_details = st.text_area(
        "Add any additional details or context about the image here:",
        disabled=not show_details
    )

# Button to trigger the analysis
analyze_button = st.button("Analyse the Scientific Image", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and OPENAI_API_KEY and analyze_button:

    with st.spinner("Analysing the image ..."):
        # Encode the image
        base64_image = encode_image(uploaded_file)
    
        # Optimized prompt for additional clarity and detail
        prompt_text = (
            "You are a highly knowledgeable ophthalmologist expert. "
            "Your task is to examine and diagnosis the disease may have the following image in detail. "
            "Provide a comprehensive, factual, and scientifically accurate explanation of what the image "
            "Highlight key elements and their significance, and present your analysis in clear, well-structured markdown format. "
            "Create a detailed image caption in bold explaining in short."
            "If user asked about which eye is this, righ or left politly reply I could not identify."
        )
    
        if show_details and additional_details:
            prompt_text += (
                f"\n\nAdditional Context Provided by the User:\n{additional_details}"
            )
    
        # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            # Without Stream
            
            # response = client.chat.completions.create(
            #     model="gpt-4-vision-preview", messages=messages, max_tokens=500, stream=False
            # )
    
            # Stream the response
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4-vision-preview", messages=messages, 
                max_tokens=1200, stream=True
            ):
                # Check if there is content to display
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
    
            # Display the response in the app
            # st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    # Warnings for user action required
    if not uploaded_file and analyze_button:
        st.warning("Please upload an image.")
    if not OPENAI_API_KEY:
        st.warning("Please enter your OpenAI API key.")
