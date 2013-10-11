from  bs4 import BeautifulSoup 
import requests


url = 'http://www.copewithcytokines.org/cope.cgi'

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

#first=title.find_next_siblings('b', text=u'\u00A5')
#entries=first[1].next_siblings
#contenido=soup.new_tag('entry')
#contenido.append(first[1])
#for e in entries:
#    if type(e)==type(contenido):
#        if n.name=='br':
#            break
#        else:
#            contenido.append(e)
#    else:
#        contenido.append(e)
        





#with open('test_unwrap3.html','w') as f:
#    f.write(str(soup))

