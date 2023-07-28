import glob
import re
import traceback
from pathlib import Path
from typing import List

import fitz
import utils
from constants import cmd_output_path
from loguru import logger
from PIL import Image
import numpy as np

def sign_img(img_path: str, offset: int = 5, output_path: str = None):
    try:
        img = Image.open(img_path)
        img = img.convert("RGBA")
        w, h = img.size
        img_array = np.array(img)
        points = []
        threshold = 100
        for j in range(w):
            for i in range(h):
                if img_array[i][j][0]>threshold and img_array[i][j][1]>threshold and img_array[i][j][2]>threshold:
                    img_array[i][j][3] = 0
                else:
                    img_array[i][j][0],img_array[i][j][1],img_array[i][j][2] = 0,0,0
                    points.append((i,j))
        points = np.array(points).reshape((-1, 2))
        min_value = np.min(points,axis=0)
        x1,y1 = min_value[0]-offset,min_value[1]-offset
        max_value = np.max(points,axis=0)
        x2,y2 = max_value[0]+offset,max_value[1]+offset
        sign_area = img_array[x1:x2,y1:y2]
        sign_img = Image.fromarray(sign_area)
        if output_path is None:
            output_path = Path(img_path).parent / f"{Path(img_path).stem}-签名.png"
        sign_img.save(output_path)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
