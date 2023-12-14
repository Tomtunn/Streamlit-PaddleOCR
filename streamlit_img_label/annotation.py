import os
import json
# from pascal_voc_writer import Writer
from xml.etree import ElementTree as ET

"""
.. module:: streamlit_img_label
   :synopsis: annotation.
.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""


# def read_xml(img_file):
#     """read_xml
#     Read the xml annotation file and extract the bounding boxes if exists.

#     Args:
#         img_file(str): the image file.
#     Returns:
#         rects(list): the bounding boxes of the image.
#     """
#     file_name = img_file.split(".")[0]
#     if not os.path.isfile(f"{file_name}.xml"):
#         return []
#     tree = ET.parse(f"{file_name}.xml")
#     root = tree.getroot()

#     rects = []

#     for boxes in root.iter("object"):
#         label = boxes.find("name").text
#         ymin = int(boxes.find("bndbox/ymin").text)
#         xmin = int(boxes.find("bndbox/xmin").text)
#         ymax = int(boxes.find("bndbox/ymax").text)
#         xmax = int(boxes.find("bndbox/xmax").text)
#         rects.append(
#             {
#                 "left": xmin,
#                 "top": ymin,
#                 "width": xmax - xmin,
#                 "height": ymax - ymin,
#                 "label": label,
#             }
#         )
#     return rects

def read_json(json_file_path, template_name):
    if not os.path.isfile(json_file_path):
        return []
    with open(json_file_path) as f:
        template_dict = json.load(f)
    if template_name not in template_dict.keys():
        return []
    boxes_template = template_dict[template_name]
    rects = []
    for boxes in boxes_template:
        type_output = boxes["type"]
        type_id = boxes["id"]
        xmin = boxes["box_pos"][0]
        ymin = boxes["box_pos"][1]
        xmax = boxes["box_pos"][2]
        ymax = boxes["box_pos"][3]
        rects.append(
            {
                "left": xmin,
                "top": ymin,
                "width": xmax - xmin,
                "height": ymax - ymin,
                "label": type_output,
                "id": type_id
            }
        )
    return rects


# def output_xml(img_file, img, rects):
#     """output_xml
#     Output the xml image annotation file

#     Args:
#         img_file(str): the image file.
#         img(PIL.Image): the image object.
#         rects(list): the bounding boxes of the image.
#     """
#     file_name = img_file.split(".")[0]
#     writer = Writer(img_file, img.width, img.height)
#     for box in rects:
#         xmin = box["left"]
#         ymin = box["top"]
#         xmax = box["left"] + box["width"]
#         ymax = box["top"] + box["height"]

#         writer.addObject(box["label"], xmin, ymin, xmax, ymax)
#     writer.save(f"{file_name}.xml")

def output_json(json_file_path, templat_name, rects):

    with open(json_file_path) as f:
        template_dict = json.load(f)
    # writer = Writer(img_file, img.width, img.height)
    if templat_name in template_dict.keys():
        template_dict[templat_name] = []
    for box in rects:
        xmin = box["left"]
        ymin = box["top"]
        xmax = box["left"] + box["width"]
        ymax = box["top"] + box["height"]
    
        box_details = {'id': box["id"], 'type': box["label"], 'box_pos': [xmin, ymin, xmax, ymax]}

        if templat_name in template_dict.keys():
            template_dict[templat_name].append(box_details)
        else:
            template_dict[templat_name] = [box_details]

    with open(json_file_path, 'w') as json_file:
        json.dump(template_dict, json_file, indent=4)

#print(read_json('template.json', 'template1'))