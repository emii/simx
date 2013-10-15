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
with open('ck_names.dat','r') as ck_list:
    for ckdefs in ck_list:  
        cks=ckdefs.strip('\n').split(',')
        ckdict[cks[0]] = [c.replace(' ','%20' ) for c in cks]
        ck_names.append(cks[0])
        cytokines+=[c.replace(' ','%20') for c in cks]

with open('cell-types.dat','r') as ct:
    types=[n.strip('\n').replace(' ','%20') for n in ct]

keys=cytokines+types

url = 'http://www.copewithcytokines.org/cope.cgi'
titles=[]
contents={}
lkin={}
lkout={}
for k in keys:
    p=requests.get(url,params={'key':k})
    if (p.status_code == requests.codes.ok):
        print (k,p.status_code,p.headers['content-type'])
    else:
	    print (k,p.status_code,'error')
	
    content='' 
    soup = BeautifulSoup(p.text,"lxml")
    
    out=soup.find_all('b',text=u'\u00A5')
    inn=soup.find_all('b',text=u'\u00A5\u00A5')
    lkout[k]=[]
    lkin[k]=[]
    for l in out:
        try:
            node=l.find_next_sibling().a.get_text()
            if node in cytokines:
                lkout[k]+=[node]
	        	
        except:
            continue
    for l in inn:
        try:
            node=l.find_next_sibling().a.get_text()
            if node in cytokines:
                lkin[k]+=[node]
        except:
            continue
#    if len(inn)>0:
#        for el in inn[0].next_elements:
#            try:
#	            el.decompose()
#            except:
#                el=''
#
#    if len(out)>0:
#        for el in out[0].next_elements:
#            try:
#                el.decompose()
#            except:
#                el=''

    #print soup.find_all('b',text=u'\u00A5')
    titles.append(k)
    title = soup.h1
    text = title.find_next_siblings('p')
    for x in text:
        cnt=x.get_text()
        if re.search(u'\u00A5',cnt) or re.match(u'\u00A5\u00A5',cnt):
            continue
        else:
	        #content+=x.encode('ascii')
            content +='\n<p>'+cnt+'</p>'
    contents[k]= content

env= Environment(loader=PackageLoader('find', 'templates'))
template = env.get_template('template.html')
ww=template.render(names=ck_names, types=types)
with codecs.open('index.html', encoding='utf-8', mode = 'w') as f:
        f.write(ww)

template = env.get_template('ck.html')
for cn in ck_names:

    ww=template.render(name=cn, cytokines=ckdict, contents=contents)
    with codecs.open('ck/'+cn.replace('%20',' ')+'.html', encoding='utf-8', mode = 'w') as f:
        f.write(ww)

template = env.get_template('ct.html')
for ct in types:
    ww=template.render(name=ct, lkin=lkin, lkout=lkout, contents=contents)
    with codecs.open('ct/'+ct.replace('%20',' ')+'.html', encoding='utf-8', mode = 'w') as f:
        f.write(ww)
