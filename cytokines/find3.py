# -*- coding: utf-8 -*-

import sys
import codecs
import re
import math
import requests
import networkx as nx
from jinja2 import Environment, PackageLoader 
from bs4 import BeautifulSoup

G=nx.DiGraph()

ckdict={}
#ck_labels=[]
ck_names=[]
with open('ck_names_cope.dat','r') as ck_list:
    for ckdefs in ck_list:  
        cks=ckdefs.strip('\n').split(',')
        ckdict[cks[0]] = [c.replace(' ','%20' ) for c in cks]
        ck_names.append(cks[-1])
        #ck_names+=[c for c in cks]

url = 'http://www.copewithcytokines.org/cope.cgi'
celltypes=('hepatocytes','fibroblasts')#,'T-cells','macrophages')
cells={}
r=50
L=len(ck_names)
i=1
for ck in ck_names:
    x=math.cos(math.pi*i/L)*r 
    y=math.sin(math.pi*i/L)*r
    i+=1
    # add a node for cytokine
    size = 15
    r,g,b = (133,153,0)
    color = {'r':r, 'g':g, 'b':b}
    position = {'x':x, 'y':y, 'z':0}
    viz = {'size':size, 'color':color,'position':position}
    G.add_node(ck,{'label':ck, 'viz':viz, 'type':'cytokine'})

for cell in celltypes:
    
    # add a node for celltype
    x,y,z = (1,1,0.0)
    size = 15
    r,g,b = (42,161,152)
    color = {'r':r, 'g':g, 'b':b}
    position = {'x':x, 'y':y, 'z':y}
    viz = {'size':size, 'color':color}
    G.add_node(cell,{'label':cell, 'viz':viz, 'type':'cell'})

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
    
    #search expressed cytokines and receptors
    el=soup.find(text=u'\xa5\xa5')
    indexed = []
    ck=soup.new_tag('entry')

    while el.name != 'center':
        if el.name == 'br':
            indexed.append(ck)
            ck=soup.new_tag('entry')
            el=el.next_element
            continue
        ck.contents.append(el)
        el=el.next_element
 
    receptors=[]
    cytokines=[]
    
    for ck in indexed:
        if re.search(ur'\xa5\xa5',ck.get_text()):

            try:
                rc_name = ck.find('a').get_text()
                if rc_name in ck_names:
                    G.add_edge(rc_name,cell)
                    receptors.append(rc_name)
            except:
                #print ck
                continue
        elif re.search(ur'\xa5',ck.get_text()):
            try:   
                ck_name = ck.find('a').get_text()
                if ck_name in ck_names:
                    G.add_edge(cell,ck_name)
                    cytokines.append(ck_name)
            except:
                #print ck
                continue
        else:
            continue
    cells[cell]['cytokines'] = cytokines
    cells[cell]['receptors'] = receptors


nx.write_gexf(G,'../../sndbxbe/output/static/D3/nt.gexf')

