# -*- coding: utf-8 -*-
"""
Принимает мин. и макс. требуемые сроки к погашению ОФЗ (пользовательский ввод). 
Собирает данные с сайта smartlab. 
Выдает словарь, в котором перечислены ОФЗ, подходящие по срокам, с их текущей ценой, 
датой погашения, количеством лет до погашения и текущей доходностью к погашению.

На данный момент работает медленно: от полминуты до 3 минут в зависимости от сроков. Переписывается.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pprint
import pandas as pd


min_years = float(input("Введите минимальный срок к погашению (например, 2.5)"))
max_years = float(input("Введите максимальный срок к погашению (например, 3.5)"))

print()
print("Подождите минутку, Морковка")
print()

url = f"https://smart-lab.ru/q/ofz/order_by_mat_years/desc/?mat_years_gt={min_years}&mat_years_lt={max_years}"


headers = {"user agent": ""
          ""
          ""} # агент пользователя ВВЕСТИ ЗДЕСЬ

html = requests.get(url, headers)

soup = BeautifulSoup(html.content, 'html.parser')

text = str(soup.get_text()) #получаем весь текст

ofz_list = [] #список выбранных ОФЗ

index = [m.start() for m in re.finditer('ОФЗ', text)]

for i in tuple(index):
    j = i+9
    ofz_list.append(text[i:j]) 

garbage = {'ОФЗ, Моск', 'ОФЗ\nКарта', 'ОФЗ - Мос', 'ОФЗ\n\n\n\n\n\n', 'ОФЗ\nКорпо', 'ОФЗ\nСубфе', 'ОФЗ\nПосто', 'ОФЗ, Моск', 'ОФЗ\nКрива'}
ofz_list = list(set(ofz_list) - garbage)

def is_real_url(ofz_num):
    for n in range(10):
        checked_url = requests.get(f'https://smart-lab.ru/q/bonds/SU{ofz_num}RMFS{n}/')
        checked_url_content = BeautifulSoup(checked_url.content, 'html.parser')
        checked_url_text = str(checked_url_content.get_text())
        if not "404" in checked_url_text:
            yield f'https://smart-lab.ru/q/bonds/SU{ofz_num}RMFS{n}/'

def new_url_list():
    url_list = [] #список нужных URL
    for o in ofz_list:
        ofz_num = str(o).replace("ОФЗ ", "")
        a = is_real_url(ofz_num)
        for i in a:
            url_list.append(i)
    return url_list
        

def get_this_ofz_dict(some_list):
    for m in some_list:
    
        now = datetime.now()    
    
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
        maturity_date = str(string_convert[g+9:g+19]) #даты погашения в формате строки
        
        mat_date_datetime = datetime.strptime(maturity_date, "%Y-%m-%d") #даты погашения в формате даты datetime
        years_to_mat = format((((mat_date_datetime - now).days)/365), ".2f") #лет до погашения в дес.формате
        
        h = int(string_convert.find("или"))
        price_percent = string_convert[h+4:h+10]
        
        this_ofz_dict = {
            "Current price": price_percent,
            "Yield to maturity": yield_to_mat,
            "Maturity date": maturity_date,
            "Years to maturity": years_to_mat
            }
        
        yield [ofz_name, this_ofz_dict]

ofz_url_list = new_url_list()

ofz_dictionary = {}

b = get_this_ofz_dict(ofz_url_list)
for i in b:
    ofz_dictionary.update({i[0]:i[1]})

pprint.pprint(ofz_dictionary)

pd.DataFrame(ofz_dictionary).fillna('').to_csv('ofz.csv')

print()
print("Сохранено в файл: ofz.csv")
