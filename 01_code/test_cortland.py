# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 13:59:46 2026

@author: hirsc
"""

## Cortland county

import re
import os
import pypdfium2 as pdfium
import pytesseract
from PIL import Image
import numpy as np
import time

### Create a list of document names embedded in their location
docpath = r"C:\Users\hirsc\Documents\Raven3\surplus_project\00_data\cortland_jof"
alldocs = os.listdir(docpath)
full_path = []
for a in alldocs:
    full_path.append(os.path.join(docpath, a))

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
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

### Transform each page into an image and run OCR on each image to get each page
### as a text string
docs_list_text = []
for d in range(len(docs_list)):
    bitmap = docs_list[d].render(scale=1, rotation=0)
    pil_image = bitmap.to_pil()
    docs_list_text.append(pytesseract.image_to_string(pil_image))
    
docs_clean = []
for d in docs_list_text:
    docs_clean.append(d.replace('\n', ' '))
    
### Extract address
address = []
for d in range(len(docs_clean)):
    try:
        address.append(re.search(r'(?<=PROPERTY:).+\d.+\d{5}', docs_clean[d]).group())
    except:
        None
        
for a in range(len(address)):
    try:
        address[a] = re.search(r'\d.+\d{5}', address[a]).group()
    except:
        None
    
## Extract lien
lien = []
for d in range(len(docs_clean)):
    try:
        lien.append(re.search('(?<=FOURTH: ).+[0-9,.]+', docs_clean[d]).group())
    except:
        None
        
for l in range(len(lien)):
    try:
        lien[l] = re.search(r'[0-9,\\.]+', lien[l]).group()
    except:
        None
        
## Extract costs and disbursements
costs = []
for d in range(len(docs_clean)):
    try:
        costs.append(re.search(r'(?<=Costs and Disbursements: ).+[0-9,\\.]+', docs_clean[d]).group())
    except:
        None
        
for c in range(len(costs)):
    try:
        costs[c] = re.search(r'[0-9,\\.]+', costs[c]).group()
    except:
        None
        
## Extract Additional Allowance
allowance = []
for d in range(len(docs_clean)):
    try:
        allowance.append(re.search(r'(?<=Allowance: ).+[0-9,\\.]+', docs_clean[d]).group())
    except:
        None
        
for a in range(len(allowance)):
    try:
        allowance[a] = re.search(r'[0-9,\\.]+', allowance[a]).group()
    except:
        None
        
## Extract Attorney Fees:
fees = []
for d in range(len(docs_clean)):
    try:
        fees.append(re.search(r'(?<=Fees: ).+[0-9,\\.]+', docs_clean[d]).group())
    except:
        None
        
for i in range(len(fees)):
    try:
        fees[i] = re.search(r'[0-9,\\.]+', fees[i]).group()
    except:
        None
    