import cv2
from paddleocr import PPStructure
import pandas as pd
from tablepyxl import tablepyxl
from copy import deepcopy
import io
import numpy as np
# from deskew import determine_skew
# from skimage.transform import rotate

# def strighten_image(img):
#     """
#     img: np.array

#     rotate image to strighten
#     """
#     angle = determine_skew(img)
#     rotated = rotate(img, angle, resize=True) * 255
#     rotated_img = rotated.astype(np.uint8)
#     return rotated_img, angle

def load_model():
    """
    load model from paddleocr (PPStructure)

    Returns:
        tabular engine model
    """
    table_engine = PPStructure(recovery=True, lang='en', layout=False)
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
    # image, angle = strighten_image(image)
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
        # if html are available
        if 'html' in region['res']:
            # try to convert html to dataframe with tablepyxl
            try:
                html = region['res']['html']
                wb = tablepyxl.document_to_workbook(html)
                output = io.BytesIO()
                wb.save(output)
                output.seek(0)
                df = pd.read_excel(output, header=None)
                df = df.dropna(how='all').dropna(axis=1, how='all')
                df_ls.append(df)
            # if tablepyxl give error, try to convert html to dataframe with pandas
            except:
                try:
                    df = pd.read_html(result[0]['res']['html'])[0]
                    df = df.dropna(how='all').dropna(axis=1, how='all')
                    df_ls.append(df)
                except:
                    df = pd.DataFrame()
                    df_ls.append(df)
        else:
            # empty dataframe
            df = pd.DataFrame()
            df_ls.append(df)
            
    # concat dataframe if there are more than 1 dataframe  
    if len(df_ls) == 0:
        return pd.DataFrame()
    else:    
        return pd.concat(df_ls, axis=0).reset_index(drop=True)

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
        image = page['image']
        image = np.asarray(image)
        for box_index in range(len(page['template_name'])):
            x1, y1, x2, y2 = page['template_name'][box_index]['box_pos']
            roi_image = image[y1:y2, x1:x2]
            result = predict(engine, roi_image)
            df_predict = process_result(result)
            id_column = page['template_name'][box_index]['id']
            index_columns = df_predict.columns.get_level_values(0)
            df_predict.columns = pd.MultiIndex.from_product([[id_column], index_columns])
            df_predict_ls.append(df_predict)
            
    return pd.concat(df_predict_ls, axis=1)