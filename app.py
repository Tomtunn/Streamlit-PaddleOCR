import streamlit as st
import numpy as np
import base64
import io
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import fitz

##################
## Page Interface ##
##################
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

# Extraction method selection
options = ["Manual labelling", "Auto-extraction"]
selected_option = st.radio("Select an option:", options)

# Display the selected option
file = None

# Function for display PDF file within the scaled pdf viewer
def displayPDF(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Function for capture annotated coordinates
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

##################

def show_image(page_number):
    pdf_page = doc[page_number]
    pix = pdf_page.get_pixmap(dpi=300)
    image = Image.open(io.BytesIO(pix.pil_tobytes(format='jpeg')))
    st.image(image, caption=f"Page {page_number}", use_column_width=True)

def next_page():
    st.session_state.page_number += 1

def previous_page():
    st.session_state.page_number -= 1

##################
## Manual labelling ##
##################
# If select manual labelling, come to this part

# Function for next and previous page
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0

if selected_option == "Manual labelling":
    st.write("Please upload PDF, PNG, or JPG file")
    file = st.file_uploader("Upload a file:", type=["pdf", "png", "jpg"], accept_multiple_files=True)

    if file is not None: 
        st.write(f"You have uploaded {len(file)} file(s).")
        for uploaded_file in file:
            # Annotation on the uploaded image
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

            # Show converted image from PDF file        
            elif uploaded_file.type == "application/pdf":
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf") 
                page_number = 0

                show_image(st.session_state.page_number)
                print(st.session_state.page_number)

                if st.sidebar.button("Next Page", on_click=next_page):
                    print("Next Page", st.session_state.page_number)

                if st.sidebar.button("Previous Page", on_click=previous_page):

                    print("Previous Page", st.session_state.page_number)
         

##################              
## Auto-extraction ##   
##################       
elif selected_option == "Auto-extraction":
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