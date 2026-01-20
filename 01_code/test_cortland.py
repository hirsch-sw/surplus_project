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
        re.search(r'(?<=(PROPERTY: |PREMISES: |Address: )).+\d.+\d{5}', docs_clean[d]).group()
    except:
        address.append(None)
    else:
        address.append(re.search(r'(?<=(PROPERTY: |PREMISES: |Address: )).+\d.+\d{5}', docs_clean[d]).group())
        
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
        re.search(r'P\s*R\s*E\s*S\s*E\s*N\s*T\s*|County of CORTLAND|Image: 1 ', docs_clean[d]).group()
    except:
        beg.append(None)
    else:
        beg.append("beginning")

        
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
    
all_beg = address_count + beg_count

all_beg = all_beg.map(lambda x: 1 if x > 0 else 0)
    
# Create a DataFrame
d_surplus = pd.DataFrame({'address_id': address_iter,
                          'address': address,
                          'lien': lien,
                          'costs': costs,
                          'allowance': allowance,
                          'fees': fees})

# Aggregate all items into a single column
d_surplus['complete'] = d_surplus.iloc[:, 1:6].bfill(axis=1).iloc[:, 0]

# Count items per address (there should be 5 including the address itself)
d_surplus['item_count'] = d_surplus['complete'].isnull().astype(int)

d_surplus['item_count'] = d_surplus['item_count'].map(lambda x: 1 if x == 0 else 0)

# number of elements by address ID
d_surplus['total'] = d_surplus['item_count'].groupby(d_surplus['address_id']).transform('sum')

# Now we know that if total < 5, we're missing an element;
# If total > 5, we're missing an address (because they're grouped by address)
# Note: index must be formatted as a list literal and columns cannot be listed in order to return a series
d_surplus.loc[d_surplus['total'] > 5, 'address_id'].unique()

## There's gotta be way more than just two addresses that got conflated, but we'll deal with that later
## Make a table?? of unique values by index
add_dict = d_surplus['complete'].groupby(d_surplus['address_id']).unique().to_dict()

for d in add_dict:
    print(len(add_dict[d][0]))
    
# First missing after index 2 array 1 (156,166.78). Missing address 1351 Hauck Hill Road
# handwriting in prior sheets. $44,183.73 is completely correct, but from next document.
# Again, missing all numbers from handwriting

docs_clean[14] # doesn't even show up

# Appears at the end of the document as "Said property is commonly known as..."
# add a truncating string from the last page

docs_clean[27]
## "Auction locations and contact list"

## Got the next one (richmond hill road)   
## Missing after hamlin st 
docs_clean[53]
