import streamlit as st
import numpy as np
import base64
import io
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import fitz
 
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

# Initialize session state for persistent variables
if "page_number" not in st.session_state:
    st.session_state.page_number = 0

if "annotations_by_page" not in st.session_state:
    st.session_state.annotations_by_page = {}

def show_image(page_number, files):
    if files[page_number].type.startswith('image'):
        image = Image.open(files[page_number])
        st.subheader("Please draw an annotation box") 
        canvas_key = f"canvas_{page_number}"
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="red",
            background_image=image,
            update_streamlit=True,
            height=image.size[1],
            drawing_mode="rect",
            key=canvas_key,
            width=image.size[0],
        )

        confirmation_button_key = f"confirmation_button_{page_number}"

        if st.button("Confirm this region", key=confirmation_button_key):
            boxes = canvas_result.json_data["objects"]
            st.session_state.annotations_by_page[page_number] = boxes  # Store annotations for this page
            st.balloons()  # Trigger balloons after successful download

        # Display the annotated image if annotations exist for this page
        if page_number in st.session_state.annotations_by_page:
            annotated_images, annotated_arrays = capture_annotated_region(image, st.session_state.annotations_by_page[page_number])
            for i, annotated_image in enumerate(annotated_images):
                st.image(annotated_image, caption=f"Captured Image {i + 1}", use_column_width=False)
                st.text(f"Array of Captured Image {i + 1}:\n{str(annotated_arrays[i].tolist())}")

    elif files[page_number].type == "application/pdf":
        doc = fitz.open(stream=files[page_number].read(), filetype="pdf") 
        st.session_state.page_number = st.session_state.page_number % len(doc)
        pdf_page = doc[st.session_state.page_number]
        pix = pdf_page.get_pixmap(dpi=300)
        image = Image.open(io.BytesIO(pix.pil_tobytes(format='jpeg')))
        st.image(image, caption=f"Page {st.session_state.page_number + 1}", use_column_width=True)

# Page Interface
st.set_page_config(
    page_title="OCR Web App",
    page_icon="👀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Local path to the logo image
logo_path = r'C:\Users\Asus\Vs code\WEB APP_OCR\logo.png'  
# Open the logo image
logo_image = Image.open(logo_path)

# Display the logo in the sidebar
st.sidebar.image(logo_image,  caption='BheeBuaPoonTongEarth', use_column_width=True)

st.sidebar.success("OCR WebApp")
st.title("OCR for Ophthalmology Document")
st.subheader("You can easily upload Ophthalmology test document for Optical character recognition (OCR) here.")
st.subheader("Please select your extraction method")

# Extraction method selection
options = ["Manual labelling", "Auto-extraction"]
selected_option = st.radio("Select an option:", options)

# Display initial image
files = None

# Manual labelling
if selected_option == "Manual labelling":
    st.write("Please upload PDF, PNG, or JPG file")
    files = st.file_uploader("Upload files:", type=["pdf", "png", "jpg"], accept_multiple_files=True)

    if files is not None and len(files) > 0:
        st.write(f"You have uploaded {len(files)} file(s).")

        # Display the initial image
        show_image(st.session_state.page_number, files)

        # Navigation buttons
        if st.button("Next Page"):
            st.session_state.page_number = (st.session_state.page_number + 1) % len(files)
            show_image(st.session_state.page_number, files)

        if st.button("Previous Page"):
            st.session_state.page_number = (st.session_state.page_number - 1) % len(files)
            show_image(st.session_state.page_number, files)

# Auto-extraction
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

