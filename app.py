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
        
        annotated_images_list = []  # List to store annotated images

        for index, uploaded_file in enumerate(file):
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
                    key=f"canvas_{index}",  # Make the key unique
                    width=image.size[0],
                )

                confirmation_button_key = f"confirmation_button_{index}"

                if st.button("Confirm this region", key=confirmation_button_key):
                    boxes = canvas_result.json_data["objects"]
                    annotated_images, annotated_arrays = capture_annotated_region(image, boxes)
                    annotated_images_list.extend(annotated_images)  # Add annotated images to the list

        # Display all annotated images
        for i, annotated_image in enumerate(annotated_images_list):
            st.image(annotated_image, caption=f"Captured Image {i + 1}", use_column_width=False)
                        
            st.text(f"Array of Captured Image {i + 1}:\n{str(annotated_arrays[i].tolist())}")

            # Show converted image from PDF file        
            for uploaded_file.type in file:
                 if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf") 
                    page_number = 0

                    show_image(st.session_state.page_number)
                    print(st.session_state.page_number)

                    next_button_key = f"next_page_button_{index}"
                    previous_button_key = f"previous_page_button_{index}"

                    if st.sidebar.button(f"Next Page {index}", key=next_button_key):
                        print("Next Page", st.session_state.page_number)

                    if st.sidebar.button(f"Previous Page {index}", key=previous_button_key):
                        print("Previous Page", st.session_state.page_number)
