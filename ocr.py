# <<<<<<< HEAD
import streamlit as st
import numpy as np
import base64
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
from pdf2image import convert_from_bytes, convert_from_path

poppler_path = r'C:\Users\user\Desktop\EGBI_433_image_processing\Release-23.11.0-0\poppler-23.11.0\Library\bin'

st.set_page_config(
    page_title="OCR Web App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.success("OCR WebApp")
st.title("OCR for Ophthalmology document")
st.subheader("You can easily upload Ophthalmology test document for Optical character recognition (OCR) here.")
st.subheader("Please select your extraction method")

# Create a list of options
options = ["Auto-extraction", "Manual labelling"]

# Use selectbox to create an option selection dropdown
selected_option = st.radio("Select an option:", options)

# Display the selected option
file = None

def displayPDF(uploaded_file):
    # Read file as bytes:
    bytes_data = uploaded_file.getvalue()
    # Convert to utf-8
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    # Embed PDF in HTML and scale the size
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    # Display file
    st.markdown(pdf_display, unsafe_allow_html=True)

# Capture annotated region
def capture_annotated_region(image, boxes):
    annotated_images = []
    annotated_arrays = []
    for box in boxes:
        x, y, x1, y1 = box["left"], box["top"], box["left"] + box["width"], box["top"] + box["height"]
        annotated_image = image.crop((x, y, x1, y1))
        annotated_images.append(annotated_image)

        annotated_array = np.array(annotated_image)
        annotated_arrays.append(annotated_array)
    return annotated_images, annotated_arrays

# Auto-extraction function

if selected_option == "Auto-extraction":
    st.write("Please upload only PDF file")
    file = st.file_uploader("Upload a file:", type=["pdf"], accept_multiple_files=True)
   
    if file is not None and len(file) > 0:
        st.write(f"You have uploaded {len(file)} file(s).")
        file = file[0]
        if file.type != "application/pdf":
            st.error("This file type is not available for auto-extraction. Please upload a PDF file.")
        else:
            displayPDF(file)   

            if st.button("Perform OCR"):
                # OCR process algorithm
                st.text("OCR processing completed") 

# Manual labelling function
elif selected_option == "Manual labelling":
    st.write("Please upload PDF, PNG, or JPG file")
    file = st.file_uploader("Upload a file:", type=["pdf", "png", "jpg"], accept_multiple_files=True)

    if file is not None: 
        st.write(f"You have uploaded {len(file)} file(s).")
        for uploaded_file in file:

            if uploaded_file.type.startswith('image'):
                image = Image.open(uploaded_file)
                st.subheader("Please draw an annotation box") 
                canvas_result = st_canvas(
                    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                    stroke_width=2,
                    stroke_color="red",
                    background_image=image,
                    update_streamlit=True,
                    height=image.size[1],
                    drawing_mode="rect",
                    key="canvas",
                    width=image.size[0],
                )

                if st.button("Confirm this region"):
                    boxes = canvas_result.json_data["objects"]
                    annotated_images, annotated_arrays = capture_annotated_region(image, boxes)

                    for i, annotated_image in enumerate(annotated_images):
                        st.image(annotated_image, caption=f"Captured Image {i + 1}", use_column_width=False)

                        st.text(f"Array of Captured Image {i + 1}:\n{str(annotated_arrays[i].tolist())}")
            
            elif uploaded_file.type == "application/pdf":
                pdf_images = convert_from_bytes(uploaded_file.read(), poppler_path=poppler_path)  
                for i, pdf_image in enumerate(pdf_images):
                    st.image(pdf_image, caption=f"Page {i + 1}", use_column_width=False)

                    st.subheader(f"Page {i + 1}: Please draw an annotation box")
                    canvas_result = st_canvas(
                        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                        stroke_width=2,
                        stroke_color="red",
                        background_image=pdf_image,
                        update_streamlit=True,
                        height=pdf_image.size[1],
                        drawing_mode="rect",
                        key=f"canvas_page_{i}",
                        width=pdf_image.size[0],
                    )

                    if st.button(f"Confirm annotations for Page {i + 1}"):
                        boxes = canvas_result.json_data["objects"]
                        annotated_images, annotated_arrays = capture_annotated_region(pdf_image, boxes)

                        for j, annotated_image in enumerate(annotated_images):
                            st.image(annotated_image, caption=f"Captured Image {j + 1}", use_column_width=False)
                            st.text(f"Array of Captured Image {j + 1}:\n{str(annotated_arrays[j].tolist())}")


# =======
# import os
# import cv2
# from paddleocr import PPStructure
# import pandas as pd
# from tablepyxl import tablepyxl
# from copy import deepcopy
# import io

# def load_model():
#     """
#     load model from paddleocr (PPStructure)

#     Returns:
#         tabular engine model
#     """
#     table_engine = PPStructure(recovery=True, lang='en')
#     return table_engine

# def predict(table_engine, image):
#     """
#     predict table from image

#     Args:
#         table_engine: tabular engine model
#         image: input image

#     Returns:
#         result of prediction
#     """
#     result = table_engine(image)
#     return result

# def process_result(result):
#     """
#     process result from prediction

#     Args:
#         result: result of prediction

#     Returns:
#         dataframe from result
#     """
#     result_cp = deepcopy(result)
#     df_ls = []
#     for region in result_cp:
#         # if region is table
#         if 'html' in region['res']:
#             html = region['res']['html']
#             wb = tablepyxl.document_to_workbook(html)
#             output = io.BytesIO()
#             wb.save(output)
#             output.seek(0)
#             df = pd.read_excel(output, header=None)
#             df_ls.append(df)
#         # else region is circle
#         else:
#             text_ls = []
#             for text in region['res']:
#                 text_ls.append(text['text'])
#             df = pd.DataFrame(text_ls)
#             df_ls.append(df)
            
#     return pd.concat(df_ls, axis=0) 

# def inference(data_input, engine):
#     """
#     inference from input data

#     Args:
#         data_input (dict): input data
#         engine : engine model

#     Returns:
#         dataframe from result    
#     """
#     df_predict_ls = []
#     for page_index in range(len(data_input)):
#         page = data_input[page_index]
#         image_path = page['path']
#         image = cv2.imread(image_path)
        
#         for box_index in range(len(page['template_name'])):
#             x1, y1, x2, y2 = page['template_name'][box_index]['box_pos']
#             roi_image = image[y1:y2, x1:x2]
#             result = predict(engine, roi_image)
#             df_predict = process_result(result)
#             columns_ls = [page['template_name'][box_index]['id']] * (len(df_predict.columns))
#             df_predict.columns = columns_ls
#             df_predict_ls.append(df_predict)     
#     return pd.concat(df_predict_ls, axis=1)
# >>>>>>> 7825ad52a014ef4d1b21939c07a06d9a778df182
