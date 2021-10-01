# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 22:57:24 2021

@author: panasetskaya
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pprint
import pandas as pd

min_years = float(input("What's the minimum maturity period? (ex.: 2.5)"))
max_years = float(input("What's the maximum maturity period? (ex.: 3.5)"))

print()
print("Please wait")
print()

url = f"https://smart-lab.ru/q/ofz/order_by_mat_years/desc/?mat_years_gt={min_years}&mat_years_lt={max_years}"

headers = {"user agent": ""
          ""
          ""} # YOUR USER AGENT HERE
html = requests.get(url, headers)
soup = BeautifulSoup(html.content, 'html.parser')
text = str(soup.get_text()) 
ofz_list = [] #chosen bonds' names
index = [m.start() for m in re.finditer('ОФЗ', text)]

for i in tuple(index):
    j = i+9
    ofz_list.append(text[i:j]) 

garbage = {'ОФЗ, Моск', 'ОФЗ\nКарта', 'ОФЗ - Мос', 'ОФЗ\n\n\n\n\n\n', 'ОФЗ\nКорпо', 'ОФЗ\nСубфе', 'ОФЗ\nПосто', 'ОФЗ, Моск', 'ОФЗ\nКрива'}
ofz_list = list(set(ofz_list) - garbage)

def new_url_list():
    url_list = [] 
    for o in ofz_list:
        ofz_num = str(o).replace("ОФЗ ", "")
        def is_real_url():
            for n in range(10):
                checked_url = requests.get(f'https://smart-lab.ru/q/bonds/SU{ofz_num}RMFS{n}/')
                checked_url_content = BeautifulSoup(checked_url.content, 'html.parser')
                checked_url_text = str(checked_url_content.get_text())
                if not "404" in checked_url_text:
                    return f'https://smart-lab.ru/q/bonds/SU{ofz_num}RMFS{n}/'
        url_list.append(is_real_url())
    return url_list
        
ofz_url_list = new_url_list()

now = datetime.now()

ofz_dictionary = {}

for m in ofz_url_list:
    
    this_ofz_html = requests.get(m, headers)
    new_soup = BeautifulSoup(this_ofz_html.content, 'html.parser')
    convert = new_soup.findAll('div', {'style': 'margin: 1em 1em 1em 16px; font-size: 12px'})
    string_convert = str(convert)
    
    p = int(string_convert.find("ОФЗ"))
    ofz_name = string_convert[p:p+9]
    
    b = int(string_convert.find("составляет"))
    if string_convert[b+11:b+15] == 'e="m':
        yield_to_mat = "Unavailable"
    else:
        yield_to_mat = string_convert[b+11:b+15]

    g = int(string_convert.find("номиналу"))
    maturity_date = str(string_convert[g+9:g+19]) 
    
    mat_date_datetime = datetime.strptime(maturity_date, "%Y-%m-%d") 
    years_to_mat = format((((mat_date_datetime - now).days)/365), ".2f") 
    
    h = int(string_convert.find("или"))
    price_percent = string_convert[h+4:h+10]
    
    this_ofz_dict = {
        "Current price": price_percent,
        "Yield to maturity": yield_to_mat,
        "Maturity date": maturity_date,
        "Years to maturity": years_to_mat
        }
    
    ofz_dictionary.update({ofz_name:this_ofz_dict})

pprint.pprint(ofz_dictionary)

pd.DataFrame(ofz_dictionary).fillna('').to_csv('ofz.csv')
print("Saved to: ofz.csv")
