import requests
from lxml import etree
import networkx as nx

url = 'http://rest.kegg.jp/'
action = 'get'
db = 'path'
org = 'hsa'
item = '04060'
formt = 'kgml' 

requrl = url+'/'+action+'/'+':'.join([db,org+item])+'/'+formt

keggreq = requests.get(requrl)

root = etree.XML(keggreq.text)
G=nx.DiGraph()

for el in root.iterfind('entry'):
    if el.get('type')=='gene':
        nid = el.get('id')
        lo = el.find('graphics')
        label = [x.strip() for x in el.find('graphics').get('name').split(',')][0]
        x,y,z = (lo.get('x'),lo.get('y'),0.0)
        size = 15
        r,g,b = (255,51,51)
        color = {'r':r, 'g':g, 'b':b}
        position = {'x':x, 'y':y, 'z':y}
        viz = {'size':size, 'color':color, 'position':position}
        G.add_node(nid,{'label':label, 'viz':viz})
for rl in root.iterfind('relation'):
    id1=rl.get('entry1')
    id2=rl.get('entry2')
    G.add_edge(id1,id2)
if write_
    nx.write_gexf(G,'kegg_pathway.gexf')






    
