import requests
from lxml import etree
import networkx as nx

url = 'http://rest.kegg.jp/'
action = 'get'
db = 'path'
org = 'hsa'
item = '04060'
formt = 'kgml' 
write_ = True
requrl = url+'/'+action+'/'+':'.join([db,org+item])+'/'+formt

#keggreq = requests.get(requrl)
#root = etree.XML(keggreq.text)
root = etree.parse('hsa04060.xml')
G=nx.DiGraph()

ckdict={}
cytokines=[]
ck_names=[]
with open('ck_names.dat','r') as ck_list:
    for ckdefs in ck_list:  
        cks=ckdefs.strip('\n').split(',')
        ckdict[cks[0]] = [c.replace(' ','%20' ) for c in cks]
        ck_names.append(cks[0])
        cytokines+=[c.replace(' ','%20') for c in cks]

for el in root.iterfind('entry'):
    if el.get('type')=='gene':
        nid = el.get('id')
        lo = el.find('graphics')
        labels = [x.strip() for x in el.find('graphics').get('name').split(',')]
        label= labels[0]
        altnames=lo.get('name')
        x,y,z = (lo.get('x'),lo.get('y'),0.0)
        size = 15
        r,g,b = (147,161,161)
        color = {'r':r, 'g':g, 'b':b}
        position = {'x':x, 'y':y, 'z':y}
        viz = {'size':size, 'color':color, 'position':position}
        G.add_node(nid,{'label':label, 'viz':viz, 'names':altnames, 'type':'single'})
    elif el.get('type')=='group':
        nid = el.get('id')
        lo = el.find('graphics')
        comps=el.findall('component')
        ids= [co.get('id') for co in comps]
        label = ''
        x,y,z = (lo.get('x'),lo.get('y'),-1)
        size = 10
        r,g,b = (133,153,0)
        color = {'r':r, 'g':g, 'b':b}
        position = {'x':x, 'y':y, 'z':y}
        viz = {'size':size, 'color':color, 'position':position}
        G.add_node(nid,{'label':label, 'viz':viz,'type':'receptor complex'})
        for co in ids:
            G.node[co]['viz']['color']=color
    else:
        continue
for rl in root.iterfind('relation'):
    id1=rl.get('entry1')
    id2=rl.get('entry2')
    G.node[id1]['viz']['color']={'r':42,'g':161,'b':152}
    G.node[id1]['type']='cytokine'
    if G.node[id2]['type']=='single':
        G.node[id2]['viz']['color']={'r':211, 'g':54, 'b':130}
        G.node[id2]['type']='receptor'
    else:
        G.node[id2]['viz']['color']={'r':253, 'g':246, 'b':227}
    G.add_edge(id1,id2)
if write_:
    nx.write_gexf(G,'../../sndbxbe/output/static/D3/test2.gexf')
