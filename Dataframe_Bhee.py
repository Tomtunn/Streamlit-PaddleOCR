# import easyocr as ocr
import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import base64
from ocr import load_model, inference

table_engine = load_model()
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
# def perform_ocr_editable_df(image, image_index):
#     reader = ocr.Reader(['en'], model_storage_directory='.')
#     ocr_results = []

#     img = Image.open(image)  # Read the uploaded image
#     st.image(img, caption=f"Uploaded Image - {image_index}", use_column_width=True)
    
#     result = reader.readtext(np.array(img))  # Perform OCR
#     ocr_texts = [text[1] for text in result]

#     # Create a DataFrame from the OCR results
#     ocr_df = pd.DataFrame(ocr_texts, columns=["Text"])

#     # Display the OCR results DataFrame
#     st.write(f"### OCR Results for Image {image_index}")

#     # Use st.data_editor for interactive editing with dynamic row addition/deletion
#     edited_df = st.data_editor(ocr_df, num_rows="dynamic")

#     # Button to download the edited DataFrame as a CSV file
#     if st.button(f"Download Edited CSV - Image {image_index}"):
#         csv = edited_df.to_csv(index=False).encode()  # Convert DataFrame to CSV bytes
#         b64 = base64.b64encode(csv).decode()  # Encode CSV bytes to base64
#         href = f'<a href="data:file/csv;base64,{b64}" download="edited_ocr_results_Image_{image_index}.csv">Click here to download</a>'
#         st.markdown(href, unsafe_allow_html=True)  # Display download link

#     ocr_results.append(ocr_df)
#     return ocr_results

def perform_ocr(data_input, engine):
    """
    perform ocr from data input

    Args:
        data_input: data input
        engine: tabular engine model

    Returns:
        result of paddleocr
    """
    result_df = inference(data_input, engine)
    return result_df

# Image uploader
images = st.file_uploader(label='Upload your images here', accept_multiple_files=True)

if images:
    for idx, image in enumerate(images):
        image_pil = Image.open(image) # foor testing paddleocr
        # sample data input
        tmp = {
            "name1": [
                {
                    "id": "circle_right",
                    "type": "image",
                    "box_pos": [800, 1530, 1200, 1850]  # x1, y1, x2, y2
                },
                {
                    "id": "circle_left",
                    "type": "image",
                    "box_pos": [1500, 1530, 1900, 1850]
                }
            ],
            "name2": [
                {
                    "id": "name",
                    "type": "text",
                    "box_pos": [127.440, 741.671, 204.817, 749.921]
                },
                {
                    "id": "id",
                    "type": "text",
                    "box_pos": [127.440, 721.511, 164.136, 729.761]
                },
                {
                    "id": "DOB",
                    "type": "text",
                    "box_pos": [127.440, 708.551, 164.119, 716.801]
                }
            ]
        }

        data_input = [{
                "template_name": tmp['name1'],
                "image": image_pil,
                "page": 1,
        }]
        # perform_ocr_editable_df(image, idx + 1)
        result_df = perform_ocr(data_input, table_engine)
        edited_df = st.data_editor(result_df, num_rows="dynamic")
        csv = edited_df.to_csv(index=False).encode()  # Convert DataFrame to CSV bytes
        b64 = base64.b64encode(csv).decode()  # Encode CSV bytes to base64
        href = f'<a href="data:file/csv;base64,{b64}" download="edited_ocr_results_Image_.csv">Click here to download</a>'
        st.markdown(href, unsafe_allow_html=True)  # Display download link












