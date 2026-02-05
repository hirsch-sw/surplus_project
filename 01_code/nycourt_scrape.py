# -*- coding: utf-8 -*-
"""
Created on Thu Jan  8 10:06:17 2026

@author: hirsc
"""

import selenium
from bs4 import BeautifulSoup
import requests
import subprocess
import re
import os
import pypdfium2 as pdfium
import pytesseract
from PIL import Image
import numpy as np
import time

url = 'https://www.nycourts.gov/legacyPDFs/courts/2jd/kings/civil/foreclosures/foreclosure%20scans/'

    
with open(r"C:\Windows\System32\foreclosure%20scans.html", "r", encoding="utf-8") as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Extract all 'href' attributes from 'a' tags
urls = []
for link in soup.find_all('a'):
    href = link.get('href')
    if href:
        # Optional: convert relative URLs to absolute URLs
        absolute_url = "https://nycourts.gov" + href
        urls.append(absolute_url)

urls.pop() # remove last entry, which we can't use
urls.sort()
urls.pop(0) # remove first entry, which is empty

addresses = []
for u in urls:
    addresses.append(re.findall('(?<=scans/).*', u))

address_list = sum(addresses, [])

print(address_list)

address_list.sort()
genny = np.random.default_rng()

for u in range(len(urls)):
    sub = subprocess.run(['curl', 
                          urls[u],
                          '-A "Mozilla ()/20100101 Firefox/81.0"',
                          r"-o " + address_list[u]],
                          shell=True)
    sub
    print(sub.args)
    print(sub.returncode)
    time.sleep(genny.integers(low=43, high=64))
    
### Create a list of document names embedded in their location
docpath = r"C:\Users\hirsc\foreclosure_docs"
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
    
### Extract Amount of Judgement
amount_of_judgment = []
for d in range(len(docs_clean)):
    amount_of_judgment.append(re.findall('(?<=\\$)[0-9,\\.]+', docs_clean[d]))
    
### Extract case index #
index = []
for d in range(len(docs_clean)):
    index.append(re.findall('\\d{6}/', docs_clean[d]))
    
# Choose first (not analytically sound, but shortcut here)
aoj_temp = [sublist[0] for sublist in amount_of_judgment if sublist]
index_temp = [sublist[0] for sublist in index if sublist]

import pandas as pd

df = pd.DataFrame({'aoj': aoj_temp, 'caseIndex': index_temp})
    
# amount_of_judgement = []
# for d in docs_list_text:
#     amount_of_judgement.append(re.findall('(?<=\\$)[0-9,\\.]+', d))

# amount_of_judgement = []
# for d in docs_list_text:
#     amount_of_judgement.append(re.findall('(?<=[Aa]mount of [Jj]udgment)[0-9,\\.]+', d))