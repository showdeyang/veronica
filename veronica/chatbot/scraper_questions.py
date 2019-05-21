# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import numpy as np
import random
import math
import json

#This script scrapes questions and saves them to questions.txt
def scrape():
    with open('./questions.txt','a') as f:
        [print(question,file=f) for question in [elem.a.get_text().replace('\n','') for elem in BeautifulSoup(requests.get('https://zhidao.baidu.com/list?type=feed').content,'lxml').findAll('div',{'class':'question-title-section'})]]
        
[scrape() for i in range(30)]