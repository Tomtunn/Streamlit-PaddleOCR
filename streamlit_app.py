import streamlit as st
import json
import numpy as np
import base64
import io
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import fitz
from ocr import load_model, inference
import pandas as pd
import os
from streamlit_img_label import st_img_label
from streamlit_img_label.manage import ImageManager, ImageDirManager

json_template_path = "template_file.json"


def read_pdf(_doc, page_number):
    pdf_page = _doc[page_number]
    pix = pdf_page.get_pixmap(dpi=300)
    pdf_data = io.BytesIO(pix.pil_tobytes(format="jpeg"))
    return pdf_data


def get_predict(_data_input, _engine):
    predict_df = inference(_data_input, _engine)
    return predict_df


def next_page():
    st.session_state.page_number += 1


def previous_page():
    st.session_state.page_number -= 1


def run(img_dir, engine):

    pdf_data = None
    n_max_page = 0
    idm = ImageDirManager(img_dir)

    if "files" not in st.session_state:
        st.session_state["files"] = idm.get_all_files()
        st.session_state["image_index"] = 0
    else:
        idm.set_all_files(st.session_state["files"])

    st.sidebar.title("**Plato - OCR Web App 👁️**")
    st.sidebar.subheader("**Template Option**")
    options = ["Manual labelling", "Auto-extraction"]
    selected_option = st.sidebar.radio("Select an option:", options)

    if selected_option == "Manual labelling":
        selected_template = st.sidebar.text_input("Input template", "")

    if selected_option == "Auto-extraction":
        with open(json_template_path) as f:
            template_dict = json.load(f)
        selected_template = st.sidebar.selectbox(
            "Select the template:", list(template_dict.keys())
        )





    def reset_page_number():
        st.session_state.page_number = 0

    def go_to_image():
        file_index = st.session_state["files"].index(st.session_state["file"])
        st.session_state["image_index"] = file_index
        reset_page_number()

    st.sidebar.subheader("Input file")

    img_file_name = "_____"

    uploaded_file = st.sidebar.file_uploader(
        "Upload a file:",
        type=["pdf", "png", "jpg"],
        accept_multiple_files=False,
        on_change=reset_page_number,
    )
    if uploaded_file:
        img_file_name = uploaded_file.name
        img_path = os.path.join(img_dir, img_file_name)
        with open(img_path, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"File '{uploaded_file.name}' successfully saved to '{img_dir}'.")
        st.session_state["files"] = idm.get_all_files()

    if st.sidebar.selectbox(
        "Files",
        st.session_state["files"],
        index=st.session_state["image_index"],
        on_change=go_to_image,
        key="file",
    ):
        img_file_name = idm.get_image(st.session_state["image_index"])

    st.title("Work Space")
    st.write(f"**Current File: {img_file_name}**")

    img_path = os.path.join(img_dir, img_file_name)

    def refresh():
        st.session_state["files"] = idm.get_all_files()
        st.session_state["image_index"] = 0

    def next_image():
        image_index = st.session_state["image_index"]
        if image_index < len(st.session_state["files"]) - 1:
            st.session_state["image_index"] += 1
        else:
            st.warning("This is the last image.")

    def previous_image():
        image_index = st.session_state["image_index"]
        if image_index > 0:
            st.session_state["image_index"] -= 1
        else:
            st.warning("This is the first image.")


    def annotate():
        im.save_annotation()
        st.session_state.button = not st.session_state.button

    def get_box_coords(rects, i):
        xmin = rects[i]["left"]
        ymin = rects[i]["top"]
        xmax = rects[i]["left"] + rects[i]["width"]
        ymax = rects[i]["top"] + rects[i]["height"]
        return (xmin, ymin, xmax, ymax)

    def reset_page_number():
        st.session_state.page_number = 0

    # Sidebar: show status
    n_files = len(st.session_state["files"])
    st.sidebar.write("Total files:", n_files)

    # Main content: annotate images
    if "page_number" not in st.session_state:
        reset_page_number()

    if "button" not in st.session_state:
        st.session_state.button = False

    if img_path.split(".")[-1] == "jpg" or img_path.split(".")[-1] == "png":
        input_data = img_path
        n_max_page = 1
    if img_path.split(".")[-1] == "pdf":
        doc = fitz.open(img_path)
        n_max_page = len(doc)
        input_data = read_pdf(doc, st.session_state.page_number)

    show_navigation_buttons = n_max_page > 1

    im = ImageManager(input_data, json_template_path, selected_template)
    img = im.get_img()
    resized_img = im.resizing_img(1200, 1200)
    resized_rects = im.get_resized_rects()
    rects = st_img_label(resized_img, box_color="red", rects=resized_rects)

    # Previous and next page buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.page_number > 0 and show_navigation_buttons:
            st.button(label="Previous page", on_click=previous_page)
    with col2:
        st.write(f"Page {st.session_state.page_number + 1}/ {n_max_page}")
    with col3:
        if st.session_state.page_number < n_max_page - 1 and show_navigation_buttons:
            st.button(label="Next page", on_click=next_page)
        elif st.session_state.page_number == n_max_page - 1 and show_navigation_buttons:
            st.warning("This is the last page.")

    if rects:
        st.button(label="Save Template", on_click=annotate)
        preview_imgs = im.init_annotation(rects)

        df_ls = [pd.DataFrame()] * len(
            preview_imgs
        )  # crete list of zeros for save annotation predict df
        for i, prev_img in enumerate(preview_imgs):
            prev_img[0].thumbnail((500, 300))
            col1, col2, col3 = st.columns(3)
            with col1:
                col1.image(prev_img[0])
            with col2:
                if prev_img[2]:
                    img_id = prev_img[2]
                elif not prev_img[2]:
                    img_id = ""

                col2.write("Output Type")
                select_type = ""
                img_checkbox = st.checkbox("image", key=f"img_check_{i}")
                text_checkbox = st.checkbox("table", key=f"text_check_{i}")
                if img_checkbox and not text_checkbox:
                    select_type = "image"
                if text_checkbox and not img_checkbox:
                    select_type = "table"
                if img_checkbox and text_checkbox:
                    select_type = "both"

                select_id = col2.text_input(
                    "ID Name", img_id if img_id else f"box_{i}", key=f"label_{i}"
                )
                im.set_annotation(i, select_type, select_id)
            with col3:

                if select_type == "table" or select_type == "both":
                    xmin, ymin, xmax, ymax = get_box_coords(rects, i)

                    # create data_input
                    current_bbox = [
                        {
                            "id": select_id,
                            "type": "image",
                            "box_pos": [xmin, ymin, xmax, ymax],
                        }
                    ]
                    data_input = [
                        {
                            "template_name": current_bbox,
                            "image": img,
                            "page": st.session_state.page_number,
                        }
                    ]

                    predict_df = inference(data_input, engine)  # ocr image
                    current_df = st.data_editor(
                        predict_df, num_rows="dynamic", key=f"dataframe{i}"
                    )  # editable dataframe
                    df_ls[i] = current_df
                
                if selected_option == "Auto-extraction":
                    box_type = template_dict[selected_template][i]["type"]
                    if box_type == "table" or box_type == "both":
                        xmin, ymin, xmax, ymax = get_box_coords(rects, i)

                        # create data_input
                        current_bbox = [
                            {
                                "id": select_id,
                                "type": "image",
                                "box_pos": [xmin, ymin, xmax, ymax],
                            }
                        ]
                        data_input = [
                            {
                                "template_name": current_bbox,
                                "image": img,
                                "page": st.session_state.page_number,
                            }
                        ]

                        predict_df = inference(data_input, engine)  # ocr image
                        current_df = st.data_editor(
                            predict_df, num_rows="dynamic", key=f"dataframe{i}"
                        )  # editable dataframe
                        df_ls[i] = current_df

        # button to concatenate dataframe
        if st.button(label="Concatenate Dataframes"):
            # if there are no dataframes
            if len(df_ls) == 0:
                st.warning("No dataframe to concatenate")
            # if there are dataframes
            else:
                try:
                    concat_df = pd.concat(
                        df_ls, axis=1
                    )  # horizontal concatenate dataframe
                    st.data_editor(
                        concat_df, num_rows="dynamic", key="concat_dataframe"
                    )  # display concatenated dataframe
                    csv = concat_df.to_csv(
                        index=False
                    ).encode()  # Convert DataFrame to CSV bytes
                    b64 = base64.b64encode(csv).decode()  # Encode CSV bytes to base64
                    href = f'<a href="data:file/csv;base64,{b64}" download="concatenated_dataframe.csv">Click here to download</a>'
                    st.markdown(href, unsafe_allow_html=True)  # Display download link
                    # Check if selected_id (column name) is the same
                    if concat_df.columns.duplicated().any():
                        st.warning("Selected ID names are not unique")
                except Exception as e:
                    st.error(f"Error concatenating dataframes: {e}")

        st.write("File name will be the same as ID Name")

        if st.button(label="Save Dataframe"):
            file_name = img_file_name.split(".")[0]
            page_name = data_input[0]["page"]
            folder_name = os.path.join(img_dir, file_name, "csv")
            os.makedirs(folder_name, exist_ok=True)
            # save concat dataframe
            try:
                concat_df = pd.concat(df_ls, axis=1)
                concat_df.to_csv(
                    os.path.join(folder_name, f"{file_name}_{page_name}.csv"), index=False
                )
                st.success(f"Dataframe saved successfully at {folder_name}")
            except Exception as e:
                st.error(f"Error saving dataframe: {e} {folder_name}")

        if st.button(label="Save All Image"):
            file_name = img_file_name.split(".")[0]
            page_name = data_input[0]["page"]
            folder_name = os.path.join(img_dir, file_name, "img")
            os.makedirs(folder_name, exist_ok=True)
            # crop and save image
            for i, box_info in enumerate(rects):
                xmin, ymin, xmax, ymax = get_box_coords(rects, i)
                cropped_image = img.crop((xmin, ymin, xmax, ymax))
                output_path = os.path.join(folder_name, box_info["id"] + f"{page_name}.png")
                if box_info["label"] == "image" or box_info["label"] == "both":
                    try:
                        cropped_image.save(output_path)
                        st.success(f"Image saved successfully at {output_path}")
                    except Exception as e:
                        st.error(f"Error saving image: {e} {output_path}")
                if selected_option == "Auto-extraction":
                    box_type = template_dict[selected_template][i]["type"]
                    if box_type == "image" or box_type == "both":
                        try:
                            cropped_image.save(output_path)
                            st.success(f"Image saved successfully at {output_path}")
                        except Exception as e:
                            st.error(f"Error saving image: {e} {output_path}")
                else:
                    st.warning("Select image checkbox to save image")


if __name__ == "__main__":
    st.set_page_config(page_title="The Ramsey Highlights", layout="wide")
    directory_name = "data_dir"
    os.makedirs(directory_name, exist_ok=True)

    @st.cache_resource()
    def get_model():
        table_engine = load_model()
        return table_engine

    table_engine = get_model()
    run(img_dir=directory_name, engine=table_engine)
