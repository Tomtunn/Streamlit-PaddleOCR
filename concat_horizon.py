import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import base64
import easyocr as ocr

# Custom CSS for theming
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ADC7F9; /* Change background color */
    }
    .primary-text {
        color: blue;
        font-size: 24px;
    }
    /* Add more CSS for other elements as needed */
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.title("Easy OCR - Extract Text from Images")

# Subtitle
st.markdown("## Optical Character Recognition - Using `easyocr`, `streamlit`")
st.markdown("")

# Function to perform OCR for individual images and create editable DataFrames
def perform_ocr_editable_df(image, image_index):
    reader = ocr.Reader(['en'], model_storage_directory='.')
    ocr_results = []

    img = Image.open(image)  # Read the uploaded image
    st.image(img, caption=f"Uploaded Image - {image_index}", use_column_width=True)
    
    result = reader.readtext(np.array(img))  # Perform OCR
    ocr_texts = [text[1] for text in result]

    ### Create a DataFrame from the OCR results
    ocr_df = pd.DataFrame(ocr_texts, columns=[f"Text_{image_index}"])

    # Display the OCR results DataFrame
    st.write(f"### OCR Results for Image {image_index}")

    # Use st.data_editor for interactive editing with dynamic row addition/deletion
    edited_df = st.data_editor(ocr_df, num_rows="dynamic")

    # Button to download the edited DataFrame as a CSV file
    if st.button(f"Download Edited CSV - Image {image_index}"):
        csv = edited_df.to_csv(index=False).encode()  # Convert DataFrame to CSV bytes
        b64 = base64.b64encode(csv).decode()  # Encode CSV bytes to base64
        href = f'<a href="data:file/csv;base64,{b64}" download="edited_ocr_results_Image_{image_index}.csv">Click here to download</a>'
        st.markdown(href, unsafe_allow_html=True)  # Display download link

    ocr_results.append(ocr_df)
    return ocr_results

# Image uploader
images = st.file_uploader(label='Upload your images here', accept_multiple_files=True)

if images:
    all_ocr_results = []  # List to store OCR results from all images
    for idx, image in enumerate(images):
        all_ocr_results.extend(perform_ocr_editable_df(image, idx + 1))

    ### Combine all DataFrames into one
    combined_df = pd.concat([df.reset_index(drop=True) for df in all_ocr_results], axis=1)

    # Display the combined DataFrame
    st.write("### Combined OCR Results for All Images")
    st.write(combined_df)




 