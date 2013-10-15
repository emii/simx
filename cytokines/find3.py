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
with open('ck_names_cope.dat','r') as ck_list:
    for ckdefs in ck_list:  
        cks=ckdefs.strip('\n').split(',')
        ckdict[cks[0]] = [c.replace(' ','%20' ) for c in cks]
        ck_names.append(cks[0])
        #cytokines+=[c.replace(' ','%20') for c in cks]

url = 'http://www.copewithcytokines.org/cope.cgi'
celltypes=('hepatocytes',)#,'fibroblasts','T-cells','macrophages')
cells={}

for cell in celltypes:
    cells[cell]={}
    p=requests.get(url,params={'key':cell})
    if (p.status_code == requests.codes.ok):
        print (cell,p.status_code,p.headers['content-type'])
    else:
        print (cell,p.status_code,'error')

    soup = BeautifulSoup(p.text,"lxml")                                     
    [s.unwrap() for s in soup.body.find_all('span')]
    title=soup.find('h1')
    #pcontents=title.find_next_siblings('p')
    #plist=[p for p in pcontents if p.find('b', text=u'\u00A5')]
   
    for p in title.find_next_siblings('p'):
        if p.find('b',text=u'\u00A5'):    
            p.append(soup.new_tag('br'))
            p.unwrap()
            #bcont=b.contents
            #b.unwrap()
                

    # get the text contents of the page
    content=[]
    for p in title.find_next_siblings('p'):
        cnt=p.get_text()
        cnt=cnt.strip();
        if len(cnt)<1:
            continue
        else:
	        #content+=x.encode('ascii')
            content.append(cnt)
    cells[cell]['contents'] = content
    
    #search expressed cytokines
    first=title.find_next_siblings('b', text=u'\u00A5')
    expressed = []

    for el in first:
        ck = soup.new_tag('entry')
        while el.name != 'br':
            ck.contents.append(el)
            el=el.next_sibling
        expressed.append(ck)
    
    cytokines=[]
    for ck in expressed:
        try:
            cytokines.append(ck.find('a').get_text())
        except:
            continue
    
    #search expressed cytokine receptors
    el=soup.find(text=u'\xa5\xa5')
    recepted = []
    ck=soup.new_tag('entry')

    while el.name != 'center':
        if el.name == 'br':
            recepted.append(ck)
            ck=soup.new_tag('entry')
            el=el.next_element
            continue
        ck.contents.append(el)
        el=el.next_element

#    for el in first:
#        ck = soup.new_tag('entry')
#        while el.name != 'br':
#        #    if c < 1000:
#         #       print el
#          #  c+=1
#            ck.contents.append(el)
#            el=el.next_element
#        recepted.append(ck)
    
    receptors=[]
    cytokines=[]
    for ck in recepted:
        if re.search(ur'\xa5\xa5',ck.get_text()):

            try:   
                receptors.append(ck.find('a').get_text())
            except:
                #print ck
                continue
        else:
            try:   
                cytokines.append(ck.find('a').get_text())
            except:
                #print ck
                continue

    with open('test_unwrap3.html','w') as f:
        f.write(str(soup))
