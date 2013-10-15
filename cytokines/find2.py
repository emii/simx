# -*- coding: utf-8 -*-

import sys
import codecs
import re
import requests
from jinja2 import Environment, PackageLoader 
from bs4 import BeautifulSoup

ckdict={}
cytokines=[]
ck_names=[]
with open('ck_names.dat','w') as ck_list:
    for ckdefs in ck_list:  
        cks=ckdefs.strip('\n').split(',')
        ckdict[cks[0]] = [c.replace(' ','%20' ) for c in cks]
        ck_names.append(cks[0])
        cytokines+=[c.replace(' ','%20') for c in cks]

with open('cell-types.dat','w') as ct:
    types=[n.strip('\n').replace(' ','%20') for n in ct]

keys=cytokines+types


url = 'http://www.copewithcytokines.org/cope.cgi'
celltypes=('hepatocytes','fibroblasts','T-cells','macrophages')
k='endothelial%20cells'

p=requests.get(url,params={'key':k})
if (p.status_code == requests.codes.ok):
    print (k,p.status_code,p.headers['content-type'])
else:
    print (k,p.status_code,'error')

soup = BeautifulSoup(p.text,"lxml")                                     
[s.unwrap() for s in soup.body.find_all('span')]
title=soup.find('h1')
contents=title.find_next_siblings('p')
plist=[p for p in contents if p.find('b', text=u'\u00A5')]
for p in plist:
    p.append(soup.new_tag('br'))
    p.unwrap()

first=title.find_next_siblings('b', text=u'\u00A5\u00A5')
contenidos=[]
for el in first:
    contenido = soup.new_tag('entry')
    while el.name != 'br':
        contenido.contents.append(el)
        el=el.next_sibling
    contenidos.append(contenido)

cytokines=[]
for cont in contenidos:
    cytokines+=[l.get_text() for l in cont.find_all('a')]    

#with open('test_unwrap3.html','w') as f:
#    f.write(str(soup))
