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
import pandas as pd
from paddleocr import PPStructureV3
from datetime import datetime

pd.set_option('display.max_columns', None)

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
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

# ### Transform each page into an image and run OCR on each image to get each page
# ### as a text string
docs_list_img = []
for d in range(len(docs_list)):
    bitmap = docs_list[d].render(scale=1, rotation=0)
    pil_image = bitmap.to_pil()
    docs_list_img.append(pil_image)

## Try PaddleOCR
ocr = PPStructureV3(text_recognition_model_name="en_PP-OCRv4_mobile_rec")
docs_list_text = [ocr.predict(full_path[i]) for i in range(len(full_path))]    

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


    
### Extract address
address = []
for d in range(len(docs_clean)):
    try:
        re.search(r'(PROPERTY|PREMISES|Foreclosure of:|Property:|Premises:|Property address:).+\d.+\d{5}', docs_clean[d]).group()
    except:
        address.append(None)
    else:
        address.append(re.search(r'(PROPERTY|PREMISES|Foreclosure of:|Property:|Premises:|Property address:).+\d.+\d{5}', docs_clean[d]).group())
        
for i in range(len(address)):
    try:
        re.search(r'(\d+\D+\d{5})+?', address[i]).group()
    except:
        address[i] = None
    else:
        address[i] = re.search(r'(\d+\D+\d{5})+?', address[i]).group()
    
## Extract lien
lien = []
for d in range(len(docs_clean)):
    try:
        re.search('(?<=Report: ).+[0-9,.]+', docs_clean[d]).group()
    except:
        lien.append(None)
    else:
        lien.append(re.search('(?<=Report: ).+[0-9,.]+', docs_clean[d]).group())
        
for i in range(len(lien)):
    try:
        re.search(r'[0-9,\\.]+', lien[i]).group()
    except:
        lien[i] = None
    else:
        lien[i] = re.search(r'[0-9,\\.]+', lien[i]).group()
        
        
## Extract costs and disbursements
costs = []
for d in range(len(docs_clean)):
    try:
        re.search(r'(?<=Costs and Disbursements: ).+[0-9,\\.]+', docs_clean[d]).group()
    except:
        costs.append(None)
    else:
        costs.append(re.search(r'(?<=Costs and Disbursements: ).+[0-9,\\.]+', docs_clean[d]).group())
        
for i in range(len(costs)):
    try:
        re.search(r'[0-9,\\.]+', costs[i]).group()
    except:
        costs[i] = None
    else:
        costs[i] = re.search(r'[0-9,\\.]+', costs[i]).group()
        
## Extract Additional Allowance
allowance = []
for d in range(len(docs_clean)):
    try:
        re.search(r'(?<=Allowance: ).+[0-9,\\.]+', docs_clean[d]).group()
    except:
        allowance.append(None)
    else:
        allowance.append(re.search(r'(?<=Allowance: ).+[0-9,\\.]+', docs_clean[d]).group())
        
for i in range(len(allowance)):
    try:
        re.search(r'[0-9,\\.]+', allowance[i]).group()
    except:
        allowance[i] = None
    else:
        allowance[i] = re.search(r'[0-9,\\.]+', allowance[i]).group()
        
## Extract Attorney Fees:
fees = []
for d in range(len(docs_clean)):
    try:
        re.search(r'(?<=Fees: ).+[0-9,\\.]+', docs_clean[d]).group()
    except:
        fees.append(None)
    else:
        fees.append(re.search(r'(?<=Fees: ).+[0-9,\\.]+', docs_clean[d]).group())
        
for i in range(len(fees)):
    try:
        re.search(r'[0-9,\\.]+', fees[i]).group()
    except:
        fees[i] = None
    else:
        fees[i] = re.search(r'[0-9,\\.]+', fees[i]).group()
        
# Extract document termination flag
beg = []
for d in range(len(docs_clean)):
    try:
        re.search(r'P\s*R\s*E\s*S\s*E\s*N\s*T\s*|Image: 1 |PROPERTY|PREMISES|Foreclosure of:|Property:|Premises:|Property address:', 
                  docs_clean[d]).group()
    except:
        beg.append(None)
    else:
        beg.append("beginning")

# Extract dates
dates = []
for d in range(len(docs_clean)):
    try:
        re.search(r'(?<=EF\d{2}-\d{3})\d{2}/\d{2}/202\d', docs_clean[d], regex = True).group()
    except:
        dates.append(None)
    else:
        dates.append(re.search(r'(?<=EF\d{2}-\d{3})\d{2}/\d{2}/202\d', docs_clean[d], regex = True).group())
        
for i in range(len(fees)):
    try:
        re.search(r'[0-9,\\.]+', fees[i]).group()
    except:
        dates[i] = None
    else:
        dates[i] = re.search(r'[0-9,\\.]+', fees[i]).group()

        
# Now check to see which documents loaded correctly
# Number documents by each new address entry

address_count = []
for i in range(len(address)):
    if address[i] is None:
        address_count.append(0)
    else:
        address_count.append(1)
        
total = 0
address_iter = []
for i in address_count:
    total += i
    address_iter.append(total)
    
beg_count = []
for i in range(len(beg)):
    if beg[i] is None:
        beg_count.append(0)
    else:
        beg_count.append(1)
        
total_beg = 0
beg_iter = []
for i in beg_count:
    total_beg += i
    beg_iter.append(total_beg)
    
all_beg = [a + b for a,b in zip(address_count, beg_count)]

all_beg = [1 if tally > 0 else 0 for tally in all_beg]

total_all = 0
all_iter = []
for i in all_beg:
    total_all += i
    all_iter.append(total_all)
    
address_index = [i for i, x in enumerate(address) if x is not None]
beg_index = [i for i, x in enumerate(beg) if x is not None]

missings = [b for b in beg_index if b not in address_index]
add_missings = [a for a in address_index if a not in beg_index]
# missings (without adding Foreclosure of:, Premises:, Property:, and Property address: to regex string)
# Out[144]: 
# [95, "Foreclosure of:"
#  180, no address (followed by a list of properties)
# markdown_images[183]['imgs/img_in_table_box_90_24_1181_1483.jpg'].show() also saved
# markdown_images[184]['imgs/img_in_table_box_102_56_1167_703.jpg'].show() also saved
#  185, Mortgaged Premises:
#  276, Mortgaged Premises:
#  301, Mortgaged Property:
#  315, Property address:
#  348, Schedule A (address appears elsewhere)
#  413, no address - OCR error
#  428, Mortgaged Premises:
#  573, Mortgaged Premises:
#  586, MORTGAGED PROPERTY:0 -- no zip code, so no pattern
#  674, Mortgaged Premises:
#  800, Mortgaged Premises:
#  971, amendment (OK)
#  979, Mortgaged Premises:
#  1018] Mortgaged Premises:
    
# picked up wrong address at index 211
# has problems with state route addresses
# missed 413-422 entirely

# After correction of address regex string
# missings
# Out[193]: [180 ^, 348 ^, 413 ^, 586 ^, 971 ^]
    
# Create a DataFrame
d_surplus = pd.DataFrame({'id': beg_iter,
                          'address': address,
                          'lien': lien,
                          'costs': costs,
                          'allowance': allowance,
                          'fees': fees})

# Create a dictionary of values per property
l_keys = list(d_surplus.columns)
dict_jof = dict.fromkeys(l_keys)

id_col = []
address_col = []

for i in range(1, total_beg+1):
    id_col.append(i)
    '''addresses'''
    try:
        d_surplus.loc[(d_surplus['id']==i) & (d_surplus['address'].notnull()), 'address'].to_list()[0]
    except: 
        address_col.append(None)
    else:
        address_col.append(d_surplus.loc[(d_surplus['id']==i) & (d_surplus['address'].notnull()), 'address'].to_list()[0])

lien_col = []
for i in range(1, total_beg+1):
    try:
        d_surplus.loc[(d_surplus['id']==i) & (d_surplus['lien'].notnull()), 'lien'].to_list()[0]
    except:
        lien_col.append(None)
    else:
        lien_col.append(d_surplus.loc[(d_surplus['id']==i) & (d_surplus['lien'].notnull()), 'lien'].to_list()[0])

costs_col = []
for i in range(1, total_beg+1):                        
    try:
        d_surplus.loc[(d_surplus['id']==i) & (d_surplus['costs'].notnull()), 'costs'].to_list()[0]
    except:
        costs_col.append(None)
    else:
        costs_col.append(d_surplus.loc[(d_surplus['id']==i) & (d_surplus['costs'].notnull()), 'costs'].to_list()[0])
        
        
allowance_col = []
for i in range(1, total_beg+1):
    try:
        d_surplus.loc[(d_surplus['id']==i) & (d_surplus['allowance'].notnull()), 'allowance'].to_list()[0]
    except:
        allowance_col.append(None)
    else:
        allowance_col.append(d_surplus.loc[(d_surplus['id']==i) & (d_surplus['allowance'].notnull()), 'allowance'].to_list()[0])

fees_col = []
for i in range(1, total_beg+1):                             
    try:
        d_surplus.loc[(d_surplus['id']==i) & (d_surplus['fees'].notnull()), 'fees'].to_list()[0]
    except:
        fees_col.append(None)
    else:
        fees_col.append(d_surplus.loc[(d_surplus['id']==i) & (d_surplus['fees'].notnull()), 'fees'].to_list()[0])
                        
                        
                       
                        
d_jof = pd.DataFrame({'id': id_col,
                          'address': address_col,
                          'lien': lien_col,
                          'costs': costs_col,
                          'allowance': allowance_col,
                          'fees': fees_col})

# Clean
for i in range(2,6):
    d_jof.iloc[:,i] = d_jof.iloc[:,i].astype(str).str.replace(r'\.{2}', '', regex = True)
    d_jof.iloc[:,i] = d_jof.iloc[:,i].astype(str).str.replace(r'\.(?=\d{3})', '', regex = True)
    d_jof.iloc[:,i] = d_jof.iloc[:,i].astype(str).str.replace(r'\.$', '', regex = True)
    d_jof.iloc[:,i] = d_jof.iloc[:,i].astype(str).str.replace(r'^\s*$', 'None', regex = True)
    d_jof.iloc[:,i] = d_jof.iloc[:,i].astype(str).str.replace(r',', '', regex = True)
    
d_jof = d_jof.fillna(value=np.nan)
d_jof = d_jof.replace({'None': np.nan})
for i in range(2,6):
    d_jof.iloc[:,i] = d_jof.iloc[:,i].astype(float)


# Write to disk
folder = r"C:\Users\hirsc\Documents\Raven3\surplus_project\00_data\cortland_foreclosures\cortland_foreclosures_"
d_jof.to_csv(folder + str(datetime.now().date()) + '.csv')
