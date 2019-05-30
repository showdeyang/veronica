# -*- coding: utf-8 -*-
import re


with open('/web/veronica/nlp/废水处理目录.txt','w', encoding='utf-8') as f:
    f.write(data)
with open('/web/veronica/nlp/废水处理目录.txt','r') as f:
    keywords = [d.strip() for d in f.readlines()]
    
def formatText(text):
    t = text.replace('\ufeff','')
    t = t.replace('\u3000','')
    if ' ' in t:
        t = t.split(' ')[1]
    t = t.replace('本章小结','')
    t = t.replace('习题与思考','')
    t = t.replace('参考文献','')
    t = t.replace('第1章绪论','')
    t = t.replace('概述','')
    t = t.replace('附：','')
    t = t.replace('实例','')
    t = t.replace('研究报告','')
    t = t.replace('编写大纲','')
    t = t.replace('编制依据和范围','')
    if len(t) < 4:
        t = re.sub(r'\d*','',t)
    return t

keywords = [formatText(keyword) for keyword in keywords]
keywords = [keyword for keyword in keywords if keyword]
keywords = list(set(keywords))
with open('./feishui.txt','w') as f:
    [print(keyword, file=f) for keyword in keywords]
