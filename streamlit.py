import streamlit as st
import numpy as np
import json
import base64
import os
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
from pdf2image import convert_from_bytes, convert_from_path

poppler_path = r'C:/Users/user/Desktop/EGBI_433_image_processing/Release-23.11.0-0/poppler-23.11.0/Library/bin'

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
   
   #Dropdown for template selection
    template_files = [file for file in os.listdir() if file.endswith(".json")]
    selected_template = st.selectbox("Select a template:", template_files, key="template_selection")

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

            # Display image and allow annotation 
            if uploaded_file.type.startswith('image'):
                image = Image.open(uploaded_file)
                st.subheader("Please draw an annotation box") 
                canvas_result = st_canvas(
                    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                    stroke_width=2,
                    stroke_color="red",
                    background_image=image,
                    # update_streamlit=True,
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

                        # Display coordinates in the sidebar
                        # for j, box in enumerate(boxes):
                            # st.sidebar.text(f"Box {j + 1} - Coordinates: Left={box['left']}, Top={box['top']}, Width={box['width']}, Height={box['height']}")

            # Display converted PDF and allow annotation           
            elif uploaded_file.type == "application/pdf":
                pdf_images = convert_from_bytes(uploaded_file.read(), poppler_path=poppler_path)  
                for i, pdf_image in enumerate(pdf_images):
                   
                    st.subheader(f"Page {i + 1}: Please draw an annotation box")
                    canvas_result = st_canvas(
                        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                        stroke_width=2,
                        stroke_color="red",
                        background_image=pdf_image,
                        # update_streamlit=True,

                        height=792,
                        drawing_mode="rect",
                        key=f"canvas_page_{i}",
                        width=612,
                    )

                    if st.button(f"Confirm annotations for Page {i + 1}"):
                        boxes = canvas_result.json_data["objects"]
                        annotated_images, annotated_arrays = capture_annotated_region(pdf_image, boxes)

                        for j, annotated_image in enumerate(annotated_images):
                            # st.image(annotated_image, caption=f"Captured Image {j + 1}", use_column_width=False)
                            st.text(f"Array of Captured Image {j + 1}:\n{str(annotated_arrays[j].tolist())}")

                            # Display coordinates in the sidebar
                            # for k, box in enumerate(boxes):
                                # st.sidebar.text(f"Page {i + 1} - Box {k + 1} - Coordinates: Left={box['left']}, Top={box['top']}, Width={box['width']}, Height={box['height']}")
