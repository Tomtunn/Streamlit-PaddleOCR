import cv2
from paddleocr import PPStructure
import pandas as pd
from tablepyxl import tablepyxl
from copy import deepcopy
import io
import numpy as np

def load_model():
    """
    load model from paddleocr (PPStructure)

    Returns:
        tabular engine model
    """
    table_engine = PPStructure(recovery=True, lang='en')
    return table_engine

def predict(table_engine, image):
    """
    predict table from image

    Args:
        table_engine: tabular engine model
        image: input image

    Returns:
        result of prediction
    """
    result = table_engine(image)
    return result

def process_result(result):
    """
    process result from prediction

    Args:
        result: result of prediction

    Returns:
        dataframe from result
    """
    result_cp = deepcopy(result)
    df_ls = []
    for region in result_cp:
        # if region is table
        if 'html' in region['res']:
            html = region['res']['html']
            wb = tablepyxl.document_to_workbook(html)
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            df = pd.read_excel(output, header=None)
            df_ls.append(df)
        # else region is circle
        else:
            text_ls = []
            for text in region['res']:
                text_ls.append(text['text'])
            df = pd.DataFrame(text_ls)
            df_ls.append(df)
            
    return pd.concat(df_ls, axis=0) 

def inference(data_input, engine):
    """
    inference from input data

    Args:
        data_input (dict): input data
        engine : engine model

    Returns:
        dataframe from result    
    """
    df_predict_ls = []
    for page_index in range(len(data_input)):
        page = data_input[page_index]
        # image_path = page['path']
        # image = cv2.imread(image_path)
        image = page['image']
        image = np.asarray(image)
        for box_index in range(len(page['template_name'])):
            x1, y1, x2, y2 = page['template_name'][box_index]['box_pos']
            roi_image = image[y1:y2, x1:x2]
            result = predict(engine, roi_image)
            df_predict = process_result(result)
            columns_ls = [page['template_name'][box_index]['id']] * (len(df_predict.columns))
            df_predict.columns = columns_ls
            df_predict_ls.append(df_predict)
            
    return pd.concat(df_predict_ls, axis=1)