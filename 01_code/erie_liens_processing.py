# -*- coding: utf-8 -*-
"""
Created on Fri Jan 23 16:04:32 2026

@author: hirsc
"""

import re
import os
import pypdfium2 as pdfium
import pytesseract
from PIL import Image
import numpy as np
import pandas as pd
from paddleocr import PPStructureV3
from datetime import datetime

pd.set_option('display.max_columns', None)

### Create a list of document names embedded in their location
docpath = r"C:\Users\hirsc\Documents\Raven3\surplus_project\00_data\other_liens\erie_liens-redemptions"
alldocs = os.listdir(docpath)
full_path = []
for a in alldocs:
    full_path.append(os.path.join(docpath, a))


## Try PaddleOCR
ocr = PPStructureV3(text_recognition_model_name="en_PP-OCRv4_mobile_rec")
docs_list_text_erie = [ocr.predict(full_path[i]) for i in range(len(full_path))]  

### Make a list of PDFs
docs_pdf = []
for f in full_path:
    try:
        pdfium.PdfDocument(f)
    except:
        print('oops')
    else:
        docs_pdf.append(pdfium.PdfDocument(f))

### Flatten the list (make it into a list of pages)
docs_list = [item for sublist in docs_pdf for item in sublist]

### Give a path to the location of Tesseract
### It's probably here unless you did something weird
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

# ### Transform each page into an image and run OCR on each image to get each page
# ### as a text string
docs_list_img = []
for d in range(len(docs_list)):
    bitmap = docs_list[d].render(scale=1, rotation=0)
    pil_image = bitmap.to_pil()
    docs_list_img.append(pil_image)  

markdown_list = []
markdown_images = []

for d in range(len(docs_list_text)):
    for i in range(len(docs_list_text[d])):
        md_info = docs_list_text[d][i].markdown
        markdown_list.append(md_info)
        markdown_images.append(md_info.get('markdown_images', {}))
    
# markdown_texts = ocr.concatenate_markdown_pages(markdown_list)

docs_clean = []
for d in range(len(markdown_list)):
    doc = markdown_list[d]['markdown_texts']
    clean_doc = doc.replace('\n', ' ')
    docs_clean.append(clean_doc)

# Write to txt
clean_folder = r"C:\Users\hirsc\Documents\Raven3\surplus_project\00_data\cortland_jof_txt\cortland_jof"
clean_paths = [clean_folder + str(i) + '.txt' for i in range(len(docs_clean))]

for d in range(len(docs_clean)):
    with open(clean_paths[d], 'w') as file:
        file.write(docs_clean[d])
        
# Write to png
clean_folder = r"C:\Users\hirsc\Documents\Raven3\surplus_project\00_data\cortland_jof_png\cortland_jof"
clean_paths = [clean_folder + str(i) + '.png' for i in range(len(docs_list_img))]

for d in range(len(docs_list_img)):
    docs_list_img[d].save(clean_paths[d])