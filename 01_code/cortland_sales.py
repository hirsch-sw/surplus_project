# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 13:58:47 2026

@author: hirsc
"""

import re
import os
from PIL import Image
import numpy as np
import pandas as pd

# There was some cleaning that happened in Excel. 
# This included adding dates and correcting addresses a little bit, such as:
    # adding spaces
    # adding "route" when it had been erased
    # removing some extraneous info
d_jof = pd.read_csv(r'/path/to/foreclosures')

path_sales = r'/path/to/sales'
allsales = os.listdir(path_sales)
full_sales = []
for a in allsales:
    full_sales.append(os.path.join(path_sales, a))
    
l_sales = []
for f in full_sales:
    file = pd.read_csv(f)
    l_sales.append(file)
    
d_sales = pd.concat(l_sales, axis=0)
d_sales = d_sales.drop_duplicates()


d_jof['address'] = d_jof['address'].str.lower()
l_towns = [r'Cincinnatus',
           r'Cortland',
r'Cortlandville',
r'Cuyler',
r'Freetown',
r'Harford',
r'Homer',
r'Lapeer',
r'Marathon',
r'Preble',
r'Scott',
r'Solon',
r'Taylor',
r'Truxton',
r'Willet']
l_towns = [l.lower() for l in l_towns]


d_jof['address'] = d_jof['address'].str.replace(r'[\s\.,]+$', '', regex = True) # remove extraneous characters from end of string
d_jof['address'] = d_jof['address'].str.replace(r'[\s\.,]+', ' ', regex = True) # remove extra spaces
d_jof['address'] = d_jof['address'].str.replace(r' ny \d{5}', '', regex = True) # remove ny and zip code
d_jof['address'] = d_jof['address'].str.replace(r' new york \d{5}', '', regex = True) # again, remove ny and zip code

d_jof['address'] = d_jof['address'].str.rsplit(n=1, expand=True)[0]
d_jof['city'] = d_jof['address'].str.rsplit(n=1, expand=True)[1]

d_sales['ADDRESS'] = d_sales['ADDRESS'].str.lower()
d_sales['CITY'] = d_sales['CITY'].str.lower()

d_sales['ADDRESS'] = d_sales['ADDRESS'].str.replace(r' rd', ' road ', regex = True)
d_sales['ADDRESS'] = d_sales['ADDRESS'].str.replace(r' st', ' street ', regex = True)
d_sales['ADDRESS'] = d_sales['ADDRESS'].str.replace(r' ave', ' avenue ', regex = True)
d_sales['ADDRESS'] = d_sales['ADDRESS'].str.replace(r' dr', ' drive ', regex = True)
d_sales['ADDRESS'] = d_sales['ADDRESS'].str.replace(r' e ', ' east ', regex = True)
d_sales['ADDRESS'] = d_sales['ADDRESS'].str.replace(r' w ', ' west ', regex = True)
d_sales['ADDRESS'] = d_sales['ADDRESS'].str.replace(r' (rt|rte) ', ' route ', regex = True)

l_jof_addresses = d_jof['address'].to_list()
l_sales_addresses = d_sales['ADDRESS'].to_list()

l_jof_sold = [j for j in l_jof_addresses if j in l_sales_addresses]
