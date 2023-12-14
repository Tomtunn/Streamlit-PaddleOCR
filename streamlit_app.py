import streamlit as st
import json
import numpy as np
import base64
import io
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import fitz
from ocr import load_model, inference

import os
from streamlit_img_label import st_img_label
from streamlit_img_label.manage import ImageManager, ImageDirManager

json_template_path = "template_file.json"

def read_pdf(doc, page_number):
    pdf_page = doc[page_number]
    pix = pdf_page.get_pixmap(dpi=300)
    pdf_data = io.BytesIO(pix.pil_tobytes(format='jpeg'))
    # st.image(Image.open(pdf_data), caption=f"Page {page_number}", use_column_width=True)
    return pdf_data

# Next and previous page function
def next_page():
    st.session_state.page_number += 1
        

def previous_page():
    st.session_state.page_number -= 1

def run(img_dir, data_type):

    # st.set_option("deprecation.showfileUploaderEncoding", False)
    idm = ImageDirManager(img_dir)

    if "files" not in st.session_state:
        st.session_state["files"] = idm.get_all_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0
    else:
        idm.set_all_files(st.session_state["files"]) 
        idm.set_annotation_files(st.session_state["annotation_files"])
    
    def refresh():
        st.session_state["files"] = idm.get_all_files()
        st.session_state["annotation_files"] = idm.get_exist_annotation_files()
        st.session_state["image_index"] = 0

    def next_image():
        image_index = st.session_state["image_index"]
        if image_index < len(st.session_state["files"]) - 1:
            st.session_state["image_index"] += 1
        else:
            st.warning('This is the last image.')

    def previous_image():
        image_index = st.session_state["image_index"]
        if image_index > 0:
            st.session_state["image_index"] -= 1
        else:
            st.warning('This is the first image.')

    def next_annotate_file():
        image_index = st.session_state["image_index"]
        next_image_index = idm.get_next_annotation_image(image_index)
        if next_image_index:
            st.session_state["image_index"] = idm.get_next_annotation_image(image_index)
        else:
            st.warning("All images are annotated.")
            next_image()

    def go_to_image():
        file_index = st.session_state["files"].index(st.session_state["file"])
        st.session_state["image_index"] = file_index
        
    def annotate():
        im.save_annotation()
        # image_annotate_file_name = uploaded_file.split(".")[0] + ".xml"
        # if image_annotate_file_name not in st.session_state["annotation_files"]:
            # st.session_state["annotation_files"].append(image_annotate_file_name)
        next_annotate_file()


    # Sidebar: show status
    # n_files = len(st.session_state["files"])
    # n_annotate_files = len(st.session_state["annotation_files"])
    # st.sidebar.write("Total files:", n_files)
    # st.sidebar.write("Total annotate files:", n_annotate_files)
    # st.sidebar.write("Remaining files:", n_files - n_annotate_files)
    
    # load initail model
    tabular_engine = load_model()
    

    options = ["Manual labelling", "Auto-extraction"]
    selected_option = st.sidebar.radio("Select an option:", options)

    if selected_option == "Manual labelling":
        selected_template = st.sidebar.text_input("Input template", "")

    if selected_option == "Auto-extraction":
        # load and select json template
        with open(json_template_path) as f:
            template_dict = json.load(f)
        selected_template = st.sidebar.selectbox("Select the template:", list(template_dict.keys()))


    # st.sidebar.selectbox(
    #     "Files",
    #     st.session_state["files"],
    #     index=st.session_state["image_index"],
    #     on_change=go_to_image,
    #     key="file",
    # )

    file = st.file_uploader("Upload a file:", type=["pdf", "png", "jpg"], accept_multiple_files=True)
    
    # Main content: annotate images
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 0

    for uploaded_file in file:
        if uploaded_file.type == "application/pdf":
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            n_max_page = len(doc)
            # page_number = 0
            pdf_data = read_pdf(doc, st.session_state.page_number)
            # col1, col2 = st.columns(2)
            # with col1:
            #     st.button(label="Previous image", on_click=previous_image)
            # with col2:
            #     st.button(label="Next image", on_click=next_image)

        # img_file_name = idm.get_image(st.session_state["image_index"])
        # img_path = os.path.join(img_dir, img_file_name)
            
            im = ImageManager(pdf_data, json_template_path, selected_template)
            img = im.get_img()
            resized_img = im.resizing_img()
            resized_rects = im.get_resized_rects()
            rects = st_img_label(resized_img, box_color="red", rects=resized_rects)

            # Previous and next page buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.session_state.page_number > 0:
                    st.button(label="Previous page", on_click=previous_page)
                elif st.session_state.page_number == 0:
                    st.warning('This is the first page.')
            with col2:
                st.write(f"Page {st.session_state.page_number + 1}/ {n_max_page}")
            with col3:
                if st.session_state.page_number < n_max_page - 1:
                    st.button(label="Next page", on_click=next_page)
                elif st.session_state.page_number == n_max_page - 1:
                    st.warning('This is the last page.')


            
        

        if rects:
            st.button(label="Save", on_click=annotate)
            preview_imgs = im.init_annotation(rects)

            for i, prev_img in enumerate(preview_imgs):
                prev_img[0].thumbnail((200, 200))
                col1, col2 = st.columns(2)
                with col1:
                    col1.image(prev_img[0])
                with col2:
                    default_index = 0
                    if prev_img[1]:
                        default_index = data_type.index(prev_img[1])
                    if prev_img[2]:
                        img_id = prev_img[2]
                    elif not prev_img[2]:
                        img_id = ""
                         
                    select_type = col2.selectbox(
                        "output_type", data_type, key=f"type_{i}", index=default_index
                    )
                    select_id = col2.text_input('column_name', img_id, key=f"label_{i}")
                    im.set_annotation(i, select_type, select_id)
                    
                    bbox = im.get_current_rects()
                    xmin = bbox[i]["left"]
                    ymin = bbox[i]["top"]
                    xmax = bbox[i]["left"] + bbox[i]["width"]
                    ymax = bbox[i]["top"] + bbox[i]["height"]
                    
                    #create data_input
                    current_bbox = [
                            {
                                "id": select_id,
                                "type": "image",
                                "box_pos": [xmin, ymin, xmax, ymax]
                            }
                        ]
                        
                    data_input = [
                        {
                            "template_name": current_bbox,
                            "image": img,
                            "page": st.session_state.page_number,
                            }
                        ]
                    
                    predict_df = inference(data_input, tabular_engine)
                    st.write(predict_df)


if __name__ == "__main__":
    data_types = ["table", "image"]
    run(img_dir="img_dir", data_type=data_types)

